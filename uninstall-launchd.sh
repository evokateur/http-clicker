#!/usr/bin/env bash
# Stop and remove the http-clicker launchd agent installed by install.sh.
set -euo pipefail

LABEL="com.wesley.http-clicker"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
rm -f "$PLIST_PATH" "${PROJECT_DIR}/launchd.log"

echo "Removed ${LABEL}."
