"""
NEONPAY Backup - Data backup and synchronization system
Provides automatic backups, data migration, and synchronization
"""

import asyncio
import json
import logging
import os
import sys
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiofiles  # type: ignore

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backups"""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(Enum):
    """Backup status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackupConfig:
    """Backup configuration"""

    backup_directory: str = "./backups"
    max_backups: int = 10
    compression: bool = True
    encryption: bool = False
    encryption_key: Optional[str] = None
    auto_backup: bool = True
    backup_interval_hours: int = 24
    include_analytics: bool = True
    include_logs: bool = True
    include_templates: bool = True


@dataclass
class BackupInfo:
    """Backup information"""

    backup_id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    size_bytes: int = 0
    file_path: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncConfig:
    """Synchronization configuration"""

    target_bot_token: str
    sync_payment_stages: bool = True
    sync_analytics: bool = True
    sync_templates: bool = True
    sync_settings: bool = True
    conflict_resolution: str = "ask"  # ask, source, target


class DataCollector:
    """Collects data for backup"""

    def __init__(self, neonpay_instance: Any) -> None:
        self.neonpay = neonpay_instance

    async def collect_payment_data(self) -> Dict[str, Any]:
        """Collect payment-related data"""
        data: Dict[str, Any] = {
            "payment_stages": {},
            "payment_callbacks": [],
            "promo_codes": [],
            "subscriptions": [],
            "security_data": {},
        }

        # Collect payment stages
        if hasattr(self.neonpay, "list_payment_stages"):
            stages = self.neonpay.list_payment_stages()
            for stage_id, stage in stages.items():
                data["payment_stages"][stage_id] = {
                    "title": stage.title,
                    "description": stage.description,
                    "price": stage.price,
                    "label": stage.label,
                    "photo_url": stage.photo_url,
                    "payload": stage.payload,
                    "start_parameter": stage.start_parameter,
                }

        # Collect promo codes
        if hasattr(self.neonpay, "promotions") and self.neonpay.promotions:
            promo_system = self.neonpay.promotions
            if hasattr(promo_system, "list_promo_codes"):
                promo_codes = promo_system.list_promo_codes(active_only=False)
                data["promo_codes"] = [
                    {
                        "code": promo.code,
                        "discount_type": promo.discount_type.value,
                        "discount_value": promo.discount_value,
                        "max_uses": promo.max_uses,
                        "expires_at": promo.expires_at,
                        "min_amount": promo.min_amount,
                        "max_discount": promo.max_discount,
                        "user_limit": promo.user_limit,
                        "active": promo.active,
                        "description": promo.description,
                        "used_count": promo.used_count,
                    }
                    for promo in promo_codes
                ]

        # Collect subscriptions
        if hasattr(self.neonpay, "subscriptions") and self.neonpay.subscriptions:
            subscription_manager = self.neonpay.subscriptions
            if hasattr(subscription_manager, "get_all_subscriptions"):
                subscriptions = subscription_manager.get_all_subscriptions()
                data["subscriptions"] = [
                    {
                        "user_id": sub.user_id,
                        "plan_id": sub.plan_id,
                        "status": sub.status.value,
                        "start_date": sub.start_date,
                        "end_date": sub.end_date,
                        "auto_renew": sub.auto_renew,
                    }
                    for sub in subscriptions
                ]

        # Collect security data
        if hasattr(self.neonpay, "security") and self.neonpay.security:
            security_manager = self.neonpay.security
            if hasattr(security_manager, "get_security_stats"):
                data["security_data"] = security_manager.get_security_stats()

        return data

    async def collect_analytics_data(self) -> Dict[str, Any]:
        """Collect analytics data"""
        data: Dict[str, Any] = {
            "events": [],
            "user_sessions": {},
            "product_views": {},
            "conversion_funnel": {},
        }

        if hasattr(self.neonpay, "analytics") and self.neonpay.analytics:
            analytics = self.neonpay.analytics
            if hasattr(analytics, "collector"):
                collector = analytics.collector
                # Collect events
                events = collector.get_events()
                data["events"] = [
                    {
                        "event_type": event.event_type,
                        "user_id": event.user_id,
                        "amount": event.amount,
                        "stage_id": event.stage_id,
                        "metadata": event.metadata,
                        "timestamp": event.timestamp,
                        "session_id": event.session_id,
                    }
                    for event in events
                ]

                # Collect user sessions
                data["user_sessions"] = dict(collector._user_sessions)
                # Collect product views
                data["product_views"] = dict(collector._product_views)
                # Collect conversion funnel
                data["conversion_funnel"] = dict(collector._conversion_funnel)

        return data

    async def collect_template_data(self) -> Dict[str, Any]:
        """Collect template data"""
        data: Dict[str, Any] = {"templates": {}, "custom_templates": []}

        if hasattr(self.neonpay, "templates") and self.neonpay.templates:
            template_manager = self.neonpay.templates
            if hasattr(template_manager, "list_templates"):
                templates = template_manager.list_templates()
                for template in templates:
                    data["templates"][template.name] = {
                        "name": template.name,
                        "description": template.description,
                        "template_type": template.template_type.value,
                        "theme": {
                            "primary_color": template.theme.primary_color,
                            "secondary_color": template.theme.secondary_color,
                            "accent_color": template.theme.accent_color,
                        },
                        "categories": [
                            {
                                "id": cat.id,
                                "name": cat.name,
                                "description": cat.description,
                                "icon": cat.icon,
                                "products": [
                                    {
                                        "id": prod.id,
                                        "name": prod.name,
                                        "description": prod.description,
                                        "price": prod.price,
                                        "category": prod.category,
                                        "features": prod.features,
                                        "tags": prod.tags,
                                    }
                                    for prod in cat.products
                                ],
                            }
                            for cat in template.categories
                        ],
                    }

        return data

    async def collect_all_data(self) -> Dict[str, Any]:
        """Collect all data for backup"""
        return {
            "backup_info": {
                "created_at": datetime.now().isoformat(),
                "neonpay_version": getattr(self.neonpay, "__version__", "unknown"),
                "backup_type": "full",
            },
            "payment_data": await self.collect_payment_data(),
            "analytics_data": await self.collect_analytics_data(),
            "template_data": await self.collect_template_data(),
            "system_info": {
                "python_version": sys.version,
                "platform": os.name,
                "timestamp": time.time(),
            },
        }


class BackupManager:
    """Manages backup operations"""

    def __init__(self, neonpay_instance: Any, config: BackupConfig) -> None:
        self.neonpay = neonpay_instance
        self.config = config
        self.data_collector = DataCollector(neonpay_instance)
        self._backups: List[BackupInfo] = []
        self._load_existing_backups()
        # Ensure backup directory exists
        os.makedirs(self.config.backup_directory, exist_ok=True)

    def _load_existing_backups(self) -> None:
        """Load existing backup information"""
        backup_info_file = os.path.join(
            self.config.backup_directory, "backup_info.json"
        )
        if os.path.exists(backup_info_file):
            try:
                with open(backup_info_file, "r", encoding="utf-8") as f:
                    backup_data = json.load(f)
                    for backup_info in backup_data.get("backups", []):
                        self._backups.append(
                            BackupInfo(
                                backup_id=backup_info["backup_id"],
                                backup_type=BackupType(backup_info["backup_type"]),
                                status=BackupStatus(backup_info["status"]),
                                created_at=datetime.fromisoformat(
                                    backup_info["created_at"]
                                ),
                                size_bytes=backup_info.get("size_bytes", 0),
                                file_path=backup_info.get("file_path", ""),
                                description=backup_info.get("description", ""),
                                metadata=backup_info.get("metadata", {}),
                            )
                        )
            except Exception as e:
                logger.error(f"Failed to load backup info: {e}")

    def _save_backup_info(self) -> None:
        """Save backup information to file"""
        backup_info_file = os.path.join(
            self.config.backup_directory, "backup_info.json"
        )
        backup_data = {
            "backups": [
                {
                    "backup_id": backup.backup_id,
                    "backup_type": backup.backup_type.value,
                    "status": backup.status.value,
                    "created_at": backup.created_at.isoformat(),
                    "size_bytes": backup.size_bytes,
                    "file_path": backup.file_path,
                    "description": backup.description,
                    "metadata": backup.metadata,
                }
                for backup in self._backups
            ]
        }

        try:
            with open(backup_info_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save backup info: {e}")

    async def create_backup(
        self, backup_type: BackupType = BackupType.FULL, description: str = ""
    ) -> BackupInfo:
        """Create a new backup"""
        backup_id = f"backup_{int(time.time())}"
        backup_info = BackupInfo(
            backup_id=backup_id,
            backup_type=backup_type,
            status=BackupStatus.IN_PROGRESS,
            created_at=datetime.now(),
            description=description,
        )

        self._backups.append(backup_info)
        try:
            # Collect data
            logger.info(f"Creating backup: {backup_id}")
            data = await self.data_collector.collect_all_data()
            # Save backup file
            backup_filename = f"{backup_id}.json"
            if self.config.compression:
                backup_filename += ".zip"
            backup_path = os.path.join(self.config.backup_directory, backup_filename)
            if self.config.compression:
                # Create compressed backup
                with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.writestr(
                        "backup_data.json",
                        json.dumps(data, indent=2, ensure_ascii=False),
                    )
            else:
                # Create uncompressed backup
                async with aiofiles.open(backup_path, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(data, indent=2, ensure_ascii=False))

            # Update backup info
            backup_info.status = BackupStatus.COMPLETED
            backup_info.file_path = backup_path
            backup_info.size_bytes = os.path.getsize(backup_path)
            # Clean up old backups
            await self._cleanup_old_backups()
            # Save backup info
            self._save_backup_info()
            logger.info(f"Backup created successfully: {backup_id}")
            return backup_info
        except Exception as e:
            backup_info.status = BackupStatus.FAILED
            logger.error(f"Failed to create backup: {e}")
            raise

    async def restore_backup(self, backup_id: str) -> bool:
        """Restore from backup"""
        backup_info = next((b for b in self._backups if b.backup_id == backup_id), None)
        if not backup_info:
            raise ValueError(f"Backup not found: {backup_id}")
        if backup_info.status != BackupStatus.COMPLETED:
            raise ValueError(f"Backup is not completed: {backup_info.status}")
        try:
            logger.info(f"Restoring backup: {backup_id}")
            # Load backup data
            if self.config.compression and backup_info.file_path.endswith(".zip"):
                with zipfile.ZipFile(backup_info.file_path, "r") as zipf:
                    data = json.loads(zipf.read("backup_data.json"))
            else:
                async with aiofiles.open(
                    backup_info.file_path, "r", encoding="utf-8"
                ) as f:
                    data = json.loads(await f.read())

            # Restore payment stages
            if "payment_data" in data and "payment_stages" in data["payment_data"]:
                for stage_id, stage_data in data["payment_data"][
                    "payment_stages"
                ].items():
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

            # Restore promo codes
            if "payment_data" in data and "promo_codes" in data["payment_data"]:
                if hasattr(self.neonpay, "promotions") and self.neonpay.promotions:
                    promo_system = self.neonpay.promotions
                    for promo_data in data["payment_data"]["promo_codes"]:
                        from .promotions import DiscountType

                        promo_system.create_promo_code(
                            code=promo_data["code"],
                            discount_type=DiscountType(promo_data["discount_type"]),
                            discount_value=promo_data["discount_value"],
                            max_uses=promo_data["max_uses"],
                            expires_at=promo_data["expires_at"],
                            min_amount=promo_data["min_amount"],
                            max_discount=promo_data["max_discount"],
                            user_limit=promo_data["user_limit"],
                            description=promo_data["description"],
                        )

            logger.info(f"Backup restored successfully: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    async def _cleanup_old_backups(self) -> None:
        """Clean up old backups based on max_backups setting"""
        if len(self._backups) <= self.config.max_backups:
            return
        # Sort by creation date (oldest first)
        sorted_backups = sorted(self._backups, key=lambda b: b.created_at)
        # Remove oldest backups
        backups_to_remove = sorted_backups[: -self.config.max_backups]
        for backup in backups_to_remove:
            try:
                if os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                self._backups.remove(backup)
                logger.info(f"Removed old backup: {backup.backup_id}")
            except Exception as e:
                logger.error(f"Failed to remove backup {backup.backup_id}: {e}")

    def list_backups(self) -> List[BackupInfo]:
        """List all available backups"""
        return sorted(self._backups, key=lambda b: b.created_at, reverse=True)

    def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """Get backup information by ID"""
        return next((b for b in self._backups if b.backup_id == backup_id), None)

    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup"""
        backup_info = self.get_backup_info(backup_id)
        if not backup_info:
            return False
        try:
            if os.path.exists(backup_info.file_path):
                os.remove(backup_info.file_path)
            self._backups.remove(backup_info)
            self._save_backup_info()
            logger.info(f"Backup deleted: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False


class SyncManager:
    """Manages synchronization between bots"""

    def __init__(self, neonpay_instance: Any, config: SyncConfig) -> None:
        self.neonpay = neonpay_instance
        self.config = config

    async def sync_with_bot(self, target_bot_token: str) -> Dict[str, Any]:
        """Synchronize data with another bot"""
        try:
            logger.info(f"Starting sync with bot: {target_bot_token[:10]}...")
            # Placeholder - в реальности нужно создать bot instance
            target_neonpay: Optional[Any] = None  

            sync_results: Dict[str, Any] = {
                "payment_stages": 0,
                "promo_codes": 0,
                "templates": 0,
                "errors": [],
            }

            # Sync payment stages
            if self.config.sync_payment_stages:
                try:
                    if target_neonpay is not None:
                        stages = self.neonpay.list_payment_stages()
                        for stage_id, stage in stages.items():
                            target_neonpay.create_payment_stage(stage_id, stage)
                            sync_results["payment_stages"] += 1
                    else:
                        logger.info("Simulating payment stages sync (no target bot)")
                        sync_results["errors"].append(
                            "Target bot instance not available - sync simulated"
                        )
                except Exception as e:
                    sync_results["errors"].append(f"Payment stages sync failed: {e}")

            # Sync promo codes
            if self.config.sync_templates and hasattr(self.neonpay, "promotions"):
                try:
                    if target_neonpay is not None:
                        promo_system = self.neonpay.promotions
                        if promo_system:
                            promo_codes = promo_system.list_promo_codes(active_only=False)
                            for promo in promo_codes:
                                target_neonpay.create_promo_code(
                                    code=promo.code,
                                    discount_type=promo.discount_type,
                                    discount_value=promo.discount_value,
                                    **promo.__dict__,
                                )
                                sync_results["promo_codes"] += 1
                    else:
                        logger.info("Simulating promo codes sync (no target bot)")
                        sync_results["errors"].append(
                            "Target bot instance not available - sync simulated"
                        )
                except Exception as e:
                    sync_results["errors"].append(f"Promo codes sync failed: {e}")

            logger.info(f"Sync completed: {sync_results}")
            return sync_results

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"errors": [str(e)]}



    async def export_data(self, format_type: str = "json") -> str:
        """Export data for external sync"""
        data_collector = DataCollector(self.neonpay)
        data = await data_collector.collect_all_data()
        if format_type.lower() == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    async def import_data(self, data: str, format_type: str = "json") -> bool:
        """Import data from external source"""
        try:
            if format_type.lower() == "json":
                imported_data = json.loads(data)
            else:
                raise ValueError(f"Unsupported import format: {format_type}")
            # Import payment stages
            if (
                "payment_data" in imported_data
                and "payment_stages" in imported_data["payment_data"]
            ):
                for stage_id, stage_data in imported_data["payment_data"][
                    "payment_stages"
                ].items():
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

            logger.info("Data imported successfully")
            return True

        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False


class BackupScheduler:
    """Schedules automatic backups"""

    def __init__(self, backup_manager: BackupManager) -> None:
        self.backup_manager = backup_manager
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start_scheduler(self) -> None:
        """Start automatic backup scheduler"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Backup scheduler started")

    async def stop_scheduler(self) -> None:
        """Stop automatic backup scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Backup scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self._running:
            try:
                await asyncio.sleep(
                    self.backup_manager.config.backup_interval_hours * 3600
                )
                if self._running:
                    await self.backup_manager.create_backup(
                        backup_type=BackupType.FULL, description="Automatic backup"
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying


