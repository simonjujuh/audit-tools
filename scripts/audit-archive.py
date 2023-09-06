#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Imports section
import os
import sys
import pathlib
import argparse
import configparser
import py7zr
import subprocess


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

    # Define the configuration dictionnary to retun
    config = {
        "projects_dir": pathlib.Path(config.get('audits', 'directory')).expanduser(),
    }

    return config


def main():
    """Main function"""

    # Load the configuration from file
    config = load_config('~/.local/share/audit-tools/config.ini')

    # Command line parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs='+', help="The audit project's name")
    args = parser.parse_args()

    # Iterate over the list of given projects
    for project in args.name:
        
        # Define the project full path
        project_path = config['projects_dir'] / pathlib.Path(project)
        print(f"[*] Working on {project_path}")

        # Ensure project is a real directory
        if project_path.is_dir():
            # Take full ownership of the project directory
            # Get the current user's username
            current_user = os.getlogin()

            # Use the subprocess module to run the chown command with sudo
            command = f"sudo chown {current_user}:{current_user} {project_path}"

            # Try to take full ownership of the project
            # If this fails, do not archive the project
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"[*] Ownership of {project_path} changed to {current_user}")
            except subprocess.CalledProcessError as e:
                print(f"[!] Error: {e}")
            else:
                # Define the name of the output 7z archive file
                output_archive_file = config['projects_dir'] / pathlib.Path(name + ".7z")

                # Create a 7z archive
                with py7zr.SevenZipFile(output_archive_file, 'w') as archive:
                    for file_path in config['projects_dir'].rglob('*'):
                        if file_path.is_file():
                            archive.write(file_path, file_path.relative_to(config['projects_dir']))

                print(f"[+] 7z archive created: {output_archive_file}")
            
        # Otherwise, print an error message
        else:
            print(f"[-] Unknown file or directory: {project_path}")

if __name__ == '__main__':
    main()
    sys.exit(0)
