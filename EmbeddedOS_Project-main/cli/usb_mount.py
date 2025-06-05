#!/usr/bin/env python3
import sys
import pyudev
import subprocess

if len(sys.argv) < 2:
    print("Usage: usb_mount.py <serial|devpath>")
    sys.exit(1)

serial = sys.argv[1]
context = pyudev.Context()
for device in context.list_devices(subsystem='block'):
    if device.get('ID_SERIAL_SHORT') == serial or device.get('DEVPATH') == serial:
        dev_node = device.device_node
        mount_point = f"/mnt/usb_{device.get('ID_VENDOR_ID')}_{device.get('ID_MODEL_ID')}"
        subprocess.run(['mkdir', '-p', mount_point], check=True)
        subprocess.run(['mount', dev_node, mount_point], check=True)
        print(f"Mounted {dev_node} at {mount_point}")
        sys.exit(0)
print("Device not found")
sys.exit(1)
