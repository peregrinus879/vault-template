# AGENTS.md - vault

Zettelkasten knowledge vault for Obsidian and obsidian.nvim: Syncthing sync, dual-layer encryption (git-crypt + git-remote-gcrypt), and systemd auto-commit. Syncthing runs over Tailscale with a headless Linux server as the always-on hub. Encrypted content backed up to GitHub via the auto-commit timer.

## Scope

This repo is a knowledge base, not a code project. It holds notes, not source code.

It owns:

- Zettelkasten fleeting notes, literature notes (source records with brief pointers), permanent notes (atomic evergreen claims), overview notes (curated narrative tours through topics), writing notes (long-form output)
- Obsidian app configuration (`.obsidian/`)
- Note templates (`5-templates/`)
- Vault-specific Neovim plugins (`nvim-vault/`): obsidian.nvim config and render-markdown.nvim (recommended companion). Canonical home for these files.
- Hub-only reference files (`infra/`): pinentry-null, systemd units
- Git hooks (`.githooks/`): note normalizer (pre-commit), public template sync (post-commit)

It does not own:

- Base Neovim configuration (LazyVim, colorscheme, personal plugins; user-managed outside this repo)
- Syncthing configuration (system service on the remote hub)
- Public template repo (`vault-template`); synced automatically via post-commit hook

## Key Files

- [README.md](README.md) - landing page: pitch, feature highlights, directory structure
- [SETUP-LOCAL.md](SETUP-LOCAL.md) - local setup: clone, Obsidian, version history and hooks, optional Neovim overlay
- [SETUP-SYNC.md](SETUP-SYNC.md) - tier 1: Syncthing hub and device pairing (Linux, Windows, Android)
- [SETUP-BACKUP.md](SETUP-BACKUP.md) - tier 2: dual-layer encrypted GitHub backup with hourly auto-commit; recovery
- [SETUP-MIRROR.md](SETUP-MIRROR.md) - tier 3: public template mirror via post-commit sync
- [WORKFLOW.md](WORKFLOW.md) - Zettelkasten method, naming conventions, capture loop, keybindings
- [DESIGN.md](DESIGN.md) - opinionated choices and the reasoning behind each
- `AGENTS.md` - canonical assistant context (this file)
- `CLAUDE.md` - thin Claude Code wrapper importing `AGENTS.md`
- `nvim-vault/.config/nvim/lua/plugins/obsidian.lua` - vault-specific obsidian.nvim config (canonical). Deviations from obsidian.nvim defaults enumerated in DESIGN.md §12.
- `nvim-vault/.config/nvim/lua/plugins/render-markdown.lua` - recommended markdown rendering (not required by obsidian.nvim)
- `infra/pinentry-null` - headless pinentry for unattended GPG operations
- `infra/vault-autocommit.service` - systemd oneshot for auto-commit
- `infra/vault-autocommit.timer` - hourly trigger for auto-commit
- `.githooks/pre-commit` - note normalizer for staged notes in content directories (delegates to `.githooks/lib/normalize.py --apply`)
- `.githooks/post-commit` - auto-sync hook for public template repo (enable with `git config core.hooksPath .githooks` on the hub)
- `.githooks/lib/normalize.py` - **single source of truth for note normalization**. Called by the pre-commit hook (on every commit), by the `<leader>o<space>` slug-rename orchestrator (`--apply`), and by the `<leader>op` promotion orchestrator (`--reapply`). Modes: `--apply` (no frontmatter → full template; frontmatter present + body has no `## ` → insert template body sections after H1, wrap pre-existing content in `## Capture`; frontmatter present + body has ≥1 `## ` → fill only), `--reapply` (force-apply target template regardless of body state; preserves existing `## Capture` block or wraps body in a new one), `--fill` (canonicalize frontmatter, ensure body H1, sync `aliases[0]` with H1; prints modified paths to stdout), `--check` (report problems including unsubstituted `{{...}}` placeholders; non-zero exit). Any change to normalization behavior must go here. See DESIGN.md §11 for the identity model.

## Commit Policy

Only commit `5-templates/`, `nvim-vault/`, `infra/`, docs, `.githooks/`, and config. All other content is captured by the hourly auto-commit timer.

## Conventions

Rules about how we name and describe things across the repo. Precede the Invariants section because the terminology below is used there.

### Terminology: normalize vs canonical

- **Normalize** / **normalization**: the full note-shaping pipeline. Covers template body application, H1 insertion, `aliases[0]`↔H1 sync, frontmatter canonicalization, and (for `<leader>o<space>`) slug rename. The verb describes everything `normalize.py` does end-to-end.
- **Canonical** / **canonicalize**: the frontmatter schema only. The three-field order (`id`, `aliases`, `tags`), the `id` = filename stem rule, the `aliases[0]` ↔ H1 bidirectional sync, the empty `tags: []` default. `build_canonical_fields` canonicalizes frontmatter. Normalizing a note *includes* canonicalizing its frontmatter, plus more.

Use "normalize" when describing the full pipeline or any superset of frontmatter work. Use "canonical" / "canonicalize" when the scope is specifically the frontmatter schema. Do not treat them as synonyms.

### Keybinding uppercase convention

When a lowercase/uppercase letter pair under `<leader>o` is a natural fit, uppercase = "the 'create a new note' variant of its lowercase sibling":

- `<leader>on` = new note (default); `<leader>oN` = new note from template picker
- `<leader>ol` = link text to existing note; `<leader>oL` = link text to new note

Not forced — applied only where the pair reads natural. Outside the "create new" family (e.g., `<leader>op` for promote), lowercase is the default letter. The convention lives in `nvim-vault/.config/nvim/lua/plugins/obsidian.lua`'s header comment.

### Keybinding desc strings

Keybinding `desc` strings are our own short forms, not verbatim mirrors of obsidian.nvim's shipped desc strings in `lua/obsidian/commands/init-legacy.lua`. The policy change is deliberate: upstream's shipped strings are verbose for which-key popups (e.g., "Rename note and update all references to it"); short forms improve readability, and we accept maintaining them ourselves.

When writing or editing a `desc`:

- Keep the imperative verb from upstream where possible ("Collect", "Link", "Rename", "Paste", "Switch").
- Drop articles ("a", "an", "the") unless dropping them hurts readability.
- Drop qualifiers already implied by context ("selected text" → "text" on a visual-mode binding; "within the current buffer" → "in buffer" on a per-note picker).
- Do not invent new verbs upstream does not use; stay close to obsidian.nvim's command naming so readers switching between our docs and upstream docs recognize the action.
- For custom orchestrators (`<leader>o<space>`, `<leader>op`), match the shipped-desc tone: primary verb(s) + object + optional "and <side-effect>" clause.

## Propagation Model

Three exclusion layers decide what propagates where:

| Layer | Controls | Defined in |
|---|---|---|
| `.gitignore` | What git tracks | `.gitignore` |
| `.stignore` | What Syncthing propagates between devices | `.stignore` |
| Rsync allowlist | What reaches the public `vault-template` mirror | `.githooks/post-commit` |

### Directory naming: dot-prefix rule

**Dot-prefix when an external tool imposes the directory name. Non-dot when this repo invents the name.**

| Directory | Imposed by | Effect |
|---|---|---|
| `.obsidian/` | Obsidian (vault config root) | Hidden by Obsidian from its own file explorer |
| `.githooks/` | git convention (`core.hooksPath` target) | Hidden |
| `.stfolder/` | Syncthing (folder sentinel) | Hidden |
| `.claude/` | Claude Code (per-project files) | Hidden |
| `.trash/` | Obsidian (soft-delete bucket) | Hidden |
| `nvim-vault/` | repo-invented (stow package name) | Visible; hidden explicitly (see below) |
| `infra/` | repo-invented (hub-only support files) | Visible; hidden explicitly (see below) |

Obsidian hides dot-prefixed entries from its file explorer automatically. For the two repo-invented infrastructure directories, Obsidian hiding is handled by `userIgnoreFilters` in `.obsidian/app.json` (search, graph, link suggestions) and `.obsidian/snippets/hide-root-docs.css` (file explorer sidebar, using `.nav-folder-title[data-path]` selectors). This is the coupling cost of choosing your own names; it is the reason a new non-dot infrastructure directory triggers invariant #10.

Content directories never start with a dot.

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
| `.syncthing.*.tmp` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Syncthing in-flight transfer files; disposable |
| `.trash/` | No (`.gitignore`) | No (`.stignore`) | No (rsync) | Obsidian soft-delete bucket |
| `nvim-vault/` | Yes | Yes | Yes | Neovim overlay (LazyVim stow package) |
| `infra/` | Yes | Yes | Yes | Hub-only reference files (pinentry, systemd units) |

Two patterns visible at a glance:

- **Fully shared** (all three Yes): config references that forks of `vault-template` need to reproduce the setup.
- **Fully excluded** (all three No): per-device state.
- **Tracked and synced but not public** (Yes/Yes/No): private note content. This is the one intentional asymmetry; content is excluded from `vault-template` by the rsync allowlist. Any other asymmetry across the three layers is worth investigating.

The `.obsidian/` directory is split by subpath rather than treated as a unit; rows above list the subfiles whose handling is interesting. All other tracked files under `.obsidian/` (`appearance.json`, `core-plugins.json`, `graph.json`, `snippets/**`) are fully shared, tracked in git, synced by Syncthing, included in `vault-template`. Themes are the exception: `themes/` is tracked and synced (so all your own devices see the same theme) but excluded from the public mirror so forks are not forced into your theme choice.

Private note content (files under `0-fleeting/`, `1-literature/`, `2-permanent/`, `3-overview/`, `4-writing/`, `6-assets/`) is tracked and synced but excluded from `vault-template` by the rsync allowlist (content dirs are not in the allowlist; structural `.gitkeep` stubs are recreated separately).

**When adding a new directory or file**, decide first whether it is per-device or shared, then update all three layers and the table above consistently. For visible infrastructure (no dot prefix), also update `userIgnoreFilters` in `.obsidian/app.json` and the CSS snippet at `.obsidian/snippets/hide-root-docs.css`. An inconsistency means one of the failure modes the layers exist to prevent.

## Invariants

Rules that must hold continuously. Each is a specific failure mode observed in past work; violating one silently breaks the setup in a way that is expensive to diagnose later. Pair with §Post-Change Verification below.

### Code and configuration

1. **`normalize.py` is the single source of truth for note normalization.** `.githooks/pre-commit`, `<leader>o<space>`, and `<leader>op` all delegate. Do not duplicate field or template logic in callers; changes go in `.githooks/lib/normalize.py`. The pre-commit hook is a thin shell wrapper; the `<leader>o<space>` and `<leader>op` keybindings are thin Lua orchestrators.
2. **Orchestrator splits (`<leader>o<space>`, `<leader>op`)**: each Lua keybinding is a thin sequencer. The filesystem primitive is chosen to match what is changing, and `normalize.py` owns body/frontmatter.
    - `<leader>o<space>`: `:Obsidian rename <slug>` owns filename rename + vault-wide `[[wikilink]]` rewrite; `normalize.py --apply` owns template body application, H1 insertion, and frontmatter canonicalization (including `aliases[0]`↔H1 sync).
    - `<leader>op`: `os.rename` owns the folder-only move; `normalize.py --reapply` owns target template application (with `## Capture` preservation) and frontmatter canonicalization.
    - **Name change vs folder move.** Backlinks in this vault resolve by filename stem + alias, so folder-only moves cannot break them and are safe through `os.rename`. Filename stem changes can break backlinks and must go through `:Obsidian rename` so that the vault-wide `[[wikilink]]` rewrite runs. Do not reintroduce `vim.fn.rename` / `os.rename` into `<leader>o<space>` for name changes; do not reintroduce `:Obsidian rename` into `<leader>op` (it would refuse the folder move, and the filename is not what's changing anyway).
    - (`<leader>or` is a pass-through to `:Obsidian rename` for free-form filename renames, not slug normalization.)
    - Preserve these splits. Do not fold body or frontmatter logic into either Lua orchestrator; the template and frontmatter rules live in `apply_file` / `reapply_file` / `fill_file` and nowhere else.
3. **`id` tracks the filename stem.** `normalize.py` enforces this on every run. Do not rewrite `id` to a free-form value expecting it to be preserved; the next commit will sync it back to the stem.
4. **Template placeholders must be single-quoted**: `id: '{{id}}'`, `aliases:\n  - '{{title}}'`. YAML 1.2 plain scalars cannot start with `{`, so unquoted `{{title}}` is invalid YAML even before substitution. Titles containing apostrophes break this after substitution; WORKFLOW rule 4 (ASCII-only titles) is the upstream workaround.
5. **`aliases[0]` is synced bidirectionally with body H1; `aliases[1..]` are preserved.** Obsidian writes `aliases: []` on template insert, not a missing field. `normalize.py` treats any empty form (`[]`, `[ ]`, `[  ]`, block-empty) as equivalent to missing. Whenever frontmatter is normalized, canonical `aliases[0]` = body H1 > caller-supplied fallback > filename stem. If both H1 and an existing aliases[0] are present and differ, H1 wins (aliases[0] is rewritten to match). User-added `aliases[1..]` (synonyms, historical names) are preserved with duplicates against aliases[0] removed. If the body has no `# H1` as its first non-blank line, `normalize.py` inserts `# {aliases[0]}` after the frontmatter. Do not add code that assumes "field present means populated" without going through `aliases_is_empty`.
6. **Canonical frontmatter is exactly `{id, aliases, tags}`.** Matches obsidian.nvim's default emitter shape (see DESIGN.md §9). Legacy notes carrying `type`/`created`/`updated` from the earlier six-field schema are preserved verbatim as unknown fields — `build_canonical_fields` emits the canonical trio first, then any unknowns in source order. Content folder names must still carry the `\d+-<name>` prefix because `derive_folder_type` maps `0-fleeting/` → `fleeting.md` for the `--apply` template lookup, but the folder-derived value is no longer written into frontmatter as `type:`.
7. **`normalize.py` stdout is reserved for modified file paths.** `--apply` and `--fill` print one path per modified file; unchanged files produce no stdout. The pre-commit hook reads stdout to re-stage. All diagnostic output (warnings, summaries, errors) must go to stderr, or the hook will mistake diagnostic lines for file paths and `git add` them.

### Change-control coordination

8. **Renaming a content directory requires updating four places**: `.gitattributes` (git-crypt rules, also drives hook derivation), `nvim-vault/.config/nvim/lua/plugins/obsidian.lua` (`customizations` routing), `README.md`, `WORKFLOW.md`. The post-commit hook picks up the change from `.gitattributes` automatically. If the rename affects the captured-to folder or any path mentioned in setup, also update the relevant setup doc(s) under `SETUP-LOCAL.md`, `SETUP-SYNC.md`, `SETUP-BACKUP.md`, `SETUP-MIRROR.md`. Run §Post-Change Verification afterward.
9. **Adding a new root-level file to the public mirror requires updating four places**: the rsync `--include` allowlist at the top of `.githooks/post-commit`, the `ALLOWED_ROOT_FILES` constant lower in the same file, `userIgnoreFilters` in `.obsidian/app.json` (so the file is hidden from Obsidian search/graph), and `.obsidian/snippets/hide-root-docs.css` (so it is hidden from the file explorer sidebar).
10. **Adding a new non-content root-level directory requires the above plus the orphan-cleanup skip-list** in `.githooks/post-commit` (the `case "$name" in ... continue ;;` line near the rsync invocation). Missing the skip-list entry causes the directory to be deleted on every sync. An inline comment in the hook flags this coupling.
11. **Pause the auto-commit timer before multi-stage structural changes** on the hub: `systemctl --user stop vault-autocommit.timer`; resume after with `systemctl --user start vault-autocommit.timer`. The timer fires on `*:00`; any work straddling the hour may be swept into an `auto:` commit with no descriptive message.

### Deployment and operation

12. **Editing `infra/vault-autocommit.service` does NOT redeploy.** The running timer uses the static copy at `~/.config/systemd/user/vault-autocommit.service`. After any edit to the source, redeploy: `cp ~/vault/infra/vault-autocommit.service ~/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user restart vault-autocommit.timer`.
13. **Every vault commit produces two commit lines in output**: one in the vault (your message), one `sync: YYYY-MM-DD-HHMM` in the public mirror (from `.githooks/post-commit`). This is expected; the public commit is a derived sync, not a duplicate of your work.
14. **Hooks run only where `core.hooksPath` is set.** `SETUP-LOCAL.md` §2 sets it locally for new forks; `SETUP-MIRROR.md` §4 enables it on the hub so the post-commit public sync runs. If a clone has no hooks configured, `pre-commit` normalization and `post-commit` public sync both no-op silently.

## Post-Change Verification

After any change that adds, renames, or moves content directories, modifies `.gitattributes`, or edits the post-commit hook, you **must** verify no private content can leak. Not every change requires this; routine note edits and template tweaks do not. Use judgment: if the change could affect what gets encrypted or what gets synced to the public repo, run the checks.

### When to verify

- Adding, renaming, or removing a content directory
- Editing `.gitattributes` (git-crypt encryption rules; also drives post-commit hook content directory derivation)
- Editing `.githooks/post-commit` (public repo sync logic)
- Editing `.obsidian/app.json` (default new-note folder, attachment folder, userIgnoreFilters) or `.obsidian/templates.json`
- Editing `.stignore` (Syncthing propagation rules; affects what reaches other devices)
- Changing `.gitignore`, `.stignore`, or the rsync allowlist in `.githooks/post-commit` (update the per-item state table in §Propagation Model)
- Editing GPG config (`~/.gnupg/gpg-agent.conf`) or `infra/pinentry-null`
- Adding, renaming, or reordering sections across `README.md`, `SETUP-LOCAL.md`, `SETUP-SYNC.md`, `SETUP-BACKUP.md`, `SETUP-MIRROR.md`, `WORKFLOW.md`, or `AGENTS.md`
- Any change that references directory paths in templates, docs, or config
- Completing a themed work pass (audit remediation, structural change, new hook or template, setup flow change): draft a `CHANGELOG.md` entry before declaring the work done, per §Changelog conventions

### What to check

1. **git-crypt encryption**: `git-crypt status` must show all files in content directories as `encrypted`. If any content file shows `not encrypted`, stop and fix `.gitattributes` before pushing.
2. **Public template repo**: `ls ~/projects/repos/templates/vault-template/` must show empty content directories (with `.gitkeep`), templates, config, docs, `nvim-vault/`, `infra/`, and the `.public-mirror-marker` sentinel file. No note content. Grep for any content that should not be there.
3. **Stale references**: `grep -rn '<old-name>' --include='*.md' --include='*.json' --include='*.css' . --exclude-dir=.git` must return no hits outside `.obsidian/workspace-mobile.json` (which Obsidian regenerates) and `CHANGELOG.md` (which preserves historical references).
4. **obsidian.nvim config**: if directory paths changed, verify `nvim-vault/.config/nvim/lua/plugins/obsidian.lua` has the correct `notes_subdir`, `templates.folder`, `attachments.folder`, and `templates.customizations` values.
5. **Doc cross-references and overviews**: cross-document references (section numbers, file names, headings) must resolve. `README.md` Documentation table must list all public docs. `AGENTS.md` Key Files descriptions must still match each doc's actual scope. Run `grep -rn 'step [0-9]\|§[0-9]' --include='*.md' .` and confirm every referenced section exists.

## Changelog conventions

`CHANGELOG.md` is theme-grouped, not per-commit. It lives in the private repo only (not synced to `vault-template`). Update it when a logical arc wraps, a session boundary, a coherent feature/fix bundle, an audit-remediation pass. Do not commit each non-trivial change with its own changelog line; git log is the per-commit record.

`README.md` §Highlights is the public-facing feature showcase. It updates only when user-visible capabilities change, not on the same cadence as `CHANGELOG.md`.

When adding a changelog entry:

- Place at the top of the file (newest first).
- Use a descriptive theme heading with an ISO date: `## Theme name (YYYY-MM-DD)`.
- Sort bullets under `### Added`, `### Changed`, `### Removed`.
- Reference commit hashes only for archaeological value (rarely).

Skip the changelog for: typo fixes, routine template content tweaks, auto-commit sweeps, and individual chore commits that don't close an arc.

Triggers for an update pass: end of a working session, completion of an audit or review, any commit that introduces a new note type, a new hook, a new config layer, or a visible workflow change.

## Known Limitations

- **Obsidian file explorer**: repo docs and infrastructure directories (README.md, WORKFLOW.md, SETUP-LOCAL.md, SETUP-SYNC.md, SETUP-BACKUP.md, SETUP-MIRROR.md, CHANGELOG.md, DESIGN.md, AGENTS.md, CLAUDE.md, LICENSE, `nvim-vault/`, `infra/`) would appear in the Obsidian sidebar by default. `userIgnoreFilters` in `.obsidian/app.json` only hides them from search, graph, and link suggestions, not from the file explorer. Workaround: the tracked CSS snippet at `.obsidian/snippets/hide-root-docs.css` (enabled in `.obsidian/appearance.json`) hides them via `display: none` rules targeting both `.nav-file-title[data-path]` (files) and `.nav-folder-title[data-path]` (directories). Enable per device in Settings > Appearance > CSS snippets if Obsidian does not pick up the config automatically.
- **Public repo commit messages must be opaque**: the post-commit hook uses `sync: <date>` for public template repo commits. Do not forward private repo commit messages to the public repo. Private commit messages may reference note names, topics, or other content that would leak through the public repo's git history.
- **No batch slug rename**: the pre-commit hook normalizes frontmatter and applies templates but does not slugify filenames (renaming breaks wiki-links and causes Syncthing churn). Slug normalization requires `<leader>o<space>` one file at a time. Future enhancement: extend `<leader>o<space>` to operate on multiple files (e.g., all notes in a directory), or add a separate hook/script that renames files in `0-fleeting/` only (low-risk: fleeting notes are temporary and rarely have backlinks).
- **Auto-commit timer can preempt planned commits**: `vault-autocommit.timer` fires hourly on the hub (`*:00`) and runs `git add -A`, commits any diff as `auto: <ts>`, and pushes. Push failures log to stderr (visible via `journalctl --user -u vault-autocommit`) but do not block the next tick. If a planned multi-stage change straddles the top of the hour, the timer will sweep staged changes into an `auto:` commit and push it before you can write a descriptive message. Before any structural change on the hub, pause the timer: `systemctl --user stop vault-autocommit.timer`. Restart after the planned commit: `systemctl --user start vault-autocommit.timer`. If the timer preempts anyway, prefer accepting the `auto:` message. Amending is allowed but requires force-push; reserve it for commits where the message loss is materially worse than a rewritten hash.

## Deferred Items

Items deliberately not done in past passes. Each carries a short rationale so future work can decide whether to reopen. Distinct from Known Limitations (which are structural constraints) and from CHANGELOG (which records what did happen).

### Decisions pending user input

- **Obsidian `bases` core plugin**. Obsidian 1.9 added the Bases core plugin (database views over frontmatter). Currently enabled in `.obsidian/core-plugins.json` but unused by the Zettelkasten workflow. Leaving it enabled costs nothing; disabling would match the `daily-notes` precedent (disabled as stale config). Decision deferred.

### Technical deferrals (low current value)

- **Data-driven vault path in `infra/vault-autocommit.service`**. The unit hardcodes `WorkingDirectory=%h/vault`. Forks using a different path edit the copied unit per `SETUP-BACKUP.md` §5. A systemd drop-in override (`~/.config/systemd/user/vault-autocommit.service.d/override.conf`) or `EnvironmentFile` would remove the manual edit but adds a config file for a single value. Revisit if a fork deviates from the `~/vault` convention.
- **Defensive reload after `:Obsidian rename` in `<leader>o<space>`**. The Lua orchestrator reads `vim.api.nvim_buf_get_name(0)` immediately after `:Obsidian rename` and assumes the buffer name reflects the new path. True in the current obsidian.nvim; a future upstream change to rename semantics would leave `normalize.py` running on a stale path. No defensive reload is implemented. Revisit if obsidian.nvim's rename contract changes.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history.
