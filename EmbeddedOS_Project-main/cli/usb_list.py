#!/usr/bin/env python3
import pyudev

context = pyudev.Context()
for device in context.list_devices(subsystem='usb'):
    print(f"Device: {device.device_path}")
    print(f"  Vendor: {device.get('ID_VENDOR_ID')}")
    print(f"  Product: {device.get('ID_MODEL_ID')}")
    print(f"  Serial: {device.get('ID_SERIAL_SHORT')}")
    print(f"  Class: {device.get('ID_USB_CLASS')}")
    print(f"  Driver: {device.driver}")
    print("-" * 50)
