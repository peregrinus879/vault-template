# Features

What this vault template provides out of the box and why each piece matters.

## Opinionated Zettelkasten structure

Seven numbered directories enforce a knowledge lifecycle: capture, process, synthesize, navigate, compose. Each directory has a dedicated template with pre-filled frontmatter. The numbered prefix keeps folders sorted in every file explorer and picker, across every platform.

## Templates for every note type

Six templates cover the full Zettelkasten workflow: fleeting, literature, permanent, MOC, index, and writing. Each template sets `type`, `id`, `aliases`, `tags`, and type-specific fields. Enum-valued fields carry inline YAML comments for reference. Notes land in the correct folder automatically when created via obsidian.nvim's `<leader>oN`.

## Dual-editor support

The same markdown files work in both Obsidian (desktop, mobile) and Neovim (terminal, via obsidian.nvim). No import step, no format conversion, no sync delay beyond Syncthing. The `nvim-vault/` stow overlay ships a complete obsidian.nvim configuration as a LazyVim plugin spec, including slug-based filenames, template routing, and a custom rename command.

## Slug filenames with readable aliases

Note filenames are auto-generated lowercase-hyphenated slugs (e.g., `risk-appetite-is-a-board-level-choice.md`). The human-readable title lives in the `aliases` frontmatter field, which powers search and `[[link]]` autocomplete in both editors. Slugs avoid all cross-platform filename issues (Syncthing moves files across Linux, Windows, and Android).

## Frontmatter normalization

A pre-commit hook (`.githooks/pre-commit`) fills missing `id`, `aliases`, `tags`, and `type` fields on staged notes. Notes created outside templates (mobile captures, file manager, copy-paste) get correct metadata automatically on commit. The `type` field is derived from the folder name.

## Multi-device sync

Syncthing over Tailscale provides real-time file sync across Linux desktops, Windows (native + WSL), and Android. A headless Linux server acts as the always-on hub so devices sync asynchronously. No cloud dependency; all traffic stays on the private Tailscale mesh.

## Dual-layer encryption (self-hosting)

Two encryption layers protect note content before it reaches GitHub:

1. **git-crypt**: encrypts file contents in git objects (AES-256). Templates and config stay unencrypted.
2. **git-remote-gcrypt**: encrypts the entire remote, including filenames, directory structure, and commit history.

Together, GitHub sees only opaque encrypted data. Neither layer alone provides full coverage.

## Automated backup (self-hosting)

A systemd timer commits and pushes changes hourly. A post-commit hook mirrors the vault's structure, templates, config, and documentation to a public template repo via rsync. Content directories are excluded; the public mirror shows the layout without any private notes. The sync uses a fail-closed allowlist at the root level: new root files and directories do not publish unless explicitly added. Files inside already-allowlisted subtrees (e.g., `5-templates/`, `nvim-vault/`) publish automatically.

## Public template mirroring (self-hosting)

The post-commit hook automatically syncs public-safe files to a separate GitHub repo. Content directories appear as empty shells (with `.gitkeep`). The hook derives content directories from `.gitattributes`, so adding a new encrypted directory requires only one file change. A sentinel file guards against accidental sync to the wrong repo.
