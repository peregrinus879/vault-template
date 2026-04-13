# AGENTS.md - vault

Zettelkasten knowledge vault for Obsidian and Neovim (obsidian.nvim). Synced via Syncthing over Tailscale with a headless Linux server as the always-on hub. Backed up to GitHub via systemd auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten permanent notes, daily journals, fleeting notes, project notes, meeting notes, and literature notes
- Obsidian app configuration (`.obsidian/`)
- Note templates
- Index notes (curated entry points into note clusters)

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

- Capture quickly in `1-fleeting/` without overthinking structure
- Process daily: review fleeting notes, promote to `2-literature/` or `3-permanent/` if worth keeping
- Process weekly: write permanent notes, update index notes if clusters emerge
- Always link: when writing in `3-permanent/`, ask "what existing notes does this connect to?"
- Do not create index notes preemptively; let them emerge from linked note clusters
- Move or rename notes only via neo-tree (nvim) or Obsidian's file explorer; both update `[[wiki-links]]` automatically. Do not use terminal `mv` or OS file managers as links will break.

## Post-Change Verification

After any change that adds, renames, or moves content directories, modifies `.gitattributes`, or edits the post-commit hook, you **must** verify no private content can leak. Not every change requires this; routine note edits and template tweaks do not. Use judgment: if the change could affect what gets encrypted or what gets synced to the public repo, run the checks.

### When to verify

- Adding, renaming, or removing a content directory
- Editing `.gitattributes` (encryption rules)
- Editing `.git/hooks/post-commit` (public repo sync logic)
- Editing `.obsidian/daily-notes.json` or `.obsidian/templates.json` (folder paths)
- Any change that references directory paths in templates, docs, or config

### What to check

1. **git-crypt encryption**: `git-crypt status` must show all files in content directories as `encrypted`. If any content file shows `not encrypted`, stop and fix `.gitattributes` before pushing.
2. **Public template repo**: `ls ~/projects/repos/templates/vault-template/` must show only empty content directories (with `.gitkeep`), templates, config, and docs. No note content. Grep for any content that should not be there.
3. **Stale references**: `grep -rn '<old-name>' --include='*.md' --include='*.json' . --exclude-dir=.git` must return no hits outside `.obsidian/workspace-mobile.json` (which Obsidian regenerates).
4. **obsidian.nvim config**: if directory paths changed, verify `~/projects/repos/dotfiles/dotfiles-arch/nvim/.config/nvim/lua/plugins/obsidian.lua` has the correct `notes_subdir` and `daily_notes.folder` values. This file lives in a separate repo and must be updated and committed independently.

## Known Limitations

- **Obsidian file explorer**: repo docs (README.md, AGENTS.md, CLAUDE.md, SETUP.md) appear in the Obsidian sidebar. The `userIgnoreFilters` setting in `.obsidian/app.json` only hides files from search, graph, and link suggestions, not from the file explorer. No native fix exists as of 2026-04. Revisit if Obsidian adds explorer-level exclusion.

## Neovim Usage

*This section applies to users of [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim). Skip if using Obsidian GUI only.*

obsidian.nvim only loads when a markdown file inside `~/vault/` is opened. Keybindings are not available until then. Start a vault session with `nvim ~/vault/0-daily/` or use `<leader>od` to open today's daily note.

| Keys | Action |
|------|--------|
| `<leader>od` | Open/create daily note |
| `<leader>on` | New note (lands in `1-fleeting/`) |
| `<leader>oo` | Find note (fuzzy search) |
| `<leader>os` | Search vault content |
| `<leader>ob` | Show backlinks |
| `<leader>ot` | Insert template |
| `<leader>ol` | Show links from current note |
| `<leader>op` | Paste image from clipboard |
