#!/bin/bash
#
# Sync counting game config and stats with Google Drive
#
# Setup:
#   1. Install rclone: sudo apt install rclone
#   2. Configure rclone: rclone config (create remote named 'gdrive')
#   3. Create folder on Google Drive: rclone mkdir gdrive:counting-game
#   4. Make this script executable: chmod +x sync_gdrive.sh
#   5. Run manually or add to cron
#
# Usage:
#   ./sync_gdrive.sh pull    # Download config from Google Drive
#   ./sync_gdrive.sh push    # Upload stats to Google Drive
#   ./sync_gdrive.sh sync    # Bidirectional sync (pull config, push stats)
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE="gdrive:counting-game"

# Files to sync
CONFIG_FILE="config.json"
STATS_FILE="stats.json"

case "$1" in
    pull)
        echo "Pulling config from Google Drive..."
        rclone copy "$REMOTE/$CONFIG_FILE" "$SCRIPT_DIR/" --update
        echo "Done. Config updated from Google Drive."
        ;;
    push)
        echo "Pushing stats to Google Drive..."
        rclone copy "$SCRIPT_DIR/$STATS_FILE" "$REMOTE/" --update
        echo "Done. Stats uploaded to Google Drive."
        ;;
    sync)
        echo "Syncing with Google Drive..."
        # Pull config (Google Drive -> Pi)
        rclone copy "$REMOTE/$CONFIG_FILE" "$SCRIPT_DIR/" --update
        # Push stats (Pi -> Google Drive)
        rclone copy "$SCRIPT_DIR/$STATS_FILE" "$REMOTE/" --update
        # Also push config if it doesn't exist on Drive yet
        rclone copy "$SCRIPT_DIR/$CONFIG_FILE" "$REMOTE/" --ignore-existing
        echo "Done. Config pulled, stats pushed."
        ;;
    init)
        echo "Initializing Google Drive folder..."
        rclone mkdir "$REMOTE" 2>/dev/null
        rclone copy "$SCRIPT_DIR/$CONFIG_FILE" "$REMOTE/" --ignore-existing
        rclone copy "$SCRIPT_DIR/$STATS_FILE" "$REMOTE/" --ignore-existing 2>/dev/null
        echo "Done. Folder created and initial files uploaded."
        ;;
    *)
        echo "Usage: $0 {pull|push|sync|init}"
        echo ""
        echo "  pull  - Download config.json from Google Drive"
        echo "  push  - Upload stats.json to Google Drive"
        echo "  sync  - Pull config, push stats"
        echo "  init  - Create Google Drive folder and upload initial files"
        exit 1
        ;;
esac
