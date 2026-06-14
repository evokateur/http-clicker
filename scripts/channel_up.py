"""Sanity check: send channel up without running the web server."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tv_control


async def main():
    result = await tv_control.press_channel("up")
    if result["status"] != "ok":
        print(result["message"])


asyncio.run(main())
