"""
Tests for Reports Service

Comprehensive tests for reports service including palette statistics,
expedition statistics, performance reports, dashboard data, and exports.
"""

import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.reports_service import ReportsService
from app.models.palette import Palette, PaletteStatus
from app.models.expedition import Expedition, ExpeditionStatus
from app.models.palette_movement import PaletteMovement
from app.models.notification import Notification, NotificationStatus
from app.models.user import User, UserRole


class TestPaletteStatistics:
    """Test suite for palette statistics."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = ReportsService(self.db)

    def test_get_palette_statistics_basic(self):
        """Test getting basic palette statistics."""
        # Mock palettes
        mock_palettes = [
            Mock(spec=Palette, utilization_rate=50.0, status=PaletteStatus.DISPONIBLE),
            Mock(spec=Palette, utilization_rate=75.0, status=PaletteStatus.EN_EXPEDITION),
            Mock(spec=Palette, utilization_rate=90.0, status=PaletteStatus.DISPONIBLE),
        ]

        # Mock query
        mock_query = Mock()
        mock_query.count.return_value = 3
        mock_query.filter.return_value.count.return_value = 2
        mock_query.all.return_value = mock_palettes
        self.db.query.return_value = mock_query

        # Mock most used palettes query
        mock_most_used = Mock()
        mock_most_used.join.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []

        # Execute
        stats = self.service.get_palette_statistics()

        # Assertions
        assert "total_palettes" in stats
        assert "by_status" in stats
        assert "average_utilization" in stats
        assert "most_used_palettes" in stats
        assert "maintenance_needed" in stats

    def test_get_palette_statistics_with_date_range(self):
        """Test getting palette statistics with date filtering."""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_query.all.return_value = []
        self.db.query.return_value = mock_query

        stats = self.service.get_palette_statistics(start_date, end_date)

        # Verify date filters were applied
        assert mock_query.filter.call_count >= 2

    def test_get_palette_utilization_trend(self):
        """Test getting palette utilization trend."""
        mock_data = [
            Mock(date="2025-01-01", movement_count=10, unique_palettes=5),
            Mock(date="2025-01-02", movement_count=15, unique_palettes=7),
        ]

        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_data
        self.db.query.return_value = mock_query

        trend = self.service.get_palette_utilization_trend(days=7)

        assert len(trend) == 2
        assert trend[0]["movement_count"] == 10
        assert trend[1]["unique_palettes"] == 7

    def test_get_palette_distribution_by_location(self):
        """Test getting palette distribution by location."""
        mock_data = [
            Mock(current_location="Warehouse A", count=20),
            Mock(current_location="Warehouse B", count=15),
        ]

        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.all.return_value = mock_data
        self.db.query.return_value = mock_query

        distribution = self.service.get_palette_distribution_by_location()

        assert distribution["Warehouse A"] == 20
        assert distribution["Warehouse B"] == 15


class TestExpeditionStatistics:
    """Test suite for expedition statistics."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = ReportsService(self.db)

    def test_get_expedition_statistics_basic(self):
        """Test getting basic expedition statistics."""
        # Mock expeditions
        mock_expeditions = [
            Mock(
                spec=Expedition,
                status=ExpeditionStatus.LIVREE,
                date_depart=datetime.utcnow() - timedelta(hours=24),
                date_delivery=datetime.utcnow()
            )
        ]

        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_expeditions
        self.db.query.return_value = mock_query

        stats = self.service.get_expedition_statistics()

        assert "total_expeditions" in stats
        assert "by_status" in stats
        assert "average_delivery_time_hours" in stats
        assert "success_rate" in stats
        assert "delayed_expeditions" in stats

    def test_get_expedition_statistics_calculates_delivery_time(self):
        """Test that average delivery time is calculated correctly."""
        # Mock completed expeditions with known delivery times
        mock_expeditions = [
            Mock(
                spec=Expedition,
                status=ExpeditionStatus.LIVREE,
                date_depart=datetime(2025, 1, 1, 0, 0, 0),
                date_delivery=datetime(2025, 1, 1, 12, 0, 0)  # 12 hours
            ),
            Mock(
                spec=Expedition,
                status=ExpeditionStatus.LIVREE,
                date_depart=datetime(2025, 1, 2, 0, 0, 0),
                date_delivery=datetime(2025, 1, 3, 0, 0, 0)  # 24 hours
            )
        ]

        mock_query = Mock()
        mock_query.count.return_value = 2
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_expeditions
        self.db.query.return_value = mock_query

        stats = self.service.get_expedition_statistics()

        # Average should be (12 + 24) / 2 = 18 hours
        assert stats["average_delivery_time_hours"] == 18.0

    def test_get_expedition_trend(self):
        """Test getting expedition trend."""
        mock_data = [
            Mock(date="2025-01-01", expedition_count=5, total_palettes=25),
            Mock(date="2025-01-02", expedition_count=7, total_palettes=35),
        ]

        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_data
        self.db.query.return_value = mock_query

        trend = self.service.get_expedition_trend(days=7)

        assert len(trend) == 2
        assert trend[0]["expedition_count"] == 5
        assert trend[1]["total_palettes"] == 35

    def test_get_top_destinations(self):
        """Test getting top destinations."""
        mock_data = [
            Mock(destination_address="Address 1", expedition_count=15, total_palettes=75),
            Mock(destination_address="Address 2", expedition_count=10, total_palettes=50),
        ]

        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = mock_data
        self.db.query.return_value = mock_query

        destinations = self.service.get_top_destinations(limit=5)

        assert len(destinations) == 2
        assert destinations[0]["address"] == "Address 1"
        assert destinations[0]["expedition_count"] == 15


class TestPerformanceReports:
    """Test suite for performance reports."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = ReportsService(self.db)

    def test_get_performance_report(self):
        """Test getting comprehensive performance report."""
        # Mock all queries
        mock_query = Mock()
        mock_query.count.return_value = 10
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.scalar.return_value = 10
        self.db.query.return_value = mock_query

        report = self.service.get_performance_report()

        assert "period" in report
        assert "expeditions" in report
        assert "palettes" in report
        assert "notifications" in report
        assert "overall_health" in report

    def test_calculate_health_score_excellent(self):
        """Test health score calculation for excellent performance."""
        health = self.service._calculate_health_score(95.0, 85.0, 90.0)

        assert health["score"] >= 80
        assert health["status"] == "EXCELLENT"

    def test_calculate_health_score_good(self):
        """Test health score calculation for good performance."""
        health = self.service._calculate_health_score(75.0, 65.0, 70.0)

        assert 60 <= health["score"] < 80
        assert health["status"] == "GOOD"

    def test_calculate_health_score_fair(self):
        """Test health score calculation for fair performance."""
        health = self.service._calculate_health_score(55.0, 45.0, 50.0)

        assert 40 <= health["score"] < 60
        assert health["status"] == "FAIR"

    def test_calculate_health_score_poor(self):
        """Test health score calculation for poor performance."""
        health = self.service._calculate_health_score(30.0, 20.0, 25.0)

        assert health["score"] < 40
        assert health["status"] == "POOR"


class TestDashboard:
    """Test suite for dashboard functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = ReportsService(self.db)

    def test_get_dashboard_overview(self):
        """Test getting dashboard overview."""
        # Mock scalar returns for counts
        self.db.query.return_value.scalar.return_value = 10
        self.db.query.return_value.filter.return_value.scalar.return_value = 5

        # Mock trend data
        self.db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []

        overview = self.service.get_dashboard_overview()

        assert "overview" in overview
        assert "recent_activity" in overview
        assert "alerts" in overview
        assert "trends" in overview

    def test_dashboard_overview_structure(self):
        """Test dashboard overview has correct structure."""
        self.db.query.return_value.scalar.return_value = 0
        self.db.query.return_value.filter.return_value.scalar.return_value = 0
        self.db.query.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []

        overview = self.service.get_dashboard_overview()

        # Check overview section
        assert "total_palettes" in overview["overview"]
        assert "available_palettes" in overview["overview"]
        assert "active_expeditions" in overview["overview"]

        # Check recent activity
        assert "expeditions_24h" in overview["recent_activity"]
        assert "movements_24h" in overview["recent_activity"]

        # Check alerts
        assert "delayed_expeditions" in overview["alerts"]
        assert "pending_validations" in overview["alerts"]


class TestUserPerformance:
    """Test suite for user performance reports."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = ReportsService(self.db)

    def test_get_user_performance_all_users(self):
        """Test getting performance for all users."""
        mock_users = [
            Mock(id=uuid4(), username="user1", email="user1@example.com", expeditions_created=10),
            Mock(id=uuid4(), username="user2", email="user2@example.com", expeditions_created=5),
        ]

        mock_query = Mock()
        mock_query.outerjoin.return_value.filter.return_value.group_by.return_value.all.return_value = mock_users
        self.db.query.return_value = mock_query

        performance = self.service.get_user_performance()

        assert len(performance) == 2
        assert performance[0]["username"] == "user1"
        assert performance[0]["expeditions_created"] == 10

    def test_get_user_performance_specific_user(self):
        """Test getting performance for specific user."""
        user_id = str(uuid4())
        mock_users = [
            Mock(id=user_id, username="user1", email="user1@example.com", expeditions_created=10)
        ]

        mock_query = Mock()
        mock_query.outerjoin.return_value.filter.return_value.group_by.return_value.all.return_value = mock_users
        self.db.query.return_value = mock_query

        performance = self.service.get_user_performance(user_id=user_id)

        assert len(performance) == 1
        assert performance[0]["user_id"] == user_id


class TestExportFunctionality:
    """Test suite for data export functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = ReportsService(self.db)

    def test_export_expedition_data_json(self):
        """Test exporting expedition data in JSON format."""
        mock_expeditions = [
            Mock(
                reference_number="EXP-001",
                status=ExpeditionStatus.LIVREE,
                destination_address="Address 1",
                palette_count=5,
                created_at=datetime.utcnow(),
                date_depart=datetime.utcnow(),
                date_delivery=datetime.utcnow(),
                eta=datetime.utcnow()
            )
        ]

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_expeditions
        self.db.query.return_value = mock_query

        data = self.service.export_expedition_data(format="json")

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["reference_number"] == "EXP-001"

    def test_export_expedition_data_csv(self):
        """Test exporting expedition data in CSV format."""
        mock_expeditions = [
            Mock(
                reference_number="EXP-001",
                status=ExpeditionStatus.LIVREE,
                destination_address="Address 1",
                palette_count=5,
                created_at=datetime.utcnow(),
                date_depart=datetime.utcnow(),
                date_delivery=datetime.utcnow(),
                eta=datetime.utcnow()
            )
        ]

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_expeditions
        self.db.query.return_value = mock_query

        data = self.service.export_expedition_data(format="csv")

        assert isinstance(data, str)
        assert "reference_number" in data
        assert "EXP-001" in data

    def test_export_palette_data_json(self):
        """Test exporting palette data in JSON format."""
        mock_palettes = [
            Mock(
                reference_number="PAL-001",
                rfid_tag="RFID-001",
                status=PaletteStatus.DISPONIBLE,
                capacity=100,
                current_bottles=50,
                utilization_rate=50.0,
                current_location="Warehouse A",
                created_at=datetime.utcnow()
            )
        ]

        self.db.query.return_value.all.return_value = mock_palettes

        data = self.service.export_palette_data(format="json")

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["reference_number"] == "PAL-001"

    def test_export_palette_data_csv(self):
        """Test exporting palette data in CSV format."""
        mock_palettes = [
            Mock(
                reference_number="PAL-001",
                rfid_tag="RFID-001",
                status=PaletteStatus.DISPONIBLE,
                capacity=100,
                current_bottles=50,
                utilization_rate=50.0,
                current_location="Warehouse A",
                created_at=datetime.utcnow()
            )
        ]

        self.db.query.return_value.all.return_value = mock_palettes

        data = self.service.export_palette_data(format="csv")

        assert isinstance(data, str)
        assert "reference_number" in data
        assert "PAL-001" in data

    def test_export_unsupported_format_raises_error(self):
        """Test that unsupported export format raises exception."""
        from app.utils.exceptions import ValidationException

        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = []
        self.db.query.return_value = mock_query

        with pytest.raises(ValidationException):
            self.service.export_expedition_data(format="xml")


class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db = Mock(spec=Session)
        self.service = ReportsService(self.db)

    def test_statistics_with_no_data(self):
        """Test statistics calculation with no data."""
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        self.db.query.return_value = mock_query

        stats = self.service.get_palette_statistics()

        assert stats["total_palettes"] == 0
        assert stats["average_utilization"] == 0.0

    def test_performance_report_with_no_notifications(self):
        """Test performance report when no notifications exist."""
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.scalar.return_value = 0
        self.db.query.return_value = mock_query

        report = self.service.get_performance_report()

        assert report["notifications"]["success_rate"] == 0.0

    def test_trend_with_no_data_returns_empty_list(self):
        """Test trend functions return empty lists when no data."""
        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []
        self.db.query.return_value = mock_query

        trend = self.service.get_expedition_trend(days=7)

        assert trend == []
