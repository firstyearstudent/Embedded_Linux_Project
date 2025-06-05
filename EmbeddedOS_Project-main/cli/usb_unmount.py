#!/usr/bin/env python3
import sys
import pyudev
import subprocess

if len(sys.argv) < 2:
    print("Usage: usb_unmount.py <serial|devpath>")
    sys.exit(1)

serial = sys.argv[1]
context = pyudev.Context()
for device in context.list_devices(subsystem='block'):
    if device.get('ID_SERIAL_SHORT') == serial or device.get('DEVPATH') == serial:
        dev_node = device.device_node
        subprocess.run(['umount', dev_node], check=True)
        print(f"Unmounted {dev_node}")
        sys.exit(0)
print("Device not found")
sys.exit(1)
