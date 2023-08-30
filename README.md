# Pentest Engagement Scripts
A set of useful tools dedicated to manage your pentest engagements more easily.

## Installation
Add you new configuration
```bash
# Copy the sample configuration file
cp engagements.conf.sample engagements.conf
# Edit your configuration based on your needs
vim engagements.conf
...
# Run the installation
make
```

## Scenarios
### Workspace creation
```bash
wsnew.py 202309_client_audit # Create a new workspace named 202309_client_audit in the engagement directories
wsnew.py --link ~/audit 202309_client_audit # Same as above, and create a symlink to the new engagement
```