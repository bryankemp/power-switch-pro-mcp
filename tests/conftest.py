"""Shared test fixtures and configuration for pytest."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for all tests."""
    monkeypatch.setenv("POWER_SWITCH_HOST", "192.168.0.100")
    monkeypatch.setenv("POWER_SWITCH_PASSWORD", "test-password")
    monkeypatch.setenv("POWER_SWITCH_USERNAME", "admin")
    monkeypatch.setenv("POWER_SWITCH_USE_HTTPS", "false")


@pytest.fixture
def mock_power_switch():
    """Create a mock PowerSwitchPro device."""
    mock_device = MagicMock()

    # Mock outlets
    mock_outlet = MagicMock()
    mock_outlet.on.return_value = None
    mock_outlet.off.return_value = None
    mock_outlet.cycle.return_value = None
    mock_outlet.state = True
    mock_outlet.name = "Test Outlet"
    mock_outlet.locked = False

    # Create mock outlets manager
    mock_outlets = MagicMock()
    mock_outlets.__getitem__ = lambda self, idx: mock_outlet
    mock_outlets.get_all_states.return_value = [True, False, True, False, True, False, True, False]
    mock_outlets.bulk_operation.return_value = None
    mock_device.outlets = mock_outlets

    # Mock meters
    mock_device.meters.get_voltage.return_value = 120.5
    mock_device.meters.get_current.return_value = 2.5
    mock_device.meters.get_power.return_value = 300.0
    mock_device.meters.get_energy.return_value = 1.5

    # Mock device info
    mock_device.info = {
        "serial": "TEST123456",
        "firmware": "1.7.0",
        "model": "LPC952X",
    }

    return mock_device


@pytest.fixture
def reset_device_singleton():
    """Reset the global device singleton between tests."""
    from power_switch_pro_mcp import http_server, server

    server._device = None
    http_server._device = None
    yield
    server._device = None
    http_server._device = None
