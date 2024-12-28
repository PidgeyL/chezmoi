#!/usr/bin/env python3
import argparse
import os
import json
import subprocess

_HOME_     = os.getenv("HOME")
_CONF_DIR_ = os.path.join(_HOME_, ".local", "share", "bootstrap")
_CONF_     = os.path.join(_CONF_DIR_, "config.json")

def read_settings():
    with open(_CONF_, 'r') as f:
        return json.loads(f.read())

def bootstrap(desktop):
    print("Running bootstrap...")

def keyboard(desktop):
    if not desktop:
        print("Desktop Environment not specified"); return
    desktop  = desktop.lower()
    settings = read_settings()
    layout   = settings.get('input', {}).get('keyboard')
    if not layout:
        print("Layout not specified in config"); return
    if desktop == "sway":
        subprocess.run(["swaymsg", "input", "type:keyboard", "xkb_layout", f'"{layout}"'], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to handle various setups.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Bootstrap command
    parser_bootstrap = subparsers.add_parser("bootstrap", help="Run the bootstrap setup")
    parser_bootstrap.add_argument("extra_arg", nargs="?", default=None, help="Optional extra argument for bootstrap")
    parser_bootstrap.set_defaults(func=bootstrap)

    # Keyboard command
    parser_keyboard = subparsers.add_parser("keyboard", help="Configure the keyboard")
    parser_keyboard.add_argument("extra_arg", nargs="?", default=None, help="Optional extra argument for keyboard")
    parser_keyboard.set_defaults(func=keyboard)

    args = parser.parse_args()
    args.func(args.extra_arg)
