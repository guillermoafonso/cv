#!/bin/bash
#
# Launcher for counting game.
# Used by autostart when the child user logs in.
# Pygame uses the normal desktop display - no special drivers needed.
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"

# Small delay to let the desktop finish drawing, so the game
# window reliably takes fullscreen focus
sleep 2

python3 counting_game.py
