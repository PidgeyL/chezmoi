#!/usr/bin/env python3
import argparse
import os
import json
import subprocess
import sys

_HOME_     = os.getenv("HOME")
_CONF_DIR_ = os.path.join(_HOME_, ".local", "share", "bootstrap")
_CONF_     = os.path.join(_CONF_DIR_, "config.json")

# Helper functions

def read_settings():
    try:
        with open(_CONF_, 'r') as f:
            return json.loads(f.read())
    except Exception as e:
        sys.exit(f"Could not read the config file!\n{e}")

def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return ""

def get_connected_displays():
    dir = '/sys/class/drm'
    connected = [dev for dev in os.listdir(dir)
                   if read_file( os.path.join(dir, dev, 'status') ) == "connected\n"]
    return [dev.split("-", 1)[1] for dev in connected if dev.startswith("card") and "-" in dev]

def get_active_screen_config():
    settings  = read_settings()
    connected = set(get_connected_displays())
    for config in settings.get('output',{}).get('screen_configs', []):
        if set([x['name'] for x in config]) == connected:
            return config
    return None



# Bootstrap functions

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

def screens(desktop):
    if not desktop:
        print("Desktop Environment not specified"); return
    desktop = desktop.lower()
    config = get_active_screen_config()
    if not config:
        print("No config specified")
        return
    for screen in config:
        n, x, y, s = screen['name'], screen['pos_x'], screen['pos_y'], screen['scale']
        if desktop == "sway":
            subprocess.run(f"swaymsg 'output {n} pos {x} {y} scale {s}'", shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script to handle various setups.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Bootstrap command
    p_bootstrap = subparsers.add_parser("bootstrap", help="Run the bootstrap setup")
    p_bootstrap.add_argument("desktop", nargs="?", default=None, help="Specify the desktop used")
    p_bootstrap.set_defaults(func=bootstrap)

    # Keyboard command
    p_keyboard = subparsers.add_parser("keyboard", help="Set the keyboard layout")
    p_keyboard.add_argument("desktop", nargs="?", default=None, help="Specify the desktop used")
    p_keyboard.set_defaults(func=keyboard)

    # Screens command
    p_screens = subparsers.add_parser("screens", help="Set the screen layout")
    p_screens.add_argument("desktop", nargs="?", default=None, help="Specify the desktop used")
    p_screens.set_defaults(func=screens)

    args = parser.parse_args()
    args.func(args.desktop)
