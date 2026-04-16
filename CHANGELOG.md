# Changelog

All notable changes to the vault structure, templates, tooling, and documentation. Grouped by theme; within each, sorted Added / Changed / Removed. Dates in parentheses indicate when the theme's primary work landed.

## Post-audit round 3 accuracy (2026-04-16)

### Changed

- Pre-commit hook now derives `type:` from the top-level folder name (`3-permanent/foo.md` → `type: permanent`). Non-template-created notes get a correct value automatically; the field stays empty only when the folder does not match the `N-name` pattern.
- Pre-commit hook header rewritten to describe actual scope: "filler for missing required fields," explicit that it does not slugify filenames and does not rewrite existing values. Prevents the "normalizer" label from implying more than it delivers.
- `README.md` Synced list adds `LICENSE` (LICENSE is now in the private vault and in the rsync allowlist, was previously omitted from the doc).
- `AGENTS.md` Post-Change Verification step 2 mentions `.vault-template-marker` as an expected public-repo file.
- `SETUP.md` §1.7 documents the public-mirror constraint: `--delete` plus the orphan cleanup loop mean public-only items require an explicit rsync protect filter.
- `WORKFLOW.md` §Writing Notes clarifies what the pre-commit hook does and does not do (fills missing frontmatter; does not slugify or rewrite).

## Post-audit hardening round 2 (2026-04-16)

### Added

- Sentinel check in the post-commit hook. A new `.vault-template-marker` file in vault-template is the identity proof; the hook refuses to touch `$PUBLIC` unless the marker is present, guarding against a misconfigured `vault.publicPath` trashing an unrelated repo. Matching rsync protect filter preserves the marker from `--delete`.
- `LICENSE` (MIT, copied from vault-template) at the private vault root. Aligns with the public mirror; makes the existing `userIgnoreFilters` and `hide-root-docs` CSS rule describe real files rather than defensive no-ops.

### Changed

- Post-commit push no longer hardcodes `origin main`. Uses `git push --quiet` with upstream tracking so forks with different remote names or default branches work unchanged; push errors surface on stderr (were silently suppressed).
- Pre-commit frontmatter normalizer uses single-quoted YAML scalars (only `'` needs escaping), making filename-stem emission safe against colons, hashes, brackets, backslashes, and double quotes.
- Pre-commit content-directory list now derived from `.gitattributes` (same source post-commit uses). Adding a new content directory requires only a `.gitattributes` update, as the docs already claimed.
- `SETUP.md` §1.4 and §5.5 gcrypt signing config: `gcrypt.signingkey` → `user.signingkey`. The old key is not read by upstream git-remote-gcrypt, so signing was silently unpinned.
- `SETUP.md` §1.7 rsync rules table rewritten to reflect the sentinel check and the new protect filter.
- `SETUP.md` §4.3 Obsidian Mobile: note that mobile captures do not auto-apply templates; pull-down invokes the template picker.
- `README.md` Setup overview updated to match `SETUP.md`'s actual top-level structure (Prerequisites, 1-5, Verify, Appendix).
- `--filter='P LICENSE'` protect rule removed from `.githooks/post-commit`. LICENSE now lives in both repos; the rule's purpose (protect a public-only file from `--delete`) no longer applies.
- `daily-notes` core plugin disabled in `.obsidian/core-plugins.json` (was left enabled as stale config after the knowledge-vault restructure removed the daily-note workflow).

## Hook hardening and doc alignment (2026-04-16, external audit remediation)

### Added

- obsidian.nvim configuration reference appendix in SETUP.md — explicit snapshot for forks, with a banner naming the live source of truth (`dotfiles-arch`, `dotfiles-omarchy`).
- Deploy-key caveat in SETUP.md §1.5: `gh`-added keys may be removed if the authenticating `gh` session is revoked; verify after any credential rotation.

### Changed

- Post-commit hook: denylist → fail-closed allowlist. Only named root files, `6-templates/**`, `.githooks/**`, and public-safe `.obsidian/` subpaths publish. A new top-level file or directory no longer publishes by default.
- Post-commit hook: `VAULT` resolved via `git rev-parse --show-toplevel`; `PUBLIC` via `git config vault.publicPath` with fallback to the previous default. Works in any clone; forks override without editing the tracked script.
- Pre-commit frontmatter normalizer: CRLF-safe awk pattern (`---\r?$`), YAML values quoted to defend against filename characters.
- SETUP.md §1.4 gcrypt config corrected per upstream: participants and signing key are settable per-remote (`remote.<name>.gcrypt-*`) or repo-wide; the "remote keys unsupported" claim was inaccurate.
- SETUP.md §1.7 rsync rules table rewritten for the allowlist.
- WORKFLOW.md explorer note: `hide-root-docs` CSS snippet closes the prior "no native fix" limitation.
- AGENTS.md Hidden Files table: catch-all paragraph covering other tracked `.obsidian/` files so the authoritative claim holds.
- README §Public Template Synced list adds `CHANGELOG.md`.
- `.obsidian/app.json` `userIgnoreFilters` adds `CHANGELOG.md`.

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
- Post-commit hook migrated from `.git/hooks/post-commit` to a tracked location (initially `hooks/`; renamed to `.githooks/` in a later theme). Enabled on the hub via `git config core.hooksPath <path>`.

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
