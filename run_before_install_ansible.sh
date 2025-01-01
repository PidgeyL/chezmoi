#!/bin/bash

install_on_fedora() {
    sudo dnf install -y ansible
}

install_on_ubuntu() {
    sudo apt-get update
    sudo apt-get install -y ansible
}


if ! command -v ansible-playbook 2>&1 >/dev/null
then
    OS="$(uname -s)"
    case "${OS}" in
        Linux*)
            if [ -f /etc/fedora-release ]; then
                install_on_fedora
            elif [ -f /etc/lsb-release ]; then
                install_on_ubuntu
            else
                echo "Unsupported Linux distribution"
                exit 1
            fi
            ;;
        *)
            echo "Unsupported operating system: ${OS}"
            exit 1
            ;;
    esac
    echo "Ansible installation complete."
fi
