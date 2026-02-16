#!/bin/bash
#
# Boot wrapper for counting game - runs Pygame on framebuffer
# before the desktop environment starts.
#
# This script is called by the counting-game.service systemd unit.
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Try KMS/DRM first (Raspberry Pi OS Bookworm and newer),
# fall back to fbcon (older Pi OS versions)
export SDL_VIDEODRIVER=kmsdrm

# Ensure we can access the display device
export SDL_KMSDRM_DEVICE=/dev/dri/card0

# Disable audio to avoid ALSA errors at boot
export SDL_AUDIODRIVER=dummy

cd "$SCRIPT_DIR"

# Try running with kmsdrm, if it fails try fbcon
python3 counting_game.py 2>/dev/null
if [ $? -ne 0 ]; then
    export SDL_VIDEODRIVER=fbcon
    python3 counting_game.py 2>/dev/null
fi

# Always exit 0 so the desktop starts even if the game crashes
exit 0
