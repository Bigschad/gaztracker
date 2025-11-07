"""
Report Schemas

Pydantic models for reports, statistics, and analytics responses.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


# =============================================================================
# Palette Statistics Schemas
# =============================================================================

class MostUsedPalette(BaseModel):
    """Schema for most used palette data."""
    id: str
    reference: str
    movements: int

    class Config:
        from_attributes = True


class PaletteStatistics(BaseModel):
    """Schema for palette statistics response."""
    total_palettes: int = Field(..., description="Total number of palettes")
    by_status: Dict[str, int] = Field(..., description="Count by status")
    average_utilization: float = Field(..., description="Average utilization rate")
    most_used_palettes: List[MostUsedPalette] = Field(..., description="Top 10 most used palettes")
    maintenance_needed: int = Field(..., description="Palettes needing maintenance")
    available_palettes: int = Field(..., description="Available palettes")
    in_use_palettes: int = Field(..., description="Palettes in use")
    damaged_palettes: int = Field(..., description="Damaged palettes")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_palettes": 100,
                "by_status": {
                    "DISPONIBLE": 50,
                    "EN_EXPEDITION": 30,
                    "EN_MAINTENANCE": 10,
                    "ENDOMMAGEE": 5,
                    "RETIREE": 5
                },
                "average_utilization": 65.5,
                "most_used_palettes": [
                    {"id": "uuid", "reference": "PAL-001", "movements": 45}
                ],
                "maintenance_needed": 15,
                "available_palettes": 50,
                "in_use_palettes": 30,
                "damaged_palettes": 5
            }
        }


class DailyUtilizationData(BaseModel):
    """Schema for daily utilization data point."""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    movement_count: int = Field(..., description="Number of movements")
    unique_palettes: int = Field(..., description="Unique palettes moved")

    class Config:
        from_attributes = True


class PaletteUtilizationTrend(BaseModel):
    """Schema for palette utilization trend response."""
    data: List[DailyUtilizationData] = Field(..., description="Daily utilization data")
    days: int = Field(..., description="Number of days analyzed")

    class Config:
        from_attributes = True


class PaletteDistribution(BaseModel):
    """Schema for palette distribution by location."""
    distribution: Dict[str, int] = Field(..., description="Location to count mapping")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "distribution": {
                    "Warehouse A": 45,
                    "Warehouse B": 30,
                    "In Transit": 25
                }
            }
        }


# =============================================================================
# Expedition Statistics Schemas
# =============================================================================

class ExpeditionStatistics(BaseModel):
    """Schema for expedition statistics response."""
    total_expeditions: int = Field(..., description="Total expeditions")
    by_status: Dict[str, int] = Field(..., description="Count by status")
    average_delivery_time_hours: float = Field(..., description="Average delivery time in hours")
    success_rate: float = Field(..., description="Success rate percentage")
    delayed_expeditions: int = Field(..., description="Expeditions delayed")
    problems_reported: int = Field(..., description="Problems reported")
    completed_expeditions: int = Field(..., description="Completed expeditions")
    active_expeditions: int = Field(..., description="Active expeditions")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_expeditions": 150,
                "by_status": {
                    "PREPAREE": 10,
                    "DEPART": 15,
                    "EN_ROUTE": 20,
                    "ARRIVEE": 5,
                    "LIVREE": 90,
                    "ANNULEE": 5,
                    "PROBLEME": 5
                },
                "average_delivery_time_hours": 24.5,
                "success_rate": 95.5,
                "delayed_expeditions": 3,
                "problems_reported": 5,
                "completed_expeditions": 90,
                "active_expeditions": 35
            }
        }


class DailyExpeditionData(BaseModel):
    """Schema for daily expedition data point."""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    expedition_count: int = Field(..., description="Number of expeditions")
    total_palettes: int = Field(..., description="Total palettes")

    class Config:
        from_attributes = True


class ExpeditionTrend(BaseModel):
    """Schema for expedition trend response."""
    data: List[DailyExpeditionData] = Field(..., description="Daily expedition data")
    days: int = Field(..., description="Number of days analyzed")

    class Config:
        from_attributes = True


class DestinationData(BaseModel):
    """Schema for destination data."""
    address: str = Field(..., description="Destination address")
    expedition_count: int = Field(..., description="Number of expeditions")
    total_palettes: int = Field(..., description="Total palettes sent")

    class Config:
        from_attributes = True


class TopDestinations(BaseModel):
    """Schema for top destinations response."""
    destinations: List[DestinationData] = Field(..., description="Top destinations")
    limit: int = Field(..., description="Number of destinations returned")

    class Config:
        from_attributes = True


# =============================================================================
# Performance Report Schemas
# =============================================================================

class PeriodInfo(BaseModel):
    """Schema for report period information."""
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date")

    class Config:
        from_attributes = True


class ExpeditionPerformance(BaseModel):
    """Schema for expedition performance metrics."""
    total: int = Field(..., description="Total expeditions")
    completed: int = Field(..., description="Completed expeditions")
    active: int = Field(..., description="Active expeditions")
    success_rate: float = Field(..., description="Success rate percentage")
    average_delivery_time: float = Field(..., description="Average delivery time in hours")
    delayed_count: int = Field(..., description="Delayed expeditions")

    class Config:
        from_attributes = True


class PalettePerformance(BaseModel):
    """Schema for palette performance metrics."""
    total: int = Field(..., description="Total palettes")
    available: int = Field(..., description="Available palettes")
    in_use: int = Field(..., description="Palettes in use")
    utilization_rate: float = Field(..., description="Utilization rate percentage")
    maintenance_needed: int = Field(..., description="Palettes needing maintenance")

    class Config:
        from_attributes = True


class NotificationPerformance(BaseModel):
    """Schema for notification performance metrics."""
    total: int = Field(..., description="Total notifications")
    sent: int = Field(..., description="Sent notifications")
    success_rate: float = Field(..., description="Success rate percentage")

    class Config:
        from_attributes = True


class HealthScore(BaseModel):
    """Schema for system health score."""
    score: float = Field(..., description="Overall health score (0-100)")
    status: str = Field(..., description="Health status (EXCELLENT, GOOD, FAIR, POOR)")

    class Config:
        from_attributes = True


class PerformanceReport(BaseModel):
    """Schema for comprehensive performance report."""
    period: PeriodInfo = Field(..., description="Report period")
    expeditions: ExpeditionPerformance = Field(..., description="Expedition metrics")
    palettes: PalettePerformance = Field(..., description="Palette metrics")
    notifications: NotificationPerformance = Field(..., description="Notification metrics")
    overall_health: HealthScore = Field(..., description="Overall system health")

    class Config:
        from_attributes = True


# =============================================================================
# Dashboard Schemas
# =============================================================================

class PaletteStats(BaseModel):
    """Schema for palette statistics in dashboard."""
    total: int = Field(..., description="Total palettes")
    available: int = Field(..., description="Available palettes")
    in_transit: int = Field(..., description="Palettes in transit")
    utilization_rate: float = Field(..., description="Utilization rate percentage")

    class Config:
        from_attributes = True


class ExpeditionStats(BaseModel):
    """Schema for expedition statistics in dashboard."""
    total: int = Field(..., description="Total expeditions")
    in_transit: int = Field(..., description="Expeditions in transit")
    completed_today: int = Field(..., description="Expeditions completed today")
    delayed: int = Field(..., description="Delayed expeditions")

    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """Schema for notification statistics in dashboard."""
    total: int = Field(..., description="Total notifications")
    sent_today: int = Field(..., description="Notifications sent today")
    failed_today: int = Field(..., description="Notifications failed today")

    class Config:
        from_attributes = True


class RecentActivity(BaseModel):
    """Schema for recent activity metrics."""
    recent_expeditions: int = Field(..., description="Recent expeditions")
    recent_deliveries: int = Field(..., description="Recent deliveries")
    pending_validations: int = Field(..., description="Pending validations")

    class Config:
        from_attributes = True


class AlertMetrics(BaseModel):
    """Schema for alert metrics."""
    delayed_expeditions: int = Field(..., description="Delayed expeditions")
    pending_validations: int = Field(..., description="Pending validations")
    failed_notifications: int = Field(..., description="Failed notifications")

    class Config:
        from_attributes = True


class TrendDataPoint(BaseModel):
    """Schema for trend data point."""
    date: str = Field(..., description="Date")
    count: int = Field(..., description="Count")

    class Config:
        from_attributes = True


class DashboardTrends(BaseModel):
    """Schema for dashboard trends."""
    expeditions_7days: List[TrendDataPoint] = Field(..., description="Expedition trend (7 days)")
    deliveries_7days: List[TrendDataPoint] = Field(..., description="Delivery trend (7 days)")

    class Config:
        from_attributes = True


class DashboardOverview(BaseModel):
    """Schema for complete dashboard overview."""
    palette_stats: PaletteStats = Field(..., description="Palette statistics")
    expedition_stats: ExpeditionStats = Field(..., description="Expedition statistics")
    notification_stats: NotificationStats = Field(..., description="Notification statistics")
    recent_activity: RecentActivity = Field(..., description="Recent activity")
    alerts: AlertMetrics = Field(..., description="Alert counts")
    trends: DashboardTrends = Field(..., description="Trends data")
    health_score: float = Field(..., description="Overall health score (0-100)")
    health_status: str = Field(..., description="Health status (EXCELLENT, GOOD, FAIR, POOR)")

    class Config:
        from_attributes = True


# =============================================================================
# User Performance Schemas
# =============================================================================

class UserPerformanceData(BaseModel):
    """Schema for individual user performance."""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    expeditions_created: int = Field(..., description="Expeditions created")

    class Config:
        from_attributes = True


class UserPerformanceReport(BaseModel):
    """Schema for user performance report."""
    users: List[UserPerformanceData] = Field(..., description="User performance data")
    period: PeriodInfo = Field(..., description="Report period")

    class Config:
        from_attributes = True


# =============================================================================
# Export Schemas
# =============================================================================

class ExportRequest(BaseModel):
    """Schema for export request."""
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    format: str = Field("json", description="Export format (json, csv)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-01-31T23:59:59",
                "format": "json"
            }
        }


class ExportResponse(BaseModel):
    """Schema for export response."""
    format: str = Field(..., description="Export format")
    record_count: int = Field(..., description="Number of records")
    data: Any = Field(..., description="Exported data")

    class Config:
        from_attributes = True


# =============================================================================
# Query Parameter Schemas
# =============================================================================

class DateRangeParams(BaseModel):
    """Schema for date range query parameters."""
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")

    class Config:
        from_attributes = True


class TrendParams(BaseModel):
    """Schema for trend query parameters."""
    days: int = Field(30, ge=1, le=365, description="Number of days")

    class Config:
        from_attributes = True
