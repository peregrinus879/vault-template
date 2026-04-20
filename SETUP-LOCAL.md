# Setup: Local vault (Obsidian + optional Neovim)

Run the Zettelkasten on a single machine with Obsidian on desktop and, optionally, obsidian.nvim in the terminal. No multi-device sync and no encrypted backup; for those layers, see [SETUP-HUB.md](SETUP-HUB.md).

This path takes 5 to 15 minutes depending on whether you add Neovim.

## 1. Clone the template

```bash
git clone https://github.com/peregrinus879/vault-template.git ~/vault
cd ~/vault && rm -rf .git
```

Choose a different path if you prefer; the default is `~/vault`. If you add Neovim later, set the `OBSIDIAN_VAULT` environment variable to match (see §3).

## 2. Initialize version history (optional)

Initialize a fresh git repo for local version history and to enable the pre-commit note normalizer:

```bash
cd ~/vault
git init -b main
git config core.hooksPath .githooks
git add -A && git commit -m "init: vault from template"
```

The pre-commit hook calls `python3` for note normalization (frontmatter, H1 sync, template body application). Python 3 ships by default on Arch Linux, Ubuntu, macOS, and WSL. On native Windows, install from [python.org](https://www.python.org/downloads/) or via `winget install Python.Python.3`. If `python3` is not on `PATH`, the hook logs a warning and skips normalization; commits still succeed.

This requires a git identity. If not already configured:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Skip this step if you only want to use Obsidian without version history. The vault works without git.

## 3. Install Obsidian

**Linux** (Flatpak):

```bash
flatpak install flathub md.obsidian.Obsidian
```

Or download from [obsidian.md/download](https://obsidian.md/download).

**Windows**:

```powershell
winget install Obsidian.Obsidian
```

Mobile install is covered in [SETUP-HUB.md](SETUP-HUB.md) §3.3, since a useful mobile setup requires sync.

## 4. Open as vault

Open Obsidian. Choose **Open folder as vault** (not "Create new vault"). Select the cloned directory.

Settings to verify (Settings > Files and links):

- **Default location for new notes**: In the folder specified below > `0-fleeting`
- **Attachment folder path**: `6-assets`

These should already be set from the included `.obsidian/app.json`.

## 5. Write your first note

Press `Ctrl+N` (desktop). The note lands in `0-fleeting/`. Type a thought and save.

See [WORKFLOW.md](WORKFLOW.md) for the full Zettelkasten method, naming conventions, and daily routine.

## 6. Add Neovim (optional)

*Skip this section if you don't use Neovim.*

### 6.1 Prerequisites

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

### 6.2 Install the overlay

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

### 6.3 Vault path

The overlay defaults to `~/vault`. If you cloned elsewhere, set the `OBSIDIAN_VAULT` environment variable:

```bash
# In ~/.bashrc, ~/.zshrc, or equivalent
export OBSIDIAN_VAULT="$HOME/notes"
```

### 6.4 Verify

```bash
nvim ~/vault/0-fleeting/test.md
```

Run `:checkhealth obsidian` inside Neovim. All checks should pass.

Try `<leader>on` to create a fleeting note, `<leader>oN` to create a note from a template.

## Next steps

- [WORKFLOW.md](WORKFLOW.md): Zettelkasten method, naming conventions, capture loop, keybindings.
- [SETUP-HUB.md](SETUP-HUB.md): multi-device sync, encrypted backup, public template mirroring.
