"""
D-Bus service cho quản lý USB.
Cung cấp các method: ListDevices, MountDevice, UnmountDevice, GetStatus, SendEvent.
"""

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import pyudev
import subprocess

# Giả sử bạn có các hàm hoặc class quản lý thiết bị USB ở nơi khác
# Ở đây sẽ dùng biến giả lập để minh họa

class USBManagerService(dbus.service.Object):
    """
    D-Bus service cho quản lý USB.
    """

    def __init__(self, bus, object_path='/org/example/USBManager'):
        super().__init__(bus, object_path)
        self.context = pyudev.Context()

    @dbus.service.method("org.example.USBManager",
                         in_signature='', out_signature='a{sa{sv}}')
    def ListDevices(self):
        """
        Trả về danh sách thiết bị USB hiện tại.
        """
        devices = []
        for device in self.context.list_devices(subsystem='usb'):
            dev = {
                "id": device.get('ID_SERIAL_SHORT') or device.get('DEVPATH'),
                "name": device.get('ID_MODEL') or device.get('ID_MODEL_ID'),
                "status": "mounted" if device.get('DEVNAME') and self.is_mounted(device.get('DEVNAME')) else "unmounted",
                "serial": device.get('ID_SERIAL_SHORT')
            }
            devices.append(dev)
        return devices

    def is_mounted(self, devname):
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    if devname in line:
                        return True
        except Exception:
            pass
        return False

    @dbus.service.method("org.example.USBManager",
                         in_signature='s', out_signature='b')
    def MountDevice(self, device_id):
        """
        Mount thiết bị USB theo device_id.
        """
        for device in self.context.list_devices(subsystem='block'):
            if device.get('ID_SERIAL_SHORT') == device_id or device.get('DEVPATH') == device_id:
                dev_node = device.device_node
                mount_point = f"/mnt/usb_{device.get('ID_VENDOR_ID')}_{device.get('ID_MODEL_ID')}"
                try:
                    subprocess.run(['mkdir', '-p', mount_point], check=True)
                    subprocess.run(['mount', dev_node, mount_point], check=True)
                    return True
                except Exception:
                    return False
        return False

    @dbus.service.method("org.example.USBManager",
                         in_signature='s', out_signature='b')
    def UnmountDevice(self, device_id):
        """
        Unmount thiết bị USB theo device_id.
        """
        for device in self.context.list_devices(subsystem='block'):
            if device.get('ID_SERIAL_SHORT') == device_id or device.get('DEVPATH') == device_id:
                dev_node = device.device_node
                try:
                    subprocess.run(['umount', dev_node], check=True)
                    return True
                except Exception:
                    return False
        return False

    @dbus.service.method("org.example.USBManager",
                         in_signature='s', out_signature='s')
    def GetStatus(self, device_id):
        """
        Lấy trạng thái thiết bị USB.
        """
        for dev in self.device_list:
            if dev["id"] == device_id:
                return dev["status"]
        return "unknown"

    @dbus.service.signal("org.example.USBManager",
                         signature='ss')
    def SendEvent(self, event_type, data):
        """
        Gửi sự kiện tới client (signal).
        """
        pass  # Signal sẽ được gửi khi gọi hàm này

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    name = dbus.service.BusName("org.example.USBManager", bus)
    service = USBManagerService(bus)
    print("USBManagerService D-Bus đang chạy...")
    loop = GLib.MainLoop()
    loop.run()

if __name__ == "__main__":
    main()

"""
Hướng dẫn sử dụng:
- Chạy trực tiếp: python3 usb_management/dbus_service.py
- Hoặc tạo file .service cho systemd để tự động khởi động cùng hệ thống.
"""