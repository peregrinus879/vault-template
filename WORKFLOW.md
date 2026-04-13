# Vault Workflow

A beginner's walkthrough for running a Zettelkasten in this vault using `obsidian.nvim` (terminal) and the Obsidian app (mobile, desktop). Read it once end-to-end, then use it as reference.

## What You're Learning at Once

You are learning four things in parallel. Keep them straight:

1. **Note-taking**: the habit of writing down thoughts in your own words.
2. **Zettelkasten**: a method where atomic notes link to each other so ideas compound over time. The value is in the links, not the notes.
3. **Obsidian**: a GUI app that reads a folder of markdown files. It gives you a graph, backlinks, and search.
4. **obsidian.nvim**: a Neovim plugin that replicates the core Obsidian features inside your terminal.

You do not need to pick one editor. They read the same files. Use `nvim` when you are at the keyboard, Obsidian mobile for capture on the go, Obsidian desktop when you want the graph view.

## The Mental Model (Ahrens, in Plain Terms)

Four core note types, four jobs:

| Type | Folder | One-line job |
|------|--------|--------------|
| Daily | `0-daily/` | Timestamped anchor for the day. Plan, log, reflect. |
| Fleeting | `1-fleeting/` | Half-thoughts. Written fast, processed within 24-48h, then deleted. |
| Literature | `2-literature/` | What someone else said, paraphrased in your words, tied to a source. |
| Permanent | `3-permanent/` | What **you** think, one claim per note, linked to other notes. |

The flow is always the same: **capture (fleeting) --> process (literature or permanent) --> link --> discard the fleeting**.

Ahrens' rule: a fleeting note is a confession that you were too lazy to write a real note. Keep that drawer empty.

The vault also has folders for writing (`4-writing/`), projects (`5-projects/`), and meetings (`6-meetings/`). See README.md for their purpose and status lifecycle. Master the four core types first.

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

## First Time Setup Check

Before the daily loop, confirm the plumbing works. Do each once:

1. Open a terminal and run `nvim ~/vault/0-daily/`. A directory listing opens.
2. Press `<leader>od` (leader is likely `\` or `<space>`; check `:map <leader>` in nvim if unsure). Today's daily note should open, populated from the `daily.md` template.
3. Press `<leader>on`, type `test`, press Enter. A new file lands in `1-fleeting/test.md`.
4. In the new file, press `<leader>ot` and pick the `fleeting` template. Frontmatter fills in.
5. Delete the file: open neo-tree (`<leader>e`), navigate to `1-fleeting/test.md`, press `d` to delete. You just confirmed capture, templating, and cleanup.

If any step fails, stop and fix it before building habits on a broken base.

## Daily Loop

### Morning: anchor the day

Open the vault, open the daily note:

```
nvim ~/vault/0-daily/
<leader>od
```

The daily note is your timeline. Fill in **Plan** with 3 to 5 bullets. Do not over-plan. The daily note is also a capture surface: if something small comes up during the day and does not warrant its own fleeting note, drop it under **Log**.

### Throughout the day: capture fast

Every time a thought shows up that is not tied to the current task, capture it. Two channels:

**In nvim:**

```
<leader>on
<title>
<Enter>
<leader>ot   --> choose "fleeting"
```

Write the thought in one to three sentences. Do not format. Do not link. Do not title well. Speed is the whole point.

**On mobile (Obsidian app):**

- Tap the `+` icon (or the new-note button in the sidebar).
- Confirm the default folder is set to `1-fleeting/`. If not, set it in Settings --> Files and links --> Default location for new notes --> In the folder specified below --> `1-fleeting`.
- Type, save. Syncthing will push it to the hub, and it will appear in your nvim `1-fleeting/` within seconds-to-minutes depending on network.

Mobile captures will not have the `fleeting.md` template applied automatically. That is fine. You will process them later anyway.

### End of day: triage (2 to 5 minutes)

Open the fleeting folder:

```
nvim ~/vault/1-fleeting/
```

For each note, make one of three decisions. **Do not skip. Do not "leave it for tomorrow."**

1. **The thought came from something you read, watched, or listened to.**
   - Create a literature note (see next section).
   - Delete the fleeting note.
2. **The thought is your own, and it is worth keeping.**
   - Create a permanent note (see section after).
   - Delete the fleeting note.
3. **The thought is noise or redundant.**
   - Delete the fleeting note. This is the correct answer more than half the time. No guilt.

Then return to your daily note and fill in **Log**, **Reflections**, **Connections**.

## Writing a Literature Note

A literature note answers: **what did this source say, in my words, that I might want to use later?**

Steps:

1. In neo-tree (the file tree, toggle with `<leader>e` in LazyVim), navigate to `2-literature/`.
2. With `2-literature/` highlighted, press `a` to create a new file. Name it following the [naming conventions](#naming-conventions): `Author YYYY - Short source title.md`.
3. Open the file. Press `<leader>ot` and choose `literature`.
4. Fill in the frontmatter: `source`, `author`, `year`, `url`.
5. Write the body:
   - **Summary**: 3 to 5 sentences. What is this source fundamentally arguing?
   - **Key Arguments**: bullets. The author's main claims, not yours.
   - **Notable Passages**: quotes are allowed here, but each quote must be followed by why it matters to **you**.
   - **My Response**: where you disagree, where you are convinced, what it reminds you of.
   - **Permanent Note Candidates**: bullets. Each bullet is a seed for a separate permanent note you will write later.
   - **Connections**: link to existing notes with `[[...]]`. Explain the link.

Example (filename `Ahrens 2017 - How to Take Smart Notes.md`):

```markdown
## Summary
Ahrens argues that writing is not the output of thinking, it is the medium
of thinking itself. He rebuilds Luhmann's slip-box method around three note
types (fleeting, literature, permanent) and makes the case that linking is
the single highest-leverage habit in knowledge work.

## Key Arguments
- Writing notes is how you find out whether you actually understood something.
- A note is valuable only in proportion to what it connects to.
...
```

Do not try to summarize the whole book in one note. One source = one literature note, but it may seed a dozen permanent notes over time.

## Writing a Permanent Note

A permanent note answers: **what is one thing I believe, and why?**

The title **is** the claim. Not the topic. This is the single habit that separates a live Zettelkasten from a filing cabinet.

- Bad (topic): `Risk management.md`
- Good (claim): `Risk appetite is a board-level choice, not a risk-team calculation.md`

Steps:

1. In neo-tree, navigate to `3-permanent/`.
2. Press `a` to create a new file. Title as a claim, sentence case (see [naming conventions](#naming-conventions)).
3. Press `<leader>ot` and choose `permanent`.
4. Body:
   - One or two paragraphs stating the claim and why you hold it.
   - **Why It Matters**: what decisions or other ideas does this claim affect?
   - **Connections**: link to at least one other note. If you cannot, the note is not ready.
   - **References**: the literature notes or external sources that support it. Use `[[Author YYYY - Title]]` for literature links.

**The one rule**: every permanent note must link to at least one other permanent or literature note. An unlinked note is a dead end. If you cannot find a link, move the note back to `1-fleeting/` until you can.

### What "atomic" means, concretely

If your note contains the word "and" or "also" at the top level, split it. Two examples:

- `Risk registers decay without an owner, and controls need testing cadence.md` --> split into:
  - `Risk registers decay without an assigned owner.md`
  - `Controls require a defined testing cadence to remain effective.md`
- Now each can be linked independently from different contexts.

## Linking

Linking is the habit. Do it every time you write in `3-permanent/`.

- Type `[[`. obsidian.nvim offers a picker with fuzzy search over note names.
- Pick the target. The link is inserted as `[[Note Name]]`.
- After the link, write a short because-clause. The link without reasoning is decoration.

Example:

```markdown
This extends [[Risk appetite is a board-level choice, not a risk-team calculation]]
because tolerance sits one level below appetite and is owned by the executive,
not the board.
```

Four useful lookups while you write:

- `<leader>ob` --> **backlinks**: who links to this note? This is the Zettelkasten's serendipity engine. Check it every time you open a permanent note.
- `<leader>ol` --> **outgoing links**: where does this note point?
- `<leader>os` --> **search vault content**: find a phrase you half-remember.
- `<leader>oo` --> **find note by name**: when you know the title.

## Moving and Renaming Notes Safely

This is the one place you can break the vault. Read carefully.

**Rule**: only rename or move notes through neo-tree (in nvim) or Obsidian's file explorer. Both editors rewrite all `[[wiki-links]]` that point to the file.

**Never** use the terminal (`mv`, `rm`), ranger, nautilus, Finder, or Files (Android). These tools do not know about wiki-links. You will silently orphan every link pointing to the file.

### Rename in neo-tree (nvim)

1. Open neo-tree (`<leader>e`).
2. Navigate to the file.
3. Press `r`. Edit the name. Enter.
4. obsidian.nvim rewrites links across the vault.

### Move in neo-tree (nvim)

1. On the source file, press `m` (move/cut) or `x` depending on LazyVim's neo-tree config. Check with `?` inside neo-tree for the exact keymap in your install.
2. Navigate to the target folder.
3. Press `p` to paste. Links update.

### Promote a fleeting note (the most common move)

Your usual case: a fleeting note graduated into a permanent note.

1. In neo-tree, navigate to the fleeting note.
2. Rename it to a claim-style title (see [naming conventions](#naming-conventions)).
3. Move it to `3-permanent/`.
4. Open it, replace the fleeting template with the permanent template (`<leader>ot` --> `permanent`), copy in your content.
5. Add at least one `[[link]]`.

If it is easier, you can instead: create a fresh note in `3-permanent/`, paste the content, delete the fleeting note. Same outcome. Fleeting notes rarely have backlinks, so you will not lose anything.

## Weekly Review (15 to 30 minutes, Sunday evening or Monday morning)

1. In `0-daily/`, create a new file named `YYYY-MM-DD Weekly Review.md` (the Sunday that closes the week).
2. Press `<leader>ot`, choose `review`.
3. Walk through the template sections. Be honest.
4. Key trigger questions:
   - Any fleeting notes older than 48 hours? Process or delete them now.
   - Any cluster of 5 or more permanent notes on one theme? Start an index note in `7-index/`.
   - Any permanent notes with zero links? Revisit them; find a link or move back to fleeting.
   - What surprised you this week? That surprise is the seed of a permanent note.

## Index Notes (Emergent, Not Planned)

Do not create index notes up front. When you notice 5-10 permanent notes circling the same theme, create an index note in `7-index/`:

1. `<leader>on`, then move it to `7-index/` via neo-tree (or create it directly there with `a` in neo-tree).
2. `<leader>ot` --> `index`.
3. Write it as a **guided tour**, not a list. Explain which note to read first, which extends which, and what question the cluster is collectively answering.

If you find yourself writing "see also" followed by 30 bullets, you are making a table of contents, not an index note. Stop and argue for a path through the notes instead.

## Common Beginner Pitfalls

| Pitfall | Fix |
|---------|-----|
| Titling permanent notes as topics ("Risk management") | Re-title as a claim ("Risk management fails when controls lack owners") |
| Writing permanent notes you never link | Enforce the one-rule: no unlinked permanent notes |
| Hoarding fleeting notes for weeks | Triage daily. Deletion is a valid outcome. |
| Copy-pasting from sources into permanent notes | That is a literature note. Permanent notes must be in your words. |
| Creating folders inside `3-permanent/` to organize | Don't. Links are the structure. Folders are storage. |
| Renaming files with `mv` in a terminal | Use neo-tree or Obsidian. Links will break otherwise. |
| Multi-idea notes ("X and also Y") | Split into atomic notes. One claim per file. |
| Waiting for the "right" title before writing | Write the note, title later. Rename is cheap. |

## Mobile Quirks to Know

- Obsidian mobile does not apply templates by default. Accept that mobile fleeting notes are rawer. You will re-template them if you promote them.
- Syncthing on Android pauses on battery saver. If mobile captures are not showing up on the desktop, check Syncthing-Fork is running and not throttled.
- The Android file picker is hostile. Do not try to rename or move notes from the Files app. Use Obsidian's file explorer only.

## Quick Reference

| What you want | Do this |
|---------------|---------|
| Start session | `nvim ~/vault/0-daily/` then `<leader>od` |
| Quick capture (fleeting) | `<leader>on` |
| Find any note by name | `<leader>oo` |
| Search note contents | `<leader>os` |
| See what links to this note | `<leader>ob` |
| See what this note links to | `<leader>ol` |
| Insert template into current note | `<leader>ot` |
| Paste image from clipboard | `<leader>op` |
| Weekly review | Create `YYYY-MM-DD Weekly Review.md` in `0-daily/`, `<leader>ot` --> `review` |
| Rename file (keeps links intact) | neo-tree --> `r` |
| Toggle file tree | `<leader>e` (LazyVim default) |
| Show leader key | `:map <leader>` |

## The Minimum Viable Habit

If you forget everything above, do just this:

1. Open the daily note every morning.
2. Capture anything that flickers.
3. Empty `1-fleeting/` every evening.
4. Never write a permanent note without one `[[link]]`.

The rest compounds on top of that.
