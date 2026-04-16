# vault

Zettelkasten knowledge vault for [Obsidian](https://obsidian.md) and [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim): Syncthing sync, dual-layer encryption (git-crypt + git-remote-gcrypt), and systemd auto-commit.

## Stack

- **Editor (GUI/mobile)**: Obsidian
- **Editor (terminal)**: Neovim + obsidian.nvim + render-markdown.nvim
- **Sync**: Syncthing over Tailscale (remote hub as always-on relay)
- **Backup**: Git + GitHub (auto-commit via systemd timer)
- **Security**: git-crypt (AES-256 content encryption) + git-remote-gcrypt (full remote encryption)
- **Methodology**: Zettelkasten

## Structure

```text
0-fleeting/       Fleeting notes (capture, processing queue)
1-sources/        Source notes (bibliographic records, one per work cited)
2-literature/     Literature notes (paraphrase tied to a source)
3-permanent/      Permanent notes (atomic, your words, linked)
4-writing/        Long-form compositions (drafts, published, abandoned)
5-index/          Index notes (curated entry points, emergent)
6-templates/      Note templates (only unencrypted content directory)
7-assets/         Images and attachments
.obsidian/        Obsidian app configuration
hooks/            Git hooks tracked in repo (enabled via core.hooksPath on the hub)
```

## Methodology

This vault follows the [Zettelkasten](https://zettelkasten.de/introduction/) method, a system for building a network of interconnected atomic notes that grows in value over time.

### Note Types

| Type | Folder | Purpose | Lifespan |
|------|--------|---------|----------|
| **Fleeting** | `0-fleeting/` | Quick captures, half-formed ideas | Temporary; promote to literature or permanent, or discard |
| **Source** | `1-sources/` | Bibliographic record of a cited work | Lasting; one per source, referenced by literature notes |
| **Literature** | `2-literature/` | Paraphrased content tied to a source | Lasting; may seed many permanent notes over time |
| **Permanent** | `3-permanent/` | Your own refined ideas, one atomic claim per note | Permanent; the core of the Zettelkasten |
| **Writing** | `4-writing/` | Long-form compositions (posts, articles, essays) | Active until published or abandoned |
| **Index** | `5-index/` | Curated entry points linking clusters of related notes | Emergent; created when patterns form |

### Status Lifecycle

Writing notes carry a `status` field: `draft`, `published`, or `abandoned`. All other types exist or are deleted; they have no lifecycle transitions.

Source notes carry an informational `status` field: `unread`, `reading`, `read`, `abandoned`, `reference`. This is progress tracking, not a state machine.

### Principles

1. **Atomic notes**: each note in `3-permanent/` expresses one idea, not a topic. "Risk appetite vs risk tolerance" is a note. "Risk management" is a topic dump.
2. **Sources are separate from literature**: the bibliographic record lives in `1-sources/` (one note per work). Literature notes in `2-literature/` paraphrase specific content from a source and reference it via `source: "[[slug]]"`. One source can feed many literature notes.
3. **Links over hierarchy**: `[[wiki-links]]` connect ideas across folders. The link graph is the real structure; folders are just storage. Move or rename notes only via Obsidian or neo-tree (nvim); both update links automatically. Do not use terminal `mv` or OS file managers, as links will break.
4. **Tags for retrieval, links for connection**: tags (`#risk`, `#controls`) help find notes by filtering. Links (`[[note-name]]`) express relationships between ideas.
5. **Index notes are emergent**: do not pre-plan index notes. Create one in `5-index/` when 5-10 related notes naturally cluster. A good index note reads like a guided tour, not a table of contents.
6. **Your own words**: permanent notes must express your thinking, not copy-paste from sources. Literature notes quote and paraphrase selectively; permanent notes synthesize.
7. **Numbered directories**: prefixes (0-7) enforce a logical display order. The sequence reflects the knowledge lifecycle: capture, cite, paraphrase, synthesize, compose, navigate; templates and assets follow as infrastructure.

### Processing Workflow

```text
Capture (0-fleeting/)
    --> Refine --> Source (1-sources/) + Literature (2-literature/)
               --> Permanent (3-permanent/)
    --> Discard

Permanent (3-permanent/)
    --> Compose --> Writing (4-writing/)
    --> Cluster --> Index notes (5-index/)
```

| When | What | Where |
|------|------|-------|
| Anytime | Capture quickly, do not overthink | `0-fleeting/` |
| Daily (2-5 min) | Review fleeting notes, promote or discard | `0-fleeting/` to `1-sources/` + `2-literature/` or `3-permanent/` |
| As needed | Create a source note when you start engaging with a new work | `1-sources/` |
| As themes emerge | Write permanent notes, link, update index notes if clusters form | All folders |

For a step-by-step walkthrough of this workflow, naming conventions, and keybindings, see [WORKFLOW.md](WORKFLOW.md).

### Templates

| Template | Target folder | Trigger |
|----------|--------------|---------|
| `fleeting.md` | `0-fleeting/` | `<leader>on` (`:Obsidian new`) |
| `source.md` | `1-sources/` | `<leader>oN` (`:Obsidian new_from_template`) |
| `literature.md` | `2-literature/` | `<leader>oN` |
| `permanent.md` | `3-permanent/` | `<leader>oN` |
| `writing-short.md` | `4-writing/` | `<leader>oN` (≤280 chars) |
| `writing-medium.md` | `4-writing/` | `<leader>oN` (~500 words) |
| `writing-long.md` | `4-writing/` | `<leader>oN` (500+ words) |
| `index.md` | `5-index/` | `<leader>oN` |

Triggers shown are for [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim). `<leader>oN` picks a template from a list and routes the note to the correct folder. In Obsidian GUI: Ctrl/Cmd+P > Insert template.

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

Vault content is protected by two encryption layers before reaching GitHub:

1. **git-crypt** (content encryption): encrypts file contents in git objects using AES-256. Files appear as plaintext locally; git stores ciphertext. Defined by `.gitattributes` filter rules.
2. **git-remote-gcrypt** (remote encryption): encrypts the entire repository on the remote, including filenames, directory structure, and commit history. GitHub sees only opaque encrypted data.

**Why two layers**: git-crypt alone leaves filenames visible on GitHub. git-remote-gcrypt hides everything on the remote but does not encrypt local git objects. Together, they provide defense-in-depth.

**Encrypted (git-crypt)**: `0-fleeting/`, `1-sources/`, `2-literature/`, `3-permanent/`, `4-writing/`, `5-index/`, `7-assets/`

**Unencrypted (git-crypt)**: `6-templates/`, `.obsidian/`, `hooks/`, repo documentation files

**GitHub visibility**: none. The entire remote is opaque (encrypted filenames, content, and history).

Encryption rules for git-crypt are defined in `.gitattributes`. Each content directory has a `filter=git-crypt diff=git-crypt` rule. Adding a new content directory requires adding it to `.gitattributes`. The post-commit hook derives content directories from these same rules for public template sync.

### Key Management

Two keys are required. Both must be stored securely outside the vault and outside GitHub (e.g., password manager). Losing either key means losing the ability to restore from GitHub.

| Key | Purpose | Generated by | Backup method |
|-----|---------|-------------|---------------|
| git-crypt symmetric key | Decrypt file contents after clone | `git-crypt init` | `git-crypt export-key <path>` |
| GPG key (`vault-backup`) | Decrypt the encrypted remote | `gpg --gen-key` | Export private key, public key, revocation cert |

Also record:
- GPG fingerprint: for quick identification without importing
- gcrypt remote ID: shown during first push, needed for recovery verification

### Deploy Key

A dedicated SSH key (no passphrase) enables unattended push from the remote hub. It is scoped to this repository only (GitHub deploy key with write access) and cannot access other repos.

## Backup

The remote hub runs a systemd timer (`vault-autocommit.timer`) that commits and pushes changes hourly.

```text
vault-autocommit.timer (hourly, on the hour)
  └── vault-autocommit.service
        └── git add -A && git commit && git push
              └── post-commit hook (hooks/post-commit, enabled via core.hooksPath)
                    └── rsync to public repo && git commit && git push
```

- Commits only when changes exist (no empty commits)
- Push failures are non-fatal; local commits still succeed
- Push retries automatically on the next hourly run
- Syncthing provides real-time sync between devices; git provides version history and off-site backup

## Public Template

A public template repo ([vault-template](https://github.com/peregrinus879/vault-template)) mirrors the vault's structure, templates, config, and documentation. It contains no note content.

A git post-commit hook (tracked at `hooks/post-commit`) syncs public-facing files via rsync after every commit (including auto-commits). Content directories are excluded; only templates, `.obsidian/` config, `hooks/`, and documentation are copied. The public repo has its own deploy key for unattended push.

**Synced**: `6-templates/`, `.obsidian/` config, `hooks/`, `README.md`, `WORKFLOW.md`, `SETUP.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`

**Excluded**: `0-fleeting/`, `1-sources/`, `2-literature/`, `3-permanent/`, `4-writing/`, `5-index/`, `7-assets/` (contents only; empty directory structure is preserved via `.gitkeep` files)

Content directories are derived from `.gitattributes` automatically. Adding a new content directory only requires updating `.gitattributes`.

## Setup

See [SETUP.md](SETUP.md) for the full step-by-step guide covering:

1. **Remote hub** (headless Linux): baseline tools, Syncthing, git-crypt, git-remote-gcrypt, GPG key, deploy key, auto-commit timer, public template sync
2. **Local machines** (Linux): Syncthing, Neovim config, Obsidian desktop
3. **Local machines** (Windows / WSL): native Syncthing, Obsidian, WSL symlink
4. **Mobile** (Android): Tailscale, Syncthing-Fork, Obsidian
5. **Recovery**: fresh clone with gcrypt + git-crypt unlock

## References

- `README.md` - structure, methodology, and overview
- `WORKFLOW.md` - vault workflow tutorial and naming conventions
- `SETUP.md` - full setup guide with commands and app links
- `AGENTS.md` - canonical assistant context
- `CLAUDE.md` - thin Claude Code wrapper importing `AGENTS.md`
- [vault-template](https://github.com/peregrinus879/vault-template) - public template repo
- [Zettelkasten introduction](https://zettelkasten.de/introduction/)
- [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim)
- [git-crypt](https://github.com/AGWA/git-crypt)
- [git-remote-gcrypt](https://github.com/spwhitton/git-remote-gcrypt)
- [Syncthing](https://syncthing.net/)
