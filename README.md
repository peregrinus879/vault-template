# vault: Zettelkasten template for Obsidian and Neovim

Opinionated structure, templates for every note type, multi-device sync, and optional encrypted backup. Works with [Obsidian](https://obsidian.md) (desktop/mobile) and [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim) (terminal).

## What you get

- **5 note templates** covering the full Zettelkasten lifecycle: fleeting, literature, permanent, overview, and writing
- **Dual-editor support**: same files in Obsidian (desktop/mobile) and Neovim (terminal via obsidian.nvim); no import, no format conversion
- **Neovim overlay** (`nvim-vault/`): a LazyVim-compatible stow package with obsidian.nvim config, template routing, slug filenames, and vault-specific normalize/slugify commands
- **Slug filenames with readable aliases**: auto-generated cross-platform-safe filenames; human-readable titles preserved in `aliases` for search and `[[link]]` autocomplete
- **Note normalization**: pre-commit hook applies the folder-matched template, fills canonical frontmatter, and ensures a body H1 synced with `aliases[0]` — for notes created outside templates (mobile captures, Ctrl+N without template, copy-paste)
- **Multi-device sync**: Syncthing over Tailscale across Linux, Windows, and Android
- **Dual-layer encryption** (optional): git-crypt (content) + git-remote-gcrypt (filenames, history); GitHub sees only opaque data
- **Automated backup** (optional): systemd timer commits hourly; post-commit hook mirrors structure and templates to a public repo

## Quick start

```bash
git clone https://github.com/peregrinus879/vault-template.git ~/vault
cd ~/vault && rm -rf .git
```

Open Obsidian, choose **Open folder as vault**, select `~/vault`. Press `Ctrl+N`. Write a thought. See [GETTING-STARTED.md](GETTING-STARTED.md) for the full setup, including version history, Neovim, and multi-device sync.

## Structure

```text
0-fleeting/       Capture and triage (process or discard within 48h)
1-literature/     Source records with brief pointers to key ideas
2-permanent/      Atomic evergreen notes (the core of the slip-box)
3-overview/       Curated narrative tours through topics
4-writing/        Long-form output from the slip-box
5-templates/      Note templates (one per note type)
6-assets/         Images, PDFs, and attachments
nvim-vault/       Neovim overlay (LazyVim stow package)
self-hosting/     Reference files for encryption and backup setup
.obsidian/        Obsidian app configuration
.githooks/        Git hooks (note normalizer, public template sync)
```

## Note types

| Type | Folder | Purpose | Lifespan |
|------|--------|---------|----------|
| **Fleeting** | `0-fleeting/` | Quick captures, half-formed ideas | Temporary; promote or discard within 48h |
| **Literature** | `1-literature/` | Source record with brief pointers to key ideas | Lasting; one per source, a processing bridge to permanent notes |
| **Permanent** | `2-permanent/` | Atomic evergreen claims, one per note, in your own words | Permanent; the core of the slip-box |
| **Overview** | `3-overview/` | Curated narrative tour through a topic | Emergent; created when 5+ notes cluster |
| **Writing** | `4-writing/` | Long-form output assembled from permanent notes | Active until published or abandoned |

### Frontmatter

All templates share the same three-field frontmatter (`id`, `aliases`, `tags`), matching obsidian.nvim's default schema. Literature notes carry bibliographic metadata (medium, author, year, identifier) in the body under `## Source`.

## Documentation

| Doc | What it covers |
|-----|---------------|
| [GETTING-STARTED.md](GETTING-STARTED.md) | Clone, open in Obsidian, version history, add Neovim, multi-device sync |
| [WORKFLOW.md](WORKFLOW.md) | Zettelkasten method, naming conventions, capture loop, keybindings |
| [DESIGN.md](DESIGN.md) | Opinionated choices and the reasoning behind each |
| [FEATURES.md](FEATURES.md) | Detailed feature showcase |
| [SELF-HOSTING.md](SELF-HOSTING.md) | Encryption, automated backup, public template mirroring |
| [AGENTS.md](AGENTS.md) | AI assistant context for working with this repo |
| [CLAUDE.md](CLAUDE.md) | Claude Code wrapper for AGENTS.md |

## Stack

- **Editor (GUI/mobile)**: [Obsidian](https://obsidian.md)
- **Editor (terminal)**: [Neovim](https://neovim.io/) + [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim) + [render-markdown.nvim](https://github.com/MeanderingProgrammer/render-markdown.nvim) (recommended)
- **Sync**: [Syncthing](https://syncthing.net/) over [Tailscale](https://tailscale.com/)
- **Backup**: Git + GitHub (auto-commit via systemd timer)
- **Security**: [git-crypt](https://github.com/AGWA/git-crypt) + [git-remote-gcrypt](https://github.com/spwhitton/git-remote-gcrypt)
- **Methodology**: [Zettelkasten](https://zettelkasten.de/introduction/)

## References

- [Zettelkasten introduction](https://zettelkasten.de/introduction/)
- [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim)
- [git-crypt](https://github.com/AGWA/git-crypt)
- [git-remote-gcrypt](https://github.com/spwhitton/git-remote-gcrypt)
- [Syncthing](https://syncthing.net/)
