# Vault Workflow

A hands-on tutorial for running a Zettelkasten in this vault. It covers two editors: [Obsidian](https://obsidian.md) (desktop and mobile GUI) and [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim) (terminal, inside Neovim). Both read the same markdown files in the same folder. You do not need to pick one; use Obsidian on desktop and mobile, Neovim at the keyboard, Obsidian when you want the graph view. For installation, see [SETUP-LOCAL.md](SETUP-LOCAL.md); for multi-device sync, see [SETUP-SYNC.md](SETUP-SYNC.md); for encrypted backup, see [SETUP-BACKUP.md](SETUP-BACKUP.md); for the public template mirror, see [SETUP-MIRROR.md](SETUP-MIRROR.md).

## The Method

### Note Types

| Type | Folder | Job |
|------|--------|-----|
| Fleeting | `0-fleeting/` | Half-thoughts. Written fast, processed within 24-48h, then deleted. |
| Literature | `1-literature/` | Source record with brief pointers to key ideas. One per source. A processing bridge, not a storage endpoint. |
| Permanent | `2-permanent/` | What **you** think. One atomic claim per note, self-contained, linked to other notes. |

Writing (`4-writing/`) and overview notes (`3-overview/`) are downstream outputs built from the core types. Master the core first. See [README.md](README.md) for the full directory layout.

### The Flow

```text
Capture ── Fleeting ─┬── Discard
                     │
                     ├── Literature (source record + brief pointers)
                     │         │
                     │         ▼
                     └── Permanent ─── Writing / Structure
```

Three paths out of fleeting:

1. **The thought came from a source** (book, article, video, podcast, conversation). Create or locate a literature note in `1-literature/`. Add a brief pointer with a locator (page number, timestamp, section heading). Develop the idea as a permanent note in `2-permanent/`, linking back to the literature note. Delete the fleeting note.
2. **The thought is your own and worth keeping.** Create a permanent note in `2-permanent/`. Delete the fleeting note.
3. **The thought is noise.** Delete the fleeting note. This is the correct answer more often than not.

Literature notes persist. Over time, one literature note accumulates many brief pointers, each potentially extracted into a permanent note as your thinking develops. You do not delete or "promote" literature notes; they stay put and accumulate links.

Permanent notes are the core of the slip-box. Each states a single claim, links to at least one other note, and is written in your own words. They grow in value as the link network grows.

### Why Linking Matters

The value of a Zettelkasten is in the links, not the notes. An unlinked permanent note is a dead end; a linked note is a node in a growing network where ideas compound. Every time you write in `2-permanent/`, ask: what existing note does this support, contradict, or extend? Insert a `[[wiki-link]]` and write a short clause explaining the relationship. If you cannot find a single link for a permanent note, the note is not ready. Move it back to `0-fleeting/` until you can connect it.

## Naming Conventions

A naming system drawn from Ahrens' *How to Take Smart Notes*, adapted for this vault. No Folgezettel numbering; `[[wiki-links]]` replace numeric hierarchy.

### How It Works

When you create a note (via obsidian.nvim or Obsidian), the filename is auto-generated as a slug:

1. You type a title (e.g., "Risk appetite is a board-level choice")
2. The slug function creates a filename: `risk-appetite-is-a-board-level-choice.md`
3. The `aliases` frontmatter field preserves your original title for search and `[[link]]` autocomplete

You never need to think about the filename. Type the title naturally; the slug is generated for you. The exact transformation rules (spaces → hyphens, non-alphanumeric stripped, etc.) and known limitations (non-ASCII stripping; punctuation collision) are documented with worked examples in [DESIGN.md](DESIGN.md) §11.

### Design Principles

- **Title as claim**: a permanent note's title is its assertion, written as a full declarative sentence. Literature titles identify the source work. Fleeting titles are disposable.
- **Picker-first**: titles are the primary search key in Quick Switcher (`Ctrl+O`) and `[[` autocomplete. Start with the content-bearing word, not a date or tag.
- **Slug filenames, readable aliases**: all notes get auto-generated lowercase-hyphenated filenames. The human-readable title lives in the `aliases` frontmatter field, which powers search and link autocomplete.
- **Cross-platform safety**: Syncthing moves files across Linux, Windows (WSL), and Android. Slug filenames avoid all platform-specific character issues by design (lowercase, hyphens, alphanumeric only).
- **Aliases are the single source of truth for display**: the `aliases` field is what appears in search, autocomplete, and link resolution. Both obsidian.nvim and Obsidian rewrite every `[[link]]` on rename, so titles can evolve freely.

### Convention per Note Type

| Type | Title you type | Slug filename |
|------|---------------|---------------|
| Fleeting | `Contingency is not a buffer` | `contingency-is-not-a-buffer.md` |
| Literature | `Ahrens 2022 - How to Take Smart Notes` | `ahrens-2022-how-to-take-smart-notes.md` |
| Permanent | `Risk appetite is a board-level choice, not a risk-team calculation` | `risk-appetite-is-a-board-level-choice-not-a-risk-team-calculation.md` |
| Overview | `Risk management in capital projects` | `risk-management-in-capital-projects.md` |
| Writing | `The case against stage-gate theatre` | `the-case-against-stage-gate-theatre.md` |

### Rules

1. **Sentence case, always.** Easier to scan; avoids Title Case tax on every new note.
2. **Permanent titles must be declarative claims.** If the title reads as a topic ("risk appetite"), it is wrong. Rewrite as a sentence that asserts something.
3. **Literature titles identify the source**, typically as `Author Year - Title`.
4. **ASCII only in titles**: no em dash, no smart quotes, no slashes. The slug function strips non-alphanumeric characters.
5. **Rename freely.** obsidian.nvim and Obsidian both update every `[[link]]` on rename. The title is not a commitment; the claim is.
6. **Fleeting titles are disposable.** Do not invest effort. They die within 48 hours.
7. **Type the title naturally.** Do not think about filenames. The slug is generated automatically.

### Trade-offs

**Long slug filenames.** Permanent notes produce long filenames (60-100+ characters after slugification). This is fine; you never type or read the slug. The alias carries the readable title. The long slug is a side effect of long, claim-style titles, which force atomicity.

**Aliases in links.** Wiki-links display the alias, not the slug. When you type `[[` and select a note, the link resolves through the alias. If a link renders as a slug in some context, you can add a display name: `[[slug-filename|Readable title]]`.

## The Capture Loop

The vault has no daily anchor note. Capture is continuous; triage is daily.

### Throughout the Day: Capture

When a thought appears, capture it immediately. Speed matters more than structure.

**In Obsidian desktop:** press `Ctrl+N` to create a new note. It lands in `0-fleeting/` (configured in Settings > Files and links > Default location). Type the thought.

**In Obsidian mobile:** tap the `+` icon or new-note button. Confirm the default folder is `0-fleeting/` (Settings > Files and links > Default location for new notes > In the folder specified below > `0-fleeting`). Type, save. Syncthing pushes it to the hub within seconds to minutes.

Obsidian captures (desktop and mobile) start without frontmatter or template structure. That is fine: the pre-commit hook on the hub applies the fleeting template, adds canonical frontmatter, and wraps your typed content in `## Capture` on the first commit. During triage you see a fully structured note ready to process or delete.

**In Neovim** *(skip if you don't use Neovim)*: nvim defaults to permanent, not fleeting. For quick throwaway captures, prefer Obsidian (desktop or mobile). For captures you expect to turn into a permanent claim, press `<leader>on` and type the title. The note lands in `2-permanent/` with the permanent template applied. If you want a fleeting capture in nvim, press `<leader>oN` and pick `fleeting` from the picker; it routes to `0-fleeting/`.

Either way the filename is a slug (e.g., typing "Contingency is not a buffer" creates `contingency-is-not-a-buffer.md`). Your original title is preserved in the `aliases` field for search and link autocomplete.

### End of Day: Triage (2-5 minutes)

Open the fleeting folder.

**In Obsidian:** expand `0-fleeting/` in the file explorer sidebar.

**In Neovim:** `nvim ~/vault/0-fleeting/`

For each note, make one decision:

| If the thought... | Then... |
|---|---|
| Came from something you read, watched, or heard | Find or create the literature note in `1-literature/`. Add a brief pointer with a locator. Develop into a permanent note if the idea is ready. Delete the fleeting note. |
| Is your own and worth keeping | Create a permanent note in `2-permanent/`. Delete the fleeting note. |
| Is noise or redundant | Delete the fleeting note. |

Do not skip. Do not "leave it for tomorrow." An unprocessed fleeting folder is a sign the system is stalling. See [Literature Notes](#literature-notes), [Permanent Notes](#permanent-notes) for step-by-step creation.

### Periodic Self-Check Questions

No enforced cadence. When you notice the vault getting stale (once a month, once a season), walk through these:

1. **Fleeting age.** Any fleeting notes older than 48 hours? Process or delete now.
2. **Orphan permanent notes.** Any permanent notes with zero outgoing links? Find a link or move them back to fleeting. Use the Obsidian graph view or grep for notes with no `[[...]]` in the body.
3. **Emerging clusters.** Any theme with 5+ interconnected permanent notes? Start an overview note in `3-overview/`. For flat enumeration of all notes on a topic, tag them with a common tag instead of maintaining a hand-written list.
4. **Stalled literature notes.** Any literature notes with few key ideas that you haven't touched in months? Decide: resume reading, or move on.
5. **Unexpected backlinks.** Open a few recent permanent notes and check backlinks. Surprise connections are the slip-box's serendipity engine.

## Writing Notes

### Note Anatomy

Every note has two parts separated by `---` fences:

1. **Frontmatter** (between the `---` lines): metadata like `id`, `aliases`, and `tags`. Do not write content here.
2. **Body** (everything after the closing `---`): your actual content. The title heading, template sections, and your writing live here.

**In Obsidian:** press `Ctrl+N` for a new note (lands in `0-fleeting/`), or right-click a folder and choose **New note**, then insert a template via `Ctrl+P` > "Insert template."

**In Neovim:** press `<leader>on` for a new permanent note (default; template auto-applied), or `<leader>oN` to pick a different template and route to the matching folder. obsidian.nvim generates the base frontmatter automatically.

All templates share the same three frontmatter fields, matching obsidian.nvim's default schema:

- **`id`**: the slugified filename (e.g., `quis-custodiet-ipsos-custodes`). Used internally for linking.
- **`aliases`**: the original title you typed, preserving spaces and punctuation. Powers search and `[[link]]` autocomplete. `aliases[0]` is kept in sync with the body H1; additional entries (`aliases[1..]`) are preserved as user-added synonyms.
- **`tags`**: empty by default. Add tags as needed.

No type-specific frontmatter. The folder path already encodes the note type (`2-permanent/...` vs `1-literature/...`); no redundant field is written. For dates, rely on `git log` (first-commit = created; last-commit = updated) or filesystem `mtime`. Literature notes carry bibliographic metadata (medium, author, year, identifier) in the body under `## Source`, not in frontmatter. Write your content in the body, below any instructional comments.

**Notes created outside templates** (mobile captures without pull-down, neo-tree `a`, copy-paste, Obsidian desktop Ctrl+N without a template) miss this auto-generation. The shared normalizer `.githooks/lib/normalize.py` holds the rules in one place and runs automatically on every commit via `.githooks/pre-commit` — `--apply` mode inserts the folder-matched template when appropriate, canonicalizes frontmatter, ensures a body `# H1`, and syncs `aliases[0]` with the H1 (H1 wins when both exist and differ). The apply rule branches on body structure: no frontmatter → full template + pre-existing body wrapped in `## Capture`; frontmatter present + body has no `## ` heading → insert template body sections only (note's H1 and existing content preserved, raw content moved to `## Capture`); frontmatter present + body has at least one `## ` heading → fill only (body untouched). User-added `aliases[1..]` synonyms are preserved throughout. In-session, `<leader>o<space>` runs the same normalization plus a slug rename. The hook never slugifies filenames on its own. See [DESIGN.md](DESIGN.md) §9 for the three-field schema rationale and §11 for the identity model.

### Fleeting Notes

Fleeting notes exist to get thoughts out of your head. They have no quality bar.

The template (`5-templates/fleeting.md`) has minimal structure: the universal frontmatter and a title heading. The comment reminds you to process within 48h.

Write rapidly. Do not format, link, or title carefully. The note dies within 48 hours: it either becomes a literature pointer and permanent note, or it gets deleted.

### Literature Notes

A literature note answers: **what is this source, and what ideas in it are worth developing?**

One literature note per source (book, article, paper, podcast episode, video, talk, web page). The body contains bibliographic metadata under `## Source`, a brief summary, and a list of pointers to key ideas, each with a locator (page number, timestamp, section heading). The literature note is a processing bridge: ideas that deserve full development are extracted as permanent notes.

**Creating the note:**

*In Obsidian:* right-click `1-literature/` in the file explorer, select **New note**. Press `Ctrl+P`, type "Insert template", choose `literature`.

*In Neovim:* press `<leader>oN`. Pick the `literature` template. Type the title, conventionally `Author Year - Title` (e.g., `Ahrens 2022 - How to Take Smart Notes`). The note is created in `1-literature/`.

**Filling in the template:**

| Section | Fill with |
|---|---|
| Source | Medium, author, year, identifier (ISBN/DOI/URL) |
| Notes | One bullet per idea: page, colon, paraphrase, arrow, link. Example: `- p. 42: memory hierarchy depends on access patterns -> [[cache-locality]]`. Add the `[[permanent-note]]` link when the idea is extracted. |

**Paraphrase by default; quote only when wording matters.** Literature notes are processing bridges, not quote archives. Writing the idea in your own words is itself a learning act (Ahrens calls it "elaboration") and avoids the collector's fallacy (stockpiling quotes without engagement). Quote verbatim only when the exact wording is what you want to keep (definitions, disputed phrasings, language you may cite later). In those cases, use blockquote syntax: `> "exact phrase" (p.N) -> [[]]`. See [DESIGN.md](DESIGN.md) §2 for the rationale.

**Inline locator conventions** (goes in parentheses next to each pointer):

| Medium | Format | Example |
|---|---|---|
| Book, article, paper | `(p.N)` or `(pp.N-M)` | `(p.47)`, `(pp.47-49)` |
| Podcast, video, talk | `(MM:SS)` or `(HH:MM:SS)` | `(12:30)`, `(01:24:05)` |
| Web | `(§heading)` or omit | `(§methods)` |

**Lazy create.** When writing a permanent note, type `[[author-year-title]]` even if the literature note does not yet exist. The link renders as unresolved; click it in Obsidian or press `gf` in Neovim to create a stub literature note, then fill in the metadata.

### Permanent Notes

A permanent note answers: **what is one thing I believe, and why?**

The title **is** the claim. Not the topic. This is the single habit that separates a live Zettelkasten from a filing cabinet.

- Bad (topic): `Risk management.md`
- Good (claim): `Risk appetite is a board-level choice, not a risk-team calculation.md`

**Creating the note:**

*In Obsidian:* right-click `2-permanent/` in the file explorer, select **New note**. Title as a claim. Press `Ctrl+P`, type "Insert template", choose `permanent`.

*In Neovim:* press `<leader>on` (permanent is the default template). Type the title as a full declarative sentence, sentence case. The note is created in `2-permanent/`. Or press `<leader>oN` and pick `permanent` explicitly; same result.

**Filling in the template:**

| Section | What to write |
|---|---|
| **Claim** | 1-2 sentences restating the claim. Sharpen what the title asserts. |
| **Development** | Your reasoning in your own words. Cite sources with `[[literature-note]]` where claims depend on them. |
| **Connections** | Link to at least one other note. State the relationship: supports, contradicts, extends, or is prerequisite to. |
| **Sources** | Literature notes this claim draws from. |

**The one rule:** every permanent note must link to at least one other permanent or literature note. An unlinked note is a dead end. If you cannot find a link, move the note back to `0-fleeting/` until you can.

**What "atomic" means, concretely:**

If your note title contains "and" or "also" at the top level, split it.

- `Risk registers decay without an owner, and controls need testing cadence.md` becomes:
  - `Risk registers decay without an assigned owner.md`
  - `Controls require a defined testing cadence to remain effective.md`
- Now each can be linked independently from different contexts.

### Writing Notes

Writing notes hold long-form output assembled from permanent notes. All route to `4-writing/`. In Obsidian, create a note in `4-writing/` and insert a template. In Neovim, press `<leader>oN` and pick the `writing` template.

**No bibliography section.** Sources are already tracked in `1-literature/` and connections via `## Connections`. For a piece that needs a formal reference list (academic journal, formatted citations), add `## References` at the bottom of that specific piece by hand, in whatever citation style the venue requires.

**Where to put the piece content.** Fill `## Audience`, `## Outline`, then `## Draft`. For shorter pieces, leave Audience and Outline empty and write into `## Draft`.

### Overview Notes

Overview notes provide entry points into the slip-box. They do not contain original claims; they organize and connect permanent notes. Do not create them up front. When you notice 5+ permanent notes circling the same theme, create an overview in `3-overview/`.

An overview is a **curated narrative tour through a topic**: prose between links, author's synthesis and opinion about the order and relationships. For a flat enumeration of notes on a topic (no narrative, no curation), **use tags** and rely on Obsidian's tag pane; do not maintain a hand-written list.

1. *In Obsidian:* right-click `3-overview/` in the file explorer, select **New note**. Press `Ctrl+P`, type "Insert template", choose `overview`.
   *In Neovim:* press `<leader>oN`, pick the `overview` template, type the theme as a title.
2. Write an **Orientation** (what this covers, where to start), list **Starting points** (read these first), then build the **Core** as sections organized by your argument, with prose between links. Note **Open questions** (unresolved threads, candidates for future notes).

If an overview has little or no prose between the links, it is really a flat list; delete it and use tags instead. See [DESIGN.md](DESIGN.md) §3 for the rationale behind dropping Index as a separate type.

## Promoting Notes

This is the most frequent workflow: turning a fleeting note into a literature pointer or a permanent note.

### In Obsidian

1. Open the fleeting note from the file explorer or Quick Switcher (`Ctrl+O`).
2. Read the thought. Decide its destination (literature pointer, permanent note, or discard).
3. Right-click the target folder (e.g., `2-permanent/`), select **New note**. Type the title.
4. Press `Ctrl+P`, type "Insert template", choose the matching template.
5. Write the content. Add at least one `[[link]]` for permanent notes. For literature notes, fill in the bibliographic fields.
6. Go back to the fleeting note and delete it (right-click > Delete in the file explorer, or `Ctrl+P` > "Delete current file").

### In Neovim

**`<leader>op` method** (recommended; keeps the original filename and backlinks):

1. Open the note to promote (from neo-tree or `<leader>oo`).
2. Press `<leader>op`. A picker opens with the five types; `permanent` is preselected.
3. Hit Enter to accept permanent, or type the first letter of another type (`l` for literature, `f` for fleeting, `o` for overview, `w` for writing) and Enter.
4. The file is moved to the target folder. The old template sections are replaced with the target template's sections. Any existing body content below H1 is preserved under `## Capture` for you to weave into the new structure. The buffer follows the file. Backlinks resolve automatically; the filename is unchanged, and `[[wiki-links]]` resolve by stem + alias regardless of folder.

**Side-by-side method** (best when you want to rewrite the content from scratch while keeping the original in view):

1. Open the original note (from neo-tree or `<leader>oo`).
2. Split the screen: `<leader>|` (vertical split, side by side).
3. In the new right pane, press `<leader>oN`. Pick the target template (`literature`, `permanent`, `overview`, or `writing`). Type the title. The new note is created in the correct folder with the template applied.
4. You now have the original on the left, the new note on the right. Use `Ctrl+h` / `Ctrl+l` to move focus between panes. Copy lines with `yy` in one pane, switch panes, paste with `p`.
5. Write the content in the new note. Add at least one `[[link]]` for permanent notes.
6. Close the left pane: `<leader>wd` (closes the window, not the buffer).
7. Delete the original: `<leader>e` to open neo-tree, navigate to it, press `d`.

Fleeting notes rarely have backlinks, so nothing is lost by deleting them when you go with the side-by-side method. Use `<leader>op` when you want to keep the filename (and therefore any existing backlinks) stable.

### Splitting a multi-idea note

The "one claim per file" rule for permanent notes means a multi-idea note needs to be split. In Neovim, `<leader>ox` (visual-mode) does this in one keystroke:

1. Visual-select the portion that represents the extractable idea.
2. Press `<leader>ox`.
3. A prompt asks for the new note's title.
4. The selection is removed from the source, a new note is created with that selection as its body, and a `[[link]]` to the new note is inserted in place of the removed text.

The new note is created in the default `notes_subdir` (`2-permanent/` in nvim) with the permanent template. Promote it with `<leader>op` if it belongs elsewhere.

## Linking

Linking is the core habit. Do it every time you write in `2-permanent/`.

**In Obsidian:** type `[[`. An autocomplete dropdown appears. Start typing to filter. Select the target.

**In Neovim:** type `[[` in Insert mode. obsidian.nvim opens a fuzzy picker over all note names. Start typing to filter, select a note, press Enter. The link inserts as `[[Note Title]]`.

**Linking from an existing selection (Neovim, visual mode).** When the phrase you want to turn into a link is already written, visual-select it, then:

| Binding | Action |
|---|---|
| `<leader>ol` | Link the selected text to an existing note (fuzzy picker) |
| `<leader>oL` | Create a new note titled after the selection, and link to it |

The selection becomes the link's display text automatically; no need to retype it.

After inserting the link, write a short because-clause. A link without reasoning is decoration.

```markdown
This extends [[Risk appetite is a board-level choice, not a risk-team calculation]]
because tolerance sits one level below appetite and is owned by the executive,
not the board.
```

**Discovery tools for finding connections:**

| Action | Obsidian desktop | Neovim |
|---|---|---|
| Backlinks (who links here?) | Right sidebar > Backlinks panel | `<leader>ob` |
| Outgoing links (where does this point?) | Right sidebar > Outgoing links panel | `<leader>oa` |
| Search vault content | `Ctrl+Shift+F` | `<leader>os` |
| Find note by name | `Ctrl+O` (Quick Switcher) | `<leader>oo` |
| Visual link map | `Ctrl+G` (Graph view) | N/A |

Check backlinks every time you open a permanent note or a literature note. Literature backlinks show every permanent note derived from that source; unexpected permanent-note backlinks are the slip-box's serendipity engine.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Titling permanent notes as topics ("Risk management") | Re-title as a claim ("Risk management fails when controls lack owners") |
| Writing permanent notes with no links | Enforce the one-rule: no unlinked permanent notes. Move back to fleeting if stuck. |
| Hoarding fleeting notes for weeks | Triage daily. Deletion is a valid outcome. |
| Copy-pasting from sources into permanent notes | Paraphrase belongs in literature note pointers. Permanent notes must be in your words. |
| Creating sub-folders inside `2-permanent/` | Links are the structure. Folders are storage. Keep `2-permanent/` flat. |
| Renaming files with `mv` in the terminal | Use Obsidian's file explorer or neo-tree. Links break otherwise. |
| Multi-idea notes ("X and also Y") | Split into atomic notes. One claim per file. In Neovim: visual-select the extractable idea, press `<leader>ox` (see §Promoting Notes > Splitting a multi-idea note). |
| Waiting for the "right" title before writing | Write the note, title later. Rename is cheap; both editors update links. |
| Creating fleeting notes in nvim with `<leader>on` | In nvim, `<leader>on` defaults to permanent. For a fleeting capture in nvim, press `<leader>oN` and pick `fleeting`. Or capture in Obsidian (mobile or desktop), where the default is fleeting. |
| Ignoring backlinks | Check backlinks (Obsidian right sidebar or `<leader>ob`) on literature and permanent notes. |
| Writing full paraphrases in literature notes | Literature notes are brief pointers, not full paraphrases. Develop ideas in permanent notes. |
| Notes created in Obsidian keep typed filenames (`My thought.md`), never auto-slugified | Expected. Obsidian (mobile and desktop) uses the typed title as the filename; our vault only slugifies via `<leader>o<space>` in Neovim. Hourly auto-commit normalizes frontmatter and applies templates but never renames files. Run `<leader>o<space>` when you promote a note you want to keep. |

## Using Obsidian

### Desktop

Obsidian reads the same markdown files as Neovim. No import, no sync delay beyond Syncthing.

Key actions: `Ctrl+O` (Quick Switcher), `Ctrl+Shift+F` (search), `Ctrl+G` (graph view), `Ctrl+P` (command palette), `Ctrl+N` (new note). The command palette (`Ctrl+P`) is the Swiss Army knife; any action you cannot find has a command there.

Keep the **Backlinks panel** visible in the right sidebar while writing permanent notes. It shows every note that links to the current note.

**Note:** repo docs and infrastructure directories are hidden from search, graph, and link suggestions via `userIgnoreFilters` in `.obsidian/app.json`, and hidden from the file explorer sidebar via the `hide-root-docs` CSS snippet (enabled in `.obsidian/appearance.json`; per-device toggle in Settings > Appearance > CSS snippets if it doesn't auto-load).

### Mobile

Obsidian mobile is for capture, not composition.

1. Open Obsidian. Tap `+` to create a new note.
2. Confirm the default folder is `0-fleeting/` (Settings > Files and links > Default location > `0-fleeting`).
3. Type the thought. Save. Syncthing pushes it to the hub within seconds to minutes.

**Insert template on mobile:** swipe down (pull) on an open note to trigger the template picker. Templates are not auto-applied on mobile; process raw captures during triage.

**Limitations:** Syncthing on Android pauses on battery saver. Do not rename or move notes from the Android Files app; use Obsidian's file explorer only.

## Using Neovim

*Skip this entire section if you don't use Neovim. Everything above works with Obsidian alone.*

This section covers Neovim, neo-tree, and obsidian.nvim basics relevant to the vault workflow. It assumes [LazyVim](https://www.lazyvim.org/) as the Neovim distribution with the vault's `nvim-vault/` overlay installed (see [SETUP-LOCAL.md](SETUP-LOCAL.md) §6).

### Starting a Session

Three entry patterns.

**A. Bare nvim (recommended).**

```bash
cd ~/vault
nvim
```

LazyVim shows the dashboard. Pick notes by name rather than navigating folders.

| Key | Action |
|---|---|
| `<leader>oo` | Find note by name |
| `<leader>on` | New note (permanent by default) |
| `<leader>oN` | New note from template picker |
| `<leader>e` | Toggle neo-tree as left sidebar |

**B. Open a specific file.**

```bash
nvim ~/vault/0-fleeting/some-note.md
```

File opens in the editor; `<leader>e` toggles neo-tree on the left.

**C. Open a directory.**

```bash
nvim ~/vault/
```

Neo-tree fills the whole window. Press `s` on a file in the tree to open it in a vertical split; the tree stays on the left as a sidebar.

Treat neo-tree as a *sometimes tool*: renames, moves, visual triage of `0-fleeting/`. For everything else, `<leader>oo` is faster.

### Screen Layout

```text
┌──────────┬──────────────────────────────────┐
│ Neo-tree │  Buffer tab bar                  │
│ (sidebar)├──────────────────────────────────┤
│          │                                  │
│ 0-fleeti.│  Editor area                     │
│ 1-litera.│  (your note content goes here)   │
│ 2-perman.│                                  │
│ 3-overvi.│                                  │
│ ...      │                                  │
│          ├──────────────────────────────────┤
│          │  Status line (mode, filename)    │
└──────────┴──────────────────────────────────┘
```

- **Neo-tree** (left sidebar): file explorer. Toggle with `<leader>e`.
- **Editor area** (right): where you read and write notes.
- **Buffer tab bar** (top of the editor area): each open file is a tab. Switch with `Shift+h` / `Shift+l`.
- **Status line** (bottom): current mode, filename, cursor position.

**One rule to remember:** `Ctrl` + a vim direction (`h`/`j`/`k`/`l`) always moves focus between areas and splits. It works the same way everywhere.

### Buffers vs. Windows

Two concepts that look similar but work differently:

- A **buffer** is an open file. It appears as a tab in the tab bar. You can have many buffers open; switching between them (`Shift+h`/`Shift+l`) changes what is displayed in the current window. Close a buffer with `<leader>bd`.
- A **window** is a viewport. A split (`<leader>|`) creates two windows side by side, each showing a different buffer. Close a window with `<leader>wd`; the buffer stays open in the tab bar.

In short: buffers are files, windows are panes. `<leader>bd` closes the file. `<leader>wd` closes the pane.

### Neovim Essentials

**Modes.** Neovim is a modal editor. You are always in one of these modes:

| Mode | Enter with | Purpose |
|---|---|---|
| Normal | `Esc` | Navigate, run commands, trigger keybindings. You start here. |
| Insert | `i`, `a`, or `o` | Type text. |
| Visual | `v` | Select text. |
| Command | `:` | Run Ex commands (save, quit, search-replace). |

All obsidian.nvim keybindings (`<leader>on`, `<leader>oN`, etc.) work from Normal mode.

**Leader key.** In LazyVim, the leader key is `Space`. When this document says `<leader>on`, press Space, then `o`, then `n`. Press Space and wait; [which-key](https://github.com/folke/which-key.nvim) shows all available bindings grouped by category.

### Neo-tree

Neo-tree is the file explorer sidebar. Toggle it with `<leader>e`.

Navigate with `j`/`k`, open files with `Enter`, collapse directories with `h`. Press `?` inside neo-tree to see all available keybindings.

**Essential operations:**

| Keys | Action |
|---|---|
| `a` | Create new file (add trailing `/` for a directory) |
| `r` | Rename (does NOT update wiki-links; use `:Obsidian rename` instead) |
| `d` | Delete (confirms before deleting) |
| `m` | Move (prompts for destination path) |
| `s` | Open in a vertical split (side by side) |
| `/` | Fuzzy filter the tree |

**Creating a note in a specific folder:** the recommended way is `<leader>oN`, which picks a template and routes the note to the correct folder automatically. Alternatively, navigate to the target folder in neo-tree, press `a`, type the full filename including `.md`, and press Enter. Notes created via neo-tree `a` do not get auto-generated frontmatter or templates; they will get both automatically on the first commit via the pre-commit hook's normalize pass.

### Moving and Renaming Notes Safely

**Obsidian's file explorer** is the safest way to rename or move notes. It rewrites all `[[wiki-links]]` that point to the file automatically.

**In Neovim**, two paths:

- `<leader>o<space>` (recommended for slug renames). Slug-renames the filename, invokes `:Obsidian rename` under the hood so backlinks update vault-wide, then runs `.githooks/lib/normalize.py --apply` to sync `id` to the new stem, apply the template if missing, and preserve the pre-rename readable name as `aliases[0]` when no body H1 exists. Works on a note that is already a slug too: the rename step is skipped and only normalization runs.
- `<leader>or` (or `:Obsidian rename <new-title>`) for free-form renames where you want a new title that is not just a slug of the old one. Updates backlinks and frontmatter `id` but does not trigger full normalization; the next commit's pre-commit hook will sync `aliases[0]` with the new H1 if you also updated the H1, or you can run `<leader>o<space>` to normalize immediately.

**Neo-tree renames (`r`) and moves (`m`) do NOT update wiki-links.** They are plain filesystem operations. Use them only when you intend to fix links manually afterward, or when the note has no backlinks (e.g., new fleeting notes).

**Never** use terminal `mv`, `rm`, ranger, or OS file managers for vault notes. They do not know about wiki-links. Every link pointing to the file will silently break.

## Quick Reference

### Obsidian Desktop

| Keys | Action |
|------|--------|
| `Ctrl+N` | New note |
| `Ctrl+O` | Quick Switcher (find note by name) |
| `Ctrl+Shift+F` | Search vault |
| `Ctrl+G` | Graph view |
| `Ctrl+P` | Command palette |

### obsidian.nvim

Normal-mode:

| Keys | Action |
|------|--------|
| `<leader>oa` | Collect all links in buffer |
| `<leader>ob` | Collect backlinks |
| `<leader>oc` | Load ToC into picker |
| `<leader>od` | Delete current note (with confirm) |
| `<leader>oD` | Delete note from picker (with confirm) |
| `<leader>of` | Find tags |
| `<leader>oi` | Paste image from clipboard |
| `<leader>on` | Create a new note (default: permanent) |
| `<leader>oN` | Create a new note from a template |
| `<leader>oo` | Switch notes (fuzzy picker over name + aliases) |
| `<leader>op` | Promote note to different type |
| `<leader>or` | Rename note and update references |
| `<leader>os` | Search vault (ripgrep over body text) |
| `<leader>ot` | Insert template |
| `<leader>o<space>` | Slug-rename and normalize note |
| `<CR>` | Follow `[[link]]` under cursor (smart action) |
| `]o` / `[o` | Next / previous link in current note |
| `[[` | Insert wiki-link (fuzzy picker) |

Visual-mode:

| Keys | Action |
|------|--------|
| `<leader>ol` | Link selected text to existing note |
| `<leader>oL` | Link selected text to new note |
| `<leader>ox` | Extract selected text to new note and link to it |

### Buffers and Windows

| Keys | Action |
|------|--------|
| `Shift+h` / `Shift+l` | Previous / next buffer (tab) |
| `<leader>bb` | Toggle between last two buffers |
| `<leader>,` | Browse all open buffers |
| `<leader>bd` | Close current buffer (file) |
| `<leader>bo` | Close all other buffers |
| `<leader>\|` / `<leader>-` | Split vertical / horizontal |
| `Ctrl+h` `Ctrl+j` `Ctrl+k` `Ctrl+l` | Move focus between areas/splits |
| `<leader>wd` | Close current window (pane) |
| `<leader>wm` | Zoom (maximize window) |
| `<leader>qq` | Quit all |

### Finding Files

| Keys | Action |
|------|--------|
| `<leader>oo` | Find note by name (obsidian.nvim, vault-scoped) |
| `<leader>os` | Search note content (obsidian.nvim, vault-scoped) |
| `<leader><space>` | Find any file by name (LazyVim, all files) |
| `<leader>/` | Grep across vault |
| `<leader>fr` | Recent files |

### Neo-tree

| Keys | Action |
|------|--------|
| `<leader>e` | Toggle file explorer |
| `a` | Create file |
| `r` | Rename (does NOT update wiki-links) |
| `d` | Delete |
| `m` | Move |
| `s` | Open in vertical split |
| `/` | Fuzzy filter the tree |
| `?` | Show all keybindings |

### Editing and Navigation

| Keys | Action |
|------|--------|
| `i` / `a` / `o` | Enter Insert mode (before / after cursor / new line below) |
| `Esc` | Return to Normal mode |
| `Ctrl+s` | Save |
| `:wq` or `ZZ` | Save and quit |
| `u` / `Ctrl+r` | Undo / Redo |
| `yy` / `p` | Copy line / Paste below |
| `yap` | Copy paragraph |
| `v` then `y` | Visual select then copy |
| `dd` | Delete line |
| `ciw` | Change word under cursor |
| `s` | Flash jump (type 2 chars, then label) |
| `Ctrl+d` / `Ctrl+u` | Scroll half-page down / up |
| `/text` | Search in file (`n`/`N` for next/previous) |
| `<leader>uz` | Zen mode |
| `<leader>uw` | Toggle word wrap |
| `<leader>us` | Toggle spell check |
| `:RenderMarkdown toggle` | Toggle rendered markdown |

## The Minimum Viable Habit

If you forget everything above, do just this:

1. Capture anything that flickers into `0-fleeting/`.
2. Empty `0-fleeting/` every evening.
3. When a fleeting came from a source, create or update the literature note and add a brief pointer.
4. Never write a permanent note without one `[[link]]`.

The rest compounds on top of that.
