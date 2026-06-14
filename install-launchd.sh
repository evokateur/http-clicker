#!/usr/bin/env bash
# Install http-clicker as a launchd user agent, self-locating from this
# script's directory. Safe to re-run: replaces any existing agent.
set -euo pipefail

LABEL="com.wesley.http-clicker"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UV_PATH="$(command -v uv)"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"

mkdir -p "$HOME/Library/LaunchAgents"

# Tear down any existing agent and wait for launchd to fully release the
# label before re-registering it. bootout is asynchronous, so bootstrapping
# immediately afterwards can race a slow-exiting process and fail with
# "Bootstrap failed: 5: Input/output error".
launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
for _ in $(seq 1 20); do
    launchctl print "gui/$(id -u)/${LABEL}" >/dev/null 2>&1 || break
    sleep 0.25
done

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${UV_PATH}</string>
        <string>run</string>
        <string>server.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${PROJECT_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardOutPath</key>
    <string>${PROJECT_DIR}/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>${PROJECT_DIR}/launchd.log</string>
</dict>
</plist>
EOF

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"

echo "Installed and started ${LABEL}."
echo "Plist: ${PLIST_PATH}"
echo "Logs:  ${PROJECT_DIR}/launchd.log"
