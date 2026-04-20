# Setup: Self-hosted hub (sync, encryption, backup)

A self-hosted hub adds real-time sync across Linux, Windows, and Android, plus encrypted backup to GitHub with automated commits and a public template mirror. This guide covers the infrastructure layer that sits on top of the local vault described in [SETUP-LOCAL.md](SETUP-LOCAL.md).

## What this adds

| Feature | Purpose |
|---|---|
| Hub Syncthing | Always-on hub for asynchronous device sync over Tailscale |
| Device pairing (Linux, Windows, Android) | Each client syncs with the hub |
| git-crypt | Encrypts file contents in git objects (AES-256) |
| git-remote-gcrypt | Encrypts the entire remote (filenames, structure, history) |
| Automated backup | systemd timer commits and pushes hourly |
| Public template sync | Post-commit hook mirrors structure, templates, and docs to a public repo |

## Prerequisites

- A **local vault** set up per [SETUP-LOCAL.md](SETUP-LOCAL.md) on at least one machine.
- **Arch Linux** on the remote hub (headless, always-on).
- **[Tailscale](https://tailscale.com/)** installed and connected on all devices (hub and clients).
- **GitHub account** with two repos: one private (encrypted backup, e.g., `vault-backup`), one public (template mirror, e.g., `vault-template`).

This guide standardizes on `~/vault` for the hub. All commands, systemd units, and scripts assume this path. If you use a different location, adjust the service file (`self-hosting/vault-autocommit.service`) and the commands below accordingly. The `OBSIDIAN_VAULT` environment variable documented in SETUP-LOCAL.md is for the Neovim overlay on local machines, not for hub infrastructure.

## 1. Hub baseline tools

Install on the remote hub:

```bash
sudo pacman -S --needed base-devel git github-cli gnupg openssh rsync
```

Bootstrap `yay` (AUR helper) for git-remote-gcrypt:

```bash
git clone https://aur.archlinux.org/yay.git /tmp/yay
( cd /tmp/yay && makepkg -si )
rm -rf /tmp/yay
```

Set your Git identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 2. Hub Syncthing

The remote hub runs Syncthing as a system service (always-on, survives reboot). The vault directory (`~/vault`) is created by Syncthing during the first device pairing.

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

Note the hub's device ID for pairing other devices:

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

## 3. Pair devices with the hub

Each client device needs Syncthing installed and paired with the hub. Wait for the initial sync to complete (Syncthing UI shows "Up to Date") before continuing to the encryption sections below.

### 3.1 Linux

Install and enable Syncthing on the client:

```bash
sudo pacman -S syncthing
systemctl --user enable --now syncthing
```

Open `http://localhost:8384` and add the vault folder.

Pair with the hub:

1. **Add Remote Device**: paste the hub's device ID
2. **Accept** the vault folder share when prompted
3. Set the folder path to the vault location on that device
4. Wait for initial sync to complete

Harden for Tailscale-only sync:

```bash
syncthing cli config options raw-listen-addresses 0 set tcp://<tailscale-ip>:22000
syncthing cli config options natenabled set false
syncthing cli config options global-ann-enabled set false
syncthing cli config options local-ann-enabled set false
syncthing cli config options relays-enabled set false
```

### 3.2 Windows

Install Syncthing natively on Windows (not inside WSL):

```powershell
winget install Syncthing.Syncthing
```

Syncthing does not auto-start on Windows. Create a VBS script in the Startup folder:

```powershell
$p = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Syncthing.vbs"
Set-Content -Path $p -Value 'Set WshShell = CreateObject("WScript.Shell")'
Add-Content -Path $p -Value 'WshShell.Run Chr(34) & WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Microsoft\WinGet\Links\syncthing.exe" & Chr(34) & " --no-browser", 0, False'
```

Run each line separately in PowerShell. The executable path assumes installation via `winget install Syncthing.Syncthing`. If installed differently, find the path with `where.exe syncthing` and adjust accordingly.

Access the web UI at `http://127.0.0.1:8384` (`localhost` may not work on Windows due to IPv6 resolution).

Pair with the hub:

1. Click **Add Remote Device**, paste the hub's device ID, set address to `tcp://<hub-tailscale-ip>:22000`
2. Accept the **vault** folder share when it appears, set path to `C:\Users\<user>\vault`
3. Harden for Tailscale-only sync via **Actions** > **Settings** > **Connections**:
   - Set **Sync Protocol Listen Addresses** to `tcp://<tailscale-ip>:22000`
   - Uncheck **NAT Traversal**
   - Uncheck **Global Discovery**
   - Uncheck **Local Discovery**
   - Uncheck **Enable Relaying**
   - Save

Wait for initial sync to complete.

**WSL access**: symlink the Windows-synced vault into WSL:

```bash
ln -s /mnt/c/Users/<user>/vault ~/vault
```

**Neovim in WSL** *(skip if not applicable)*: install Neovim and apply the vault overlay inside WSL:

```bash
sudo pacman -S --needed neovim ripgrep git stow
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
cd ~/vault && stow -v -t ~ nvim-vault
```

Do not run git auto-commit from WSL. The remote hub handles all git operations.

### 3.3 Android

1. Install [Obsidian](https://play.google.com/store/apps/details?id=md.obsidian) from Play Store.
2. Install [Tailscale](https://play.google.com/store/apps/details?id=com.tailscale.ipn) and sign in.
3. Install [Syncthing-Fork](https://github.com/Catfriend1/syncthing-android) via [Obtainium](https://github.com/ImranR98/Obtainium) (recommended) or [Play Store](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid).
4. Add the hub as a remote device (paste device ID, set address to `tcp://<hub-tailscale-ip>:22000`).
5. Accept the vault folder share; set path to device storage (e.g., `[int]/Obsidian/vault`).
6. Wait for initial sync to complete.
7. Open Obsidian, choose **Open folder as vault**, select the Syncthing folder.

Syncthing on Android pauses on battery saver. Do not rename or move notes from the Android Files app; use Obsidian's file explorer only.

On mobile, templates are not auto-applied. After creating a new note, swipe down (pull) to trigger the template picker. This behavior is configured by `mobilePullAction: insert-template` in `.obsidian/app.json` (already set in this template).

Confirm the default folder is `0-fleeting/` in Settings > Files and links > Default location.

### 3.4 Resolving sync conflicts

On first sync, Obsidian may write to `.obsidian/app.json` at the same time the hub version syncs, creating a `.sync-conflict-*` file. This is normal:

1. The live file is correct as-is
2. Delete the conflict file (the one with `sync-conflict` in the name)
3. Conflict files are ignored by `.gitignore` and will never be committed

## 4. git-crypt

git-crypt encrypts file contents in git objects. Encryption rules are defined in `.gitattributes`:

```text
0-fleeting/** filter=git-crypt diff=git-crypt
1-literature/** filter=git-crypt diff=git-crypt
...
6-assets/** filter=git-crypt diff=git-crypt
```

Adding a new content directory requires adding a rule to `.gitattributes`. The post-commit hook derives content directories from these same rules.

```bash
sudo pacman -S git-crypt
cd ~/vault && git-crypt init
git-crypt export-key ~/vault-git-crypt.key
```

Copy the key to a secure location. The key is raw binary (not human-readable text). Store it as a **file attachment** in a password manager. Transfer to a trusted workstation (not the hub itself), then delete the local copy:

```bash
scp ~/vault-git-crypt.key <user>@<workstation-tailscale-ip>:~/Downloads/
rm ~/vault-git-crypt.key
```

## 5. git-remote-gcrypt

git-remote-gcrypt encrypts the entire repository on the remote, including filenames and directory structure. This prevents note titles from being visible on GitHub.

### 5.1 Install

```bash
yay -S git-remote-gcrypt
```

### 5.2 GPG key

Generate a dedicated GPG key for unattended encrypted backup. No passphrase (required for the systemd timer):

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

### 5.3 Headless GPG configuration

Configure GPG for unattended operation. gpg-agent invokes pinentry even for no-passphrase keys; the `pinentry-null` script provides a headless pinentry that returns an empty passphrase automatically.

Install from the `self-hosting/` directory:

```bash
cp ~/vault/self-hosting/pinentry-null ~/.local/bin/
chmod +x ~/.local/bin/pinentry-null
```

Configure `~/.gnupg/gpg-agent.conf`:

```ini
pinentry-program /home/<user>/.local/bin/pinentry-null
```

Restart the agent and verify:

```bash
gpgconf --kill gpg-agent
echo "test" | gpg --no-tty -e -r vault-backup@noreply | gpg --no-tty -d
```

### 5.4 Backup GPG key material

Export and store securely (same location as the git-crypt key). Transfer to a trusted workstation:

```bash
gpg --export --armor vault-backup@noreply > ~/vault-backup-public.asc
gpg --export-secret-keys --armor vault-backup@noreply > ~/vault-backup-private.asc
cp ~/.gnupg/openpgp-revocs.d/<fingerprint>.rev ~/vault-backup-revocation.asc
scp ~/vault-backup-public.asc ~/vault-backup-private.asc ~/vault-backup-revocation.asc \
  <user>@<workstation-tailscale-ip>:~/Downloads/
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

### 5.5 Configure remote

The GitHub backup repo name may differ from the local vault directory name (e.g., `vault-backup` on GitHub, `vault` locally). Use the GitHub repo name in the remote URL.

gcrypt supports both per-remote and repo-wide config keys. Participants and signing key can be set as `remote.<name>.gcrypt-participants` / `remote.<name>.gcrypt-signingkey`, or repo-wide as `gcrypt.participants` and `user.signingkey`. `gcrypt.gpg-args` is documented as a repo-level or global value; a per-remote variant is not documented upstream, so leave it set at repo level. The commands below use repo-local values; this repo has a single gcrypt remote so either layout works.

```bash
cd ~/vault
git remote add origin "gcrypt::git@github.com:<owner>/<repo>.git#main"
git config gcrypt.participants "<GPG-FINGERPRINT>"
git config user.signingkey "<GPG-FINGERPRINT>"
git config gcrypt.gpg-args "--no-tty"
```

If the target branch already exists with plain git data, delete it on GitHub first. gcrypt does not fully replace an existing branch; it may merge old tree data with encrypted blobs, leaving filenames visible:

```bash
# If the branch already has plain git data, delete it on GitHub first:
# gh api repos/<owner>/<repo>/git/refs/heads/main -X DELETE

git push -u origin main
```

The `-u` flag sets upstream tracking so that subsequent `git push` (without arguments) targets the correct remote and branch. The auto-commit timer relies on this.

Record the gcrypt remote ID shown in the output (`:id:...`).

GitHub will show a single synthetic commit ("Initial commit" by root@localhost, dated 2013-01-01). This is the encrypted container. Your actual commits are preserved inside the encrypted payload.

### 5.6 Performance note

git-remote-gcrypt re-encrypts and re-uploads the full repository on every push (git backend limitation). This is acceptable for a small vault. If the vault grows substantially (primarily from `6-assets/`), push duration will increase. Monitor with `du -sh .git/` periodically.

## 6. Deploy key

Generate a dedicated SSH key (no passphrase) for unattended push:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vault-deploy-key -N "" -C "vault-autocommit"
cd ~/vault && git config core.sshCommand "ssh -i ~/.ssh/vault-deploy-key -o IdentitiesOnly=yes"
gh repo deploy-key add ~/.ssh/vault-deploy-key.pub --repo <owner>/<repo> --title "vault-autocommit" --allow-write
```

**Note**: deploy keys added via `gh` are attributed to the authenticating user. If that `gh` auth session is later revoked or rotated, GitHub audit policies may remove the key. Verify the key still appears under Settings > Deploy keys after any credential rotation.

Verify push works without passphrase prompt:

```bash
cd ~/vault && git push --dry-run origin main
```

## 7. Auto-commit timer

Enable user linger so the timer persists across SSH logout:

```bash
sudo loginctl enable-linger $USER
```

Install the systemd units from `self-hosting/`:

```bash
mkdir -p ~/.config/systemd/user
cp ~/vault/self-hosting/vault-autocommit.service ~/.config/systemd/user/
cp ~/vault/self-hosting/vault-autocommit.timer ~/.config/systemd/user/
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

## 8. Public template sync

A public repo mirrors the vault's structure, templates, config, and docs. Note content is not synced.

### 8.1 Clone the public repo

```bash
cd ~/projects/repos/templates
git clone git@github.com:<owner>/vault-template.git
```

### 8.2 Deploy key

Generate a dedicated SSH key for unattended push:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vault-template-deploy-key -N "" -C "vault-template-sync"
cd ~/projects/repos/templates/vault-template && git config core.sshCommand "ssh -i ~/.ssh/vault-template-deploy-key -o IdentitiesOnly=yes"
gh repo deploy-key add ~/.ssh/vault-template-deploy-key.pub --repo <owner>/vault-template --title "vault-template-sync" --allow-write
```

Verify:

```bash
cd ~/projects/repos/templates/vault-template && git push --dry-run origin main
```

### 8.3 Sentinel file

The post-commit hook refuses to run unless the public repo contains a `.public-mirror-marker` file. This guards against a misconfigured `vault.publicPath` trashing an unrelated repo. Create it once:

```bash
touch ~/projects/repos/templates/vault-template/.public-mirror-marker
cd ~/projects/repos/templates/vault-template && git add .public-mirror-marker && git commit -m "chore: add sentinel marker"
```

### 8.4 Post-commit hook

The hook is tracked in the repo at `.githooks/post-commit`. Enable it on the remote hub only:

```bash
cd ~/vault && git config core.hooksPath .githooks
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

### 8.5 Rsync rules

The hook uses a fail-closed allowlist: only paths named explicitly in the `--include` list are published; the trailing `--exclude='*'` denies everything else.

| Rule | Effect |
|---|---|
| Explicit `--include` allowlist | Only named root files (docs, `LICENSE`, `.gitignore`, `.gitattributes`, `.stignore`), `nvim-vault/**`, `self-hosting/**`, `5-templates/**`, `.githooks/**`, and public-safe `.obsidian/` subfiles are published |
| Trailing `--exclude='*'` | Anything not in the allowlist is denied; a new top-level file or directory will not publish unless its path is added to the filter |
| Sentinel check (`.public-mirror-marker`) | Hook refuses to sync unless `$PUBLIC` contains the marker file. Guards against a wrong `vault.publicPath` trashing an unrelated repo |
| `--filter='P /.public-mirror-marker'` | Protects the sentinel file from `--delete` (the marker lives only in vault-template, not in the private vault) |
| Orphan cleanup loop | Removes top-level directories from the public repo that no longer exist in the vault (catches renames) |
| `.gitkeep` creation loop | Creates empty content-directory shells in the public repo (content dirs are not in the allowlist) |
| `--delete` | Anything in the public repo but not matched by the allowlist is removed on the next sync |
| `VAULT` resolution | Read from `git rev-parse --show-toplevel`; the hook works in any clone regardless of filesystem location |
| `PUBLIC` resolution | Read from `git config vault.publicPath`, falling back to `$HOME/projects/repos/templates/vault-template`. Forks override via `git config vault.publicPath /their/path` |

**Public-mirror constraint**: `--delete` plus the cleanup loops mean the public repo is strictly a derived view of the private vault's allowlisted set. Any file or directory that exists only in the public repo will be wiped on the next sync unless explicitly protected. To preserve a public-only item, three places in `.githooks/post-commit` must be updated: (1) add an rsync protect filter (e.g., `--filter='P /.github/'`), (2) add the directory name to the orphan-directory skip list, and (3) add the filename to the `ALLOWED_ROOT_FILES` list for root files.

### 8.6 Testing

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
echo "<!-- test -->" >> ~/vault/5-templates/fleeting.md
cd ~/vault && git add -A && git commit -m "test: sync check"

# Verify it appeared in the public repo
tail -1 ~/projects/repos/templates/vault-template/5-templates/fleeting.md
# Expected: <!-- test -->

# Clean up
sed -i '$ d' ~/vault/5-templates/fleeting.md
cd ~/vault && git add -A && git commit -m "test: clean up"
```

## 9. Recovery (fresh clone)

Recovery requires both the GPG key and the git-crypt key.

### 9.1 Import GPG key

```bash
gpg --import vault-backup-private.asc
```

### 9.2 Configure GPG for headless operation

Install `pinentry-null` and configure `gpg-agent.conf` as described in §5.3.

### 9.3 Clone from encrypted remote

```bash
git clone -c gcrypt.gpg-args="--no-tty" \
  "gcrypt::git@github.com:<owner>/<repo>.git#main" ~/vault
```

### 9.4 Unlock git-crypt

```bash
cd ~/vault && git-crypt unlock <path-to-git-crypt-key>
```

### 9.5 Configure gcrypt for future pushes

```bash
cd ~/vault
git config gcrypt.participants "<GPG-FINGERPRINT>"
git config user.signingkey "<GPG-FINGERPRINT>"
git config gcrypt.gpg-args "--no-tty"
```

Without the GPG key, the clone fails. Without the git-crypt key, file contents are unreadable.

## Verify

After setup on the remote hub:

- Syncthing is running: `systemctl status syncthing@$USER`
- Vault folder is syncing: check Syncthing web UI for "Up to Date"
- Auto-commit timer is active: `systemctl --user list-timers vault-autocommit.timer`
- Deploy key push works: `cd ~/vault && git push --dry-run origin main`
- Encryption: the GitHub repo shows only opaque encrypted data (no readable filenames or content)
- Public template sync: modify a template, commit, verify it appears in the public repo and on GitHub
