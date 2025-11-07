"""
Reports Routes

API endpoints for reports, statistics, analytics, and data export.
Includes palette reports, expedition reports, performance metrics,
dashboard data, and export functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.schemas.reports import (
    PaletteStatistics,
    PaletteUtilizationTrend,
    PaletteDistribution,
    ExpeditionStatistics,
    ExpeditionTrend,
    TopDestinations,
    PerformanceReport,
    DashboardOverview,
    UserPerformanceReport,
    ExportRequest,
    DailyUtilizationData,
    DailyExpeditionData,
    DestinationData
)
from app.services.reports_service import ReportsService
from app.middleware.auth_middleware import get_current_user
from app.middleware.rbac import require_role

router = APIRouter()


# =============================================================================
# Palette Reports
# =============================================================================

@router.get(
    "/palettes/statistics",
    response_model=PaletteStatistics,
    summary="Get palette statistics",
    description="Get comprehensive palette statistics including status distribution, utilization, and maintenance needs."
)
async def get_palette_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get palette statistics.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns:
    - Total palettes count
    - Distribution by status
    - Average utilization rate
    - Top 10 most used palettes
    - Maintenance needs
    """
    reports_service = ReportsService(db)
    stats = reports_service.get_palette_statistics(start_date, end_date)
    return PaletteStatistics(**stats)


@router.get(
    "/palettes/utilization-trend",
    response_model=PaletteUtilizationTrend,
    summary="Get palette utilization trend",
    description="Get palette utilization trend over time."
)
async def get_palette_utilization_trend(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get palette utilization trend.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns daily movement counts and unique palette usage over the specified period.
    """
    reports_service = ReportsService(db)
    trend_data = reports_service.get_palette_utilization_trend(days)

    return PaletteUtilizationTrend(
        data=[DailyUtilizationData(**d) for d in trend_data],
        days=days
    )


@router.get(
    "/palettes/distribution",
    response_model=PaletteDistribution,
    summary="Get palette distribution by location",
    description="Get current palette distribution across locations."
)
async def get_palette_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get palette distribution by location.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns count of palettes at each location.
    """
    reports_service = ReportsService(db)
    distribution = reports_service.get_palette_distribution_by_location()
    return PaletteDistribution(distribution=distribution)


# =============================================================================
# Expedition Reports
# =============================================================================

@router.get(
    "/expeditions/statistics",
    response_model=ExpeditionStatistics,
    summary="Get expedition statistics",
    description="Get comprehensive expedition statistics including success rate, delivery times, and delays."
)
async def get_expedition_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get expedition statistics.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns:
    - Total expeditions count
    - Distribution by status
    - Average delivery time
    - Success rate
    - Delayed expeditions
    - Problems reported
    """
    reports_service = ReportsService(db)
    stats = reports_service.get_expedition_statistics(start_date, end_date)
    return ExpeditionStatistics(**stats)


@router.get(
    "/expeditions/trend",
    response_model=ExpeditionTrend,
    summary="Get expedition trend",
    description="Get expedition creation trend over time."
)
async def get_expedition_trend(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get expedition trend.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns daily expedition counts and palette totals over the specified period.
    """
    reports_service = ReportsService(db)
    trend_data = reports_service.get_expedition_trend(days)

    return ExpeditionTrend(
        data=[DailyExpeditionData(**d) for d in trend_data],
        days=days
    )


@router.get(
    "/expeditions/top-destinations",
    response_model=TopDestinations,
    summary="Get top destinations",
    description="Get top destinations by expedition count."
)
async def get_top_destinations(
    limit: int = Query(10, ge=1, le=50, description="Number of destinations to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get top destinations.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns the most frequent expedition destinations with counts.
    """
    reports_service = ReportsService(db)
    destinations = reports_service.get_top_destinations(limit)

    return TopDestinations(
        destinations=[DestinationData(**d) for d in destinations],
        limit=limit
    )


# =============================================================================
# Performance Reports
# =============================================================================

@router.get(
    "/performance",
    response_model=PerformanceReport,
    summary="Get performance report",
    description="Get comprehensive system performance report including all metrics and health score."
)
async def get_performance_report(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get comprehensive performance report.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns:
    - Expedition performance metrics
    - Palette performance metrics
    - Notification performance metrics
    - Overall system health score
    """
    reports_service = ReportsService(db)
    report = reports_service.get_performance_report(start_date, end_date)
    return PerformanceReport(**report)


# =============================================================================
# Dashboard
# =============================================================================

@router.get(
    "/dashboard/overview",
    response_model=DashboardOverview,
    summary="Get dashboard overview",
    description="Get complete dashboard overview with real-time metrics, trends, and alerts."
)
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard overview.

    Available to all authenticated users.

    Returns:
    - Overview metrics (palettes, expeditions, notifications)
    - Recent activity (last 24 hours)
    - Active alerts (delays, pending validations)
    - 7-day trends (expeditions, palette utilization)
    """
    reports_service = ReportsService(db)
    overview = await reports_service.get_dashboard_overview()
    return DashboardOverview(**overview)


# =============================================================================
# User Performance
# =============================================================================

@router.get(
    "/users/performance",
    response_model=UserPerformanceReport,
    summary="Get user performance",
    description="Get user performance metrics including expeditions created."
)
async def get_user_performance(
    user_id: Optional[str] = Query(None, description="Specific user ID (optional)"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """
    Get user performance metrics.

    Required roles: ADMIN

    Returns performance data for all users or a specific user.
    """
    reports_service = ReportsService(db)
    performance = reports_service.get_user_performance(user_id, start_date, end_date)

    return UserPerformanceReport(
        users=performance,
        period={
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    )


# =============================================================================
# Export
# =============================================================================

@router.get(
    "/export/expeditions",
    summary="Export expedition data",
    description="Export expedition data in JSON or CSV format."
)
async def export_expeditions(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    format: str = Query("json", regex="^(json|csv)$", description="Export format (json, csv)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Export expedition data.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns expedition data in the specified format (JSON or CSV).
    """
    reports_service = ReportsService(db)
    data = reports_service.export_expedition_data(start_date, end_date, format)

    if format.lower() == "csv":
        return Response(
            content=data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=expeditions_{datetime.utcnow().strftime('%Y%m%d')}.csv"
            }
        )
    else:
        return {
            "format": format,
            "record_count": len(data),
            "data": data
        }


@router.get(
    "/export/palettes",
    summary="Export palette data",
    description="Export palette data in JSON or CSV format."
)
async def export_palettes(
    format: str = Query("json", regex="^(json|csv)$", description="Export format (json, csv)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Export palette data.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns all palette data in the specified format (JSON or CSV).
    """
    reports_service = ReportsService(db)
    data = reports_service.export_palette_data(format)

    if format.lower() == "csv":
        return Response(
            content=data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=palettes_{datetime.utcnow().strftime('%Y%m%d')}.csv"
            }
        )
    else:
        return {
            "format": format,
            "record_count": len(data),
            "data": data
        }


# =============================================================================
# Quick Stats (Public for operators)
# =============================================================================

@router.get(
    "/quick-stats",
    summary="Get quick statistics",
    description="Get quick statistics available to all users."
)
async def get_quick_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get quick statistics.

    Available to all authenticated users.

    Returns basic counts for quick overview.
    """
    from app.models.palette import Palette, PaletteStatus
    from app.models.expedition import Expedition, ExpeditionStatus

    total_palettes = db.query(func.count(Palette.id)).scalar()
    available_palettes = db.query(func.count(Palette.id)).filter(
        Palette.status == PaletteStatus.EN_STOCK
    ).scalar()

    active_expeditions = db.query(func.count(Expedition.id)).filter(
        Expedition.status.in_([
            ExpeditionStatus.CREEE,
            ExpeditionStatus.EN_TRANSIT,
            ExpeditionStatus.ARRIVEE
        ])
    ).scalar()

    return {
        "total_palettes": total_palettes,
        "available_palettes": available_palettes,
        "active_expeditions": active_expeditions
    }
