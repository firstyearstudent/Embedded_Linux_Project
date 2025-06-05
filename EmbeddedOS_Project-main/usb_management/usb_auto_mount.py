try:
    import pyudev
except ImportError:
    print("pyudev not installed. Please install with: pip install pyudev")
    exit(1)
import subprocess
import shutil

if not shutil.which('udisksctl'):
    print("udisksctl not found. Please install udisks2 package.")
    exit(1)

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='block', device_type='disk')

print("Đang theo dõi sự kiện USB...")

for device in iter(monitor.poll, None):
    if device.action == 'add':
        # Kiểm tra thiết bị là USB storage
        if 'ID_BUS' in device and device['ID_BUS'] == 'usb':
            devnode = device.device_node
            print(f"Phát hiện USB storage: {devnode}")
            # Dùng udisksctl để mount
            try:
                subprocess.run(['udisksctl', 'mount', '-b', devnode], check=True)
                print(f"Đã mount {devnode}")
            except subprocess.CalledProcessError:
                print(f"Lỗi khi mount {devnode}")
    elif device.action == 'remove':
        if 'ID_BUS' in device and device['ID_BUS'] == 'usb':
            devnode = device.device_node
            print(f"USB storage bị tháo: {devnode}")
            # Tự động unmount nếu cần (không bắt buộc vì udisksctl sẽ tự xử lý)