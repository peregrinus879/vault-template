# AGENTS.md - vault

Zettelkasten knowledge vault for Obsidian and obsidian.nvim: Syncthing sync, git-crypt encryption, and systemd auto-commit. Syncthing runs over Tailscale with a headless Linux server as the always-on hub. Encrypted content backed up to GitHub via the auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten permanent notes, daily journals, fleeting notes, project charters, meeting notes, and literature notes
- Obsidian app configuration (`.obsidian/`)
- Note templates
- Index notes (curated entry points into note clusters)

It does not own:

- Neovim plugin configuration (lives in `dotfiles-arch` and `dotfiles-omarchy`)
- Syncthing configuration (system service on the remote hub)
- Git auto-commit timer (systemd user unit on the remote hub)
- Public template repo (`vault-template`); synced automatically via post-commit hook

## Key Files

- [README.md](README.md) - vault structure, methodology, templates, sync, security
- [WORKFLOW.md](WORKFLOW.md) - naming conventions, note creation, processing workflow, keybindings
- [SETUP.md](SETUP.md) - full setup guide with commands and app links for all devices
- `AGENTS.md` - canonical assistant context (this file)
- `CLAUDE.md` - thin Claude Code wrapper importing `AGENTS.md`
- `.git/hooks/post-commit` - auto-sync hook for public template repo

## Commit Policy

Only commit `8-templates/`, docs, and config. All other content is captured by the hourly auto-commit timer.

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
4. **obsidian.nvim config**: if directory paths changed, verify `~/projects/repos/dotfiles/dotfiles-arch/nvim/.config/nvim/lua/plugins/obsidian.lua` and `~/projects/repos/dotfiles/dotfiles-omarchy/nvim/.config/nvim/lua/plugins/obsidian.lua` have the correct `notes_subdir` and `daily_notes.folder` values. These files live in separate repos and must be updated and committed independently.

## Known Limitations

- **Obsidian file explorer**: repo docs (README.md, WORKFLOW.md, AGENTS.md, CLAUDE.md, SETUP.md) appear in the Obsidian sidebar. The `userIgnoreFilters` setting in `.obsidian/app.json` only hides files from search, graph, and link suggestions, not from the file explorer. No native fix exists as of 2026-04. Revisit if Obsidian adds explorer-level exclusion.
