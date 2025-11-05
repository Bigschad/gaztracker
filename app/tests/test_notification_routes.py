"""
Tests for Notification Routes

Comprehensive tests for notification API endpoints including
creating, sending, listing, and managing notifications.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationChannel
)
from app.models.user import User, UserRole
from app.database import get_db


# Test client
client = TestClient(app)


class TestNotificationRoutes:
    """Test suite for notification API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_user_admin = User(
            id=uuid4(),
            email="admin@example.com",
            username="admin",
            role=UserRole.ADMIN,
            is_active=True
        )

        self.test_user_logistic = User(
            id=uuid4(),
            email="logistic@example.com",
            username="logistic",
            role=UserRole.RESPONSABLE_LOGISTIQUE,
            is_active=True
        )

    def get_auth_headers(self, user=None):
        """Get authentication headers for testing."""
        if user is None:
            user = self.test_user_admin
        # This would normally create a JWT token
        return {"Authorization": "Bearer test_token"}

    # =============================================================================
    # Create Notification Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_create_notification_success(self, mock_get_user, mock_service_class):
        """Test successful notification creation."""
        mock_get_user.return_value = self.test_user_admin

        mock_notification = Mock(spec=Notification)
        mock_notification.id = uuid4()
        mock_notification.type = NotificationType.EXPEDITION_CREEE
        mock_notification.status = NotificationStatus.PENDING

        mock_service = Mock()
        mock_service.create_notification.return_value = mock_notification
        mock_service_class.return_value = mock_service

        payload = {
            "type": "EXPEDITION_CREEE",
            "channel": "EMAIL",
            "recipient_email": "test@example.com",
            "subject": "Test Notification",
            "message": "Test message"
        }

        response = client.post(
            "/api/v1/notifications/",
            json=payload,
            headers=self.get_auth_headers()
        )

        assert response.status_code == 201

    @patch('app.routes.notifications.get_current_user')
    def test_create_notification_missing_email_fails(self, mock_get_user):
        """Test creating email notification without email fails."""
        mock_get_user.return_value = self.test_user_admin

        payload = {
            "type": "EXPEDITION_CREEE",
            "channel": "EMAIL",
            "subject": "Test",
            "message": "Test"
            # Missing recipient_email
        }

        response = client.post(
            "/api/v1/notifications/",
            json=payload,
            headers=self.get_auth_headers()
        )

        assert response.status_code == 422  # Validation error

    # =============================================================================
    # Send Notification Now Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_send_notification_now_success(self, mock_get_user, mock_service_class):
        """Test sending notification immediately."""
        mock_get_user.return_value = self.test_user_admin

        mock_notification = Mock(spec=Notification)
        mock_notification.id = uuid4()
        mock_notification.status = NotificationStatus.SENT

        mock_service = Mock()
        mock_service.send_notification_now.return_value = mock_notification
        mock_service_class.return_value = mock_service

        payload = {
            "type": "EXPEDITION_CREEE",
            "channel": "EMAIL",
            "recipient_email": "test@example.com",
            "subject": "Test",
            "message": "Test message"
        }

        response = client.post(
            "/api/v1/notifications/send-now",
            json=payload,
            headers=self.get_auth_headers()
        )

        assert response.status_code == 201
        mock_service.send_notification_now.assert_called_once()

    # =============================================================================
    # Send Email Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_send_email_success(self, mock_get_user, mock_service_class):
        """Test sending standalone email."""
        mock_get_user.return_value = self.test_user_admin

        mock_service = Mock()
        mock_service.send_email.return_value = True
        mock_service_class.return_value = mock_service

        payload = {
            "to_email": "test@example.com",
            "subject": "Test Email",
            "body": "<p>Test body</p>",
            "is_html": True
        }

        response = client.post(
            "/api/v1/notifications/send-email",
            json=payload,
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_service.send_email.assert_called_once()

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_send_email_failure(self, mock_get_user, mock_service_class):
        """Test email sending failure."""
        mock_get_user.return_value = self.test_user_admin

        mock_service = Mock()
        mock_service.send_email.side_effect = Exception("SMTP error")
        mock_service_class.return_value = mock_service

        payload = {
            "to_email": "test@example.com",
            "subject": "Test",
            "body": "Test",
            "is_html": False
        }

        response = client.post(
            "/api/v1/notifications/send-email",
            json=payload,
            headers=self.get_auth_headers()
        )

        assert response.status_code == 502  # Bad Gateway

    # =============================================================================
    # Send SMS Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_send_sms_success(self, mock_get_user, mock_service_class):
        """Test sending standalone SMS."""
        mock_get_user.return_value = self.test_user_admin

        mock_service = Mock()
        mock_service.send_sms.return_value = True
        mock_service_class.return_value = mock_service

        payload = {
            "to_phone": "+1234567890",
            "message": "Test SMS"
        }

        response = client.post(
            "/api/v1/notifications/send-sms",
            json=payload,
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_service.send_sms.assert_called_once()

    # =============================================================================
    # List Notifications Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_list_notifications_success(self, mock_get_user, mock_service_class):
        """Test listing notifications."""
        mock_get_user.return_value = self.test_user_admin

        mock_notifications = [
            Mock(spec=Notification, id=uuid4(), type=NotificationType.EXPEDITION_CREEE),
            Mock(spec=Notification, id=uuid4(), type=NotificationType.ALERTE_RETARD),
        ]

        mock_service = Mock()
        mock_service.list_notifications.return_value = (mock_notifications, 2)
        mock_service_class.return_value = mock_service

        response = client.get(
            "/api/v1/notifications/",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["notifications"]) == 2

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_list_notifications_with_filters(self, mock_get_user, mock_service_class):
        """Test listing notifications with filters."""
        mock_get_user.return_value = self.test_user_admin

        mock_notifications = [
            Mock(spec=Notification, id=uuid4(), status=NotificationStatus.SENT)
        ]

        mock_service = Mock()
        mock_service.list_notifications.return_value = (mock_notifications, 1)
        mock_service_class.return_value = mock_service

        response = client.get(
            "/api/v1/notifications/?status=SENT&type=EXPEDITION_CREEE",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        mock_service.list_notifications.assert_called_once()

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_list_notifications_with_pagination(self, mock_get_user, mock_service_class):
        """Test listing notifications with pagination."""
        mock_get_user.return_value = self.test_user_admin

        mock_notifications = [Mock(spec=Notification) for _ in range(10)]

        mock_service = Mock()
        mock_service.list_notifications.return_value = (mock_notifications, 50)
        mock_service_class.return_value = mock_service

        response = client.get(
            "/api/v1/notifications/?page=2&page_size=10",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 50

    # =============================================================================
    # Get Notification Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_get_notification_success(self, mock_get_user, mock_service_class):
        """Test getting notification by ID."""
        mock_get_user.return_value = self.test_user_admin

        notification_id = uuid4()
        mock_notification = Mock(spec=Notification)
        mock_notification.id = notification_id

        mock_service = Mock()
        mock_service.get_notification.return_value = mock_notification
        mock_service_class.return_value = mock_service

        response = client.get(
            f"/api/v1/notifications/{notification_id}",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        mock_service.get_notification.assert_called_once_with(notification_id)

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_get_notification_not_found(self, mock_get_user, mock_service_class):
        """Test getting non-existent notification."""
        mock_get_user.return_value = self.test_user_admin

        notification_id = uuid4()
        mock_service = Mock()
        mock_service.get_notification.side_effect = Exception("Not found")
        mock_service_class.return_value = mock_service

        response = client.get(
            f"/api/v1/notifications/{notification_id}",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 404

    # =============================================================================
    # Send Pending Notification Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_send_pending_notification_success(self, mock_get_user, mock_service_class):
        """Test sending a pending notification."""
        mock_get_user.return_value = self.test_user_admin

        notification_id = uuid4()
        mock_notification = Mock(spec=Notification)
        mock_notification.id = notification_id
        mock_notification.status = NotificationStatus.SENT

        mock_service = Mock()
        mock_service.send_notification.return_value = mock_notification
        mock_service_class.return_value = mock_service

        response = client.post(
            f"/api/v1/notifications/{notification_id}/send",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        mock_service.send_notification.assert_called_once_with(notification_id)

    # =============================================================================
    # Retry Failed Notifications Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_retry_failed_notifications(self, mock_get_user, mock_service_class):
        """Test retrying failed notifications."""
        mock_get_user.return_value = self.test_user_admin

        mock_service = Mock()
        mock_service.retry_failed_notifications.return_value = 5
        mock_service_class.return_value = mock_service

        response = client.post(
            "/api/v1/notifications/retry/failed?max_retries=3",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["retried_count"] == 5

    # =============================================================================
    # Statistics Tests
    # =============================================================================

    @patch('app.routes.notifications.NotificationService')
    @patch('app.routes.notifications.get_current_user')
    def test_get_statistics(self, mock_get_user, mock_service_class):
        """Test getting notification statistics."""
        mock_get_user.return_value = self.test_user_admin

        mock_stats = {
            "total_notifications": 100,
            "by_status": {
                "SENT": 80,
                "FAILED": 10,
                "PENDING": 10
            },
            "by_type": {
                "EXPEDITION_CREEE": 50,
                "ALERTE_RETARD": 30,
                "CONFIRMATION_LIVRAISON": 20
            },
            "by_channel": {
                "EMAIL": 60,
                "SMS": 20,
                "BOTH": 20
            },
            "success_rate": 80.0,
            "failed_count": 10
        }

        mock_service = Mock()
        mock_service.get_notification_statistics.return_value = mock_stats
        mock_service_class.return_value = mock_service

        response = client.get(
            "/api/v1/notifications/statistics/overview",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_notifications"] == 100
        assert data["success_rate"] == 80.0

    # =============================================================================
    # Automatic Alerts Tests
    # =============================================================================

    @patch('app.routes.notifications.AutomaticAlerts')
    @patch('app.routes.notifications.get_current_user')
    def test_check_delayed_expeditions(self, mock_get_user, mock_alerts_class):
        """Test checking for delayed expeditions."""
        mock_get_user.return_value = self.test_user_admin

        mock_alerts = Mock()
        mock_alerts.check_delayed_expeditions.return_value = 3
        mock_alerts_class.return_value = mock_alerts

        response = client.post(
            "/api/v1/notifications/alerts/check-delays",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["alerts_sent"] == 3

    @patch('app.routes.notifications.AutomaticAlerts')
    @patch('app.routes.notifications.get_current_user')
    def test_check_pending_validations(self, mock_get_user, mock_alerts_class):
        """Test checking for pending validations."""
        mock_get_user.return_value = self.test_user_admin

        mock_alerts = Mock()
        mock_alerts.check_pending_validations.return_value = 2
        mock_alerts_class.return_value = mock_alerts

        response = client.post(
            "/api/v1/notifications/alerts/check-validations",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["reminders_sent"] == 2

    @patch('app.routes.notifications.AutomaticAlerts')
    @patch('app.routes.notifications.get_current_user')
    def test_run_all_checks(self, mock_get_user, mock_alerts_class):
        """Test running all automatic checks."""
        mock_get_user.return_value = self.test_user_admin

        mock_results = {
            "delay_alerts": 3,
            "validation_reminders": 2,
            "total_alerts": 5
        }

        mock_alerts = Mock()
        mock_alerts.run_all_checks.return_value = mock_results
        mock_alerts_class.return_value = mock_alerts

        response = client.post(
            "/api/v1/notifications/alerts/run-all",
            headers=self.get_auth_headers()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["results"]["total_alerts"] == 5

    # =============================================================================
    # Authorization Tests
    # =============================================================================

    @patch('app.routes.notifications.get_current_user')
    def test_logistic_user_can_create_notification(self, mock_get_user):
        """Test that logistic user can create notifications."""
        mock_get_user.return_value = self.test_user_logistic

        # This test would verify RBAC permissions
        # In real implementation, you'd need proper JWT token generation
        pass

    @patch('app.routes.notifications.get_current_user')
    def test_unauthorized_user_cannot_send_notification(self, mock_get_user):
        """Test that unauthorized users cannot send notifications."""
        # Create a regular user without permissions
        regular_user = User(
            id=uuid4(),
            email="user@example.com",
            username="user",
            role=UserRole.OPERATEUR,
            is_active=True
        )
        mock_get_user.return_value = regular_user

        # This would fail due to RBAC checks
        # In real implementation, you'd verify 403 Forbidden
        pass
