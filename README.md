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
0-inbox/          Quick captures, fleeting notes (processing queue)
1-daily/          Daily journal notes (permanent chronological log)
2-sources/        Literature notes (books, articles, podcasts, videos)
3-notes/          Permanent Zettelkasten notes (atomic, linked, tagged)
4-drafts/         Long-form compositions from notes (articles, reports)
5-projects/       Active project notes (time-bound)
  _archive/       Completed or paused projects
6-meetings/       Meeting notes
7-maps/           Maps of Content (MOC index notes)
8-templates/      Note templates
9-assets/         Images and attachments
.obsidian/        Obsidian app configuration
```

## Methodology

This vault follows the [Zettelkasten](https://zettelkasten.de/introduction/) method, a system for building a network of interconnected atomic notes that grows in value over time.

### Note Types

| Type | Folder | Purpose | Lifespan |
|------|--------|---------|----------|
| **Fleeting** | `0-inbox/` | Quick captures, half-formed ideas | Temporary; process into permanent notes or discard |
| **Daily** | `1-daily/` | Daily journal, plans, logs, reflections | Permanent chronological record |
| **Literature** | `2-sources/` | Summaries of external sources (books, articles, podcasts, videos) | Permanent, tied to a source |
| **Permanent** | `3-notes/` | Your own refined ideas, one atomic concept per note | Permanent, the core of the Zettelkasten |
| **Draft** | `4-drafts/` | Long-form compositions from notes (articles, reports, docs) | Active until published or abandoned |
| **Project** | `5-projects/` | Time-bound, context-specific work notes | Active during project, then archived |
| **Meeting** | `6-meetings/` | Structured meeting records with actions and decisions | Permanent record |
| **Index (MOC)** | `7-maps/` | Curated entry points linking clusters of related notes | Emergent; created when patterns form |

### Principles

1. **Atomic notes**: each note in `3-notes/` captures one idea, not a topic. "Risk appetite vs risk tolerance" is a note. "Risk management" is a topic dump.
2. **Links over hierarchy**: `[[wiki-links]]` connect ideas across folders. The link graph is the real structure; folders are just storage.
3. **Tags for retrieval, links for connection**: tags (`#risk`, `#controls`) help find notes by filtering. Links (`[[note-name]]`) express relationships between ideas.
4. **MOCs are emergent**: do not pre-plan index notes. Create a MOC in `7-maps/` when 5-10 related notes naturally cluster. A good MOC reads like a guided tour, not a table of contents.
5. **Your own words**: permanent notes must express your thinking, not copy-paste from sources. Literature notes summarize; permanent notes synthesize.

### Processing Workflow

```text
Capture (0-inbox/) --> Refine --> Literature (2-sources/)
                                   Permanent (3-notes/)
                    --> Compose --> Drafts (4-drafts/)
                    --> Connect --> Maps of Content (7-maps/)
                    --> Discard
```

| When | What | Where |
|------|------|-------|
| Anytime | Capture quickly, do not overthink | `0-inbox/` |
| Daily (2-5 min) | Review captures, promote or discard | `0-inbox/` to `3-notes/` or `2-sources/` |
| Weekly (15-30 min) | Write permanent notes, link, update MOCs if clusters emerge | All folders |

### Templates

| Template | Target folder | Trigger |
|----------|--------------|---------|
| `capture.md` | `0-inbox/` | `:Obsidian new` (default landing) |
| `daily.md` | `1-daily/` | `:Obsidian today` |
| `source.md` | `2-sources/` | Insert template after creating note |
| `note.md` | `3-notes/` | Insert template after creating note |
| `draft.md` | `4-drafts/` | Insert template after creating note |
| `project.md` | `5-projects/` | Insert template after creating note |
| `meeting.md` | `6-meetings/` | Insert template after creating note |

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

**Encrypted**: `0-inbox/`, `1-daily/`, `2-sources/`, `3-notes/`, `4-drafts/`, `5-projects/`, `6-meetings/`, `7-maps/`, `9-assets/`

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

**Excluded**: `0-inbox/`, `1-daily/`, `2-sources/`, `3-notes/`, `4-drafts/`, `5-projects/`, `6-meetings/`, `7-maps/`, `9-assets/` (contents only; empty directory structure is preserved via `.gitkeep` files)

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

