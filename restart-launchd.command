#!/usr/bin/env bash
# Double-click to restart http-clicker if it's stopped responding.
launchctl kickstart -k "gui/$(id -u)/com.wesley.http-clicker"
echo "http-clicker restarted."
