#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import os
import sys
import pathlib
import argparse
import configparser


config_path = pathlib.Path('~/.local/share/engagements.conf').expanduser()
engagements_dir = None


def load_config():
    global engagements_dir

    # Check if the configuration file exists
    if not config_path.exists():
        print(f"[-] Unable to find config file {config_path}")
        print(f"[*] Please run the `make` command in the engagement-scripts project")
        sys.exit(1)
    
    # Read and load the configuration
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
    except Exception as e:
        print(f"[-] Error reading configuration file: {e}")
        sys.exit(1)

    # Load the variables 
    engagements_dir = pathlib.Path(config.get('engagements', 'directory')).expanduser()


def main():
    """Main function"""
    load_config()

    # Command line parsing
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-l', '--link', action='store', 
        help="Create a symlink to the newly created project")
    parser.add_argument('engagement_name')

    args = parser.parse_args()

    # Create the engagement directory
    try:
        new_engagement_path = os.path.join(engagements_dir, args.engagement_name)
        os.mkdir(pathlib.Path(new_engagement_path))
    except Exception as e:
        print(e)
    else:
        if args.link:
            # Try creating the symlink
            if pathlib.Path(args.link).exists():
                print(f"[-] Link '{args.link}' already exists")
                os.rmdir(new_engagement_path)
                sys.exit(1)
            else:
                pathlib.Path(args.link).symlink_to(new_engagement_path, target_is_directory=True)
                print(f"[+] Link '{args.link}' created successfully")
        

if __name__ == '__main__':
    main()
    sys.exit(0)