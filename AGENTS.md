# AGENTS.md - vault

Zettelkasten knowledge vault for Obsidian and obsidian.nvim: Syncthing sync, dual-layer encryption (git-crypt + git-remote-gcrypt), and systemd auto-commit. Syncthing runs over Tailscale with a headless Linux server as the always-on hub. Encrypted content backed up to GitHub via the auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten fleeting notes, source notes (bibliographic records), literature notes (paraphrase), permanent notes (atomic claims), writing notes (long-form output), and index notes
- Obsidian app configuration (`.obsidian/`)
- Note templates
- Post-commit hook (`.githooks/post-commit`) for public template sync

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
- `.githooks/post-commit` - auto-sync hook for public template repo (enable with `git config core.hooksPath .githooks` on the hub)
- `~/.local/bin/pinentry-null` - headless pinentry for unattended GPG operations
- `~/.gnupg/gpg-agent.conf` - GPG agent config (pinentry-null)

## Commit Policy

Only commit `6-templates/`, docs, `.githooks/`, and config. All other content is captured by the hourly auto-commit timer.

## Hidden Files and Directories

Infrastructure directories use a dotfile prefix (`.obsidian/`, `.githooks/`, `.stfolder/`, `.claude/`, `.trash/`). The convention signals "not content" and is respected by Obsidian, which hides dotfile-prefixed entries from its file explorer. Content directories never start with a dot.

Three exclusion layers decide what propagates where:

| Layer | Controls | Defined in |
|---|---|---|
| `.gitignore` | What git tracks | `.gitignore` |
| `.stignore` | What Syncthing propagates between devices | `.stignore` |
| Rsync excludes | What reaches the public `vault-template` mirror | `.githooks/post-commit` |

**Per-device items** (local state, machine-specific UI, soft-deletes) must be in all three layers. Current examples: `.trash/`, `.claude/`, `.obsidian/workspace.json`, `.obsidian/workspace-mobile.json`, `.obsidian/cache`. Keeping the three layers aligned prevents sync conflicts (two devices writing to the same file) and cross-device state leakage (e.g., a trash restore on device A appearing on device B).

**Shared vault items** (templates, docs, tracked Obsidian config like `.obsidian/app.json` and `.obsidian/templates.json`, `.githooks/post-commit`, `.gitattributes`, `.stignore`) are tracked in git, synced by Syncthing, and included in `vault-template`. Private note content is tracked and synced but excluded from `vault-template` by rsync.

**When adding a new hidden directory or file**, decide first whether it is per-device or shared, then update all three layers consistently. An inconsistency means one of the failure modes above.

## Post-Change Verification

After any change that adds, renames, or moves content directories, modifies `.gitattributes`, or edits the post-commit hook, you **must** verify no private content can leak. Not every change requires this; routine note edits and template tweaks do not. Use judgment: if the change could affect what gets encrypted or what gets synced to the public repo, run the checks.

### When to verify

- Adding, renaming, or removing a content directory
- Editing `.gitattributes` (git-crypt encryption rules; also drives post-commit hook content directory derivation)
- Editing `.githooks/post-commit` (public repo sync logic)
- Editing `.obsidian/app.json` (default new-note folder, attachment folder) or `.obsidian/templates.json`
- Editing `.stignore` (Syncthing propagation rules; affects what reaches other devices)
- Editing GPG config (`~/.gnupg/gpg-agent.conf`) or `~/.local/bin/pinentry-null`
- Adding, renaming, or reordering sections across `README.md`, `WORKFLOW.md`, `SETUP.md`, or `AGENTS.md`
- Any change that references directory paths in templates, docs, or config

### What to check

1. **git-crypt encryption**: `git-crypt status` must show all files in content directories as `encrypted`. If any content file shows `not encrypted`, stop and fix `.gitattributes` before pushing.
2. **Public template repo**: `ls ~/projects/repos/templates/vault-template/` must show only empty content directories (with `.gitkeep`), templates, config, and docs. No note content. Grep for any content that should not be there.
3. **Stale references**: `grep -rn '<old-name>' --include='*.md' --include='*.json' . --exclude-dir=.git` must return no hits outside `.obsidian/workspace-mobile.json` (which Obsidian regenerates).
4. **obsidian.nvim config**: if directory paths changed, verify `~/projects/repos/dotfiles/dotfiles-arch/nvim/.config/nvim/lua/plugins/obsidian.lua` and `~/projects/repos/dotfiles/dotfiles-omarchy/nvim/.config/nvim/lua/plugins/obsidian.lua` have the correct `notes_subdir`, `templates.folder`, `attachments.folder`, and `templates.customizations` values. These files live in separate repos and must be updated and committed independently.
5. **Doc cross-references and overviews**: cross-document references (section numbers, file names, headings) must resolve. `README.md` §Setup overview must reflect `SETUP.md`'s top-level section structure. `AGENTS.md` Key Files descriptions must still match each doc's actual scope. Run `grep -rn 'step [0-9]\|§[0-9]' --include='*.md' .` and confirm every referenced section exists.

## Known Limitations

- **Obsidian file explorer**: repo docs (README.md, WORKFLOW.md, AGENTS.md, CLAUDE.md, SETUP.md) appear in the Obsidian sidebar. The `userIgnoreFilters` setting in `.obsidian/app.json` only hides files from search, graph, and link suggestions, not from the file explorer. No native fix exists as of 2026-04. Revisit if Obsidian adds explorer-level exclusion.
- **Public repo commit messages must be opaque**: the post-commit hook uses `sync: <date>` for public template repo commits. Do not forward private repo commit messages to the public repo. Private commit messages may reference note names, topics, or other content that would leak through the public repo's git history.
- **Auto-commit timer can preempt planned commits**: `vault-autocommit.timer` fires hourly on the hub (`*:00`) and runs `git add -A && git commit -m "auto: <ts>" && git push`. If a planned multi-stage change straddles the top of the hour, the timer will sweep staged changes into an `auto:` commit and push it before you can write a descriptive message. Before any structural change on the hub, pause the timer: `systemctl --user stop vault-autocommit.timer`. Restart after the planned commit: `systemctl --user start vault-autocommit.timer`. If the timer preempts anyway, prefer accepting the `auto:` message. Amending is allowed but requires force-push; reserve it for commits where the message loss is materially worse than a rewritten hash.

## Changelog

### Post-restructure polish (templates, infrastructure, docs)

- Standardize all templates: `type:` field per folder, inline YAML comments for enums, one-line section comments
- Split writing into `writing-short` and `writing-long` variants
- Rename `hooks/` to `.githooks/` so Obsidian hides it
- Align per-device state in `.stignore` with `.gitignore` and rsync excludes
- Document the dotfile-prefix convention and three-layer exclusion model in AGENTS

### Knowledge-vault restructure

- Drop daily, review, meeting, project-charter: vault is knowledge, not tracking
- Add `1-sources/` (Ahrens-style reference-note layer); literature notes link via `source: "[[...]]"`
- Renumber directories: 0-fleeting, 1-sources, 2-literature, 3-permanent, 4-writing, 5-index, 6-templates, 7-assets
- Migrate post-commit hook to a tracked location (now `.githooks/post-commit`)
- Drop `_archive/` subfolders; use status frontmatter instead

### Standalone setup documentation

- Make SETUP.md fully self-contained; declare prerequisites and install baseline tools in the guide
- Remove implicit dotfiles-arch dependency (still referenced as an optional shortcut)

### Dual-layer encryption migration

- Add git-remote-gcrypt as second encryption layer (encrypts filenames, history, tree)
- Rename GitHub repo from vault to vault-backup
- Add headless GPG config (dedicated key, pinentry-null, `gcrypt.gpg-args --no-tty`)
- Keep public repo commit messages opaque (`sync: <date>`)

### Vault restructuring

- Ahrens-style numeric-prefix directories; `[[wiki-links]]` replace Folgezettel numbering
- Add WORKFLOW.md as dual-editor tutorial
- Add git-crypt encryption, deploy keys, auto-commit timer, public template sync
