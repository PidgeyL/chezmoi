#!/usr/bin/python3

###
# Actions:
#  1) Create settings file if not exists
#  2) Read settings file and apply settings as such
#

# Imports
import os
import json
import subprocess
import sys
import termios
import tty

_HOME_     = os.getenv("HOME")
_CONF_DIR_ = os.path.join(_HOME_, ".local", "share", "bootstrap")
_CONF_     = os.path.join(_CONF_DIR_, "config.json")

_SETTINGS  = {
                  'bootstrap': {
                      'base': False,
                      'workstation': False,
                      'server': False,
                      'development': False,
                  }
             }

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


def do_bootstrap(text, setting):
    r = confirm(f"[BOOTSTRAP] {text} bootstrap?")
    _SETTINGS['bootstrap'][setting] = r


def interact_settings():
    if os.path.exists(_CONF_):
        return
    do_bootstrap("Base system", 'base')
    do_bootstrap("Workstation", 'workstation')
    do_bootstrap("Server",      'server')
    do_bootstrap("Development", 'development')
    with open(_CONF_, 'w') as f:
        f.write(json.dumps(_SETTINGS))


def read_settings():
    with open(_CONF_, 'r') as f:
        return json.loads(f.read())


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
    interact_settings()
    settings = read_settings()
    bootstrap(settings)
