"""
NEONPAY Web Analytics - Web interface for analytics data collection
Provides HTTP endpoints for bots to send analytics data
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional

from aiohttp import web
from aiohttp.web import Request, Response

logger = logging.getLogger(__name__)


class AnalyticsWebHandler:
    """Web handler for analytics endpoints"""

    def __init__(
        self,
        multi_bot_analytics: Any,
        event_collector: Any,
        webhook_secret: Optional[str] = None,
    ) -> None:
        self.multi_bot_analytics = multi_bot_analytics
        self.event_collector = event_collector
        self.webhook_secret = webhook_secret
        self._event_buffer: List[Dict[str, Any]] = []
        self._buffer_lock = asyncio.Lock()

    def _verify_webhook(self, request: Request) -> bool:
        """Verify webhook signature"""
        if not self.webhook_secret:
            return True  # No secret configured

        signature = request.headers.get("X-Webhook-Secret")
        if not signature:
            return False

        return signature == self.webhook_secret

    async def handle_event_collection(self, request: Request) -> Response:
        """Handle event collection from bots"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            data = await request.json()
            bot_id = data.get("bot_id")
            bot_name = data.get("bot_name")
            events = data.get("events", [])

            if not bot_id or not events:
                return web.json_response(
                    {"status": "error", "message": "Missing bot_id or events"},
                    status=400,
                )

            # Register bot if not already registered
            if self.multi_bot_analytics:
                self.multi_bot_analytics.register_bot(bot_id, bot_name or bot_id)

            # Process events
            processed_count = 0
            for event_data in events:
                try:
                    # Track event in analytics
                    if self.multi_bot_analytics:
                        self.multi_bot_analytics.track_event(
                            event_type=event_data.get("event_type", "unknown"),
                            bot_id=bot_id,
                            user_id=event_data.get("user_id", 0),
                            amount=event_data.get("amount"),
                            product_id=event_data.get("product_id"),
                            metadata=event_data.get("metadata", {}),
                        )

                    processed_count += 1

                except Exception as e:
                    logger.error(f"Error processing event: {e}")

            return web.json_response(
                {
                    "status": "success",
                    "processed_events": processed_count,
                    "message": f"Processed {processed_count} events from {bot_name}",
                }
            )

        except Exception as e:
            logger.error(f"Event collection error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_realtime_event(self, request: Request) -> Response:
        """Handle real-time event from bots"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            event_data = await request.json()

            # Add timestamp if not present
            if "timestamp" not in event_data:
                event_data["timestamp"] = time.time()

            # Send to real-time collector
            if self.event_collector:
                await self.event_collector.receive_realtime_event(event_data)

            return web.json_response(
                {"status": "success", "message": "Real-time event received"}
            )

        except Exception as e:
            logger.error(f"Real-time event error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_analytics_query(self, request: Request) -> Response:
        """Handle analytics queries from bots"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            query_params = request.query
            bot_id = query_params.get("bot_id")
            # period = query_params.get("period", "day")  # Not used
            days = int(query_params.get("days", "30"))

            if not self.multi_bot_analytics:
                return web.json_response(
                    {"status": "error", "message": "Analytics not available"},
                    status=503,
                )

            # Get analytics data
            if bot_id:
                # Bot-specific analytics
                analytics = self.multi_bot_analytics.get_bot_analytics(
                    bot_id, days=days
                )
                if analytics:
                    data = {
                        "bot_id": analytics.bot_id,
                        "bot_name": analytics.bot_name,
                        "total_events": analytics.total_events,
                        "total_users": analytics.total_users,
                        "total_revenue": analytics.total_revenue,
                        "total_transactions": analytics.total_transactions,
                        "conversion_rate": analytics.conversion_rate,
                        "last_activity": analytics.last_activity,
                        "events_by_type": analytics.events_by_type,
                        "revenue_by_product": analytics.revenue_by_product,
                    }
                else:
                    data = {"error": "Bot not found"}
            else:
                # Network analytics
                analytics = self.multi_bot_analytics.get_network_analytics(days=days)
                if analytics:
                    data = {
                        "total_bots": analytics.total_bots,
                        "total_events": analytics.total_events,
                        "total_users": analytics.total_users,
                        "total_revenue": analytics.total_revenue,
                        "total_transactions": analytics.total_transactions,
                        "network_conversion_rate": analytics.network_conversion_rate,
                        "top_performing_bots": analytics.top_performing_bots,
                        "top_products": analytics.top_products,
                        "user_journey": analytics.user_journey,
                        "revenue_trends": analytics.revenue_trends,
                    }
                else:
                    data = {"error": "Network analytics not available"}

            return web.json_response(
                {"status": "success", "data": data, "timestamp": time.time()}
            )

        except Exception as e:
            logger.error(f"Analytics query error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_analytics_export(self, request: Request) -> Response:
        """Handle analytics data export"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            query_params = request.query
            format_type = query_params.get("format", "json")
            # period = query_params.get("period", "day")  # Not used
            days = int(query_params.get("days", "30"))

            if not self.multi_bot_analytics:
                return web.json_response(
                    {"status": "error", "message": "Analytics not available"},
                    status=503,
                )

            # Export analytics data
            exported_data = self.multi_bot_analytics.export_network_analytics(
                format_type=format_type, days=days
            )

            if exported_data:
                if format_type.lower() == "json":
                    return web.json_response(json.loads(exported_data))
                elif format_type.lower() == "csv":
                    return web.Response(
                        text=exported_data,
                        content_type="text/csv",
                        headers={
                            "Content-Disposition": "attachment; filename=analytics.csv"
                        },
                    )
                else:
                    return web.Response(text=exported_data)
            else:
                return web.json_response(
                    {"status": "error", "message": "Export failed"}, status=500
                )

        except Exception as e:
            logger.error(f"Analytics export error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_analytics_status(self, request: Request) -> Response:
        """Handle analytics status requests"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            status_data = {
                "analytics_enabled": self.multi_bot_analytics is not None,
                "event_collector_enabled": self.event_collector is not None,
                "timestamp": time.time(),
            }

            if self.multi_bot_analytics:
                analytics_stats = self.multi_bot_analytics.get_stats()
                status_data.update(analytics_stats)

            if self.event_collector:
                collector_stats = self.event_collector.get_stats()
                status_data["collector_stats"] = collector_stats

            return web.json_response(status_data)

        except Exception as e:
            logger.error(f"Analytics status error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)


def create_analytics_app(
    multi_bot_analytics: Any, event_collector: Any, webhook_secret: Optional[str] = None
) -> web.Application:
    """Create web application for analytics"""
    handler = AnalyticsWebHandler(multi_bot_analytics, event_collector, webhook_secret)

    app = web.Application()

    # Add routes
    app.router.add_post("/analytics/collect", handler.handle_event_collection)
    app.router.add_post("/analytics/realtime", handler.handle_realtime_event)
    app.router.add_get("/analytics/query", handler.handle_analytics_query)
    app.router.add_get("/analytics/export", handler.handle_analytics_export)
    app.router.add_get("/analytics/status", handler.handle_analytics_status)

    # Health check endpoint
    async def health_check(request: Request) -> Response:
        return web.json_response(
            {"status": "healthy", "service": "analytics", "timestamp": time.time()}
        )

    app.router.add_get("/health", health_check)

    return app


async def run_analytics_server(
    multi_bot_analytics: Any,
    event_collector: Any,
    host: str = "localhost",
    port: int = 8081,
    webhook_secret: Optional[str] = None,
) -> None:
    """Run analytics web server"""
    app = create_analytics_app(multi_bot_analytics, event_collector, webhook_secret)

    logger.info(f"Starting analytics server on {host}:{port}")

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info("Analytics server started successfully")

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Analytics server stopped by user")
    finally:
        await runner.cleanup()
