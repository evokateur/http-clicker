"""Forget the locally stored TV pairing and wake state."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lgtv


def main():
    if not lgtv.STATE_FILE.exists():
        print("No local TV state to clear.")
        return

    lgtv.STATE_FILE.unlink()
    print(f"Forgot TV state from {lgtv.STATE_FILE}.")


if __name__ == "__main__":
    main()
