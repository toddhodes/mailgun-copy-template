
## mailgun-copy-template

Copy a Mailgun email template from one name to another within an account.

Supports listing available template versions and copying a specific version.

### Usage:
 - Install python dependencies
 - Set required environment variables
 - Execute python script

### Environment Variables:
```bash
MG_MAIL_DOMAIN='mg.sample.com'              # Domain name under which existing template exists
MG_API_KEY='xxxxxxxxxx'                     # Mailgun API Key
MG_BASE_URL='https://api.mailgun.net/v3'    # Mailgun API base URL; defaults to https://api.mailgun.net/v3
```

### Command:
```bash
python3 mailgun-copy-template.py [src] [dest] [version_tag]
```
- `[src]`: Name of the source template.
- `[dest]`: Name for the new template.
- `[version_tag]` (optional): Tag of the version to copy from the source template (e.g., `active`, `draft`). If omitted, the script will list available versions and use the first one as default.

### Features:
- Lists available versions for the source template.
- Copies the selected version to the new template name.
- If no version is provided, script will default to the first version.

### Example:
```bash
python3 mailgun-copy-template.py welcome-template welcome-template-copy active
```

If you omit the version tag, available versions for the source template will be displayed, and the default will be used.

