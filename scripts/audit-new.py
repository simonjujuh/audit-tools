#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import os
import sys
import pathlib
import argparse
import configparser


config_path = pathlib.Path('~/.local/share/audit-tools/config.ini').expanduser()
projects_basedir = None
project_dirtree = {}


def load_config():
    global projects_basedir

    # Check if the configuration file exists
    if not config_path.exists():
        print(f"[-] Unable to find config file {config_path}")
        print(f"[*] Please run the `install.py` script in this project")
        sys.exit(1)
    
    # Read and load the configuration
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
    except Exception as e:
        print(f"[-] Error reading configuration file: {e}")
        sys.exit(1)

    # Load the variables 
    projects_basedir = pathlib.Path(config.get('audits', 'directory')).expanduser()


def main():
    """Main function"""
    load_config()

    # Command line parsing
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-l', '--link', action='store', 
        help="Create a symlink to the newly created project")
    # parser.add_argument('-t', '--template', action='store',
    #     help="Choose a directory structure for the project, based on templates (available are:)")
    parser.add_argument('name')

    args = parser.parse_args()

    # Create the audit directory
    try:
        new_project_path = os.path.join(projects_basedir, args.name)
        os.mkdir(pathlib.Path(new_project_path))
    except Exception as e:
        print(e)
    else:
        if args.link:
            # Try creating the symlink
            if pathlib.Path(args.link).exists():
                print(f"[-] Link '{args.link}' already exists")
                os.rmdir(new_project_path)
                sys.exit(1)
            else:
                pathlib.Path(args.link).symlink_to(new_project_path, target_is_directory=True)
                print(f"[+] Link '{args.link}' created successfully")
    
    # TODO: Create the project directory tree


if __name__ == '__main__':
    main()
    sys.exit(0)