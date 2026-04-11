# AGENTS.md - vault

Knowledge vault using the Zettelkasten method. Edited in Neovim (obsidian.nvim) and Obsidian. Synced via Syncthing over Tailscale with a headless Linux server as the always-on hub. Backed up to GitHub via systemd auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten permanent notes, daily journals, project notes, meeting notes, and reference notes
- Obsidian app configuration (`.obsidian/`)
- Note templates
- Maps of Content (MOC index notes)

It does not own:

- Neovim plugin configuration (lives in `dotfiles-arch`)
- Syncthing configuration (system service on the remote hub)
- Git auto-commit timer (systemd user unit on the remote hub)
- Public template repo (`obsidian-vault`); synced automatically via post-commit hook

## Key Files

- `README.md` - structure, methodology, and overview
- `SETUP.md` - full setup guide with commands and app links for all devices
- `AGENTS.md` - canonical assistant context
- `CLAUDE.md` - thin Claude Code wrapper importing `AGENTS.md`
- `.git/hooks/post-commit` - auto-sync hook for public template repo

## Structure

```text
journal/          Daily notes and quick captures
projects/         Active project notes (time-bound)
  _archive/       Completed or paused projects
notes/            Permanent Zettelkasten notes (atomic, linked, tagged)
references/       Literature notes (books, articles, podcasts, videos)
meetings/         Meeting notes
maps/             Maps of Content (MOC index notes)
templates/        Note templates
assets/           Images and attachments
.obsidian/        Obsidian app configuration
```

## Methodology

This vault follows the Zettelkasten method:

- **Atomic notes**: each note in `notes/` captures one idea
- **Links over hierarchy**: `[[wiki-links]]` connect ideas; folders are just storage
- **Tags for retrieval, links for connection**: tags help find notes; links express relationships
- **Processing workflow**: capture in `journal/`, refine into `notes/` or `references/`, connect via `maps/`
- **MOCs are emergent**: create index notes in `maps/` when clusters of 5-10 related notes form naturally

## Templates

| Template | Target folder | Trigger |
|----------|--------------|---------|
| `daily.md` | `journal/` | `:Obsidian today` |
| `capture.md` | `journal/` | `:Obsidian new` (default landing) |
| `note.md` | `notes/` | Manual: insert template after creating note |
| `project.md` | `projects/` | Manual |
| `meeting.md` | `meetings/` | Manual |
| `reference.md` | `references/` | Manual |

## Sync Topology

```text
Mobile (Android)
      |
      | Syncthing over Tailscale
      |
Local machines ---- Syncthing over Tailscale ---- Remote hub (headless Linux) ---- GitHub (backup)
```

## Security

- Content directories are encrypted with [git-crypt](https://github.com/AGWA/git-crypt) (AES-256)
- Encrypted: `journal/`, `notes/`, `projects/`, `references/`, `meetings/`, `maps/`, `assets/`
- Unencrypted: `templates/`, `.obsidian/`, repo docs (`.gitignore`, `.stignore`, `.gitattributes`, `README.md`, `SETUP.md`, `AGENTS.md`, `CLAUDE.md`)
- Encryption is transparent locally; files appear as plaintext in the working directory
- GitHub sees ciphertext for encrypted paths; filenames remain visible
- The symmetric key must be backed up outside the vault and outside GitHub
- A dedicated deploy key (no passphrase) enables unattended push from the remote hub

## Backup

- Systemd timer (`vault-autocommit.timer`) runs hourly on the remote hub
- Commits all changes and pushes to GitHub via deploy key
- Syncthing provides real-time sync; git provides version history and off-site backup
- Local commits succeed even if push fails (network down); push retries next hour
- Post-commit hook syncs public-facing files (templates, config, docs) to the public template repo via rsync
- Content directories are excluded from sync; if a new content directory is added, update the hook's exclude list in `.git/hooks/post-commit`

## Workflow

- Capture quickly in `journal/` without overthinking structure
- Process daily: review captures, promote to `notes/` or `references/` if worth keeping
- Process weekly: write permanent notes, update MOCs if clusters emerge
- Always link: when writing in `notes/`, ask "what existing notes does this connect to?"
- Do not create MOCs preemptively; let them emerge from linked note clusters
- Move or rename notes only via neo-tree (nvim) or Obsidian's file explorer; both update `[[wiki-links]]` automatically. Do not use terminal `mv` or OS file managers as links will break.

## Neovim Usage

*This section applies to users of [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim). Skip if using Obsidian GUI only.*

obsidian.nvim only loads when a markdown file inside `~/vault/` is opened. Keybindings are not available until then. Start a vault session with `nvim ~/vault/journal/` or use `<leader>od` to open today's daily note.

| Keys | Action |
|------|--------|
| `<leader>od` | Open/create daily note |
| `<leader>on` | New note (lands in `journal/`) |
| `<leader>oo` | Find note (fuzzy search) |
| `<leader>os` | Search vault content |
| `<leader>ob` | Show backlinks |
| `<leader>ot` | Insert template |
| `<leader>ol` | Show links from current note |
| `<leader>op` | Paste image from clipboard |
