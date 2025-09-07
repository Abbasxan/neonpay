"""
NEONPAY Analytics - Comprehensive analytics and reporting system
Provides detailed insights into payment performance and user behavior
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


class AnalyticsPeriod(Enum):
    """Analytics time periods"""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class MetricType(Enum):
    """Types of metrics"""

    REVENUE = "revenue"
    TRANSACTIONS = "transactions"
    CONVERSION = "conversion"
    USER_ACTIVITY = "user_activity"
    PRODUCT_PERFORMANCE = "product_performance"


@dataclass
class AnalyticsEvent:
    """Analytics event record"""

    event_type: str
    user_id: int
    amount: Optional[int] = None
    stage_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None


@dataclass
class RevenueData:
    """Revenue analytics data"""

    total_revenue: int
    total_transactions: int
    average_transaction: float
    period: str
    start_date: datetime
    end_date: datetime
    daily_breakdown: Dict[str, int] = field(default_factory=dict)
    hourly_breakdown: Dict[str, int] = field(default_factory=dict)


@dataclass
class ConversionData:
    """Conversion analytics data"""

    total_visitors: int
    total_purchases: int
    conversion_rate: float
    period: str
    funnel_steps: Dict[str, int] = field(default_factory=dict)
    drop_off_points: Dict[str, float] = field(default_factory=dict)


@dataclass
class ProductPerformance:
    """Product performance analytics"""

    product_id: str
    product_name: str
    total_sales: int
    total_revenue: int
    conversion_rate: float
    average_price: float
    views: int = 0
    purchases: int = 0


class AnalyticsCollector:
    """Collects and stores analytics events"""

    def __init__(self, max_events: int = 100000) -> None:
        self._events: deque = deque(maxlen=max_events)
        self._user_sessions: Dict[int, Dict[str, Any]] = {}
        self._product_views: Dict[str, int] = defaultdict(int)
        self._conversion_funnel: Dict[str, int] = defaultdict(int)

    def track_event(self, event: AnalyticsEvent) -> None:
        """Track an analytics event"""
        self._events.append(event)

        # Update session data
        if event.user_id not in self._user_sessions:
            self._user_sessions[event.user_id] = {
                "first_seen": event.timestamp,
                "last_seen": event.timestamp,
                "events": [],
                "total_spent": 0,
            }

        session = self._user_sessions[event.user_id]
        session["last_seen"] = event.timestamp
        session["events"].append(event.event_type)

        if event.amount:
            session["total_spent"] += event.amount

        # Track product views
        if event.event_type == "product_view" and event.stage_id:
            self._product_views[event.stage_id] += 1

        # Track conversion funnel
        self._conversion_funnel[event.event_type] += 1

    def get_events(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        event_type: Optional[str] = None,
    ) -> List[AnalyticsEvent]:
        """Get filtered events"""
        events = list(self._events)

        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events


class AnalyticsEngine:
    """Main analytics engine for processing and generating insights"""

    def __init__(self, collector: AnalyticsCollector) -> None:
        self.collector = collector

    def calculate_revenue(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> RevenueData:
        """Calculate revenue metrics for specified period"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)

        # Get payment events
        payment_events = self.collector.get_events(
            start_time=start_time, end_time=end_time, event_type="payment_completed"
        )

        total_revenue = sum(event.amount or 0 for event in payment_events)
        total_transactions = len(payment_events)
        average_transaction = (
            total_revenue / total_transactions if total_transactions > 0 else 0
        )

        # Calculate daily breakdown
        daily_breakdown: defaultdict[str, int] = defaultdict(int)
        hourly_breakdown: defaultdict[str, int] = defaultdict(int)

        for event in payment_events:
            date = datetime.fromtimestamp(event.timestamp)
            daily_key = date.strftime("%Y-%m-%d")
            hourly_key = date.strftime("%H:00")

            daily_breakdown[daily_key] += event.amount or 0
            hourly_breakdown[hourly_key] += event.amount or 0

        return RevenueData(
            total_revenue=total_revenue,
            total_transactions=total_transactions,
            average_transaction=average_transaction,
            period=period.value,
            start_date=datetime.fromtimestamp(start_time),
            end_date=datetime.fromtimestamp(end_time),
            daily_breakdown=dict(daily_breakdown),
            hourly_breakdown=dict(hourly_breakdown),
        )

    def calculate_conversion_rate(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> ConversionData:
        """Calculate conversion rate and funnel analysis"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)

        # Get all events in period
        all_events = self.collector.get_events(start_time=start_time, end_time=end_time)

        # Count unique visitors
        unique_visitors = len(set(event.user_id for event in all_events))

        # Count purchases
        purchases = len([e for e in all_events if e.event_type == "payment_completed"])

        conversion_rate = (
            (purchases / unique_visitors * 100) if unique_visitors > 0 else 0
        )

        # Analyze funnel
        funnel_steps: defaultdict[str, int] = defaultdict(int)
        for event in all_events:
            funnel_steps[event.event_type] += 1

        # Calculate drop-off points
        drop_off_points = {}
        if funnel_steps["product_view"] > 0:
            drop_off_points["view_to_cart"] = (
                (funnel_steps["product_view"] - funnel_steps.get("add_to_cart", 0))
                / funnel_steps["product_view"]
                * 100
            )
        if funnel_steps.get("add_to_cart", 0) > 0:
            drop_off_points["cart_to_payment"] = (
                (funnel_steps["add_to_cart"] - funnel_steps.get("payment_started", 0))
                / funnel_steps["add_to_cart"]
                * 100
            )
        if funnel_steps.get("payment_started", 0) > 0:
            drop_off_points["payment_to_complete"] = (
                (funnel_steps["payment_started"] - purchases)
                / funnel_steps["payment_started"]
                * 100
            )

        return ConversionData(
            total_visitors=unique_visitors,
            total_purchases=purchases,
            conversion_rate=conversion_rate,
            period=period.value,
            funnel_steps=dict(funnel_steps),
            drop_off_points=drop_off_points,
        )

    def get_product_performance(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> List[ProductPerformance]:
        """Get product performance analytics"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)

        # Get product-related events
        product_events = self.collector.get_events(
            start_time=start_time, end_time=end_time
        )

        # Group by product
        product_data: defaultdict[str, dict[str, Any]] = defaultdict(
            lambda: {"views": 0, "purchases": 0, "revenue": 0, "prices": []}
        )

        for event in product_events:
            if not event.stage_id:
                continue

            if event.event_type == "product_view":
                product_data[event.stage_id]["views"] += 1
            elif event.event_type == "payment_completed":
                product_data[event.stage_id]["purchases"] += 1
                product_data[event.stage_id]["revenue"] += event.amount or 0
                product_data[event.stage_id]["prices"].append(event.amount or 0)

        # Convert to ProductPerformance objects
        performance_list = []
        for product_id, data in product_data.items():
            avg_price = (
                sum(data["prices"]) / len(data["prices"]) if data["prices"] else 0
            )
            conversion_rate = (
                (data["purchases"] / data["views"] * 100) if data["views"] > 0 else 0
            )

            performance_list.append(
                ProductPerformance(
                    product_id=product_id,
                    product_name=product_id.replace("_", " ").title(),
                    total_sales=data["purchases"],
                    total_revenue=data["revenue"],
                    conversion_rate=conversion_rate,
                    average_price=avg_price,
                    views=data["views"],
                    purchases=data["purchases"],
                )
            )

        # Sort by revenue
        performance_list.sort(key=lambda x: x.total_revenue, reverse=True)
        return performance_list

    def get_user_insights(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Dict[str, Any]:
        """Get user behavior insights"""
        end_time = time.time()
        start_time = end_time - (days * 24 * 60 * 60)

        # Get user sessions
        active_users = []
        for user_id, session in self.collector._user_sessions.items():
            if session["last_seen"] >= start_time:
                active_users.append(
                    {
                        "user_id": user_id,
                        "first_seen": session["first_seen"],
                        "last_seen": session["last_seen"],
                        "total_spent": session["total_spent"],
                        "event_count": len(session["events"]),
                    }
                )

        # Calculate metrics
        total_users = len(active_users)
        total_spent = sum(user["total_spent"] for user in active_users)
        avg_spent_per_user = total_spent / total_users if total_users > 0 else 0

        # User segments
        high_value_users = len(
            [u for u in active_users if u["total_spent"] > avg_spent_per_user * 2]
        )
        new_users = len([u for u in active_users if u["first_seen"] >= start_time])

        return {
            "total_active_users": total_users,
            "new_users": new_users,
            "returning_users": total_users - new_users,
            "high_value_users": high_value_users,
            "total_user_revenue": total_spent,
            "average_revenue_per_user": avg_spent_per_user,
            "user_retention_rate": (
                ((total_users - new_users) / total_users * 100)
                if total_users > 0
                else 0
            ),
        }


class AnalyticsDashboard:
    """Dashboard for displaying analytics data"""

    def __init__(self, engine: AnalyticsEngine) -> None:
        self.engine = engine

    def generate_report(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        revenue_data = self.engine.calculate_revenue(period, days)
        conversion_data = self.engine.calculate_conversion_rate(period, days)
        product_performance = self.engine.get_product_performance(period, days)
        user_insights = self.engine.get_user_insights(period, days)

        return {
            "period": {
                "type": period.value,
                "days": days,
                "start_date": revenue_data.start_date.isoformat(),
                "end_date": revenue_data.end_date.isoformat(),
            },
            "revenue": {
                "total": revenue_data.total_revenue,
                "transactions": revenue_data.total_transactions,
                "average_transaction": revenue_data.average_transaction,
                "daily_breakdown": revenue_data.daily_breakdown,
                "hourly_breakdown": revenue_data.hourly_breakdown,
            },
            "conversion": {
                "rate": conversion_data.conversion_rate,
                "visitors": conversion_data.total_visitors,
                "purchases": conversion_data.total_purchases,
                "funnel_steps": conversion_data.funnel_steps,
                "drop_off_points": conversion_data.drop_off_points,
            },
            "products": [
                {
                    "id": p.product_id,
                    "name": p.product_name,
                    "sales": p.total_sales,
                    "revenue": p.total_revenue,
                    "conversion_rate": p.conversion_rate,
                    "average_price": p.average_price,
                    "views": p.views,
                }
                for p in product_performance
            ],
            "users": user_insights,
            "generated_at": datetime.now().isoformat(),
        }

    def export_to_json(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> str:
        """Export analytics report to JSON"""
        report = self.generate_report(period, days)
        return json.dumps(report, indent=2, ensure_ascii=False)

    def export_to_csv(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> str:
        """Export analytics data to CSV format"""
        revenue_data = self.engine.calculate_revenue(period, days)
        product_performance = self.engine.get_product_performance(period, days)

        csv_lines = ["Metric,Value"]
        csv_lines.append(f"Total Revenue,{revenue_data.total_revenue}")
        csv_lines.append(f"Total Transactions,{revenue_data.total_transactions}")
        csv_lines.append(f"Average Transaction,{revenue_data.average_transaction}")
        csv_lines.append("")
        csv_lines.append("Product ID,Product Name,Sales,Revenue,Conversion Rate")

        for product in product_performance:
            csv_lines.append(
                f"{product.product_id},{product.product_name},"
                f"{product.total_sales},{product.total_revenue},"
                f"{product.conversion_rate:.2f}%"
            )

        return "\n".join(csv_lines)


class AnalyticsManager:
    """Main analytics manager for NEONPAY"""

    def __init__(self, enable_analytics: bool = True) -> None:
        self.enabled = enable_analytics
        self.collector = AnalyticsCollector() if enable_analytics else None
        self.engine = (
            AnalyticsEngine(self.collector) if self.collector is not None else None
        )
        self.dashboard = (
            AnalyticsDashboard(self.engine) if self.engine is not None else None
        )

        if enable_analytics:
            logger.info("Analytics system initialized")

    def track_event(
        self,
        event_type: str,
        user_id: int,
        amount: Optional[int] = None,
        stage_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an analytics event"""
        if not self.enabled or not self.collector:
            return

        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            amount=amount,
            stage_id=stage_id,
            metadata=metadata or {},
        )

        self.collector.track_event(event)

    def get_revenue_analytics(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Optional[RevenueData]:
        """Get revenue analytics"""
        if not self.enabled or not self.engine:
            return None
        return self.engine.calculate_revenue(period, days)

    def get_conversion_analytics(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Optional[ConversionData]:
        """Get conversion analytics"""
        if not self.enabled or not self.engine:
            return None
        return self.engine.calculate_conversion_rate(period, days)

    def get_product_analytics(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Optional[List[ProductPerformance]]:
        """Get product performance analytics"""
        if not self.enabled or not self.engine:
            return None
        return self.engine.get_product_performance(period, days)

    def get_dashboard_report(
        self, period: AnalyticsPeriod = AnalyticsPeriod.DAY, days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive dashboard report"""
        if not self.enabled or not self.dashboard:
            return None
        return self.dashboard.generate_report(period, days)

    def export_analytics(
        self,
        format_type: str = "json",
        period: AnalyticsPeriod = AnalyticsPeriod.DAY,
        days: int = 30,
    ) -> Optional[str]:
        """Export analytics data"""
        if not self.enabled or not self.dashboard:
            return None

        if format_type.lower() == "json":
            return self.dashboard.export_to_json(period, days)
        elif format_type.lower() == "csv":
            return self.dashboard.export_to_csv(period, days)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def get_stats(self) -> Dict[str, Any]:
        """Get analytics system statistics"""
        if not self.enabled or self.collector is None:
            return {"enabled": False}

        return {
            "enabled": True,
            "total_events": len(self.collector._events),
            "active_users": len(self.collector._user_sessions),
            "tracked_products": len(self.collector._product_views),
            "conversion_funnel_steps": len(self.collector._conversion_funnel),
        }
