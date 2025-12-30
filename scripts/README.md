# Power Switch Pro MCP Scripts

Utility scripts for configuring and managing Power Switch Pro devices.

## setup_ecowitt_autoping.py

Configure automatic ping monitoring and power cycling for an Ecowitt weather station.

### What it does

This script configures the Power Switch Pro's built-in AutoPing feature to:
- Continuously ping your Ecowitt device at a specified interval
- Automatically power cycle the outlet if the device stops responding
- Reboot the Ecowitt to restore connectivity

### Usage

```bash
# Run interactively (will prompt for all settings)
python scripts/setup_ecowitt_autoping.py

# Or set environment variables first
export POWER_SWITCH_HOST="192.168.1.100"
export POWER_SWITCH_PASSWORD="your-password"
python scripts/setup_ecowitt_autoping.py
```

### Configuration

You'll be prompted for:
- **Ecowitt IP address**: The IP address of your Ecowitt device
- **Outlet number**: Which outlet (0-7) the Ecowitt is plugged into
- **Ping interval**: How often to ping (default: 60 seconds)
- **Retries**: Number of failed pings before rebooting (default: 3)

### Example

```
Enter Ecowitt IP address: 192.168.1.50
Enter outlet number for Ecowitt (0-7): 2
Ping interval in seconds (default: 60): 300
Number of failed pings before reboot (default: 3): 5

Configuration:
  Host: 192.168.1.50
  Outlet: 2
  Interval: 300s
  Retries: 5

Add this AutoPing entry? (y/n): y

✓ AutoPing entry added successfully!

The Power Switch Pro will now:
  - Ping 192.168.1.50 every 300 seconds
  - If 5 consecutive pings fail, it will cycle power on outlet 2
  - This will automatically reboot your Ecowitt device
```

## Requirements

The `power-switch-pro` library must be installed:

```bash
pip install power-switch-pro
```

Or if working in this project:

```bash
pip install -e .
```
