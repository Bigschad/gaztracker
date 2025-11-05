"""
Automatic Alerts

System for automatic alerts based on expeditions delays, RFID anomalies, etc.
This module can be called from background tasks or cron jobs.
"""

import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from app.models.expedition import Expedition, ExpeditionStatus
from app.models.palette import Palette
from app.models.notification import NotificationType, NotificationChannel
from app.models.user import User
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService
from app.utils.notification_templates import NotificationTemplates

logger = logging.getLogger(__name__)


class AutomaticAlerts:
    """System for automatic alerts."""

    def __init__(self, db: Session):
        """
        Initialize automatic alerts system.

        Args:
            db: Database session
        """
        self.db = db
        self.notification_service = NotificationService(db)

    def check_delayed_expeditions(self) -> int:
        """
        Check for delayed expeditions and send alerts.

        Returns:
            Number of alerts sent
        """
        logger.info("Checking for delayed expeditions...")

        # Find expeditions that are delayed
        delayed_expeditions = self.db.query(Expedition).filter(
            Expedition.eta < datetime.utcnow(),
            Expedition.status.notin_([ExpeditionStatus.LIVREE, ExpeditionStatus.ANNULEE]),
            Expedition.eta.isnot(None)
        ).all()

        alerts_sent = 0

        for expedition in delayed_expeditions:
            try:
                # Check if alert already sent (to avoid spam)
                # You could add a flag to the expedition model to track this

                # Prepare notification data
                data = {
                    "reference_number": expedition.reference_number,
                    "eta": expedition.eta.strftime("%Y-%m-%d %H:%M") if expedition.eta else "N/A",
                    "status": expedition.status.value,
                }

                # Generate email template
                subject, html_body = NotificationTemplates.delay_alert(data)
                sms_message = NotificationTemplates.get_sms_template("ALERTE_RETARD", data)

                # Get recipient (creator of expedition or responsible)
                recipient_email = None
                recipient_phone = None

                if expedition.created_by:
                    recipient_email = expedition.created_by.email
                    recipient_phone = expedition.created_by.phone

                if recipient_email:
                    # Create and send notification
                    notification_data = NotificationCreate(
                        type=NotificationType.ALERTE_RETARD,
                        channel=NotificationChannel.EMAIL,
                        recipient_email=recipient_email,
                        subject=subject,
                        message=html_body,
                        expedition_id=expedition.id
                    )

                    self.notification_service.send_notification_now(notification_data)
                    alerts_sent += 1

                    logger.info(f"Delay alert sent for expedition {expedition.reference_number}")

            except Exception as e:
                logger.error(f"Failed to send delay alert for expedition {expedition.id}: {e}")
                continue

        logger.info(f"Sent {alerts_sent} delay alerts")
        return alerts_sent

    def check_pending_validations(self) -> int:
        """
        Check for expeditions requiring validation and send reminders.

        Returns:
            Number of alerts sent
        """
        logger.info("Checking for pending validations...")

        # Find expeditions that arrived but not yet validated
        pending_expeditions = self.db.query(Expedition).filter(
            Expedition.status == ExpeditionStatus.ARRIVEE
        ).all()

        alerts_sent = 0

        for expedition in pending_expeditions:
            try:
                # Prepare notification data
                data = {
                    "reference_number": expedition.reference_number,
                    "otp_code": expedition.otp_code or "",
                }

                # Generate templates
                subject, html_body = NotificationTemplates.validation_required(data)
                sms_message = NotificationTemplates.get_sms_template("VALIDATION_REQUISE", data)

                # Get recipient (destination contact or validated_by user)
                recipient_email = expedition.destination_contact if "@" in (expedition.destination_contact or "") else None
                recipient_phone = expedition.destination_phone

                if recipient_email:
                    notification_data = NotificationCreate(
                        type=NotificationType.VALIDATION_REQUISE,
                        channel=NotificationChannel.EMAIL,
                        recipient_email=recipient_email,
                        subject=subject,
                        message=html_body,
                        expedition_id=expedition.id
                    )

                    self.notification_service.send_notification_now(notification_data)
                    alerts_sent += 1

                    logger.info(f"Validation reminder sent for expedition {expedition.reference_number}")

            except Exception as e:
                logger.error(f"Failed to send validation reminder for expedition {expedition.id}: {e}")
                continue

        logger.info(f"Sent {alerts_sent} validation reminders")
        return alerts_sent

    def send_expedition_notifications(
        self,
        expedition: Expedition,
        notification_type: NotificationType
    ) -> bool:
        """
        Send notifications for expedition events.

        Args:
            expedition: Expedition object
            notification_type: Type of notification to send

        Returns:
            True if sent successfully
        """
        try:
            # Prepare expedition data
            data = {
                "reference_number": expedition.reference_number,
                "destination_address": expedition.destination_address,
                "palette_count": expedition.palette_count,
                "eta": expedition.eta.strftime("%Y-%m-%d %H:%M") if expedition.eta else "N/A",
                "otp_code": expedition.otp_code or "",
                "delivery_date": expedition.date_delivery.strftime("%Y-%m-%d %H:%M") if expedition.date_delivery else "N/A",
                "status": expedition.status.value,
                "problem_description": expedition.problem_description or ""
            }

            # Get appropriate template
            template_map = {
                NotificationType.EXPEDITION_CREEE: NotificationTemplates.expedition_created,
                NotificationType.EXPEDITION_DEPART: NotificationTemplates.expedition_departed,
                NotificationType.CONFIRMATION_LIVRAISON: NotificationTemplates.delivery_confirmation,
                NotificationType.ALERTE_RETARD: NotificationTemplates.delay_alert,
                NotificationType.PROBLEME_EXPEDITION: NotificationTemplates.expedition_problem,
                NotificationType.VALIDATION_REQUISE: NotificationTemplates.validation_required,
            }

            template_func = template_map.get(notification_type)
            if not template_func:
                logger.warning(f"No template for notification type {notification_type.value}")
                return False

            subject, html_body = template_func(data)
            sms_message = NotificationTemplates.get_sms_template(notification_type.value, data)

            # Determine recipient
            recipient_email = None
            recipient_phone = None

            if notification_type in [NotificationType.EXPEDITION_CREEE, NotificationType.EXPEDITION_DEPART]:
                # Notify creator
                if expedition.created_by:
                    recipient_email = expedition.created_by.email
                    recipient_phone = expedition.created_by.phone
            else:
                # Notify destination contact
                recipient_email = expedition.destination_contact if "@" in (expedition.destination_contact or "") else None
                recipient_phone = expedition.destination_phone

            if not recipient_email and not recipient_phone:
                logger.warning(f"No recipient for expedition {expedition.id}")
                return False

            # Create notification
            notification_data = NotificationCreate(
                type=notification_type,
                channel=NotificationChannel.EMAIL if recipient_email else NotificationChannel.SMS,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                subject=subject,
                message=html_body if recipient_email else sms_message,
                expedition_id=expedition.id
            )

            self.notification_service.send_notification_now(notification_data)
            logger.info(f"Notification sent for expedition {expedition.reference_number}: {notification_type.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to send expedition notification: {e}")
            return False

    def run_all_checks(self) -> dict:
        """
        Run all automatic checks and send alerts.

        Returns:
            Dictionary with results
        """
        logger.info("Running all automatic checks...")

        results = {
            "delay_alerts": 0,
            "validation_reminders": 0,
            "total_alerts": 0
        }

        # Check delays
        results["delay_alerts"] = self.check_delayed_expeditions()

        # Check pending validations
        results["validation_reminders"] = self.check_pending_validations()

        results["total_alerts"] = results["delay_alerts"] + results["validation_reminders"]

        logger.info(f"Automatic checks complete: {results['total_alerts']} alerts sent")
        return results
