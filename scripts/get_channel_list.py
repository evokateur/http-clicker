"""Sanity check: dump the TV's scanned channel list as JSON."""

import asyncio
import json
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

    print(json.dumps(response, indent=2))


asyncio.run(main())
