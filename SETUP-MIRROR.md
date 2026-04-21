# Setup: Public template mirror

Mirror the vault's structure, templates, config, and public-safe docs to a separate public GitHub repo. Note content never reaches the mirror. A post-commit hook on the hub runs rsync with a fail-closed allowlist after every private-repo commit. Useful if you want to share the template so others can fork it (or if you want a public record of future reinstalls).

**Prerequisite**: [SETUP-BACKUP.md](SETUP-BACKUP.md) (auto-commit timer must be running so the post-commit hook has a trigger).

**What this adds**:

| Feature | Purpose |
|---|---|
| Public GitHub repo (`vault-template`) | Forkable starting point; shows the repo layout and configuration without any private notes |
| Post-commit sync hook | Runs after every commit on the hub; rsyncs the allowlisted paths to the public repo |
| Fail-closed allowlist | Only explicitly named paths publish; anything new is excluded by default |
| Sentinel file | Guards against a misconfigured `vault.publicPath` trashing an unrelated repo |

**Prerequisites**:

- **Public GitHub repo** (e.g., `vault-template`).
- **rsync** installed on the hub: `sudo pacman -S rsync`.

## 1. Clone the public repo

```bash
cd ~/projects/repos/templates
git clone git@github.com:<owner>/vault-template.git
```

The hook defaults to `$HOME/projects/repos/templates/vault-template`. Override per-repo via `git config vault.publicPath /your/path` if you clone elsewhere.

## 2. Deploy key

Generate a dedicated SSH key for unattended push:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/vault-template-deploy-key -N "" -C "vault-template-sync"
cd ~/projects/repos/templates/vault-template && git config core.sshCommand "ssh -i ~/.ssh/vault-template-deploy-key -o IdentitiesOnly=yes"
gh repo deploy-key add ~/.ssh/vault-template-deploy-key.pub --repo <owner>/vault-template --title "vault-template-sync" --allow-write
```

Verify:

```bash
cd ~/projects/repos/templates/vault-template && git push --dry-run origin main
```

## 3. Sentinel file

The post-commit hook refuses to run unless the public repo contains a `.public-mirror-marker` file. This guards against a misconfigured `vault.publicPath` trashing an unrelated repo. Create it once:

```bash
touch ~/projects/repos/templates/vault-template/.public-mirror-marker
cd ~/projects/repos/templates/vault-template && git add .public-mirror-marker && git commit -m "chore: add sentinel marker"
```

## 4. Post-commit hook

The hook is tracked in the repo at `.githooks/post-commit`. Enable it on the remote hub only:

```bash
cd ~/vault && git config core.hooksPath .githooks
```

Verify the executable bit is set (git preserves it on clone):

```bash
ls -la ~/vault/.githooks/post-commit
```

If not executable, set and re-commit:

```bash
chmod +x ~/vault/.githooks/post-commit
cd ~/vault && git add .githooks/post-commit && git commit -m "chore: mark hook executable"
```

Local machines skip this step; the hook runs only on the remote hub.

## 5. Rsync rules

The hook uses a fail-closed allowlist: only paths named explicitly in the `--include` list are published; the trailing `--exclude='*'` denies everything else.

| Rule | Effect |
|---|---|
| Explicit `--include` allowlist | Only named root files (docs, `LICENSE`, `.gitignore`, `.gitattributes`, `.stignore`), `nvim-vault/**`, `infra/**`, `5-templates/**`, `.githooks/**`, and public-safe `.obsidian/` subfiles are published |
| Trailing `--exclude='*'` | Anything not in the allowlist is denied; a new top-level file or directory will not publish unless its path is added to the filter |
| Sentinel check (`.public-mirror-marker`) | Hook refuses to sync unless `$PUBLIC` contains the marker file. Guards against a wrong `vault.publicPath` trashing an unrelated repo |
| `--filter='P /.public-mirror-marker'` | Protects the sentinel file from `--delete` (the marker lives only in vault-template, not in the private vault) |
| Orphan cleanup loop | Removes top-level directories from the public repo that no longer exist in the vault (catches renames) |
| `.gitkeep` creation loop | Creates empty content-directory shells in the public repo (content dirs are not in the allowlist) |
| `--delete` | Anything in the public repo but not matched by the allowlist is removed on the next sync |
| `VAULT` resolution | Read from `git rev-parse --show-toplevel`; the hook works in any clone regardless of filesystem location |
| `PUBLIC` resolution | Read from `git config vault.publicPath`, falling back to `$HOME/projects/repos/templates/vault-template`. Forks override via `git config vault.publicPath /their/path` |

**Public-mirror constraint**: `--delete` plus the cleanup loops mean the public repo is strictly a derived view of the private vault's allowlisted set. Any file or directory that exists only in the public repo will be wiped on the next sync unless explicitly protected. To preserve a public-only item, three places in `.githooks/post-commit` must be updated: (1) add an rsync protect filter (e.g., `--filter='P /.github/'`), (2) add the directory name to the orphan-directory skip list, and (3) add the filename to the `ALLOWED_ROOT_FILES` list for root files.

## 6. Testing

Verify no private content leaks:

```bash
# Create a fake note in a content directory
echo "PRIVATE" > ~/vault/0-fleeting/test-leak.md
cd ~/vault && git add -A && git commit -m "test: leak check"

# Verify it did NOT appear in the public repo
ls ~/projects/repos/templates/vault-template/0-fleeting/
# Expected: only .gitkeep

# Clean up
rm ~/vault/0-fleeting/test-leak.md
cd ~/vault && git add -A && git commit -m "test: clean up"
```

Verify template sync works:

```bash
# Modify a template
echo "<!-- test -->" >> ~/vault/5-templates/fleeting.md
cd ~/vault && git add -A && git commit -m "test: sync check"

# Verify it appeared in the public repo
tail -1 ~/projects/repos/templates/vault-template/5-templates/fleeting.md
# Expected: <!-- test -->

# Clean up
sed -i '$ d' ~/vault/5-templates/fleeting.md
cd ~/vault && git add -A && git commit -m "test: clean up"
```

## Verify

- Public template sync: modify a template, commit, verify it appears in the public repo and on GitHub.
- Leak check: add a file in a content directory, commit, confirm it does NOT appear in the public repo.
- Post-commit log: `journalctl --user -u vault-autocommit.service` shows `sync: <date>` commits appearing alongside `auto:` commits.
