#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import os
import sys
import pathlib
import argparse
import configparser
import py7zr
import subprocess
import secrets
import getpass
from pykeepass import PyKeePass


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

    # Returns a path if keepass_kdbx is configured, otherwise make it None
    keepass_db = pathlib.Path(config.get('encryption', 'keepass_kdbx')).expanduser() if config.get('encryption', 'keepass_kdbx') else None
    keepass_keyfile = pathlib.Path(config.get('encryption', 'keepass_key')).expanduser() if config.get('encryption', 'keepass_key') else None

    # Define the configuration dictionnary to retun
    config = {
        "projects_dir": pathlib.Path(config.get('audits', 'directory')).expanduser(),
        "keepass_db": keepass_db,
        "keepass_keyfile": keepass_keyfile,
    }

    return config


def open_kdbx(keepass_db, keepass_key=None):
    # 0. Prompt for password
    password = getpass.getpass("[+] Enter your keepass password: ")

    # 1. Check if the keepass db is a real file
    if keepass_db.is_file():

        # 2. If the keyfile is configured, ensure it is a real file
        if keepass_key and not keepass_key.is_file():
            print(f"[!] Keepass Database '{keepass_key}' not found")
            sys.exit(1)

        # 3. Open the keepass database
        try:
            kpcon = PyKeePass(keepass_db, password=password, keyfile=keepass_key)
        except Exception as e:
            print(f"[!] Error opening the keepass database: {e}")
            sys.exit(1)
        return kpcon
    else:
        print(f"[!] Keepass Database '{keepass_db}' not found")
        sys.exit(1)


def main():
    """Main function"""

    # Load the configuration from file
    config = load_config('~/.local/share/audit-tools/config.ini')

    # Command line parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='+', help="The audit project's path")
    parser.add_argument('-e', '--encrypt', action='store_true', help="Enable encryption on the selected projects")
    args = parser.parse_args()

    # If encryption option is set
    if args.encrypt:
        kpcon = open_kdbx(config['keepass_db'], config['keepass_keyfile'])

        # Ensure the password storing group is available in the keepass
        # NOTE the case where multiple groups are found will not occurs due to first=true
        group_name = "Audits"
        group_found = kpcon.find_groups(name=group_name, first=True)
        # Case where the group does not exists; then create it
        if not group_found:
            kpcon.add_group(kpcon.root_group, group_name)
            kpcon.save()
            print(f"[+] Group {group_name} created in keepass database")

    # Iterate over the list of given projects
    for project_path in args.path:
        
        # Define the project full path
        project_path = pathlib.Path(project_path)

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
                print(f"[*] Ownership of project '{project_path}' changed to '{current_user}'")
            except subprocess.CalledProcessError as e:
                print(f"[!] Error: {e}")
                continue

            # Define the name of the output 7z archive file
            # projects base directory / basename of the project_path + 7z
            archive_basename = pathlib.Path(project_path).with_suffix('.7z').name
            archive_file_fullpath = config['projects_dir'] / archive_basename

            # If encryption is set
            if args.encrypt:
                
                # Check if there is no entry for the current project
                if kpcon.find_entries_by_username(archive_basename):
                    print("Entry already exists, pass")
                else:

                    # Set the desired length of the password
                    password_length = 25  # You can change this to your preferred length

                    # Generate a random password
                    random_password = secrets.token_hex(password_length // 2)[:password_length]
                    
                    # Create a 7z archive
                    with py7zr.SevenZipFile(archive_file_fullpath, 'w', password=random_password) as archive:
                        for file_path in project_path.rglob('*'):
                            if file_path.is_file():
                                archive.write(file_path, file_path.relative_to(config['projects_dir']))
                    print(f"[*] 7z archive created: {archive_file_fullpath}")
                    # Add this password to keepass
                    try:
                        # kpcon.add_entry(group_found, archive_basename, archive_file_fullpath.as_posix(), random_password)
                        kpcon.add_entry(group_found, archive_basename, "encrypted archive", random_password)
                        kpcon.save()

                    except Exception as e:
                        print(f"[-] Error while adding entry: {e}")

            # If encryption is not set, simply create an archive
            else:       
                # Create a 7z archive
                with py7zr.SevenZipFile(archive_file_fullpath, 'w') as archive:
                    for file_path in project_path.rglob('*'):
                        if file_path.is_file():
                            archive.write(file_path, file_path.relative_to(config['projects_dir']))
            
                print(f"[*] 7z archive created: {archive_file_fullpath}")

        # Otherwise, print an error message
        else:
            print(f"[-] Unknown file or directory: {project_path}")

if __name__ == '__main__':
    main()
    sys.exit(0)
