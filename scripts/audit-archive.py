#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


import os
import sys
import pathlib
import argparse
import configparser
import py7zr
import subprocess
import shutil
import secrets
import getpass
from pykeepass import PyKeePass


class bcolor:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_info(message):
    print(f"{bcolor.BOLD}{bcolor.BLUE}[*]{bcolor.END} {message}")


def print_success(message):
    print(f"{bcolor.BOLD}{bcolor.GREEN}[+]{bcolor.END} {message}")


def print_error(message):
    print(f"{bcolor.BOLD}{bcolor.RED}[-]{bcolor.END} {message}")


def print_warning(message):
    print(f"{bcolor.BOLD}{bcolor.YELLOW}[!]{bcolor.END} {message}")


def load_config(file_path):
    """Load the configuration from `file_path`"""

    # Convert file_path parameter to a Path object
    file_path = pathlib.Path(file_path).expanduser()

    # Check if the configuration file exists
    if not file_path.exists():
        print_error(f"Unable to find config file {file_path}")
        print_info("Please run the `install.py` script in this project")
        sys.exit(1)

    # Create the config parser object
    config = configparser.ConfigParser()

    try:
        # Read and load the configuration
        config.read(file_path)
    except Exception as e:
        print_error(f"Error reading configuration file: {e}")
        sys.exit(1)

    # Returns a path if keepass_kdbx is configured, otherwise make it None
    keepass_db = pathlib.Path(
            config.get('encryption', 'keepass_kdbx')
        ).expanduser() if config.get('encryption', 'keepass_kdbx') else None
    keepass_keyfile = pathlib.Path(
            config.get('encryption', 'keepass_key')
        ).expanduser() if config.get('encryption', 'keepass_key') else None

    # Define the configuration dictionnary to retun
    config = {
        "projects_dir": pathlib.Path(config.get('audits', 'directory')
                                     ).expanduser(),
        "keepass_db": keepass_db,
        "keepass_keyfile": keepass_keyfile,
    }

    return config


def open_kdbx(keepass_db, keepass_key=None):
    # 0. Prompt for password
    prompt = f"{bcolor.BOLD}{bcolor.PURPLE}[~]{bcolor.END} Enter your keepass password: "
    password = getpass.getpass(prompt)

    # 1. Check if the keepass db is a real file
    if keepass_db.is_file():

        # 2. If the keyfile is configured, ensure it is a real file
        if keepass_key and not keepass_key.is_file():
            print_error(f"Keepass Database '{keepass_key}' not found")
            sys.exit(1)

        # 3. Open the keepass database
        try:
            kpcon = PyKeePass(keepass_db,
                              password=password,
                              keyfile=keepass_key)
        except Exception as e:
            print_error(f"Error opening the keepass database: {e}")
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
    parser = argparse.ArgumentParser(
        description="Utility to archive and encrypt your project directory")
    parser.add_argument('path',
                        nargs='+',
                        help="The audit project's path")
    parser.add_argument('-e', '--encrypt',
                        action='store_true',
                        help="Enable encryption on the selected projects")
    parser.add_argument('-d', '--delete-directory',
                        action='store_true',
                        help="Delete the archive original directory")
    args = parser.parse_args()

    # If encryption option is set
    if args.encrypt:
        kpcon = open_kdbx(config['keepass_db'], config['keepass_keyfile'])

        # Ensure the password storing group is available in the keepass
        # NOTE the case where multiple groups are found will not occurs
        # due to first=true
        group_name = "Audits"
        group_found = kpcon.find_groups(name=group_name, first=True)
        # Case where the group does not exists; then create it
        if not group_found:
            kpcon.add_group(kpcon.root_group, group_name)
            kpcon.save()
            print_info(f"Group {group_name} created in keepass database")

    # Iterate over the list of given projects
    for project_path in args.path:

        # Define the project full path
        project_path = pathlib.Path(project_path)
        print_info(f"Archiving target project: '{project_path.name}'")

        # Ensure project is a real directory
        if not project_path.is_dir():
            print_warning(f"Unknown file or directory: {project_path}")
            continue

        # Take full ownership of the project directory
        # Get the current user's username
        current_user = os.getlogin()

        # Use the subprocess module to run the chown command with sudo
        cmd = f"sudo chown -R {current_user}:{current_user} {project_path}"

        # Try to take full ownership of the project
        # If this fails, do not archive the project
        try:
            subprocess.run(cmd, shell=True, check=True)
            print_info(f"Ownership changed to '{current_user}'")
        except subprocess.CalledProcessError as e:
            print_error(f"Error: {e}")
            continue

        # Define the name of the output 7z archive file
        # projects base directory / basename of the project_path + 7z
        archive_basename = pathlib.Path(project_path).with_suffix('.7z').name
        archive_file_fullpath = config['projects_dir'] / archive_basename
        archive_password = None
        # Fail safe to not delete the project directory if the keepass update
        # fails
        archive_success = False

        # If encryption is selected
        if args.encrypt:
            # Set the desired length of the password
            # You can change this to your preferred length
            length = 25

            # Generate a random password
            archive_password = secrets.token_hex(length // 2)[:length]

        # Create a 7z archive
        with py7zr.SevenZipFile(archive_file_fullpath,
                                'w',
                                password=archive_password) as archive:
            # Get all files from the project
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    archive.write(file_path)

        if args.encrypt:
            # Search the entry in keepass
            entry = kpcon.find_entries(title=archive_basename, first=True)

            # If the entry already exists
            if entry:
                print_warning(f"Entry '{archive_basename}' already exists,")
                print_info("Saving the current entry password in history")
                # Add current password to history
                entry.save_history()
                entry.password = archive_password

            # Otherwise add entry
            else:
                kpcon.add_entry(group_found, archive_basename,
                                "encrypted archive",
                                archive_password)

            # Save changes to the database
            try:
                print_info("Updating keepass database")
                kpcon.save()
            except Exception as e:
                print_error(f"Error while updating database: {e}")
                print_info("Remove the encrypted archive created")
                archive_file_fullpath.unlink()
            else:
                archive_success = True

        if archive_success:
            if args.delete_directory:
                print_info(f"Deleted source directory '{project_path.name}'")
                shutil.rmtree(project_path)
            
            print_success(f"Archive created: {archive_file_fullpath}")


if __name__ == '__main__':
    main()
    sys.exit(0)
