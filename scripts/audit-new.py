#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


# Imports section
import os
import sys
import pathlib
import argparse
import configparser


def load_config(file_path):
    """Load the audits configuration parameters

    Returns a dictionnary the configurations settings
    """

    # Convert file_path parameter to a Path object
    file_path = pathlib.Path(file_path).expanduser()

    # Check if the configuration file exists
    if not file_path.exists():
        print(f"[-] Unable to find config file {file_path}")
        print(f"[*] Please run the `install.py` script in this project")
        sys.exit(1)
    
    # Create the config parser object
    config = configparser.ConfigParser()
    
    try:
        # Read and load the configuration
        config.read(file_path)
    except Exception as e:
        print(f"[-] Error reading configuration file: {e}")
        sys.exit(1)
    
    # Load the available projects templates
    templates = {}
    for template_name in config['templates']:
        template_dirtree_str = config['templates'][template_name]
        template_dirtree_lst = [x.strip() for x in template_dirtree_str.split(',')]
        templates.update({template_name: template_dirtree_lst})

    # Define the configuration dictionnary to retun
    config = {
        "projects_dir": pathlib.Path(config.get('audits', 'directory')).expanduser(),
        "templates": templates,
    }

    return config


def main():
    """Main function"""
    
    # Load the configuration from file
    config = load_config('~/.local/share/audit-tools/config.ini')

    # Command line parsing
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-l', '--link', action='store', 
        help="Create a symlink to the newly created project")
    parser.add_argument('-t', '--template', action='store',
        help=f"Choose a directory structure for the project, \
        based on templates (available are: {list(config['templates'].keys())})")
    parser.add_argument('name', help="The audit project's name")

    args = parser.parse_args()

    # Create the audit directory
    try:
        project_path = os.path.join(config['projects_dir'], args.name)
        pathlib.Path(project_path).mkdir(parents=True)
        print(f"[+] Directory {project_path} created successfully")
    except Exception as e:
        print(e)
        return 1

    # --template option is set
    if args.template:
        # Check if submitted template exists
        if args.template in config['templates'].keys():
            # For each directory from the template list, create the new dir
            for directory in config['templates'][args.template]:
                new_path = pathlib.Path(project_path) / pathlib.Path(directory)
                new_path.mkdir()
            dir_str = ",".join(config['templates'][args.template])
            print(f"    - {dir_str} created successfully")
        else:
            print(f"[!] Unknown template: {args.template} - delete previously created directories")
            # Delete the project because use might want to reuse same names
            pathlib.Path(project_path).rmdir()
            sys.exit(1)

    # --link option is set
    if args.link:
        # Try creating the symlink
        if pathlib.Path(args.link).exists():
            print(f"[!] Link '{args.link}' already exists")
        else:
            pathlib.Path(args.link).symlink_to(project_path, target_is_directory=True)
            print(f"[+] Link '{args.link}' created successfully")


if __name__ == '__main__':
    main()
    sys.exit(0)