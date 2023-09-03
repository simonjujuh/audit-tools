#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import configparser

# Get the directory of the currently running script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the configuration template path
template_path = script_dir + '/config/config_template.ini'

# Define the destination path for the configuration
config_path = os.path.expanduser('~/.local/share/audit-tools/config.ini')

def install_config(template_path, config_path):
    # Check if the configuration template exists
    if not os.path.isfile(template_path):
        print(f"[-] File not found: '{template_path}'")
        return

    # Create the configparser object
    config = configparser.ConfigParser()

    # Load the configuration from template
    config.read(template_path)

    # Create parents directories if necessary
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Create the destination configuration file
    with open(config_path, 'w') as config_file:
        config.write(config_file)

    print(f"[+] '{config_path}' installed successfully")
    print(f"[*] Please edit the above file with your desired parameters")

if __name__ == "__main__":
    install_config(template_path, config_path)
