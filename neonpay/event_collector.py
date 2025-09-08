"""
NEONPAY Event Collector - Automatic event collection from all synchronized bots
Collects events from multiple bots and sends them to central analytics
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class EventCollectorConfig:
    """Configuration for event collection"""

    central_analytics_url: str
    collection_interval_seconds: int = 30
    batch_size: int = 100
    max_retries: int = 3
    retry_delay: float = 5.0
    enable_real_time: bool = True
    enable_batch_collection: bool = True


class BotEventCollector:
    """Collects events from a single bot"""

    def __init__(self, bot_id: str, bot_name: str, webhook_url: str) -> None:
        self.bot_id = bot_id
        self.bot_name = bot_name
        self.webhook_url = webhook_url
        self._pending_events: List[Dict[str, Any]] = []
        self._last_collection_time = 0

    async def collect_events(self) -> List[Dict[str, Any]]:
        """Collect events from bot webhook"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.webhook_url}/analytics/events"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        events = data.get("events", [])

                        # Add bot metadata to events
                        for event in events:
                            event["bot_id"] = self.bot_id
                            event["bot_name"] = self.bot_name
                            event["collected_at"] = time.time()

                        logger.info(
                            f"Collected {len(events)} events from {self.bot_name}"
                        )
                        return events if isinstance(events, list) else []
                    else:
                        logger.warning(
                            f"Failed to collect events from {self.bot_name}: {response.status}"
                        )
                        return []
        except Exception as e:
            logger.error(f"Error collecting events from {self.bot_name}: {e}")
            return []

    async def send_events_to_central(
        self, events: List[Dict[str, Any]], central_url: str, max_retries: int = 3
    ) -> bool:
        """Send events to central analytics"""
        if not events:
            return True

        payload = {
            "bot_id": self.bot_id,
            "bot_name": self.bot_name,
            "events": events,
            "timestamp": time.time(),
        }

        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{central_url}/analytics/collect", json=payload
                    ) as response:
                        if response.status in [200, 201]:
                            logger.info(
                                f"Sent {len(events)} events to central analytics from {self.bot_name}"
                            )
                            return True
                        else:
                            logger.warning(
                                f"Failed to send events to central analytics: {response.status}"
                            )

            except Exception as e:
                logger.error(
                    f"Error sending events to central analytics (attempt {attempt + 1}): {e}"
                )

            if attempt < max_retries - 1:
                await asyncio.sleep(2**attempt)  # Exponential backoff

        return False


class CentralEventCollector:
    """Central event collector for multiple bots"""

    def __init__(self, config: EventCollectorConfig) -> None:
        self.config = config
        self._bot_collectors: Dict[str, BotEventCollector] = {}
        self._running = False
        self._collection_task: Optional[asyncio.Task] = None

    def add_bot(self, bot_id: str, bot_name: str, webhook_url: str) -> None:
        """Add a bot for event collection"""
        collector = BotEventCollector(bot_id, bot_name, webhook_url)
        self._bot_collectors[bot_id] = collector
        logger.info(f"Added bot {bot_name} ({bot_id}) for event collection")

    def remove_bot(self, bot_id: str) -> bool:
        """Remove a bot from event collection"""
        if bot_id in self._bot_collectors:
            del self._bot_collectors[bot_id]
            logger.info(f"Removed bot {bot_id} from event collection")
            return True
        return False

    async def start_collection(self) -> None:
        """Start automatic event collection"""
        if self._running:
            return

        self._running = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Started automatic event collection")

    async def stop_collection(self) -> None:
        """Stop automatic event collection"""
        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped automatic event collection")

    async def _collection_loop(self) -> None:
        """Main collection loop"""
        while self._running:
            try:
                await self._collect_from_all_bots()
                await asyncio.sleep(self.config.collection_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Collection loop error: {e}")
                await asyncio.sleep(self.config.retry_delay)

    async def _collect_from_all_bots(self) -> None:
        """Collect events from all registered bots"""
        if not self._bot_collectors:
            return

        # Collect events from all bots concurrently
        tasks = []
        for collector in self._bot_collectors.values():
            tasks.append(self._collect_from_bot(collector))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log results
            successful = sum(1 for result in results if result is True)
            total = len(results)
            logger.info(
                f"Event collection completed: {successful}/{total} bots successful"
            )

    async def _collect_from_bot(self, collector: BotEventCollector) -> bool:
        """Collect events from a single bot"""
        try:
            # Collect events
            events = await collector.collect_events()

            if events:
                # Send to central analytics
                success = await collector.send_events_to_central(
                    events, self.config.central_analytics_url, self.config.max_retries
                )
                return success
            else:
                return True  # No events to collect is not an error

        except Exception as e:
            logger.error(f"Error collecting from bot {collector.bot_name}: {e}")
            return False

    async def collect_now(self) -> Dict[str, bool]:
        """Manually trigger collection from all bots"""
        results = {}

        for bot_id, collector in self._bot_collectors.items():
            try:
                success = await self._collect_from_bot(collector)
                results[bot_id] = success
            except Exception as e:
                logger.error(f"Manual collection failed for bot {bot_id}: {e}")
                results[bot_id] = False

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return {
            "running": self._running,
            "registered_bots": len(self._bot_collectors),
            "collection_interval": self.config.collection_interval_seconds,
            "batch_size": self.config.batch_size,
            "central_url": self.config.central_analytics_url,
            "bots": [
                {
                    "bot_id": bot_id,
                    "bot_name": collector.bot_name,
                    "webhook_url": collector.webhook_url,
                }
                for bot_id, collector in self._bot_collectors.items()
            ],
        }


class RealTimeEventCollector:
    """Real-time event collector using webhooks"""

    def __init__(self, central_analytics_url: str) -> None:
        self.central_analytics_url = central_analytics_url
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start real-time event processing"""
        if self._running:
            return

        self._running = True
        self._processing_task = asyncio.create_task(self._process_events())
        logger.info("Started real-time event collection")

    async def stop(self) -> None:
        """Stop real-time event processing"""
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped real-time event collection")

    async def receive_event(self, event: Dict[str, Any]) -> None:
        """Receive an event from a bot webhook"""
        await self._event_queue.put(event)

    async def _process_events(self) -> None:
        """Process events from the queue"""
        while self._running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                # Send to central analytics
                await self._send_to_central(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _send_to_central(self, event: Dict[str, Any]) -> None:
        """Send event to central analytics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.central_analytics_url}/analytics/realtime", json=event
                ) as response:
                    if response.status in [200, 201]:
                        logger.debug("Sent real-time event to central analytics")
                    else:
                        logger.warning(
                            f"Failed to send real-time event: {response.status}"
                        )
        except Exception as e:
            logger.error(f"Error sending real-time event: {e}")


class MultiBotEventCollector:
    """Main event collector for multiple bots"""

    def __init__(self, config: EventCollectorConfig) -> None:
        self.config = config
        self.batch_collector = CentralEventCollector(config)
        self.realtime_collector = RealTimeEventCollector(config.central_analytics_url)

    async def start(self) -> None:
        """Start all event collection services"""
        if self.config.enable_batch_collection:
            await self.batch_collector.start_collection()

        if self.config.enable_real_time:
            await self.realtime_collector.start()

        logger.info("Multi-bot event collection started")

    async def stop(self) -> None:
        """Stop all event collection services"""
        await self.batch_collector.stop_collection()
        await self.realtime_collector.stop()
        logger.info("Multi-bot event collection stopped")

    def add_bot(self, bot_id: str, bot_name: str, webhook_url: str) -> None:
        """Add a bot for event collection"""
        self.batch_collector.add_bot(bot_id, bot_name, webhook_url)

    def remove_bot(self, bot_id: str) -> bool:
        """Remove a bot from event collection"""
        return self.batch_collector.remove_bot(bot_id)

    async def collect_now(self) -> Dict[str, bool]:
        """Manually trigger collection from all bots"""
        return await self.batch_collector.collect_now()

    async def receive_realtime_event(self, event: Dict[str, Any]) -> None:
        """Receive a real-time event from a bot"""
        await self.realtime_collector.receive_event(event)

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return {
            "batch_collection": self.batch_collector.get_stats(),
            "realtime_collection": {
                "enabled": self.config.enable_real_time,
                "running": self.realtime_collector._running,
            },
            "config": {
                "central_url": self.config.central_analytics_url,
                "collection_interval": self.config.collection_interval_seconds,
                "batch_size": self.config.batch_size,
                "enable_realtime": self.config.enable_real_time,
                "enable_batch": self.config.enable_batch_collection,
            },
        }
