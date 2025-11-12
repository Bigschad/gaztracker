"""
Notification Routes

API endpoints for notification management including sending emails/SMS,
viewing notification history, and managing automatic alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import math

from app.database import get_db
from app.models.user import User
from app.models.notification import NotificationType, NotificationStatus, NotificationChannel
from app.schemas.notification import (
    NotificationCreate,
    NotificationSendEmail,
    NotificationSendSMS,
    NotificationRetry,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatistics
)
from app.services.notification_service import NotificationService
from app.middleware.auth_middleware import get_current_user
from app.middleware.rbac import require_role
from app.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    ExternalServiceException
)
from app.utils.automatic_alerts import AutomaticAlerts

router = APIRouter()


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification",
    description="Create a new notification record (without sending it immediately)."
)
async def create_notification(
    notification_create: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Create a new notification.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    The notification will be created with PENDING status.
    Use the /send endpoint to actually send it.
    """
    try:
        notification_service = NotificationService(db)
        notification = notification_service.create_notification(notification_create)
        return notification
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/send-now",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and send notification immediately",
    description="Create a notification and send it immediately via email/SMS."
)
async def send_notification_now(
    notification_create: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Create and send a notification immediately.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    The notification will be created and sent through the specified channel(s).
    """
    try:
        notification_service = NotificationService(db)
        notification = notification_service.send_notification_now(notification_create)
        return notification
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ExternalServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )


@router.post(
    "/send-email",
    status_code=status.HTTP_200_OK,
    summary="Send a standalone email",
    description="Send an email without creating a notification record."
)
async def send_email(
    email_data: NotificationSendEmail,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Send a standalone email.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    This is useful for one-off emails that don't need to be tracked.
    """
    try:
        notification_service = NotificationService(db)
        success = notification_service.send_email(
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=email_data.body,
            is_html=email_data.is_html
        )
        return {"success": success, "message": "Email sent successfully"}
    except ExternalServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )


@router.post(
    "/send-sms",
    status_code=status.HTTP_200_OK,
    summary="Send a standalone SMS",
    description="Send an SMS without creating a notification record."
)
async def send_sms(
    sms_data: NotificationSendSMS,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Send a standalone SMS.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    This is useful for one-off SMS that don't need to be tracked.
    """
    try:
        notification_service = NotificationService(db)
        success = notification_service.send_sms(
            to_phone=sms_data.to_phone,
            message=sms_data.message
        )
        return {"success": success, "message": "SMS sent successfully"}
    except ExternalServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="List notifications",
    description="Get a paginated list of notifications with optional filters."
)
async def list_notifications(
    status_filter: Optional[NotificationStatus] = Query(None, alias="status", description="Filter by status"),
    type_filter: Optional[NotificationType] = Query(None, alias="type", description="Filter by type"),
    channel_filter: Optional[NotificationChannel] = Query(None, alias="channel", description="Filter by channel"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all notifications with pagination and filters.

    Supports filtering by:
    - Status (PENDING, SENT, FAILED, RETRYING)
    - Type (EXPEDITION_CREEE, ALERTE_RETARD, etc.)
    - Channel (EMAIL, SMS, BOTH)
    """
    notification_service = NotificationService(db)
    notifications, total = notification_service.list_notifications(
        status=status_filter,
        notification_type=type_filter,
        channel=channel_filter,
        page=page,
        page_size=page_size
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return NotificationListResponse(
        items=notifications,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification details",
    description="Get detailed information about a specific notification."
)
async def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific notification by ID.
    """
    try:
        notification_service = NotificationService(db)
        notification = notification_service.get_notification(notification_id)
        return notification
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{notification_id}/send",
    response_model=NotificationResponse,
    summary="Send a pending notification",
    description="Send a notification that was previously created but not sent."
)
async def send_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Send a pending notification.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    The notification must be in PENDING status.
    """
    try:
        notification_service = NotificationService(db)
        notification = notification_service.send_notification(notification_id)
        return notification
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ExternalServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )


@router.post(
    "/retry/failed",
    summary="Retry failed notifications",
    description="Retry all failed notifications that haven't exceeded max retries."
)
async def retry_failed_notifications(
    max_retries: int = Query(3, ge=1, le=10, description="Maximum retry attempts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """
    Retry all failed notifications.

    Required roles: ADMIN

    This will attempt to resend all notifications in FAILED or RETRYING status
    that haven't exceeded the maximum number of retries.
    """
    notification_service = NotificationService(db)
    count = notification_service.retry_failed_notifications(max_retries=max_retries)
    return {
        "success": True,
        "retried_count": count,
        "message": f"Retried {count} failed notifications"
    }


@router.get(
    "/statistics/overview",
    response_model=NotificationStatistics,
    summary="Get notification statistics",
    description="Get statistical overview of all notifications."
)
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Get notification statistics.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    Returns:
    - Total number of notifications
    - Count by status
    - Count by type
    - Count by channel
    - Success rate
    - Failed notifications count
    """
    notification_service = NotificationService(db)
    stats = notification_service.get_notification_statistics()
    return NotificationStatistics(**stats)


@router.post(
    "/alerts/check-delays",
    summary="Check for delayed expeditions",
    description="Manually trigger check for delayed expeditions and send alerts."
)
async def check_delayed_expeditions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Check for delayed expeditions and send alerts.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    This will find all expeditions past their ETA and send delay alerts.
    """
    alerts = AutomaticAlerts(db)
    count = alerts.check_delayed_expeditions()
    return {
        "success": True,
        "alerts_sent": count,
        "message": f"Sent {count} delay alerts"
    }


@router.post(
    "/alerts/check-validations",
    summary="Check for pending validations",
    description="Manually trigger check for pending validations and send reminders."
)
async def check_pending_validations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RESPONSABLE_LOGISTIQUE"]))
):
    """
    Check for expeditions requiring validation and send reminders.

    Required roles: ADMIN, RESPONSABLE_LOGISTIQUE

    This will find all expeditions in ARRIVEE status and send validation reminders.
    """
    alerts = AutomaticAlerts(db)
    count = alerts.check_pending_validations()
    return {
        "success": True,
        "reminders_sent": count,
        "message": f"Sent {count} validation reminders"
    }


@router.post(
    "/alerts/run-all",
    summary="Run all automatic checks",
    description="Run all automatic alert checks (delays, validations, etc.)."
)
async def run_all_checks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """
    Run all automatic alert checks.

    Required roles: ADMIN

    This will:
    - Check for delayed expeditions
    - Check for pending validations
    - Send appropriate alerts
    """
    alerts = AutomaticAlerts(db)
    results = alerts.run_all_checks()
    return {
        "success": True,
        "results": results,
        "message": f"All checks complete: {results['total_alerts']} alerts sent"
    }
