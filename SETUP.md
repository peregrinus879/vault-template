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

```bash
sudo pacman -S git-crypt
cd ~/vault && git-crypt init
git-crypt export-key ~/vault-git-crypt.key
```

Copy the key to a secure location. The key is raw binary (not human-readable text). Store it as a **file attachment** in a password manager, or base64-encode it for a text field. Then delete the local copy:

```bash
# Copy to another machine over Tailscale
scp ~/vault-git-crypt.key <user>@<tailscale-ip>:~/Downloads/

# Or base64-encode for pasting into a password manager
base64 ~/vault-git-crypt.key

# Delete the local copy (the vault retains the key in .git/git-crypt/)
rm ~/vault-git-crypt.key
```

### 1.3 Deploy Key

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

### 1.4 Auto-commit Timer

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
    git commit -m "auto: $(date +%%F %%T)"; \
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

If the machine uses `dotfiles-arch` via GNU Stow:

```bash
cd ~/projects/repos/dotfiles/dotfiles-arch && git pull && stow -R -v -t ~ nvim
```

If the machine uses a separate nvim config (e.g., Omarchy default):

```bash
cp ~/projects/repos/dotfiles/dotfiles-arch/nvim/.config/nvim/lua/plugins/obsidian.lua \
   ~/.config/nvim/lua/plugins/obsidian.lua
```

Append to `~/.config/nvim/lua/config/options.lua` if not already present:

```lua
-- Markdown heading fold support (used by obsidian.nvim vault navigation)
vim.g.markdown_folding = 1
```

Verify: `nvim ~/vault/journal/test.md` then `:checkhealth obsidian`

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

Install from [obsidian.md/download](https://obsidian.md/download). Open `C:\Users\<user>\vault` as vault. Choose **Open folder as vault**.

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

GitHub repo for Obtainium: `https://github.com/Catfriend1/syncthing-android`

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
5. Use `journal/` for quick captures; they sync to the hub within seconds

### 4.4 Resolving Sync Conflicts

On first sync, Obsidian may write to `.obsidian/app.json` at the same time the hub version syncs, creating a `.sync-conflict-*` file. This is normal:

1. The live file (e.g., `.obsidian/app.json`) is correct as-is
2. Delete the conflict file (the one with `sync-conflict` in the name)
3. Conflict files are ignored by `.gitignore` and will never be committed

## 5. Recovery (fresh clone)

```bash
git clone <repo-url> ~/vault
cd ~/vault && git-crypt unlock <path-to-key>
```

The git-crypt key must have been backed up outside the vault (see step 1.2). Without it, encrypted directories are unreadable.

## Verify

After setup on each device:

- Confirm Syncthing is running: `systemctl --user status syncthing` (local) or `systemctl status syncthing@$USER` (remote hub)
- Confirm vault folder is syncing: check Syncthing web UI for "Up to Date" status
- Confirm obsidian.nvim loads (if using Neovim): `nvim ~/vault/journal/test.md` then `:checkhealth obsidian`
- Confirm auto-commit timer is active (remote hub only): `systemctl --user list-timers vault-autocommit.timer`
- Confirm deploy key push works (remote hub only): `cd ~/vault && git push --dry-run origin main`
- Confirm encryption: push a test note, verify it appears as binary on GitHub
