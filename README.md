# Pentest Engagement Scripts
A set of useful tools dedicated to manage your pentest engagements more easily.

## Installation
Run the installation script
```bash
pip3 install -r requirements.txt
python3 install.py
```

Then **edit the generated configuration file**.

## Use cases
### Audit workspace creation
```bash
# Create a new audit project
./scripts/audit-new.py project_name
# Create a new audit project with symlink to project
./scripts/audit-new.py --link ~/audit project_name
# Create a new audit project with a template directory tree
./scripts/audit-new.py --template pentest project_name
```

### Audit worskapce archive and encryption
```bash
# Create a 7z archive in the projects base directory
./scripts/audit-archive.py /path/to/project_1 ../path/to/project_2
# Create a 7z encrypted archive; password in stored in your configured keepass DB
./scripts/audit-new.py --encrypt /path/to/project_1
# Same as above but delete the project directory
./scripts/audit-new.py --encrypt --delete-directory /path/to/project_1
```

### Useful aliases
```bash
alias anew='/path/to/scripts/audit-new.py'
alias aarch='/path/to/scripts/audit-archive.py'
```