#!/usr/bin/env python3
"""
Configure AutoPing for Ecowitt weather station.

This script sets up the Power Switch Pro to automatically reboot the Ecowitt
device if it fails to respond to ping requests.
"""

import os
import sys

from power_switch_pro import PowerSwitchPro


def main():
    """Configure AutoPing for Ecowitt device."""
    # Get connection parameters from environment or prompt
    host = os.getenv("POWER_SWITCH_HOST")
    username = os.getenv("POWER_SWITCH_USERNAME", "admin")
    password = os.getenv("POWER_SWITCH_PASSWORD")
    use_https = os.getenv("POWER_SWITCH_USE_HTTPS", "false").lower() == "true"

    if not host:
        host = input("Enter Power Switch Pro IP address: ")
    if not password:
        password = input("Enter Power Switch Pro password: ")

    # Get Ecowitt configuration
    ecowitt_ip = input("Enter Ecowitt IP address: ")
    outlet_id = int(input("Enter outlet number for Ecowitt (0-7): "))

    # Optional parameters with defaults
    interval_input = input("Ping interval in seconds (default: 60): ").strip()
    interval = int(interval_input) if interval_input else 60

    retries_input = input("Number of failed pings before reboot (default: 3): ").strip()
    retries = int(retries_input) if retries_input else 3

    print(f"\nConnecting to Power Switch Pro at {host}...")
    switch = PowerSwitchPro(
        host=host,
        username=username,
        password=password,
        use_https=use_https,
        verify_ssl=False,
    )

    if not switch.test_connection():
        print("Failed to connect to device!")
        sys.exit(1)

    print("Connected successfully!\n")

    # List existing AutoPing entries
    print("=== Current AutoPing Entries ===\n")
    entries = switch.autoping.list_entries()
    if entries:
        for i, entry in enumerate(entries):
            print(f"Entry {i}:")
            print(f"  Host: {entry.get('host', 'N/A')}")
            print(f"  Outlet: {entry.get('outlet', 'N/A')}")
            print(f"  Enabled: {entry.get('enabled', 'N/A')}")
            print(f"  Interval: {entry.get('interval', 'N/A')}s")
            print(f"  Retries: {entry.get('retries', 'N/A')}")
            print()
    else:
        print("No AutoPing entries configured\n")

    # Add AutoPing entry for Ecowitt
    print("=== Adding AutoPing Entry for Ecowitt ===\n")
    print("Configuration:")
    print(f"  Host: {ecowitt_ip}")
    print(f"  Outlet: {outlet_id}")
    print(f"  Interval: {interval}s")
    print(f"  Retries: {retries}")
    print()

    confirm = input("Add this AutoPing entry? (y/n): ").lower()
    if confirm != "y":
        print("Cancelled.")
        sys.exit(0)

    result = switch.autoping.add_entry(
        host=ecowitt_ip,
        outlet=outlet_id,
        enabled=True,
        interval=interval,
        retries=retries,
    )

    print("\n✓ AutoPing entry added successfully!")
    print(f"  Entry details: {result}")
    print("\nThe Power Switch Pro will now:")
    print(f"  - Ping {ecowitt_ip} every {interval} seconds")
    print(f"  - If {retries} consecutive pings fail, it will cycle power on outlet {outlet_id}")
    print("  - This will automatically reboot your Ecowitt device")


if __name__ == "__main__":
    main()
