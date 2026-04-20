# Design

Opinionated choices in this vault, with the reasoning behind each. The tutorial (`WORKFLOW.md`) tells you *what* to do. This document explains *why* the vault is shaped the way it is, so you can decide whether each choice fits your work before forking.

Every section follows the same form: **Decision → Rationale → Alternatives considered → When to revisit**.

## 1. Numeric prefixes on content directories

**Decision**. Content directories are numbered in processing order: `0-fleeting/`, `1-literature/`, `2-permanent/`, `3-overview/`, `4-writing/`. Infrastructure directories follow (`5-templates/`, `6-assets/`).

**Rationale**. The Zettelkasten workflow is sequential: capture (fleeting) and reading (literature) feed synthesis (permanent), which feeds output (writing). Numbering the directories in that order gives Obsidian's file explorer a left-to-right workflow hint: "where does this new thought go?" is answered by walking the sidebar top-to-bottom. A beginner learning the method sees the steps in the right order.

The numbering reflects **sequence**, not **importance**. Permanent notes are where all lasting value lives; fleeting and literature exist to feed permanent. This is a doctrinal point worth repeating: importance and sequence are different axes, and the directory sort orders sequence.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Importance-first (`0-permanent, 1-literature, 2-fleeting`) | Fleeting appears last, but it is where most daily activity happens. Confuses "where do I put this?" for no analytical gain. |
| No numeric prefixes (`fleeting/, literature/, permanent/`) | Closer to Luhmann, but loses the sidebar workflow hint. Alphabetic order is an accident of English. |
| Two-digit prefixes (`00-fleeting, 10-literature, ...`) | Allows intermediate insertions. YAGNI at this directory count. |

**When to revisit**. If the method changes enough that sequence stops reflecting actual flow (e.g., if literature notes are abandoned entirely). Or if we ever exceed 10 top-level content directories, which is a sign the method has bloated.

## 2. One literature note per source (merged bibliography and notes)

**Decision**. Each source (book, paper, podcast, talk) gets exactly one file in `1-literature/`. That file carries both the bibliographic record (`## Source` block: medium, author, year, identifier) and the reading notes (`## Summary`, `## Key ideas`). Key ideas are paraphrased, not quoted, by default.

**Rationale**. Luhmann kept a separate bibliography box (`Literaturkartei`, ~15,000 cards) alongside his slip-box. Each bibliography card held full citation data and a short list of page-locked pointers to ideas worth extracting. He went from bibliography card straight to permanent notes. There was no intermediate "literature note" type in the sense Ahrens uses it.

Ahrens, writing for a digital audience, collapses the two into one file per source. He adds paraphrase: the act of writing a source's ideas in your own words is itself a learning moment and avoids the collector's fallacy (stockpiling quotes without engagement).

Merging is more ergonomic in Obsidian than a physical box: search, backlinks, and `[[links]]` make the bibliographic layer cheap to reach without a separate file. Paraphrase-first is a direct adoption of Ahrens's advice.

Quotes are not forbidden. When exact wording matters (definitions, disputed phrasings, language you may want to cite verbatim later), quote with a locator. The rule is: **paraphrase by default, quote when the wording matters**.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Two layers (`references/` citation-only + `literature/` notes) | Luhmann-accurate but doubles the file count per source with no analytical benefit in Obsidian. |
| Quote-heavy literature notes with locators (Luhmann style) | Produces collectors, not thinkers. Ahrens's explicit warning. |
| Bibliographic metadata in frontmatter instead of body | Tried earlier; frontmatter bloats with per-type fields and breaks the unified schema (see §9). |

**When to revisit**. If reading volume grows to the point where separating raw pointers from developed notes reduces friction; at that point, promote `## Key ideas` to its own file per source.

## 3. One structure type: Overview (drop Index; use tags)

**Decision**. The `3-overview/` directory holds one note type: **Overview** (curated narrative tour through a topic, prose between links). Flat enumeration of all notes matching a keyword is handled by Obsidian's tag pane, not by hand-maintained index files.

**Rationale**. Three tools were in scope: tags, Index, MOC.

- **Tags** (Obsidian core): live, automatic, zero maintenance. Filtering every note carrying `#topic` is instant.
- **Index** (static note): a hand-maintained flat list of notes on a topic. Requires remembering to update.
- **MOC** (static note): a narrated tour with curated ordering and author synthesis. Updated when the narrative changes.

Index and tags do the same job, except tags do it automatically. A hand-maintained Index is redundant unless it carries curation (selective inclusion or deliberate ordering), which is really an MOC with thin prose. The distinction between Index and MOC was a judgment call on every note. That friction kills methods.

Dropping Index leaves two tools with a clean split:

- **Tags**: mechanical filtering. Every note carries 0-N tags. Obsidian's tag pane is the enumeration.
- **Overview**: curated narrative entry point. Exists only when a topic has enough interconnected notes that prose synthesis adds value.

The name "Overview" maps directly to Luhmann's `Übersichten` (overview notes) and is accurate in translation.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Keep MOC and Index as separate types | Perpetuates judgment-call friction. Tag pane already covers Index use cases. |
| Drop all structure notes; put overviews inside `2-permanent/` | Closer to Luhmann (Übersichten lived in the slip-box). Loses visual separation between atomic claims and narrative tours, which helps cognitive load in capital projects work. Sidebar folder kept for this reason. |
| MOC as the name (Obsidian community convention) | Acronym assumes reader knowledge. "Overview" is self-explanatory. |

**When to revisit**. If tags prove insufficient for filtering (e.g., filters that need AND across three tags that Obsidian's tag pane cannot express), Dataview or Bases queries become the fallback, not hand-maintained Index files.

## 4. No project-notes layer

**Decision**. The vault has no dedicated directory for project-scoped notes (e.g., meeting notes, working documents tied to a specific initiative with a start and end date).

**Rationale**. Ahrens describes four note types; the fourth is project notes: notes relevant to a specific project, kept separate from the slip-box, deleted when the project ends. This vault implements three of the four (fleeting, literature, permanent, with overview/writing as derived types) and deliberately omits project notes.

The omission is a scope declaration: this vault is a knowledge base, not a project tracker. Project tracking belongs in other tools (Notion, Jira, a dedicated PM system). Mixing project ephemera into a Zettelkasten risks:

- **Dilution**: half the notes have a six-month lifespan; the slip-box loses its permanent-storage character.
- **Boundary creep**: "project" becomes undefined; every temporary context wants its own folder.
- **Deletion anxiety**: permanent notes and project notes look alike after a year; users hesitate to delete either.

Long-form output (blog drafts, papers, reports) lives in `4-writing/`. Those are outputs of the slip-box, not projects tracked alongside it.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| `5-projects/` directory with a `project.md` template | Tried in an earlier iteration; removed. Bloated the vault and blurred the knowledge-base boundary. |
| Project context inside tags (`#project/alpha`) | Acceptable workaround if you must; no tooling needed. Kept as a user option, not a first-class structure. |

**When to revisit**. If the user's work shifts enough that project tracking is the dominant use case. At that point, consider a separate Obsidian vault for projects, not a folder in this one.

## 5. Slug filenames with readable aliases

**Decision**. Filenames are auto-generated lowercase-hyphenated slugs (`risk-appetite-is-a-board-level-choice.md`). The human-readable title lives in the `aliases` frontmatter field. Both Obsidian and obsidian.nvim resolve `[[wikilinks]]` through aliases.

**Rationale**. Three problems are solved together:

1. **Cross-platform safety**. Syncthing moves files across Linux (ext4), Windows (NTFS), and Android (exFAT/ext4). Each filesystem has different rules for which characters are legal in filenames. Slug (lowercase, hyphens, alphanumeric only) is the intersection of legal-everywhere. No smart quotes, no colons, no slashes, no em dashes ever surface in a filename.
2. **Rename stability**. Titles evolve ("Risk register entries need an owner" becomes "Risk registers decay without an owner"). If the filename tracked the title, every rename would touch `git log`, Syncthing queues, and every device's sync state. With slugs + aliases, renames happen in the alias field alone; filename can stay stable.
3. **Search ergonomics**. Obsidian's Quick Switcher and `[[link]]` autocomplete search aliases, not filenames. A user types "risk appetite" and finds the note instantly, even though the filename is hyphenated lowercase.

The `id` frontmatter field mirrors the filename stem. It is redundant with the filename but explicit (useful for Dataview/Bases queries and makes the slug visible to the reader).

The `slugify()` function that maps titles to filenames lives in `obsidian.lua`. Its exact transformation rules, known limitations (non-ASCII stripping, punctuation collision), and worked examples are documented in §11.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Filename = title (e.g., `Risk appetite.md`) | Breaks on Windows (colons, special characters). Rename-heavy: any title tweak rewrites the file. |
| Timestamp-prefix filenames (`20260419-risk.md`) | Luhmann-adjacent (via Folgezettel-style numeric IDs). Adds ugliness to every filename for a problem aliases already solve. |
| Plain slugs, no `id` field | Tooling (obsidian.nvim) expects `id`. Redundancy is cheap. |

**When to revisit**. If a filesystem in the sync chain (a new mobile platform, a cloud layer) imposes stricter rules than the current intersection, or if Obsidian changes its link-resolution model and aliases stop being the primary search key.

## 6. No Folgezettel; wiki-links replace numeric sequencing

**Decision**. Notes are not numbered with Luhmann's `1`, `1a`, `1a1`, `1a2`, `1b` scheme. Relatedness is expressed exclusively through `[[wikilinks]]`.

**Rationale**. Folgezettel was a physical-medium solution: Luhmann needed a way to insert a new card "near" a related one, and he needed a way to navigate from a card to its neighbors without an index. The numeric scheme provided both.

In Obsidian, both problems are solved differently:

- **Proximity**: `[[wikilinks]]` + graph view. Relatedness is a named edge, not a filesystem adjacency.
- **Navigation**: backlinks + outgoing links + search. Every note knows what links to it and where it points.

Adopting Folgezettel in a digital tool adds bookkeeping (assigning and maintaining numeric IDs, reordering on insertion) without unlocking anything the link graph does not already provide. It also locks the slug/filename (see §5) into a non-semantic identifier.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Full Folgezettel with manual numbering | Pure bookkeeping overhead. Adds friction without benefit in Obsidian. |
| Hybrid (slug filenames + soft Folgezettel in a tag `#z/1a2`) | Tried by some Zettelkasten-traditionalists. Doubles the representation of relatedness; rarely adds insight. |

**When to revisit**. Never, under this tool stack. If the vault migrates to a non-graph tool where link-based navigation is worse than numeric-proximity navigation, the calculus changes.

## 7. Three-layer propagation model

**Decision**. Three independent exclusion layers decide what flows where:

| Layer | Controls | File |
|---|---|---|
| `.gitignore` | What git tracks | `.gitignore` |
| `.stignore` | What Syncthing propagates between devices | `.stignore` |
| Rsync allowlist | What reaches the public `vault-template` mirror | `.githooks/post-commit` |

Each layer has a distinct job. The three are documented and cross-checked in `AGENTS.md` §Propagation Model.

**Rationale**. Early versions tried to collapse the three into one (e.g., "if git ignores it, Syncthing should too"). Every collapse broke something.

- Git history should not sync (waste of bandwidth, clobbers on mobile). `.git/` is in `.stignore`.
- Syncthing conflicts (`*.sync-conflict-*`) should not commit. In `.gitignore`.
- Private content should sync but not publish. In rsync allowlist (excluded), not in `.gitignore` (tracked) or `.stignore` (propagated).
- Per-device state (`.obsidian/workspace.json`) should be excluded from all three.

Layering is explicit. Every item in the vault is classifiable against each layer independently, and the AGENTS.md table shows the matrix. Inconsistency across layers is a sign of a bug; consistency is the default.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Single ignore file propagated to all three | Fails for the private-content-but-sync-between-devices case. No way to express "track, sync, exclude from public" in one file. |
| Public mirror driven by a separate private repo with filtered content | Extra machinery; rsync + allowlist is simpler and auditable. |

**When to revisit**. When a new propagation target appears (a fourth layer, e.g., a backup service with its own exclusion rules). Add the column to the matrix; keep the independence.

## 8. Dual-layer encryption (git-crypt + git-remote-gcrypt)

**Decision**. Two encryption layers before content reaches GitHub:

1. **git-crypt**: encrypts file contents in git objects (AES-256). Templates and config stay unencrypted.
2. **git-remote-gcrypt**: encrypts the entire remote, including filenames, directory structure, and commit history.

Together, GitHub sees only opaque encrypted data.

**Rationale**. git-crypt alone leaks metadata: filenames, directory structure, commit messages, and the SHA graph are all visible. For a knowledge vault containing capital projects notes, that metadata is sensitive (project names, client names, dates of engagement, topic clusters).

git-remote-gcrypt encrypts the remote as a single opaque blob. But it has no file-level granularity: without git-crypt inside, a user with the gcrypt key would see all content. Layering gives defense in depth:

- Compromise of the gcrypt key alone: GitHub content is decryptable to git-level visibility, but content is still git-crypt encrypted.
- Compromise of the git-crypt key alone: without the gcrypt key, the remote is unreadable.
- Both compromised: game over, same as any symmetric scheme.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| git-crypt only | Leaks filenames, directory structure, commit history. Not acceptable for client-sensitive material. |
| git-remote-gcrypt only | No file-level protection if the gcrypt key is exposed. |
| Self-hosted git with client-side encryption | Adds server maintenance. GitHub + dual-layer gets the same confidentiality with zero infrastructure. |

**When to revisit**. If an algorithm break appears against git-crypt's AES-256 or gcrypt's GPG. Or if a simpler tool emerges that provides both filename and content encryption as one layer (none known as of 2026-04).

## 9. Unified three-field frontmatter

**Decision**. Every note carries the same three frontmatter fields in this order: `id`, `aliases`, `tags`. No type-specific fields. Literature notes keep bibliographic metadata in the body under `## Source`, not in frontmatter. The schema intentionally matches the default output of obsidian.nvim's frontmatter emitter, so no Lua customization is needed and `normalize.py` re-emits in the same shape.

**Rationale**. Earlier iterations carried six fields (`id`, `aliases`, `type`, `created`, `updated`, `tags`). Each extra field earned its keep less than the last:

- **`type`** was folder-derived. Dataview / Bases queries work equally well with `FROM "2-permanent"` as with `WHERE type = "permanent"`. The field was a redundant copy of the path.
- **`created`** was useful in principle but never read in practice. Age-based triage of fleeting notes (the main imagined use case) is better served by `git log --diff-filter=A --format=%aI` or filesystem `mtime`.
- **`updated`** was reserved. No mechanism populated it; it sat empty forever.

Dropping the three unused fields aligns the schema with obsidian.nvim's default (`{id, aliases, tags}`). That alignment removes the need for a custom `note_frontmatter_func` on the Lua side, eliminates the Lua/Python dual-source-of-truth risk, and trims the normalizer's field logic.

| Field | Purpose |
|---|---|
| `id` | Slug of the filename. Tautological with filename; explicit for tooling. |
| `aliases` | Human-readable title(s). Drives search and `[[link]]` autocomplete. aliases[0] syncs with body H1; aliases[1..] preserved as user-added synonyms. |
| `tags` | User-defined classification. Free-form. |

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Keep six fields | Dead weight; `type`/`created`/`updated` never read in practice; maintenance cost for no gain. |
| Custom `note_frontmatter_func` to emit six fields in Lua | Duplicates canonical-schema logic across Python (normalize.py) and Lua (obsidian.lua); drift risk on any schema change. |
| Type-specific frontmatter per template (`status` on writing, `medium` on literature) | Fragments the normalizer; increases cognitive load; rejected as-was in the six-field iteration. |
| No frontmatter; parse title/tags from body | Loses link autocomplete, breaks Dataview queries, inconsistent with Obsidian conventions. |

**When to revisit**. If a cross-type field emerges that is genuinely load-bearing (e.g., `provenance` if the vault tracks capture device, or a mandatory `status` for writing notes that actually gets queried). Otherwise, three is enough — and matching obsidian.nvim's default is a stable target.

**Migration**. Notes carried over from the earlier six-field schema keep their `type`/`created`/`updated` values: `build_canonical_fields` preserves unknown fields after the canonical block. Clean-up is manual or opportunistic.

## 10. External sync and version control (not the Obsidian Git plugin)

**Decision**. Multi-device sync, version history, and public mirroring are handled by external infrastructure, not by the Obsidian Git community plugin or Obsidian Sync. Syncthing propagates file changes between devices in near real-time. A systemd timer on the hub commits and pushes to an encrypted GitHub backup hourly. A post-commit hook mirrors public-safe files to `vault-template`. Obsidian itself does not participate in the commit, push, or sync flow.

**Rationale**. Four concerns drive the split:

- **Automation must survive the editor being closed.** Mobile captures happen with Obsidian in the background; the hub commits while Obsidian is not running at all. Any plugin-based commit requires Obsidian to be open, which is incompatible with a headless hub and unreliable for devices that go to sleep.
- **Plugin dependencies are moving targets.** The Obsidian Git community plugin is maintained out-of-tree and can break on Obsidian API changes. systemd, bash, and git are stable over decades. A backup system whose failure mode is "plugin stopped working after an Obsidian update" is not a backup system.
- **Hub-centric architecture requires server-side commit.** The always-on Linux hub is the commit origin of record: it has the GPG key for gcrypt, the SSH deploy key, and the pinned GPG configuration. The Obsidian Git plugin is desktop-only and cannot run in this role. Commit must happen where the keys live.
- **Syncthing and git are different layers; a plugin conflates them.** Syncthing propagates changes continuously between devices (peer-to-peer, near real-time). Git records history snapshots and provides off-site backup (central, periodic). Conflating them in a desktop plugin creates race conditions: a plugin commit on one device can race with a Syncthing-delivered change from another device, producing merge conflicts inside the commit flow rather than at the sync layer where they are recoverable.

The result is a pipeline where each tool does one thing: Syncthing moves files between devices; git records history; rsync mirrors the public view; the Obsidian Git plugin is simply not part of it.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Obsidian Git community plugin | Desktop-only; dependent on a community plugin staying compatible with Obsidian; conflates sync with version control; cannot commit when Obsidian is closed. |
| Obsidian Sync (first-party paid service) | Paid subscription; closed vendor lock-in; no git history; no off-site backup we control; fine for users who only want "sync" but does not meet the backup or encryption goals here. |
| Git only, no Syncthing | Mobile commit is fraught (Android git is awkward); pull-before-edit workflows defeat the "capture speed" requirement; concurrent edits on two devices become merge conflicts instead of transparent sync. |
| Syncthing only, no git | No version history; no off-site backup; Syncthing's own conflict files accumulate with no authoritative source-of-truth to reconcile against. |
| Cloud storage sync (iCloud, Dropbox, OneDrive) | File corruption and conflict patterns vary by provider; no history beyond the provider's retention; data leaves the Tailscale mesh; defeats the encryption posture. |

**When to revisit**. If Obsidian ships a first-party automation API that exposes file-watcher hooks at the OS level (would let the plugin work headlessly); if the community Git plugin gains a headless server mode; or if the vault migrates off Obsidian entirely. Also revisit if the hub pattern is abandoned (e.g., moving to a per-device commit model), since that removes the main objection to a desktop-only plugin.

## 11. Identity and naming: filename, id, aliases, H1

**Decision**. Every note carries five distinct identity slots (four if you collapse `aliases` into one; the table splits its primary entry and synonym tail for clarity), each with a fixed role and update rule:

| Slot | Form | Role | Source of truth |
|---|---|---|---|
| Filename | Slug (lowercase-hyphens) | Filesystem primary key; cross-platform safe | User (`<leader>oS` or `:Obsidian rename`) |
| `id` frontmatter | Slug, mirrors filename | Query key for Dataview/Bases; self-describing identifier inside the file | Auto-synced from filename stem |
| `aliases[0]` | Readable | Primary link target; powers Quick Switcher and `[[` autocomplete | Bidirectional sync with body H1 (H1 wins) |
| `aliases[1..]` | Readable | User-added synonyms, shorthand, historical names | User-controlled; preserved verbatim |
| Body H1 (`# Title`) | Readable | Canonical display title in rendered views (reading mode, pandoc, GitHub, terminal) | User-controlled; drives aliases[0] |

Two invariants run across these slots, auto-enforced by `normalize.py`:

- **`id` = filename stem**, always.
- **`aliases[0]` = body H1**, bidirectional (H1 wins when both present).

**Rationale**. Each slot earns its place by solving a different problem:

- **Filename (slug)** is the filesystem identifier and the unit of sync (git, Syncthing, rsync). Slugs are the intersection of legal characters across ext4, NTFS, exFAT, and APFS — lowercase ASCII + hyphens. A user-typed title with a colon ("PMO: Owner or not?") silently fails on NTFS; the slug never has that problem. See §5 for the broader argument.
- **`id` frontmatter field** makes the canonical identifier visible *inside* the file. `head -5 note.md` shows the id without needing filesystem context. Dataview and Obsidian Bases queries use it as a stable filter key. obsidian.nvim's Note model references it. Redundancy with filename stem is intentional and cheap — auto-synced on every hook run.
- **`aliases[0]` as human-readable primary** separates "what the machine sees" (slug) from "what you type when linking" (readable form). Slugs are ugly in prose: `[[risk-appetite-is-a-board-level-choice]]` reads badly. aliases[0] is the natural form: `[[Risk appetite is a board-level choice]]`. Obsidian and obsidian.nvim resolve `[[link]]` against filename stems *and* aliases, so a note answers to either.
- **`aliases[1..]`** capture the real-world fact that one note often has multiple natural names: "PMO" and "Project Management Office," long claim-form and short reference form, historical names after renames, cross-language variants. A YAML list is the idiomatic shape.
- **Body H1** is what renders as the big visible title in Obsidian reading view, pandoc exports, MkDocs sites, GitHub markdown preview, and `cat note.md` in a terminal. The filename (slug) is unreadable for these purposes; aliases live in frontmatter (invisible in rendered markdown). H1 is the only portable readable title.

**Why H1 wins the sync**. When body H1 and `aliases[0]` disagree, the hook rewrites aliases[0] to match H1:

- H1 is user-visible (rendered large at the top of the note) and user-edited when the claim changes.
- aliases[0] is frontmatter — less visually salient, rarely edited directly.
- Users reliably update H1 when they revise; they often forget the alias.
- Making H1 authoritative minimizes drift.

`aliases[1..]` are preserved verbatim because they represent deliberate user intent (synonyms, historical names), not drift.

**Resolution hierarchy**. When Obsidian resolves `[[link-text]]`:

1. Exact match against any filename stem across the vault.
2. Exact match against any alias across the vault.
3. Fuzzy/ranked match as fallback.

`id` field and body H1 are not consulted for link resolution. They exist for query and display respectively.

**Slug function**. The `slugify()` function in `obsidian.lua` maps a human title to a filename:

1. Replace spaces with hyphens.
2. Strip every character that isn't ASCII alphanumeric or hyphen.
3. Collapse runs of hyphens into one.
4. Strip leading and trailing hyphens.
5. Lowercase.

| Input | Output |
|---|---|
| `Risk appetite is a board-level choice` | `risk-appetite-is-a-board-level-choice` |
| `Risk appetite: is it a board-level choice?` | `risk-appetite-is-it-a-board-level-choice` |
| `PMO!` | `pmo` |
| `EVM (earned value) on mega-projects` | `evm-earned-value-on-mega-projects` |
| `Ahrens 2022 - How to Take Smart Notes` | `ahrens-2022-how-to-take-smart-notes` |
| `Café résumé — smart?` | `caf-rsum-smart` (non-ASCII stripped) |

Known limitations:
- Non-ASCII characters (accents, Arabic, Cyrillic, emoji) strip to nothing. Titles in those scripts become empty or near-empty slugs, which collapses to stem-collision. Users writing non-English titles must transliterate before slugifying.
- Punctuation carries no information in the output. "Risk: response" and "Risk response" produce identical slugs; only meaningful for titles that differ only by punctuation.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| Single identity (filename = title verbatim) | Fails on Windows/NTFS (colons, special chars); rename-heavy; aliases already solve the visibility problem without filesystem risk. |
| Drop `id` field | obsidian.nvim's Note model expects it; Dataview queries are more stable; `id` lets a file describe itself without filesystem context. Auto-sync keeps the redundancy cheap. |
| H1 optional | Body H1 is the only portable readable title outside Obsidian. Without it, terminal/GitHub/pandoc readers see only the slug. |
| Single-scalar `aliases` | Notes legitimately answer to multiple names. List is the idiomatic shape; single-value forces the user to pick one. |
| `aliases[0]` authoritative (not H1) | Users edit H1 in the body more than aliases in frontmatter. Making aliases authoritative pushes sync burden onto users; H1-authoritative lets the hook catch drift. |
| Hook auto-rewrites body H1 | Too invasive for an unattended hook. User edits to H1 are respected as-is; alias drift is the only thing auto-fixed. |

**When to revisit**. If Obsidian changes its link resolution model (e.g., removes alias lookup); if a non-Obsidian editor becomes primary and its identity model differs; if `aliases[0] ↔ H1` bidirectional sync proves more confusing than the drift it prevents (monitor `normalize.py --check` output). The slug function's non-ASCII handling should be revisited if multilingual titles become common — transliteration at the slugify() level would solve the empty-slug problem.

## 12. obsidian.nvim overlay deviations

**Decision**. The Lua overlay at `nvim-vault/.config/nvim/lua/plugins/obsidian.lua` configures obsidian.nvim beyond naming the workspace. Every deviation from the plugin's defaults has a vault-workflow reason tied to a choice documented elsewhere in this file.

**Opts that change obsidian.nvim behavior**.

| Opt | Effect | Rationale |
|---|---|---|
| `notes_subdir = "0-fleeting"` + `new_notes_location = "notes_subdir"` | `:Obsidian new` lands notes in `0-fleeting/` | §1 (numeric directory prefixes; fleeting is where captures go) |
| `note.template = "fleeting.md"` | Fleeting template auto-applied on `:Obsidian new` | §9 (unified frontmatter); keeps the capture path template-consistent without a second step |
| `templates.folder = "5-templates"` | Template discovery | §1, §9 |
| `templates.customizations` | Each template type routes to its matching content folder (`literature` → `1-literature/`, etc.) | §1 (one folder per type; new-from-template should land there, not in the default subdir) |
| `note_id_func = slugify` | Filenames derived from titles via the slug function | §5 (slug filenames), §11 (slug rules with examples) |
| `attachments.folder = "6-assets"` | Pasted images save to `6-assets/` | §1 (vault directory layout) |
| `ui.enable = false` | Plugin's own UI renderer disabled | Overlap with `render-markdown.nvim` (recommended companion); leaving obsidian.nvim's UI on produces double rendering |
| `completion.blink = true`, `completion.nvim_cmp = false` | Use blink.cmp, not nvim-cmp | LazyVim default is blink.cmp; align the completion engine |

**Added keybindings**. obsidian.nvim provides no default keybindings. Every `<leader>o*` binding is a vault choice. The three below are custom orchestrators (not obsidian.nvim commands); they shell out to `.githooks/lib/normalize.py`:

| Keybinding | Invokes | Purpose |
|---|---|---|
| `<leader>oS` | `:Obsidian rename <slug>` + `normalize.py --apply` | Slugify filename (with vault-wide backlink rewrite) + apply template + re-sync `id`, `aliases[0]`, H1. The only vault-custom keybinding. |

Routine normalization (frontmatter hygiene, H1 insertion, aliases↔H1 sync, template body insertion when body lacks `## ` headings) runs automatically via the pre-commit hook on every commit. No in-session keybinding is needed for it; pressing `<leader>oS` in-session runs the same pipeline plus a slug rename.

All other `<leader>o*` bindings (`on`, `oN`, `oo`, `os`, `ob`, `ol`, `op`, `ot`, `or`) are pass-throughs to native obsidian.nvim subcommands. They exist because obsidian.nvim leaves keymapping to the user; picking the letters is a vault choice, the behavior is obsidian.nvim's.

**Alternatives considered**.

| Alternative | Why not |
|---|---|
| No overlay; let obsidian.nvim defaults apply | Leaves every note in an undefined default subdir; no slugification; no canonical template application for non-Neovim captures. The overlay is the vehicle for §1/§5/§9/§11 to hold. |
| Overlay via vanilla Neovim `init.lua`, not a LazyVim plugin spec | LazyVim is the assumed distribution per `GETTING-STARTED.md` §2; the stow overlay integrates directly as a plugin spec. Users on vanilla Neovim can port the file with minor tweaks. |
| Bind custom logic to existing obsidian.nvim letters (e.g., override `<leader>ot` with our template apply) | Muddies the mental model when reading obsidian.nvim documentation elsewhere. Kept native `<leader>ot`/`<leader>or` as pass-throughs; put vault logic on fresh letters (`oi`, `of`, `oS`). |

**Source of truth**. `nvim-vault/.config/nvim/lua/plugins/obsidian.lua` is the overlay. Its file-header comment enumerates the same deviations in one block for a reader already inside the code.

**When to revisit**. If obsidian.nvim's defaults change such that an opt we set would no longer deviate (check the README/CHANGELOG on version upgrade). If LazyVim swaps away from blink.cmp. If `render-markdown.nvim` merges functionality with obsidian.nvim's UI and the disable becomes redundant.

## Glossary

**Folgezettel**. Luhmann's numeric ID scheme (`1`, `1a`, `1a1`). Not used here; `[[wikilinks]]` replace it.

**Literaturkartei**. Luhmann's separate bibliography card file. Merged into `1-literature/` here, Ahrens-style.

**MOC (Map of Content)**. Obsidian community term for a narrative tour through a topic. Equivalent to "Overview" in this vault.

**Overview / Übersichten**. Luhmann's overview notes. Curated entry points into a topic cluster. Live in `3-overview/` here.

**Schlagwortregister**. Luhmann's alphabetical keyword index. Replaced by Obsidian's tag pane here.

**Slip-box / Zettelkasten**. The collection of permanent notes. `2-permanent/` is this vault's slip-box.

**Zettel**. A single note card. Generic term; covers all note types in the digital vault.

## Further reading

- Ahrens, Sönke. *How to Take Smart Notes* (2nd ed., 2022). The canonical reference for the merged literature-note model.
- Luhmann, Niklas. "Communicating with Slip Boxes" (translated essay). Primary source for the two-box (bibliography + slip-box) architecture.
- Schmidt, Johannes F. K. "Niklas Luhmann's Card Index" in *Forgetting Machines* (2018). Detailed description of the physical system.
