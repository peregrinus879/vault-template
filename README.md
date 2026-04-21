# vault: Zettelkasten template for Obsidian and Neovim

Opinionated structure, templates for every note type, multi-device sync, and optional encrypted backup. Works with [Obsidian](https://obsidian.md) (desktop/mobile) and [obsidian.nvim](https://github.com/obsidian-nvim/obsidian.nvim) (terminal).

## Choose your path

| Path | What you get | Time |
|---|---|---|
| **Local** ([SETUP-LOCAL.md](SETUP-LOCAL.md)) | Full Zettelkasten template on one machine: Obsidian plus optional Neovim overlay and local git version history. | 5 to 15 min |
| **Hub** ([SETUP-HUB.md](SETUP-HUB.md)) | Adds real-time multi-device sync (Linux, Windows, Android), encrypted GitHub backup, and automated public template mirroring. Builds on the Local path. | +30 min |

## Highlights

**Opinionated Zettelkasten structure.** Seven numbered directories enforce a knowledge lifecycle: capture, process, synthesize, navigate, compose. Each content directory has a dedicated template with pre-filled frontmatter. The numbered prefix keeps folders sorted in every file explorer and picker, across every platform. See [DESIGN.md](DESIGN.md) §1 for the rationale behind the numbering order.

**Templates for every note type.** Five templates cover the full Zettelkasten workflow: fleeting, literature, permanent, overview, and writing. All share the same three-field frontmatter (`id`, `aliases`, `tags`), matching obsidian.nvim's default schema. Literature notes carry bibliographic metadata in the body, not in frontmatter. Notes land in the correct folder automatically when created via obsidian.nvim's `<leader>oN`.

**Dual-editor support.** The same markdown files work in both Obsidian (desktop, mobile) and Neovim (terminal, via obsidian.nvim). No import step, no format conversion, no sync delay beyond Syncthing. The `nvim-vault/` stow overlay ships a complete obsidian.nvim configuration as a LazyVim plugin spec, including slug-based filenames, template routing, and two vault-specific keybindings: `<leader>o<space>` to slug-rename and normalize a note, and `<leader>op` to promote a note to a different type (folder move + template swap, preserving body content under `## Capture`). Routine normalization runs automatically via the pre-commit hook on every commit. See [DESIGN.md](DESIGN.md) §12 for overlay deviations from obsidian.nvim defaults.

**Slug filenames with readable aliases.** Note filenames are auto-generated lowercase-hyphenated slugs (e.g., `risk-appetite-is-a-board-level-choice.md`). The human-readable title lives in the `aliases` frontmatter field, which powers search and `[[link]]` autocomplete in both editors. Slugs avoid all cross-platform filename issues when Syncthing moves files across Linux, Windows, and Android.

**Note normalization.** A shared Python normalizer (`.githooks/lib/normalize.py`) holds the single source of truth for the three canonical frontmatter fields, body H1 insertion, and template body application. It runs in three contexts:

- `.githooks/pre-commit` runs `--apply` on every staged note in a content directory. Notes created outside templates (mobile captures, Obsidian Ctrl+N without a template, copy-paste, Neovim `:e`/`:w`) get the folder-matched template body, correct frontmatter, and an H1 automatically on commit. Pre-existing body content is wrapped in a `## Capture` section for later integration.
- `<leader>o<space>` in obsidian.nvim runs the same `--apply` plus a slug rename (via `:Obsidian rename`, which rewrites backlinks vault-wide), passing the pre-rename stem as the alias fallback.
- `<leader>op` in obsidian.nvim moves the note to a different content folder and runs `--reapply`, which force-installs the target template's body sections while preserving any `## Capture` block (or wrapping existing body content in a new one). Used for promoting fleeting captures into permanent notes or reclassifying between types.

The apply rule branches three ways on the note's state: no frontmatter → prepend full template + wrap pre-existing content in `## Capture`; frontmatter present + body has no `## ` heading → insert template body sections only (note's H1 preserved); frontmatter + at least one `## ` heading → fill only (frontmatter + H1 sync; body untouched). Key rules: `id` always tracks the filename stem; `aliases[0]` is synced with the body H1 bidirectionally (H1 wins when both exist and differ); user-added `aliases[1..]` are preserved verbatim. Running the normalizer twice produces no further changes (idempotent). `--check` flags issues including unsubstituted `{{...}}` placeholders. See [DESIGN.md](DESIGN.md) §9 and §11.

**Multi-device sync.** Syncthing over Tailscale provides real-time file sync across Linux desktops, Windows (native + WSL), and Android. A headless Linux server acts as the always-on hub so devices sync asynchronously. No cloud dependency; all traffic stays on the private Tailscale mesh. See [DESIGN.md](DESIGN.md) §10 for why Syncthing handles sync rather than the Obsidian Git plugin or Obsidian Sync.

**Dual-layer encryption (optional, self-hosting).** Two encryption layers protect note content before it reaches GitHub: **git-crypt** encrypts file contents in git objects (AES-256), and **git-remote-gcrypt** encrypts the entire remote, including filenames, directory structure, and commit history. Together, GitHub sees only opaque encrypted data. Neither layer alone provides full coverage.

**Automated backup and public template mirroring (optional, self-hosting).** A systemd timer commits and pushes changes hourly. A post-commit hook mirrors the vault's structure, templates, config, and documentation to a public template repo via rsync. Content directories are excluded; the public mirror shows the layout without any private notes. The sync uses a fail-closed allowlist at the root level: new root files and directories do not publish unless explicitly added. Files inside already-allowlisted subtrees (e.g., `5-templates/`, `nvim-vault/`) publish automatically. A sentinel file guards against accidental sync to the wrong repo. See [DESIGN.md](DESIGN.md) §10.

## Quick start

```bash
git clone https://github.com/peregrinus879/vault-template.git ~/vault
cd ~/vault && rm -rf .git
```

Open Obsidian, choose **Open folder as vault**, select `~/vault`. Press `Ctrl+N`. Write a thought. See [SETUP-LOCAL.md](SETUP-LOCAL.md) for the full local setup (version history, Neovim). For multi-device sync and encrypted backup, see [SETUP-HUB.md](SETUP-HUB.md).

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
infra/            Hub-only infrastructure files (pinentry, systemd units)
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
| [SETUP-LOCAL.md](SETUP-LOCAL.md) | Clone, Obsidian install, version history, optional Neovim overlay |
| [SETUP-HUB.md](SETUP-HUB.md) | Self-hosted hub: Syncthing, device pairing, encryption, automated backup, public template mirroring |
| [WORKFLOW.md](WORKFLOW.md) | Zettelkasten method, naming conventions, capture loop, keybindings |
| [DESIGN.md](DESIGN.md) | Opinionated choices and the reasoning behind each |
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
