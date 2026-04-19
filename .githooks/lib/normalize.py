#!/usr/bin/env python3
"""Vault frontmatter normalizer.

Two modes:

  --fill PATH [PATH ...]
      Add missing frontmatter fields and sync `id` to the filename
      stem. Never rewrites existing user values beyond `id`. Exits 0
      on success; non-zero only on I/O errors. Writes the file back
      when changed.

  --check PATH [PATH ...]
      Report problems without modifying files. Prints one line per
      issue to stderr. Exits non-zero if any issue is found.

Canonical field order written by --fill:
    id, aliases, type, created, updated, tags

Field rules (--fill):
    id       : always rewritten to match the filename stem
               (tautological with filename; kept in sync)
    aliases  : if field absent, added with a single entry chosen as
               the first populated of: first-line H1 heading, filename
               stem. If field present, preserved verbatim.
    type     : if field absent or empty value, set to the folder-
               derived type (first path component, stripping the
               leading 'N-' prefix). Otherwise preserved.
    created  : if field absent or empty value, set to today's date
               (YYYY-MM-DD). Otherwise preserved.
    updated  : if field absent, added with empty value. Preserved if
               present (value never touched by this tool).
    tags     : if field absent, added as empty flow sequence `[]`.
               Preserved if present.

Extra user-added frontmatter fields are preserved and emitted after
the canonical six, in the order they appear in the source.

Idempotent: running --fill twice on the same file produces no further
changes on the second run.

Design notes:
    The parser is intentionally tolerant of the vault's known YAML
    subset (flat key: value pairs plus a single block-style list for
    `aliases`). It does not handle general YAML. Files with malformed
    frontmatter (unclosed `---`, inline flow mappings) are skipped
    with a warning rather than mangled.
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


def yaml_single_quote(value: str) -> str:
    """Quote a scalar as a YAML single-quoted string.

    Single quotes in YAML single-quoted strings are escaped by
    doubling. No backslash escapes are interpreted. Safe for arbitrary
    content including colons, braces, and special characters.
    """
    return "'" + value.replace("'", "''") + "'"


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
    # Preserve insertion order via dict (Python 3.7+).
    ordered = {k: fields[k] for k in order}
    return ordered


def field_has_value(field_lines: list[str]) -> bool:
    """True if the field's first line has a non-empty value after the colon."""
    first = field_lines[0]
    m = KEY_LINE_RE.match(first)
    if not m:
        return False
    return m.group(2).strip() != ""


def extract_h1_title(body_lines: list[str]) -> str | None:
    """Return the first H1 heading text, skipping leading blank lines.

    Returns None if the first non-blank line is not an H1 heading.
    """
    for raw in body_lines:
        line = raw.rstrip("\r\n")
        if line.strip() == "":
            continue
        m = H1_RE.match(line)
        return m.group(1) if m else None
    return None


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
) -> dict[str, list[str]]:
    """Return the field map after applying fill rules in canonical order.

    Extra user-added fields (not in CANONICAL_ORDER) are preserved at
    the end in source order.
    """
    out: dict[str, list[str]] = {}

    # id: always synced to stem.
    out["id"] = [f"id: {yaml_single_quote(stem)}"]

    # aliases: preserve if present, else fill from H1 or stem.
    if "aliases" in existing:
        out["aliases"] = list(existing["aliases"])
    else:
        title = h1_title if h1_title else stem
        out["aliases"] = ["aliases:", f"  - {yaml_single_quote(title)}"]

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


def fill_file(path: str, vault_root: str, today: str) -> bool:
    """Normalize the frontmatter of one file in place.

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
    )

    new_fm = render_frontmatter(new_fields)
    new_lines = [FM_DELIM, *new_fm, FM_DELIM]

    # If the original had no frontmatter, ensure one blank line before body.
    if fm_lines is None:
        separator = [""] if body and body[0].strip() != "" else []
        new_lines.extend(separator)
        new_lines.extend(body)
    else:
        new_lines.extend(body)

    new_content = "\n".join(new_lines)
    # Preserve trailing newline presence.
    if original.endswith("\n") and not new_content.endswith("\n"):
        new_content += "\n"

    if new_content == original:
        return False

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_content)
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

    for required in CANONICAL_ORDER:
        if required not in existing:
            issues.append(f"{path}: missing field '{required}'")

    if "id" in existing:
        first = existing["id"][0]
        m = KEY_LINE_RE.match(first)
        value = m.group(2).strip() if m else ""
        unquoted = value.strip("'\"")
        if unquoted != stem:
            issues.append(f"{path}: id '{unquoted}' does not match filename stem '{stem}'")

    if folder_type and "type" in existing and field_has_value(existing["type"]):
        first = existing["type"][0]
        m = KEY_LINE_RE.match(first)
        value = m.group(2).strip() if m else ""
        if value != folder_type:
            issues.append(f"{path}: type '{value}' does not match folder-derived '{folder_type}'")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize vault note frontmatter.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fill", action="store_true",
                       help="Add missing fields and sync id in-place.")
    group.add_argument("--check", action="store_true",
                       help="Report issues; exit non-zero if any found.")
    parser.add_argument("paths", nargs="+",
                        help="Markdown files to process.")
    parser.add_argument("--vault-root", default=None,
                        help="Override vault root (defaults to git toplevel).")
    args = parser.parse_args()

    if args.vault_root:
        vault_root = os.path.abspath(args.vault_root)
    else:
        # Fall back to the parent of .githooks/lib.
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
                if fill_file(p, vault_root, today):
                    changed += 1
            except OSError as exc:
                print(f"[normalize] error: {p}: {exc}", file=sys.stderr)
                return 1
        else:  # --check
            for issue in check_file(p, vault_root):
                print(issue, file=sys.stderr)
                issues_found += 1

    if args.fill and changed > 0:
        print(f"[normalize] filled {changed} file(s).", file=sys.stderr)

    return 1 if issues_found > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
