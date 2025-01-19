#!/usr/bin/python3

###
# Actions:
#  1) Create settings file if not exists
#  2) Read settings file and apply settings as such
#

# Imports
import copy
import os
import json
import subprocess
import sys
import termios
import tty

_HOME_     = os.getenv("HOME")
_CONF_DIR_ = os.path.join(_HOME_, ".local", "share", "bootstrap")
_CONF_     = os.path.join(_CONF_DIR_, "config.json")

_PLAYBOOKS = [("Base system",  'base'),
              ("Workstation",  'workstation'),
              ("Server",       'server'),
              ("Development",  'development'),
              ("Work Desktop", 'work')]

_SETTINGS  = {
                  'bootstrap': { i[1]: None for i in _PLAYBOOKS },
                  'input': {
                      'keyboard': None},
                  'output': {
                      'screen_configs': []
                  }
             }

_SCREEN = {key: None for key in ['name', 'pos_x', 'pos_y', 'scale']}

#####
# Helper Functions

def confirm(text):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        print(f"{text} [Y/N]")
        tty.setraw(fd)
        while True:
            key = sys.stdin.read(1)
            if key.lower() in ["y", "n"]:
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key.lower() == "y"


def deep_update(original, update):
    for key, value in update.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            deep_update(original[key], value)
        else:
            original[key] = value

def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return ""

#####
# Bootstrap functions

def do_bootstrap(text, setting):
    r = confirm(f"[BOOTSTRAP] {text} bootstrap?")

def get_connected_displays():
        dir = '/sys/class/drm'
        connected = [dev for dev in os.listdir(dir)
                         if read_file( os.path.join(dir, dev, 'status') ) == "connected\n"]
        return [dev.split("-", 1)[1] for dev in connected if dev.startswith("card") and "-" in dev]


def interact_settings(settings):
    # Set playbooks
    for desc, playbook in _PLAYBOOKS:
        if not settings['bootstrap'][playbook] == None:  # The variable has been set
            continue
        settings['bootstrap'][playbook] = confirm(f"[BOOTSTRAP] {desc} bootstrap?")
    # Set keyboard
    if not settings['input']['keyboard']:
        code = input("[SETTINGS] Preferred keyboard layout code: ")
        settings['input']['keyboard'] = code
    # Set displays
    connected = set(get_connected_displays())
    current_config_known = False
    for config in settings['output']['screen_configs']:
        if set([x['name'] for x in config]) == connected:
            current_config_known = True
            break
    if current_config_known == False:
        if confirm("[SETTINGS] Current screen-set-up has no config. Make one now?"):
            conf = []
            for screen in connected:
                print(f" == Screen: {screen} ==")
                s = copy.deepcopy(_SCREEN)
                s['name'] = screen
                for key in [k for k in _SCREEN.keys() if k != "name"]:
                    s[key] = input(f"{key}: ")
                conf.append(s)
            settings['output']['screen_configs'].append(conf)
    # Save config
    with open(_CONF_, 'w') as f:
        f.write(json.dumps(settings, indent=2))


def read_settings():
    settings = copy.deepcopy(_SETTINGS)
    if not os.path.exists(_CONF_):
        print("No settings file found... Generating a new one.")
    with open(_CONF_, 'r') as f:
        deep_update(settings, json.loads(f.read()))
        return settings


def bootstrap(settings):
    if not confirm("Do bootstrap now?"):
        return
    for key, enabled in settings['bootstrap'].items():
        if not enabled:
            continue
        file = os.path.join(_CONF_DIR_, key+".yml")
        if not os.path.exists(file):
            print(f"[Bootstrap] ERR: Couldn't find {file}")
            continue
        subprocess.run(['ansible-playbook', file, "--ask-become-pass"], check=True)

if __name__ == "__main__":
    settings = read_settings()
    interact_settings(settings)
    bootstrap(settings)
