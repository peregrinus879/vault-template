# Changelog

All notable changes to the vault structure, templates, tooling, and documentation. Grouped by theme; within each, sorted Added / Changed / Removed. Dates in parentheses indicate when the theme's primary work landed.

## Post-restructure polish (2026-04-16)

### Added

- Pre-commit frontmatter normalizer hook (`.githooks/pre-commit`): injects missing `id`, `aliases`, `tags`, `type` fields into staged notes in content directories. Keeps the `type:` convention enforceable without requiring `<leader>or` every time. Auto-commit safe.
- CSS snippet `.obsidian/snippets/hide-root-docs.css` that hides repo documentation from Obsidian's file explorer (closes the prior `userIgnoreFilters` limitation).
- `.gitattributes` and `.stignore` now sync to `vault-template` as configuration references for forks. Closes a footgun where a forked hook would silently sync all note content because `.gitattributes` was missing.
- AGENTS.md §Hidden Files and Directories: authoritative per-item state table (git / Syncthing / vault-template) plus the three-layer exclusion model.
- AGENTS.md Known Limitation documenting the auto-commit timer preemption hazard (fires at `*:00`; may sweep in-progress work into an `auto:` commit with no descriptive message).
- `type:` field in all templates, matching folder name.
- Inline YAML `#` comments on enum-valued frontmatter fields (medium, identifier, status, source link, writing status).
- `writing-short` and `writing-long` template variants covering tweet-sized and longer-form compositions respectively.
- `<leader>or` slug-rename injects an empty `type:` field when missing, preserving existing values (handles non-template-created notes).
- WORKFLOW.md section clarifying the three nvim session entry patterns (bare, file arg, directory arg) and the `s`-for-split trick when opening on a directory.

### Changed

- `hooks/` renamed to `.githooks/` to match the dotfile convention for infrastructure (Obsidian hides dotfile-prefixed dirs).
- Template body HTML comments tightened to one line per section with aligned wording across templates.
- Per-device state (`.trash/`, `.claude/`, `.obsidian/workspace.json`, `.obsidian/workspace-mobile.json`, `.obsidian/cache`) added to `.stignore` so all three exclusion layers (git, Syncthing, rsync) agree.
- README.md §Security consolidated: the encrypted/unencrypted directory enumeration replaced by a one-sentence principle statement pointing at AGENTS.md's per-item table.

### Removed

- `writing-medium` template (tried briefly; mid-length pieces fit `writing-long` with empty Audience and Outline).

## Knowledge-vault restructure (2026-04-16)

### Added

- `1-sources/` directory and `source.md` template for bibliographic records (Ahrens reference-note layer).
- Literature notes now reference their source via `source: "[[slug]]"` wiki-link; one source can feed many literature notes.
- Inline per-quote locator conventions in literature notes (book/article: `p.N`; podcast/video: `MM:SS`; web: `§heading`).

### Changed

- Directory numbering tightened: `0-fleeting`, `1-sources`, `2-literature`, `3-permanent`, `4-writing`, `5-index`, `6-templates`, `7-assets`.
- Post-commit hook migrated from `.git/hooks/post-commit` to a tracked location; enabled on the hub via `git config core.hooksPath .githooks`.
- obsidian.nvim config in `dotfiles-arch` and `dotfiles-omarchy` aligned with the new folder layout and template customizations.

### Removed

- `0-daily/`, `5-projects/`, `6-meetings/` directories and their templates (`daily.md`, `review.md`, `meeting.md`, `project-charter.md`). The vault is a knowledge base, not a tracking system.
- Weekly review ritual; trigger questions absorbed into WORKFLOW.md as periodic self-check prompts without cadence.
- `_archive/` subfolders; status frontmatter replaces folder-based state.
- `<leader>od` daily-note keybinding.
- `.obsidian/daily-notes.json`.

## Standalone setup documentation (2026-04-15)

### Added

- Neovim and LazyVim installation steps in local-machine and WSL sections of SETUP.md.
- Doc cross-references as a Post-Change Verification trigger in AGENTS.md.

### Changed

- SETUP.md made fully self-contained: prerequisites and baseline tool installs live in the guide itself instead of assuming `dotfiles-arch`. `dotfiles-arch` remains a shortcut, not a requirement.

## Dual-layer encryption migration (2026-04-15)

### Added

- `git-remote-gcrypt` as a second encryption layer. Remote encrypts filenames, directory structure, and commit history in addition to git-crypt's content encryption. GitHub sees only opaque data.
- Dedicated GPG key (`vault-backup`, ed25519 + cv25519 subkey, no passphrase) for unattended remote encryption.
- Headless GPG configuration (`~/.local/bin/pinentry-null`, `gpg-agent.conf` pinentry directive, `gcrypt.gpg-args --no-tty`).
- Password manager checklist covering 4 key files and 5 identifying values for recovery.
- Recovery workflow documented in SETUP.md §5 (fresh clone + gcrypt unlock + git-crypt unlock).

### Changed

- GitHub repo renamed: `vault` → `vault-backup`.
- Public repo commit messages kept opaque (`sync: <date>`); forwarding private messages would leak note names via the hook's public-repo history.

### Removed

- `.trash/` files from git tracking.

## Initial vault setup and Zettelkasten alignment (2026-04-10 to 2026-04-14)

### Added

- Vault initialized with git-crypt encryption on content directories.
- Deploy keys for unattended push to the private GitHub backup.
- systemd auto-commit timer (hourly on the hub) with post-commit hook triggering the public template sync.
- Public `vault-template` repo (renamed from `obsidian-vault`) synced via rsync from the hook; excludes derived automatically from `.gitattributes` with `.gitkeep` auto-management and orphan cleanup.
- Multi-device SETUP.md guide for Linux, Windows (native Syncthing), WSL, and Android.
- Windows Syncthing auto-start via hidden VBS script (no console, no taskbar entry).
- Syncthing hardening: Tailscale-only listener, NAT traversal disabled, global and local discovery disabled, relaying disabled.
- Leak testing procedure documented (fake notes, verify public repo does not receive them, clean up).
- Ahrens-style numeric-prefix directory layout; `[[wiki-links]]` replace Folgezettel numbering.
- WORKFLOW.md as a comprehensive dual-editor tutorial (Obsidian desktop/mobile and obsidian.nvim), with LazyVim essentials, buffer/split navigation, neo-tree guide, and split-based promotion workflow.
- Initial Zettelkasten template set: fleeting, source-adjacent (then merged), literature, permanent, writing, index, review, meeting, project-charter. Subsequent themes pruned some of these.
- Post-change verification checklist in AGENTS.md.
- `<leader>or` keybinding for slug-renaming notes created outside obsidian.nvim (mobile captures, neo-tree `a`).
- Status lifecycle documentation for note types that carry `status:` (writing, meeting).
- AGENTS.md Known Limitation noting Obsidian's file explorer not respecting `userIgnoreFilters` (later resolved in Post-restructure polish via CSS snippet).

### Changed

- Templates rewritten to obsidian.nvim conventions: slug filenames (lowercase kebab-case), `aliases:` preserving the human-readable title, trimmed section comments.
- AGENTS.md deduplicated; shared sections reference README.md rather than restating.
- Status lifecycles tightened per Ahrens methodology (removed fleeting status; added meeting lifecycle; reordered tables to match folder numbering).
- `project` template renamed to `project-charter` for PMI/PRINCE2/AACE alignment (later removed in Knowledge-vault restructure).
- Directory naming iterated several times before settling (journal → inbox/daily, notes → zettelkasten, maps → mocs, then Ahrens terms). History preserved; final state is what matters for new forks.
