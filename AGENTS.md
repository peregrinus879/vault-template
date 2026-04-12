# AGENTS.md - vault

Zettelkasten knowledge vault for Obsidian and Neovim (obsidian.nvim). Synced via Syncthing over Tailscale with a headless Linux server as the always-on hub. Backed up to GitHub via systemd auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten permanent notes, daily journals, fleeting captures, project notes, meeting notes, and source notes
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

## Reference

For vault structure, directory layout, methodology, templates, sync topology, security, and backup details, see [README.md](README.md).

## Workflow

- Capture quickly in `0-inbox/` without overthinking structure
- Process daily: review captures, promote to `3-zettelkasten/` or `2-sources/` if worth keeping
- Process weekly: write permanent notes, update MOCs if clusters emerge
- Always link: when writing in `3-zettelkasten/`, ask "what existing notes does this connect to?"
- Do not create MOCs preemptively; let them emerge from linked note clusters
- Move or rename notes only via neo-tree (nvim) or Obsidian's file explorer; both update `[[wiki-links]]` automatically. Do not use terminal `mv` or OS file managers as links will break.

## Known Limitations

- **Obsidian file explorer**: repo docs (README.md, AGENTS.md, CLAUDE.md, SETUP.md) appear in the Obsidian sidebar. The `userIgnoreFilters` setting in `.obsidian/app.json` only hides files from search, graph, and link suggestions, not from the file explorer. No native fix exists as of 2026-04. Revisit if Obsidian adds explorer-level exclusion.

## Neovim Usage

*This section applies to users of [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim). Skip if using Obsidian GUI only.*

obsidian.nvim only loads when a markdown file inside `~/vault/` is opened. Keybindings are not available until then. Start a vault session with `nvim ~/vault/0-inbox/` or use `<leader>od` to open today's daily note.

| Keys | Action |
|------|--------|
| `<leader>od` | Open/create daily note |
| `<leader>on` | New note (lands in `0-inbox/`) |
| `<leader>oo` | Find note (fuzzy search) |
| `<leader>os` | Search vault content |
| `<leader>ob` | Show backlinks |
| `<leader>ot` | Insert template |
| `<leader>ol` | Show links from current note |
| `<leader>op` | Paste image from clipboard |
