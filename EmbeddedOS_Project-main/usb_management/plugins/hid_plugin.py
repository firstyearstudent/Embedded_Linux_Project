import os
import subprocess

def load_hid_devices_from_usb_ids():
    usb_ids_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'usb_ids.txt')
    hid_devices = set()
    current_vendor = None
    try:
        with open(usb_ids_path, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                if not line.startswith('\t'):
                    current_vendor = line.strip().split(None, 1)[0].lower()
                else:
                    parts = line.strip().split(None, 1)
                    if len(parts) >= 2 and current_vendor:
                        product_id, product_name = parts[0].lower(), parts[1].lower()
                        # Nhận diện thiết bị HID qua tên
                        if 'keyboard' in product_name or 'mouse' in product_name or 'hid' in product_name:
                            hid_devices.add((current_vendor, product_id))
    except Exception as e:
        pass
    return hid_devices

HID_DEVICES = load_hid_devices_from_usb_ids()

def can_handle(device):
    vendor = device.get('ID_VENDOR_ID', '').lower()
    product = device.get('ID_MODEL_ID', '').lower()
    # Kiểm tra theo danh sách tự động từ usb_ids.txt
    if (vendor, product) in HID_DEVICES:
        return True
    # Kiểm tra theo class code
    return device.get('ID_USB_CLASS') == '03'

def handle(device, action):
    try:
        subprocess.run(['modprobe', 'usbhid'], check=True)
        return f"HID device handled: {device.get('ID_VENDOR_ID')}:{device.get('ID_MODEL_ID')}"
    except Exception as e:
        return f"Failed to handle HID device: {e}" 