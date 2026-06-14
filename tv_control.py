"""Orchestration logic for TV remote actions.

Sits between the low-level webOS protocol (lgtv.py) and the HTTP layer
(server.py): runs the live-TV recovery flow and channel commands, returning
JSON-serializable result dicts.
"""

import asyncio
import os

import lgtv


async def _launch_from_saved_tv(state):
    if not state.get("ip"):
        return False

    try:
        ws = await lgtv.connect(state["ip"])
    except (OSError, asyncio.TimeoutError):
        return False

    try:
        state["client_key"] = await lgtv.register(ws, state.get("client_key"))
        if not state.get("mac"):
            mac = await lgtv.get_wakeup_mac(ws)
            if mac:
                state["mac"] = mac
        await lgtv.launch_live_tv(ws)
    except RuntimeError:
        return False
    finally:
        await ws.close()

    lgtv.save_state(state)
    return True


def _verify_tv_identity(state):
    """Saved TV isn't responding - check whether it's now at a different IP."""
    if not state.get("uuid"):
        return False

    for tv in lgtv.discover_tvs():
        if tv.get("uuid") == state["uuid"]:
            state["ip"] = tv["ip"]
            if tv.get("mac"):
                state["mac"] = tv["mac"]
            return True

    return False


async def press_tv():
    """Get to Live TV from whatever state the TV is in."""
    state = lgtv.load_state()

    if await _launch_from_saved_tv(state):
        return {"status": "ok", "message": "Live TV."}

    if _verify_tv_identity(state) and await _launch_from_saved_tv(state):
        return {"status": "ok", "message": "Live TV."}

    if state.get("mac"):
        lgtv.send_magic_packet(state["mac"])
        for delay in (2, 4, 8, 16):
            await asyncio.sleep(delay)
            if await _launch_from_saved_tv(state):
                return {"status": "ok", "message": "Live TV."}

    tvs = lgtv.discover_tvs()
    if tvs:
        state = tvs[0]  # pick one to pair (first, for now)
        lgtv.save_state(state)
        if await _launch_from_saved_tv(state):
            return {"status": "ok", "message": "Live TV."}

    return {"status": "failed", "message": "Make sure your TV is on."}


async def press_channel(direction):
    """Send a channel up/down command. Assumes the TV is already paired and on."""
    state = lgtv.load_state()
    if not state.get("ip"):
        return {"status": "failed", "message": "Press TV first."}

    try:
        ws = await lgtv.connect(state["ip"])
    except (OSError, asyncio.TimeoutError):
        return {"status": "failed", "message": "Can't reach the TV. Press TV first."}

    try:
        await lgtv.register(ws, state.get("client_key"))
        if direction == "up":
            await lgtv.channel_up(ws)
        else:
            await lgtv.channel_down(ws)
        return {"status": "ok", "message": ""}
    except RuntimeError as e:
        return {"status": "failed", "message": str(e)}
    finally:
        await ws.close()


def get_status():
    state = lgtv.load_state()
    return {
        "paired": bool(state.get("ip")),
        "ip": state.get("ip"),
        "mac": state.get("mac"),
        "open_fds": len(os.listdir("/dev/fd")),
    }
