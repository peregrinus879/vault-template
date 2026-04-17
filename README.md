# vault

A Zettelkasten vault template for [Obsidian](https://obsidian.md) and [Neovim](https://github.com/obsidian-nvim/obsidian.nvim). Opinionated structure, templates for every note type, multi-device sync, and optional encrypted backup.

## What you get

- **7 note templates** covering the full Zettelkasten lifecycle: fleeting, source, literature, permanent, writing (short/long), and index
- **Dual-editor support**: same files in Obsidian (desktop/mobile) and Neovim (terminal via obsidian.nvim); no import, no format conversion
- **Neovim overlay** (`nvim-vault/`): a LazyVim-compatible stow package with obsidian.nvim config, template routing, slug filenames, and a custom rename command
- **Slug filenames with readable aliases**: auto-generated cross-platform-safe filenames; human-readable titles preserved in `aliases` for search and `[[link]]` autocomplete
- **Frontmatter normalization**: pre-commit hook fills missing metadata on notes created outside templates (mobile captures, copy-paste)
- **Multi-device sync**: Syncthing over Tailscale across Linux, Windows, and Android
- **Dual-layer encryption** (optional): git-crypt (content) + git-remote-gcrypt (filenames, history); GitHub sees only opaque data
- **Automated backup** (optional): systemd timer commits hourly; post-commit hook mirrors structure and templates to a public repo

## Quick start

```bash
git clone https://github.com/peregrinus879/vault-template.git ~/vault
```

Open `~/vault` in Obsidian as a vault. Press `Ctrl+N`. Write a thought. See [GETTING-STARTED.md](GETTING-STARTED.md) for the full setup, including Neovim and multi-device sync.

## Structure

```text
0-fleeting/       Fleeting notes (capture, processing queue)
1-sources/        Source notes (bibliographic records, one per work cited)
2-literature/     Literature notes (paraphrase tied to a source)
3-permanent/      Permanent notes (atomic, your words, linked)
4-writing/        Long-form compositions (drafts, published, abandoned)
5-index/          Index notes (curated entry points, emergent)
6-templates/      Note templates (7 templates, one per note type)
7-assets/         Images and attachments
nvim-vault/       Neovim overlay (LazyVim stow package)
self-hosting/     Reference files for encryption and backup setup
.obsidian/        Obsidian app configuration
.githooks/        Git hooks (frontmatter normalizer, public template sync)
```

## Note types

| Type | Folder | Purpose | Lifespan |
|------|--------|---------|----------|
| **Fleeting** | `0-fleeting/` | Quick captures, half-formed ideas | Temporary; promote or discard within 48h |
| **Source** | `1-sources/` | Bibliographic record of a cited work | Lasting; one per source |
| **Literature** | `2-literature/` | Paraphrased content tied to a source | Lasting; may seed many permanent notes |
| **Permanent** | `3-permanent/` | Your own refined ideas, one atomic claim per note | Permanent; the core of the Zettelkasten |
| **Writing** | `4-writing/` | Long-form compositions (posts, articles, essays) | Active until published or abandoned |
| **Index** | `5-index/` | Curated entry points linking clusters of related notes | Emergent; created when patterns form |

### Status lifecycle

Writing notes carry a `status` field: `draft`, `published`, or `abandoned`.

Source notes carry an informational `status` field: `unread`, `reading`, `read`, `abandoned`, `reference`. This is progress tracking, not a state machine.

## Documentation

| Doc | What it covers |
|-----|---------------|
| [GETTING-STARTED.md](GETTING-STARTED.md) | Clone, open in Obsidian, add Neovim, add multi-device sync |
| [WORKFLOW.md](WORKFLOW.md) | Zettelkasten method, naming conventions, capture loop, keybindings |
| [FEATURES.md](FEATURES.md) | Detailed feature showcase |
| [SELF-HOSTING.md](SELF-HOSTING.md) | Encryption, automated backup, public template mirroring |

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
