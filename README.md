# The (HTTP) Clicker

A very simple LG TV controller, for those whose ability watch TV (as one does) is thwarted by the WTF of the LG TV UI.

<img width="250" height="420" alt="BD_4_FE_2_A6_74_C6_43_D6_9_AAE_A778_C793_DF_7_E" src="https://github.com/user-attachments/assets/ed1ef83a-04b7-4c82-ac7b-7e02a33787e2" />

## Functions

### TV Button

Puts the TV in Live (terrestrial) TV mode, using SDDP discovery to initiate pairing if necessary. Once paired, wakes the TV if it's asleep.

### Channel Up/Down

Cycles through scanned terrestrial channels, avoiding "IP channels"

## Setup

### Requirements

- An LG TV (tested on LR600BZUC / webOS 8.5)
- A macOS machine with `uv`. The host Mac must be on the same network as the TV.

The TV needs the following enabled:

- SDDP
- Network IP Control
- Wake on LAN (WoL)

Menu paths may vary. On webOS 8.5 I found them via **Settings** -> **Support** -> **IP Control Settings**

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
>This should happen separately for the terminal `uv run server.py` ran in, and for `uv` itself with `install-launchd.sh`.

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
