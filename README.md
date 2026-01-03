# MADMIN Modules Registry

Official registry of modules available for [MADMIN](https://github.com/EdoardoFiore/VPNManager).

## For Users

Your MADMIN instance automatically fetches this registry to display available modules in the Store.

## For Module Developers

Want to add your module to the store? 

1. Fork this repository
2. Create `modules/<your-module-id>.json` using the template below
3. Open a Pull Request

### Module Template

```json
{
  "id": "my-module",
  "name": "My Module Name",
  "description": "Brief description of what your module does",
  "repository": "https://github.com/username/my-module",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://yourwebsite.com"
  },
  "category": "networking",
  "tags": ["tag1", "tag2"],
  "icon": "tabler-icon-name",
  "features": [
    "Feature 1",
    "Feature 2"
  ],
  "requirements": {
    "os": ["ubuntu-22.04", "debian-12"],
    "min_madmin_version": "2.0.0"
  }
}
```

### Categories

- `networking` - VPN, DNS, firewall, etc.
- `monitoring` - System monitoring, logs, alerts
- `security` - Authentication, encryption, auditing
- `utilities` - Backup, cron, file management
- `other` - Anything else

## Verification

Modules marked with `"verified": true` have been reviewed by the MADMIN team.
