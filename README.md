# The (HTTP) Clicker

A VERY simple controller for people who just want to watch TV and change channels, and are thwarted by their LG TV.

<img width="224" height="500" alt="iphone-13-mini" src="https://github.com/user-attachments/assets/8d252d97-c817-4f8d-8b20-9327d747fef0" />

## Functions

### TV Button

Puts the TV in Live (terrestrial) TV mode. Searches for TV and initiates pairing if necessary. Wakes the TV if it's asleep.

### Channel Up/Down

Navigates through scanned-in terrestrial channels, avoiding "IP channels"

## Setup

### Requirements

A macOS machine with `uv`. The host Mac must be on the same network as the TV.

To install `uv`:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Smoke test

- Copy or clone this project folder onto the machine.

- `cd` into the project directory and start the server:

```sh
uv run server.py
```

When you see "Uvicorn running on <http://0.0.0.0:8000>", the app should be available on the LAN at `http://{machine name}.local:8000/`.

>[!note]
>macOS may ask to allow access to devices on the local network the first time the server runs.
>
>This should happen separately for the terminal `uv run server.py` ran in, and for `uv` with `install-launchd.sh`.

Stop the server with Ctrl-C

### Install launch daemon

To install the server as a background service:

```sh
./install-launchd.sh
```

To restart:

```sh
./restart-launchd.command
```

To remove: 

```sh
./uninstall-launchd.sh
```

## Logs

`launchd` writes stdout and stderr to `launchd.log` in the project
directory:

```sh
tail -f launchd.log
```
