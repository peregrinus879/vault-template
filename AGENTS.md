# AGENTS.md - vault

Zettelkasten knowledge vault for Obsidian and Neovim (obsidian.nvim). Synced via Syncthing over Tailscale with a headless Linux server as the always-on hub. Backed up to GitHub via systemd auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten permanent notes, daily journals, fleeting captures, project notes, meeting notes, and reference notes
- Obsidian app configuration (`.obsidian/`)
- Note templates
- Maps of Content (MOC index notes)

It does not own:

- Neovim plugin configuration (lives in `dotfiles-arch`)
- Syncthing configuration (system service on the remote hub)
- Git auto-commit timer (systemd user unit on the remote hub)
- Public template repo (`vault-template`); synced automatically via post-commit hook

## Key Files

- `README.md` - structure, methodology, and overview
- `SETUP.md` - full setup guide with commands and app links for all devices
- `AGENTS.md` - canonical assistant context
- `CLAUDE.md` - thin Claude Code wrapper importing `AGENTS.md`
- `.git/hooks/post-commit` - auto-sync hook for public template repo

## Structure

```text
1-inbox/          Quick captures, fleeting notes (processing queue)
2-daily/          Daily journal notes (permanent chronological log)
3-notes/          Permanent Zettelkasten notes (atomic, linked, tagged)
4-references/     Literature notes (books, articles, podcasts, videos)
5-projects/       Active project notes (time-bound)
  _archive/       Completed or paused projects
6-meetings/       Meeting notes
7-maps/           Maps of Content (MOC index notes)
8-templates/      Note templates
9-assets/         Images and attachments
.obsidian/        Obsidian app configuration
```

## Methodology

This vault follows the Zettelkasten method:

- **Atomic notes**: each note in `3-notes/` captures one idea
- **Links over hierarchy**: `[[wiki-links]]` connect ideas; folders are just storage
- **Tags for retrieval, links for connection**: tags help find notes; links express relationships
- **Processing workflow**: capture in `1-inbox/`, refine into `3-notes/` or `4-references/`, connect via `7-maps/`
- **Numbered directories**: prefixes (1-9) enforce a logical display order across all tools
- **MOCs are emergent**: create index notes in `7-maps/` when clusters of 5-10 related notes form naturally

## Templates

| Template | Target folder | Trigger |
|----------|--------------|---------|
| `daily.md` | `2-daily/` | `:Obsidian today` |
| `capture.md` | `1-inbox/` | `:Obsidian new` (default landing) |
| `note.md` | `3-notes/` | Manual: insert template after creating note |
| `project.md` | `5-projects/` | Manual |
| `meeting.md` | `6-meetings/` | Manual |
| `reference.md` | `4-references/` | Manual |

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
- Encrypted: `1-inbox/`, `2-daily/`, `3-notes/`, `4-references/`, `5-projects/`, `6-meetings/`, `7-maps/`, `9-assets/`
- Unencrypted: `8-templates/`, `.obsidian/`, repo docs (`.gitignore`, `.stignore`, `.gitattributes`, `README.md`, `SETUP.md`, `AGENTS.md`, `CLAUDE.md`)
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
- Content directories are derived from `.gitattributes`; adding a new content directory only requires updating `.gitattributes`

## Workflow

- Capture quickly in `1-inbox/` without overthinking structure
- Process daily: review captures, promote to `3-notes/` or `4-references/` if worth keeping
- Process weekly: write permanent notes, update MOCs if clusters emerge
- Always link: when writing in `3-notes/`, ask "what existing notes does this connect to?"
- Do not create MOCs preemptively; let them emerge from linked note clusters
- Move or rename notes only via neo-tree (nvim) or Obsidian's file explorer; both update `[[wiki-links]]` automatically. Do not use terminal `mv` or OS file managers as links will break.

## Neovim Usage

*This section applies to users of [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim). Skip if using Obsidian GUI only.*

obsidian.nvim only loads when a markdown file inside `~/vault/` is opened. Keybindings are not available until then. Start a vault session with `nvim ~/vault/1-inbox/` or use `<leader>od` to open today's daily note.

| Keys | Action |
|------|--------|
| `<leader>od` | Open/create daily note |
| `<leader>on` | New note (lands in `1-inbox/`) |
| `<leader>oo` | Find note (fuzzy search) |
| `<leader>os` | Search vault content |
| `<leader>ob` | Show backlinks |
| `<leader>ot` | Insert template |
| `<leader>ol` | Show links from current note |
| `<leader>op` | Paste image from clipboard |
