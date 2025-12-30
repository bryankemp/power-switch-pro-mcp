#!/usr/bin/env python3
"""MCP Server for Power Switch Pro devices.

This server provides tools for controlling and monitoring Digital Loggers
Power Switch Pro devices via the Model Context Protocol (MCP).
"""

import json
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from power_switch_pro import PowerSwitchPro
from power_switch_pro.exceptions import PowerSwitchError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server instance
server = Server("power-switch-pro")

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


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="outlet_on",
            description="Turn on a specific outlet on the Power Switch Pro device",
            inputSchema={
                "type": "object",
                "properties": {
                    "outlet_id": {
                        "type": "integer",
                        "description": "Outlet number (0-7 for 8-outlet device)",
                        "minimum": 0,
                        "maximum": 7,
                    }
                },
                "required": ["outlet_id"],
            },
        ),
        Tool(
            name="outlet_off",
            description="Turn off a specific outlet on the Power Switch Pro device",
            inputSchema={
                "type": "object",
                "properties": {
                    "outlet_id": {
                        "type": "integer",
                        "description": "Outlet number (0-7 for 8-outlet device)",
                        "minimum": 0,
                        "maximum": 7,
                    }
                },
                "required": ["outlet_id"],
            },
        ),
        Tool(
            name="outlet_cycle",
            description="Power cycle a specific outlet (turn off, wait, then turn back on)",
            inputSchema={
                "type": "object",
                "properties": {
                    "outlet_id": {
                        "type": "integer",
                        "description": "Outlet number (0-7 for 8-outlet device)",
                        "minimum": 0,
                        "maximum": 7,
                    }
                },
                "required": ["outlet_id"],
            },
        ),
        Tool(
            name="get_outlet_state",
            description="Get the current power state of a specific outlet",
            inputSchema={
                "type": "object",
                "properties": {
                    "outlet_id": {
                        "type": "integer",
                        "description": "Outlet number (0-7 for 8-outlet device)",
                        "minimum": 0,
                        "maximum": 7,
                    }
                },
                "required": ["outlet_id"],
            },
        ),
        Tool(
            name="get_all_outlet_states",
            description="Get the power states of all outlets on the device",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_outlet_info",
            description="Get detailed information about an outlet (name, state, lock status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "outlet_id": {
                        "type": "integer",
                        "description": "Outlet number (0-7 for 8-outlet device)",
                        "minimum": 0,
                        "maximum": 7,
                    }
                },
                "required": ["outlet_id"],
            },
        ),
        Tool(
            name="set_outlet_name",
            description="Set or rename an outlet on the device",
            inputSchema={
                "type": "object",
                "properties": {
                    "outlet_id": {
                        "type": "integer",
                        "description": "Outlet number (0-7 for 8-outlet device)",
                        "minimum": 0,
                        "maximum": 7,
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the outlet",
                        "maxLength": 16,
                    },
                },
                "required": ["outlet_id", "name"],
            },
        ),
        Tool(
            name="get_power_metrics",
            description="Get real-time power metrics (voltage, current, power) from the device",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_device_info",
            description="Get device information (serial number, firmware version, etc.)",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="bulk_outlet_operation",
            description="Perform an operation on multiple outlets at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform: 'on', 'off', or 'cycle'",
                        "enum": ["on", "off", "cycle"],
                    },
                    "outlet_ids": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0, "maximum": 7},
                        "description": (
                            "List of outlet IDs to operate on "
                            "(if omitted, operates on all unlocked outlets)"
                        ),
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="autoping_add_entry",
            description="Add an AutoPing entry to monitor a host and reset an outlet if ping fails",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Host to ping (IP address or hostname)",
                    },
                    "outlet_id": {
                        "type": "integer",
                        "description": "Outlet number (0-7 for 8-outlet device)",
                        "minimum": 0,
                        "maximum": 7,
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Whether entry is enabled",
                        "default": True,
                    },
                    "interval": {
                        "type": "integer",
                        "description": "Ping interval in seconds",
                        "default": 60,
                        "minimum": 1,
                    },
                    "retries": {
                        "type": "integer",
                        "description": "Number of retries before cycling outlet",
                        "default": 3,
                        "minimum": 1,
                    },
                },
                "required": ["host", "outlet_id"],
            },
        ),
        Tool(
            name="autoping_list_entries",
            description="List all AutoPing entries configured on the device",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="autoping_get_entry",
            description="Get details of a specific AutoPing entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "AutoPing entry ID",
                        "minimum": 0,
                    }
                },
                "required": ["entry_id"],
            },
        ),
        Tool(
            name="autoping_update_entry",
            description="Update an existing AutoPing entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "AutoPing entry ID",
                        "minimum": 0,
                    },
                    "host": {
                        "type": "string",
                        "description": "New host to ping (optional)",
                    },
                    "outlet_id": {
                        "type": "integer",
                        "description": "New outlet number (optional)",
                        "minimum": 0,
                        "maximum": 7,
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "New enabled status (optional)",
                    },
                    "interval": {
                        "type": "integer",
                        "description": "New ping interval in seconds (optional)",
                        "minimum": 1,
                    },
                    "retries": {
                        "type": "integer",
                        "description": "New number of retries (optional)",
                        "minimum": 1,
                    },
                },
                "required": ["entry_id"],
            },
        ),
        Tool(
            name="autoping_delete_entry",
            description="Delete an AutoPing entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "AutoPing entry ID",
                        "minimum": 0,
                    }
                },
                "required": ["entry_id"],
            },
        ),
        Tool(
            name="autoping_enable_entry",
            description="Enable an AutoPing entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "AutoPing entry ID",
                        "minimum": 0,
                    }
                },
                "required": ["entry_id"],
            },
        ),
        Tool(
            name="autoping_disable_entry",
            description="Disable an AutoPing entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "AutoPing entry ID",
                        "minimum": 0,
                    }
                },
                "required": ["entry_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        device = get_device()

        if name == "outlet_on":
            outlet_id = arguments["outlet_id"]
            device.outlets[outlet_id].on()
            return [TextContent(type="text", text=f"Outlet {outlet_id + 1} turned ON")]

        elif name == "outlet_off":
            outlet_id = arguments["outlet_id"]
            device.outlets[outlet_id].off()
            return [TextContent(type="text", text=f"Outlet {outlet_id + 1} turned OFF")]

        elif name == "outlet_cycle":
            outlet_id = arguments["outlet_id"]
            device.outlets[outlet_id].cycle()
            return [TextContent(type="text", text=f"Outlet {outlet_id + 1} power cycled")]

        elif name == "get_outlet_state":
            outlet_id = arguments["outlet_id"]
            state = device.outlets[outlet_id].state
            state_str = "ON" if state else "OFF"
            return [TextContent(type="text", text=f"Outlet {outlet_id + 1} is {state_str}")]

        elif name == "get_all_outlet_states":
            states = device.outlets.get_all_states()
            result = []
            for i, state in enumerate(states):
                state_str = "ON" if state else "OFF"
                result.append(f"Outlet {i + 1}: {state_str}")
            return [TextContent(type="text", text="\n".join(result))]

        elif name == "get_outlet_info":
            outlet_id = arguments["outlet_id"]
            outlet = device.outlets[outlet_id]
            info = {
                "id": outlet_id,
                "name": outlet.name,
                "state": "ON" if outlet.state else "OFF",
                "locked": outlet.locked,
            }
            return [TextContent(type="text", text=json.dumps(info, indent=2))]

        elif name == "set_outlet_name":
            outlet_id = arguments["outlet_id"]
            name = arguments["name"]
            device.outlets[outlet_id].name = name
            return [TextContent(type="text", text=f"Outlet {outlet_id + 1} renamed to '{name}'")]

        elif name == "get_power_metrics":
            voltage = device.meters.get_voltage()
            current = device.meters.get_current()
            power = device.meters.get_power()
            energy = device.meters.get_energy()

            metrics = {
                "voltage_v": voltage,
                "current_a": current,
                "power_w": power,
                "energy_kwh": energy,
            }
            return [TextContent(type="text", text=json.dumps(metrics, indent=2))]

        elif name == "get_device_info":
            info = device.info
            return [TextContent(type="text", text=json.dumps(info, indent=2))]

        elif name == "bulk_outlet_operation":
            action = arguments["action"]
            outlet_ids = arguments.get("outlet_ids")

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

            return [TextContent(type="text", text=msg)]

        elif name == "autoping_add_entry":
            host = arguments["host"]
            outlet_id = arguments["outlet_id"]
            enabled = arguments.get("enabled", True)
            interval = arguments.get("interval", 60)
            retries = arguments.get("retries", 3)

            result = device.autoping.add_entry(
                host=host,
                outlet=outlet_id,
                enabled=enabled,
                interval=interval,
                retries=retries,
            )
            msg = (
                f"Added AutoPing entry for host {host} on outlet {outlet_id + 1}\n"
                f"{json.dumps(result, indent=2)}"
            )
            return [TextContent(type="text", text=msg)]

        elif name == "autoping_list_entries":
            entries = device.autoping.list_entries()
            if entries:
                result = []
                for i, entry in enumerate(entries):
                    result.append(
                        f"Entry {i}:\n"
                        f"  Host: {entry.get('host', 'N/A')}\n"
                        f"  Outlet: {int(entry.get('outlet', -1)) + 1}\n"
                        f"  Enabled: {entry.get('enabled', 'N/A')}\n"
                        f"  Interval: {entry.get('interval', 'N/A')}s\n"
                        f"  Retries: {entry.get('retries', 'N/A')}"
                    )
                return [TextContent(type="text", text="\n\n".join(result))]
            return [TextContent(type="text", text="No AutoPing entries configured")]

        elif name == "autoping_get_entry":
            entry_id = arguments["entry_id"]
            entry = device.autoping.get_entry(entry_id)
            return [TextContent(type="text", text=json.dumps(entry, indent=2))]

        elif name == "autoping_update_entry":
            entry_id = arguments["entry_id"]
            host = arguments.get("host")
            outlet_id = arguments.get("outlet_id")
            enabled = arguments.get("enabled")
            interval = arguments.get("interval")
            retries = arguments.get("retries")

            success = device.autoping.update_entry(
                entry_id=entry_id,
                host=host,
                outlet=outlet_id,
                enabled=enabled,
                interval=interval,
                retries=retries,
            )
            status = "updated successfully" if success else "update failed"
            return [TextContent(type="text", text=f"AutoPing entry {entry_id} {status}")]

        elif name == "autoping_delete_entry":
            entry_id = arguments["entry_id"]
            success = device.autoping.delete_entry(entry_id)
            status = "deleted successfully" if success else "delete failed"
            return [TextContent(type="text", text=f"AutoPing entry {entry_id} {status}")]

        elif name == "autoping_enable_entry":
            entry_id = arguments["entry_id"]
            success = device.autoping.enable_entry(entry_id)
            status = "enabled successfully" if success else "enable failed"
            return [TextContent(type="text", text=f"AutoPing entry {entry_id} {status}")]

        elif name == "autoping_disable_entry":
            entry_id = arguments["entry_id"]
            success = device.autoping.disable_entry(entry_id)
            status = "disabled successfully" if success else "disable failed"
            return [TextContent(type="text", text=f"AutoPing entry {entry_id} {status}")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except PowerSwitchError as e:
        logger.error(f"Power Switch error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error in {name}: {e}")
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
