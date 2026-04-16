# Vault Workflow

A hands-on tutorial for running a Zettelkasten in this vault. It covers two editors: [Obsidian](https://obsidian.md) (desktop and mobile GUI) and [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim) (terminal, inside Neovim). Both read the same markdown files in the same folder. You do not need to pick one; use Neovim at the keyboard, Obsidian mobile for capture on the go, Obsidian desktop when you want the graph view. For installation and device setup, see [SETUP.md](SETUP.md).

## The Method

### Note Types

| Type | Folder | Job |
|------|--------|-----|
| Fleeting | `0-fleeting/` | Half-thoughts. Written fast, processed within 24-48h, then deleted. |
| Source | `1-sources/` | Bibliographic record for a cited work. One per source. |
| Literature | `2-literature/` | What someone else said, paraphrased in your words, tied to a source. |
| Permanent | `3-permanent/` | What **you** think. One claim per note, linked to other notes. |

Writing (`4-writing/`) and index notes (`5-index/`) are downstream outputs built from the four core types. Master the core first. See [README.md](README.md) for the full directory layout and status lifecycles.

### The Flow

```text
Capture ── Fleeting ─┬── Discard
                     │
                     ├── Source (bibliographic record) + Literature (paraphrase)
                     │         │
                     │         ▼
                     └── Permanent ─── Writing / Index
```

Three paths out of fleeting:

1. **The thought came from a source** (book, article, video, podcast, conversation). Create or locate a source note in `1-sources/`, then create a literature note in `2-literature/` that references it via `source: "[[slug]]"`. Delete the fleeting note.
2. **The thought is your own and worth keeping.** Create a permanent note in `3-permanent/`. Delete the fleeting note.
3. **The thought is noise.** Delete the fleeting note. This is the correct answer more often than not.

Source notes persist; literature notes persist. Over time, one source note is referenced by many literature notes (a book's chapters, for example), and each literature note may seed multiple permanent notes as your thinking develops. You do not delete or "promote" source or literature notes; they stay put and accumulate links.

Permanent notes are the core of the Zettelkasten. Each states a single claim, links to at least one other note, and is written in your own words. They grow in value as the link network grows.

**Why sources are separate from literature**. Ahrens' classical Zettelkasten distinguishes a **reference note** (bibliographic metadata) from a **literature note** (paraphrased content). This vault uses the same split under the names `source` and `literature`. The split earns its weight when you read a book and write multiple literature notes across its chapters; the source metadata is entered once in `1-sources/` and each literature note references it by wiki-link, not by retyping.

### Why Linking Matters

The value of a Zettelkasten is in the links, not the notes. An unlinked permanent note is a dead end; a linked note is a node in a growing network where ideas compound. Every time you write in `3-permanent/`, ask: what existing note does this support, contradict, or extend? Insert a `[[wiki-link]]` and write a short clause explaining the relationship. If you cannot find a single link for a permanent note, the note is not ready. Move it back to `0-fleeting/` until you can connect it.

## Naming Conventions

A naming system drawn from Ahrens' *How to Take Smart Notes*, adapted for this vault. No Folgezettel numbering; `[[wiki-links]]` replace numeric hierarchy.

### How It Works

obsidian.nvim auto-generates filenames and aliases from the title you type:

1. You type a title (e.g., "Risk appetite is a board-level choice")
2. `note_id_func` creates a slug filename: `risk-appetite-is-a-board-level-choice.md`
3. The `aliases` frontmatter field preserves your original title for search and `[[link]]` autocomplete

You never need to think about the filename. Type the title naturally; the slug is generated for you.

### Design Principles

- **Title as claim**: a permanent note's title is its assertion, written as a full declarative sentence. Source titles identify the work. Literature titles identify the scope of the paraphrase (often by chapter or section). Fleeting titles are disposable.
- **Picker-first**: titles are the primary search key in `<leader>oo` and `[[` autocomplete. Start with the content-bearing word, not a date or tag.
- **Slug filenames, readable aliases**: all notes get auto-generated lowercase-hyphenated filenames. The human-readable title lives in the `aliases` frontmatter field, which powers search and link autocomplete.
- **Cross-platform safety**: Syncthing moves files across Linux, Windows (WSL), and Android. Slug filenames avoid all platform-specific character issues by design (lowercase, hyphens, alphanumeric only).
- **Aliases are the single source of truth for display**: the `aliases` field is what appears in search, autocomplete, and link resolution. Both obsidian.nvim and Obsidian rewrite every `[[link]]` on rename, so titles can evolve freely.

### Convention per Note Type

| Type | Title you type | Slug filename |
|------|---------------|---------------|
| Fleeting | `Contingency is not a buffer` | `contingency-is-not-a-buffer.md` |
| Source | `Ahrens 2017 - How to Take Smart Notes` | `ahrens-2017---how-to-take-smart-notes.md` |
| Literature | `Ahrens 2017 Ch3 - The slip-box is a thinking partner` | `ahrens-2017-ch3---the-slip-box-is-a-thinking-partner.md` |
| Permanent | `Risk appetite is a board-level choice, not a risk-team calculation` | `risk-appetite-is-a-board-level-choice-not-a-risk-team-calculation.md` |
| Writing | `The case against stage-gate theatre` | `the-case-against-stage-gate-theatre.md` |
| Index | `How controls fail in capital projects` | `how-controls-fail-in-capital-projects.md` |

### Rules

1. **Sentence case, always.** Easier to scan; avoids Title Case tax on every new note.
2. **Permanent titles must be declarative claims.** If the title reads as a topic ("risk appetite"), it is wrong. Rewrite as a sentence that asserts something.
3. **Source titles identify the work**, typically as `Author Year - Title`.
4. **Literature titles identify scope**, typically as `Author Year Ch/§ - theme` so siblings cluster in pickers.
5. **ASCII only in titles**: no em dash, no smart quotes, no slashes. The slug function strips non-alphanumeric characters.
6. **Rename freely.** obsidian.nvim and Obsidian both update every `[[link]]` on rename. The title is not a commitment; the claim is.
7. **Fleeting titles are disposable.** Do not invest effort. They die within 48 hours.
8. **Type the title naturally.** Do not think about filenames. The slug is generated automatically.

### Trade-offs

**Long slug filenames.** Permanent notes produce long filenames (60-100+ characters after slugification). This is fine; you never type or read the slug. The alias carries the readable title. The long slug is a side effect of long, claim-style titles, which force atomicity.

**Aliases in links.** Wiki-links display the alias, not the slug. When you type `[[` and select a note, the link resolves through the alias. If a link renders as a slug in some context, you can add a display name: `[[slug-filename|Readable title]]`.

## The Capture Loop

The vault has no daily anchor note. Capture is continuous; triage is daily.

### Throughout the Day: Capture

When a thought appears, capture it immediately. Speed matters more than structure.

**In Neovim:**

```
<leader>on
```

Type a short title, press Enter. The note lands in `0-fleeting/` with the fleeting template applied: frontmatter (`id`, `aliases`, `tags`) and body structure are ready. Write the thought in one to three sentences below the comment. Do not format, do not link, do not polish.

The filename is a slug (e.g., typing "Contingency is not a buffer" creates `contingency-is-not-a-buffer.md`). Your original title is preserved in the `aliases` field for search and link autocomplete.

**In Obsidian desktop:** press `Ctrl+N` to create a new note. It lands in `0-fleeting/` (configured in Settings > Files and links > Default location). Type the thought.

**In Obsidian mobile:** tap the `+` icon or new-note button. Confirm the default folder is `0-fleeting/` (Settings > Files and links > Default location for new notes > In the folder specified below > `0-fleeting`). Type, save. Syncthing pushes it to the hub within seconds to minutes.

Mobile captures will not have the fleeting template applied automatically. That is fine; you will process them during triage.

### End of Day: Triage (2-5 minutes)

Open the fleeting folder.

**In Neovim:** `nvim ~/vault/0-fleeting/`

**In Obsidian:** expand `0-fleeting/` in the file explorer sidebar.

For each note, make one decision:

| If the thought... | Then... |
|---|---|
| Came from something you read, watched, or heard | Find or create the source note in `1-sources/`, then create a literature note in `2-literature/`. Delete the fleeting note. |
| Is your own and worth keeping | Create a permanent note in `3-permanent/`. Delete the fleeting note. |
| Is noise or redundant | Delete the fleeting note. |

Do not skip. Do not "leave it for tomorrow." An unprocessed fleeting folder is a sign the system is stalling. See [Source Notes](#source-notes), [Literature Notes](#literature-notes), and [Permanent Notes](#permanent-notes) for step-by-step creation.

### Periodic Self-Check Questions

No enforced cadence. When you notice the vault getting stale (once a month, once a season), walk through these:

1. **Fleeting age.** Any fleeting notes older than 48 hours? Process or delete now.
2. **Orphan permanent notes.** Any permanent notes with zero outgoing links? Find a link or move them back to fleeting. Use the Obsidian graph view or grep for notes with no `[[...]]` in the body.
3. **Emerging clusters.** Any theme with 5-10 interconnected permanent notes? Start an index note in `5-index/`.
4. **Stalled source notes.** Any `status: reading` source notes you haven't touched in months? Decide: resume, mark `abandoned`, or keep as `reference`.
5. **Unexpected backlinks.** Open a few recent permanent notes and check backlinks. Surprise connections are the Zettelkasten's serendipity engine.

## Writing Notes

### Note Anatomy

Every note has two parts separated by `---` fences:

1. **Frontmatter** (between the `---` lines): metadata like `id`, `aliases`, and `tags`. Do not write content here.
2. **Body** (everything after the closing `---`): your actual content. The title heading, template sections, and your writing live here.

When you create a note with `<leader>on`, the fleeting template is applied automatically. When you create a note with `<leader>oN`, you pick a template and the note is routed to the correct folder. In both cases, obsidian.nvim generates the base frontmatter:

- **`id`**: the slugified filename (e.g., `quis-custodiet-ipsos-custodes`). Used internally for linking.
- **`aliases`**: the original title you typed, preserving spaces and punctuation. Used for search and `[[link]]` autocomplete.
- **`tags`**: empty by default. Add tags as needed.

Some templates add type-specific fields (source and literature notes share `type:`; source notes add `medium`, `author`, `year`, `title`, `publisher`, `identifier`, `status`; literature notes add `source:`; writing notes add `status`). Write your content in the body, below any instructional comments.

### Fleeting Notes

Fleeting notes exist to get thoughts out of your head. They have no quality bar.

The template (`6-templates/fleeting.md`) has minimal structure: `id`, `aliases`, `tags`, and a title heading. The comment reminds you to process within 1-2 days.

Write fast. Do not format, link, or title carefully. The note dies within 48 hours: it either becomes a source+literature pair or a permanent note, or it gets deleted.

### Source Notes

A source note answers: **what is the cited work, and what is its bibliographic metadata?**

One source note per work (book, article, paper, podcast episode, video, talk, web page, conversation). The note body captures *why you engaged with it* and *a brief summary*; it does not paraphrase the content. Paraphrase lives in literature notes.

**Creating the note:**

*In Neovim:* press `<leader>oN`. Pick the `source` template. Type the title, conventionally `Author Year - Title` (e.g., `Ahrens 2017 - How to Take Smart Notes`). The note is created in `1-sources/`.

*In Obsidian:* right-click `1-sources/` in the file explorer, select **New note**. Press `Ctrl+P`, type "Insert template", choose `source`.

**Filling in the template:**

| Field | Fill with |
|---|---|
| `medium` | `book`, `article`, `paper`, `podcast`, `video`, `talk`, `web`, `other` |
| `author`, `year`, `title`, `publisher` | Bibliographic metadata |
| `identifier` | ISBN, DOI, or URL |
| `status` | `unread`, `reading`, `read`, `abandoned`, `reference` |
| Why this source | One or two lines on what drew you to it |
| Summary | One paragraph in your own words once you finish |
| Connections | Other source notes in conversation with this one |

**Source-first vs lazy create.** Recommended flow: create the source note at the start of reading a new work. Alternative: when writing a literature note, type `source: "[[author-year-title]]"` even if the source does not yet exist. The link renders as unresolved; place cursor on it and press `gf` in nvim (or click in Obsidian) to create a stub source note, then fill in the metadata.

### Literature Notes

A literature note answers: **what did this source say, in my words, that I might want to use later?**

One source can have many literature notes (one per chapter, section, or theme you want to capture). Each literature note references its source via `source: "[[...]]"` in the frontmatter.

**Creating the note:**

*In Neovim:* press `<leader>oN`. Pick the `literature` template. Type the title, conventionally `Author Year Ch/§ - theme` (e.g., `Ahrens 2017 Ch3 - The slip-box is a thinking partner`). The note is created in `2-literature/`.

*In Obsidian:* right-click `2-literature/` in the file explorer, select **New note**. Press `Ctrl+P`, type "Insert template", choose `literature`.

**Filling in the template:**

| Section | What to write |
|---|---|
| **Frontmatter `source:`** | Wiki-link to the source note, e.g., `source: "[[ahrens-2017---how-to-take-smart-notes]]"` |
| **Body** | Use `>` for quotes with an inline locator (see below), then paraphrase or react in your own words below each. Be selective, not comprehensive. |
| **Connections** | Links to related literature notes and seeds for future permanent notes. Explain each link with a because-clause. |
| **Attachments** | Source PDFs, screenshots, or diagrams. |

**Inline locator conventions** (goes in parentheses next to each quote):

| Medium | Format | Example |
|---|---|---|
| Book, article, paper | `(p.N)` or `(pp.N-M)` | `(p.47)`, `(pp.47-49)` |
| Podcast, video, talk | `(MM:SS)` or `(HH:MM:SS)` | `(12:30)`, `(01:24:05)` |
| Web | `(§heading)` or omit | `(§methods)` |

Do not try to summarize an entire book in one note. One literature note per theme or chapter; many literature notes per source.

### Permanent Notes

A permanent note answers: **what is one thing I believe, and why?**

The title **is** the claim. Not the topic. This is the single habit that separates a live Zettelkasten from a filing cabinet.

- Bad (topic): `Risk management.md`
- Good (claim): `Risk appetite is a board-level choice, not a risk-team calculation.md`

**Creating the note:**

*In Neovim:* press `<leader>oN`. Pick the `permanent` template. Type the title as a full declarative sentence, sentence case. The note is created in `3-permanent/`.

*In Obsidian:* right-click `3-permanent/` in the file explorer, select **New note**. Title as a claim. Press `Ctrl+P`, type "Insert template", choose `permanent`.

**Filling in the template:**

| Section | What to write |
|---|---|
| **Body** | One or two paragraphs stating the claim and why you hold it. Your own words only. |
| **Connections** | Link to at least one other note. Use `[[Note Title]]` and write a because-clause explaining the relationship. |
| **Attachments** | Images, diagrams, or files that support the claim. |

**The one rule:** every permanent note must link to at least one other permanent or literature note. An unlinked note is a dead end. If you cannot find a link, move the note back to `0-fleeting/` until you can.

**What "atomic" means, concretely:**

If your note title contains "and" or "also" at the top level, split it.

- `Risk registers decay without an owner, and controls need testing cadence.md` becomes:
  - `Risk registers decay without an assigned owner.md`
  - `Controls require a defined testing cadence to remain effective.md`
- Now each can be linked independently from different contexts.

### Writing Notes

Writing notes hold long-form compositions from tweets and posts to essays and reports. Press `<leader>oN`, pick `writing`, type a title. The note is created in `4-writing/` with the template applied. Set `status: draft` initially; mark `published` or `abandoned` when the piece exits active composition.

**No bibliography section in the template.** The vault already tracks sources in `1-sources/` and connections via `## Connections`. For a piece that needs a formal reference list (academic journal, formatted citations), add `## References` at the bottom of that specific piece by hand, in whatever citation style the venue requires. Citation styles are venue-specific; baking one into the template would be wrong for most pieces.

**Where to put the piece content.** Write directly into the Draft section. The Outline section is optional; for short pieces, skip it. The Audience section exists to remind you who the reader is before you start.

### Index Notes

Do not create index notes up front. When you notice 5-10 permanent notes circling the same theme, create one in `5-index/`:

1. *Neovim:* press `<leader>oN`, pick the `index` template, type the theme as a title.
   *Obsidian:* right-click `5-index/` in the file explorer, select **New note**. Press `Ctrl+P`, type "Insert template", choose `index`.
2. Write it as a **guided tour**, not a list:
   - **Path**: sequence notes in a reading order that tells a story or builds an argument.
   - **Gaps**: missing coverage in the cluster. These are seeds for future permanent notes.

If you find yourself writing "see also" followed by 30 bullets, you are making a table of contents, not an index note. Stop and argue for a path through the notes instead.

## Promoting Notes

This is the most frequent workflow: turning a fleeting note into a source+literature pair or a permanent note.

### Side-by-side method

Best when you need to reference the fleeting note while writing.

1. Open the fleeting note (from neo-tree or `<leader>oo`).
2. Split the screen: `<leader>|` (vertical split, side by side).
3. In the new right pane, press `<leader>oN`. Pick the target template (`source`, `literature`, or `permanent`). Type the title. The new note is created in the correct folder with the template applied.
4. You now have the fleeting note on the left, the new note on the right. Use `Ctrl+h` / `Ctrl+l` to move focus between panes. Copy lines with `yy` in one pane, switch panes, paste with `p`.
5. Write the content in the new note. Add at least one `[[link]]` for permanent notes. For literature notes, set the `source:` field.
6. Close the left pane: `<leader>wd` (closes the window, not the buffer).
7. Delete the fleeting note: `<leader>e` to open neo-tree, navigate to it in `0-fleeting/`, press `d`.

### Quick method

Best when the fleeting note is short and you can hold the idea.

1. Open the fleeting note, read it, close it (`<leader>bd`).
2. Press `<leader>oN`, pick the template, type the title.
3. Write the promoted note from memory.
4. Delete the fleeting note via neo-tree.

Fleeting notes rarely have backlinks, so nothing is lost by deleting them.

## Linking

Linking is the core habit. Do it every time you write in `3-permanent/`.

**In Neovim:** type `[[` in Insert mode. obsidian.nvim opens a fuzzy picker over all note names. Start typing to filter, select a note, press Enter. The link inserts as `[[Note Title]]`.

**In Obsidian:** type `[[`. An autocomplete dropdown appears. Start typing to filter. Select the target.

After inserting the link, write a short because-clause. A link without reasoning is decoration.

```markdown
This extends [[Risk appetite is a board-level choice, not a risk-team calculation]]
because tolerance sits one level below appetite and is owned by the executive,
not the board.
```

**Discovery tools for finding connections:**

| Action | Neovim | Obsidian desktop |
|---|---|---|
| Backlinks (who links here?) | `<leader>ob` | Right sidebar > Backlinks panel |
| Outgoing links (where does this point?) | `<leader>ol` | Right sidebar > Outgoing links panel |
| Search vault content | `<leader>os` | `Ctrl+Shift+F` |
| Find note by name | `<leader>oo` | `Ctrl+O` (Quick Switcher) |
| Visual link map | N/A | `Ctrl+G` (Graph view) |

Check backlinks every time you open a permanent note or a source note. Source backlinks show every literature note drawn from that work; unexpected permanent-note backlinks are the Zettelkasten's serendipity engine.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Titling permanent notes as topics ("Risk management") | Re-title as a claim ("Risk management fails when controls lack owners") |
| Writing permanent notes with no links | Enforce the one-rule: no unlinked permanent notes. Move back to fleeting if stuck. |
| Hoarding fleeting notes for weeks | Triage daily. Deletion is a valid outcome. |
| Copy-pasting from sources into permanent notes | That is a literature note. Permanent notes must be in your words. |
| Re-entering bibliographic data in each literature note | Create the source note once in `1-sources/`; reference it via `source: "[[slug]]"` in every literature note from that work. |
| Creating sub-folders inside `3-permanent/` | Links are the structure. Folders are storage. Keep `3-permanent/` flat. |
| Renaming files with `mv` in the terminal | Use neo-tree or Obsidian's file explorer. Links break otherwise. |
| Multi-idea notes ("X and also Y") | Split into atomic notes. One claim per file. |
| Waiting for the "right" title before writing | Write the note, title later. Rename is cheap; both editors update links. |
| Creating permanent notes with `<leader>on` instead of `<leader>oN` | `<leader>on` creates fleeting notes. Use `<leader>oN` to pick the target template and route directly. |
| Ignoring backlinks | Check backlinks (`<leader>ob` or Obsidian's right sidebar) on source, literature, and permanent notes. |

## Using Obsidian

### Desktop

Obsidian reads the same markdown files as Neovim. No import, no sync delay beyond Syncthing.

Key actions: `Ctrl+O` (Quick Switcher), `Ctrl+Shift+F` (search), `Ctrl+G` (graph view), `Ctrl+P` (command palette), `Ctrl+N` (new note). The command palette (`Ctrl+P`) is the Swiss Army knife; any action you cannot find has a command there.

Keep the **Backlinks panel** visible in the right sidebar while writing permanent notes. It shows every note that links to the current note.

**Note:** repo docs (README.md, WORKFLOW.md, etc.) appear in the file explorer sidebar. They are hidden from search, graph, and link suggestions via `userIgnoreFilters` in `.obsidian/app.json`, but Obsidian does not support hiding files from the explorer as of 2026-04.

### Mobile

Obsidian mobile is for capture, not composition.

1. Open Obsidian. Tap `+` to create a new note.
2. Confirm the default folder is `0-fleeting/` (Settings > Files and links > Default location > `0-fleeting`).
3. Type the thought. Save. Syncthing pushes it to the hub within seconds to minutes.

**Insert template on mobile:** swipe down (pull) on an open note to trigger the template picker. Templates are not auto-applied on mobile; process raw captures during triage.

**Limitations:** Syncthing on Android pauses on battery saver. Do not rename or move notes from the Android Files app; use Obsidian's file explorer only.

## Using Neovim

This section covers Neovim, neo-tree, and obsidian.nvim basics relevant to the vault workflow. It assumes [LazyVim](https://www.lazyvim.org/) as the Neovim distribution.

### Starting a Session

```bash
nvim ~/vault/0-fleeting/
```

This opens the `0-fleeting/` directory listing in neo-tree.

### Screen Layout

```text
┌──────────┬──────────────────────────────────┐
│ Neo-tree │  Buffer tab bar                  │
│ (sidebar)├──────────────────────────────────┤
│          │                                  │
│ 0-fleeti.│  Editor area                     │
│ 1-source.│  (your note content goes here)   │
│ 2-litera.│                                  │
│ 3-perman.│                                  │
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
| `r` | Rename (obsidian.nvim updates all wiki-links) |
| `d` | Delete (confirms before deleting) |
| `m` | Move (prompts for destination path) |
| `s` | Open in a vertical split (side by side) |
| `/` | Fuzzy filter the tree |

**Creating a note in a specific folder:** the recommended way is `<leader>oN`, which picks a template and routes the note to the correct folder automatically. Alternatively, navigate to the target folder in neo-tree, press `a`, type the full filename including `.md`, and press Enter. Notes created via neo-tree `a` do not get auto-generated frontmatter or templates; use `<leader>ot` to insert a template afterward.

### Moving and Renaming Notes Safely

Only rename or move notes through neo-tree or Obsidian's file explorer. Both editors rewrite all `[[wiki-links]]` that point to the file. To re-slug a note created outside obsidian.nvim (e.g., on mobile), open it in Neovim and press `<leader>or`. This renames the file to kebab-case, updates the `id` frontmatter, and preserves the original title as an alias.

**Never** use terminal `mv`, `rm`, ranger, or OS file managers for vault notes. They do not know about wiki-links. Every link pointing to the file will silently break.

## Quick Reference

### obsidian.nvim

| Keys | Action |
|------|--------|
| `<leader>on` | New fleeting note |
| `<leader>oN` | New note from template (picks template, routes to folder) |
| `<leader>oo` | Find note by name |
| `<leader>os` | Search vault content |
| `<leader>ob` | Show backlinks |
| `<leader>ot` | Insert template |
| `<leader>ol` | Show outgoing links |
| `<leader>op` | Paste image from clipboard |
| `<leader>or` | Rename note to slug |
| `[[` | Insert wiki-link (fuzzy picker) |

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
| `r` | Rename (updates wiki-links) |
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
| `<leader>um` | Toggle rendered markdown |

### Obsidian Desktop

| Keys | Action |
|------|--------|
| `Ctrl+N` | New note |
| `Ctrl+O` | Quick Switcher (find note by name) |
| `Ctrl+Shift+F` | Search vault |
| `Ctrl+G` | Graph view |
| `Ctrl+P` | Command palette |

## The Minimum Viable Habit

If you forget everything above, do just this:

1. Capture anything that flickers into `0-fleeting/`.
2. Empty `0-fleeting/` every evening.
3. When a fleeting came from a source, create the source note once (if new) and a literature note per theme.
4. Never write a permanent note without one `[[link]]`.

The rest compounds on top of that.
