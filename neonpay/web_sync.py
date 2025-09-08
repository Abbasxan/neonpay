"""
NEONPAY Web Sync - Web interface for bot synchronization
Provides HTTP endpoints for receiving sync data from other bots
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from aiohttp import web
from aiohttp.web import Request, Response

logger = logging.getLogger(__name__)


class SyncWebHandler:
    """Web handler for synchronization endpoints"""

    def __init__(
        self, neonpay_instance: Any, webhook_secret: Optional[str] = None
    ) -> None:
        self.neonpay = neonpay_instance
        self.webhook_secret = webhook_secret
        self._sync_data: Dict[str, Any] = {}

    def _verify_webhook(self, request: Request) -> bool:
        """Verify webhook signature"""
        if not self.webhook_secret:
            return True  # No secret configured

        signature = request.headers.get("X-Webhook-Secret")
        if not signature:
            return False

        return signature == self.webhook_secret

    async def handle_payment_stages_sync(self, request: Request) -> Response:
        """Handle payment stages synchronization"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            data = await request.json()
            action = data.get("action")

            if action == "sync":
                # Receive sync data
                stages_data = data.get("data", {})
                self._sync_data["payment_stages"] = stages_data

                # Apply stages to local bot
                applied_count = 0
                for stage_id, stage_data in stages_data.items():
                    try:
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
                        applied_count += 1
                    except Exception as e:
                        logger.error(f"Failed to apply stage {stage_id}: {e}")

                return web.json_response(
                    {
                        "status": "success",
                        "applied_stages": applied_count,
                        "message": f"Applied {applied_count} payment stages",
                    }
                )

            elif action == "get":
                # Send local stages data
                local_stages = self.neonpay.list_payment_stages()
                stages_data = {}
                for stage_id, stage in local_stages.items():
                    stages_data[stage_id] = {
                        "title": stage.title,
                        "description": stage.description,
                        "price": stage.price,
                        "label": stage.label,
                        "photo_url": stage.photo_url,
                        "payload": stage.payload,
                        "start_parameter": stage.start_parameter,
                        "created_at": time.time(),
                    }

                return web.json_response({"status": "success", "data": stages_data})

            else:
                return web.json_response(
                    {"status": "error", "message": "Invalid action"}, status=400
                )

        except Exception as e:
            logger.error(f"Payment stages sync error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_promo_codes_sync(self, request: Request) -> Response:
        """Handle promo codes synchronization"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            data = await request.json()
            action = data.get("action")

            if action == "sync":
                # Receive sync data
                promo_data = data.get("data", [])
                self._sync_data["promo_codes"] = promo_data

                # Apply promo codes to local bot
                applied_count = 0
                if hasattr(self.neonpay, "promotions") and self.neonpay.promotions:
                    promo_system = self.neonpay.promotions

                    for promo_data_item in promo_data:
                        try:
                            from .promotions import DiscountType

                            promo_system.create_promo_code(
                                code=promo_data_item["code"],
                                discount_type=DiscountType(
                                    promo_data_item["discount_type"]
                                ),
                                discount_value=promo_data_item["discount_value"],
                                max_uses=promo_data_item.get("max_uses"),
                                expires_at=promo_data_item.get("expires_at"),
                                min_amount=promo_data_item.get("min_amount"),
                                max_discount=promo_data_item.get("max_discount"),
                                user_limit=promo_data_item.get("user_limit", 1),
                                description=promo_data_item.get("description", ""),
                            )
                            applied_count += 1
                        except Exception as e:
                            logger.error(
                                f"Failed to apply promo code {promo_data_item.get('code')}: {e}"
                            )

                return web.json_response(
                    {
                        "status": "success",
                        "applied_promos": applied_count,
                        "message": f"Applied {applied_count} promo codes",
                    }
                )

            elif action == "get":
                # Send local promo codes data
                promo_codes_data = []
                if hasattr(self.neonpay, "promotions") and self.neonpay.promotions:
                    promo_system = self.neonpay.promotions
                    promo_codes = promo_system.list_promo_codes(active_only=False)

                    for promo in promo_codes:
                        promo_codes_data.append(
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
                                "created_at": time.time(),
                            }
                        )

                return web.json_response(
                    {"status": "success", "data": promo_codes_data}
                )

            else:
                return web.json_response(
                    {"status": "error", "message": "Invalid action"}, status=400
                )

        except Exception as e:
            logger.error(f"Promo codes sync error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_templates_sync(self, request: Request) -> Response:
        """Handle templates synchronization"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            data = await request.json()
            action = data.get("action")

            if action == "sync":
                # Receive sync data
                templates_data = data.get("data", {})
                self._sync_data["templates"] = templates_data

                # Apply templates to local bot
                applied_count = 0
                if hasattr(self.neonpay, "templates") and self.neonpay.templates:
                    template_manager = self.neonpay.templates

                    for template_name, template_json in templates_data.items():
                        try:
                            template_manager.import_template(template_json)
                            applied_count += 1
                        except Exception as e:
                            sanitized_template_name = str(template_name).replace('\r', '').replace('\n', '')
                            logger.error(
                                f"Failed to apply template {sanitized_template_name}: {e}"
                            )

                return web.json_response(
                    {
                        "status": "success",
                        "applied_templates": applied_count,
                        "message": f"Applied {applied_count} templates",
                    }
                )

            elif action == "get":
                # Send local templates data
                templates_data = {}
                if hasattr(self.neonpay, "templates") and self.neonpay.templates:
                    template_manager = self.neonpay.templates
                    templates = template_manager.list_templates()

                    for template in templates:
                        templates_data[template.name] = (
                            template_manager.export_template(template, "json")
                        )

                return web.json_response({"status": "success", "data": templates_data})

            else:
                return web.json_response(
                    {"status": "error", "message": "Invalid action"}, status=400
                )

        except Exception as e:
            logger.error(f"Templates sync error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_settings_sync(self, request: Request) -> Response:
        """Handle settings synchronization"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            data = await request.json()
            action = data.get("action")

            if action == "sync":
                # Receive sync data
                settings_data = data.get("data", {})
                self._sync_data["settings"] = settings_data

                # Apply settings to local bot
                applied_count = 0
                for key, value in settings_data.items():
                    if hasattr(self.neonpay, key):
                        setattr(self.neonpay, key, value)
                        applied_count += 1

                return web.json_response(
                    {
                        "status": "success",
                        "applied_settings": applied_count,
                        "message": f"Applied {applied_count} settings",
                    }
                )

            elif action == "get":
                # Send local settings data
                settings_data = {
                    "thank_you_message": getattr(self.neonpay, "thank_you_message", ""),
                    "max_stages": getattr(self.neonpay, "_max_stages", 100),
                    "logging_enabled": getattr(self.neonpay, "_enable_logging", True),
                }

                return web.json_response({"status": "success", "data": settings_data})

            else:
                return web.json_response(
                    {"status": "error", "message": "Invalid action"}, status=400
                )

        except Exception as e:
            logger.error(f"Settings sync error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def handle_sync_status(self, request: Request) -> Response:
        """Handle sync status requests"""
        if not self._verify_webhook(request):
            return web.Response(text="Unauthorized", status=401)

        try:
            status_data = {
                "bot_info": {
                    "name": "NEONPAY Bot",
                    "version": getattr(self.neonpay, "__version__", "unknown"),
                    "status": "online",
                },
                "sync_data": {
                    "payment_stages": len(self._sync_data.get("payment_stages", {})),
                    "promo_codes": len(self._sync_data.get("promo_codes", [])),
                    "templates": len(self._sync_data.get("templates", {})),
                    "settings": len(self._sync_data.get("settings", {})),
                },
                "local_data": {
                    "payment_stages": len(self.neonpay.list_payment_stages()),
                    "promo_codes": (
                        len(self.neonpay.promotions.list_promo_codes())
                        if hasattr(self.neonpay, "promotions")
                        and self.neonpay.promotions
                        else 0
                    ),
                    "templates": (
                        len(self.neonpay.templates.list_templates())
                        if hasattr(self.neonpay, "templates") and self.neonpay.templates
                        else 0
                    ),
                },
                "timestamp": time.time(),
            }

            return web.json_response(status_data)

        except Exception as e:
            logger.error(f"Sync status error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)


def create_sync_app(
    neonpay_instance: Any, webhook_secret: Optional[str] = None
) -> web.Application:
    """Create web application for synchronization"""
    handler = SyncWebHandler(neonpay_instance, webhook_secret)

    app = web.Application()

    # Add routes
    app.router.add_post("/sync/payment_stages", handler.handle_payment_stages_sync)
    app.router.add_get("/sync/payment_stages", handler.handle_payment_stages_sync)

    app.router.add_post("/sync/promo_codes", handler.handle_promo_codes_sync)
    app.router.add_get("/sync/promo_codes", handler.handle_promo_codes_sync)

    app.router.add_post("/sync/templates", handler.handle_templates_sync)
    app.router.add_get("/sync/templates", handler.handle_templates_sync)

    app.router.add_post("/sync/settings", handler.handle_settings_sync)
    app.router.add_get("/sync/settings", handler.handle_settings_sync)

    app.router.add_get("/sync/status", handler.handle_sync_status)

    # Health check endpoint
    async def health_check(request: Request) -> Response:
        return web.json_response({"status": "healthy", "timestamp": time.time()})

    app.router.add_get("/health", health_check)

    return app


async def run_sync_server(
    neonpay_instance: Any,
    host: str = "localhost",
    port: int = 8080,
    webhook_secret: Optional[str] = None,
) -> None:
    """Run synchronization web server"""
    app = create_sync_app(neonpay_instance, webhook_secret)

    logger.info(f"Starting sync server on {host}:{port}")

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info("Sync server started successfully")

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Sync server stopped by user")
    finally:
        await runner.cleanup()

