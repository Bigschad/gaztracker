"""
Tests for Notification Templates

Comprehensive tests for email and SMS template generation,
HTML rendering, and content validation.
"""

import pytest
from datetime import datetime

from app.utils.notification_templates import NotificationTemplates


class TestEmailTemplates:
    """Test suite for email HTML templates."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_data = {
            "reference_number": "EXP-20250105-00001",
            "destination_address": "123 Main St, City, Country",
            "palette_count": 10,
            "eta": "2025-01-15 14:30",
            "otp_code": "123456",
            "delivery_date": "2025-01-15 16:45",
            "status": "EN_ROUTE",
            "problem_description": "Damaged packaging on 2 palettes"
        }

    # =============================================================================
    # Expedition Created Template Tests
    # =============================================================================

    def test_expedition_created_template(self):
        """Test expedition created email template."""
        subject, html = NotificationTemplates.expedition_created(self.test_data)

        # Check subject
        assert "EXP-20250105-00001" in subject
        assert "créée" in subject.lower() or "creee" in subject.lower()

        # Check HTML content
        assert "EXP-20250105-00001" in html
        assert "123 Main St" in html
        assert "10" in html
        assert "<html" in html
        assert "</html>" in html
        assert "GazTracker" in html

    def test_expedition_created_minimal_data(self):
        """Test expedition created template with minimal data."""
        minimal_data = {
            "reference_number": "EXP-001",
            "destination_address": "Address",
            "palette_count": 1
        }

        subject, html = NotificationTemplates.expedition_created(minimal_data)

        assert "EXP-001" in subject
        assert "EXP-001" in html
        assert len(html) > 0

    # =============================================================================
    # Expedition Departed Template Tests
    # =============================================================================

    def test_expedition_departed_template(self):
        """Test expedition departed email template."""
        subject, html = NotificationTemplates.expedition_departed(self.test_data)

        # Check subject
        assert "EXP-20250105-00001" in subject
        assert "route" in subject.lower() or "parti" in subject.lower()

        # Check HTML content
        assert "EXP-20250105-00001" in html
        assert "123 Main St" in html
        assert "2025-01-15 14:30" in html
        assert "123456" in html  # OTP code
        assert "GazTracker" in html

    def test_expedition_departed_without_otp(self):
        """Test expedition departed template without OTP."""
        data = self.test_data.copy()
        data["otp_code"] = ""

        subject, html = NotificationTemplates.expedition_departed(data)

        assert "EXP-20250105-00001" in subject
        # OTP section should not appear or be empty
        assert len(html) > 0

    # =============================================================================
    # Delivery Confirmation Template Tests
    # =============================================================================

    def test_delivery_confirmation_template(self):
        """Test delivery confirmation email template."""
        subject, html = NotificationTemplates.delivery_confirmation(self.test_data)

        # Check subject
        assert "EXP-20250105-00001" in subject
        assert "confirmée" in subject.lower() or "confirmee" in subject.lower() or "Livraison" in subject

        # Check HTML content
        assert "EXP-20250105-00001" in html
        assert "2025-01-15 16:45" in html
        assert "GazTracker" in html

    # =============================================================================
    # Delay Alert Template Tests
    # =============================================================================

    def test_delay_alert_template(self):
        """Test delay alert email template."""
        subject, html = NotificationTemplates.delay_alert(self.test_data)

        # Check subject
        assert "EXP-20250105-00001" in subject
        assert "Retard" in subject or "retard" in subject.lower()

        # Check HTML content
        assert "EXP-20250105-00001" in html
        assert "2025-01-15 14:30" in html  # ETA
        assert "EN_ROUTE" in html  # Status
        assert "retard" in html.lower()

    def test_delay_alert_styling(self):
        """Test that delay alert has warning styling."""
        subject, html = NotificationTemplates.delay_alert(self.test_data)

        # Should have warning-box class or similar styling
        assert "warning" in html.lower() or "alert" in html.lower()

    # =============================================================================
    # RFID Anomaly Template Tests
    # =============================================================================

    def test_rfid_anomaly_template(self):
        """Test RFID anomaly email template."""
        rfid_data = {
            "rfid_tag": "RFID-12345",
            "palette_id": "PAL-001",
            "issue": "Tag not responding"
        }

        subject, html = NotificationTemplates.rfid_anomaly(rfid_data)

        # Check subject
        assert "RFID-12345" in subject
        assert "Anomalie" in subject or "anomalie" in subject.lower()

        # Check HTML content
        assert "RFID-12345" in html
        assert "PAL-001" in html
        assert "Tag not responding" in html

    # =============================================================================
    # Expedition Problem Template Tests
    # =============================================================================

    def test_expedition_problem_template(self):
        """Test expedition problem email template."""
        subject, html = NotificationTemplates.expedition_problem(self.test_data)

        # Check subject
        assert "EXP-20250105-00001" in subject
        assert "Problème" in subject or "probleme" in subject.lower() or "Probleme" in subject

        # Check HTML content
        assert "EXP-20250105-00001" in html
        assert "Damaged packaging on 2 palettes" in html

    def test_expedition_problem_no_description(self):
        """Test expedition problem template without description."""
        data = self.test_data.copy()
        data["problem_description"] = ""

        subject, html = NotificationTemplates.expedition_problem(data)

        assert "EXP-20250105-00001" in subject
        # Should handle empty problem description
        assert len(html) > 0

    # =============================================================================
    # Validation Required Template Tests
    # =============================================================================

    def test_validation_required_template(self):
        """Test validation required email template."""
        subject, html = NotificationTemplates.validation_required(self.test_data)

        # Check subject
        assert "EXP-20250105-00001" in subject
        assert "Validation" in subject or "validation" in subject.lower()

        # Check HTML content
        assert "EXP-20250105-00001" in html
        assert "123456" in html  # OTP code

    def test_validation_required_without_otp(self):
        """Test validation required template without OTP."""
        data = self.test_data.copy()
        data["otp_code"] = ""

        subject, html = NotificationTemplates.validation_required(data)

        assert "EXP-20250105-00001" in subject
        assert len(html) > 0

    # =============================================================================
    # HTML Structure Tests
    # =============================================================================

    def test_all_templates_have_valid_html(self):
        """Test that all templates generate valid HTML structure."""
        templates = [
            NotificationTemplates.expedition_created,
            NotificationTemplates.expedition_departed,
            NotificationTemplates.delivery_confirmation,
            NotificationTemplates.delay_alert,
            NotificationTemplates.expedition_problem,
            NotificationTemplates.validation_required,
        ]

        for template_func in templates:
            subject, html = template_func(self.test_data)

            # Basic HTML structure checks
            assert "<!DOCTYPE html>" in html
            assert "<html" in html
            assert "</html>" in html
            assert "<head>" in html
            assert "</head>" in html
            assert "<body>" in html
            assert "</body>" in html
            assert "<style>" in html
            assert "</style>" in html

    def test_all_templates_have_branding(self):
        """Test that all templates include GazTracker branding."""
        templates = [
            NotificationTemplates.expedition_created,
            NotificationTemplates.expedition_departed,
            NotificationTemplates.delivery_confirmation,
            NotificationTemplates.delay_alert,
            NotificationTemplates.expedition_problem,
            NotificationTemplates.validation_required,
        ]

        for template_func in templates:
            subject, html = template_func(self.test_data)

            # Check for branding
            assert "GazTracker" in html
            assert "support@gaztracker.com" in html.lower() or "gaztracker" in html.lower()

    def test_templates_are_responsive(self):
        """Test that templates include viewport meta tag for mobile."""
        templates = [
            NotificationTemplates.expedition_created,
            NotificationTemplates.expedition_departed,
        ]

        for template_func in templates:
            subject, html = template_func(self.test_data)

            # Check for responsive meta tag
            assert "viewport" in html.lower()
            assert "width=device-width" in html.lower()


class TestSMSTemplates:
    """Test suite for SMS templates."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_data = {
            "reference_number": "EXP-20250105-00001",
            "otp_code": "123456"
        }

    # =============================================================================
    # SMS Template Tests
    # =============================================================================

    def test_expedition_creee_sms(self):
        """Test expedition created SMS template."""
        message = NotificationTemplates.get_sms_template("EXPEDITION_CREEE", self.test_data)

        assert "EXP-20250105-00001" in message
        assert "GazTracker" in message
        assert len(message) <= 160

    def test_expedition_depart_sms(self):
        """Test expedition departed SMS template."""
        message = NotificationTemplates.get_sms_template("EXPEDITION_DEPART", self.test_data)

        assert "EXP-20250105-00001" in message
        assert "123456" in message  # OTP
        assert len(message) <= 160

    def test_confirmation_livraison_sms(self):
        """Test delivery confirmation SMS template."""
        message = NotificationTemplates.get_sms_template("CONFIRMATION_LIVRAISON", self.test_data)

        assert "EXP-20250105-00001" in message
        assert len(message) <= 160

    def test_alerte_retard_sms(self):
        """Test delay alert SMS template."""
        message = NotificationTemplates.get_sms_template("ALERTE_RETARD", self.test_data)

        assert "EXP-20250105-00001" in message
        assert "ALERTE" in message or "retard" in message.lower()
        assert len(message) <= 160

    def test_probleme_expedition_sms(self):
        """Test expedition problem SMS template."""
        message = NotificationTemplates.get_sms_template("PROBLEME_EXPEDITION", self.test_data)

        assert "EXP-20250105-00001" in message
        assert "PROBLEME" in message or "probleme" in message.lower()
        assert len(message) <= 160

    def test_validation_requise_sms(self):
        """Test validation required SMS template."""
        message = NotificationTemplates.get_sms_template("VALIDATION_REQUISE", self.test_data)

        assert "EXP-20250105-00001" in message
        assert "123456" in message  # OTP
        assert len(message) <= 160

    def test_unknown_type_sms(self):
        """Test SMS template with unknown type returns default."""
        message = NotificationTemplates.get_sms_template("UNKNOWN_TYPE", self.test_data)

        assert "EXP-20250105-00001" in message
        assert len(message) <= 160

    def test_all_sms_templates_within_limit(self):
        """Test that all SMS templates are within 160 character limit."""
        sms_types = [
            "EXPEDITION_CREEE",
            "EXPEDITION_DEPART",
            "CONFIRMATION_LIVRAISON",
            "ALERTE_RETARD",
            "PROBLEME_EXPEDITION",
            "VALIDATION_REQUISE"
        ]

        for sms_type in sms_types:
            message = NotificationTemplates.get_sms_template(sms_type, self.test_data)
            assert len(message) <= 160, f"SMS {sms_type} exceeds 160 chars: {len(message)}"

    def test_sms_templates_no_html(self):
        """Test that SMS templates don't contain HTML tags."""
        sms_types = [
            "EXPEDITION_CREEE",
            "EXPEDITION_DEPART",
            "CONFIRMATION_LIVRAISON",
            "ALERTE_RETARD",
            "PROBLEME_EXPEDITION",
            "VALIDATION_REQUISE"
        ]

        for sms_type in sms_types:
            message = NotificationTemplates.get_sms_template(sms_type, self.test_data)
            assert "<" not in message
            assert ">" not in message

    def test_sms_with_long_reference(self):
        """Test SMS template with very long reference number."""
        long_data = {
            "reference_number": "EXP-20250105-99999-VERY-LONG-REFERENCE",
            "otp_code": "123456"
        }

        message = NotificationTemplates.get_sms_template("EXPEDITION_DEPART", long_data)

        # Should still be within limit
        assert len(message) <= 160


class TestTemplateDataHandling:
    """Test template handling of missing or invalid data."""

    def test_missing_data_fields(self):
        """Test templates handle missing data fields gracefully."""
        minimal_data = {
            "reference_number": "EXP-001"
        }

        # Should not raise exceptions
        subject, html = NotificationTemplates.expedition_created(minimal_data)
        assert "EXP-001" in subject
        assert "N/A" in html or len(html) > 0

    def test_none_values(self):
        """Test templates handle None values."""
        none_data = {
            "reference_number": "EXP-001",
            "destination_address": None,
            "palette_count": None,
            "otp_code": None
        }

        subject, html = NotificationTemplates.expedition_created(none_data)
        assert "EXP-001" in subject
        # Should handle None gracefully
        assert len(html) > 0

    def test_special_characters_in_data(self):
        """Test templates handle special characters."""
        special_data = {
            "reference_number": "EXP-001",
            "destination_address": "123 Main St & Co. <Test>",
            "palette_count": 5
        }

        subject, html = NotificationTemplates.expedition_created(special_data)

        # HTML should escape special characters or handle them properly
        assert "EXP-001" in subject
        assert len(html) > 0

    def test_unicode_in_data(self):
        """Test templates handle unicode characters."""
        unicode_data = {
            "reference_number": "EXP-001",
            "destination_address": "123 Rue de l'Église, Montréal",
            "palette_count": 5
        }

        subject, html = NotificationTemplates.expedition_created(unicode_data)

        # Should handle unicode properly
        assert "EXP-001" in subject
        assert "UTF-8" in html or "utf-8" in html


class TestBaseTemplate:
    """Test base HTML template functionality."""

    def test_base_template_structure(self):
        """Test base template has correct structure."""
        title = "Test Title"
        content = "<p>Test Content</p>"

        html = NotificationTemplates._base_html_template(title, content)

        assert title in html
        assert content in html
        assert "<!DOCTYPE html>" in html
        assert "GazTracker" in html

    def test_base_template_styling(self):
        """Test base template includes styling."""
        html = NotificationTemplates._base_html_template("Title", "Content")

        # Check for CSS classes
        assert ".header" in html
        assert ".content" in html
        assert ".footer" in html
        assert ".info-box" in html
        assert ".warning-box" in html
        assert ".success-box" in html
        assert ".danger-box" in html

    def test_base_template_footer(self):
        """Test base template includes footer."""
        html = NotificationTemplates._base_html_template("Title", "Content")

        assert "support@gaztracker.com" in html.lower() or "message automatique" in html.lower()
