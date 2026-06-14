"""LAN web server exposing TV remote controls for an LG webOS TV."""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import tv_control

STATIC_DIR = Path(__file__).parent / "static"

FD_LOG_INTERVAL = 3600  # seconds


async def _log_fd_count():
    while True:
        await asyncio.sleep(FD_LOG_INTERVAL)
        print(f"open file descriptors: {len(os.listdir('/dev/fd'))}")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_log_fd_count())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

tv_lock = asyncio.Lock()


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/manifest.json")
async def manifest():
    return FileResponse(STATIC_DIR / "manifest.json")


@app.post("/tv")
async def tv_button():
    async with tv_lock:
        return await tv_control.press_tv()


@app.post("/channel-up")
async def channel_up():
    async with tv_lock:
        return await tv_control.press_channel("up")


@app.post("/channel-down")
async def channel_down():
    async with tv_lock:
        return await tv_control.press_channel("down")


@app.get("/status")
async def status():
    return tv_control.get_status()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
