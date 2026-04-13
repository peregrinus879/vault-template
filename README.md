# vault

Zettelkasten knowledge vault for [Obsidian](https://obsidian.md) and [Neovim](https://github.com/neovim/neovim) ([obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim)).

## Stack

- **Editor (GUI/mobile)**: Obsidian
- **Editor (terminal)**: Neovim + obsidian.nvim + render-markdown.nvim
- **Sync**: Syncthing over Tailscale (remote hub as always-on relay)
- **Backup**: Git + GitHub (auto-commit via systemd timer)
- **Security**: git-crypt (AES-256 encryption for vault content)
- **Methodology**: Zettelkasten

## Structure

```text
0-daily/          Daily journal notes (ongoing chronological log, vault entry point)
1-fleeting/       Fleeting notes (processing queue)
2-literature/     Literature notes (books, articles, podcasts, videos)
3-permanent/      Permanent notes (atomic, linked, tagged)
4-writing/        Long-form compositions (drafts, published, abandoned)
5-projects/       Active project notes (time-bound)
  _archive/       Completed projects (spatial declutter, not a status)
6-meetings/       Meeting notes
7-index/          Index notes (curated entry points, emergent)
8-templates/      Note templates
9-assets/         Images and attachments
.obsidian/        Obsidian app configuration
```

## Methodology

This vault follows the [Zettelkasten](https://zettelkasten.de/introduction/) method, a system for building a network of interconnected atomic notes that grows in value over time.

### Note Types

| Type | Folder | Purpose | Lifespan |
|------|--------|---------|----------|
| **Daily** | `0-daily/` | Daily journal, plans, logs, reflections, weekly reviews | Ongoing chronological record |
| **Fleeting** | `1-fleeting/` | Quick captures, half-formed ideas | Temporary; process into literature or permanent notes, or discard |
| **Literature** | `2-literature/` | Summaries of external sources (books, articles, podcasts, videos) | Lasting; tied to a source |
| **Permanent** | `3-permanent/` | Your own refined ideas, one atomic idea per note | Permanent, the core of the Zettelkasten |
| **Writing** | `4-writing/` | Long-form compositions from notes (articles, reports, docs) | Active until published or abandoned |
| **Project** | `5-projects/` | Time-bound, context-specific work notes | Active during project, then archived |
| **Meeting** | `6-meetings/` | Structured meeting records with actions and decisions | Planned → held or cancelled |
| **Index** | `7-index/` | Curated entry points linking clusters of related notes | Emergent; created when patterns form |

### Status Lifecycle

Some note types use a `status` frontmatter field to drive processing workflows. Types without a status field (daily, fleeting, literature, permanent, index) exist or are deleted; they have no lifecycle transitions.

| Type | Values | Flow |
|------|--------|------|
| Writing | `draft`, `published`, `abandoned` | draft → published or abandoned |
| Project | `planned`, `in-progress`, `completed`, `paused` | planned → in-progress → completed or paused |
| Meeting | `planned`, `held`, `cancelled` | planned → held or cancelled |

### Principles

1. **Atomic notes**: each note in `3-permanent/` expresses one idea, not a topic. "Risk appetite vs risk tolerance" is a note. "Risk management" is a topic dump.
2. **Links over hierarchy**: `[[wiki-links]]` connect ideas across folders. The link graph is the real structure; folders are just storage. Move or rename notes only via Obsidian or neo-tree (nvim); both update links automatically. Do not use terminal `mv` or OS file managers as links will break.
3. **Tags for retrieval, links for connection**: tags (`#risk`, `#controls`) help find notes by filtering. Links (`[[note-name]]`) express relationships between ideas.
4. **Index notes are emergent**: do not pre-plan index notes. Create an index note in `7-index/` when 5-10 related notes naturally cluster. A good index note reads like a guided tour, not a table of contents.
5. **Your own words**: permanent notes must express your thinking, not copy-paste from sources. Literature notes summarize; permanent notes synthesize.
6. **Numbered directories**: prefixes (0-9) enforce a logical display order across all tools. The sequence reflects the knowledge lifecycle: anchor, capture, process, synthesize, compose, execute, review, navigate.

### Processing Workflow

```text
Capture (1-fleeting/)
    --> Refine  --> Literature (2-literature/)
                --> Permanent (3-permanent/)
    --> Discard

Permanent (3-permanent/)
    --> Compose --> Writing (4-writing/)
    --> Cluster --> Index notes (7-index/)
```

| When | What | Where |
|------|------|-------|
| Anytime | Capture quickly, do not overthink | `1-fleeting/` |
| Daily (2-5 min) | Review fleeting notes, promote or discard | `1-fleeting/` to `2-literature/` or `3-permanent/` |
| Weekly (15-30 min) | Write permanent notes, link, update index notes if clusters emerge | All folders |

### Templates

| Template | Target folder | Trigger |
|----------|--------------|---------|
| `daily.md` | `0-daily/` | `:Obsidian today` |
| `fleeting.md` | `1-fleeting/` | `:Obsidian new` (default landing) |
| `literature.md` | `2-literature/` | Insert template after creating note |
| `permanent.md` | `3-permanent/` | Insert template after creating note |
| `writing.md` | `4-writing/` | Insert template after creating note |
| `project.md` | `5-projects/` | Insert template after creating note |
| `meeting.md` | `6-meetings/` | Insert template after creating note |
| `index.md` | `7-index/` | Insert template after creating note |
| `review.md` | `0-daily/` | Manual (weekly cadence) |

Triggers shown are for [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim). In Obsidian GUI: use the Daily notes core plugin for `daily.md`, and Ctrl/Cmd+P > Insert template for others.

## Sync

Syncthing runs over a Tailscale mesh network. A headless Linux server acts as the always-on hub so devices sync asynchronously through it.

```text
Mobile (Android)
      |
      | Syncthing over Tailscale
      |
Local machines ---- Syncthing over Tailscale ---- Remote hub (headless Linux) ---- GitHub (backup)
```

- **Remote hub**: `syncthing@<user>.service` (system service), always on
- **Local machines**: `syncthing.service` (user service), runs with desktop session
- **Mobile**: Syncthing-Fork, syncs over Tailscale

## Security

Vault content is encrypted with [git-crypt](https://github.com/AGWA/git-crypt) before being pushed to GitHub. Files appear as plaintext locally; GitHub sees ciphertext.

**Encrypted**: `0-daily/`, `1-fleeting/`, `2-literature/`, `3-permanent/`, `4-writing/`, `5-projects/`, `6-meetings/`, `7-index/`, `9-assets/`

**Unencrypted**: `8-templates/`, `.obsidian/`, repo documentation files

Encryption rules are defined in `.gitattributes`. Filenames are not encrypted (git-crypt limitation).

### Key Management

- The symmetric key is generated by `git-crypt init` and stored in `.git/git-crypt/`
- Export with `git-crypt export-key <path>` for backup
- To decrypt a fresh clone: `git-crypt unlock <path-to-key>`
- The key must be stored securely outside the vault and outside GitHub (e.g., password manager)

### Deploy Key

A dedicated SSH key (no passphrase) enables unattended push from the remote hub. It is scoped to this repository only (GitHub deploy key with write access) and cannot access other repos.

## Backup

The remote hub runs a systemd timer (`vault-autocommit.timer`) that commits and pushes changes hourly.

```text
vault-autocommit.timer (hourly, on the hour)
  └── vault-autocommit.service
        └── git add -A && git commit && git push
              └── post-commit hook
                    └── rsync to public repo && git commit && git push
```

- Commits only when changes exist (no empty commits)
- Push failures are non-fatal; local commits still succeed
- Push retries automatically on the next hourly run
- Syncthing provides real-time sync between devices; git provides version history and off-site backup

## Public Template

A public template repo ([vault-template](https://github.com/peregrinus879/vault-template)) mirrors the vault's structure, templates, config, and documentation. It contains no note content.

A git post-commit hook syncs public-facing files via rsync after every commit (including auto-commits). Content directories are excluded; only templates, `.obsidian/` config, and documentation are copied. The public repo has its own deploy key for unattended push.

**Synced**: `8-templates/`, `.obsidian/` config, `README.md`, `SETUP.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`

**Excluded**: `0-daily/`, `1-fleeting/`, `2-literature/`, `3-permanent/`, `4-writing/`, `5-projects/`, `6-meetings/`, `7-index/`, `9-assets/` (contents only; empty directory structure is preserved via `.gitkeep` files)

Content directories are derived from `.gitattributes` automatically. Adding a new content directory only requires updating `.gitattributes`.

## Setup

See [SETUP.md](SETUP.md) for the full step-by-step guide covering:

1. **Remote hub** (headless Linux): Syncthing, git-crypt, deploy key, auto-commit timer, public template sync
2. **Local machines** (Linux): Syncthing, Neovim config, Obsidian desktop
3. **Local machines** (Windows / WSL): native Syncthing, Obsidian, WSL symlink
4. **Mobile** (Android): Tailscale, Syncthing-Fork, Obsidian
5. **Recovery**: fresh clone with git-crypt unlock

## References

- `README.md` - structure, methodology, and overview
- `SETUP.md` - full setup guide with commands and app links
- `AGENTS.md` - canonical assistant context
- `CLAUDE.md` - thin Claude Code wrapper importing `AGENTS.md`
- [vault-template](https://github.com/peregrinus879/vault-template) - public template repo
- [Zettelkasten introduction](https://zettelkasten.de/introduction/)
- [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim)
- [git-crypt](https://github.com/AGWA/git-crypt)
- [Syncthing](https://syncthing.net/)

