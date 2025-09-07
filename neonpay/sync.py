"""
NEONPAY Sync - Multi-bot synchronization system
Allows synchronization of payment stages, analytics, and settings between multiple bots
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Synchronization direction"""

    PUSH = "push"  # Send data to target
    PULL = "pull"  # Get data from target
    BIDIRECTIONAL = "bidirectional"  # Sync both ways


class SyncStatus(Enum):
    """Synchronization status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ConflictResolution(Enum):
    """Conflict resolution strategy"""

    ASK_USER = "ask_user"  # Ask user to choose
    SOURCE_WINS = "source_wins"  # Source data overwrites target
    TARGET_WINS = "target_wins"  # Target data overwrites source
    MERGE = "merge"  # Try to merge data
    SKIP = "skip"  # Skip conflicting items


@dataclass
class SyncConfig:
    """Synchronization configuration"""

    target_bot_token: str
    target_bot_name: str = "Target Bot"
    sync_payment_stages: bool = True
    sync_promo_codes: bool = True
    sync_subscriptions: bool = True
    sync_analytics: bool = False  # Usually disabled for privacy
    sync_templates: bool = True
    sync_settings: bool = True
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    conflict_resolution: ConflictResolution = ConflictResolution.ASK_USER
    auto_sync: bool = False
    sync_interval_minutes: int = 60
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None


@dataclass
class SyncResult:
    """Synchronization result"""

    sync_id: str
    status: SyncStatus
    start_time: float
    end_time: Optional[float] = None
    items_synced: Dict[str, int] = field(default_factory=dict)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncConflict:
    """Synchronization conflict"""

    item_type: str
    item_id: str
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    conflict_reason: str
    resolution: Optional[ConflictResolution] = None


class BotConnector:
    """Connects to remote bots for synchronization"""

    def __init__(self, bot_token: str, bot_name: str = "Remote Bot") -> None:
        self.bot_token = bot_token
        self.bot_name = bot_name
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getMe") as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result", {})
                        return result if isinstance(result, dict) else {}
                    else:
                        raise Exception(f"Failed to get bot info: {response.status}")
        except Exception as e:
            logger.error(f"Failed to get bot info for {self.bot_name}: {e}")
            return {}

    async def send_data(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Send data to bot webhook endpoint"""
        if not endpoint:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=data) as response:
                    return response.status in [200, 201]
        except Exception as e:
            logger.error(f"Failed to send data to {endpoint}: {e}")
            return False

    async def receive_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Receive data from bot webhook endpoint"""
        if not endpoint:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data if isinstance(data, dict) else None
                    else:
                        return None
        except Exception as e:
            logger.error(f"Failed to receive data from {endpoint}: {e}")
            return None


class DataSerializer:
    """Serializes and deserializes data for synchronization"""

    @staticmethod
    def serialize_payment_stages(stages: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize payment stages for sync"""
        serialized = {}
        for stage_id, stage in stages.items():
            if hasattr(stage, "__dict__"):
                serialized[stage_id] = {
                    "title": stage.title,
                    "description": stage.description,
                    "price": stage.price,
                    "label": stage.label,
                    "photo_url": stage.photo_url,
                    "payload": stage.payload,
                    "start_parameter": stage.start_parameter,
                    "created_at": getattr(stage, "created_at", time.time()),
                }
            else:
                serialized[stage_id] = stage
        return serialized

    @staticmethod
    def deserialize_payment_stages(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize payment stages from sync"""
        return data  # Already in correct format

    @staticmethod
    def serialize_promo_codes(promo_codes: List[Any]) -> List[Dict[str, Any]]:
        """Serialize promo codes for sync"""
        serialized = []
        for promo in promo_codes:
            if hasattr(promo, "__dict__"):
                serialized.append(
                    {
                        "code": promo.code,
                        "discount_type": (
                            promo.discount_type.value
                            if hasattr(promo.discount_type, "value")
                            else str(promo.discount_type)
                        ),
                        "discount_value": promo.discount_value,
                        "max_uses": promo.max_uses,
                        "expires_at": promo.expires_at,
                        "min_amount": promo.min_amount,
                        "max_discount": promo.max_discount,
                        "user_limit": promo.user_limit,
                        "active": promo.active,
                        "description": promo.description,
                        "created_at": getattr(promo, "created_at", time.time()),
                    }
                )
            else:
                serialized.append(promo)
        return serialized

    @staticmethod
    def serialize_subscriptions(subscriptions: List[Any]) -> List[Dict[str, Any]]:
        """Serialize subscriptions for sync"""
        serialized = []
        for sub in subscriptions:
            if hasattr(sub, "__dict__"):
                serialized.append(
                    {
                        "user_id": sub.user_id,
                        "plan_id": sub.plan_id,
                        "status": (
                            sub.status.value
                            if hasattr(sub.status, "value")
                            else str(sub.status)
                        ),
                        "start_date": sub.start_date,
                        "end_date": sub.end_date,
                        "auto_renew": sub.auto_renew,
                        "created_at": getattr(sub, "created_at", time.time()),
                    }
                )
            else:
                serialized.append(sub)
        return serialized


class ConflictResolver:
    """Resolves conflicts during synchronization"""

    def __init__(
        self, strategy: ConflictResolution = ConflictResolution.ASK_USER
    ) -> None:
        self.strategy = strategy

    def resolve_conflict(self, conflict: SyncConflict) -> Optional[Dict[str, Any]]:
        """Resolve a synchronization conflict"""
        if self.strategy == ConflictResolution.SOURCE_WINS:
            return conflict.source_data
        elif self.strategy == ConflictResolution.TARGET_WINS:
            return conflict.target_data
        elif self.strategy == ConflictResolution.MERGE:
            return self._merge_data(conflict.source_data, conflict.target_data)
        elif self.strategy == ConflictResolution.SKIP:
            return None  # Skip this item
        else:  # ASK_USER
            return self._ask_user_resolution(conflict)

    def _merge_data(
        self, source: Dict[str, Any], target: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge source and target data"""
        merged = target.copy()

        # Merge non-conflicting fields
        for key, value in source.items():
            if key not in target or target[key] == value:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(target.get(key), dict):
                merged[key] = self._merge_data(value, target[key])
            else:
                # Conflict - use source value
                merged[key] = value

        return merged

    def _ask_user_resolution(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Ask user to resolve conflict (placeholder implementation)"""
        logger.warning(
            f"Conflict resolution needed for {conflict.item_type}:{conflict.item_id}"
        )
        logger.warning(f"Source: {conflict.source_data}")
        logger.warning(f"Target: {conflict.target_data}")
        logger.warning(f"Reason: {conflict.conflict_reason}")

        # For now, default to source wins
        return conflict.source_data


class SyncManager:
    """Main synchronization manager"""

    def __init__(self, neonpay_instance: Any, config: SyncConfig) -> None:
        self.neonpay = neonpay_instance
        self.config = config
        self.connector = BotConnector(config.target_bot_token, config.target_bot_name)
        self.serializer = DataSerializer()
        self.conflict_resolver = ConflictResolver(config.conflict_resolution)
        self._sync_history: List[SyncResult] = []
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None

    async def start_auto_sync(self) -> None:
        """Start automatic synchronization"""
        if not self.config.auto_sync:
            return

        if self._running:
            return

        self._running = True
        self._sync_task = asyncio.create_task(self._auto_sync_loop())
        logger.info(f"Auto-sync started for {self.config.target_bot_name}")

    async def stop_auto_sync(self) -> None:
        """Stop automatic synchronization"""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Auto-sync stopped for {self.config.target_bot_name}")

    async def _auto_sync_loop(self) -> None:
        """Main auto-sync loop"""
        while self._running:
            try:
                await asyncio.sleep(self.config.sync_interval_minutes * 60)
                if self._running:
                    await self.sync_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-sync error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def sync_all(self) -> SyncResult:
        """Synchronize all configured data"""
        sync_id = f"sync_{int(time.time())}"
        result = SyncResult(
            sync_id=sync_id, status=SyncStatus.IN_PROGRESS, start_time=time.time()
        )

        try:
            logger.info(f"Starting sync {sync_id} with {self.config.target_bot_name}")

            # Sync payment stages
            if self.config.sync_payment_stages:
                stages_result = await self.sync_payment_stages()
                result.items_synced["payment_stages"] = stages_result.get("synced", 0)
                result.conflicts.extend(stages_result.get("conflicts", []))

            # Sync promo codes
            if self.config.sync_promo_codes:
                promo_result = await self.sync_promo_codes()
                result.items_synced["promo_codes"] = promo_result.get("synced", 0)
                result.conflicts.extend(promo_result.get("conflicts", []))

            # Sync subscriptions
            if self.config.sync_subscriptions:
                sub_result = await self.sync_subscriptions()
                result.items_synced["subscriptions"] = sub_result.get("synced", 0)
                result.conflicts.extend(sub_result.get("conflicts", []))

            # Sync templates
            if self.config.sync_templates:
                template_result = await self.sync_templates()
                result.items_synced["templates"] = template_result.get("synced", 0)
                result.conflicts.extend(template_result.get("conflicts", []))

            # Sync settings
            if self.config.sync_settings:
                settings_result = await self.sync_settings()
                result.items_synced["settings"] = settings_result.get("synced", 0)
                result.conflicts.extend(settings_result.get("conflicts", []))

            result.status = SyncStatus.COMPLETED
            result.end_time = time.time()

            logger.info(f"Sync {sync_id} completed successfully")

        except Exception as e:
            result.status = SyncStatus.FAILED
            result.end_time = time.time()
            result.errors.append(str(e))
            logger.error(f"Sync {sync_id} failed: {e}")

        self._sync_history.append(result)
        return result

    async def sync_payment_stages(self) -> Dict[str, Any]:
        """Synchronize payment stages"""
        logger.info("Syncing payment stages...")

        # Get local stages
        local_stages = self.neonpay.list_payment_stages()
        local_data = self.serializer.serialize_payment_stages(local_stages)

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/payment_stages",
                {"action": "sync", "data": local_data},
            )
            if not success:
                logger.warning("Failed to send payment stages to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/payment_stages"
            )

        # Process conflicts and apply changes
        conflicts: List[Dict[str, Any]] = []
        synced_count = 0

        if target_data:
            for stage_id, stage_data in target_data.items():
                if stage_id in local_stages:
                    # Check for conflicts
                    local_stage = local_stages[stage_id]
                    if self._has_conflict(local_stage, stage_data):
                        conflict = SyncConflict(
                            item_type="payment_stage",
                            item_id=stage_id,
                            source_data=local_data.get(stage_id, {}),
                            target_data=stage_data,
                            conflict_reason="Data mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            # Apply resolved data
                            from .core import PaymentStage

                            stage = PaymentStage(
                                title=resolved_data["title"],
                                description=resolved_data["description"],
                                price=resolved_data["price"],
                                label=resolved_data["label"],
                                photo_url=resolved_data["photo_url"],
                                payload=resolved_data["payload"],
                                start_parameter=resolved_data["start_parameter"],
                            )
                            self.neonpay.create_payment_stage(stage_id, stage)
                            synced_count += 1
                    else:
                        # No conflict, update if needed
                        synced_count += 1
                else:
                    # New stage from target
                    from .core import PaymentStage

                    stage = PaymentStage(
                        title=stage_data["title"],
                        description=stage_data["description"],
                        price=stage_data["price"],
                        label=stage_data["label"],
                        photo_url=stage_data["photo_url"],
                        payload=stage_data["payload"],
                        start_parameter=stage_data["start_parameter"],
                    )
                    self.neonpay.create_payment_stage(stage_id, stage)
                    synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    async def sync_promo_codes(self) -> Dict[str, Any]:
        """Synchronize promo codes"""
        logger.info("Syncing promo codes...")

        # Get local promo codes
        local_promos = []
        if hasattr(self.neonpay, "promotions") and self.neonpay.promotions:
            local_promos = self.neonpay.promotions.list_promo_codes(active_only=False)

        local_data = self.serializer.serialize_promo_codes(local_promos)

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/promo_codes",
                {"action": "sync", "data": local_data},
            )
            if not success:
                logger.warning("Failed to send promo codes to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/promo_codes"
            )

        # Process conflicts and apply changes
        conflicts: List[Dict[str, Any]] = []
        synced_count = 0

        if (
            target_data
            and hasattr(self.neonpay, "promotions")
            and self.neonpay.promotions
        ):
            promo_system = self.neonpay.promotions

            # target_data is a dict, extract promo codes
            # Check if it's a dict of promo codes or a single promo code
            if "promo_codes" in target_data:
                # If it has a promo_codes key, extract the list
                promo_list = target_data["promo_codes"]
                if not isinstance(promo_list, list):
                    logger.warning("promo_codes is not a list")
                    return {"synced": 0, "conflicts": []}
            else:
                # If it's a single promo code dict, wrap it in a list
                promo_list = [target_data]

            for promo_data in promo_list:
                if not isinstance(promo_data, dict):
                    logger.warning(f"Invalid promo data format: {promo_data}")
                    continue
                code = promo_data["code"]
                existing_promo = promo_system.get_promo_code(code)

                if existing_promo:
                    # Check for conflicts
                    if self._has_conflict(existing_promo, promo_data):
                        conflict = SyncConflict(
                            item_type="promo_code",
                            item_id=code,
                            source_data=self.serializer.serialize_promo_codes(
                                [existing_promo]
                            )[0],
                            target_data=promo_data,
                            conflict_reason="Data mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            # Update promo code
                            from .promotions import DiscountType

                            promo_system.create_promo_code(
                                code=resolved_data["code"],
                                discount_type=DiscountType(
                                    resolved_data["discount_type"]
                                ),
                                discount_value=resolved_data["discount_value"],
                                **{
                                    k: v
                                    for k, v in resolved_data.items()
                                    if k
                                    not in ["code", "discount_type", "discount_value"]
                                },
                            )
                            synced_count += 1
                    else:
                        synced_count += 1
                else:
                    # New promo code from target
                    from .promotions import DiscountType

                    promo_system.create_promo_code(
                        code=promo_data["code"],
                        discount_type=DiscountType(promo_data["discount_type"]),
                        discount_value=promo_data["discount_value"],
                        **{
                            k: v
                            for k, v in promo_data.items()
                            if k not in ["code", "discount_type", "discount_value"]
                        },
                    )
                    synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    async def sync_subscriptions(self) -> Dict[str, Any]:
        """Synchronize subscriptions"""
        logger.info("Syncing subscriptions...")

        # Get local subscriptions
        # local_subs = []  # Not used
        if hasattr(self.neonpay, "subscriptions") and self.neonpay.subscriptions:
            # This would need to be implemented in the subscription manager
            pass

        # local_data = self.serializer.serialize_subscriptions(local_subs)  # Not used

        # Similar implementation to promo codes...
        return {"synced": 0, "conflicts": []}

    async def sync_templates(self) -> Dict[str, Any]:
        """Synchronize templates"""
        logger.info("Syncing templates...")

        # Get local templates
        local_templates = {}
        if hasattr(self.neonpay, "templates") and self.neonpay.templates:
            template_manager = self.neonpay.templates
            templates = template_manager.list_templates()
            for template in templates:
                local_templates[template.name] = template_manager.export_template(
                    template, "json"
                )

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/templates",
                {"action": "sync", "data": local_templates},
            )
            if not success:
                logger.warning("Failed to send templates to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/templates"
            )

        # Process conflicts and apply changes
        conflicts: List[Dict[str, Any]] = []
        synced_count = 0

        if (
            target_data
            and hasattr(self.neonpay, "templates")
            and self.neonpay.templates
        ):
            template_manager = self.neonpay.templates

            for template_name, template_data in target_data.items():
                existing_template = template_manager.get_template(template_name)

                if existing_template:
                    # Check for conflicts
                    existing_json = template_manager.export_template(
                        existing_template, "json"
                    )
                    if existing_json != template_data:
                        conflict = SyncConflict(
                            item_type="template",
                            item_id=template_name,
                            source_data=json.loads(existing_json),
                            target_data=json.loads(template_data),
                            conflict_reason="Template data mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            # Import resolved template
                            template_manager.import_template(json.dumps(resolved_data))
                            synced_count += 1
                    else:
                        synced_count += 1
                else:
                    # New template from target
                    template_manager.import_template(template_data)
                    synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    async def sync_settings(self) -> Dict[str, Any]:
        """Synchronize bot settings"""
        logger.info("Syncing settings...")

        # Get local settings
        local_settings = {
            "thank_you_message": getattr(self.neonpay, "thank_you_message", ""),
            "max_stages": getattr(self.neonpay, "_max_stages", 100),
            "logging_enabled": getattr(self.neonpay, "_enable_logging", True),
        }

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/settings",
                {"action": "sync", "data": local_settings},
            )
            if not success:
                logger.warning("Failed to send settings to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/settings"
            )

        # Apply target settings
        synced_count = 0
        conflicts: List[Dict[str, Any]] = []

        if target_data:
            for key, value in target_data.items():
                if hasattr(self.neonpay, key):
                    current_value = getattr(self.neonpay, key)
                    if current_value != value:
                        # Conflict detected
                        conflict = SyncConflict(
                            item_type="setting",
                            item_id=key,
                            source_data={key: current_value},
                            target_data={key: value},
                            conflict_reason="Setting value mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            setattr(self.neonpay, key, resolved_data[key])
                            synced_count += 1
                    else:
                        synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    def _has_conflict(self, local_item: Any, target_item: Dict[str, Any]) -> bool:
        """Check if there's a conflict between local and target items"""
        if isinstance(local_item, dict):
            local_dict = local_item
        else:
            local_dict = local_item.__dict__ if hasattr(local_item, "__dict__") else {}

        # Compare key fields
        key_fields = ["title", "description", "price", "code", "name"]
        for field_name in key_fields:
            if field_name in local_dict and field_name in target_item:
                if local_dict[field_name] != target_item[field_name]:
                    return True

        return False

    def get_sync_history(self) -> List[SyncResult]:
        """Get synchronization history"""
        return self._sync_history.copy()

    def get_last_sync(self) -> Optional[SyncResult]:
        """Get last synchronization result"""
        return self._sync_history[-1] if self._sync_history else None

    def get_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        if not self._sync_history:
            return {"total_syncs": 0}

        total_syncs = len(self._sync_history)
        successful_syncs = len(
            [s for s in self._sync_history if s.status == SyncStatus.COMPLETED]
        )
        failed_syncs = len(
            [s for s in self._sync_history if s.status == SyncStatus.FAILED]
        )

        total_items_synced = sum(
            sum(s.items_synced.values()) for s in self._sync_history
        )

        total_conflicts = sum(len(s.conflicts) for s in self._sync_history)

        return {
            "total_syncs": total_syncs,
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "success_rate": (
                (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
            ),
            "total_items_synced": total_items_synced,
            "total_conflicts": total_conflicts,
            "last_sync": (
                self._sync_history[-1].start_time if self._sync_history else None
            ),
            "auto_sync_enabled": self.config.auto_sync,
            "sync_interval_minutes": self.config.sync_interval_minutes,
        }


class MultiBotSyncManager:
    """Manages synchronization between multiple bots"""

    def __init__(self, neonpay_instance: Any) -> None:
        self.neonpay = neonpay_instance
        self._sync_managers: Dict[str, SyncManager] = {}

    def add_bot(self, config: SyncConfig) -> SyncManager:
        """Add a bot for synchronization"""
        sync_manager = SyncManager(self.neonpay, config)
        self._sync_managers[config.target_bot_name] = sync_manager
        return sync_manager

    def remove_bot(self, bot_name: str) -> bool:
        """Remove a bot from synchronization"""
        if bot_name in self._sync_managers:
            sync_manager = self._sync_managers[bot_name]
            asyncio.create_task(sync_manager.stop_auto_sync())
            del self._sync_managers[bot_name]
            return True
        return False

    async def sync_all_bots(self) -> Dict[str, SyncResult]:
        """Synchronize with all configured bots"""
        results = {}

        for bot_name, sync_manager in self._sync_managers.items():
            try:
                result = await sync_manager.sync_all()
                results[bot_name] = result
            except Exception as e:
                logger.error(f"Failed to sync with {bot_name}: {e}")
                results[bot_name] = SyncResult(
                    sync_id=f"failed_{int(time.time())}",
                    status=SyncStatus.FAILED,
                    start_time=time.time(),
                    end_time=time.time(),
                    errors=[str(e)],
                )

        return results

    async def start_auto_sync_all(self) -> None:
        """Start automatic synchronization for all bots"""
        for sync_manager in self._sync_managers.values():
            await sync_manager.start_auto_sync()

    async def stop_auto_sync_all(self) -> None:
        """Stop automatic synchronization for all bots"""
        for sync_manager in self._sync_managers.values():
            await sync_manager.stop_auto_sync()

    def get_all_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics for all bots"""
        stats = {}
        for bot_name, sync_manager in self._sync_managers.items():
            stats[bot_name] = sync_manager.get_sync_stats()
        return stats

    def list_configured_bots(self) -> List[str]:
        """List all configured bots"""
        return list(self._sync_managers.keys())
