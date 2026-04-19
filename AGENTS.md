# AGENTS.md - vault

Zettelkasten knowledge vault for Obsidian and obsidian.nvim: Syncthing sync, dual-layer encryption (git-crypt + git-remote-gcrypt), and systemd auto-commit. Syncthing runs over Tailscale with a headless Linux server as the always-on hub. Encrypted content backed up to GitHub via the auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten fleeting notes, literature notes (source records with brief pointers), permanent notes (atomic evergreen claims), overview notes (curated narrative tours through topics), writing notes (long-form output)
- Obsidian app configuration (`.obsidian/`)
- Note templates (`5-templates/`)
- Vault-specific Neovim plugins (`nvim-vault/`): obsidian.nvim config and render-markdown.nvim (recommended companion). Canonical home for these files.
- Self-hosting reference files (`self-hosting/`): pinentry-null, systemd units
- Git hooks (`.githooks/`): frontmatter normalizer (pre-commit), public template sync (post-commit)

It does not own:

- Base Neovim configuration (LazyVim, colorscheme, personal plugins; user-managed outside this repo)
- Syncthing configuration (system service on the remote hub)
- Public template repo (`vault-template`); synced automatically via post-commit hook

## Key Files

- [README.md](README.md) - landing page: pitch, feature highlights, directory structure
- [GETTING-STARTED.md](GETTING-STARTED.md) - setup guide: Obsidian, version history and hooks, Neovim overlay, multi-device sync
- [WORKFLOW.md](WORKFLOW.md) - Zettelkasten method, naming conventions, capture loop, keybindings
- [DESIGN.md](DESIGN.md) - opinionated choices and the reasoning behind each
- [FEATURES.md](FEATURES.md) - detailed feature showcase
- [SELF-HOSTING.md](SELF-HOSTING.md) - encryption, automated backup, public template mirroring
- `AGENTS.md` - canonical assistant context (this file)
- `CLAUDE.md` - thin Claude Code wrapper importing `AGENTS.md`
- `nvim-vault/.config/nvim/lua/plugins/obsidian.lua` - vault-specific obsidian.nvim config (canonical)
- `nvim-vault/.config/nvim/lua/plugins/render-markdown.lua` - recommended markdown rendering (not required by obsidian.nvim)
- `self-hosting/pinentry-null` - headless pinentry for unattended GPG operations
- `self-hosting/vault-autocommit.service` - systemd oneshot for auto-commit
- `self-hosting/vault-autocommit.timer` - hourly trigger for auto-commit
- `.githooks/pre-commit` - frontmatter normalizer for staged notes in content directories
- `.githooks/post-commit` - auto-sync hook for public template repo (enable with `git config core.hooksPath .githooks` on the hub)

## Commit Policy

Only commit `5-templates/`, `nvim-vault/`, `self-hosting/`, docs, `.githooks/`, and config. All other content is captured by the hourly auto-commit timer.

## Propagation Model

Three exclusion layers decide what propagates where:

| Layer | Controls | Defined in |
|---|---|---|
| `.gitignore` | What git tracks | `.gitignore` |
| `.stignore` | What Syncthing propagates between devices | `.stignore` |
| Rsync allowlist | What reaches the public `vault-template` mirror | `.githooks/post-commit` |

### Dot-prefixed infrastructure

Infrastructure directories use a dotfile prefix (`.obsidian/`, `.githooks/`, `.stfolder/`, `.claude/`, `.trash/`). The convention signals "not content" and is respected by Obsidian, which hides dotfile-prefixed entries from its file explorer. Content directories never start with a dot.

### Visible infrastructure

`nvim-vault/` and `self-hosting/` are infrastructure directories that do not use a dot prefix. They are intentionally visible on GitHub for discoverability by public template users. Obsidian hiding is handled by `userIgnoreFilters` in `.obsidian/app.json` (search, graph, links) and `.obsidian/snippets/hide-root-docs.css` (file explorer sidebar, using `.nav-folder-title[data-path]` selectors).

### Current state per item

| Item | In git | In Syncthing | In `vault-template` | Notes |
|---|---|---|---|---|
| `.claude/` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Claude Code per-device state |
| `.git/` | n/a (is git) | No (`.stignore`) | No (rsync) | Git internals |
| `.gitattributes` | Yes | Yes | Yes | git-crypt encryption rules; hook reads it at runtime |
| `.githooks/` | Yes | Yes | Yes | Tracked hooks, enabled via `core.hooksPath` on the hub |
| `.gitignore` | Yes | Yes | Yes | Standard git ignore patterns |
| `.obsidian/app.json` | Yes | Yes | Yes | Shared Obsidian settings |
| `.obsidian/templates.json` | Yes | Yes | Yes | Templates folder pointer |
| `.obsidian/workspace.json` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Per-device UI layout |
| `.obsidian/workspace-mobile.json` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Per-device mobile UI layout |
| `.obsidian/cache` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Per-device search/graph cache |
| `.obsidian/themes/` | Yes | Yes | No (rsync) | Local theme; excluded from the public mirror so forks choose their own theme |
| `.stfolder/` | No (`.gitignore`) | Syncthing's own marker | No (rsync) | Syncthing folder sentinel |
| `.stignore` | Yes | Yes | Yes | Syncthing ignore patterns |
| `.stversions/` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Syncthing versioning backups (transient) |
| `.trash/` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Obsidian soft-delete bucket |
| `nvim-vault/` | Yes | Yes | Yes | Neovim overlay (LazyVim stow package) |
| `self-hosting/` | Yes | Yes | Yes | Reference files for encryption and backup |

Two patterns visible at a glance:

- **Fully shared** (all three Yes): config references that forks of `vault-template` need to reproduce the setup.
- **Fully excluded** (all three No): per-device state.
- **Tracked and synced but not public** (Yes/Yes/No): private note content. This is the one intentional asymmetry; content is excluded from `vault-template` by the rsync allowlist. Any other asymmetry across the three layers is worth investigating.

The `.obsidian/` directory is split by subpath rather than treated as a unit; rows above list the subfiles whose handling is interesting. All other tracked files under `.obsidian/` (`appearance.json`, `core-plugins.json`, `graph.json`, `snippets/**`) are fully shared, tracked in git, synced by Syncthing, included in `vault-template`. Themes are the exception: `themes/` is tracked and synced (so all your own devices see the same theme) but excluded from the public mirror so forks are not forced into your theme choice.

Private note content (files under `0-fleeting/`, `1-literature/`, `2-permanent/`, `3-overview/`, `4-writing/`, `6-assets/`) is tracked and synced but excluded from `vault-template` by the rsync allowlist (content dirs are not in the allowlist; structural `.gitkeep` stubs are recreated separately).

**When adding a new directory or file**, decide first whether it is per-device or shared, then update all three layers and the table above consistently. For visible infrastructure (no dot prefix), also update `userIgnoreFilters` in `.obsidian/app.json` and the CSS snippet at `.obsidian/snippets/hide-root-docs.css`. An inconsistency means one of the failure modes the layers exist to prevent.

## Post-Change Verification

After any change that adds, renames, or moves content directories, modifies `.gitattributes`, or edits the post-commit hook, you **must** verify no private content can leak. Not every change requires this; routine note edits and template tweaks do not. Use judgment: if the change could affect what gets encrypted or what gets synced to the public repo, run the checks.

### When to verify

- Adding, renaming, or removing a content directory
- Editing `.gitattributes` (git-crypt encryption rules; also drives post-commit hook content directory derivation)
- Editing `.githooks/post-commit` (public repo sync logic)
- Editing `.obsidian/app.json` (default new-note folder, attachment folder, userIgnoreFilters) or `.obsidian/templates.json`
- Editing `.stignore` (Syncthing propagation rules; affects what reaches other devices)
- Changing `.gitignore`, `.stignore`, or the rsync allowlist in `.githooks/post-commit` (update the per-item state table in §Propagation Model)
- Editing GPG config (`~/.gnupg/gpg-agent.conf`) or `self-hosting/pinentry-null`
- Adding, renaming, or reordering sections across `README.md`, `GETTING-STARTED.md`, `SELF-HOSTING.md`, `WORKFLOW.md`, or `AGENTS.md`
- Any change that references directory paths in templates, docs, or config
- Completing a themed work pass (audit remediation, structural change, new hook or template, setup flow change): draft a `CHANGELOG.md` entry before declaring the work done, per §Changelog discipline

### What to check

1. **git-crypt encryption**: `git-crypt status` must show all files in content directories as `encrypted`. If any content file shows `not encrypted`, stop and fix `.gitattributes` before pushing.
2. **Public template repo**: `ls ~/projects/repos/templates/vault-template/` must show empty content directories (with `.gitkeep`), templates, config, docs, `nvim-vault/`, `self-hosting/`, and the `.vault-template-marker` sentinel file. No note content. Grep for any content that should not be there.
3. **Stale references**: `grep -rn '<old-name>' --include='*.md' --include='*.json' --include='*.css' . --exclude-dir=.git` must return no hits outside `.obsidian/workspace-mobile.json` (which Obsidian regenerates) and `CHANGELOG.md` (which preserves historical references).
4. **obsidian.nvim config**: if directory paths changed, verify `nvim-vault/.config/nvim/lua/plugins/obsidian.lua` has the correct `notes_subdir`, `templates.folder`, `attachments.folder`, and `templates.customizations` values.
5. **Doc cross-references and overviews**: cross-document references (section numbers, file names, headings) must resolve. `README.md` Documentation table must list all public docs. `AGENTS.md` Key Files descriptions must still match each doc's actual scope. Run `grep -rn 'step [0-9]\|§[0-9]' --include='*.md' .` and confirm every referenced section exists.

## Changelog discipline

`CHANGELOG.md` is theme-grouped, not per-commit. It lives in the private repo only (not synced to `vault-template`). Update it when a logical arc wraps, a session boundary, a coherent feature/fix bundle, an audit-remediation pass. Do not commit each non-trivial change with its own changelog line; git log is the per-commit record.

`FEATURES.md` is the public-facing feature showcase. It updates only when user-visible capabilities change, not on the same cadence as `CHANGELOG.md`.

When adding a changelog entry:

- Place at the top of the file (newest first).
- Use a descriptive theme heading with an ISO date: `## Theme name (YYYY-MM-DD)`.
- Sort bullets under `### Added`, `### Changed`, `### Removed`.
- Reference commit hashes only for archaeological value (rarely).

Skip the changelog for: typo fixes, routine template content tweaks, auto-commit sweeps, and individual chore commits that don't close an arc.

Triggers for an update pass: end of a working session, completion of an audit or review, any commit that introduces a new note type, a new hook, a new config layer, or a visible workflow change.

## Known Limitations

- **Obsidian file explorer**: repo docs and infrastructure directories (README.md, WORKFLOW.md, GETTING-STARTED.md, SELF-HOSTING.md, FEATURES.md, CHANGELOG.md, AGENTS.md, CLAUDE.md, LICENSE, `nvim-vault/`, `self-hosting/`) would appear in the Obsidian sidebar by default. `userIgnoreFilters` in `.obsidian/app.json` only hides them from search, graph, and link suggestions, not from the file explorer. Workaround: the tracked CSS snippet at `.obsidian/snippets/hide-root-docs.css` (enabled in `.obsidian/appearance.json`) hides them via `display: none` rules targeting both `.nav-file-title[data-path]` (files) and `.nav-folder-title[data-path]` (directories). Enable per device in Settings > Appearance > CSS snippets if Obsidian does not pick up the config automatically.
- **Public repo commit messages must be opaque**: the post-commit hook uses `sync: <date>` for public template repo commits. Do not forward private repo commit messages to the public repo. Private commit messages may reference note names, topics, or other content that would leak through the public repo's git history.
- **No batch slug rename**: the pre-commit hook fills missing frontmatter but does not slugify filenames (renaming breaks wiki-links and causes Syncthing churn). Slug normalization requires `<leader>or` one file at a time. Future enhancement: extend `<leader>or` to operate on multiple files (e.g., all notes in a directory), or add a separate hook/script that renames files in `0-fleeting/` only (low-risk: fleeting notes are temporary and rarely have backlinks).
- **Auto-commit timer can preempt planned commits**: `vault-autocommit.timer` fires hourly on the hub (`*:00`) and runs `git add -A && git commit -m "auto: <ts>" && git push`. If a planned multi-stage change straddles the top of the hour, the timer will sweep staged changes into an `auto:` commit and push it before you can write a descriptive message. Before any structural change on the hub, pause the timer: `systemctl --user stop vault-autocommit.timer`. Restart after the planned commit: `systemctl --user start vault-autocommit.timer`. If the timer preempts anyway, prefer accepting the `auto:` message. Amending is allowed but requires force-push; reserve it for commits where the message loss is materially worse than a rewritten hash.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history.
