# Vault Workflow

A hands-on tutorial for running a Zettelkasten in this vault. It covers two editors: [Obsidian](https://obsidian.md) (desktop and mobile GUI) and [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim) (terminal, inside Neovim). Both read the same markdown files in the same folder. You do not need to pick one; use Neovim at the keyboard, Obsidian mobile for capture on the go, Obsidian desktop when you want the graph view. For installation and device setup, see [SETUP.md](SETUP.md).

## The Method

### Note Types

| Type | Folder | Job |
|------|--------|-----|
| Daily | `0-daily/` | Timestamped anchor for the day. Plan, log, reflect. |
| Fleeting | `1-fleeting/` | Half-thoughts. Written fast, processed within 24-48h, then deleted. |
| Literature | `2-literature/` | What someone else said, paraphrased in your words, tied to a source. |
| Permanent | `3-permanent/` | What **you** think. One claim per note, linked to other notes. |

The vault also has folders for writing (`4-writing/`), projects (`5-projects/`), meetings (`6-meetings/`), and index notes (`7-index/`). Master the four core types first. See [README.md](README.md) for the full directory layout and status lifecycles.

### The Flow

```text
                  ┌──────────────────── Discard
                  │
Capture ── Fleeting ──── Literature ──── (persists, seeds permanent notes)
                  │                         │
                  │                         ▼
                  └─────────────────── Permanent ──── Writing / Index
```

Three paths out of fleeting:

1. **The thought came from a source** (book, article, video, podcast, conversation). Create a literature note in `2-literature/`. Delete the fleeting note.
2. **The thought is your own and worth keeping.** Create a permanent note in `3-permanent/`. Delete the fleeting note.
3. **The thought is noise.** Delete the fleeting note. This is the correct answer more often than not.

Literature notes persist. They are a lasting record of what a source said, in your words. Over time, a single literature note seeds multiple permanent notes as your thinking develops. You do not delete or "promote" literature notes; they stay in `2-literature/` and accumulate links.

Permanent notes are the core of the Zettelkasten. Each one states a single claim, links to at least one other note, and is written in your own words. They grow in value as the link network grows.

**Why there is no separate "reference" step.** Some Zettelkasten descriptions separate "reference notes" (bibliographic metadata) from "literature notes" (paraphrased content). In this vault, the literature note template merges both: frontmatter holds the `source` field, and the body holds the paraphrased content. Splitting them only pays off if you routinely write multiple literature notes about different chapters of the same source. For most material, one literature note per source is sufficient.

### Why Linking Matters

The value of a Zettelkasten is in the links, not the notes. An unlinked permanent note is a dead end; a linked note is a node in a growing network where ideas compound. Every time you write in `3-permanent/`, ask: what existing note does this support, contradict, or extend? Insert a `[[wiki-link]]` and write a short clause explaining the relationship. If you cannot find a single link for a permanent note, the note is not ready. Move it back to `1-fleeting/` until you can connect it.

## Naming Conventions

A naming system drawn from Ahrens' *How to Take Smart Notes*, adapted for this vault. No Folgezettel numbering; `[[wiki-links]]` replace numeric hierarchy.

### How It Works

obsidian.nvim auto-generates filenames and aliases from the title you type:

1. You type a title (e.g., "Risk appetite is a board-level choice")
2. `note_id_func` creates a slug filename: `risk-appetite-is-a-board-level-choice.md`
3. The `aliases` frontmatter field preserves your original title for search and `[[link]]` autocomplete

You never need to think about the filename. Type the title naturally; the slug is generated for you.

### Design Principles

- **Title as claim**: a permanent note's title is its assertion, written as a full declarative sentence. Literature titles point to the source. Fleeting titles are disposable.
- **Picker-first**: titles are the primary search key in `<leader>oo` and `[[` autocomplete. Start with the content-bearing word, not a date or tag.
- **Slug filenames, readable aliases**: all notes get auto-generated lowercase-hyphenated filenames. The human-readable title lives in the `aliases` frontmatter field, which powers search and link autocomplete. You see the readable title in pickers; the filesystem sees the slug.
- **Cross-platform safety**: Syncthing moves files across Linux, Windows (WSL), and Android. Slug filenames avoid all platform-specific character issues by design (lowercase, hyphens, alphanumeric only).
- **Aliases are the single source of truth for display**: the `aliases` field is what appears in search, autocomplete, and link resolution. Both obsidian.nvim and Obsidian rewrite every `[[link]]` on rename, so titles can evolve freely.

### Convention per Note Type

The "title" column is what you type when creating a note. obsidian.nvim converts it to a slug filename and stores the original as an alias.

| Type | Title you type | Slug filename |
|------|---------------|---------------|
| Daily | (auto, via `<leader>od`) | `2026-04-13.md` |
| Review | `2026-04-19 Weekly Review` | `2026-04-19-weekly-review.md` |
| Fleeting | `Contingency is not a buffer` | `contingency-is-not-a-buffer.md` |
| Literature | `Ahrens 2017 - How to Take Smart Notes` | `ahrens-2017---how-to-take-smart-notes.md` |
| Permanent | `Risk appetite is a board-level choice, not a risk-team calculation` | `risk-appetite-is-a-board-level-choice-not-a-risk-team-calculation.md` |
| Writing | `The case against stage-gate theatre` | `the-case-against-stage-gate-theatre.md` |
| Project | `Line 3 upgrade - baseline schedule` | `line-3-upgrade---baseline-schedule.md` |
| Meeting | `2026-04-13 Sponsor - gate 2 review` | `2026-04-13-sponsor---gate-2-review.md` |
| Index | `How controls fail in capital projects` | `how-controls-fail-in-capital-projects.md` |

### Rules

1. **Sentence case, always.** Easier to scan; avoids Title Case tax on every new note.
2. **Permanent titles must be declarative claims.** If the title reads as a topic ("risk appetite"), it is wrong. Rewrite as a sentence that asserts something.
3. **ASCII only in titles**: no em dash, no smart quotes, no slashes. The slug function strips non-alphanumeric characters.
4. **Rename freely.** obsidian.nvim and Obsidian both update every `[[link]]` on rename. The title is not a commitment; the claim is.
5. **Fleeting titles are disposable.** Do not invest effort. They die within 48 hours.
6. **Type the title naturally.** Do not think about filenames. The slug is generated automatically.

### Trade-offs

**Long slug filenames.** Permanent notes produce long filenames (60-100+ characters after slugification). This is fine; you never type or read the slug. The alias carries the readable title. The long slug is a side effect of long, claim-style titles, which force atomicity.

**Aliases in links.** Wiki-links display the alias, not the slug. When you type `[[` and select a note, the link resolves through the alias. If a link renders as a slug in some context, you can add a display name: `[[slug-filename|Readable title]]`.

## The Daily Loop

### Morning: Anchor the Day

Open the vault and create or open today's daily note.

**In Neovim:**

```
nvim ~/vault/0-daily/
<leader>od
```

**In Obsidian desktop:** click the **Open today's daily note** icon in the left ribbon (calendar icon), or press `Ctrl+P` and type "daily".

**In Obsidian mobile:** tap the calendar icon in the bottom toolbar, or open the command palette and search for "daily".

The daily note is your timeline. Fill in **Plan** with 3-5 bullets. Do not over-plan. If something comes up during the day that does not warrant its own fleeting note, drop it under **Log**.

### Throughout the Day: Capture

When a thought appears that is not tied to your current task, capture it immediately. Speed matters more than structure.

**In Neovim:**

```
<leader>on
```

Type a short title, press Enter. The note lands in `1-fleeting/` with the fleeting template applied automatically: frontmatter (`id`, `aliases`, `tags`) and body structure are ready. Write the thought in one to three sentences below the comment. Do not format, do not link, do not polish.

The filename is a slug (e.g., typing "Contingency is not a buffer" creates `contingency-is-not-a-buffer.md`). Your original title is preserved in the `aliases` field for search and link autocomplete.

**In Obsidian desktop:** press `Ctrl+N` to create a new note. It lands in `1-fleeting/` (configured in Settings > Files and links > Default location). Type the thought.

**In Obsidian mobile:** tap the `+` icon or new-note button. Confirm the default folder is `1-fleeting/` (Settings > Files and links > Default location for new notes > In the folder specified below > `1-fleeting`). Type, save. Syncthing pushes it to the hub within seconds to minutes.

Mobile captures will not have the fleeting template applied automatically. That is fine; you will process them during triage.

### End of Day: Triage (2-5 minutes)

Open the fleeting folder.

**In Neovim:** `nvim ~/vault/1-fleeting/`

**In Obsidian:** expand `1-fleeting/` in the file explorer sidebar.

For each note, make one decision:

| If the thought... | Then... |
|---|---|
| Came from something you read, watched, or heard | Create a literature note in `2-literature/`. Delete the fleeting note. |
| Is your own and worth keeping | Create a permanent note in `3-permanent/`. Delete the fleeting note. |
| Is noise or redundant | Delete the fleeting note. |

Do not skip. Do not "leave it for tomorrow." An unprocessed fleeting folder is a sign the system is stalling. See [Literature Notes](#literature-notes) and [Permanent Notes](#permanent-notes) for step-by-step creation.

After triage, return to the daily note and fill in **Log**, **Reflections**, and **Connections**.

## Writing Notes

### Note Anatomy

Every note has two parts separated by `---` fences:

1. **Frontmatter** (between the `---` lines): metadata like `id`, `aliases`, and `tags`. Do not write content here.
2. **Body** (everything after the closing `---`): your actual content. The title heading, template sections, and your writing live here.

When you create a note with `<leader>on`, the fleeting template is applied automatically. When you create a note with `<leader>oN`, you pick a template and the note is routed to the correct folder. In both cases, obsidian.nvim generates the base frontmatter:

- **`id`**: the slugified filename (e.g., `quis-custodiet-ipsos-custodes`). Used internally for linking.
- **`aliases`**: the original title you typed, preserving spaces and punctuation. Used for search and `[[link]]` autocomplete.
- **`tags`**: empty by default. Add tags as needed.

Some templates add type-specific fields (e.g., `source` for literature notes, `status` for project notes). Write your content in the body, below any instructional comments.

### Fleeting Notes

Fleeting notes exist to get thoughts out of your head. They have no quality bar.

The template (`8-templates/fleeting.md`) has minimal structure: `id`, `aliases`, `tags`, and a title heading. The comment reminds you to process within 1-2 days.

Write fast. Do not format, link, or title carefully. The note dies within 48 hours: it either becomes a literature or permanent note, or it gets deleted.

### Literature Notes

A literature note answers: **what did this source say, in my words, that I might want to use later?**

**Creating the note:**

*In Neovim:* press `<leader>oN`. Pick the `literature` template from the picker. Type the title (e.g., "Ahrens 2017 - How to Take Smart Notes"). The note is created in `2-literature/` with a slug filename and the literature template applied.

*In Obsidian:* right-click `2-literature/` in the file explorer, select **New note**. Press `Ctrl+P`, type "Insert template", choose `literature`.

**Filling in the template:**

| Section | What to write |
|---|---|
| **Frontmatter** | `source`: full reference (title, author, year, URL as applicable). |
| **Summary** | 3-5 sentences. What is this source fundamentally arguing? |
| **Key Ideas** | Bullets. The author's main claims, not yours. |
| **Notable Passages** | Paraphrase or quote, but each must be followed by *why it matters to you*. A quote without your reaction is decoration. |
| **My Response** | Where you disagree, where you are convinced, what it connects to in your existing thinking. |
| **Permanent Note Candidates** | Bullets. Each bullet is a seed for a separate permanent note. This is the most important section; it drives future permanent notes. |
| **Connections** | Link to existing notes with `[[...]]`. Explain the link with a because-clause. |

Do not try to summarize an entire book in one note. One source = one literature note, but it may seed many permanent notes over time.

### Permanent Notes

A permanent note answers: **what is one thing I believe, and why?**

The title **is** the claim. Not the topic. This is the single habit that separates a live Zettelkasten from a filing cabinet.

- Bad (topic): `Risk management.md`
- Good (claim): `Risk appetite is a board-level choice, not a risk-team calculation.md`

**Creating the note:**

*In Neovim:* press `<leader>oN`. Pick the `permanent` template from the picker. Type the title as a full declarative sentence, sentence case. The note is created in `3-permanent/` with a slug filename and the permanent template applied.

*In Obsidian:* right-click `3-permanent/` in the file explorer, select **New note**. Title as a claim. Press `Ctrl+P`, type "Insert template", choose `permanent`.

**Filling in the template:**

| Section | What to write |
|---|---|
| **Frontmatter** | `source`: the literature note or external source that prompted this, if any. |
| **Body** | One or two paragraphs stating the claim and why you hold it. Your own words only. |
| **Why It Matters** | What decisions or other ideas does this claim affect? |
| **Connections** | Link to at least one other note. Use `[[Note Title]]` and write a because-clause explaining the relationship. |
| **References** | The literature notes or external sources that support it. Use `[[Author YYYY - Title]]`. |

**The one rule:** every permanent note must link to at least one other permanent or literature note. An unlinked note is a dead end. If you cannot find a link, move the note back to `1-fleeting/` until you can.

**What "atomic" means, concretely:**

If your note title contains "and" or "also" at the top level, split it.

- `Risk registers decay without an owner, and controls need testing cadence.md` becomes:
  - `Risk registers decay without an assigned owner.md`
  - `Controls require a defined testing cadence to remain effective.md`
- Now each can be linked independently from different contexts.

### Other Note Types

Writing, project, and meeting notes follow the same pattern: press `<leader>oN`, pick the template, type a title. The note is created in the correct folder with the template applied. Each template is self-documenting with comments explaining what goes where.

| Type | Folder | Template | Key sections |
|---|---|---|---|
| Writing | `4-writing/` | `writing.md` | Outline, Draft, Sources. Status: draft, published, or abandoned. |
| Project | `5-projects/` | `project.md` | Objective, Scope, Deliverables, Schedule, Risks, Decisions. Status: planned, in-progress, completed, or paused. |
| Meeting | `6-meetings/` | `meeting.md` | Attendees, Agenda, Discussion, Action Items, Decisions. Status: planned, held, or cancelled. |

All three templates include a **Permanent Note Candidates** section. Use it. Reusable insights from projects and meetings should graduate to permanent notes; otherwise they are locked inside a time-bound context.

## Promoting Notes

This is the most frequent workflow: turning a fleeting note into a literature or permanent note.

### Side-by-side method

Best when you need to reference the fleeting note while writing.

1. Open the fleeting note (from neo-tree or `<leader>oo`).
2. Split the screen: `<leader>|` (vertical split, side by side).
3. In the new right pane, press `<leader>oN`. Pick the target template (e.g., `permanent` or `literature`). Type the title. The new note is created in the correct folder with the template applied.
4. You now have the fleeting note on the left, the new note on the right. Use `Ctrl+h` / `Ctrl+l` to move focus between panes. Copy lines with `yy` in one pane, switch panes, paste with `p`.
5. Write the content in the new note. Add at least one `[[link]]` for permanent notes.
6. Close the left pane: `<leader>wd` (closes the window, not the buffer).
7. Delete the fleeting note: `<leader>e` to open neo-tree, navigate to it in `1-fleeting/`, press `d`.

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

Check backlinks every time you open a permanent note. Unexpected backlinks are the Zettelkasten's serendipity engine.

## The Weekly Review (15-30 minutes)

Do this on Sunday evening or Monday morning.

1. Create the review note.
   - *Neovim:* press `<leader>oN`, pick the `review` template, type the title (e.g., "2026-04-19 Weekly Review"). The note is created in `0-daily/`.
   - *Obsidian:* right-click `0-daily/` > New note. Press `Ctrl+P`, type "Insert template", choose `review`.
2. Walk through each template section. Key trigger questions:
   - Any fleeting notes older than 48 hours? Process or delete them now.
   - Any cluster of 5+ permanent notes on one theme? Start an index note in `7-index/`.
   - Any permanent notes with zero links? Find a link or move them back to fleeting.
   - What surprised you this week? That surprise is the seed of a permanent note.
3. Open the graph view in Obsidian (`Ctrl+G`). Look for:
   - Orphan nodes (notes with no links). Fix or delete.
   - Emerging clusters (groups of interconnected notes). Consider an index note.
   - Unexpected connections. Follow them; they often produce the best permanent notes.

## Index Notes

Do not create index notes up front. When you notice 5-10 permanent notes circling the same theme, create one in `7-index/`:

1. *Neovim:* press `<leader>oN`, pick the `index` template, type the theme as a title. The note is created in `7-index/`.
   *Obsidian:* right-click `7-index/` in the file explorer, select **New note**. Press `Ctrl+P`, type "Insert template", choose `index`.
2. Write it as a **guided tour**, not a list:
   - **Entry Points**: the 2-3 notes that introduce the theme.
   - **Argument / Path**: arrange notes in a sequence that builds an argument or tells a story.
   - **Open Questions**: what the cluster does not yet answer. These are seeds for future permanent notes.

If you find yourself writing "see also" followed by 30 bullets, you are making a table of contents, not an index note. Stop and argue for a path through the notes instead.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Titling permanent notes as topics ("Risk management") | Re-title as a claim ("Risk management fails when controls lack owners") |
| Writing permanent notes with no links | Enforce the one-rule: no unlinked permanent notes. Move back to fleeting if stuck. |
| Hoarding fleeting notes for weeks | Triage daily. Deletion is a valid outcome. |
| Copy-pasting from sources into permanent notes | That is a literature note. Permanent notes must be in your words. |
| Creating sub-folders inside `3-permanent/` | Links are the structure. Folders are storage. Keep `3-permanent/` flat. |
| Renaming files with `mv` in the terminal | Use neo-tree or Obsidian's file explorer. Links break otherwise. |
| Multi-idea notes ("X and also Y") | Split into atomic notes. One claim per file. |
| Waiting for the "right" title before writing | Write the note, title later. Rename is cheap; both editors update links. |
| Creating permanent notes with `<leader>on` instead of `<leader>oN` | `<leader>on` creates fleeting notes. Use `<leader>oN` to pick the permanent template and route directly to `3-permanent/`. |
| Ignoring backlinks | Check backlinks (`<leader>ob` or Obsidian's right sidebar) every time you open a permanent note. They surface connections you did not plan. |

## Using Obsidian

### Desktop

Obsidian reads the same markdown files as Neovim. No import, no sync delay beyond Syncthing.

Key actions: `Ctrl+O` (Quick Switcher), `Ctrl+Shift+F` (search), `Ctrl+G` (graph view), `Ctrl+P` (command palette), `Ctrl+N` (new note). The command palette (`Ctrl+P`) is the Swiss Army knife; any action you cannot find has a command there.

Keep the **Backlinks panel** visible in the right sidebar while writing permanent notes. It shows every note that links to the current note.

**Note:** repo docs (README.md, WORKFLOW.md, etc.) appear in the file explorer sidebar. They are hidden from search, graph, and link suggestions via `userIgnoreFilters` in `.obsidian/app.json`, but Obsidian does not support hiding files from the explorer as of 2026-04.

### Mobile

Obsidian mobile is for capture, not composition.

1. Open Obsidian. Tap `+` to create a new note.
2. Confirm the default folder is `1-fleeting/` (Settings > Files and links > Default location > `1-fleeting`).
3. Type the thought. Save. Syncthing pushes it to the hub within seconds to minutes.

**Insert template on mobile:** swipe down (pull) on an open note to trigger the template picker. Templates are not auto-applied on mobile; process raw captures during triage.

**Limitations:** Syncthing on Android pauses on battery saver. Do not rename or move notes from the Android Files app; use Obsidian's file explorer only.

## Using Neovim

This section covers Neovim, neo-tree, and obsidian.nvim basics relevant to the vault workflow. It assumes [LazyVim](https://www.lazyvim.org/) as the Neovim distribution.

### Starting a Session

```bash
nvim ~/vault/0-daily/
```

This opens the `0-daily/` directory listing in neo-tree. Press `<leader>od` to open today's daily note.

### Screen Layout

```text
┌──────────┬──────────────────────────────────┐
│ Neo-tree │  Buffer tab bar                  │
│ (sidebar)├──────────────────────────────────┤
│          │                                  │
│ 0-daily/ │  Editor area                     │
│ 1-fleeti.│  (your note content goes here)   │
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

**One rule to remember:** `Ctrl` + a vim direction (`h`/`j`/`k`/`l`) always moves focus between areas and splits. It works the same way everywhere: neo-tree to editor, editor to neo-tree, split to split.

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

All obsidian.nvim keybindings (`<leader>od`, `<leader>on`, etc.) work from Normal mode.

**Leader key.** In LazyVim, the leader key is `Space`. When this document says `<leader>od`, press Space, then `o`, then `d`. Press Space and wait; [which-key](https://github.com/folke/which-key.nvim) shows all available bindings grouped by category. If you forget any keybinding, press Space and read the menu.

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

Only rename or move notes through neo-tree or Obsidian's file explorer. Both editors rewrite all `[[wiki-links]]` that point to the file.

**Never** use terminal `mv`, `rm`, ranger, or OS file managers for vault notes. They do not know about wiki-links. Every link pointing to the file will silently break.

## Quick Reference

### obsidian.nvim

| Keys | Action |
|------|--------|
| `<leader>od` | Open/create daily note |
| `<leader>on` | New fleeting note |
| `<leader>oN` | New note from template (picks template, routes to folder) |
| `<leader>oo` | Find note by name |
| `<leader>os` | Search vault content |
| `<leader>ob` | Show backlinks |
| `<leader>ot` | Insert template |
| `<leader>ol` | Show outgoing links |
| `<leader>op` | Paste image from clipboard |
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

1. Open the daily note every morning.
2. Capture anything that flickers.
3. Empty `1-fleeting/` every evening.
4. Never write a permanent note without one `[[link]]`.

The rest compounds on top of that.
