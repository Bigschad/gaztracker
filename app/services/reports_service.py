"""
Reports Service

Business logic for generating reports, statistics, and analytics
including palette reports, expedition reports, performance metrics,
and dashboard data.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract, select
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict

from app.models.palette import Palette, PaletteStatus
from app.models.expedition import Expedition, ExpeditionStatus
from app.models.palette_movement import PaletteMovement
from app.models.notification import Notification, NotificationStatus
from app.models.user import User
from app.utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ReportsService:
    """Service for generating reports and statistics."""

    def __init__(self, db: Session):
        """
        Initialize reports service.

        Args:
            db: Database session
        """
        self.db = db

    # =============================================================================
    # Palette Statistics
    # =============================================================================

    def get_palette_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive palette statistics.

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            Dictionary with palette statistics
        """
        logger.info("Generating palette statistics...")

        # Base query
        query = self.db.query(Palette)

        # Apply date filters if provided
        if start_date:
            query = query.filter(Palette.created_at >= start_date)
        if end_date:
            query = query.filter(Palette.created_at <= end_date)

        # Total palettes
        total_palettes = query.count()

        # Count by status
        by_status = {}
        for status in PaletteStatus:
            count = query.filter(Palette.status == status).count()
            by_status[status.value] = count

        # Average utilization
        palettes = query.all()
        total_utilization = sum(p.utilization_rate for p in palettes if p.utilization_rate)
        avg_utilization = (total_utilization / len(palettes)) if palettes else 0.0

        # Most used palettes
        most_used = self.db.query(
            Palette.id,
            Palette.reference_number,
            func.count(PaletteMovement.id).label('movement_count')
        ).join(
            PaletteMovement, Palette.id == PaletteMovement.palette_id
        ).group_by(
            Palette.id, Palette.reference_number
        ).order_by(
            func.count(PaletteMovement.id).desc()
        ).limit(10).all()

        # Palettes needing maintenance (high usage)
        maintenance_needed = query.filter(
            Palette.utilization_rate >= 80.0
        ).count()

        return {
            "total_palettes": total_palettes,
            "by_status": by_status,
            "average_utilization": round(avg_utilization, 2),
            "most_used_palettes": [
                {
                    "id": str(p.id),
                    "reference": p.reference_number,
                    "movements": p.movement_count
                }
                for p in most_used
            ],
            "maintenance_needed": maintenance_needed,
            "available_palettes": by_status.get("AU_DEPOT", 0) + by_status.get("AU_CENTRE", 0),
            "in_use_palettes": by_status.get("EN_ROUTE_LIVRAISON", 0) + by_status.get("EN_ROUTE_RETOUR", 0),
            "damaged_palettes": by_status.get("OUT", 0)
        }

    async def get_palette_utilization_trend(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get palette utilization trend over time.

        Args:
            days: Number of days to analyze

        Returns:
            List of daily utilization data
        """
        logger.info(f"Generating palette utilization trend for {days} days...")

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Query movements per day
        stmt = select(
            func.date(PaletteMovement.timestamp).label('date'),
            func.count(PaletteMovement.id).label('movement_count'),
            func.count(func.distinct(PaletteMovement.palette_id)).label('unique_palettes')
        ).where(
            PaletteMovement.timestamp >= start_date,
            PaletteMovement.timestamp <= end_date
        ).group_by(
            func.date(PaletteMovement.timestamp)
        ).order_by(
            func.date(PaletteMovement.timestamp)
        )

        result = self.db.execute(stmt)
        daily_data = result.all()

        return [
            {
                "date": str(row.date),
                "movement_count": row.movement_count,
                "unique_palettes": row.unique_palettes
            }
            for row in daily_data
        ]

    def get_palette_distribution_by_location(self) -> Dict[str, int]:
        """
        Get palette distribution by current location.

        Returns:
            Dictionary with location counts
        """
        logger.info("Generating palette distribution by location...")

        distribution = self.db.query(
            Palette.current_location,
            func.count(Palette.id).label('count')
        ).filter(
            Palette.current_location.isnot(None)
        ).group_by(
            Palette.current_location
        ).all()

        return {
            row.current_location: row.count
            for row in distribution
        }

    # =============================================================================
    # Expedition Statistics
    # =============================================================================

    def get_expedition_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive expedition statistics.

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            Dictionary with expedition statistics
        """
        logger.info("Generating expedition statistics...")

        # Base query
        query = self.db.query(Expedition)

        # Apply date filters
        if start_date:
            query = query.filter(Expedition.created_at >= start_date)
        if end_date:
            query = query.filter(Expedition.created_at <= end_date)

        # Total expeditions
        total_expeditions = query.count()

        # Count by status
        by_status = {}
        for status in ExpeditionStatus:
            count = query.filter(Expedition.status == status).count()
            by_status[status.value] = count

        # Completed expeditions
        completed = query.filter(
            Expedition.status == ExpeditionStatus.LIVREE
        ).all()

        # Calculate average delivery time
        delivery_times = []
        for exp in completed:
            if exp.date_depart and exp.date_delivery:
                duration = (exp.date_delivery - exp.date_depart).total_seconds() / 3600  # hours
                delivery_times.append(duration)

        avg_delivery_time = (sum(delivery_times) / len(delivery_times)) if delivery_times else 0.0

        # Success rate (delivered / total non-cancelled)
        non_cancelled = query.filter(
            Expedition.status != ExpeditionStatus.ANNULEE
        ).count()
        success_rate = (len(completed) / non_cancelled * 100) if non_cancelled > 0 else 0.0

        # Delayed expeditions
        delayed = query.filter(
            Expedition.eta < datetime.utcnow(),
            Expedition.status.notin_([ExpeditionStatus.LIVREE, ExpeditionStatus.ANNULEE]),
            Expedition.eta.isnot(None)
        ).count()

        # Problems reported
        problems = query.filter(
            Expedition.status == ExpeditionStatus.PROBLEME
        ).count()

        return {
            "total_expeditions": total_expeditions,
            "by_status": by_status,
            "average_delivery_time_hours": round(avg_delivery_time, 2),
            "success_rate": round(success_rate, 2),
            "delayed_expeditions": delayed,
            "problems_reported": problems,
            "completed_expeditions": len(completed),
            "active_expeditions": query.filter(
                Expedition.status.in_([
                    ExpeditionStatus.CREEE,
                    ExpeditionStatus.EN_TRANSIT,
                    ExpeditionStatus.ARRIVEE
                ])
            ).count()
        }

    def get_expedition_trend(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get expedition creation trend over time.

        Args:
            days: Number of days to analyze

        Returns:
            List of daily expedition data
        """
        logger.info(f"Generating expedition trend for {days} days...")

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        stmt = select(
            func.date(Expedition.created_at).label('date'),
            func.count(Expedition.id).label('expedition_count'),
            func.sum(Expedition.palette_count).label('total_palettes')
        ).where(
            Expedition.created_at >= start_date,
            Expedition.created_at <= end_date
        ).group_by(
            func.date(Expedition.created_at)
        ).order_by(
            func.date(Expedition.created_at)
        )

        result = self.db.execute(stmt)
        daily_data = result.all()

        return [
            {
                "date": str(row.date),
                "expedition_count": row.expedition_count,
                "total_palettes": row.total_palettes or 0
            }
            for row in daily_data
        ]

    def get_top_destinations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top destinations by expedition count.

        Args:
            limit: Number of top destinations to return

        Returns:
            List of top destinations with counts
        """
        logger.info(f"Getting top {limit} destinations...")

        destinations = self.db.query(
            Expedition.destination_address,
            func.count(Expedition.id).label('expedition_count'),
            func.sum(Expedition.palette_count).label('total_palettes')
        ).filter(
            Expedition.destination_address.isnot(None)
        ).group_by(
            Expedition.destination_address
        ).order_by(
            func.count(Expedition.id).desc()
        ).limit(limit).all()

        return [
            {
                "address": row.destination_address,
                "expedition_count": row.expedition_count,
                "total_palettes": row.total_palettes or 0
            }
            for row in destinations
        ]

    # =============================================================================
    # Performance Reports
    # =============================================================================

    def get_performance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance report.

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            Dictionary with performance metrics
        """
        logger.info("Generating performance report...")

        # Get expedition stats
        exp_stats = self.get_expedition_statistics(start_date, end_date)

        # Get palette stats
        palette_stats = self.get_palette_statistics(start_date, end_date)

        # Get notification stats
        notification_query = self.db.query(Notification)
        if start_date:
            notification_query = notification_query.filter(Notification.created_at >= start_date)
        if end_date:
            notification_query = notification_query.filter(Notification.created_at <= end_date)

        total_notifications = notification_query.count()
        sent_notifications = notification_query.filter(
            Notification.status == NotificationStatus.SENT
        ).count()
        notification_success_rate = (
            (sent_notifications / total_notifications * 100) if total_notifications > 0 else 0.0
        )

        # System efficiency metrics
        total_palettes = palette_stats["total_palettes"]
        in_use = palette_stats["in_use_palettes"]
        utilization = (in_use / total_palettes * 100) if total_palettes > 0 else 0.0

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "expeditions": {
                "total": exp_stats["total_expeditions"],
                "completed": exp_stats["completed_expeditions"],
                "active": exp_stats["active_expeditions"],
                "success_rate": exp_stats["success_rate"],
                "average_delivery_time": exp_stats["average_delivery_time_hours"],
                "delayed_count": exp_stats["delayed_expeditions"]
            },
            "palettes": {
                "total": total_palettes,
                "available": palette_stats["available_palettes"],
                "in_use": in_use,
                "utilization_rate": round(utilization, 2),
                "maintenance_needed": palette_stats["maintenance_needed"]
            },
            "notifications": {
                "total": total_notifications,
                "sent": sent_notifications,
                "success_rate": round(notification_success_rate, 2)
            },
            "overall_health": self._calculate_health_score(
                exp_stats["success_rate"],
                utilization,
                notification_success_rate
            )
        }

    def _calculate_health_score(
        self,
        expedition_success: float,
        palette_utilization: float,
        notification_success: float
    ) -> Dict[str, Any]:
        """
        Calculate overall system health score.

        Args:
            expedition_success: Expedition success rate
            palette_utilization: Palette utilization rate
            notification_success: Notification success rate

        Returns:
            Health score and status
        """
        # Weighted average (expedition 50%, palette 30%, notification 20%)
        health_score = (
            expedition_success * 0.5 +
            palette_utilization * 0.3 +
            notification_success * 0.2
        )

        if health_score >= 80:
            status = "EXCELLENT"
        elif health_score >= 60:
            status = "GOOD"
        elif health_score >= 40:
            status = "FAIR"
        else:
            status = "POOR"

        return {
            "score": round(health_score, 2),
            "status": status
        }

    # =============================================================================
    # Dashboard Data
    # =============================================================================

    def get_dashboard_overview(self) -> Dict[str, Any]:
        """
        Get complete dashboard overview data.

        Returns:
            Dictionary with all dashboard metrics
        """
        logger.info("Generating dashboard overview...")

        # Palette Stats
        result = self.db.execute(select(func.count()).select_from(Palette))
        total_palettes = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Palette).where(
                Palette.status.in_([PaletteStatus.AU_DEPOT, PaletteStatus.AU_CENTRE])
            )
        )
        available_palettes = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Palette).where(
                Palette.status.in_([PaletteStatus.EN_CHARGEMENT, PaletteStatus.EN_ROUTE_LIVRAISON, PaletteStatus.EN_ROUTE_RETOUR])
            )
        )
        palettes_in_transit = result.scalar() or 0

        # Calculate utilization rate
        utilization_rate = (palettes_in_transit / total_palettes * 100) if total_palettes > 0 else 0.0

        # Expedition Stats
        result = self.db.execute(select(func.count()).select_from(Expedition))
        total_expeditions = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Expedition).where(
                Expedition.status == ExpeditionStatus.EN_TRANSIT
            )
        )
        expeditions_in_transit = result.scalar() or 0

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = self.db.execute(
            select(func.count()).select_from(Expedition).where(
                Expedition.status == ExpeditionStatus.LIVREE,
                Expedition.date_delivery >= today_start
            )
        )
        completed_today = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Expedition).where(
                Expedition.eta < datetime.utcnow(),
                Expedition.status.notin_([ExpeditionStatus.LIVREE, ExpeditionStatus.ANNULEE]),
                Expedition.eta.isnot(None)
            )
        )
        delayed_expeditions = result.scalar() or 0

        # Notification Stats
        result = self.db.execute(select(func.count()).select_from(Notification))
        total_notifications = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Notification).where(
                Notification.status == NotificationStatus.SENT,
                Notification.created_at >= today_start
            )
        )
        sent_today = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Notification).where(
                Notification.status == NotificationStatus.FAILED,
                Notification.created_at >= today_start
            )
        )
        failed_today = result.scalar() or 0

        # Recent Activity (last 24 hours)
        last_24h = datetime.utcnow() - timedelta(hours=24)

        result = self.db.execute(
            select(func.count()).select_from(Expedition).where(
                Expedition.created_at >= last_24h
            )
        )
        recent_expeditions = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Expedition).where(
                Expedition.status == ExpeditionStatus.LIVREE,
                Expedition.date_delivery >= last_24h
            )
        )
        recent_deliveries = result.scalar() or 0

        result = self.db.execute(
            select(func.count()).select_from(Expedition).where(
                Expedition.status == ExpeditionStatus.ARRIVEE
            )
        )
        pending_validations = result.scalar() or 0

        # Alerts
        result = self.db.execute(
            select(func.count()).select_from(Notification).where(
                Notification.status == NotificationStatus.FAILED
            )
        )
        failed_notifications = result.scalar() or 0

        # Trends (7 days)
        expedition_trend = self.get_expedition_trend(days=7)
        expeditions_7days = [
            {"date": item["date"], "count": item["expedition_count"]}
            for item in expedition_trend
        ]

        # For deliveries, we'll get completed expeditions in the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = self.db.execute(
            select(
                func.date(Expedition.date_delivery).label('date'),
                func.count(Expedition.id).label('count')
            ).where(
                Expedition.date_delivery >= seven_days_ago,
                Expedition.status == ExpeditionStatus.LIVREE
            ).group_by(
                func.date(Expedition.date_delivery)
            ).order_by(
                func.date(Expedition.date_delivery)
            )
        )
        deliveries_data = result.all()
        deliveries_7days = [
            {"date": str(row.date), "count": row.count}
            for row in deliveries_data
        ]

        # Calculate health score
        expedition_success_rate = (completed_today / expeditions_in_transit * 100) if expeditions_in_transit > 0 else 100.0
        notification_success_rate = ((sent_today / (sent_today + failed_today)) * 100) if (sent_today + failed_today) > 0 else 100.0

        health_score = (
            expedition_success_rate * 0.5 +
            utilization_rate * 0.3 +
            notification_success_rate * 0.2
        )

        if health_score >= 80:
            health_status = "EXCELLENT"
        elif health_score >= 60:
            health_status = "GOOD"
        elif health_score >= 40:
            health_status = "FAIR"
        else:
            health_status = "POOR"

        return {
            "palette_stats": {
                "total": total_palettes,
                "available": available_palettes,
                "in_transit": palettes_in_transit,
                "utilization_rate": round(utilization_rate, 2)
            },
            "expedition_stats": {
                "total": total_expeditions,
                "in_transit": expeditions_in_transit,
                "completed_today": completed_today,
                "delayed": delayed_expeditions
            },
            "notification_stats": {
                "total": total_notifications,
                "sent_today": sent_today,
                "failed_today": failed_today
            },
            "recent_activity": {
                "recent_expeditions": recent_expeditions,
                "recent_deliveries": recent_deliveries,
                "pending_validations": pending_validations
            },
            "alerts": {
                "delayed_expeditions": delayed_expeditions,
                "pending_validations": pending_validations,
                "failed_notifications": failed_notifications
            },
            "trends": {
                "expeditions_7days": expeditions_7days,
                "deliveries_7days": deliveries_7days
            },
            "health_score": round(health_score, 2),
            "health_status": health_status
        }

    # =============================================================================
    # User Performance
    # =============================================================================

    def get_user_performance(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user performance metrics.

        Args:
            user_id: Specific user ID (optional, if None returns all users)
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of user performance data
        """
        logger.info("Generating user performance report...")

        query = self.db.query(
            User.id,
            User.username,
            User.email,
            func.count(Expedition.id).label('expeditions_created')
        ).outerjoin(
            Expedition, User.id == Expedition.created_by_id
        )

        if user_id:
            query = query.filter(User.id == user_id)

        if start_date:
            query = query.filter(Expedition.created_at >= start_date)
        if end_date:
            query = query.filter(Expedition.created_at <= end_date)

        results = query.group_by(
            User.id, User.username, User.email
        ).all()

        return [
            {
                "user_id": str(row.id),
                "username": row.username,
                "email": row.email,
                "expeditions_created": row.expeditions_created
            }
            for row in results
        ]

    # =============================================================================
    # Export Data
    # =============================================================================

    def export_expedition_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> Any:
        """
        Export expedition data for external analysis.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            format: Export format (json, csv)

        Returns:
            Exported data in requested format
        """
        logger.info(f"Exporting expedition data in {format} format...")

        query = self.db.query(Expedition)

        if start_date:
            query = query.filter(Expedition.created_at >= start_date)
        if end_date:
            query = query.filter(Expedition.created_at <= end_date)

        expeditions = query.all()

        if format.lower() == "json":
            return [
                {
                    "reference_number": exp.reference_number,
                    "status": exp.status.value,
                    "destination": exp.destination_address,
                    "palette_count": exp.palette_count,
                    "created_at": exp.created_at.isoformat() if exp.created_at else None,
                    "date_depart": exp.date_depart.isoformat() if exp.date_depart else None,
                    "date_delivery": exp.date_delivery.isoformat() if exp.date_delivery else None,
                    "eta": exp.eta.isoformat() if exp.eta else None
                }
                for exp in expeditions
            ]
        elif format.lower() == "csv":
            # Return CSV-formatted string
            headers = [
                "reference_number", "status", "destination", "palette_count",
                "created_at", "date_depart", "date_delivery", "eta"
            ]

            rows = []
            for exp in expeditions:
                rows.append([
                    exp.reference_number,
                    exp.status.value,
                    exp.destination_address or "",
                    str(exp.palette_count),
                    exp.created_at.isoformat() if exp.created_at else "",
                    exp.date_depart.isoformat() if exp.date_depart else "",
                    exp.date_delivery.isoformat() if exp.date_delivery else "",
                    exp.eta.isoformat() if exp.eta else ""
                ])

            csv_data = ",".join(headers) + "\n"
            csv_data += "\n".join([",".join(row) for row in rows])

            return csv_data
        else:
            raise ValidationException(
                message=f"Unsupported export format: {format}",
                details={"format": format}
            )

    def export_palette_data(
        self,
        format: str = "json"
    ) -> Any:
        """
        Export palette data for external analysis.

        Args:
            format: Export format (json, csv)

        Returns:
            Exported data in requested format
        """
        logger.info(f"Exporting palette data in {format} format...")

        palettes = self.db.query(Palette).all()

        if format.lower() == "json":
            return [
                {
                    "reference_number": p.reference_number,
                    "rfid_tag": p.rfid_tag,
                    "status": p.status.value,
                    "capacity": p.capacity,
                    "current_bottles": p.current_bottles,
                    "utilization_rate": p.utilization_rate,
                    "current_location": p.current_location,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in palettes
            ]
        elif format.lower() == "csv":
            headers = [
                "reference_number", "rfid_tag", "status", "capacity",
                "current_bottles", "utilization_rate", "current_location", "created_at"
            ]

            rows = []
            for p in palettes:
                rows.append([
                    p.reference_number,
                    p.rfid_tag or "",
                    p.status.value,
                    str(p.capacity),
                    str(p.current_bottles),
                    str(p.utilization_rate or 0),
                    p.current_location or "",
                    p.created_at.isoformat() if p.created_at else ""
                ])

            csv_data = ",".join(headers) + "\n"
            csv_data += "\n".join([",".join(row) for row in rows])

            return csv_data
        else:
            raise ValidationException(
                message=f"Unsupported export format: {format}",
                details={"format": format}
            )
