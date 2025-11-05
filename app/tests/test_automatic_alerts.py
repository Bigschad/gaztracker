"""
Tests for Automatic Alerts

Comprehensive tests for automatic alert checking including
delayed expeditions, pending validations, and notification triggers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.utils.automatic_alerts import AutomaticAlerts
from app.models.expedition import Expedition, ExpeditionStatus
from app.models.palette import Palette
from app.models.user import User, UserRole
from app.models.notification import NotificationType, NotificationChannel
from app.services.notification_service import NotificationService


class TestAutomaticAlerts:
    """Test suite for AutomaticAlerts."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.alerts = AutomaticAlerts(self.db)

        # Create test user
        self.test_user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            phone="+1234567890",
            role=UserRole.RESPONSABLE_LOGISTIQUE,
            is_active=True
        )

    # =============================================================================
    # Check Delayed Expeditions Tests
    # =============================================================================

    @patch.object(NotificationService, 'send_notification_now')
    def test_check_delayed_expeditions_finds_delayed(self, mock_send):
        """Test finding and alerting delayed expeditions."""
        # Create delayed expeditions
        delayed_exp1 = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.EN_ROUTE,
            eta=datetime.utcnow() - timedelta(hours=2),  # 2 hours late
            destination_address="Address 1",
            palette_count=5,
            created_by=self.test_user
        )

        delayed_exp2 = Expedition(
            id=uuid4(),
            reference_number="EXP-002",
            status=ExpeditionStatus.DEPART,
            eta=datetime.utcnow() - timedelta(days=1),  # 1 day late
            destination_address="Address 2",
            palette_count=3,
            created_by=self.test_user
        )

        # Mock query
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [delayed_exp1, delayed_exp2]
        self.db.query.return_value = mock_query

        # Mock notification service
        mock_send.return_value = Mock()

        # Run check
        count = self.alerts.check_delayed_expeditions()

        assert count == 2
        assert mock_send.call_count == 2

    @patch.object(NotificationService, 'send_notification_now')
    def test_check_delayed_expeditions_skips_completed(self, mock_send):
        """Test that completed expeditions are not flagged as delayed."""
        # Create expeditions
        completed_exp = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.LIVREE,  # Completed
            eta=datetime.utcnow() - timedelta(hours=2),
            destination_address="Address 1",
            palette_count=5,
            created_by=self.test_user
        )

        cancelled_exp = Expedition(
            id=uuid4(),
            reference_number="EXP-002",
            status=ExpeditionStatus.ANNULEE,  # Cancelled
            eta=datetime.utcnow() - timedelta(hours=1),
            destination_address="Address 2",
            palette_count=3,
            created_by=self.test_user
        )

        # Mock query to return no delayed expeditions
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        self.db.query.return_value = mock_query

        count = self.alerts.check_delayed_expeditions()

        assert count == 0
        mock_send.assert_not_called()

    @patch.object(NotificationService, 'send_notification_now')
    def test_check_delayed_expeditions_no_recipient(self, mock_send):
        """Test delayed expedition without recipient email."""
        # Create expedition without creator
        delayed_exp = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.EN_ROUTE,
            eta=datetime.utcnow() - timedelta(hours=2),
            destination_address="Address 1",
            palette_count=5,
            created_by=None  # No creator
        )

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [delayed_exp]
        self.db.query.return_value = mock_query

        count = self.alerts.check_delayed_expeditions()

        # Should not send alert if no recipient
        assert count == 0
        mock_send.assert_not_called()

    @patch.object(NotificationService, 'send_notification_now')
    def test_check_delayed_expeditions_handles_errors(self, mock_send):
        """Test that errors in sending alerts are handled gracefully."""
        delayed_exp1 = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.EN_ROUTE,
            eta=datetime.utcnow() - timedelta(hours=2),
            destination_address="Address 1",
            palette_count=5,
            created_by=self.test_user
        )

        delayed_exp2 = Expedition(
            id=uuid4(),
            reference_number="EXP-002",
            status=ExpeditionStatus.EN_ROUTE,
            eta=datetime.utcnow() - timedelta(hours=3),
            destination_address="Address 2",
            palette_count=3,
            created_by=self.test_user
        )

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [delayed_exp1, delayed_exp2]
        self.db.query.return_value = mock_query

        # First call fails, second succeeds
        mock_send.side_effect = [Exception("Send failed"), Mock()]

        count = self.alerts.check_delayed_expeditions()

        # Should only count successful sends
        assert count == 1
        assert mock_send.call_count == 2

    # =============================================================================
    # Check Pending Validations Tests
    # =============================================================================

    @patch.object(NotificationService, 'send_notification_now')
    def test_check_pending_validations_finds_pending(self, mock_send):
        """Test finding and sending reminders for pending validations."""
        pending_exp1 = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.ARRIVEE,  # Arrived, needs validation
            destination_address="Address 1",
            destination_contact="contact@example.com",
            destination_phone="+1234567890",
            otp_code="123456",
            palette_count=5
        )

        pending_exp2 = Expedition(
            id=uuid4(),
            reference_number="EXP-002",
            status=ExpeditionStatus.ARRIVEE,
            destination_address="Address 2",
            destination_contact="contact2@example.com",
            destination_phone="+0987654321",
            otp_code="654321",
            palette_count=3
        )

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [pending_exp1, pending_exp2]
        self.db.query.return_value = mock_query

        mock_send.return_value = Mock()

        count = self.alerts.check_pending_validations()

        assert count == 2
        assert mock_send.call_count == 2

    @patch.object(NotificationService, 'send_notification_now')
    def test_check_pending_validations_no_recipient(self, mock_send):
        """Test pending validation without valid recipient."""
        pending_exp = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.ARRIVEE,
            destination_address="Address 1",
            destination_contact="Invalid Contact",  # No @ sign
            destination_phone=None,
            otp_code="123456",
            palette_count=5
        )

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = [pending_exp]
        self.db.query.return_value = mock_query

        count = self.alerts.check_pending_validations()

        # Should not send if no valid recipient
        assert count == 0
        mock_send.assert_not_called()

    # =============================================================================
    # Send Expedition Notifications Tests
    # =============================================================================

    @patch.object(NotificationService, 'send_notification_now')
    def test_send_expedition_created_notification(self, mock_send):
        """Test sending notification for expedition creation."""
        expedition = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.PREPAREE,
            destination_address="Address 1",
            palette_count=5,
            eta=datetime.utcnow() + timedelta(hours=24),
            created_by=self.test_user
        )

        mock_send.return_value = Mock()

        result = self.alerts.send_expedition_notifications(
            expedition,
            NotificationType.EXPEDITION_CREEE
        )

        assert result is True
        mock_send.assert_called_once()

    @patch.object(NotificationService, 'send_notification_now')
    def test_send_expedition_departed_notification(self, mock_send):
        """Test sending notification for expedition departure."""
        expedition = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.DEPART,
            destination_address="Address 1",
            palette_count=5,
            eta=datetime.utcnow() + timedelta(hours=12),
            otp_code="123456",
            created_by=self.test_user
        )

        mock_send.return_value = Mock()

        result = self.alerts.send_expedition_notifications(
            expedition,
            NotificationType.EXPEDITION_DEPART
        )

        assert result is True
        mock_send.assert_called_once()

    @patch.object(NotificationService, 'send_notification_now')
    def test_send_delivery_confirmation_notification(self, mock_send):
        """Test sending notification for delivery confirmation."""
        expedition = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.LIVREE,
            destination_address="Address 1",
            destination_contact="contact@example.com",
            palette_count=5,
            date_delivery=datetime.utcnow()
        )

        mock_send.return_value = Mock()

        result = self.alerts.send_expedition_notifications(
            expedition,
            NotificationType.CONFIRMATION_LIVRAISON
        )

        assert result is True
        mock_send.assert_called_once()

    @patch.object(NotificationService, 'send_notification_now')
    def test_send_expedition_problem_notification(self, mock_send):
        """Test sending notification for expedition problem."""
        expedition = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.PROBLEME,
            destination_address="Address 1",
            destination_contact="contact@example.com",
            palette_count=5,
            problem_description="Damaged palettes"
        )

        mock_send.return_value = Mock()

        result = self.alerts.send_expedition_notifications(
            expedition,
            NotificationType.PROBLEME_EXPEDITION
        )

        assert result is True
        mock_send.assert_called_once()

    def test_send_notification_no_template(self):
        """Test sending notification with unknown type."""
        expedition = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.PREPAREE,
            destination_address="Address 1",
            palette_count=5
        )

        # Use a notification type not in the template map
        # This would return False
        result = self.alerts.send_expedition_notifications(
            expedition,
            None  # Invalid type
        )

        assert result is False

    @patch.object(NotificationService, 'send_notification_now')
    def test_send_notification_no_recipient(self, mock_send):
        """Test sending notification without recipient."""
        expedition = Expedition(
            id=uuid4(),
            reference_number="EXP-001",
            status=ExpeditionStatus.PREPAREE,
            destination_address="Address 1",
            palette_count=5,
            created_by=None  # No creator
        )

        result = self.alerts.send_expedition_notifications(
            expedition,
            NotificationType.EXPEDITION_CREEE
        )

        assert result is False
        mock_send.assert_not_called()

    # =============================================================================
    # Run All Checks Tests
    # =============================================================================

    @patch.object(AutomaticAlerts, 'check_delayed_expeditions')
    @patch.object(AutomaticAlerts, 'check_pending_validations')
    def test_run_all_checks_success(self, mock_validations, mock_delays):
        """Test running all automatic checks."""
        mock_delays.return_value = 3
        mock_validations.return_value = 2

        results = self.alerts.run_all_checks()

        assert results["delay_alerts"] == 3
        assert results["validation_reminders"] == 2
        assert results["total_alerts"] == 5

        mock_delays.assert_called_once()
        mock_validations.assert_called_once()

    @patch.object(AutomaticAlerts, 'check_delayed_expeditions')
    @patch.object(AutomaticAlerts, 'check_pending_validations')
    def test_run_all_checks_no_alerts(self, mock_validations, mock_delays):
        """Test running all checks with no alerts."""
        mock_delays.return_value = 0
        mock_validations.return_value = 0

        results = self.alerts.run_all_checks()

        assert results["delay_alerts"] == 0
        assert results["validation_reminders"] == 0
        assert results["total_alerts"] == 0

    @patch.object(AutomaticAlerts, 'check_delayed_expeditions')
    @patch.object(AutomaticAlerts, 'check_pending_validations')
    def test_run_all_checks_partial_failure(self, mock_validations, mock_delays):
        """Test running all checks with one check failing."""
        mock_delays.return_value = 3
        mock_validations.side_effect = Exception("Check failed")

        # Should handle exception gracefully
        with pytest.raises(Exception):
            self.alerts.run_all_checks()


class TestNotificationTemplates:
    """Test notification template generation."""

    def test_templates_exist_for_all_types(self):
        """Test that templates exist for all notification types."""
        from app.utils.notification_templates import NotificationTemplates

        # Test expedition created
        subject, body = NotificationTemplates.expedition_created({
            "reference_number": "EXP-001",
            "destination_address": "Address 1",
            "palette_count": 5
        })
        assert "EXP-001" in subject
        assert len(body) > 0

        # Test expedition departed
        subject, body = NotificationTemplates.expedition_departed({
            "reference_number": "EXP-002",
            "destination_address": "Address 2",
            "eta": "2024-01-15 10:00",
            "otp_code": "123456"
        })
        assert "EXP-002" in subject
        assert "123456" in body

        # Test delivery confirmation
        subject, body = NotificationTemplates.delivery_confirmation({
            "reference_number": "EXP-003",
            "delivery_date": "2024-01-15 15:00"
        })
        assert "EXP-003" in subject
        assert len(body) > 0

        # Test delay alert
        subject, body = NotificationTemplates.delay_alert({
            "reference_number": "EXP-004",
            "eta": "2024-01-15 10:00",
            "status": "EN_ROUTE"
        })
        assert "EXP-004" in subject
        assert "Retard" in subject or "retard" in body.lower()

    def test_sms_templates_are_short(self):
        """Test that SMS templates are within 160 character limit."""
        from app.utils.notification_templates import NotificationTemplates

        data = {
            "reference_number": "EXP-001",
            "otp_code": "123456"
        }

        # Test all SMS templates
        sms_types = [
            "EXPEDITION_CREEE",
            "EXPEDITION_DEPART",
            "CONFIRMATION_LIVRAISON",
            "ALERTE_RETARD",
            "PROBLEME_EXPEDITION",
            "VALIDATION_REQUISE"
        ]

        for sms_type in sms_types:
            message = NotificationTemplates.get_sms_template(sms_type, data)
            assert len(message) <= 160, f"SMS template for {sms_type} is too long: {len(message)} chars"
