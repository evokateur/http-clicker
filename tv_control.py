"""Orchestration logic for TV remote actions.

Sits between the low-level webOS protocol (lgtv.py) and the HTTP layer
(server.py): runs the live-TV recovery flow and channel commands, returning
JSON-serializable result dicts.
"""

import asyncio
import os

import lgtv


async def _connect_and_register(ip, state):
    """Connect to the TV and register, updating state['client_key']. Returns ws, or None if unreachable."""
    try:
        ws = await lgtv.connect(ip)
    except (OSError, asyncio.TimeoutError):
        return None

    try:
        state["client_key"] = await lgtv.register(ws, state.get("client_key"))
    except RuntimeError:
        await ws.close()
        return None

    return ws


def _channel_label(channel_id):
    return next(
        (
            f"{c['channelNumber']} {c['channelName']}"
            for c in lgtv.load_channels()
            if c["channelId"] == channel_id
        ),
        channel_id,
    )


async def _go_live(ws, state):
    """Launch Live TV and re-enter the last channel. Returns a status message."""
    if not state.get("mac"):
        mac = await lgtv.get_wakeup_mac(ws)
        if mac:
            state["mac"] = mac

    await lgtv.launch_live_tv(ws)

    channel_id = state.get("channel_id")
    if not channel_id:
        return "Live TV."

    label = _channel_label(channel_id)
    try:
        await lgtv.open_channel(ws, channel_id)
        print(f"TV: re-entered {label}")
        return label
    except RuntimeError as e:
        print(f"TV: could not re-enter {label}: {e}")
        return "Live TV."


async def _try_live_tv(state):
    """Attempt the full press-TV flow against state['ip']. Returns a message, or None on failure."""
    if not state.get("ip"):
        return None

    ws = await _connect_and_register(state["ip"], state)
    if ws is None:
        return None

    try:
        message = await _go_live(ws, state)
    except RuntimeError:
        return None
    finally:
        await ws.close()

    lgtv.save_state(state)
    return message


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

    message = await _try_live_tv(state)
    if message:
        return {"status": "ok", "message": message}

    if _verify_tv_identity(state):
        message = await _try_live_tv(state)
        if message:
            return {"status": "ok", "message": message}

    if state.get("mac"):
        lgtv.send_magic_packet(state["mac"])
        for delay in (2, 4, 8, 16):
            await asyncio.sleep(delay)
            message = await _try_live_tv(state)
            if message:
                return {"status": "ok", "message": message}

    tvs = lgtv.discover_tvs()
    if tvs:
        state = tvs[0]  # pick one to pair (first, for now)
        lgtv.save_state(state)
        message = await _try_live_tv(state)
        if message:
            return {"status": "ok", "message": message}

    return {"status": "failed", "message": "Make sure your TV is on."}


async def press_channel(direction):
    """Step through the cached terrestrial channel list. Assumes the TV is already paired and on."""
    state = lgtv.load_state()
    if not state.get("ip"):
        return {"status": "failed", "message": "Press TV first."}

    channels = lgtv.load_channels()
    if not channels:
        return {"status": "failed", "message": "No channel list. Run scan_channels.py."}

    current_index = next(
        (i for i, c in enumerate(channels) if c["channelId"] == state.get("channel_id")), -1
    )
    step = 1 if direction == "up" else -1
    channel = channels[(current_index + step) % len(channels)]

    ws = await _connect_and_register(state["ip"], state)
    if ws is None:
        return {"status": "failed", "message": "Can't reach the TV. Press TV first."}

    try:
        await lgtv.open_channel(ws, channel["channelId"])
    except RuntimeError as e:
        return {"status": "failed", "message": str(e)}
    finally:
        await ws.close()

    state["channel_id"] = channel["channelId"]
    lgtv.save_state(state)
    print(f"Channel {direction}: {channel['channelNumber']} {channel['channelName']}")
    return {"status": "ok", "message": f"{channel['channelNumber']} {channel['channelName']}"}


def get_status():
    state = lgtv.load_state()
    return {
        "paired": bool(state.get("ip")),
        "ip": state.get("ip"),
        "mac": state.get("mac"),
        "open_fds": len(os.listdir("/dev/fd")),
    }
