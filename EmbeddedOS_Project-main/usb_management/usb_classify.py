#!/usr/bin/python3
import pyudev
import subprocess
import logging
from datetime import datetime
from dbus_service import start_dbus_service
from plugin_loader import PluginLoader
import threading
import os

# ---- Cấu hình hệ thống ----
LOG_FILE = "/var/log/usb_classifier.log"
MOUNT_BASE = "/mnt/usb"

# ---- Load USB IDs ----
USB_IDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'usb_ids.txt')

def get_all_device_ids(usb_ids_path):
    device_ids = []
    current_vendor = None
    if not os.path.exists(usb_ids_path):
        print(f"[usb_classify] Warning: {usb_ids_path} not found, whitelist will be ignored.")
        return []
    try:
        with open(usb_ids_path, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                if not line.startswith('\t'):
                    current_vendor = line.strip().split(None, 1)[0].lower()
                else:
                    parts = line.strip().split(None, 1)
                    if len(parts) >= 1 and current_vendor:
                        product_id = parts[0].lower()
                        device_ids.append((current_vendor, product_id))
    except Exception as e:
        logging.warning(f"Could not load device IDs from usb_ids.txt: {e}")
    return device_ids

WHITELIST_DEVICES = get_all_device_ids(USB_IDS_PATH)

# ---- Thiết lập logging ----
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_usb_ids(file_path):
    usb_ids = {}
    current_vendor = None
    if not os.path.exists(file_path):
        print(f"[usb_classify] Warning: {file_path} not found, USB name database will be empty.")
        return {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                if not line.startswith('\t'):
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2:
                        vendor_id, vendor_name = parts
                        current_vendor = vendor_id.lower()
                        usb_ids[current_vendor] = {'name': vendor_name, 'products': {}}
                else:
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2 and current_vendor:
                        product_id, product_name = parts
                        usb_ids[current_vendor]['products'][product_id.lower()] = product_name
    except Exception as e:
        logging.warning(f"Could not load usb_ids.txt: {e}")
    return usb_ids

USB_IDS = load_usb_ids(USB_IDS_PATH)

def log_event(device, classification):
    """Ghi log sự kiện USB"""
    vendor = device.get('ID_VENDOR_ID', 'unknown').lower()
    product = device.get('ID_MODEL_ID', 'unknown').lower()
    serial = device.get('ID_SERIAL_SHORT', 'unknown')
    vendor_name = USB_IDS.get(vendor, {}).get('name', vendor)
    product_name = USB_IDS.get(vendor, {}).get('products', {}).get(product, product)
    logging.info(
        f"Device {device.device_node}: "
        f"Vendor={vendor} ({vendor_name}), Product={product} ({product_name}), "
        f"Serial={serial}, Class={classification}"
    )

def classify_device(device):
    """Phân loại thiết bị với thuật toán cải tiến"""
    usb_class = device.get('ID_USB_INTERFACES', '').lower()
    vendor = device.get('ID_VENDOR_ID', '').lower()
    product = device.get('ID_MODEL_ID', '').lower()
    
    # Kiểm tra whitelist nếu có
    if WHITELIST_DEVICES and (vendor, product) not in WHITELIST_DEVICES:
        return "blocked"
    
    # Phân loại theo class code
    if '08' in usb_class:
        return "storage"
    elif '03' in usb_class:
        return "hid"
    elif '01' in usb_class:
        return "audio"
    elif '0e' in usb_class:
        return "video"
    
    # Phân loại dự phòng bằng USB ID database
    vendor_name = USB_IDS.get(vendor, {}).get('name', None)
    product_name = USB_IDS.get(vendor, {}).get('products', {}).get(product, None)
    if vendor_name or product_name:
        # Optionally, use this info for more advanced classification
        if product_name:
            if 'storage' in product_name.lower():
                return "storage"
            elif 'keyboard' in product_name.lower() or 'mouse' in product_name.lower():
                return "hid"
            elif 'audio' in product_name.lower():
                return "audio"
            elif 'video' in product_name.lower() or 'webcam' in product_name.lower():
                return "video"
    try:
        output = subprocess.check_output(
            f"lsusb -d {vendor}:{product}",
            shell=True,
            text=True
        )
        if 'storage' in output.lower():
            return "storage"
        elif 'keyboard' in output.lower() or 'mouse' in output.lower():
            return "hid"
    except:
        pass
    
    return "unknown"

def handle_device(device, classification):
    """Xử lý thiết bị theo phân loại"""
    dev_node = device.device_node
    
    if classification == "blocked":
        logging.warning(f"Blocked unauthorized device: {dev_node}")
        return
        
    try:
        if classification == "storage":
            mount_point = f"{MOUNT_BASE}_{device.get('ID_VENDOR_ID')}_{device.get('ID_MODEL_ID')}"
            subprocess.run([
                "mount", 
                "-o", "uid=1000,gid=1000,noexec", 
                dev_node, 
                mount_point
            ], check=True)
            
        elif classification == "hid":
            subprocess.run([
                "modprobe", 
                "usbhid"
            ], check=True)
            
        log_event(device, classification)
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to handle {dev_node}: {str(e)}")

# ---- Main Execution ----
if __name__ == "__main__":
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('usb')
    
    logging.info("USB Classifier Daemon Started")
    
    # Khởi tạo và load plugin
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    plugin_loader = PluginLoader(plugins_dir)
    plugin_loader.load_plugins()

    for device in iter(monitor.poll, None):
        if device.action == 'add':
            classification = classify_device(device)
            handle_device(device, classification)
            # Gọi plugin nếu là storage, hid, audio, video
            if classification in ("storage", "hid", "audio", "video"):
                plugin_result = plugin_loader.handle_device(device, 'add')
                if plugin_result:
                    logging.info(f"Plugin handled device: {plugin_result}")

def main():
    # ... (khởi tạo context, monitor)
    
    # Khởi tạo plugin loader
    plugin_loader = PluginLoader("/path/to/plugins")
    plugin_loader.load_plugins()
    
    # Khởi chạy D-Bus service trong thread riêng
    dbus_thread = threading.Thread(target=start_dbus_service, args=(plugin_loader,))
    dbus_thread.daemon = True
    dbus_thread.start()
    
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            # Gửi signal qua D-Bus
            # service.DeviceAdded(vendor, product, dev_type)
            
            # Xử lý qua plugin
            plugin_loader.handle_device(device, 'add')
            
        elif device.action == 'remove':
            plugin_loader.handle_device(device, 'remove')