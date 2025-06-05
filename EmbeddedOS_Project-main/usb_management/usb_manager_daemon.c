// usb_manager_daemon.c 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <syslog.h>
#include <libudev.h>
#include <systemd/sd-daemon.h>

// Biến toàn cục để quản lý vòng lặp chính
static volatile sig_atomic_t running = 1;

// Xử lý tín hiệu để dừng daemon đúng cách
void handle_signal(int sig) {
    running = 0;
}

int main() {
    // Thiết lập logging
    openlog("usb_manager_daemon", LOG_PID|LOG_CONS, LOG_DAEMON);
    syslog(LOG_INFO, "USB Manager Daemon starting...");

    // Đăng ký xử lý tín hiệu
    signal(SIGTERM, handle_signal);
    signal(SIGINT, handle_signal);

    // Tạo context udev
    struct udev *udev = udev_new();
    if (!udev) {
        syslog(LOG_ERR, "Failed to create udev context");
        closelog();
        return EXIT_FAILURE;
    }

    // Tạo monitor
    struct udev_monitor *mon = udev_monitor_new_from_netlink(udev, "udev");
    if (!mon) {
        syslog(LOG_ERR, "Failed to create udev monitor");
        udev_unref(udev);
        closelog();
        return EXIT_FAILURE;
    }

    // Thiết lập filter cho USB devices
    if (udev_monitor_filter_add_match_subsystem_devtype(mon, "usb", NULL) < 0) {
        syslog(LOG_ERR, "Failed to add subsystem filter");
        udev_monitor_unref(mon);
        udev_unref(udev);
        closelog();
        return EXIT_FAILURE;
    }

    // Bắt đầu nhận sự kiện
    if (udev_monitor_enable_receiving(mon) < 0) {
        syslog(LOG_ERR, "Failed to enable receiving");
        udev_monitor_unref(mon);
        udev_unref(udev);
        closelog();
        return EXIT_FAILURE;
    }

    // Thông báo cho systemd daemon đã sẵn sàng
    sd_notify(0, "READY=1");
    syslog(LOG_INFO, "Daemon initialized and ready");

    // Vòng lặp chính
    while (running) {
        struct udev_device *dev = udev_monitor_receive_device(mon);
        if (!dev) {
            syslog(LOG_WARNING, "No device received, continuing...");
            continue;
        }

        // Lấy thông tin thiết bị
        const char *action = udev_device_get_action(dev);
        const char *vendor = udev_device_get_sysattr_value(dev, "idVendor");
        const char *product = udev_device_get_sysattr_value(dev, "idProduct");
        const char *devpath = udev_device_get_devpath(dev);

        if (action && vendor && product) {
            syslog(LOG_INFO, "Device event: %s - Vendor: %s, Product: %s, Path: %s", 
                   action, vendor, product, devpath);
            
            // Xử lý các sự kiện cụ thể
            if (strcmp(action, "add") == 0) {
                syslog(LOG_NOTICE, "USB device connected: %s:%s", vendor, product);
            } else if (strcmp(action, "remove") == 0) {
                syslog(LOG_NOTICE, "USB device disconnected: %s:%s", vendor, product);
            }
        } else {
            syslog(LOG_WARNING, "Incomplete device information received");
        }

        udev_device_unref(dev);
    }

    // Dọn dẹp trước khi thoát
    syslog(LOG_INFO, "Shutting down USB Manager Daemon");
    udev_monitor_unref(mon);
    udev_unref(udev);
    sd_notify(0, "STOPPING=1");
    closelog();

    return EXIT_SUCCESS;
}