# http-clicker

## Setup

### Requirements

- macOS. The host Mac must be on the same network as the TV.

- Install `uv`:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- Copy or clone this project folder onto the machine.

### Smoke test

- `cd` into the project directory and start the server:

```sh
uv run server.py
```

When you see "Uvicorn running on <http://0.0.0.0:8000>", the app will be available at `http://<hostname>.local:8000/`.

Stop the server with Ctrl-C

### Install launch daemon

To install it as a background service that starts on login and restarts itself if it crashes:

```sh
./install-launchd.sh
```

If it stops responding, double-click `restart-launchd.command`.

To remove the background service: `./uninstall-launchd.sh`.
