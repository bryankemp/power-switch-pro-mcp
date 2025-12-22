"""Unit tests for HTTP server module."""

from unittest.mock import MagicMock, patch

import pytest

from power_switch_pro_mcp import http_server


@pytest.mark.unit
class TestGetDevice:
    """Tests for get_device function."""

    def test_get_device_creates_device(self, reset_device_singleton):
        """Test that get_device creates a PowerSwitchPro instance."""
        with patch("power_switch_pro_mcp.http_server.PowerSwitchPro") as mock_ps:
            mock_instance = MagicMock()
            mock_ps.return_value = mock_instance

            device = http_server.get_device()

            assert device == mock_instance
            mock_ps.assert_called_once_with("192.168.0.100", "admin", "test-password", use_https=False)

    def test_get_device_returns_cached_device(self, reset_device_singleton):
        """Test that get_device returns the cached device on subsequent calls."""
        with patch("power_switch_pro_mcp.http_server.PowerSwitchPro") as mock_ps:
            mock_instance = MagicMock()
            mock_ps.return_value = mock_instance

            device1 = http_server.get_device()
            device2 = http_server.get_device()

            assert device1 == device2
            mock_ps.assert_called_once()  # Only called once

    def test_get_device_missing_host(self, monkeypatch, reset_device_singleton):
        """Test that get_device raises ValueError when host is missing."""
        monkeypatch.delenv("POWER_SWITCH_HOST")

        with pytest.raises(ValueError, match="POWER_SWITCH_HOST and POWER_SWITCH_PASSWORD"):
            http_server.get_device()

    def test_get_device_missing_password(self, monkeypatch, reset_device_singleton):
        """Test that get_device raises ValueError when password is missing."""
        monkeypatch.delenv("POWER_SWITCH_PASSWORD")

        with pytest.raises(ValueError, match="POWER_SWITCH_HOST and POWER_SWITCH_PASSWORD"):
            http_server.get_device()


@pytest.mark.unit
class TestOutletControl:
    """Tests for outlet control functions."""

    def test_outlet_on(self, mock_power_switch, reset_device_singleton):
        """Test turning on an outlet."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.outlet_on(0)

            assert result == "Outlet 1 turned ON"
            mock_power_switch.outlets[0].on.assert_called_once()

    def test_outlet_off(self, mock_power_switch, reset_device_singleton):
        """Test turning off an outlet."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.outlet_off(3)

            assert result == "Outlet 4 turned OFF"
            mock_power_switch.outlets[3].off.assert_called_once()

    def test_outlet_cycle(self, mock_power_switch, reset_device_singleton):
        """Test power cycling an outlet."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.outlet_cycle(5)

            assert result == "Outlet 6 power cycled"
            mock_power_switch.outlets[5].cycle.assert_called_once()


@pytest.mark.unit
class TestOutletStatus:
    """Tests for outlet status functions."""

    def test_get_outlet_state(self, mock_power_switch, reset_device_singleton):
        """Test getting the state of an outlet."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.get_outlet_state(0)

            assert result == "Outlet 1 is ON"

    def test_get_all_outlet_states(self, mock_power_switch, reset_device_singleton):
        """Test getting all outlet states."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.get_all_outlet_states()

            assert "Outlet 1: ON" in result
            assert "Outlet 2: OFF" in result
            assert "Outlet 3: ON" in result

    def test_get_outlet_info(self, mock_power_switch, reset_device_singleton):
        """Test getting detailed outlet info."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.get_outlet_info(0)

            assert result["id"] == 0
            assert result["name"] == "Test Outlet"
            assert result["state"] == "ON"
            assert result["locked"] is False


@pytest.mark.unit
class TestConfiguration:
    """Tests for configuration functions."""

    def test_set_outlet_name(self, mock_power_switch, reset_device_singleton):
        """Test setting outlet name."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.set_outlet_name(0, "New Name")

            assert result == "Outlet 1 renamed to 'New Name'"
            assert mock_power_switch.outlets[0].name == "New Name"


@pytest.mark.unit
class TestPowerMetrics:
    """Tests for power metrics functions."""

    def test_get_power_metrics(self, mock_power_switch, reset_device_singleton):
        """Test getting power metrics."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.get_power_metrics()

            assert result["voltage_v"] == 120.5
            assert result["current_a"] == 2.5
            assert result["power_w"] == 300.0
            assert result["energy_kwh"] == 1.5

    def test_get_device_info(self, mock_power_switch, reset_device_singleton):
        """Test getting device info."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.get_device_info()

            assert result["serial"] == "TEST123456"
            assert result["firmware"] == "1.7.0"
            assert result["model"] == "LPC952X"


@pytest.mark.unit
class TestBulkOperations:
    """Tests for bulk operations."""

    def test_bulk_outlet_operation_specific_outlets(self, mock_power_switch, reset_device_singleton):
        """Test bulk operation on specific outlets."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.bulk_outlet_operation("on", [0, 2, 4])

            assert "Performed 'on' on outlets: [1, 3, 5]" in result
            # Since all outlets share the same mock, on() should be called 3 times total
            assert mock_power_switch.outlets[0].on.call_count == 3

    def test_bulk_outlet_operation_all_outlets(self, mock_power_switch, reset_device_singleton):
        """Test bulk operation on all unlocked outlets."""
        with patch("power_switch_pro_mcp.http_server.get_device", return_value=mock_power_switch):
            result = http_server.bulk_outlet_operation("off", None)

            assert "Performed 'off' on all unlocked outlets" in result
            mock_power_switch.outlets.bulk_operation.assert_called_once_with(locked=False, action="off")
