---
name: deploy
description: Deploy PM Claw to the Hetzner server via SSH. Clones/updates repo, installs deps, and restarts the systemd service.
allowed-tools: Bash(source:*), Bash(bash:*)
---
Deploy PM Claw to the production server:

1. Run: `source .env && DEPLOY_SERVER=$DEPLOY_SERVER bash deploy.sh`
2. Show the output to the user
3. Report result:
   - ✅ Deploy successful — if the script exits with code 0
   - ❌ Deploy failed — if the script exits with non-zero code, show the error and suggest fixes
