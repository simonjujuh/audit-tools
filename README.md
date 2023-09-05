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
# Create a new workspace named 202309_client_audit
./scripts/audit-new.py 202309_client_audit

# Same as above, and create a symlink to the new engagement
./scripts/audit-new.py --link ~/audit 202309_client_audit
```

### Audit worskapce archive and encryption
...
