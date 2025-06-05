# Thêm thông tin thiết bị cụ thể của bạn vào đây
SUPPORTED_DEVICES = {
    # Format: (vendor_id, product_id): "Device Name"
    ("0bda", "9210"): "Realtek Semiconductor Corp. RTL9210 M.2 NVME Adapter",
    ("03eb", "8b05"): "Atmel Corp.",
    ("090c", "2000"): "Silicon Motion, Inc. - Taiwan (formerly Feiya Technology Corp.) USB DISK",
    ("1d6b", "0002"): "Linux Foundation 2.0 root hub",
    ("1d6b", "0003"): "Linux Foundation 3.0 root hub"
}

def can_handle(device):
    vendor = device.get('ID_VENDOR_ID')
    product = device.get('ID_MODEL_ID')
    
    # Kiểm tra theo danh sách thiết bị cụ thể
    if (vendor, product) in SUPPORTED_DEVICES:
        return True
    
    # Kiểm tra theo class code
    return device.get('ID_USB_CLASS') == '08'

def handle(device, action):
    import subprocess
    dev_node = device.get('DEVNAME') or device.get('device_node')
    mount_point = f"/mnt/usb_{device.get('ID_VENDOR_ID')}_{device.get('ID_MODEL_ID')}"
    try:
        subprocess.run(['mkdir', '-p', mount_point], check=True)
        subprocess.run(['mount', dev_node, mount_point], check=True)
        return f"Storage device mounted at {mount_point}"
    except Exception as e:
        return f"Failed to mount storage device: {e}"