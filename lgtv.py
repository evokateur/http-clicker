"""Shared functions for talking to an LG webOS TV over the local network."""

import asyncio
import json
import socket
import ssl
from pathlib import Path

import websockets
from websockets import Subprotocol

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SEARCH_TARGET = "urn:lge-com:service:webos-second-screen:1"
SUBPROTOCOL = Subprotocol("com.webos.service.networkinput.client")

STATE_FILE = Path(__file__).parent / ".tv-state.json"

MANIFEST = {
    "manifestVersion": 1,
    "appVersion": "1.0",
    "signed": {"localizedAppNames": {"": "The Clicker"}},
    "permissions": [
        "LAUNCH",
        "CONTROL_INPUT_TV",
        "CONTROL_AUDIO",
        "READ_NETWORK_STATE",
    ],
}


def discover_tvs(timeout=5):
    """SSDP M-SEARCH for LG webOS TVs. Returns a list of {ip, mac, uuid} dicts (mac/uuid omitted if absent)."""
    msg = "\r\n".join(
        [
            "M-SEARCH * HTTP/1.1",
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}",
            'MAN: "ssdp:discover"',
            "MX: 5",
            f"ST: {SEARCH_TARGET}",
            "",
            "",
        ]
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.sendto(msg.encode(), (SSDP_ADDR, SSDP_PORT))
            data, addr = sock.recvfrom(4096)
        except OSError:
            return []

    headers = {}
    for line in data.decode().split("\r\n")[1:]:
        if ":" in line:
            key, _, value = line.partition(":")
            headers[key.strip().upper()] = value.strip()

    tv = {"ip": addr[0]}

    wakeup = headers.get("WAKEUP")
    if wakeup:
        for part in wakeup.split(";"):
            if part.strip().upper().startswith("MAC="):
                tv["mac"] = part.split("=", 1)[1].strip()
                break

    usn = headers.get("USN")
    if usn:
        tv["uuid"] = usn.removeprefix("uuid:").split("::", 1)[0]

    return [tv]


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


async def connect(ip, timeout=3):
    """Open a wss connection to the TV, accepting its self-signed cert."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    return await asyncio.wait_for(
        websockets.connect(
            f"wss://{ip}:3001/",
            subprotocols=[SUBPROTOCOL],
            ssl=context,
        ),
        timeout=timeout,
    )


async def register(ws, client_key=None):
    """Register with the TV, returning the client key (new or existing)."""
    payload = {
        "forcePairing": False,
        "pairingType": "PROMPT",
        "manifest": MANIFEST,
    }
    if client_key:
        payload["client-key"] = client_key
    else:
        print("No client key on file, waiting for pairing confirmation from TV.")

    await ws.send(
        json.dumps(
            {
                "type": "register",
                "id": "register_0",
                "payload": payload,
            }
        )
    )

    while True:
        response = json.loads(await ws.recv())
        if response["type"] == "registered":
            return response["payload"]["client-key"]
        if response["type"] == "error":
            raise RuntimeError(response.get("error", "registration failed"))


async def send_command(ws, uri, payload=None):
    await ws.send(
        json.dumps(
            {
                "type": "request",
                "id": "1",
                "uri": uri,
                "payload": payload or {},
            }
        )
    )
    response = json.loads(await ws.recv())
    if response["type"] == "error":
        raise RuntimeError(response.get("error", "request failed"))
    if response.get("payload", {}).get("returnValue") is False:
        raise RuntimeError(response["payload"].get("errorText", "request failed"))
    return response


async def launch_live_tv(ws):
    return await send_command(
        ws, "ssap://system.launcher/launch", {"id": "com.webos.app.livetv"}
    )


async def get_network_info(ws):
    return await send_command(ws, "ssap://com.webos.service.connectionmanager/getinfo")


async def get_wakeup_mac(ws):
    response = await get_network_info(ws)
    payload = response.get("payload", {})
    for key in ("wifiInfo", "wiredInfo"):
        mac = payload.get(key, {}).get("macAddress")
        if mac:
            return mac
    return None


async def channel_up(ws):
    return await send_command(ws, "ssap://tv/channelUp")


async def channel_down(ws):
    return await send_command(ws, "ssap://tv/channelDown")


def send_magic_packet(mac):
    """Best-effort Wake-on-LAN."""
    mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
    magic = b"\xff" * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(magic, ("<broadcast>", 9))
