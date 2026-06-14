# The (HTTP) Clicker

A very simple (1960s simple) LG TV controller. For people who just want to watch TV and change channels and can't even with an LG remote..

## Functions

### TV Button

Put the TV in Live (terrestrial) TV mode. Searches for and pairs TV if necessary. If paired TV is unreachable it attempts to turn it on using its MAC (stored in pairing process).

### Channel Up/Down

If an LG TV is paired and in Live TV mode, it does exactly that.

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

>[!note]
>macOS may ask to allow access to devices on the local network the first time the server runs.
>
>This can happen separately for the terminal app which `uv run server.py` ran in, or for `uv` with `install-launchd.sh`.

Stop the server with Ctrl-C

### Install launch daemon

To install it as a background service that starts on login and restarts itself if it crashes:

```sh
./install-launchd.sh
```

If it stops responding, double-click `restart-launchd.command`.

To remove the background service: `./uninstall-launchd.sh`.

## Logs

`launchd` writes stdout and stderr to `launchd.log` in the project
directory:

```sh
tail -f launchd.log
```
