# Setup Guide

Step-by-step setup for the vault across all devices. This guide is self-contained: every tool it uses is installed here. If [`dotfiles-arch`](https://github.com/peregrinus879/dotfiles-arch) (headless) or [`dotfiles-omarchy`](https://github.com/peregrinus879/dotfiles-omarchy) (desktop) is already installed, most of the baseline is in place and the install steps below can be skimmed.

## Prerequisites

- **Arch Linux** on every Linux host (remote hub and local machines). Non-Arch distros are out of scope.
- **[Tailscale](https://tailscale.com/)** installed and connected on all devices.
- **GitHub account** with two repos: one private for the encrypted backup (e.g., `vault-backup`), one public for the mirrored template (e.g., `vault-template`).

## 1. Remote Hub (headless Linux, always-on)

The remote hub is the authoritative copy. It runs Syncthing as an always-on relay, git for version history, and a systemd timer for automated backup to GitHub.

### 1.1 Baseline Tools

Install the tools used throughout this guide. If `dotfiles-arch` is already installed, these are already present.

```bash
sudo pacman -S --needed base-devel git github-cli gnupg openssh rsync
```

Bootstrap `yay` (AUR helper) for `git-remote-gcrypt` in §1.4:

```bash
git clone https://aur.archlinux.org/yay.git /tmp/yay
( cd /tmp/yay && makepkg -si )
rm -rf /tmp/yay
```

Set your Git identity. If you use the `dotfiles-arch` layout, place identity in an untracked local file:

```bash
mkdir -p ~/.config/git
cat > ~/.config/git/config.local <<'EOF'
[user]
  name = Your Name
  email = your-email@example.com
EOF
```

Otherwise, set it globally:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### 1.2 Syncthing

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

### 1.3 Git-crypt

git-crypt encrypts file contents in git objects. Encryption rules are defined in `.gitattributes`:

```text
0-fleeting/** filter=git-crypt diff=git-crypt
1-sources/** filter=git-crypt diff=git-crypt
2-literature/** filter=git-crypt diff=git-crypt
3-permanent/** filter=git-crypt diff=git-crypt
4-writing/** filter=git-crypt diff=git-crypt
5-index/** filter=git-crypt diff=git-crypt
7-assets/** filter=git-crypt diff=git-crypt
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

### 1.4 Git-remote-gcrypt

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

Store the following in your password manager:

**Files:**
- `vault-git-crypt.key` (git-crypt symmetric key)
- `private-key.asc` (GPG private key)
- `public-key.asc` (GPG public key)
- `revocation-cert.asc` (GPG revocation certificate)

**Values:**
- GPG fingerprint
- GPG key ID
- GPG identity (`vault-backup <vault-backup@noreply>`)
- gcrypt remote ID (`:id:...`, shown during first push)
- Backup repo URL (`gcrypt::git@github.com:<owner>/<repo>.git#main`)

#### Configure remote

The GitHub backup repo name may differ from the local vault directory name (e.g., `vault-backup` on GitHub, `vault` locally). Use the GitHub repo name in the remote URL.

gcrypt supports both per-remote and repo-wide config keys. Participants and signing key can be set as `remote.<name>.gcrypt-participants` / `remote.<name>.gcrypt-signingkey`, or repo-wide as `gcrypt.participants` and `user.signingkey`. The commands below use repo-local `git config` values (the simpler shape); this repo has a single gcrypt remote so either layout works. `gcrypt.gpg-args` is documented as a repo-level or global value; a per-remote variant is not documented upstream, so leave it set at repo level.

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

GitHub will show a single synthetic commit ("Initial commit" by root@localhost, dated 2013-01-01). This is the encrypted container, not your real history. Your actual commits are preserved inside the encrypted payload and visible after cloning with the GPG key.

#### Performance note

git-remote-gcrypt re-encrypts and re-uploads the full repository on every push (git backend limitation). This is acceptable for a small vault. If the vault grows substantially (primarily from `7-assets/`), push duration will increase. Monitor with `du -sh .git/` periodically. If push times become problematic, this is a broader backup-architecture decision, not a drop-in backend swap.

### 1.5 Deploy Key

Generate a dedicated SSH key (no passphrase) for unattended push:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vault-deploy-key -N "" -C "vault-autocommit"
cd ~/vault && git config core.sshCommand "ssh -i ~/.ssh/vault-deploy-key -o IdentitiesOnly=yes"
gh repo deploy-key add ~/.ssh/vault-deploy-key.pub --repo <owner>/<repo> --title "vault-autocommit" --allow-write
```

**Note**: deploy keys added via `gh` are attributed to the authenticating user. If that `gh` auth session is later revoked or rotated, GitHub audit policies may remove the key. If you rotate `gh` credentials, verify the key still appears under the repo's Settings > Deploy keys and re-add if missing.

Verify push works without passphrase prompt:

```bash
cd ~/vault && git push --dry-run origin main
```

### 1.6 Auto-commit Timer

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

### 1.7 Public Template Sync

A public repo ([vault-template](https://github.com/peregrinus879/vault-template)) mirrors the vault's structure, templates, config, and docs. Note content is not synced. A git post-commit hook handles this automatically after every commit.

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

The hook is tracked in the repo at `.githooks/post-commit`. Enable it on the remote hub only:

```bash
cd ~/vault
git config core.hooksPath .githooks
```

Verify the executable bit is set (git preserves it on clone):

```bash
ls -la ~/vault/.githooks/post-commit
```

If not executable, set and re-commit:

```bash
chmod +x ~/vault/.githooks/post-commit
cd ~/vault && git add .githooks/post-commit && git commit -m "chore: mark hook executable"
```

Local machines skip this step; the hook runs only on the remote hub.

#### Rsync rules

The hook uses a fail-closed allowlist: only paths named explicitly in the `--include` list are published; the trailing `--exclude='*'` denies everything else.

| Rule | Effect |
|------|--------|
| Explicit `--include` allowlist | Only named root files (docs, `.gitignore`, `.gitattributes`, `.stignore`), `6-templates/**`, `.githooks/**`, and public-safe `.obsidian/` subfiles are published |
| Trailing `--exclude='*'` | Anything not in the allowlist is denied; a new top-level file or directory will not publish unless its path is added to the filter |
| `--filter='P LICENSE'` | Protects `LICENSE` in the public repo from `--delete` (the private vault has no LICENSE, but vault-template does) |
| Orphan cleanup loop | Removes top-level directories from the public repo that no longer exist in the vault (catches renames) |
| `.gitkeep` creation loop | Creates empty content-directory shells in the public repo (since content dirs are not in the allowlist) |
| `--delete` | Anything in the public repo but not matched by the allowlist is removed on the next sync |
| `VAULT` resolution | Read from `git rev-parse --show-toplevel`; the hook works in any clone regardless of filesystem location |
| `PUBLIC` resolution | Read from `git config vault.publicPath`, falling back to `$HOME/projects/repos/templates/vault-template`. Forks override via `git config vault.publicPath /their/path` |

#### Testing

Verify no private content leaks:

```bash
# Create a fake note in a content directory
echo "PRIVATE" > ~/vault/0-fleeting/test-leak.md
cd ~/vault && git add -A && git commit -m "test: leak check"

# Verify it did NOT appear in the public repo
ls ~/projects/repos/templates/vault-template/0-fleeting/
# Expected: only .gitkeep

# Clean up
rm ~/vault/0-fleeting/test-leak.md
cd ~/vault && git add -A && git commit -m "test: clean up"
```

Verify template sync works:

```bash
# Modify a template
echo "<!-- test -->" >> ~/vault/6-templates/fleeting.md
cd ~/vault && git add -A && git commit -m "test: sync check"

# Verify it appeared in the public repo
tail -1 ~/projects/repos/templates/vault-template/6-templates/fleeting.md
# Expected: <!-- test -->

# Clean up
sed -i '$ d' ~/vault/6-templates/fleeting.md
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
2. Paste the remote hub's device ID (from step 1.2)
3. Set the device address to `tcp://<hub-tailscale-ip>:22000`
4. Save

The remote hub must accept the device and share the vault folder (see step 1.2). Once accepted, a notification appears in the local Syncthing UI:

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

Install Neovim and supporting tools:

```bash
sudo pacman -S neovim git stow
```

Clone the LazyVim starter so `obsidian.nvim` has a config to extend:

```bash
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
```

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

Verify: `nvim ~/vault/0-fleeting/test.md` then `:checkhealth obsidian`

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

Install Neovim and supporting tools inside WSL:

```bash
sudo pacman -S neovim git stow
```

Clone the LazyVim starter:

```bash
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
```

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

The remote hub must accept the device and share the vault folder (see step 1.2).

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
5. Use `0-fleeting/` for fleeting notes; they sync to the hub within seconds

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

Set up `pinentry-null` and `gpg-agent.conf` as described in step 1.4 (GPG headless configuration).

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
- Confirm obsidian.nvim loads (if using Neovim): `nvim ~/vault/0-fleeting/test.md` then `:checkhealth obsidian`
- Confirm auto-commit timer is active (remote hub only): `systemctl --user list-timers vault-autocommit.timer`
- Confirm deploy key push works (remote hub only): `cd ~/vault && git push --dry-run origin main`
- Confirm encryption: the GitHub repo should show only opaque encrypted data (no readable filenames or content)
- Confirm public template sync (remote hub only): modify a template, commit, verify it appears in the public repo and on GitHub
