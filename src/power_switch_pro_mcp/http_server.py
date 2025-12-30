#!/usr/bin/env python3
"""HTTP server for Power Switch Pro MCP using streamable HTTP transport.

This server exposes the Power Switch Pro MCP tools over HTTP using the
MCP streamable-http transport, which is the recommended transport for
production deployments.
"""

import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from power_switch_pro import PowerSwitchPro
from power_switch_pro.exceptions import PowerSwitchError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global device instance (initialized from environment variables)
_device: PowerSwitchPro | None = None


def get_device() -> PowerSwitchPro:
    """Get or create the PowerSwitchPro device instance."""
    global _device
    if _device is None:
        host = os.getenv("POWER_SWITCH_HOST")
        username = os.getenv("POWER_SWITCH_USERNAME", "admin")
        password = os.getenv("POWER_SWITCH_PASSWORD")
        use_https = os.getenv("POWER_SWITCH_USE_HTTPS", "false").lower() == "true"

        if not host or not password:
            raise ValueError(
                "POWER_SWITCH_HOST and POWER_SWITCH_PASSWORD environment variables must be set"
            )

        _device = PowerSwitchPro(host, username, password, use_https=use_https)
        logger.info(f"Connected to Power Switch Pro at {host}")

    return _device


# Create FastMCP server with stateless HTTP and JSON responses (recommended for production)
# Configure to bind to 0.0.0.0 with configurable port (default 5000)
DEFAULT_PORT = 5000
port = int(os.getenv("PORT", DEFAULT_PORT))

mcp = FastMCP(
    "power-switch-pro",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    port=port,
)


@mcp.tool()
def outlet_on(outlet_id: int) -> str:
    """Turn on a specific outlet on the Power Switch Pro device.

    Args:
        outlet_id: Outlet number (0-7 for 8-outlet device)
    """
    try:
        device = get_device()
        device.outlets[outlet_id].on()
        return f"Outlet {outlet_id + 1} turned ON"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in outlet_on: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in outlet_on: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def outlet_off(outlet_id: int) -> str:
    """Turn off a specific outlet on the Power Switch Pro device.

    Args:
        outlet_id: Outlet number (0-7 for 8-outlet device)
    """
    try:
        device = get_device()
        device.outlets[outlet_id].off()
        return f"Outlet {outlet_id + 1} turned OFF"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in outlet_off: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in outlet_off: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def outlet_cycle(outlet_id: int) -> str:
    """Power cycle a specific outlet (turn off, wait, then turn back on).

    Args:
        outlet_id: Outlet number (0-7 for 8-outlet device)
    """
    try:
        device = get_device()
        device.outlets[outlet_id].cycle()
        return f"Outlet {outlet_id + 1} power cycled"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in outlet_cycle: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in outlet_cycle: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_outlet_state(outlet_id: int) -> str:
    """Get the current power state of a specific outlet.

    Args:
        outlet_id: Outlet number (0-7 for 8-outlet device)
    """
    try:
        device = get_device()
        state = device.outlets[outlet_id].state
        state_str = "ON" if state else "OFF"
        return f"Outlet {outlet_id + 1} is {state_str}"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in get_outlet_state: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in get_outlet_state: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_all_outlet_states() -> str:
    """Get the power states of all outlets on the device."""
    try:
        device = get_device()
        states = device.outlets.get_all_states()
        result = []
        for i, state in enumerate(states):
            state_str = "ON" if state else "OFF"
            result.append(f"Outlet {i + 1}: {state_str}")
        return "\n".join(result)
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in get_all_outlet_states: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in get_all_outlet_states: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_outlet_info(outlet_id: int) -> dict[str, Any]:
    """Get detailed information about an outlet (name, state, lock status).

    Args:
        outlet_id: Outlet number (0-7 for 8-outlet device)
    """
    try:
        device = get_device()
        outlet = device.outlets[outlet_id]
        return {
            "id": outlet_id,
            "name": outlet.name,
            "state": "ON" if outlet.state else "OFF",
            "locked": outlet.locked,
        }
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in get_outlet_info: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_outlet_info: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def set_outlet_name(outlet_id: int, name: str) -> str:
    """Set or rename an outlet on the device.

    Args:
        outlet_id: Outlet number (0-7 for 8-outlet device)
        name: New name for the outlet (max 16 characters)
    """
    try:
        device = get_device()
        device.outlets[outlet_id].name = name
        return f"Outlet {outlet_id + 1} renamed to '{name}'"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in set_outlet_name: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in set_outlet_name: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def get_power_metrics() -> dict[str, Any]:
    """Get real-time power metrics (voltage, current, power) from the device."""
    try:
        device = get_device()
        voltage = device.meters.get_voltage()
        current = device.meters.get_current()
        power = device.meters.get_power()
        energy = device.meters.get_energy()

        return {
            "voltage_v": voltage,
            "current_a": current,
            "power_w": power,
            "energy_kwh": energy,
        }
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in get_power_metrics: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_power_metrics: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def get_device_info() -> dict[str, Any]:
    """Get device information (serial number, firmware version, etc.)."""
    try:
        device = get_device()
        # Library now resolves $ref references automatically
        return device.info
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in get_device_info: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_device_info: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def bulk_outlet_operation(action: str, outlet_ids: list[int] | None = None) -> str:
    """Perform an operation on multiple outlets at once.

    Args:
        action: Action to perform: 'on', 'off', or 'cycle'
        outlet_ids: List of outlet IDs to operate on (if omitted, operates on all unlocked outlets)
    """
    try:
        device = get_device()

        if outlet_ids is not None:
            # Operate on specific outlets
            for outlet_id in outlet_ids:
                outlet = device.outlets[outlet_id]
                if action == "on":
                    outlet.on()
                elif action == "off":
                    outlet.off()
                elif action == "cycle":
                    outlet.cycle()
            msg = f"Performed '{action}' on outlets: {[i+1 for i in outlet_ids]}"
        else:
            # Operate on all unlocked outlets
            device.outlets.bulk_operation(locked=False, action=action)
            msg = f"Performed '{action}' on all unlocked outlets"

        return msg
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in bulk_outlet_operation: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in bulk_outlet_operation: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def autoping_add_entry(
    host: str,
    outlet_id: int,
    enabled: bool = True,
    interval: int = 60,
    retries: int = 3,
) -> str:
    """Add an AutoPing entry to monitor a host and reset an outlet if ping fails.

    Args:
        host: Host to ping (IP address or hostname)
        outlet_id: Outlet number (0-7 for 8-outlet device)
        enabled: Whether entry is enabled (default: True)
        interval: Ping interval in seconds (default: 60)
        retries: Number of retries before cycling outlet (default: 3)
    """
    try:
        device = get_device()
        result = device.autoping.add_entry(
            host=host,
            outlet=outlet_id,
            enabled=enabled,
            interval=interval,
            retries=retries,
        )
        return f"Added AutoPing entry for host {host} on outlet {outlet_id + 1}\n{result}"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in autoping_add_entry: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in autoping_add_entry: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def autoping_list_entries() -> str:
    """List all AutoPing entries configured on the device."""
    try:
        device = get_device()
        entries = device.autoping.list_entries()
        if entries:
            result = []
            for i, entry in enumerate(entries):
                # Extract hosts from addresses array
                hosts = entry.get("addresses", [])
                host = hosts[0] if hosts else "N/A"
                # Extract outlet from outlets array
                outlets = entry.get("outlets", [])
                outlet = outlets[0] if outlets else -1
                # Get status info
                status = entry.get("status", {})
                host_status = status.get("hosts", [{}])[0] if status.get("hosts") else {}
                success_count = host_status.get("success_count", 0)
                failure_count = host_status.get("failure_count", 0)

                result.append(
                    f"Entry {i}:\n"
                    f"  Host: {host}\n"
                    f"  Outlet: {outlet + 1}\n"
                    f"  Enabled: {entry.get('enabled', False)}\n"
                    f"  State: {'Active' if host_status.get('state') else 'Inactive'}\n"
                    f"  Success: {success_count} | Failures: {failure_count}"
                )
            return "\n\n".join(result)
        return "No AutoPing entries configured"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in autoping_list_entries: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in autoping_list_entries: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def autoping_get_entry(entry_id: int) -> dict[str, Any]:
    """Get details of a specific AutoPing entry.

    Args:
        entry_id: AutoPing entry ID
    """
    try:
        device = get_device()
        entry = device.autoping.get_entry(entry_id)
        return entry
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in autoping_get_entry: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in autoping_get_entry: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
def autoping_update_entry(
    entry_id: int,
    host: str | None = None,
    outlet_id: int | None = None,
    enabled: bool | None = None,
    interval: int | None = None,
    retries: int | None = None,
) -> str:
    """Update an existing AutoPing entry.

    Args:
        entry_id: AutoPing entry ID
        host: New host to ping (optional)
        outlet_id: New outlet number (optional)
        enabled: New enabled status (optional)
        interval: New ping interval in seconds (optional)
        retries: New number of retries (optional)
    """
    try:
        device = get_device()
        success = device.autoping.update_entry(
            entry_id=entry_id,
            host=host,
            outlet=outlet_id,
            enabled=enabled,
            interval=interval,
            retries=retries,
        )
        status = "updated successfully" if success else "update failed"
        return f"AutoPing entry {entry_id} {status}"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in autoping_update_entry: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in autoping_update_entry: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def autoping_delete_entry(entry_id: int) -> str:
    """Delete an AutoPing entry.

    Args:
        entry_id: AutoPing entry ID
    """
    try:
        device = get_device()
        success = device.autoping.delete_entry(entry_id)
        status = "deleted successfully" if success else "delete failed"
        return f"AutoPing entry {entry_id} {status}"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in autoping_delete_entry: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in autoping_delete_entry: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def autoping_enable_entry(entry_id: int) -> str:
    """Enable an AutoPing entry.

    Args:
        entry_id: AutoPing entry ID
    """
    try:
        device = get_device()
        success = device.autoping.enable_entry(entry_id)
        status = "enabled successfully" if success else "enable failed"
        return f"AutoPing entry {entry_id} {status}"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in autoping_enable_entry: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in autoping_enable_entry: {e}")
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def autoping_disable_entry(entry_id: int) -> str:
    """Disable an AutoPing entry.

    Args:
        entry_id: AutoPing entry ID
    """
    try:
        device = get_device()
        success = device.autoping.disable_entry(entry_id)
        status = "disabled successfully" if success else "disable failed"
        return f"AutoPing entry {entry_id} {status}"
    except PowerSwitchError as e:
        logger.error(f"Power Switch error in autoping_disable_entry: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in autoping_disable_entry: {e}")
        return f"Unexpected error: {str(e)}"


if __name__ == "__main__":
    # Run server with SSE (Server-Sent Events) transport for HTTP
    # Port can be configured via PORT environment variable (default: 5000)
    logger.info(f"Starting Power Switch Pro MCP HTTP server on 0.0.0.0:{port}")
    mcp.run(transport="sse")
