#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import os
import sys
import pathlib
import argparse
import configparser


config_path = pathlib.Path('~/.local/share/audit-tools/config.ini').expanduser()
projects_base_dir = None
templates = {}

def load_config():
    global projects_base_dir
    global templates

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

    # load the base directory for audits projects
    projects_base_dir = pathlib.Path(config.get('audits', 'directory')).expanduser()
    # load the available projects templates
    for template_name in config['templates']:
        template_dirtree_str = config['templates'][template_name]
        template_dirtree_lst = [x.strip() for x in template_dirtree_str.split(',')]
        templates.update({template_name: template_dirtree_lst})


def main():
    """Main function"""
    load_config()
    template_names = list(templates.keys())

    # Command line parsing
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-l', '--link', action='store', 
        help="Create a symlink to the newly created project")
    parser.add_argument('-t', '--template', action='store',
        help=f"Choose a directory structure for the project, \
        based on templates (available are: {template_names})")
    parser.add_argument('name', help="The audit project's name")

    args = parser.parse_args()

    # Create the audit directory
    try:
        new_project_path = os.path.join(projects_base_dir, args.name)
        pathlib.Path(new_project_path).mkdir(parents=True)
    except Exception as e:
        print(e)
        return 1

    if args.link:
        # Try creating the symlink
        if pathlib.Path(args.link).exists():
            print(f"[-] Link '{args.link}' already exists")
            pathlib.Path(new_project_path).rmdir()
            sys.exit(1)
        else:
            pathlib.Path(args.link).symlink_to(new_project_path, target_is_directory=True)
            print(f"[+] Link '{args.link}' created successfully")

    if args.template:
        if args.template in template_names:
            for directory in templates[args.template]:
                new_path = pathlib.Path(new_project_path) / pathlib.Path(directory)
                new_path.mkdir()
        else:
            print(f"[-] Unknown template: {args.template}")
            pathlib.Path(new_project_path).rmdir()
            sys.exit(1)


if __name__ == '__main__':
    main()
    sys.exit(0)