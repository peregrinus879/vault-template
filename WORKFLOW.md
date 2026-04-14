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

**Why there is no separate "reference" step.** Some Zettelkasten descriptions separate "reference notes" (bibliographic metadata) from "literature notes" (paraphrased content). In this vault, the literature note template merges both: frontmatter holds the source metadata (`author`, `year`, `url`), and the body holds the paraphrased content. Splitting them only pays off if you routinely write multiple literature notes about different chapters of the same source. For most material, one literature note per source is sufficient.

### Why Linking Matters

The value of a Zettelkasten is in the links, not the notes. An unlinked permanent note is a dead end; a linked note is a node in a growing network where ideas compound. Every time you write in `3-permanent/`, ask: what existing note does this support, contradict, or extend? Insert a `[[wiki-link]]` and write a short clause explaining the relationship. If you cannot find a single link for a permanent note, the note is not ready. Move it back to `1-fleeting/` until you can connect it.

## Naming Conventions

A naming system drawn from Ahrens' *How to Take Smart Notes*, adapted for this vault. No Folgezettel numbering; `[[wiki-links]]` replace numeric hierarchy.

### Design Principles

- **Title as claim**: a permanent note's title is its assertion, written as a full declarative sentence. Literature titles point to the source. Fleeting titles are disposable.
- **Picker-first**: titles are the primary search key in `<leader>oo` and `[[` autocomplete. Start with the content-bearing word, not a date or tag.
- **Spaces for content, kebab for structure**: content notes use spaces because they are claims written as prose, not code identifiers. Spaces preserve readability inside `[[wiki-links]]` embedded in flowing text. Structural files (templates, daily notes) keep their existing lowercase conventions.
- **Cross-platform safety**: Syncthing moves files across Linux, Windows (WSL), and Android. Forbidden characters across that set: `: / \ ? * | < > "`. Avoid leading dots, trailing spaces, and trailing periods.
- **Filename is the single source of truth**: no separate `title:` frontmatter field or Folgezettel IDs needed. `obsidian.nvim` and Obsidian both rewrite every `[[link]]` on rename, so titles can evolve freely.

### Convention per Note Type

| Type | Pattern | Example |
|------|---------|---------|
| Daily | `YYYY-MM-DD.md` | `2026-04-13.md` |
| Review | `YYYY-MM-DD Weekly Review.md` | `2026-04-19 Weekly Review.md` |
| Fleeting | `Short phrase, sentence case.md` | `Contingency is not a buffer.md` |
| Literature | `Author YYYY - Short source title.md` | `Ahrens 2017 - How to Take Smart Notes.md` |
| Permanent | `Full claim as a sentence, sentence case, no trailing period.md` | `Risk appetite is a board-level choice, not a risk-team calculation.md` |
| Index | `Theme or question, sentence case.md` | `How controls fail in capital projects.md` |
| Project | `Project shortname - purpose.md` | `Line 3 upgrade - baseline schedule.md` |
| Meeting | `YYYY-MM-DD Counterparty - topic.md` | `2026-04-13 Sponsor - gate 2 review.md` |
| Writing | `Working title, sentence case.md` | `The case against stage-gate theatre.md` |

### Rules

1. **Sentence case, always.** Easier to scan; avoids Title Case tax on every new note.
2. **No ending punctuation** in the filename (no `.`, `?`, `!`). Keeps filenames legal on Windows and clean in the picker.
3. **Use a hyphen with spaces around it** (` - `) as the only separator. Reads like a colon, filesystem-safe.
4. **Permanent titles must be declarative claims.** If the title reads as a topic ("risk appetite"), it is wrong. Rewrite as a sentence that asserts something.
5. **Literature prefix `Author YYYY`** for stable sort and instant disambiguation between two works by the same author.
6. **ASCII only**: no em dash, no smart quotes, no slashes. Unicode works on Linux and Android but has caused issues on Windows-side Syncthing.
7. **Rename freely.** `obsidian.nvim` and Obsidian both update every `[[link]]` on rename. The filename is not a commitment; the claim is.
8. **Fleeting titles are disposable.** Do not invest effort. They die within 48 hours.
9. **Structural files stay lowercase**: daily notes (`YYYY-MM-DD.md`), templates (`fleeting.md`), repo docs. Only content notes use spaces and sentence case.

### Trade-offs

**Long filenames.** Permanent notes will routinely be 60 to 100 characters. That is a feature: it forces you to articulate the claim before writing. If the title will not fit in a sentence, the note is not atomic yet.

**Not kebab-case.** Kebab-case serves shell hygiene, URL-safety, and identifier discipline, none of which apply here. It also degrades the readability of `[[wiki-links]]` embedded in prose (`[[risk-appetite-is-a-board-level-choice]]` reads as a slug, not a claim). Kebab-case is retained for structural files only.

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

Type a short title, press Enter. The note lands in `1-fleeting/`. Insert the fleeting template with `<leader>ot` and choose `fleeting`. Write the thought in one to three sentences. Do not format, do not link, do not polish.

Note: `<leader>on` converts the title to lowercase kebab-case for the filename (e.g., typing "Contingency is not a buffer" creates `contingency-is-not-a-buffer.md`). This is fine for fleeting notes, whose titles are disposable. When promoting to literature or permanent, rename the file to follow the [naming conventions](#naming-conventions).

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

Do not skip. Do not "leave it for tomorrow." An unprocessed fleeting folder is a sign the system is stalling.

After triage, return to the daily note and fill in **Log**, **Reflections**, and **Connections**.

## Writing Notes

### Fleeting Notes

Fleeting notes exist to get thoughts out of your head. They have no quality bar.

The template (`8-templates/fleeting.md`) has minimal structure: a date, tags, type, and a title. The comment reminds you to process within 1-2 days.

Write fast. Do not format, link, or title carefully. The note dies within 48 hours: it either becomes a literature or permanent note, or it gets deleted.

### Literature Notes

A literature note answers: **what did this source say, in my words, that I might want to use later?**

**Creating the note:**

*In Neovim:* open neo-tree (`<leader>e`), navigate to `2-literature/`, press `a` to create a new file. Name it as `Author YYYY - Short source title.md`. Open the file, press `<leader>ot`, choose `literature`.

*In Obsidian:* right-click `2-literature/` in the file explorer, select **New note**. Name it following the same convention. Press `Ctrl+P`, type "Insert template", choose `literature`.

**Filling in the template:**

| Section | What to write |
|---|---|
| **Frontmatter** | `source`: full title. `author`: name. `year`: publication year. `url`: link if applicable. |
| **Summary** | 3-5 sentences. What is this source fundamentally arguing? |
| **Key Arguments** | Bullets. The author's main claims, not yours. |
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

*In Neovim:* in neo-tree, navigate to `3-permanent/`, press `a`. Title as a full declarative sentence, sentence case. Open the file, press `<leader>ot`, choose `permanent`.

*In Obsidian:* right-click `3-permanent/` in the file explorer, select **New note**. Title as a claim. Insert the permanent template via `Ctrl+P` > "Insert template".

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

Writing, project, and meeting notes follow the same pattern: create the file in the target folder, insert the template, fill in the sections. Each template is self-documenting with comments explaining what goes where.

| Type | Folder | Template | Key sections |
|---|---|---|---|
| Writing | `4-writing/` | `writing.md` | Outline, Draft, Sources. Status: draft, published, or abandoned. |
| Project | `5-projects/` | `project.md` | Objective, Scope, Deliverables, Schedule, Risks, Decisions. Status: planned, in-progress, completed, or paused. |
| Meeting | `6-meetings/` | `meeting.md` | Agenda, Discussion, Action Items, Decisions. Status: planned, held, or cancelled. |

All three templates include a **Permanent Note Candidates** section. Use it. Reusable insights from projects and meetings should graduate to permanent notes; otherwise they are locked inside a time-bound context.

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

## Using Obsidian

### Desktop

Obsidian reads the same markdown files as Neovim. No import, no sync delay beyond Syncthing.

**File explorer** (left sidebar): browse the vault directory tree. Right-click a folder to create a new note inside it. Right-click a file to rename, move, or delete. Renames and moves through Obsidian's file explorer update all `[[wiki-links]]` automatically.

**Quick Switcher** (`Ctrl+O`): fuzzy search over note titles. The fastest way to jump to any note.

**Search** (`Ctrl+Shift+F`): full-text search across the vault. Supports regex.

**Graph view** (`Ctrl+G`): visual map of all notes and their links. Orphan notes (no links) stand out immediately. Useful during the weekly review to spot clusters and unlinked notes. Not a daily tool; think of it as a periodic audit.

**Backlinks panel** (right sidebar): every note that links to the current note, with surrounding context. Keep this visible while writing permanent notes.

**Outgoing links panel** (right sidebar): every note the current note links to. Useful for verifying connections.

**Daily notes**: click the calendar icon in the left ribbon. The template is applied automatically (configured in Settings > Daily notes > Template file location > `8-templates/daily.md`).

**Insert template**: press `Ctrl+P`, type "Insert template", choose from the list. Templates live in `8-templates/`.

**Command palette** (`Ctrl+P`): the Swiss Army knife. Any action you cannot find has a command here.

**Note:** repo docs (README.md, WORKFLOW.md, etc.) appear in the file explorer sidebar. They are hidden from search, graph, and link suggestions via `userIgnoreFilters` in `.obsidian/app.json`, but Obsidian does not support hiding files from the explorer as of 2026-04.

### Mobile

Obsidian mobile is for capture, not composition.

**Capture workflow:**

1. Open Obsidian.
2. Tap `+` to create a new note.
3. Confirm the default folder is `1-fleeting/` (Settings > Files and links > Default location > `1-fleeting`).
4. Type the thought. Save.
5. Syncthing pushes it to the hub within seconds to minutes.

**Limitations:**

- Templates are not auto-applied on new notes. Mobile fleeting notes will be rawer. Process them during triage on desktop or terminal.
- Syncthing on Android pauses on battery saver. If captures are not syncing, check Syncthing-Fork is running and not throttled.
- Do not rename or move notes from the Android Files app. Use Obsidian's file explorer only; it updates wiki-links on rename and move.

## Using Neovim

This section covers Neovim, neo-tree, and obsidian.nvim basics relevant to the vault workflow. It assumes [LazyVim](https://www.lazyvim.org/) as the Neovim distribution. For a full Neovim tutorial, run `:Tutor` inside Neovim.

### Starting a Session

```bash
nvim ~/vault/0-daily/
```

This opens the `0-daily/` directory listing in Neovim. obsidian.nvim loads automatically when any `.md` file under `~/vault/` is opened. Press `<leader>od` to open today's daily note.

### Neovim Essentials

**Modes.** Neovim is a modal editor. You are always in one of these modes:

| Mode | Enter with | Purpose |
|---|---|---|
| Normal | `Esc` | Navigate, run commands, trigger keybindings. You start here. |
| Insert | `i`, `a`, or `o` | Type text. |
| Visual | `v` | Select text. |
| Command | `:` | Run Ex commands (save, quit, search-replace). |

All obsidian.nvim keybindings (`<leader>od`, `<leader>on`, etc.) work from Normal mode.

**Leader key.** In LazyVim, the leader key is `Space`. When this document says `<leader>od`, press Space, then `o`, then `d`. Press Space and wait; [which-key](https://github.com/folke/which-key.nvim) shows all available bindings.

**Navigation:**

| Keys | Action |
|---|---|
| `h` `j` `k` `l` | Move left, down, up, right (arrow keys also work) |
| `w` / `b` | Jump forward / backward by word |
| `gg` / `G` | Jump to top / bottom of file |
| `Ctrl+d` / `Ctrl+u` | Scroll half-page down / up |
| `/text` then `Enter` | Search for "text" in the file. `n` / `N` for next / previous match. |

**Editing:**

| Keys | Action |
|---|---|
| `i` | Insert text before cursor |
| `a` | Insert text after cursor |
| `o` | Open new line below and enter Insert mode |
| `O` | Open new line above and enter Insert mode |
| `dd` | Delete current line |
| `u` | Undo |
| `Ctrl+r` | Redo |
| `yy` | Copy (yank) current line |
| `p` | Paste below cursor |

**Saving and quitting:**

| Keys | Action |
|---|---|
| `:w` | Save |
| `:q` | Quit (fails if unsaved changes exist) |
| `:wq` or `ZZ` | Save and quit |
| `:q!` | Quit without saving (discards changes) |

### Neo-tree

Neo-tree is the file explorer sidebar. It is the primary tool for creating, renaming, moving, and deleting notes in Neovim.

**Toggle:** `<leader>e`

**Navigation:**

| Keys | Action |
|---|---|
| `j` / `k` | Move down / up |
| `Enter` or `l` | Open file or expand directory |
| `h` | Collapse directory or go to parent |
| `Backspace` | Go to parent directory |
| `?` | Show all neo-tree keybindings |

**File operations:**

| Keys | Action |
|---|---|
| `a` | Create new file. Type the name, press Enter. Add a trailing `/` to create a directory instead. |
| `r` | Rename file. obsidian.nvim rewrites all `[[wiki-links]]` across the vault. |
| `d` | Delete file (confirms before deleting). |
| `m` | Move file (prompts for destination path). |
| `c` | Copy file. |
| `y` | Copy file name or path. |

**Creating a note in a specific folder:** navigate to the target folder in neo-tree, press `a`, type the full filename including `.md` (e.g., `Ahrens 2017 - How to Take Smart Notes.md`), press Enter. The file is created inside that folder. This is the recommended way to create literature and permanent notes, because the filename is used exactly as typed, following the [naming conventions](#naming-conventions).

### obsidian.nvim Keybindings

Available in Normal mode when editing any `.md` file under `~/vault/`.

| Keys | Action | Command |
|---|---|---|
| `<leader>od` | Open or create today's daily note | `:Obsidian today` |
| `<leader>on` | New note (lands in `1-fleeting/`) | `:Obsidian new` |
| `<leader>oo` | Find note by name (fuzzy search) | `:Obsidian quick_switch` |
| `<leader>os` | Search vault content | `:Obsidian search` |
| `<leader>ob` | Show backlinks to current note | `:Obsidian backlinks` |
| `<leader>ot` | Insert template into current note | `:Obsidian template` |
| `<leader>ol` | Show outgoing links from current note | `:Obsidian links` |
| `<leader>op` | Paste image from clipboard | `:Obsidian paste_img` |

**Inserting a wiki-link:** type `[[` in Insert mode. A fuzzy picker appears after 2 characters. Select a note and press Enter. The link inserts as `[[Note Title]]`.

### Moving and Renaming Notes Safely

Only rename or move notes through neo-tree or Obsidian's file explorer. Both editors rewrite all `[[wiki-links]]` that point to the file.

**Never** use terminal `mv`, `rm`, ranger, or OS file managers for vault notes. They do not know about wiki-links. Every link pointing to the file will silently break.

**Promoting a fleeting note** (the most common move):

1. In neo-tree (`<leader>e`), navigate to the fleeting note in `1-fleeting/`.
2. Press `r` to rename. Change the title to a claim-style sentence (see [naming conventions](#naming-conventions)). If the file was created with `<leader>on`, the filename will be in kebab-case; rename it to use spaces.
3. Press `m` to move. Type the destination path (e.g., `3-permanent/` or `2-literature/`).
4. Open the note. Insert the target template (`<leader>ot` > choose `permanent` or `literature`), replacing the fleeting template content.
5. Write the content. Add at least one `[[link]]` for permanent notes.

Alternative: create a fresh note directly in the target folder with `a` in neo-tree, write the content there, and delete the fleeting note. Same result. Fleeting notes rarely have backlinks, so nothing is lost.

## The Weekly Review (15-30 minutes)

Do this on Sunday evening or Monday morning.

1. Create `YYYY-MM-DD Weekly Review.md` in `0-daily/`.
   - *Neovim:* navigate to `0-daily/` in neo-tree, press `a`, type the filename.
   - *Obsidian:* right-click `0-daily/` > New note.
2. Insert the `review` template (`<leader>ot` in Neovim, `Ctrl+P` > "Insert template" in Obsidian).
3. Walk through each template section. Key trigger questions:
   - Any fleeting notes older than 48 hours? Process or delete them now.
   - Any cluster of 5+ permanent notes on one theme? Start an index note in `7-index/`.
   - Any permanent notes with zero links? Find a link or move them back to fleeting.
   - What surprised you this week? That surprise is the seed of a permanent note.
4. Open the graph view in Obsidian (`Ctrl+G`). Look for:
   - Orphan nodes (notes with no links). Fix or delete.
   - Emerging clusters (groups of interconnected notes). Consider an index note.
   - Unexpected connections. Follow them; they often produce the best permanent notes.

## Index Notes

Do not create index notes up front. When you notice 5-10 permanent notes circling the same theme, create one in `7-index/`:

1. Create the file in `7-index/` (neo-tree `a` in Neovim, or right-click in Obsidian's file explorer).
2. Insert the `index` template.
3. Write it as a **guided tour**, not a list:
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
| Using `<leader>on` for permanent notes without renaming | `<leader>on` creates kebab-case filenames. When promoting, rename to spaces and claim-style title. Or create directly in `3-permanent/` with neo-tree `a`. |
| Ignoring backlinks | Check backlinks (`<leader>ob` or Obsidian's right sidebar) every time you open a permanent note. They surface connections you did not plan. |

## Quick Reference

### obsidian.nvim

| Keys | Action |
|------|--------|
| `<leader>od` | Open/create daily note |
| `<leader>on` | New note (lands in `1-fleeting/`) |
| `<leader>oo` | Find note by name |
| `<leader>os` | Search vault content |
| `<leader>ob` | Show backlinks |
| `<leader>ot` | Insert template |
| `<leader>ol` | Show outgoing links |
| `<leader>op` | Paste image from clipboard |
| `[[` | Insert wiki-link (fuzzy picker) |

### Neo-tree

| Keys | Action |
|------|--------|
| `<leader>e` | Toggle file explorer |
| `a` | Create file (or directory with trailing `/`) |
| `r` | Rename (updates wiki-links) |
| `m` | Move |
| `d` | Delete |
| `?` | Show all keybindings |

### Obsidian Desktop

| Keys | Action |
|------|--------|
| `Ctrl+N` | New note |
| `Ctrl+O` | Quick Switcher (find note by name) |
| `Ctrl+Shift+F` | Search vault |
| `Ctrl+G` | Graph view |
| `Ctrl+P` | Command palette (templates, daily note, etc.) |

### Neovim Basics

| Keys | Action |
|------|--------|
| `i` / `a` / `o` | Enter Insert mode (before cursor / after cursor / new line below) |
| `Esc` | Return to Normal mode |
| `<leader>` (Space) | Open which-key menu (shows all bindings) |
| `:w` | Save |
| `:wq` or `ZZ` | Save and quit |
| `u` / `Ctrl+r` | Undo / Redo |

## The Minimum Viable Habit

If you forget everything above, do just this:

1. Open the daily note every morning.
2. Capture anything that flickers.
3. Empty `1-fleeting/` every evening.
4. Never write a permanent note without one `[[link]]`.

The rest compounds on top of that.
