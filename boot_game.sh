#!/bin/bash
#
# Boot wrapper for counting game - runs Pygame on framebuffer
# before the desktop environment starts.
#
# This script is called by the counting-game.service systemd unit.
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGFILE="$SCRIPT_DIR/boot_game.log"

echo "=== Boot game starting at $(date) ===" > "$LOGFILE"

# List available display devices for debugging
echo "Display devices:" >> "$LOGFILE"
ls -la /dev/dri/ >> "$LOGFILE" 2>&1

# Disable audio to avoid ALSA errors at boot
export SDL_AUDIODRIVER=dummy

cd "$SCRIPT_DIR"

# Try KMS/DRM first (Raspberry Pi OS Bookworm and newer)
echo "Trying kmsdrm..." >> "$LOGFILE"
export SDL_VIDEODRIVER=kmsdrm

# Try card1 first (common on Pi), then card0
for card in /dev/dri/card1 /dev/dri/card0; do
    if [ -e "$card" ]; then
        export SDL_KMSDRM_DEVICE="$card"
        echo "Trying $card..." >> "$LOGFILE"
        python3 counting_game.py --boot 2>> "$LOGFILE"
        if [ $? -eq 0 ]; then
            echo "Success with kmsdrm on $card" >> "$LOGFILE"
            exit 0
        fi
        echo "Failed with kmsdrm on $card" >> "$LOGFILE"
    fi
done

# Fall back to fbcon (older Pi OS)
echo "Trying fbcon..." >> "$LOGFILE"
export SDL_VIDEODRIVER=fbcon
python3 counting_game.py --boot 2>> "$LOGFILE"
if [ $? -eq 0 ]; then
    echo "Success with fbcon" >> "$LOGFILE"
    exit 0
fi

echo "All video drivers failed" >> "$LOGFILE"

# Always exit 0 so the desktop starts even if the game crashes
exit 0
