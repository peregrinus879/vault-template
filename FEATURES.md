# Features

What this vault template provides out of the box and why each piece matters.

## Opinionated Zettelkasten structure

Seven numbered directories enforce a knowledge lifecycle: capture, process, synthesize, navigate, compose. Each content directory has a dedicated template with pre-filled frontmatter. The numbered prefix keeps folders sorted in every file explorer and picker, across every platform. See [DESIGN.md](DESIGN.md) §1 for the rationale behind the numbering order.

## Templates for every note type

Five templates cover the full Zettelkasten workflow: fleeting, literature, permanent, overview, and writing. All share the same universal frontmatter (`id`, `aliases`, `type`, `created`, `updated`, `tags`). Literature notes carry bibliographic metadata in the body, not in frontmatter. Notes land in the correct folder automatically when created via obsidian.nvim's `<leader>oN`.

## Dual-editor support

The same markdown files work in both Obsidian (desktop, mobile) and Neovim (terminal, via obsidian.nvim). No import step, no format conversion, no sync delay beyond Syncthing. The `nvim-vault/` stow overlay ships a complete obsidian.nvim configuration as a LazyVim plugin spec, including slug-based filenames, template routing, and three vault-specific orchestrators: `<leader>oi` (apply canonical template), `<leader>of` (fill frontmatter), and `<leader>oS` (slugify and re-sync). See [DESIGN.md](DESIGN.md) §12 for the list of opt-level deviations from obsidian.nvim defaults.

## Slug filenames with readable aliases

Note filenames are auto-generated lowercase-hyphenated slugs (e.g., `risk-appetite-is-a-board-level-choice.md`). The human-readable title lives in the `aliases` frontmatter field, which powers search and `[[link]]` autocomplete in both editors. Slugs avoid all cross-platform filename issues (Syncthing moves files across Linux, Windows, and Android).

## Note normalization

A shared Python normalizer (`.githooks/lib/normalize.py`) holds the single source of truth for the six canonical frontmatter fields (`id`, `aliases`, `type`, `created`, `updated`, `tags`), body H1 insertion, and template body application. It runs in four contexts:

- **`.githooks/pre-commit`** runs `--apply` on every staged note in a content directory. Notes created outside templates (mobile captures, file manager, copy-paste) get the folder-matched template body, correct frontmatter, and an H1 automatically on commit. Pre-existing body content is wrapped in a `## Capture` section for later integration.
- **`<leader>oi`** in obsidian.nvim runs `--apply` on the current buffer — same comprehensive behavior, on demand.
- **`<leader>of`** runs `--fill` on the current buffer: frontmatter + H1 only, without ever inserting template sections. Use when a note has custom body structure you want to preserve.
- **`<leader>oS`** slugifies the filename (via `:Obsidian rename`, which rewrites backlinks vault-wide), then runs `--apply` with the pre-rename stem as the alias fallback.

Key rules: `id` always tracks the filename stem; `type` is derived from the folder name; `aliases[0]` is synced with the body H1 bidirectionally (H1 wins when both exist and differ); user-added `aliases[1..]` (synonyms, short forms, historical names) are preserved verbatim. If a body has no `# H1` at its first non-blank line, `# {aliases[0]}` is inserted after the frontmatter. Running the normalizer twice produces no further changes (idempotent). See [DESIGN.md](DESIGN.md) §9 for the schema and §11 for the full identity model.

## Multi-device sync

Syncthing over Tailscale provides real-time file sync across Linux desktops, Windows (native + WSL), and Android. A headless Linux server acts as the always-on hub so devices sync asynchronously. No cloud dependency; all traffic stays on the private Tailscale mesh. See [DESIGN.md](DESIGN.md) §10 for why Syncthing handles sync rather than the Obsidian Git plugin or Obsidian Sync.

## Dual-layer encryption (self-hosting)

Two encryption layers protect note content before it reaches GitHub:

1. **git-crypt**: encrypts file contents in git objects (AES-256). Templates and config stay unencrypted.
2. **git-remote-gcrypt**: encrypts the entire remote, including filenames, directory structure, and commit history.

Together, GitHub sees only opaque encrypted data. Neither layer alone provides full coverage.

## Automated backup (self-hosting)

A systemd timer commits and pushes changes hourly. A post-commit hook mirrors the vault's structure, templates, config, and documentation to a public template repo via rsync. Content directories are excluded; the public mirror shows the layout without any private notes. The sync uses a fail-closed allowlist at the root level: new root files and directories do not publish unless explicitly added. Files inside already-allowlisted subtrees (e.g., `5-templates/`, `nvim-vault/`) publish automatically. See [DESIGN.md](DESIGN.md) §10 for why the timer runs externally rather than through the Obsidian Git plugin.

## Public template mirroring (self-hosting)

The post-commit hook automatically syncs public-safe files to a separate GitHub repo. Content directories appear as empty shells (with `.gitkeep`). The hook derives content directories from `.gitattributes`, so adding a new encrypted directory requires only one file change. A sentinel file guards against accidental sync to the wrong repo.
