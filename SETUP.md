# Setup Guide

Step-by-step setup for the vault across all devices. Prerequisites: [Tailscale](https://tailscale.com/) installed and connected on all devices.

## 1. Remote Hub (headless Linux, always-on)

The remote hub is the authoritative copy. It runs Syncthing as an always-on relay, git for version history, and a systemd timer for automated backup to GitHub.

### 1.1 Syncthing

```bash
sudo pacman -S syncthing
sudo systemctl enable --now syncthing@$USER.service
```

Add the vault folder and harden for Tailscale-only sync:

```bash
# Add vault folder
syncthing cli config folders add --id vault --path ~/vault --label vault

# Restrict listener to Tailscale IP only
syncthing cli config options raw-listen-addresses 0 set tcp://<tailscale-ip>:22000

# Disable NAT traversal, relays, and discovery (all traffic stays on Tailscale mesh)
syncthing cli config options natenabled set false
syncthing cli config options global-ann-enabled set false
syncthing cli config options local-ann-enabled set false
syncthing cli config options relays-enabled set false
```

Note the device ID for pairing other devices:

```bash
syncthing cli show system | python3 -c "import sys,json; print(json.load(sys.stdin)['myID'])"
```

Accept devices from other machines as they connect:

```bash
# Check for pending devices
syncthing cli show pending devices

# Accept a device
syncthing cli config devices add --device-id <device-id> --name <name> --addresses tcp://<device-tailscale-ip>:22000

# Share vault folder with the device
syncthing cli config folders vault devices add --device-id <device-id>
```

Optionally configure via SSH tunnel from a local machine:

```bash
ssh -L 8384:127.0.0.1:8384 <user>@<tailscale-ip>
# Open http://127.0.0.1:8384 in browser for GUI configuration
```

### 1.2 Git-crypt

git-crypt encrypts file contents in git objects. Encryption rules are defined in `.gitattributes`:

```text
0-daily/** filter=git-crypt diff=git-crypt
1-fleeting/** filter=git-crypt diff=git-crypt
2-literature/** filter=git-crypt diff=git-crypt
3-permanent/** filter=git-crypt diff=git-crypt
4-writing/** filter=git-crypt diff=git-crypt
5-projects/** filter=git-crypt diff=git-crypt
6-meetings/** filter=git-crypt diff=git-crypt
7-index/** filter=git-crypt diff=git-crypt
9-assets/** filter=git-crypt diff=git-crypt
```

Adding a new content directory requires adding a rule to `.gitattributes`. The post-commit hook derives content directories from these same rules for public template sync.

```bash
sudo pacman -S git-crypt
cd ~/vault && git-crypt init
git-crypt export-key ~/vault-git-crypt.key
```

Copy the key to a secure location. The key is raw binary (not human-readable text). Store it as a **file attachment** in a password manager. Then delete the local copy:

```bash
scp ~/vault-git-crypt.key <user>@<tailscale-ip>:~/Downloads/
rm ~/vault-git-crypt.key
```

### 1.3 Git-remote-gcrypt

git-remote-gcrypt encrypts the entire repository on the remote, including filenames and directory structure. This prevents note titles from being visible on GitHub.

#### Install

```bash
yay -S git-remote-gcrypt
```

#### GPG key

Generate a dedicated GPG key for unattended encrypted backup. No passphrase (required for systemd timer):

```bash
gpg --batch --gen-key <<'EOF'
Key-Type: EdDSA
Key-Curve: ed25519
Name-Real: vault-backup
Name-Email: vault-backup@noreply
Expire-Date: 0
%no-protection
%commit
EOF

gpg --quick-add-key $(gpg --list-keys --with-colons vault-backup@noreply \
  | awk -F: '/^fpr:/{print $10; exit}') cv25519 encr never
```

Record the fingerprint:

```bash
gpg --list-keys --keyid-format long vault-backup@noreply
```

If GPG prompts for a passphrase during subkey creation, change it to empty afterward:

```bash
gpg --change-passphrase vault-backup@noreply
```

#### GPG headless configuration

Configure GPG for unattended operation (no terminal required). gpg-agent invokes pinentry even for no-passphrase keys; `pinentry-null` provides a headless pinentry that returns an empty passphrase automatically.

Create `~/.local/bin/pinentry-null`:

```bash
#!/bin/sh
echo "OK Pleased to meet you"
while IFS= read -r cmd; do
  case "$cmd" in
    GETPIN) echo "D "; echo "OK" ;;
    BYE)    echo "OK closing connection"; exit 0 ;;
    *)      echo "OK" ;;
  esac
done
```

```bash
chmod +x ~/.local/bin/pinentry-null
```

`~/.gnupg/gpg-agent.conf`:

```ini
pinentry-program /home/<user>/.local/bin/pinentry-null
```

Restart the agent:

```bash
gpgconf --kill gpg-agent
```

Verify headless decryption works:

```bash
echo "test" | gpg --no-tty -e -r vault-backup@noreply | gpg --no-tty -d
```

#### Backup GPG key material

Export and store securely (same location as git-crypt key):

```bash
gpg --export --armor vault-backup@noreply > ~/vault-backup-public.asc
gpg --export-secret-keys --armor vault-backup@noreply > ~/vault-backup-private.asc
cp ~/.gnupg/openpgp-revocs.d/<fingerprint>.rev ~/vault-backup-revocation.asc
scp ~/vault-backup-public.asc ~/vault-backup-private.asc ~/vault-backup-revocation.asc \
  <user>@<tailscale-ip>:~/Downloads/
rm ~/vault-backup-public.asc ~/vault-backup-private.asc ~/vault-backup-revocation.asc
```

Also record the GPG fingerprint and key ID alongside the key files.

#### Configure remote

```bash
cd ~/vault
git remote set-url origin "gcrypt::git@github.com:<owner>/<repo>.git#main"
git config gcrypt.participants "<GPG-FINGERPRINT>"
git config gcrypt.signingkey "<GPG-FINGERPRINT>"
git config gcrypt.gpg-args "--no-tty"
```

If the target branch already exists with plain git data, delete it on GitHub first. gcrypt does not fully replace an existing branch; it may merge old tree data with encrypted blobs, leaving filenames visible. Push only to a fresh or empty branch:

```bash
# If the branch already has plain git data, delete it on GitHub first:
# gh api repos/<owner>/<repo>/git/refs/heads/main -X DELETE

git push origin main
```

Record the gcrypt remote ID shown in the output (`:id:...`).

#### Performance note

git-remote-gcrypt re-encrypts and re-uploads the full repository on every push (git backend limitation). This is acceptable for a small vault. If the vault grows substantially (primarily from `9-assets/`), push duration will increase. Monitor with `du -sh .git/` periodically. If push times become problematic, this is a broader backup-architecture decision, not a drop-in backend swap.

### 1.4 Deploy Key

Generate a dedicated SSH key (no passphrase) for unattended push:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vault-deploy-key -N "" -C "vault-autocommit"
cd ~/vault && git config core.sshCommand "ssh -i ~/.ssh/vault-deploy-key -o IdentitiesOnly=yes"
gh repo deploy-key add ~/.ssh/vault-deploy-key.pub --repo <owner>/<repo> --title "vault-autocommit" --allow-write
```

Verify push works without passphrase prompt:

```bash
cd ~/vault && git push --dry-run origin main
```

### 1.5 Auto-commit Timer

Enable user linger so the timer persists across SSH logout:

```bash
sudo loginctl enable-linger $USER
```

Create the systemd units:

```bash
mkdir -p ~/.config/systemd/user
```

`~/.config/systemd/user/vault-autocommit.service`:

```ini
[Unit]
Description=Auto-commit vault changes to git

[Service]
Type=oneshot
WorkingDirectory=%h/vault
ExecStart=/bin/bash -c '\
  git add -A && \
  if ! git diff --cached --quiet; then \
    git commit -m "auto: $(date +%%FT%%T)"; \
    git push --quiet origin main 2>/dev/null || true; \
  fi'
```

`~/.config/systemd/user/vault-autocommit.timer`:

```ini
[Unit]
Description=Auto-commit vault every hour

[Timer]
OnCalendar=*:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable the timer:

```bash
systemctl --user daemon-reload
systemctl --user enable --now vault-autocommit.timer
```

Verify:

```bash
systemctl --user list-timers vault-autocommit.timer
systemctl --user start vault-autocommit.service
journalctl --user -u vault-autocommit.service -n 10
```

### 1.6 Public Template Sync

A public repo ([vault-template](https://github.com/peregrinus879/vault-template)) mirrors the vault's structure, templates, config, and docs. Note content is not synced. A git post-commit hook handles this automatically after every commit.

#### Install rsync

```bash
sudo pacman -S rsync
```

#### Clone the public repo

```bash
cd ~/projects/repos/templates
git clone git@github.com:<owner>/vault-template.git
```

#### Deploy key

Generate a dedicated SSH key for unattended push:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vault-template-deploy-key -N "" -C "vault-template-sync"
cd ~/projects/repos/templates/vault-template && git config core.sshCommand "ssh -i ~/.ssh/vault-template-deploy-key -o IdentitiesOnly=yes"
gh repo deploy-key add ~/.ssh/vault-template-deploy-key.pub --repo <owner>/vault-template --title "vault-template-sync" --allow-write
```

Verify push works without passphrase prompt:

```bash
cd ~/projects/repos/templates/vault-template && git push --dry-run origin main
```

#### Post-commit hook

Create `~/vault/.git/hooks/post-commit`:

```bash
#!/usr/bin/env bash
# Sync public-facing vault files to the public template repo.
# Runs after every commit in ~/vault (including auto-commits).
#
# SAFETY: Content directories are excluded by rsync. Only structure
# (empty dirs via .gitkeep), templates, config, and docs are copied.
# Private notes never leave this repo.
#
# Content directories are derived from .gitattributes (git-crypt rules).
# Adding a new content directory only requires updating .gitattributes.

set -euo pipefail

VAULT="$HOME/vault"
PUBLIC="$HOME/projects/repos/templates/vault-template"

# Bail if the public repo isn't cloned on this machine
[ -d "$PUBLIC/.git" ] || exit 0

# Derive content directories from .gitattributes
EXCLUDE_ARGS=()
CONTENT_DIRS=()
while IFS= read -r line; do
  dir="${line%%/**}"
  CONTENT_DIRS+=("$dir")
  EXCLUDE_ARGS+=(--exclude="${dir}/**")
done < <(awk '/filter=git-crypt/ {print $1}' "$VAULT/.gitattributes")

# Sync: templates, config, and docs only
rsync -a --delete \
  --filter='P LICENSE' \
  "${EXCLUDE_ARGS[@]}" \
  --exclude='.git/' \
  --exclude='.gitattributes' \
  --exclude='.stignore' \
  --exclude='.stfolder/' \
  --exclude='.stversions/' \
  --exclude='.trash/' \
  --exclude='.claude/' \
  --exclude='.obsidian/workspace.json' \
  --exclude='.obsidian/workspace-mobile.json' \
  --exclude='.obsidian/cache' \
  "$VAULT/" "$PUBLIC/"

# Clean orphaned directories (deleted/renamed in vault)
for dir in "$PUBLIC"/*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  [[ "$name" == .git ]] && continue
  [[ "$name" == .obsidian ]] && continue
  [ -d "$VAULT/$name" ] || rm -rf "$dir"
done

# Ensure content directories exist with .gitkeep
for dir in "${CONTENT_DIRS[@]}"; do
  mkdir -p "$PUBLIC/$dir"
  [ -f "$PUBLIC/$dir/.gitkeep" ] || touch "$PUBLIC/$dir/.gitkeep"
done

# Preserve _archive subdirectories
find "$VAULT" -maxdepth 2 -name '_archive' -type d | while read -r archive; do
  rel="${archive#"$VAULT/"}"
  mkdir -p "$PUBLIC/$rel"
  [ -f "$PUBLIC/$rel/.gitkeep" ] || touch "$PUBLIC/$rel/.gitkeep"
done

cd "$PUBLIC" || exit 1
git add -A

# Only commit and push if there are changes
if ! git diff --cached --quiet; then
  git commit -m "sync: $(date +%F-%H%M)"
  git push --quiet origin main 2>/dev/null || true
fi
```

Make executable:

```bash
chmod +x ~/vault/.git/hooks/post-commit
```

#### Rsync rules

| Rule | Effect |
|------|--------|
| Content excludes (from `.gitattributes`) | Directory shells are synced but nothing inside them |
| Orphan cleanup loop | Removes directories from public repo that no longer exist in vault |
| `.gitkeep` creation loop | Ensures every content directory has a `.gitkeep` for git tracking |
| `_archive` discovery | Preserves `_archive` subdirectories with `.gitkeep` |
| `--filter='P LICENSE'` | Protects `LICENSE` (exists only in public repo) from deletion |
| `--exclude='.git/'` | Never touches git internals |
| `--exclude='.gitattributes'` | git-crypt rules stay in private repo only |
| `--exclude='.stignore'`, `'.stfolder/'`, `'.stversions/'`, `'.trash/'`, `'.claude/'` | Syncthing, trash, and Claude artifacts stay private |
| `--exclude='.obsidian/workspace*.json'`, `'.obsidian/cache'` | Machine-specific Obsidian state excluded |
| `--delete` | Files removed from vault's public-facing set are removed from public repo |

#### Testing

Verify no private content leaks:

```bash
# Create a fake note in every content directory
echo "PRIVATE" > ~/vault/1-fleeting/test-leak.md
cd ~/vault && git add -A && git commit -m "test: leak check"

# Verify it did NOT appear in the public repo
ls ~/projects/repos/templates/vault-template/1-fleeting/
# Expected: only .gitkeep

# Clean up
rm ~/vault/1-fleeting/test-leak.md
cd ~/vault && git add -A && git commit -m "test: clean up"
```

Verify template sync works:

```bash
# Modify a template
echo "<!-- test -->" >> ~/vault/8-templates/daily.md
cd ~/vault && git add -A && git commit -m "test: sync check"

# Verify it appeared in the public repo
tail -1 ~/projects/repos/templates/vault-template/8-templates/daily.md
# Expected: <!-- test -->

# Clean up
sed -i '$ d' ~/vault/8-templates/daily.md
cd ~/vault && git add -A && git commit -m "test: clean up"
```

## 2. Local Machines (Linux)

### 2.1 Install Packages

```bash
sudo pacman -S syncthing wl-clipboard
```

- [Syncthing](https://syncthing.net/) provides real-time file sync
- `wl-clipboard` enables image pasting in obsidian.nvim on Wayland

### 2.2 Enable Syncthing

```bash
systemctl --user enable --now syncthing
```

User service (not system service) starts and stops with the desktop session.

### 2.3 Pair with Remote Hub

Open the Syncthing web UI at `http://localhost:8384`:

1. Click **Add Remote Device**
2. Paste the remote hub's device ID (from step 1.1)
3. Set the device address to `tcp://<hub-tailscale-ip>:22000`
4. Save

The remote hub must accept the device and share the vault folder (see step 1.1). Once accepted, a notification appears in the local Syncthing UI:

1. Accept the **vault** folder share
2. Set the folder path to `~/vault`
3. Save

Wait for initial sync to complete (check Syncthing UI for "Up to Date").

### 2.4 Harden Syncthing

Restrict to Tailscale-only traffic:

```bash
syncthing cli config options raw-listen-addresses 0 set tcp://<tailscale-ip>:22000
syncthing cli config options natenabled set false
syncthing cli config options global-ann-enabled set false
syncthing cli config options local-ann-enabled set false
syncthing cli config options relays-enabled set false
```

### 2.5 Neovim Config

*Skip this section if you don't use Neovim.*

If the machine uses `dotfiles-arch` or `dotfiles-omarchy` via GNU Stow:

```bash
# dotfiles-arch
cd ~/projects/repos/dotfiles/dotfiles-arch && git pull && stow -R -v -t ~ nvim
# or dotfiles-omarchy
cd ~/projects/repos/dotfiles/dotfiles-omarchy && git pull && stow -R -v -t ~ nvim
```

If the machine uses a separate nvim config:

```bash
cp ~/projects/repos/dotfiles/dotfiles-arch/nvim/.config/nvim/lua/plugins/obsidian.lua \
   ~/.config/nvim/lua/plugins/obsidian.lua
```

Append to `~/.config/nvim/lua/config/options.lua` if not already present:

```lua
-- Markdown heading fold support (used by obsidian.nvim vault navigation)
vim.g.markdown_folding = 1
```

Verify: `nvim ~/vault/1-fleeting/test.md` then `:checkhealth obsidian`

### 2.6 Obsidian Desktop (optional)

For graph view, canvas, and community plugins. Install from [obsidian.md/download](https://obsidian.md/download) or via Flatpak:

```bash
flatpak install flathub md.obsidian.Obsidian
```

Open `~/vault` as vault. Choose **Open folder as vault**, not "Create new vault".

## 3. Local Machines (Windows / WSL)

### 3.1 Syncthing (native Windows)

Install Syncthing natively on Windows (not inside WSL). Download from [syncthing.net/downloads](https://syncthing.net/downloads/) or install via winget:

```powershell
winget install Syncthing.Syncthing
```

### 3.2 Auto-start on Login

Windows Syncthing does not auto-start by default. Create a VBS script in the Startup folder that runs Syncthing hidden in the background with no console window or taskbar entry:

```powershell
$p = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Syncthing.vbs"
Set-Content -Path $p -Value 'Set WshShell = CreateObject("WScript.Shell")'
Add-Content -Path $p -Value 'WshShell.Run Chr(34) & WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Microsoft\WinGet\Links\syncthing.exe" & Chr(34) & " --no-browser", 0, False'
```

Run each line separately in PowerShell. The executable path assumes installation via `winget install Syncthing.Syncthing`. If installed differently, find the path with `where.exe syncthing` and adjust accordingly.

Access the web UI manually at `http://127.0.0.1:8384` when needed.

### 3.3 Pair with Remote Hub

Open the Syncthing web UI at `http://127.0.0.1:8384` (`localhost` may not work on Windows due to IPv6 resolution):

1. Click **Add Remote Device**
2. Paste the remote hub's device ID
3. Set the device address to `tcp://<hub-tailscale-ip>:22000`
4. Save
5. Accept the **vault** folder share when it appears
6. Set the folder path to `C:\Users\<user>\vault`
7. Go to **Actions** > **Settings** > **Connections**:
   - Set **Sync Protocol Listen Addresses** to `tcp://<tailscale-ip>:22000`
   - Uncheck **NAT Traversal**
   - Uncheck **Global Discovery**
   - Uncheck **Local Discovery**
   - Uncheck **Enable Relaying**
   - Save

### 3.4 Obsidian Desktop

Install via winget:

```powershell
winget install Obsidian.Obsidian
```

Open `C:\Users\<user>\vault` as vault. Choose **Open folder as vault**.

### 3.5 WSL Access

Symlink the Windows-synced vault into WSL:

```bash
ln -s /mnt/c/Users/<user>/vault ~/vault
```

*Skip the Neovim steps below if not applicable.*

If `dotfiles-arch` is cloned in WSL:

```bash
cd ~/projects/repos/dotfiles/dotfiles-arch && git pull && stow -R -v -t ~ nvim
```

Otherwise, copy the obsidian.nvim plugin spec manually:

```bash
cp ~/projects/repos/dotfiles/dotfiles-arch/nvim/.config/nvim/lua/plugins/obsidian.lua \
   ~/.config/nvim/lua/plugins/obsidian.lua
```

Append to `~/.config/nvim/lua/config/options.lua` if not already present:

```lua
-- Markdown heading fold support (used by obsidian.nvim vault navigation)
vim.g.markdown_folding = 1
```

Do not run git auto-commit from WSL. The remote hub handles all git operations.

## 4. Mobile (Android)

### 4.1 Tailscale

Install [Tailscale](https://play.google.com/store/apps/details?id=com.tailscale.ipn) from Play Store. Sign in to join the tailnet. The phone must be connected to Tailscale for sync to work.

### 4.2 Syncthing-Fork

Install [Syncthing-Fork](https://github.com/Catfriend1/syncthing-android) via [Obtainium](https://github.com/ImranR98/Obtainium) (recommended, most up-to-date releases). The [Play Store](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid) version may be significantly outdated.

Pair with the remote hub:

1. Open Syncthing-Fork
2. Go to **Devices** > **Add Device**
3. Paste the remote hub's device ID
4. Set the address to `tcp://<hub-tailscale-ip>:22000`
5. Save

The remote hub must accept the device and share the vault folder (see step 1.1).

Back on the phone, accept the **vault** folder share:

1. Set the folder path to **device storage** (not app storage), e.g., `[int]/Obsidian/vault`
2. Save
3. Wait for initial sync to complete

### 4.3 Obsidian Mobile

Install [Obsidian](https://play.google.com/store/apps/details?id=md.obsidian) from Play Store.

1. Open Obsidian
2. Choose **Open folder as vault** (not "Create new vault")
3. Select **Device storage** (not app storage)
4. Navigate to the Syncthing vault folder
5. Use `1-fleeting/` for fleeting notes; they sync to the hub within seconds

### 4.4 Resolving Sync Conflicts

On first sync, Obsidian may write to `.obsidian/app.json` at the same time the hub version syncs, creating a `.sync-conflict-*` file. This is normal:

1. The live file (e.g., `.obsidian/app.json`) is correct as-is
2. Delete the conflict file (the one with `sync-conflict` in the name)
3. Conflict files are ignored by `.gitignore` and will never be committed

## 5. Recovery (fresh clone)

Recovery requires both the GPG key and the git-crypt key.

### 5.1 Import GPG key

```bash
gpg --import vault-backup-private.asc
```

### 5.2 Configure GPG for headless operation

Set up `pinentry-null` and `gpg-agent.conf` as described in step 1.3 (GPG headless configuration).

### 5.3 Clone from encrypted remote

```bash
git clone -c gcrypt.gpg-args="--no-tty" \
  "gcrypt::git@github.com:<owner>/<repo>.git#main" ~/vault
```

### 5.4 Unlock git-crypt

```bash
cd ~/vault && git-crypt unlock <path-to-git-crypt-key>
```

### 5.5 Configure gcrypt for future pushes

```bash
cd ~/vault
git config gcrypt.participants "<GPG-FINGERPRINT>"
git config gcrypt.signingkey "<GPG-FINGERPRINT>"
git config gcrypt.gpg-args "--no-tty"
```

Without the GPG key, the clone fails. Without the git-crypt key, file contents are unreadable.

## Verify

After setup on each device:

- Confirm Syncthing is running: `systemctl --user status syncthing` (local) or `systemctl status syncthing@$USER` (remote hub)
- Confirm vault folder is syncing: check Syncthing web UI for "Up to Date" status
- Confirm obsidian.nvim loads (if using Neovim): `nvim ~/vault/1-fleeting/test.md` then `:checkhealth obsidian`
- Confirm auto-commit timer is active (remote hub only): `systemctl --user list-timers vault-autocommit.timer`
- Confirm deploy key push works (remote hub only): `cd ~/vault && git push --dry-run origin main`
- Confirm encryption: the GitHub repo should show only opaque encrypted data (no readable filenames or content)
- Confirm public template sync (remote hub only): modify a template, commit, verify it appears in the public repo and on GitHub
