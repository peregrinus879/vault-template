# Setup: Multi-device sync (Syncthing)

Add real-time file sync across Linux desktops, Windows (native + WSL), and Android. An always-on Linux hub acts as the central Syncthing peer so devices sync asynchronously without needing to be online at the same time. No cloud dependency; all traffic stays on the private Tailscale mesh.

**Prerequisite**: [SETUP-LOCAL.md](SETUP-LOCAL.md) on at least one machine (the vault repo must exist somewhere).

**What this adds**:

| Feature | Purpose |
|---|---|
| Hub Syncthing | Always-on Syncthing peer so devices sync asynchronously |
| Device pairing (Linux, Windows, Android) | Each client syncs with the hub |
| Tailscale-hardened transport | All sync traffic stays on the private mesh |

**Prerequisites**:

- **Arch Linux** on the remote hub (headless, always-on).
- **[Tailscale](https://tailscale.com/)** installed and connected on all devices (hub and clients).

This guide standardizes on `~/vault` for the hub. If you use a different location, adjust the paths accordingly.

## 1. Hub Syncthing

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

### 1.1 Enable versioning on the vault folder (recommended)

Syncthing can keep a rotating history of replaced and deleted files on the hub. This gives a cheap hub-local recovery path for accidental deletes or bad edits that would otherwise require pulling from the encrypted git remote.

Apply via the REST API (headless-friendly; no GUI required):

```bash
APIKEY=$(grep -oP '(?<=<apikey>)[^<]+' ~/.local/state/syncthing/config.xml \
  || grep -oP '(?<=<apikey>)[^<]+' ~/.config/syncthing/config.xml)

curl -sS -X PATCH -H "X-API-Key: $APIKEY" -H "Content-Type: application/json" \
  http://127.0.0.1:8384/rest/config/folders/vault \
  -d '{"versioning":{"type":"simple","params":{"keep":"10"},"cleanupIntervalS":3600}}'
```

**Where versions are saved**: `.stversions/` at the vault root, mirroring the original path with a timestamp suffix on the filename:

```
.stversions/
├── 0-fleeting/
│   └── Notes~20260422-001234.md
├── 1-literature/
│   └── ...
```

Properties of that location (already captured in `AGENTS.md` Propagation Model):

- **Decrypted content** — copies come from the working tree, not git-crypt blobs; `cat` works directly.
- **Hub-local** — `.stversions/` is in `.stignore`, so versioned copies never propagate to other devices.
- **Never committed** — `.stversions/` is in `.gitignore`; the autocommit ignores it.
- **Never mirrored** — not in the rsync allowlist; stays out of `vault-template`.
- **Auto-cleaned** — versions past the 10-keep limit are pruned on the hourly cleanup tick.

**Recovery procedure** when a file is lost or clobbered:

```bash
# List available versions for a specific path
ls '~/vault/.stversions/0-fleeting/'

# Restore the one you want
cp '~/vault/.stversions/0-fleeting/Notes~20260422-001234.md' \
   '~/vault/0-fleeting/Notes.md'
```

Syncthing treats the restored file as a normal working-tree change and propagates it to all connected devices on the next sync tick.

**Recovery precedence** (cheapest to most expensive):

1. **Obsidian file recovery plugin** on the device you last edited on (Command Palette → "File recovery: Open"). Per-device snapshots, finest granularity.
2. **Hub `.stversions/`** (this section). Last 10 versions, hub-local, no keys required.
3. **Encrypted git remote** (see [SETUP-BACKUP.md](SETUP-BACKUP.md) §6 Recovery). Full history, requires GPG + git-crypt keys.

## 2. Pair devices with the hub

Each client device needs Syncthing installed and paired with the hub. Wait for the initial sync to complete (Syncthing UI shows "Up to Date") before moving on to any tier-2 work.

### 2.1 Linux

Install and enable Syncthing on the client:

```bash
sudo pacman -S syncthing
systemctl --user enable --now syncthing
```

Open `http://localhost:8384` and add the vault folder.

Pair with the hub. Each device needs the other's device ID. In the Syncthing web UI:

1. **Add Remote Device**: paste the hub's device ID
2. **Accept** the vault folder share when prompted
3. Set the folder path to the vault location on that device
4. Wait for initial sync to complete

For Tailscale-hardened sync (recommended), restrict this device to its Tailscale IP and disable NAT traversal, global discovery, local discovery, and relaying:

```bash
syncthing cli config options raw-listen-addresses 0 set tcp://<tailscale-ip>:22000
syncthing cli config options natenabled set false
syncthing cli config options global-ann-enabled set false
syncthing cli config options local-ann-enabled set false
syncthing cli config options relays-enabled set false
```

### 2.2 Windows

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

Do not run git auto-commit from WSL. Tier 2 puts git operations exclusively on the remote hub.

### 2.3 Android

1. Install [Obsidian](https://play.google.com/store/apps/details?id=md.obsidian) from Play Store.
2. Install [Tailscale](https://play.google.com/store/apps/details?id=com.tailscale.ipn) and sign in.
3. Install [Syncthing-Fork](https://github.com/Catfriend1/syncthing-android) via [Obtainium](https://github.com/ImranR98/Obtainium) (recommended) or [Play Store](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid).
4. Add the hub as a remote device (paste device ID, set address to `tcp://<hub-tailscale-ip>:22000`).
5. Accept the vault folder share; set path to device storage (e.g., `[int]/Obsidian/vault`).
6. Wait for initial sync to complete.
7. Open Obsidian, choose **Open folder as vault**, select the Syncthing folder.

Enable **Settings > Run Conditions > "Run on mobile data"** if you want sync on cellular. Off by default; symptom when off is "changes only propagate on WiFi". The vault is small (mostly markdown), so the cellular data cost is minimal. If `6-assets/` grows and that becomes a concern, cap transfer rates in **Settings > Advanced** or add `6-assets` to the device-local `.stignore` (trades data cost for per-device ignore drift).

Syncthing on Android pauses on battery saver. Do not rename or move notes from the Android Files app; use Obsidian's file explorer only.

On mobile, templates are not auto-applied. After creating a new note, swipe down (pull) to trigger the template picker. This behavior is configured by `mobilePullAction: insert-template` in `.obsidian/app.json` (already set in this template).

Confirm the default folder is `0-fleeting/` in Settings > Files and links > Default location.

### 2.4 Resolving sync conflicts

On first sync, Obsidian may write to `.obsidian/app.json` at the same time the hub version syncs, creating a `.sync-conflict-*` file. This is normal:

1. The live file is correct as-is
2. Delete the conflict file (the one with `sync-conflict` in the name)
3. Conflict files are ignored by `.gitignore` and will never be committed

## Verify

- Syncthing on the hub is running: `systemctl status syncthing@$USER`
- Every paired device shows "Up to Date" in its Syncthing UI
- A file edited on one device appears on another within seconds

## Next steps

- [SETUP-BACKUP.md](SETUP-BACKUP.md): tier 2, encrypted git backup to GitHub.
