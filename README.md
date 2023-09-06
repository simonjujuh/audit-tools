# Pentest Engagement Scripts
A set of useful tools dedicated to manage your pentest engagements more easily.

## Installation
Run the installation script
```bash
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
...

### Useful aliases
```bash
alias anew='/path/to/scripts/audit-new.py'
alias aarch='/path/to/scripts/audit-archive.py'
```