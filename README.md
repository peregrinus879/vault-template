# vault

Knowledge vault using the Zettelkasten method, managed with [Neovim](https://github.com/neovim/neovim) ([obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim)) and [Obsidian](https://obsidian.md).

## Stack

- **Editor (terminal)**: Neovim + obsidian.nvim + render-markdown.nvim
- **Editor (GUI/mobile)**: Obsidian
- **Sync**: Syncthing over Tailscale (remote hub as always-on relay)
- **Backup**: Git + GitHub (auto-commit via systemd timer)
- **Security**: git-crypt (AES-256 encryption for vault content)
- **Methodology**: Zettelkasten

## Structure

```text
journal/          Daily notes and quick captures
projects/         Active project notes (time-bound)
  _archive/       Completed or paused projects
notes/            Permanent Zettelkasten notes (atomic, linked, tagged)
references/       Literature notes (books, articles, podcasts, videos)
meetings/         Meeting notes
maps/             Maps of Content (MOC index notes)
templates/        Note templates
assets/           Images and attachments
.obsidian/        Obsidian app configuration
```

## Methodology

This vault follows the [Zettelkasten](https://zettelkasten.de/introduction/) method, a system for building a network of interconnected atomic notes that grows in value over time.

### Note Types

| Type | Folder | Purpose | Lifespan |
|------|--------|---------|----------|
| **Fleeting** | `journal/` | Quick captures, daily logs, half-formed ideas | Temporary; process into permanent notes or discard |
| **Literature** | `references/` | Summaries of external sources (books, articles, podcasts, videos) | Permanent, tied to a source |
| **Permanent** | `notes/` | Your own refined ideas, one atomic concept per note | Permanent, the core of the Zettelkasten |
| **Project** | `projects/` | Time-bound, context-specific work notes | Active during project, then archived |
| **Meeting** | `meetings/` | Structured meeting records with actions and decisions | Permanent record |
| **Index (MOC)** | `maps/` | Curated entry points linking clusters of related notes | Emergent; created when patterns form |

### Principles

1. **Atomic notes**: each note in `notes/` captures one idea, not a topic. "Risk appetite vs risk tolerance" is a note. "Risk management" is a topic dump.
2. **Links over hierarchy**: `[[wiki-links]]` connect ideas across folders. The link graph is the real structure; folders are just storage.
3. **Tags for retrieval, links for connection**: tags (`#risk`, `#controls`) help find notes by filtering. Links (`[[note-name]]`) express relationships between ideas.
4. **MOCs are emergent**: do not pre-plan index notes. Create a MOC in `maps/` when 5-10 related notes naturally cluster. A good MOC reads like a guided tour, not a table of contents.
5. **Your own words**: permanent notes must express your thinking, not copy-paste from sources. Literature notes summarize; permanent notes synthesize.

### Processing Workflow

```text
Capture (journal/) --> Refine --> Permanent (notes/)
                                  Literature (references/)
                   --> Connect --> Maps of Content (maps/)
                   --> Discard
```

| When | What | Where |
|------|------|-------|
| Anytime | Capture quickly, do not overthink | `journal/` |
| Daily (2-5 min) | Review captures, promote or discard | `journal/` to `notes/` or `references/` |
| Weekly (15-30 min) | Write permanent notes, link, update MOCs if clusters emerge | All folders |

### Templates

| Template | Target folder | Trigger |
|----------|--------------|---------|
| `daily.md` | `journal/` | `:Obsidian today` |
| `capture.md` | `journal/` | `:Obsidian new` (default landing) |
| `note.md` | `notes/` | Insert template after creating note |
| `project.md` | `projects/` | Insert template after creating note |
| `meeting.md` | `meetings/` | Insert template after creating note |
| `reference.md` | `references/` | Insert template after creating note |

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

**Encrypted**: `journal/`, `notes/`, `projects/`, `references/`, `meetings/`, `maps/`, `assets/`

**Unencrypted**: `templates/`, `.obsidian/`, repo documentation files

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

A public template repo ([obsidian-vault](https://github.com/peregrinus879/obsidian-vault)) mirrors the vault's structure, templates, config, and documentation. It contains no note content.

A git post-commit hook syncs public-facing files via rsync after every commit (including auto-commits). Content directories are excluded; only templates, `.obsidian/` config, and documentation are copied. The public repo has its own deploy key for unattended push.

**Synced**: `templates/`, `.obsidian/` config, `README.md`, `SETUP.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`

**Excluded**: `journal/`, `notes/`, `projects/`, `references/`, `meetings/`, `maps/`, `assets/` (contents only; empty directory structure is preserved via `.gitkeep` files)

If a new content directory is added to the vault, a matching `--exclude` rule must be added to the hook (`.git/hooks/post-commit`).

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
- [obsidian-vault](https://github.com/peregrinus879/obsidian-vault) - public template repo
- [Zettelkasten introduction](https://zettelkasten.de/introduction/)
- [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim)
- [git-crypt](https://github.com/AGWA/git-crypt)
- [Syncthing](https://syncthing.net/)

