#!/bin/bash
# Script: general_hadling.sh
# Usage: general_hadling.sh mount|unmount /dev/sdX

ACTION=$1
DEV=$2
MOUNT_POINT="/mnt/usb_${DEV##*/}"
if [ -z "$ACTION" ] || [ -z "$DEV" ]; then
    echo "Usage: $0 mount|unmount /dev/sdX"
    exit 1
fi
if [ "$ACTION" = "mount" ]; then
    mkdir -p "$MOUNT_POINT"
    mount "$DEV" "$MOUNT_POINT" && echo "Mounted $DEV at $MOUNT_POINT"
elif [ "$ACTION" = "unmount" ]; then
    umount "$DEV" && echo "Unmounted $DEV"
else
    echo "Unknown action: $ACTION"
    exit 1
fi

DEVICE_PATH="$1"
VENDOR_ID=$(udevadm info -q property -n $DEVICE_PATH | grep "ID_VENDOR_ID" | cut -d= -f2)
PRODUCT_ID=$(udevadm info -q property -n $DEVICE_PATH | grep "ID_MODEL_ID" | cut -d= -f2)

# Sử dụng classify_device.sh để xác định loại thiết bị
DEVICE_TYPE=$(/usr/local/bin/usb_management/classify_device.sh $VENDOR_ID $PRODUCT_ID)

# Lưu ý: whitelist kiểm tra theo cả Vendor ID + Product ID trong classify_device.sh
# Nếu thiết bị không hợp lệ, DEVICE_TYPE sẽ là 'blocked'

# Gọi script chuyên biệt
case $DEVICE_TYPE in
    storage) /usr/local/bin/usb_management/scripts/handle_storage.sh $DEVICE_PATH;;
    hid_*) /usr/local/bin/usb_management/scripts/handle_hid.sh $DEVICE_PATH;;
    audio) /usr/local/bin/usb_management/scripts/handle_audio.sh $DEVICE_PATH;;
    *) logger -t usb_manager "Unknown device type: $DEVICE_TYPE";;
esac