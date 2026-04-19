# Getting Started

Clone this template and start writing Zettelkasten notes. Choose the path that fits your setup.

## Choose your path

| Path | What you get | Time |
|---|---|---|
| **Obsidian only** | Full Zettelkasten template, works on desktop and mobile | 5 min |
| **Obsidian + Neovim** | Terminal editing with obsidian.nvim | +10 min |
| **Multi-device sync** | Real-time sync across Linux, Windows, Android via Syncthing | +20 min |

Each path builds on the previous. Start with Obsidian; add layers as needed. For encryption, automated backup, and public template mirroring, see [SELF-HOSTING.md](SELF-HOSTING.md).

## 1. Obsidian

### 1.1 Clone the template

```bash
git clone https://github.com/peregrinus879/vault-template.git ~/vault
cd ~/vault && rm -rf .git
```

Choose a different path if you prefer; the default is `~/vault`. If you add Neovim later, set the `OBSIDIAN_VAULT` environment variable to match (see §2).

### 1.2 Initialize version history (optional)

Initialize a fresh git repo for local version history and to enable the pre-commit frontmatter normalizer:

```bash
cd ~/vault
git init -b main
git config core.hooksPath .githooks
git add -A && git commit -m "init: vault from template"
```

The pre-commit hook calls `python3` for frontmatter normalization. Python 3 ships by default on Arch Linux, Ubuntu, macOS, and WSL. On native Windows, install from [python.org](https://www.python.org/downloads/) or via `winget install Python.Python.3`. If `python3` is not on `PATH`, the hook logs a warning and skips normalization; commits still succeed.

This requires a git identity. If not already configured:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Skip this step if you only want to use Obsidian without version history. The vault works without git.

### 1.3 Install Obsidian

**Linux** (Flatpak):

```bash
flatpak install flathub md.obsidian.Obsidian
```

Or download from [obsidian.md/download](https://obsidian.md/download).

**Windows**:

```powershell
winget install Obsidian.Obsidian
```

**Android**: install [Obsidian](https://play.google.com/store/apps/details?id=md.obsidian) from Play Store.

### 1.4 Open as vault

Open Obsidian. Choose **Open folder as vault** (not "Create new vault"). Select the cloned directory.

Settings to verify (Settings > Files and links):

- **Default location for new notes**: In the folder specified below > `0-fleeting`
- **Attachment folder path**: `6-assets`

These should already be set from the included `.obsidian/app.json`.

### 1.5 Write your first note

Press `Ctrl+N` (desktop) or tap `+` (mobile). The note lands in `0-fleeting/`. Type a thought and save.

See [WORKFLOW.md](WORKFLOW.md) for the full Zettelkasten method, naming conventions, and daily routine.

### 1.6 Mobile (Android)

On mobile, templates are not auto-applied. After creating a new note, swipe down (pull) to trigger the template picker. This behavior is configured by `mobilePullAction: insert-template` in `.obsidian/app.json` (already set in this template).

Confirm the default folder is `0-fleeting/` in Settings > Files and links > Default location.

## 2. Add Neovim

*Skip this section if you don't use Neovim.*

### 2.1 Prerequisites

**Neovim distribution**: [LazyVim](https://www.lazyvim.org/). The overlay assumes stock LazyVim defaults (blink.cmp for completion, snacks_picker for pickers). Older LazyVim installs may use fzf-lua, which obsidian.nvim also supports.

**System packages** (Arch Linux):

```bash
sudo pacman -S --needed neovim ripgrep stow
```

- `ripgrep` is required for `:Obsidian search` and completion
- `stow` is optional (for the overlay install method below)

**Clipboard support** for `:Obsidian paste_img`:

| Display server | Package |
|---|---|
| Wayland | `wl-clipboard` |
| X11 | `xclip` |
| WSL | `wsl-open` (also enables `:Obsidian open`) |

```bash
# Wayland (most modern Linux desktops)
sudo pacman -S wl-clipboard
```

**LazyVim starter** (skip if already installed):

```bash
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git
```

### 2.2 Install the overlay

The `nvim-vault/` directory is a stow-compatible overlay containing obsidian.nvim and render-markdown.nvim plugin specs. It layers on top of your existing LazyVim config.

**Option A: Stow** (recommended if you manage dotfiles with stow):

```bash
cd ~/vault && stow -v -t ~ nvim-vault
```

This creates symlinks in `~/.config/nvim/lua/plugins/` pointing to the vault's overlay files.

**Option B: Copy**:

```bash
cp ~/vault/nvim-vault/.config/nvim/lua/plugins/* ~/.config/nvim/lua/plugins/
```

### 2.3 Vault path

The overlay defaults to `~/vault`. If you cloned elsewhere, set the `OBSIDIAN_VAULT` environment variable:

```bash
# In ~/.bashrc, ~/.zshrc, or equivalent
export OBSIDIAN_VAULT="$HOME/notes"
```

### 2.4 Verify

```bash
nvim ~/vault/0-fleeting/test.md
```

Run `:checkhealth obsidian` inside Neovim. All checks should pass.

Try `<leader>on` to create a fleeting note, `<leader>oN` to create a note from a template.

## 3. Add multi-device sync

*Skip this section if you use one device only.*

Syncthing provides real-time file sync over a local network or [Tailscale](https://tailscale.com/) mesh. A headless Linux server can act as an always-on hub so devices sync asynchronously.

### 3.1 Linux

Install and enable Syncthing:

```bash
sudo pacman -S syncthing
systemctl --user enable --now syncthing
```

Open `http://localhost:8384` and add the vault folder.

### 3.2 Pair devices

Each device needs the other's device ID. In the Syncthing web UI:

1. **Add Remote Device**: paste the other device's ID
2. **Accept** the vault folder share when prompted
3. Set the folder path to the vault location on that device
4. Wait for initial sync to complete (check Syncthing UI for "Up to Date")

For Tailscale-hardened sync (recommended), restrict each device to its Tailscale IP and disable NAT traversal, global discovery, local discovery, and relaying:

```bash
syncthing cli config options raw-listen-addresses 0 set tcp://<tailscale-ip>:22000
syncthing cli config options natenabled set false
syncthing cli config options global-ann-enabled set false
syncthing cli config options local-ann-enabled set false
syncthing cli config options relays-enabled set false
```

### 3.3 Windows

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
3. Harden for Tailscale-only sync: go to **Actions** > **Settings** > **Connections**:
   - Set **Sync Protocol Listen Addresses** to `tcp://<tailscale-ip>:22000`
   - Uncheck **NAT Traversal**
   - Uncheck **Global Discovery**
   - Uncheck **Local Discovery**
   - Uncheck **Enable Relaying**
   - Save

Wait for initial sync to complete (check Syncthing UI for "Up to Date").

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

### 3.4 Android

1. Install [Tailscale](https://play.google.com/store/apps/details?id=com.tailscale.ipn) and sign in
2. Install [Syncthing-Fork](https://github.com/Catfriend1/syncthing-android) via [Obtainium](https://github.com/ImranR98/Obtainium) (recommended) or [Play Store](https://play.google.com/store/apps/details?id=com.github.catfriend1.syncthingandroid)
3. Add the hub as a remote device (paste device ID, set address to `tcp://<hub-tailscale-ip>:22000`)
4. Accept the vault folder share; set path to device storage (e.g., `[int]/Obsidian/vault`)
5. Wait for initial sync to complete
6. Open Obsidian, choose **Open folder as vault**, select the Syncthing folder

Syncthing on Android pauses on battery saver. Do not rename or move notes from the Android Files app; use Obsidian's file explorer only.

### 3.5 Resolving sync conflicts

On first sync, Obsidian may write to `.obsidian/app.json` at the same time the hub version syncs, creating a `.sync-conflict-*` file. This is normal:

1. The live file is correct as-is
2. Delete the conflict file (the one with `sync-conflict` in the name)
3. Conflict files are ignored by `.gitignore` and will never be committed

## Next steps

- [WORKFLOW.md](WORKFLOW.md): Zettelkasten method, naming conventions, capture loop, keybindings
- [FEATURES.md](FEATURES.md): full feature list
- [SELF-HOSTING.md](SELF-HOSTING.md): encryption, automated backup, public template mirroring
