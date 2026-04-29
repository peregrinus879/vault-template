# Setup: Encrypted GitHub backup

Push the vault to GitHub with dual-layer encryption and an hourly auto-commit. File contents are encrypted with git-crypt; filenames and structure are encrypted with git-remote-gcrypt, so the public GitHub view shows only opaque blobs. A systemd timer on the hub commits and pushes every hour without human intervention.

**Prerequisite**: [SETUP-SYNC.md](SETUP-SYNC.md) (the hub must exist and be syncing).

**What this adds**:

| Feature | Purpose |
|---|---|
| git-crypt | AES-256 encryption of file contents in git objects |
| git-remote-gcrypt | Encrypts the entire remote including filenames and history |
| GPG (unattended) | Dedicated no-passphrase key for automated push |
| Deploy key | SSH deploy key for unattended push to GitHub |
| systemd auto-commit timer | Hourly commit + push of any changes on the hub |
| Recovery flow | Documented path for restoring from the encrypted remote |

**Prerequisites**:

- **GitHub account** with a private repo (encrypted backup, e.g., `vault-backup`).
- **SSH access to GitHub** from the hub.

## 1. Hub baseline tools

Install on the remote hub:

```bash
sudo pacman -S --needed base-devel git github-cli gnupg openssh
```

Bootstrap `yay` (AUR helper) for git-remote-gcrypt:

```bash
git clone https://aur.archlinux.org/yay.git /tmp/yay
( cd /tmp/yay && makepkg -si )
rm -rf /tmp/yay
```

Set your Git identity on the hub:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Initialize git in the vault on the hub (if not already):

```bash
cd ~/Projects/vault
git init -b main
git config core.hooksPath .githooks
git add -A && git commit -m "init: vault on hub"
```

## 2. git-crypt

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
cd ~/Projects/vault && git-crypt init
git-crypt export-key ~/vault-git-crypt.key
```

Copy the key to a secure location. The key is raw binary (not human-readable text). Store it as a **file attachment** in a password manager. Transfer to a trusted workstation (not the hub itself), then delete the local copy:

```bash
scp ~/vault-git-crypt.key <user>@<workstation-tailscale-ip>:~/Downloads/
rm ~/vault-git-crypt.key
```

## 3. git-remote-gcrypt

git-remote-gcrypt encrypts the entire repository on the remote, including filenames and directory structure. This prevents note titles from being visible on GitHub.

### 3.1 Install

```bash
yay -S git-remote-gcrypt
```

### 3.2 GPG key

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

### 3.3 Headless GPG configuration

Configure GPG for unattended operation. gpg-agent invokes pinentry even for no-passphrase keys; the `pinentry-null` script provides a headless pinentry that returns an empty passphrase automatically.

Install from the `infra/` directory:

```bash
cp ~/Projects/vault/infra/pinentry-null ~/.local/bin/
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

### 3.4 Backup GPG key material

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

### 3.5 Configure remote

The GitHub backup repo name may differ from the local vault directory name (e.g., `vault-backup` on GitHub, `vault` locally). Use the GitHub repo name in the remote URL.

gcrypt supports both per-remote and repo-wide config keys. Participants and signing key can be set as `remote.<name>.gcrypt-participants` / `remote.<name>.gcrypt-signingkey`, or repo-wide as `gcrypt.participants` and `user.signingkey`. `gcrypt.gpg-args` is documented as a repo-level or global value; a per-remote variant is not documented upstream, so leave it set at repo level. The commands below use repo-local values; this repo has a single gcrypt remote so either layout works.

```bash
cd ~/Projects/vault
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

### 3.6 Performance note

git-remote-gcrypt re-encrypts and re-uploads the full repository on every push (git backend limitation). This is acceptable for a small vault. If the vault grows substantially (primarily from `6-assets/`), push duration will increase. Monitor with `du -sh .git/` periodically.

## 4. Deploy key

Generate a dedicated SSH key (no passphrase) for unattended push:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vault-deploy-key -N "" -C "vault-autocommit"
cd ~/Projects/vault && git config core.sshCommand "ssh -i ~/.ssh/vault-deploy-key -o IdentitiesOnly=yes"
gh repo deploy-key add ~/.ssh/vault-deploy-key.pub --repo <owner>/<repo> --title "vault-autocommit" --allow-write
```

**Note**: deploy keys added via `gh` are attributed to the authenticating user. If that `gh` auth session is later revoked or rotated, GitHub audit policies may remove the key. Verify the key still appears under Settings > Deploy keys after any credential rotation.

Verify push works without passphrase prompt:

```bash
cd ~/Projects/vault && git push --dry-run origin main
```

## 5. Auto-commit timer

Enable user linger so the timer persists across SSH logout:

```bash
sudo loginctl enable-linger $USER
```

Install the systemd units from `infra/`:

```bash
mkdir -p ~/.config/systemd/user
cp ~/Projects/vault/infra/vault-autocommit.service ~/.config/systemd/user/
cp ~/Projects/vault/infra/vault-autocommit.timer ~/.config/systemd/user/
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

## 6. Recovery (fresh clone)

Recovery requires both the GPG key and the git-crypt key.

### 6.1 Import GPG key

```bash
gpg --import vault-backup-private.asc
```

### 6.2 Configure GPG for headless operation

Install `pinentry-null` and configure `gpg-agent.conf` as described in §3.3.

### 6.3 Clone from encrypted remote

```bash
mkdir -p ~/Projects
git clone -c gcrypt.gpg-args="--no-tty" \
  "gcrypt::git@github.com:<owner>/<repo>.git#main" ~/Projects/vault
```

### 6.4 Unlock git-crypt

```bash
cd ~/Projects/vault && git-crypt unlock <path-to-git-crypt-key>
```

### 6.5 Configure gcrypt for future pushes

```bash
cd ~/Projects/vault
git config gcrypt.participants "<GPG-FINGERPRINT>"
git config user.signingkey "<GPG-FINGERPRINT>"
git config gcrypt.gpg-args "--no-tty"
```

Without the GPG key, the clone fails. Without the git-crypt key, file contents are unreadable.

## Verify

- Auto-commit timer is active: `systemctl --user list-timers vault-autocommit.timer`
- Deploy key push works: `cd ~/Projects/vault && git push --dry-run origin main`
- Encryption: the GitHub repo shows only opaque encrypted data (no readable filenames or content)

## Next steps

- [SETUP-MIRROR.md](SETUP-MIRROR.md): tier 3, public template mirror via post-commit sync.
