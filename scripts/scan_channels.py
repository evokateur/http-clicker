"""Fetch the TV's scanned terrestrial channels and cache them locally.

Run this after rescanning channels on the TV (Settings > Channel Tuning).
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lgtv


async def main():
    state = lgtv.load_state()
    if not state.get("ip"):
        print("No paired TV. Press TV first.")
        return

    ws = await lgtv.connect(state["ip"])
    try:
        await lgtv.register(ws, state.get("client_key"))
        response = await lgtv.get_channel_list(ws)
    finally:
        await ws.close()

    terrestrial = [
        c for c in response["payload"]["channelList"] if c["channelMode"] == "Terrestrial"
    ]
    terrestrial.sort(key=lambda c: (c["majorNumber"], c["minorNumber"]))

    channels = [
        {
            "channelId": c["channelId"],
            "channelNumber": c["channelNumber"],
            "channelName": c["channelName"],
        }
        for c in terrestrial
    ]
    lgtv.save_channels(channels)

    print(f"Saved {len(channels)} terrestrial channels to {lgtv.CHANNELS_FILE}:")
    for c in channels:
        print(f"  {c['channelNumber']:>6}  {c['channelName']}")


asyncio.run(main())
