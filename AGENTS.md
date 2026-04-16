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
- `.githooks/pre-commit` - frontmatter normalizer for staged notes in content directories
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

### Current state per item

| Item | In git | In Syncthing | In `vault-template` | Notes |
|---|---|---|---|---|
| `.claude/` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Claude Code per-device state |
| `.git/` | n/a (is git) | No (`.stignore`) | No (rsync) | Git internals |
| `.gitattributes` | Yes | Yes | Yes | git-crypt encryption rules; hook reads it at runtime |
| `.githooks/` | Yes | Yes | Yes | Tracked hook, enabled via `core.hooksPath` on the hub |
| `.gitignore` | Yes | Yes | Yes | Standard git ignore patterns |
| `.obsidian/app.json` | Yes | Yes | Yes | Shared Obsidian settings |
| `.obsidian/templates.json` | Yes | Yes | Yes | Templates folder pointer |
| `.obsidian/workspace.json` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Per-device UI layout |
| `.obsidian/workspace-mobile.json` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Per-device mobile UI layout |
| `.obsidian/cache` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Per-device search/graph cache |
| `.stfolder/` | No (`.gitignore`) | Syncthing's own marker | No (rsync) | Syncthing folder sentinel |
| `.stignore` | Yes | Yes | Yes | Syncthing ignore patterns |
| `.stversions/` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Syncthing versioning backups (transient) |
| `.trash/` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Obsidian soft-delete bucket |

Two patterns visible at a glance:

- **Fully shared** (all three Yes): config references that forks of `vault-template` need to reproduce the setup.
- **Fully excluded** (all three No): per-device state. Any asymmetry (Yes in two columns, No in one) is a design smell worth investigating.

The `.obsidian/` directory is split by subpath rather than treated as a unit; rows above list the subfiles whose handling is interesting. All other tracked files under `.obsidian/` (`appearance.json`, `core-plugins.json`, `graph.json`, `snippets/**`, `themes/**`) are fully shared — tracked in git, synced by Syncthing, included in `vault-template`.

Private note content (files under `0-fleeting/`, `1-sources/`, `2-literature/`, `3-permanent/`, `4-writing/`, `5-index/`, `7-assets/`) is tracked and synced but excluded from `vault-template` by the rsync allowlist (content dirs are not in the allowlist; structural `.gitkeep` stubs are recreated separately).

**When adding a new hidden directory or file**, decide first whether it is per-device or shared, then update all three layers and the table above consistently. An inconsistency means one of the failure modes the layers exist to prevent.

## Post-Change Verification

After any change that adds, renames, or moves content directories, modifies `.gitattributes`, or edits the post-commit hook, you **must** verify no private content can leak. Not every change requires this; routine note edits and template tweaks do not. Use judgment: if the change could affect what gets encrypted or what gets synced to the public repo, run the checks.

### When to verify

- Adding, renaming, or removing a content directory
- Editing `.gitattributes` (git-crypt encryption rules; also drives post-commit hook content directory derivation)
- Editing `.githooks/post-commit` (public repo sync logic)
- Editing `.obsidian/app.json` (default new-note folder, attachment folder) or `.obsidian/templates.json`
- Editing `.stignore` (Syncthing propagation rules; affects what reaches other devices)
- Changing `.gitignore`, `.stignore`, or the rsync excludes in `.githooks/post-commit` (update the per-item state table in §Hidden Files and Directories)
- Editing GPG config (`~/.gnupg/gpg-agent.conf`) or `~/.local/bin/pinentry-null`
- Adding, renaming, or reordering sections across `README.md`, `WORKFLOW.md`, `SETUP.md`, or `AGENTS.md`
- Any change that references directory paths in templates, docs, or config
- Completing a themed work pass (audit remediation, structural change, new hook or template, setup flow change): draft a `CHANGELOG.md` entry before declaring the work done, per §Changelog discipline

### What to check

1. **git-crypt encryption**: `git-crypt status` must show all files in content directories as `encrypted`. If any content file shows `not encrypted`, stop and fix `.gitattributes` before pushing.
2. **Public template repo**: `ls ~/projects/repos/templates/vault-template/` must show empty content directories (with `.gitkeep`), templates, config, docs, and the `.vault-template-marker` sentinel file. No note content. Grep for any content that should not be there.
3. **Stale references**: `grep -rn '<old-name>' --include='*.md' --include='*.json' . --exclude-dir=.git` must return no hits outside `.obsidian/workspace-mobile.json` (which Obsidian regenerates).
4. **obsidian.nvim config**: if directory paths changed, verify `~/projects/repos/dotfiles/dotfiles-arch/nvim/.config/nvim/lua/plugins/obsidian.lua` and `~/projects/repos/dotfiles/dotfiles-omarchy/nvim/.config/nvim/lua/plugins/obsidian.lua` have the correct `notes_subdir`, `templates.folder`, `attachments.folder`, and `templates.customizations` values. These files live in separate repos and must be updated and committed independently.
5. **Doc cross-references and overviews**: cross-document references (section numbers, file names, headings) must resolve. `README.md` §Setup overview must reflect `SETUP.md`'s top-level section structure. `AGENTS.md` Key Files descriptions must still match each doc's actual scope. Run `grep -rn 'step [0-9]\|§[0-9]' --include='*.md' .` and confirm every referenced section exists.

## Changelog discipline

`CHANGELOG.md` is theme-grouped, not per-commit. Update it when a logical arc wraps — a session boundary, a coherent feature/fix bundle, an audit-remediation pass. Do not commit each non-trivial change with its own changelog line; git log is the per-commit record.

When adding an entry:

- Place at the top of the file (newest first).
- Use a descriptive theme heading with an ISO date: `## Theme name (YYYY-MM-DD)`.
- Sort bullets under `### Added`, `### Changed`, `### Removed`.
- Reference commit hashes only for archaeological value (rarely).

Skip the changelog for: typo fixes, routine template content tweaks, auto-commit sweeps, and individual chore commits that don't close an arc.

Triggers for an update pass: end of a working session, completion of an audit or review, any commit that introduces a new note type, a new hook, a new config layer, or a visible workflow change.

## Known Limitations

- **Obsidian file explorer**: repo docs (README.md, WORKFLOW.md, AGENTS.md, CLAUDE.md, SETUP.md, CHANGELOG.md, LICENSE) would appear in the Obsidian sidebar by default. `userIgnoreFilters` in `.obsidian/app.json` only hides them from search, graph, and link suggestions, not from the file explorer. Workaround: the tracked CSS snippet at `.obsidian/snippets/hide-root-docs.css` (enabled in `.obsidian/appearance.json`) hides them via a `display: none` rule. Enable per device in Settings > Appearance > CSS snippets if Obsidian does not pick up the config automatically.
- **Public repo commit messages must be opaque**: the post-commit hook uses `sync: <date>` for public template repo commits. Do not forward private repo commit messages to the public repo. Private commit messages may reference note names, topics, or other content that would leak through the public repo's git history.
- **Auto-commit timer can preempt planned commits**: `vault-autocommit.timer` fires hourly on the hub (`*:00`) and runs `git add -A && git commit -m "auto: <ts>" && git push`. If a planned multi-stage change straddles the top of the hour, the timer will sweep staged changes into an `auto:` commit and push it before you can write a descriptive message. Before any structural change on the hub, pause the timer: `systemctl --user stop vault-autocommit.timer`. Restart after the planned commit: `systemctl --user start vault-autocommit.timer`. If the timer preempts anyway, prefer accepting the `auto:` message. Amending is allowed but requires force-push; reserve it for commits where the message loss is materially worse than a rewritten hash.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history.
