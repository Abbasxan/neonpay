"""
NEONPAY Multi-Bot Analytics - Centralized analytics for multiple bots
Automatically tracks events across all synchronized bots
"""

import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events to track"""

    # User events
    USER_STARTED = "user_started"
    USER_MESSAGE = "user_message"
    USER_CALLBACK = "user_callback"

    # Product events
    PRODUCT_VIEW = "product_view"
    PRODUCT_CLICK = "product_click"
    PRODUCT_SHARE = "product_share"

    # Payment events
    PAYMENT_STARTED = "payment_started"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_CANCELLED = "payment_cancelled"

    # Promo events
    PROMO_CODE_USED = "promo_code_used"
    PROMO_CODE_INVALID = "promo_code_invalid"

    # Subscription events
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"

    # Bot events
    BOT_STARTED = "bot_started"
    BOT_SYNC = "bot_sync"
    BOT_ERROR = "bot_error"


class AnalyticsPeriod(Enum):
    """Analytics time periods"""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class MultiBotEvent:
    """Event from any bot in the network"""

    event_type: str
    bot_id: str
    bot_name: str
    user_id: int
    amount: Optional[int] = None
    product_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class BotAnalytics:
    """Analytics data for a specific bot"""

    bot_id: str
    bot_name: str
    total_events: int = 0
    total_users: int = 0
    total_revenue: int = 0
    total_transactions: int = 0
    conversion_rate: float = 0.0
    last_activity: Optional[float] = None
    events_by_type: Dict[str, int] = field(default_factory=dict)
    revenue_by_product: Dict[str, int] = field(default_factory=dict)
    user_activity: Dict[int, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class NetworkAnalytics:
    """Analytics data for the entire bot network"""

    total_bots: int = 0
    total_events: int = 0
    total_users: int = 0
    total_revenue: int = 0
    total_transactions: int = 0
    network_conversion_rate: float = 0.0
    top_performing_bots: List[Dict[str, Any]] = field(default_factory=list)
    top_products: List[Dict[str, Any]] = field(default_factory=list)
    user_journey: Dict[str, int] = field(default_factory=dict)
    revenue_trends: Dict[str, int] = field(default_factory=dict)


class EventCollector:
    """Collects events from multiple bots"""

    def __init__(self, max_events: int = 1000000) -> None:
        self._events: deque = deque(maxlen=max_events)
        self._bot_events: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_events // 10)
        )
        self._user_sessions: Dict[str, Dict[int, Dict[str, Any]]] = defaultdict(dict)
        self._product_views: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._conversion_funnel: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def track_event(self, event: MultiBotEvent) -> None:
        """Track an event from any bot"""
        self._events.append(event)

        # Track per-bot events
        self._bot_events[event.bot_id].append(event)

        # Update user sessions
        if event.user_id not in self._user_sessions[event.bot_id]:
            self._user_sessions[event.bot_id][event.user_id] = {
                "first_seen": event.timestamp,
                "last_seen": event.timestamp,
                "events": [],
                "total_spent": 0,
                "products_viewed": set(),
                "products_purchased": set(),
            }

        session = self._user_sessions[event.bot_id][event.user_id]
        session["last_seen"] = event.timestamp
        session["events"].append(event.event_type)

        if event.amount:
            session["total_spent"] += event.amount

        if event.product_id:
            if event.event_type == EventType.PRODUCT_VIEW.value:
                session["products_viewed"].add(event.product_id)
            elif event.event_type == EventType.PAYMENT_COMPLETED.value:
                session["products_purchased"].add(event.product_id)

        # Track product views
        if event.event_type == EventType.PRODUCT_VIEW.value and event.product_id:
            self._product_views[event.bot_id][event.product_id] += 1

        # Track conversion funnel
        self._conversion_funnel[event.bot_id][event.event_type] += 1

    def get_events(
        self,
        bot_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        event_type: Optional[str] = None,
    ) -> List[MultiBotEvent]:
        """Get filtered events"""
        if bot_id:
            events = list(self._bot_events[bot_id])
        else:
            events = list(self._events)

        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events

    def get_bot_stats(self, bot_id: str) -> Dict[str, Any]:
        """Get statistics for a specific bot"""
        events = self._bot_events[bot_id]
        user_sessions = self._user_sessions[bot_id]

        total_events = len(events)
        total_users = len(user_sessions)

        # Calculate revenue
        payment_events = [
            e for e in events if e.event_type == EventType.PAYMENT_COMPLETED.value
        ]
        total_revenue = sum(e.amount or 0 for e in payment_events)
        total_transactions = len(payment_events)

        # Calculate conversion rate
        product_views = len(
            [e for e in events if e.event_type == EventType.PRODUCT_VIEW.value]
        )
        conversion_rate = (
            (total_transactions / product_views * 100) if product_views > 0 else 0
        )

        # Events by type
        events_by_type: defaultdict[str, int] = defaultdict(int)
        for event in events:
            events_by_type[event.event_type] += 1

        # Revenue by product
        revenue_by_product: defaultdict[str, int] = defaultdict(int)
        for event in payment_events:
            if event.product_id:
                revenue_by_product[event.product_id] += event.amount or 0

        # Last activity
        last_activity = max((e.timestamp for e in events), default=None)

        return {
            "total_events": total_events,
            "total_users": total_users,
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "conversion_rate": conversion_rate,
            "last_activity": last_activity,
            "events_by_type": dict(events_by_type),
            "revenue_by_product": dict(revenue_by_product),
        }


class MultiBotAnalyticsEngine:
    """Analytics engine for multiple bots"""

    def __init__(self, collector: EventCollector) -> None:
        self.collector = collector

    def calculate_network_analytics(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> NetworkAnalytics:
        """Calculate analytics for the entire bot network"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)

        # Get all events in period
        all_events = self.collector.get_events(start_time=start_time, end_time=end_time)

        # Calculate network metrics
        total_bots = len(self.collector._bot_events)
        total_events = len(all_events)

        # Calculate total users (unique across all bots)
        all_users: set[int] = set()
        for bot_id in self.collector._user_sessions:
            all_users.update(self.collector._user_sessions[bot_id].keys())
        total_users = len(all_users)

        # Calculate total revenue
        payment_events = [
            e for e in all_events if e.event_type == EventType.PAYMENT_COMPLETED.value
        ]
        total_revenue = sum(e.amount or 0 for e in payment_events)
        total_transactions = len(payment_events)

        # Calculate network conversion rate
        product_views = len(
            [e for e in all_events if e.event_type == EventType.PRODUCT_VIEW.value]
        )
        network_conversion_rate = (
            (total_transactions / product_views * 100) if product_views > 0 else 0
        )

        # Top performing bots
        bot_performance = []
        for bot_id in self.collector._bot_events:
            bot_stats = self.collector.get_bot_stats(bot_id)
            bot_performance.append(
                {
                    "bot_id": bot_id,
                    "bot_name": bot_id,  # Would be resolved from bot registry
                    "revenue": bot_stats["total_revenue"],
                    "transactions": bot_stats["total_transactions"],
                    "conversion_rate": bot_stats["conversion_rate"],
                    "users": bot_stats["total_users"],
                }
            )

        bot_performance.sort(key=lambda x: x["revenue"], reverse=True)
        top_performing_bots = bot_performance[:10]

        # Top products across all bots
        product_revenue: defaultdict[str, int] = defaultdict(int)
        for event in payment_events:
            if event.product_id:
                product_revenue[event.product_id] += event.amount or 0

        top_products = [
            {"product_id": product_id, "revenue": revenue}
            for product_id, revenue in sorted(
                product_revenue.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]

        # User journey analysis
        user_journey: defaultdict[str, int] = defaultdict(int)
        for event in all_events:
            user_journey[event.event_type] += 1

        # Revenue trends (daily breakdown)
        revenue_trends: defaultdict[str, int] = defaultdict(int)
        for event in payment_events:
            date = datetime.fromtimestamp(event.timestamp)
            daily_key = date.strftime("%Y-%m-%d")
            revenue_trends[daily_key] += event.amount or 0

        return NetworkAnalytics(
            total_bots=total_bots,
            total_events=total_events,
            total_users=total_users,
            total_revenue=total_revenue,
            total_transactions=total_transactions,
            network_conversion_rate=network_conversion_rate,
            top_performing_bots=top_performing_bots,
            top_products=top_products,
            user_journey=dict(user_journey),
            revenue_trends=dict(revenue_trends),
        )

    def calculate_bot_analytics(
        self, bot_id: str, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> BotAnalytics:
        """Calculate analytics for a specific bot"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)

        # Get bot events
        bot_events = self.collector.get_events(
            bot_id=bot_id, start_time=start_time, end_time=end_time
        )

        # Calculate metrics
        total_events = len(bot_events)
        total_users = len(self.collector._user_sessions[bot_id])

        # Calculate revenue
        payment_events = [
            e for e in bot_events if e.event_type == EventType.PAYMENT_COMPLETED.value
        ]
        total_revenue = sum(e.amount or 0 for e in payment_events)
        total_transactions = len(payment_events)

        # Calculate conversion rate
        product_views = len(
            [e for e in bot_events if e.event_type == EventType.PRODUCT_VIEW.value]
        )
        conversion_rate = (
            (total_transactions / product_views * 100) if product_views > 0 else 0
        )

        # Events by type
        events_by_type: defaultdict[str, int] = defaultdict(int)
        for event in bot_events:
            events_by_type[event.event_type] += 1

        # Revenue by product
        revenue_by_product: defaultdict[str, int] = defaultdict(int)
        for event in payment_events:
            if event.product_id:
                revenue_by_product[event.product_id] += event.amount or 0

        # User activity
        user_activity = {}
        for user_id, session in self.collector._user_sessions[bot_id].items():
            user_activity[user_id] = {
                "first_seen": session["first_seen"],
                "last_seen": session["last_seen"],
                "total_spent": session["total_spent"],
                "products_viewed": len(session["products_viewed"]),
                "products_purchased": len(session["products_purchased"]),
                "event_count": len(session["events"]),
            }

        # Last activity
        last_activity = max((e.timestamp for e in bot_events), default=None)

        return BotAnalytics(
            bot_id=bot_id,
            bot_name=bot_id,  # Would be resolved from bot registry
            total_events=total_events,
            total_users=total_users,
            total_revenue=total_revenue,
            total_transactions=total_transactions,
            conversion_rate=conversion_rate,
            last_activity=last_activity,
            events_by_type=dict(events_by_type),
            revenue_by_product=dict(revenue_by_product),
            user_activity=user_activity,
        )


class MultiBotAnalyticsDashboard:
    """Dashboard for multi-bot analytics"""

    def __init__(self, engine: MultiBotAnalyticsEngine) -> None:
        self.engine = engine

    def generate_network_report(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive network analytics report"""
        network_data = self.engine.calculate_network_analytics(period, days)

        # Get individual bot analytics
        bot_analytics = {}
        for bot_id in self.engine.collector._bot_events:
            bot_analytics[bot_id] = self.engine.calculate_bot_analytics(
                bot_id, period, days
            )

        return {
            "period": {
                "type": period.value,
                "days": days,
                "start_date": datetime.fromtimestamp(
                    time.time() - days * 24 * 60 * 60
                ).isoformat(),
                "end_date": datetime.now().isoformat(),
            },
            "network": {
                "total_bots": network_data.total_bots,
                "total_events": network_data.total_events,
                "total_users": network_data.total_users,
                "total_revenue": network_data.total_revenue,
                "total_transactions": network_data.total_transactions,
                "network_conversion_rate": network_data.network_conversion_rate,
                "top_performing_bots": network_data.top_performing_bots,
                "top_products": network_data.top_products,
                "user_journey": network_data.user_journey,
                "revenue_trends": network_data.revenue_trends,
            },
            "bots": {
                bot_id: {
                    "bot_name": analytics.bot_name,
                    "total_events": analytics.total_events,
                    "total_users": analytics.total_users,
                    "total_revenue": analytics.total_revenue,
                    "total_transactions": analytics.total_transactions,
                    "conversion_rate": analytics.conversion_rate,
                    "last_activity": analytics.last_activity,
                    "events_by_type": analytics.events_by_type,
                    "revenue_by_product": analytics.revenue_by_product,
                    "user_activity_summary": {
                        "total_users": len(analytics.user_activity),
                        "high_value_users": len(
                            [
                                u
                                for u in analytics.user_activity.values()
                                if u["total_spent"] > 100
                            ]
                        ),
                        "active_users": len(
                            [
                                u
                                for u in analytics.user_activity.values()
                                if u["last_seen"] > time.time() - 24 * 60 * 60
                            ]
                        ),
                    },
                }
                for bot_id, analytics in bot_analytics.items()
            },
            "generated_at": datetime.now().isoformat(),
        }

    def export_network_report(
        self,
        format_type: str = "json",
        period: AnalyticsPeriod = AnalyticsPeriod.DAY,
        days: int = 30,
    ) -> str:
        """Export network analytics report"""
        report = self.generate_network_report(period, days)

        if format_type.lower() == "json":
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif format_type.lower() == "csv":
            return self._export_to_csv(report)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def _export_to_csv(self, report: Dict[str, Any]) -> str:
        """Export report to CSV format"""
        csv_lines = []

        # Network summary
        csv_lines.append("Metric,Value")
        network = report["network"]
        csv_lines.append(f"Total Bots,{network['total_bots']}")
        csv_lines.append(f"Total Events,{network['total_events']}")
        csv_lines.append(f"Total Users,{network['total_users']}")
        csv_lines.append(f"Total Revenue,{network['total_revenue']}")
        csv_lines.append(f"Total Transactions,{network['total_transactions']}")
        csv_lines.append(
            f"Network Conversion Rate,{network['network_conversion_rate']:.2f}%"
        )
        csv_lines.append("")

        # Bot performance
        csv_lines.append("Bot ID,Bot Name,Revenue,Transactions,Conversion Rate,Users")
        for bot_data in network["top_performing_bots"]:
            csv_lines.append(
                f"{bot_data['bot_id']},{bot_data['bot_name']},"
                f"{bot_data['revenue']},{bot_data['transactions']},"
                f"{bot_data['conversion_rate']:.2f}%,{bot_data['users']}"
            )
        csv_lines.append("")

        # Top products
        csv_lines.append("Product ID,Revenue")
        for product_data in network["top_products"]:
            csv_lines.append(f"{product_data['product_id']},{product_data['revenue']}")

        return "\n".join(csv_lines)


class MultiBotAnalyticsManager:
    """Main analytics manager for multiple bots"""

    def __init__(self, enable_analytics: bool = True) -> None:
        self.enabled = enable_analytics
        self.collector = EventCollector() if enable_analytics else None
        self.engine = (
            MultiBotAnalyticsEngine(self.collector)
            if self.collector is not None
            else None
        )
        self.dashboard = (
            MultiBotAnalyticsDashboard(self.engine) if self.engine is not None else None
        )
        self._bot_registry: Dict[str, str] = {}  # bot_id -> bot_name mapping

        if enable_analytics:
            logger.info("Multi-bot analytics system initialized")

    def register_bot(self, bot_id: str, bot_name: str) -> None:
        """Register a bot in the analytics system"""
        self._bot_registry[bot_id] = bot_name
        logger.info(f"Registered bot: {bot_id} -> {bot_name}")

    def track_event(
        self,
        event_type: str,
        bot_id: str,
        user_id: int,
        amount: Optional[int] = None,
        product_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an event from any bot"""
        if not self.enabled or not self.collector:
            return

        bot_name = self._bot_registry.get(bot_id, bot_id)

        event = MultiBotEvent(
            event_type=event_type,
            bot_id=bot_id,
            bot_name=bot_name,
            user_id=user_id,
            amount=amount,
            product_id=product_id,
            metadata=metadata or {},
        )

        self.collector.track_event(event)

    def get_network_analytics(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Optional[NetworkAnalytics]:
        """Get network analytics"""
        if not self.enabled or not self.engine:
            return None
        return self.engine.calculate_network_analytics(period, days)

    def get_bot_analytics(
        self, bot_id: str, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Optional[BotAnalytics]:
        """Get analytics for a specific bot"""
        if not self.enabled or not self.engine:
            return None
        return self.engine.calculate_bot_analytics(bot_id, period, days)

    def get_network_report(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive network report"""
        if not self.enabled or not self.dashboard:
            return None
        return self.dashboard.generate_network_report(period, days)

    def export_network_analytics(
        self,
        format_type: str = "json",
        period: AnalyticsPeriod = AnalyticsPeriod.DAY,
        days: int = 30,
    ) -> Optional[str]:
        """Export network analytics"""
        if not self.enabled or not self.dashboard:
            return None
        return self.dashboard.export_network_report(format_type, period, days)

    def get_stats(self) -> Dict[str, Any]:
        """Get analytics system statistics"""
        if not self.enabled or self.collector is None:
            return {"enabled": False}

        return {
            "enabled": True,
            "registered_bots": len(self._bot_registry),
            "total_events": len(self.collector._events),
            "total_bot_events": sum(
                len(events) for events in self.collector._bot_events.values()
            ),
            "total_users": sum(
                len(sessions) for sessions in self.collector._user_sessions.values()
            ),
            "bot_registry": self._bot_registry.copy(),
        }
