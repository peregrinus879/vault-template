#!/usr/bin/env python3
"""Vault note normalizer.

Enforces identity invariants across the vault's content notes:

- Canonical frontmatter (id, aliases, type, created, updated, tags).
- Body `# H1` heading matching aliases[0].
- Template body application (via --apply mode).

Modes:

  --fill PATH [PATH ...]
      Normalize frontmatter fields and ensure the body has a
      `# H1` matching aliases[0]. Body is otherwise untouched.
      Exits 0 on success; non-zero only on I/O errors.

  --apply PATH [PATH ...]
      If the file has no frontmatter, read the folder-matched
      template from 5-templates/, substitute placeholders, prepend
      to body, and wrap any pre-existing body content in a
      `## Capture` section at the end. If the file already has
      frontmatter, delegate to --fill.

  --check PATH [PATH ...]
      Report problems without modifying files. Prints one line per
      issue to stderr. Exits non-zero if any issue is found.

Canonical field order:
    id, aliases, type, created, updated, tags

Field rules:
    id       : always rewritten to match the filename stem.
    aliases  : aliases[0] = body H1 > caller-supplied fallback >
               filename stem. If aliases already exists, aliases[0]
               is overwritten with this canonical value; aliases[1..]
               are preserved (user-added synonyms), deduplicated
               against the canonical first entry.
    type     : if absent or empty, set to the folder-derived type.
               Otherwise preserved.
    created  : if absent or empty, set to today. Otherwise preserved.
    updated  : if absent, added as empty. Never rewritten.
    tags     : if absent, added as empty flow sequence `[]`.

Body rules (--fill and --apply):
    H1 heading : if body has no `# H1` as its first non-blank line,
                 `# {aliases[0]}` is inserted after the frontmatter.
                 If H1 exists, aliases[0] is synced to its text
                 (H1 wins when both are present and differ).

Extra user-added frontmatter fields are preserved and emitted
after the canonical six, in the order they appear in the source.

Idempotent: running the same mode twice produces no further
changes on the second run.

When a file is modified, its path is printed to stdout (one per
line). Callers (pre-commit hook, editor orchestrators) read
stdout to re-stage or refresh only the changed files.

Design notes:
    The parser is tolerant of the vault's YAML subset: flat
    `key: value` pairs plus a block-style or simple flow-style
    list for `aliases`. It does not handle general YAML. Files
    with malformed frontmatter (unclosed `---`, nested mappings)
    are skipped with a warning rather than mangled.

    YAML comments inside frontmatter (lines starting with `#`) are
    NOT preserved: they are merged into the preceding field's
    value lines during parsing and dropped when that field is
    rewritten in canonical order.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date

CANONICAL_ORDER = ("id", "aliases", "type", "created", "updated", "tags")
FM_DELIM = "---"
FOLDER_TYPE_RE = re.compile(r"^\d+-(.+)$")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")
KEY_LINE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:(.*)$")
TEMPLATES_SUBDIR = "5-templates"


def yaml_single_quote(value: str) -> str:
    """Quote a scalar as a YAML single-quoted string.

    Single quotes in YAML single-quoted strings are escaped by
    doubling. No backslash escapes are interpreted. Safe for arbitrary
    content including colons, braces, and special characters.
    """
    return "'" + value.replace("'", "''") + "'"


def unquote_yaml(value: str) -> str:
    """Strip YAML single or double quotes from a scalar value.

    Handles the doubled single-quote escape inside single-quoted
    strings. Double-quoted strings have backslash escapes left
    as-is (not used in the vault's content).
    """
    if len(value) >= 2:
        if value[0] == "'" and value[-1] == "'":
            return value[1:-1].replace("''", "'")
        if value[0] == '"' and value[-1] == '"':
            return value[1:-1]
    return value


def split_frontmatter(lines: list[str]) -> tuple[list[str] | None, int]:
    """Return (frontmatter_lines, body_start_index).

    frontmatter_lines excludes both `---` delimiters. Returns (None, 0)
    if the document has no frontmatter (first line is not `---`).
    Returns (None, -1) if the frontmatter is unclosed (for caller to
    report).
    """
    if not lines or lines[0].rstrip("\r\n") != FM_DELIM:
        return None, 0
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == FM_DELIM:
            return lines[1:i], i + 1
    return None, -1


def parse_fields(fm_lines: list[str]) -> dict[str, list[str]]:
    """Parse frontmatter into {key: [value-line, ...]}.

    Multi-line values (list entries, continuation lines) are attached
    to the most recent top-level key. Preserves exact line text so
    unknown formats round-trip correctly.
    """
    fields: dict[str, list[str]] = {}
    order: list[str] = []
    current: str | None = None
    for raw in fm_lines:
        line = raw.rstrip("\r\n")
        if line and not line[0].isspace() and not line.startswith("#"):
            m = KEY_LINE_RE.match(line)
            if m:
                current = m.group(1)
                fields[current] = [line]
                order.append(current)
                continue
        if current is not None:
            fields[current].append(line)
    ordered = {k: fields[k] for k in order}
    return ordered


def field_has_value(field_lines: list[str]) -> bool:
    """True if the field's first line has a non-empty value after the colon."""
    first = field_lines[0]
    m = KEY_LINE_RE.match(first)
    if not m:
        return False
    return m.group(2).strip() != ""


def aliases_is_empty(field_lines: list[str]) -> bool:
    """True if an aliases field is present but carries no entries.

    Covers inline-empty forms (`aliases:` with no value, `aliases: []`,
    `aliases: [ ]` with whitespace) and block-form with no list items
    following. A block-form field with at least one `- value` line is
    considered populated. An inline flow sequence with entries (e.g.,
    `aliases: [one, two]`) is considered populated.
    """
    first = field_lines[0]
    m = KEY_LINE_RE.match(first)
    if m:
        value = m.group(2).strip()
        if value.startswith("[") and value.endswith("]"):
            if value[1:-1].strip() == "":
                value = "[]"
        if value in ("", "[]"):
            for line in field_lines[1:]:
                stripped = line.strip()
                if stripped.startswith("-") and stripped != "-":
                    return False
            return True
    return False


def extract_alias_values(field_lines: list[str]) -> list[str]:
    """Extract alias values from an aliases field.

    Supports block form (`aliases:\\n  - item`) and simple flow form
    (`aliases: [a, b]`). Returns an empty list for empty or missing
    entries. Commas inside quoted flow items are not respected; the
    vault's content is not expected to use such values.
    """
    first = field_lines[0]
    m = KEY_LINE_RE.match(first)
    inline_value = m.group(2).strip() if m else ""

    if inline_value.startswith("[") and inline_value.endswith("]"):
        inner = inline_value[1:-1].strip()
        if inner == "":
            return []
        return [unquote_yaml(item.strip()) for item in inner.split(",") if item.strip()]

    values: list[str] = []
    for line in field_lines[1:]:
        stripped = line.strip()
        if stripped.startswith("- ") and stripped != "-":
            raw = stripped[2:].strip()
            values.append(unquote_yaml(raw))
    return values


def render_aliases(values: list[str]) -> list[str]:
    """Render an aliases list as frontmatter lines in block form.

    Empty list emits `aliases: []`. Non-empty emits a block list with
    each entry single-quoted.
    """
    if not values:
        return ["aliases: []"]
    lines = ["aliases:"]
    for v in values:
        lines.append(f"  - {yaml_single_quote(v)}")
    return lines


def extract_h1_title(body_lines: list[str]) -> str | None:
    """Return the first non-blank line's H1 text, or None.

    Non-blank line that is not an H1 returns None. Used to derive
    canonical aliases[0] and to decide whether ensure_h1 should
    insert one.
    """
    for raw in body_lines:
        line = raw.rstrip("\r\n")
        if line.strip() == "":
            continue
        m = H1_RE.match(line)
        return m.group(1) if m else None
    return None


def ensure_h1(body: list[str], title: str) -> list[str]:
    """Return body with a `# title` line before the first non-blank line.

    If the first non-blank line is already an H1, body is returned
    unchanged. If the body is empty or all-blank, the H1 is appended.
    """
    first_content_idx = next(
        (i for i, line in enumerate(body) if line.strip() != ""),
        None,
    )
    if first_content_idx is not None:
        if H1_RE.match(body[first_content_idx]):
            return body
        return body[:first_content_idx] + [f"# {title}", ""] + body[first_content_idx:]
    return body + [f"# {title}"]


def derive_folder_type(path: str, vault_root: str) -> str:
    """Extract the type suffix from the top-level content folder name.

    Example: vault_root=/home/user/vault, path=.../2-permanent/foo.md
    -> 'permanent'. Returns empty string if the path is not under a
    content folder matching the N-name pattern.
    """
    try:
        rel = os.path.relpath(path, vault_root)
    except ValueError:
        return ""
    parts = rel.split(os.sep)
    if len(parts) < 2:
        return ""
    m = FOLDER_TYPE_RE.match(parts[0])
    return m.group(1) if m else ""


def build_canonical_fields(
    existing: dict[str, list[str]],
    *,
    stem: str,
    h1_title: str | None,
    folder_type: str,
    today: str,
    fallback_alias: str | None = None,
) -> dict[str, list[str]]:
    """Return the field map after applying fill rules in canonical order.

    Aliases rule: canonical aliases[0] = h1_title > fallback_alias >
    filename stem. If the existing aliases list is populated, aliases[0]
    is overwritten with the canonical value; aliases[1..] are preserved
    (user-added synonyms) with duplicates against aliases[0] removed.
    Extra user-added fields (not in CANONICAL_ORDER) are preserved at
    the end in source order.
    """
    out: dict[str, list[str]] = {}

    # id: always synced to stem.
    out["id"] = [f"id: {yaml_single_quote(stem)}"]

    # aliases: H1 drives aliases[0] (bidirectional sync rule).
    canonical_first = h1_title or fallback_alias or stem
    existing_values: list[str] = []
    if "aliases" in existing and not aliases_is_empty(existing["aliases"]):
        existing_values = extract_alias_values(existing["aliases"])
    tail = [v for v in existing_values[1:] if v and v != canonical_first]
    out["aliases"] = render_aliases([canonical_first] + tail)

    # type: preserve if populated, else fill from folder.
    if "type" in existing and field_has_value(existing["type"]):
        out["type"] = list(existing["type"])
    else:
        out["type"] = [f"type: {folder_type}" if folder_type else "type:"]

    # created: preserve if populated, else fill with today.
    if "created" in existing and field_has_value(existing["created"]):
        out["created"] = list(existing["created"])
    else:
        out["created"] = [f"created: {today}"]

    # updated: preserve if present at all; otherwise add empty.
    if "updated" in existing:
        out["updated"] = list(existing["updated"])
    else:
        out["updated"] = ["updated:"]

    # tags: preserve if present, else empty flow sequence.
    if "tags" in existing:
        out["tags"] = list(existing["tags"])
    else:
        out["tags"] = ["tags: []"]

    # Preserve unknown user-added fields after the canonical block.
    for key, value in existing.items():
        if key not in CANONICAL_ORDER:
            out[key] = list(value)

    return out


def render_frontmatter(fields: dict[str, list[str]]) -> list[str]:
    """Flatten a field map into frontmatter lines (without delimiters)."""
    rendered: list[str] = []
    for lines in fields.values():
        rendered.extend(lines)
    return rendered


def fill_file(
    path: str,
    vault_root: str,
    today: str,
    fallback_alias: str | None = None,
) -> bool:
    """Normalize frontmatter and ensure body H1 in place.

    Returns True if the file was modified, False if already canonical.
    Prints a warning and returns False on malformed frontmatter.
    """
    with open(path, "r", encoding="utf-8") as fh:
        original = fh.read()
    lines = original.splitlines(keepends=False)

    fm_lines, body_start = split_frontmatter(lines)
    if body_start == -1:
        print(f"[normalize] warning: {path} has unclosed frontmatter; skipping.",
              file=sys.stderr)
        return False

    body = lines[body_start:] if body_start > 0 else lines
    existing = parse_fields(fm_lines) if fm_lines is not None else {}

    stem = os.path.splitext(os.path.basename(path))[0]
    h1_title = extract_h1_title(body)
    folder_type = derive_folder_type(path, vault_root)

    new_fields = build_canonical_fields(
        existing,
        stem=stem,
        h1_title=h1_title,
        folder_type=folder_type,
        today=today,
        fallback_alias=fallback_alias,
    )

    canonical_aliases = extract_alias_values(new_fields["aliases"])
    title_for_h1 = canonical_aliases[0] if canonical_aliases else stem
    new_body = ensure_h1(body, title_for_h1)

    new_fm = render_frontmatter(new_fields)
    new_lines = [FM_DELIM, *new_fm, FM_DELIM]

    # If the original had no frontmatter, ensure one blank line before body.
    if fm_lines is None:
        separator = [""] if new_body and new_body[0].strip() != "" else []
        new_lines.extend(separator)
    new_lines.extend(new_body)

    new_content = "\n".join(new_lines)
    if original.endswith("\n") and not new_content.endswith("\n"):
        new_content += "\n"

    if new_content == original:
        return False

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_content)
    return True


def substitute_placeholders(
    text: str,
    *,
    title: str,
    stem: str,
    today: str,
) -> str:
    """Replace {{title}}, {{id}}, {{date}} in a template text.

    Matches the subset of obsidian.nvim's template placeholders that
    the vault uses. Other placeholders (e.g. {{time}}) pass through
    unchanged.
    """
    return (text
        .replace("{{title}}", title)
        .replace("{{id}}", stem)
        .replace("{{date}}", today))


def apply_file(
    path: str,
    vault_root: str,
    today: str,
    fallback_alias: str | None = None,
) -> bool:
    """Apply canonical template + frontmatter to a note.

    If the file already has frontmatter, delegates to fill_file
    (which handles the aliases[0] ↔ H1 sync). Otherwise reads the
    folder-matched template from 5-templates/, substitutes
    placeholders, prepends it to the file, and wraps any pre-
    existing body content in a `## Capture` section at the end.

    Returns True if the file was modified, False if unchanged.
    """
    with open(path, "r", encoding="utf-8") as fh:
        original = fh.read()
    lines = original.splitlines(keepends=False)

    fm_lines, body_start = split_frontmatter(lines)
    if body_start == -1:
        print(f"[normalize] warning: {path} has unclosed frontmatter; skipping.",
              file=sys.stderr)
        return False

    # Frontmatter present → delegate to fill (no body template rework).
    if fm_lines is not None:
        return fill_file(path, vault_root, today, fallback_alias)

    folder_type = derive_folder_type(path, vault_root)
    if not folder_type:
        # Not in a recognized content folder; fill handles bare notes.
        return fill_file(path, vault_root, today, fallback_alias)

    template_path = os.path.join(vault_root, TEMPLATES_SUBDIR, f"{folder_type}.md")
    if not os.path.isfile(template_path):
        print(f"[normalize] warning: template {template_path} not found; "
              f"falling back to fill mode.", file=sys.stderr)
        return fill_file(path, vault_root, today, fallback_alias)

    with open(template_path, "r", encoding="utf-8") as fh:
        template_text = fh.read()

    stem = os.path.splitext(os.path.basename(path))[0]
    title = fallback_alias or stem

    substituted = substitute_placeholders(
        template_text, title=title, stem=stem, today=today
    )

    existing_body = original.strip()
    if existing_body:
        new_content = (
            substituted.rstrip("\n")
            + "\n\n## Capture\n\n"
            + existing_body
            + "\n"
        )
    else:
        new_content = substituted
        if not new_content.endswith("\n"):
            new_content += "\n"

    if new_content == original:
        return False

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    # Post-apply: run fill to sync aliases[0] ↔ H1 (the substituted
    # template may have aliases[0] as fallback/stem, but the H1 is the
    # same substitution — they should already match). Fill also
    # reconciles any edge case where the template's aliases differ.
    fill_file(path, vault_root, today, fallback_alias)

    return True


def check_file(path: str, vault_root: str) -> list[str]:
    """Return a list of human-readable issues with the file.

    Empty list means the file passes. Does not modify the file.
    """
    issues: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        return [f"{path}: cannot read ({exc})"]

    lines = content.splitlines(keepends=False)
    fm_lines, body_start = split_frontmatter(lines)
    if body_start == -1:
        issues.append(f"{path}: unclosed frontmatter")
        return issues
    if fm_lines is None:
        issues.append(f"{path}: no frontmatter")
        return issues

    existing = parse_fields(fm_lines)
    stem = os.path.splitext(os.path.basename(path))[0]
    folder_type = derive_folder_type(path, vault_root)
    body = lines[body_start:] if body_start > 0 else []
    h1_title = extract_h1_title(body)

    for required in CANONICAL_ORDER:
        if required not in existing:
            issues.append(f"{path}: missing field '{required}'")

    if "id" in existing:
        first = existing["id"][0]
        m = KEY_LINE_RE.match(first)
        value = m.group(2).strip() if m else ""
        unquoted = unquote_yaml(value)
        if unquoted != stem:
            issues.append(f"{path}: id '{unquoted}' does not match filename stem '{stem}'")

    if folder_type and "type" in existing and field_has_value(existing["type"]):
        first = existing["type"][0]
        m = KEY_LINE_RE.match(first)
        value = m.group(2).strip() if m else ""
        if value != folder_type:
            issues.append(f"{path}: type '{value}' does not match folder-derived '{folder_type}'")

    if "aliases" in existing and not aliases_is_empty(existing["aliases"]):
        alias_values = extract_alias_values(existing["aliases"])
        if alias_values and h1_title and alias_values[0] != h1_title:
            issues.append(
                f"{path}: aliases[0] '{alias_values[0]}' does not match H1 '{h1_title}'"
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize vault note frontmatter and body.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fill", action="store_true",
                       help="Normalize frontmatter and ensure body H1 in-place.")
    group.add_argument("--apply", action="store_true",
                       help="Apply folder-matched template to notes missing "
                            "frontmatter; otherwise equivalent to --fill.")
    group.add_argument("--check", action="store_true",
                       help="Report issues; exit non-zero if any found.")
    parser.add_argument("paths", nargs="+",
                        help="Markdown files to process.")
    parser.add_argument("--vault-root", default=None,
                        help="Override vault root (defaults to git toplevel).")
    parser.add_argument("--fallback-alias", default=None,
                        help="Alias used for aliases[0] when no H1 is present. "
                             "Typically the pre-rename filename stem, supplied "
                             "by the <leader>oS orchestrator.")
    args = parser.parse_args()

    if args.vault_root:
        vault_root = os.path.abspath(args.vault_root)
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        vault_root = os.path.abspath(os.path.join(here, "..", ".."))

    today = date.today().isoformat()
    changed = 0
    issues_found = 0

    for p in args.paths:
        if not os.path.isfile(p):
            print(f"[normalize] warning: {p} is not a file; skipping.", file=sys.stderr)
            continue
        if args.fill:
            try:
                if fill_file(p, vault_root, today, args.fallback_alias):
                    print(p)
                    changed += 1
            except OSError as exc:
                print(f"[normalize] error: {p}: {exc}", file=sys.stderr)
                return 1
        elif args.apply:
            try:
                if apply_file(p, vault_root, today, args.fallback_alias):
                    print(p)
                    changed += 1
            except OSError as exc:
                print(f"[normalize] error: {p}: {exc}", file=sys.stderr)
                return 1
        else:  # --check
            for issue in check_file(p, vault_root):
                print(issue, file=sys.stderr)
                issues_found += 1

    if (args.fill or args.apply) and changed > 0:
        print(f"[normalize] modified {changed} file(s).", file=sys.stderr)

    return 1 if issues_found > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
