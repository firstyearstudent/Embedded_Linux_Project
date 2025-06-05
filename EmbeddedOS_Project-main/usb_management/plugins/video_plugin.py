import os

def load_video_devices_from_usb_ids():
    usb_ids_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'usb_ids.txt')
    video_devices = set()
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
                        if 'video' in product_name or 'webcam' in product_name or 'camera' in product_name:
                            video_devices.add((current_vendor, product_id))
    except Exception as e:
        pass
    return video_devices

VIDEO_DEVICES = load_video_devices_from_usb_ids()

def can_handle(device):
    vendor = device.get('ID_VENDOR_ID', '').lower()
    product = device.get('ID_MODEL_ID', '').lower()
    if (vendor, product) in VIDEO_DEVICES:
        return True
    return device.get('ID_USB_CLASS') == '0e'

def handle(device, action):
    # Đơn giản: restart dịch vụ video nếu có
    import subprocess
    try:
        subprocess.run(['systemctl', 'restart', 'v4l2.service'], check=True)
        return f"Video device handled: {device.get('ID_VENDOR_ID')}:{device.get('ID_MODEL_ID')}"
    except Exception as e:
        return f"Failed to handle video device: {e}"
