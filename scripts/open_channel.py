"""Sanity check: switch to a channel by its display number (e.g. "10-1")."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lgtv


async def main(channel_number):
    state = lgtv.load_state()
    if not state.get("ip"):
        print("No paired TV. Press TV first.")
        return

    ws = await lgtv.connect(state["ip"])
    try:
        await lgtv.register(ws, state.get("client_key"))

        channels = (await lgtv.get_channel_list(ws))["payload"]["channelList"]
        match = next((c for c in channels if c["channelNumber"] == channel_number), None)
        if not match:
            print(f"Channel {channel_number} not found in scanned channel list.")
            return

        await lgtv.open_channel(ws, match["channelId"])
        print(f"Switched to {channel_number} ({match['channelName']}).")
    finally:
        await ws.close()


if len(sys.argv) != 2:
    print("Usage: open_channel.py <channel-number, e.g. 10-1>")
    sys.exit(1)

asyncio.run(main(sys.argv[1]))
