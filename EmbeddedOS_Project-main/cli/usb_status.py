#!/usr/bin/env python3
import sys
import pyudev

if len(sys.argv) < 2:
    print("Usage: usb_status.py <serial|devpath>")
    sys.exit(1)

serial = sys.argv[1]
context = pyudev.Context()
for device in context.list_devices(subsystem='block'):
    if device.get('ID_SERIAL_SHORT') == serial or device.get('DEVPATH') == serial:
        dev_node = device.device_node
        with open('/proc/mounts', 'r') as f:
            for line in f:
                if dev_node in line:
                    print(f"{dev_node} is mounted")
                    sys.exit(0)
        print(f"{dev_node} is not mounted")
        sys.exit(0)
print("Device not found")
sys.exit(1)
