"""
Notification Service

Business logic for notifications (Email/SMS) including templates,
retry logic, and automatic alerts.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

try:
    from twilio.rest import Client as TwilioClient
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    TwilioClient = None
    TwilioRestException = None

from app.models.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationChannel
)
from app.models.expedition import Expedition
from app.models.palette import Palette
from app.schemas.notification import NotificationCreate
from app.config import settings
from app.utils.exceptions import (
    ValidationException,
    ExternalServiceException,
    ResourceNotFoundException
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications (Email/SMS)."""

    def __init__(self, db: Session):
        """
        Initialize notification service.

        Args:
            db: Database session
        """
        self.db = db
        self._twilio_client = None

    @property
    def twilio_client(self) -> Optional[TwilioClient]:
        """
        Get Twilio client (lazy initialization).

        Returns:
            Twilio client if configured, None otherwise
        """
        if not TWILIO_AVAILABLE:
            logger.warning("Twilio SDK not installed")
            return None

        if not settings.ENABLE_SMS_NOTIFICATIONS:
            return None

        if self._twilio_client is None and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self._twilio_client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                logger.info("Twilio client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                return None

        return self._twilio_client

    # =============================================================================
    # Email Notifications
    # =============================================================================

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        """
        Send email notification via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (can be HTML)
            is_html: Whether body is HTML

        Returns:
            True if sent successfully, False otherwise

        Raises:
            ExternalServiceException: If email sending fails critically
        """
        if not settings.ENABLE_EMAIL_NOTIFICATIONS:
            logger.info("Email notifications are disabled")
            return False

        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.error("SMTP credentials not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg['To'] = to_email

            # Attach body
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type, 'utf-8'))

            # Connect to SMTP server
            if settings.SMTP_SSL:
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                if settings.SMTP_TLS:
                    server.starttls()

            # Login and send
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            raise ExternalServiceException(
                service="SMTP",
                message=f"Failed to send email: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            raise ExternalServiceException(
                service="Email",
                message=f"Unexpected error: {str(e)}"
            )

    # =============================================================================
    # SMS Notifications
    # =============================================================================

    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> bool:
        """
        Send SMS notification via Twilio.

        Args:
            to_phone: Recipient phone number (E.164 format)
            message: SMS message (max 160 characters)

        Returns:
            True if sent successfully, False otherwise

        Raises:
            ExternalServiceException: If SMS sending fails critically
        """
        if not settings.ENABLE_SMS_NOTIFICATIONS:
            logger.info("SMS notifications are disabled")
            return False

        if not TWILIO_AVAILABLE:
            logger.error("Twilio SDK not available")
            return False

        if not self.twilio_client:
            logger.error("Twilio client not initialized")
            return False

        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )

            logger.info(f"SMS sent successfully to {to_phone}, SID: {message_obj.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_phone}: {e}")
            raise ExternalServiceException(
                service="Twilio",
                message=f"Failed to send SMS: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_phone}: {e}")
            raise ExternalServiceException(
                service="SMS",
                message=f"Unexpected error: {str(e)}"
            )

    # =============================================================================
    # Notification CRUD
    # =============================================================================

    def create_notification(
        self,
        notification_create: NotificationCreate
    ) -> Notification:
        """
        Create a new notification record.

        Args:
            notification_create: Notification creation data

        Returns:
            Created notification

        Raises:
            ValidationException: If validation fails
        """
        # Validate channel requirements
        if notification_create.channel in [NotificationChannel.EMAIL, NotificationChannel.BOTH]:
            if not notification_create.recipient_email:
                raise ValidationException(
                    message="Email address required for EMAIL channel",
                    details={"channel": notification_create.channel.value}
                )

        if notification_create.channel in [NotificationChannel.SMS, NotificationChannel.BOTH]:
            if not notification_create.recipient_phone:
                raise ValidationException(
                    message="Phone number required for SMS channel",
                    details={"channel": notification_create.channel.value}
                )

        # Create notification
        notification = Notification(
            type=notification_create.type,
            status=NotificationStatus.PENDING,
            channel=notification_create.channel,
            recipient_email=notification_create.recipient_email,
            recipient_phone=notification_create.recipient_phone,
            subject=notification_create.subject,
            message=notification_create.message,
            expedition_id=notification_create.expedition_id,
            palette_id=notification_create.palette_id,
            retry_count="0"
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        logger.info(f"Notification created: {notification.id} ({notification.type.value})")
        return notification

    def get_notification(
        self,
        notification_id: UUID
    ) -> Notification:
        """
        Get a notification by ID.

        Args:
            notification_id: Notification UUID

        Returns:
            Notification

        Raises:
            ResourceNotFoundException: If notification not found
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification:
            raise ResourceNotFoundException(
                resource_type="Notification",
                resource_id=notification_id
            )

        return notification

    def list_notifications(
        self,
        status: Optional[NotificationStatus] = None,
        notification_type: Optional[NotificationType] = None,
        channel: Optional[NotificationChannel] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Notification], int]:
        """
        List notifications with filters and pagination.

        Args:
            status: Filter by status
            notification_type: Filter by type
            channel: Filter by channel
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Tuple of (notifications list, total count)
        """
        query = self.db.query(Notification)

        # Apply filters
        if status:
            query = query.filter(Notification.status == status)
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        if channel:
            query = query.filter(Notification.channel == channel)

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(page_size).all()

        logger.info(f"Listed {len(notifications)} notifications (total: {total})")
        return notifications, total

    # =============================================================================
    # Send Notification
    # =============================================================================

    def send_notification(
        self,
        notification_id: UUID
    ) -> Notification:
        """
        Send a notification (email and/or SMS).

        Args:
            notification_id: Notification ID to send

        Returns:
            Updated notification

        Raises:
            ResourceNotFoundException: If notification not found
            ExternalServiceException: If sending fails
        """
        notification = self.get_notification(notification_id)

        # Check if already sent
        if notification.status == NotificationStatus.SENT:
            logger.warning(f"Notification {notification_id} already sent")
            return notification

        try:
            success = False

            # Send email if required
            if notification.channel in [NotificationChannel.EMAIL, NotificationChannel.BOTH]:
                if notification.recipient_email:
                    email_success = self.send_email(
                        to_email=notification.recipient_email,
                        subject=notification.subject or "Notification",
                        body=notification.message,
                        is_html=True
                    )
                    success = email_success
                else:
                    logger.error(f"No recipient email for notification {notification_id}")

            # Send SMS if required
            if notification.channel in [NotificationChannel.SMS, NotificationChannel.BOTH]:
                if notification.recipient_phone:
                    sms_success = self.send_sms(
                        to_phone=notification.recipient_phone,
                        message=notification.message[:160]  # Truncate to 160 chars
                    )
                    success = success or sms_success
                else:
                    logger.error(f"No recipient phone for notification {notification_id}")

            # Update notification status
            if success:
                notification.mark_as_sent()
            else:
                notification.mark_as_failed("Failed to send through any channel")

            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)

            return notification

        except ExternalServiceException as e:
            # Mark as failed
            notification.mark_as_failed(str(e))
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            raise

    def send_notification_now(
        self,
        notification_create: NotificationCreate
    ) -> Notification:
        """
        Create and immediately send a notification.

        Args:
            notification_create: Notification data

        Returns:
            Created and sent notification
        """
        notification = self.create_notification(notification_create)

        try:
            return self.send_notification(notification.id)
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {e}")
            return notification

    # =============================================================================
    # Retry Logic
    # =============================================================================

    def retry_failed_notifications(
        self,
        max_retries: int = 3
    ) -> int:
        """
        Retry all failed notifications that haven't exceeded max retries.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            Number of notifications retried
        """
        failed_notifications = self.db.query(Notification).filter(
            and_(
                or_(
                    Notification.status == NotificationStatus.FAILED,
                    Notification.status == NotificationStatus.RETRYING
                ),
                Notification.retry_count < str(max_retries)
            )
        ).all()

        count = 0
        for notification in failed_notifications:
            try:
                notification.increment_retry()
                self.db.add(notification)
                self.db.commit()

                self.send_notification(notification.id)
                count += 1
            except Exception as e:
                logger.error(f"Failed to retry notification {notification.id}: {e}")
                continue

        logger.info(f"Retried {count} failed notifications")
        return count

    # =============================================================================
    # Statistics
    # =============================================================================

    def get_notification_statistics(self) -> dict:
        """
        Get statistics about notifications.

        Returns:
            Dictionary with notification statistics
        """
        total_notifications = self.db.query(func.count(Notification.id)).scalar()

        # Count by status
        by_status = {}
        for status in NotificationStatus:
            count = self.db.query(func.count(Notification.id)).filter(
                Notification.status == status
            ).scalar()
            by_status[status.value] = count

        # Count by type
        by_type = {}
        for ntype in NotificationType:
            count = self.db.query(func.count(Notification.id)).filter(
                Notification.type == ntype
            ).scalar()
            by_type[ntype.value] = count

        # Count by channel
        by_channel = {}
        for channel in NotificationChannel:
            count = self.db.query(func.count(Notification.id)).filter(
                Notification.channel == channel
            ).scalar()
            by_channel[channel.value] = count

        # Calculate success rate
        sent_count = by_status.get("SENT", 0)
        success_rate = (sent_count / total_notifications * 100) if total_notifications > 0 else 0.0

        return {
            "total_notifications": total_notifications,
            "by_status": by_status,
            "by_type": by_type,
            "by_channel": by_channel,
            "success_rate": round(success_rate, 2),
            "failed_count": by_status.get("FAILED", 0)
        }
