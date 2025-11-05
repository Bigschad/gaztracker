"""
Tests for Notification Service

Comprehensive tests for notification creation, sending (email/SMS),
retry logic, and statistics.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.notification_service import NotificationService
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationChannel
)
from app.schemas.notification import NotificationCreate
from app.utils.exceptions import (
    ValidationException,
    ExternalServiceException,
    ResourceNotFoundException
)


class TestNotificationService:
    """Test suite for NotificationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = NotificationService(self.db)

    # =============================================================================
    # Create Notification Tests
    # =============================================================================

    def test_create_notification_email_success(self):
        """Test successful creation of email notification."""
        notification_data = NotificationCreate(
            type=NotificationType.EXPEDITION_CREEE,
            channel=NotificationChannel.EMAIL,
            recipient_email="test@example.com",
            subject="Test Notification",
            message="Test message"
        )

        # Mock database operations
        self.db.add = Mock()
        self.db.commit = Mock()
        self.db.refresh = Mock()

        result = self.service.create_notification(notification_data)

        assert self.db.add.called
        assert self.db.commit.called
        assert self.db.refresh.called

    def test_create_notification_sms_success(self):
        """Test successful creation of SMS notification."""
        notification_data = NotificationCreate(
            type=NotificationType.ALERTE_RETARD,
            channel=NotificationChannel.SMS,
            recipient_phone="+1234567890",
            message="Test SMS"
        )

        self.db.add = Mock()
        self.db.commit = Mock()
        self.db.refresh = Mock()

        result = self.service.create_notification(notification_data)

        assert self.db.add.called
        assert self.db.commit.called

    def test_create_notification_both_channels(self):
        """Test creation of notification for both email and SMS."""
        notification_data = NotificationCreate(
            type=NotificationType.EXPEDITION_DEPART,
            channel=NotificationChannel.BOTH,
            recipient_email="test@example.com",
            recipient_phone="+1234567890",
            subject="Test",
            message="Test message"
        )

        self.db.add = Mock()
        self.db.commit = Mock()
        self.db.refresh = Mock()

        result = self.service.create_notification(notification_data)

        assert self.db.add.called

    def test_create_notification_missing_email_fails(self):
        """Test that creating email notification without email fails."""
        notification_data = NotificationCreate(
            type=NotificationType.EXPEDITION_CREEE,
            channel=NotificationChannel.EMAIL,
            recipient_email=None,
            message="Test"
        )

        with pytest.raises(ValidationException) as exc_info:
            self.service.create_notification(notification_data)

        assert "Email address required" in str(exc_info.value)

    def test_create_notification_missing_phone_fails(self):
        """Test that creating SMS notification without phone fails."""
        notification_data = NotificationCreate(
            type=NotificationType.ALERTE_RETARD,
            channel=NotificationChannel.SMS,
            recipient_phone=None,
            message="Test"
        )

        with pytest.raises(ValidationException) as exc_info:
            self.service.create_notification(notification_data)

        assert "Phone number required" in str(exc_info.value)

    # =============================================================================
    # Send Email Tests
    # =============================================================================

    @patch('app.services.notification_service.smtplib.SMTP_SSL')
    @patch('app.services.notification_service.settings')
    def test_send_email_success(self, mock_settings, mock_smtp):
        """Test successful email sending."""
        # Configure mock settings
        mock_settings.ENABLE_EMAIL_NOTIFICATIONS = True
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 465
        mock_settings.SMTP_SSL = True
        mock_settings.SMTP_FROM_NAME = "GazTracker"
        mock_settings.SMTP_FROM_EMAIL = "noreply@gaztracker.com"

        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = self.service.send_email(
            to_email="test@example.com",
            subject="Test Email",
            body="<p>Test body</p>",
            is_html=True
        )

        assert result is True
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('app.services.notification_service.settings')
    def test_send_email_disabled(self, mock_settings):
        """Test email sending when disabled."""
        mock_settings.ENABLE_EMAIL_NOTIFICATIONS = False

        result = self.service.send_email(
            to_email="test@example.com",
            subject="Test",
            body="Test"
        )

        assert result is False

    @patch('app.services.notification_service.smtplib.SMTP_SSL')
    @patch('app.services.notification_service.settings')
    def test_send_email_smtp_error(self, mock_settings, mock_smtp):
        """Test email sending with SMTP error."""
        mock_settings.ENABLE_EMAIL_NOTIFICATIONS = True
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 465
        mock_settings.SMTP_SSL = True

        # Mock SMTP error
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception("SMTP error")
        mock_smtp.return_value = mock_server

        with pytest.raises(ExternalServiceException):
            self.service.send_email(
                to_email="test@example.com",
                subject="Test",
                body="Test"
            )

    # =============================================================================
    # Send SMS Tests
    # =============================================================================

    @patch('app.services.notification_service.settings')
    @patch('app.services.notification_service.TWILIO_AVAILABLE', True)
    def test_send_sms_success(self, mock_settings):
        """Test successful SMS sending."""
        mock_settings.ENABLE_SMS_NOTIFICATIONS = True
        mock_settings.TWILIO_ACCOUNT_SID = "test_sid"
        mock_settings.TWILIO_AUTH_TOKEN = "test_token"
        mock_settings.TWILIO_PHONE_NUMBER = "+1234567890"

        # Mock Twilio client
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.sid = "SM123456"
        mock_client.messages.create.return_value = mock_message

        self.service._twilio_client = mock_client

        result = self.service.send_sms(
            to_phone="+0987654321",
            message="Test SMS"
        )

        assert result is True
        mock_client.messages.create.assert_called_once()

    @patch('app.services.notification_service.settings')
    def test_send_sms_disabled(self, mock_settings):
        """Test SMS sending when disabled."""
        mock_settings.ENABLE_SMS_NOTIFICATIONS = False

        result = self.service.send_sms(
            to_phone="+1234567890",
            message="Test"
        )

        assert result is False

    @patch('app.services.notification_service.TWILIO_AVAILABLE', False)
    def test_send_sms_twilio_unavailable(self):
        """Test SMS sending when Twilio is unavailable."""
        result = self.service.send_sms(
            to_phone="+1234567890",
            message="Test"
        )

        assert result is False

    # =============================================================================
    # Get Notification Tests
    # =============================================================================

    def test_get_notification_success(self):
        """Test getting notification by ID."""
        notification_id = uuid4()
        mock_notification = Mock(spec=Notification)
        mock_notification.id = notification_id

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_notification
        self.db.query.return_value = mock_query

        result = self.service.get_notification(notification_id)

        assert result == mock_notification
        self.db.query.assert_called_once_with(Notification)

    def test_get_notification_not_found(self):
        """Test getting non-existent notification."""
        notification_id = uuid4()

        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        self.db.query.return_value = mock_query

        with pytest.raises(ResourceNotFoundException):
            self.service.get_notification(notification_id)

    # =============================================================================
    # List Notifications Tests
    # =============================================================================

    def test_list_notifications_no_filters(self):
        """Test listing all notifications without filters."""
        mock_notifications = [Mock(spec=Notification) for _ in range(5)]

        mock_query = Mock()
        mock_query.count.return_value = 5
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_notifications
        self.db.query.return_value = mock_query

        notifications, total = self.service.list_notifications()

        assert len(notifications) == 5
        assert total == 5

    def test_list_notifications_with_status_filter(self):
        """Test listing notifications with status filter."""
        mock_notifications = [Mock(spec=Notification) for _ in range(3)]

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_notifications
        self.db.query.return_value = mock_query

        notifications, total = self.service.list_notifications(
            status=NotificationStatus.SENT
        )

        assert len(notifications) == 3
        assert total == 3

    def test_list_notifications_with_pagination(self):
        """Test listing notifications with pagination."""
        mock_notifications = [Mock(spec=Notification) for _ in range(10)]

        mock_query = Mock()
        mock_query.count.return_value = 50
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_notifications
        self.db.query.return_value = mock_query

        notifications, total = self.service.list_notifications(
            page=2,
            page_size=10
        )

        assert len(notifications) == 10
        assert total == 50

    # =============================================================================
    # Send Notification Tests
    # =============================================================================

    @patch.object(NotificationService, 'send_email')
    @patch.object(NotificationService, 'get_notification')
    def test_send_notification_email_success(self, mock_get, mock_send_email):
        """Test sending an email notification."""
        notification_id = uuid4()
        mock_notification = Mock(spec=Notification)
        mock_notification.id = notification_id
        mock_notification.status = NotificationStatus.PENDING
        mock_notification.channel = NotificationChannel.EMAIL
        mock_notification.recipient_email = "test@example.com"
        mock_notification.subject = "Test"
        mock_notification.message = "Test message"

        mock_get.return_value = mock_notification
        mock_send_email.return_value = True

        self.db.add = Mock()
        self.db.commit = Mock()
        self.db.refresh = Mock()

        result = self.service.send_notification(notification_id)

        mock_send_email.assert_called_once()
        mock_notification.mark_as_sent.assert_called_once()

    @patch.object(NotificationService, 'get_notification')
    def test_send_notification_already_sent(self, mock_get):
        """Test sending a notification that's already sent."""
        notification_id = uuid4()
        mock_notification = Mock(spec=Notification)
        mock_notification.status = NotificationStatus.SENT

        mock_get.return_value = mock_notification

        result = self.service.send_notification(notification_id)

        assert result == mock_notification

    # =============================================================================
    # Retry Logic Tests
    # =============================================================================

    @patch.object(NotificationService, 'send_notification')
    def test_retry_failed_notifications(self, mock_send):
        """Test retrying failed notifications."""
        failed_notifications = [
            Mock(spec=Notification, id=uuid4(), retry_count="0"),
            Mock(spec=Notification, id=uuid4(), retry_count="1"),
        ]

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = failed_notifications
        self.db.query.return_value = mock_query

        self.db.add = Mock()
        self.db.commit = Mock()
        mock_send.return_value = Mock()

        count = self.service.retry_failed_notifications(max_retries=3)

        assert count == 2
        assert mock_send.call_count == 2

    # =============================================================================
    # Statistics Tests
    # =============================================================================

    def test_get_notification_statistics(self):
        """Test getting notification statistics."""
        # Mock total count
        self.db.query.return_value.scalar.return_value = 100

        # Mock counts by status
        def mock_count_query(*args):
            mock_query = Mock()
            mock_query.filter.return_value.scalar.return_value = 10
            return mock_query

        self.db.query.side_effect = mock_count_query

        stats = self.service.get_notification_statistics()

        assert "total_notifications" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        assert "by_channel" in stats
        assert "success_rate" in stats
        assert "failed_count" in stats


class TestNotificationModel:
    """Test Notification model methods."""

    def test_mark_as_sent(self):
        """Test marking notification as sent."""
        notification = Notification(
            type=NotificationType.EXPEDITION_CREEE,
            channel=NotificationChannel.EMAIL,
            status=NotificationStatus.PENDING,
            recipient_email="test@example.com",
            message="Test"
        )

        notification.mark_as_sent()

        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None

    def test_mark_as_failed(self):
        """Test marking notification as failed."""
        notification = Notification(
            type=NotificationType.EXPEDITION_CREEE,
            channel=NotificationChannel.EMAIL,
            status=NotificationStatus.PENDING,
            recipient_email="test@example.com",
            message="Test"
        )

        notification.mark_as_failed("Test error")

        assert notification.status == NotificationStatus.FAILED
        assert notification.error_message == "Test error"

    def test_increment_retry(self):
        """Test incrementing retry count."""
        notification = Notification(
            type=NotificationType.EXPEDITION_CREEE,
            channel=NotificationChannel.EMAIL,
            status=NotificationStatus.FAILED,
            recipient_email="test@example.com",
            message="Test",
            retry_count="0"
        )

        notification.increment_retry()

        assert notification.retry_count == "1"
        assert notification.status == NotificationStatus.RETRYING
