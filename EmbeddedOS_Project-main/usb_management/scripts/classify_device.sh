#!/bin/bash
# Script: classify_device.sh
# Usage: classify_device.sh /dev/sdX

DEV=$1
if [ -z "$DEV" ]; then
    echo "Usage: $0 /dev/sdX"
    exit 1
fi
CLASS=$(udevadm info -q property -n "$DEV" | grep ID_USB_CLASS | cut -d= -f2)
case "$CLASS" in
    08) echo "storage";;
    03) echo "hid";;
    01) echo "audio";;
    0e) echo "video";;
    *) echo "unknown";;
esac