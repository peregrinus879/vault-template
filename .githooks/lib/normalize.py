#!/usr/bin/env python3
"""Vault note normalizer.

Enforces identity invariants across the vault's content notes:

- Canonical frontmatter (id, aliases, tags) — aligned with
  obsidian.nvim's default emitter.
- Body `# H1` heading matching aliases[0].
- Template body application (via --apply mode).

Modes:

  --fill PATH [PATH ...]
      Normalize frontmatter fields and ensure the body has a
      `# H1` matching aliases[0]. Body is otherwise untouched.
      Exits 0 on success; non-zero only on I/O errors.

  --apply PATH [PATH ...]
      Branch on note state:
      - No frontmatter → prepend full folder-matched template (FM
        + body), wrap any pre-existing body content in `## Capture`
        at the end.
      - Frontmatter present, body has no `## ` heading → insert
        template body sections after the existing H1 (template's
        own H1 stripped), wrap any pre-existing non-H1 content in
        `## Capture`. Closes the gap for captures that land with
        frontmatter but no body structure (Neovim auto-FM, mobile,
        Obsidian Ctrl+N without template).
      - Frontmatter present, body has ≥1 `## ` heading → treat as
        structured; delegate to --fill (frontmatter fields + H1
        sync only, body untouched).
      Any `## ` heading in the body is the user's escape hatch to
      opt out of template re-application.

  --reapply PATH [PATH ...]
      Force-apply the folder-matched template regardless of body
      state, used by the <leader>oM promotion orchestrator after
      moving a file between content folders.
      - No frontmatter → fall back to --apply (branch 1 handles it).
      - Frontmatter present → split the body at the first `## Capture`
        heading. Content before that (old template sections) is
        discarded; `## Capture` onward (user data) is preserved. If
        no `## Capture` exists, everything below H1 is wrapped in a
        new `## Capture`. Target template's body sections are then
        inserted between H1 and the preserved/wrapped content.
      The `## ` escape hatch that protects --apply's third branch
      is deliberately bypassed here: the caller has asked for a
      template swap, which is the whole point of promotion.
      Idempotent: the `## Capture` preserved on one run is preserved
      unchanged on the next.

  --check PATH [PATH ...]
      Report problems without modifying files. Prints one line per
      issue to stderr. Exits non-zero if any issue is found.

Canonical field order:
    id, aliases, tags

Field rules:
    id       : always rewritten to match the filename stem.
    aliases  : aliases[0] = body H1 > caller-supplied fallback >
               filename stem. If aliases already exists, aliases[0]
               is overwritten with this canonical value; aliases[1..]
               are preserved (user-added synonyms), deduplicated
               against the canonical first entry.
    tags     : if absent, added as empty flow sequence `[]`.

Body rules (--fill and --apply):
    H1 heading : if body has no `# H1` as its first non-blank line,
                 `# {aliases[0]}` is inserted after the frontmatter.
                 If H1 exists, aliases[0] is synced to its text
                 (H1 wins when both are present and differ).

Extra user-added frontmatter fields are preserved and emitted
after the canonical block, in the order they appear in the source.
Notes migrating from an earlier six-field schema retain their
`type`, `created`, `updated` values this way until cleaned up
manually.

Scalar serialization matches obsidian.nvim's yaml.lua emitter:
strings are emitted unquoted unless they start with a special
character ([, {, &, !, -, ", ', \\), contain ": ", look like a
wikilink, are empty/whitespace-only, or look like a hex color.
When quoting is required, double quotes are used and embedded
double quotes are backslash-escaped.

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

CANONICAL_ORDER = ("id", "aliases", "tags")
FM_DELIM = "---"
FOLDER_TYPE_RE = re.compile(r"^\d+-(.+)$")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")
KEY_LINE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:(.*)$")
HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
QUOTE_TRIGGER_START_CHARS = set('"\'\\[{&!-')
TEMPLATES_SUBDIR = "5-templates"


# ---------------------------------------------------------------------------
# YAML subset helpers
#
# The parser handles the vault's schema: flat `key: value` pairs plus a
# block-style or simple flow-style list for `aliases`. Not a general YAML
# parser. Files with malformed frontmatter are skipped rather than mangled.
# ---------------------------------------------------------------------------


def _should_quote(value: str) -> bool:
    """Whether a scalar needs quoting, matching obsidian.nvim's rules.

    Mirrors `should_quote` in obsidian.nvim's lua/obsidian/yaml/init.lua:
    quote if the value starts with a YAML special character, contains
    `": "`, looks like a `[[wikilink]]`, is empty or whitespace-only,
    or looks like a hex color.
    """
    if value == "" or value.isspace():
        return True
    if value[0] in QUOTE_TRIGGER_START_CHARS:
        return True
    if ": " in value:
        return True
    if re.search(r"\[\[.*?\]\]", value):
        return True
    if HEX_COLOR_RE.match(value):
        return True
    return False


def yaml_scalar(value: str) -> str:
    """Serialize a string as a YAML scalar matching obsidian.nvim's output.

    Emits the raw value unquoted when safe, or double-quoted with
    backslash-escaped embedded double quotes when special characters
    require it.
    """
    if _should_quote(value):
        return '"' + value.replace('"', '\\"') + '"'
    return value


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
    each entry serialized via yaml_scalar (quoted only when needed).
    """
    if not values:
        return ["aliases: []"]
    lines = ["aliases:"]
    for v in values:
        lines.append(f"  - {yaml_scalar(v)}")
    return lines


# ---------------------------------------------------------------------------
# Body inspection and modification
#
# Read-only extraction of the first H1, plus a minimal insert when the body
# lacks one. Both the fill and apply modes rely on these for the aliases[0]
# ↔ H1 sync rule.
# ---------------------------------------------------------------------------


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


H2_RE = re.compile(r"^##\s+")


def body_has_h2(body: list[str]) -> bool:
    """True if the body contains any `## ` (level-2 heading) line."""
    return any(H2_RE.match(line) for line in body)


def strip_template_h1(template_body_text: str) -> str:
    """Remove the first `# H1` line from template body text.

    Used when applying a template to a note that already has an H1 in
    its body — the note's H1 is preserved, and the template contributes
    only its intro comment and `##` sections. Strips the `# H1` line
    plus any blank lines immediately following it, then returns the
    remainder. If the template body has no H1, returns the input
    unchanged.
    """
    lines = template_body_text.splitlines(keepends=False)
    h1_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "":
            continue
        if H1_RE.match(line):
            h1_idx = i
        break
    if h1_idx is None:
        return template_body_text
    remaining = lines[h1_idx + 1:]
    while remaining and remaining[0].strip() == "":
        remaining.pop(0)
    return "\n".join(remaining)


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


# ---------------------------------------------------------------------------
# Path and folder classification
#
# Derives the canonical `type` value from the content directory a note lives
# under. Shared by build_canonical_fields and by apply_file (which uses it
# to pick the template).
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Canonical field building
#
# Given the existing frontmatter plus body H1 and filename stem, produces
# the canonical field map in the invariant order (id, aliases, tags).
# Unknown user-added fields (including legacy type/created/updated from
# earlier schemas) are preserved at the end in source order. See
# AGENTS.md §Invariants #5 for the aliases rule.
# ---------------------------------------------------------------------------


def build_canonical_fields(
    existing: dict[str, list[str]],
    *,
    stem: str,
    h1_title: str | None,
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
    id_emit = yaml_scalar(stem)
    # Preserve a trailing colon for slug-safe stems that don't need quoting.
    out["id"] = [f"id: {id_emit}"]

    # aliases: H1 drives aliases[0] (bidirectional sync rule).
    canonical_first = h1_title or fallback_alias or stem
    existing_values: list[str] = []
    if "aliases" in existing and not aliases_is_empty(existing["aliases"]):
        existing_values = extract_alias_values(existing["aliases"])
    tail = [v for v in existing_values[1:] if v and v != canonical_first]
    out["aliases"] = render_aliases([canonical_first] + tail)

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


# ---------------------------------------------------------------------------
# File operations (mode implementations)
#
# One function per CLI mode: fill_file for --fill, apply_file for --apply,
# check_file for --check. apply_file delegates to fill_file when the note
# already has frontmatter. substitute_placeholders is a shared helper for
# template substitution.
# ---------------------------------------------------------------------------


def fill_file(
    path: str,
    vault_root: str,
    fallback_alias: str | None = None,
) -> bool:
    """Normalize frontmatter and ensure body H1 in place.

    Returns True if the file was modified, False if already canonical.
    Prints a warning and returns False on malformed frontmatter.
    vault_root is kept in the signature for future checks that need
    folder context; currently only apply_file reads the folder type.
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

    new_fields = build_canonical_fields(
        existing,
        stem=stem,
        h1_title=h1_title,
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

    Branches on the note's current state:

    - No frontmatter → prepend the full folder-matched template
      (frontmatter + body) and wrap any pre-existing body content
      in `## Capture` at the end.
    - Frontmatter present AND body has at least one `## ` heading
      → body already has structure; delegate to fill (frontmatter
      and H1 hygiene only).
    - Frontmatter present AND body has no `## ` heading → insert
      the template's body sections (stripped of its H1 — the note
      keeps its own H1) after the existing H1; wrap any pre-
      existing non-H1 body content in `## Capture`.

    The third branch closes the gap for Neovim-created notes that
    land with obsidian.nvim's auto-frontmatter but no body template.
    Escape hatch: any `## ` in the body signals "structure already
    here," and the hook won't re-insert template sections.

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

    body = lines[body_start:] if body_start > 0 else []

    # Frontmatter present + body already structured → fill only.
    if fm_lines is not None and body_has_h2(body):
        return fill_file(path, vault_root, fallback_alias)

    folder_type = derive_folder_type(path, vault_root)
    template_path = os.path.join(vault_root, TEMPLATES_SUBDIR, f"{folder_type}.md") if folder_type else ""

    if not folder_type or not os.path.isfile(template_path):
        if folder_type and not os.path.isfile(template_path):
            print(f"[normalize] warning: template {template_path} not found; "
                  f"falling back to fill mode.", file=sys.stderr)
        return fill_file(path, vault_root, fallback_alias)

    with open(template_path, "r", encoding="utf-8") as fh:
        template_text = fh.read()

    stem = os.path.splitext(os.path.basename(path))[0]
    title = fallback_alias or stem
    substituted = substitute_placeholders(
        template_text, title=title, stem=stem, today=today
    )

    # Case: no frontmatter → full apply (prepend whole template).
    if fm_lines is None:
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
    else:
        # Case: frontmatter present + body has no ## → insert
        # template body only, keep existing FM and H1.
        sub_lines = substituted.splitlines(keepends=False)
        _, sub_body_start = split_frontmatter(sub_lines)
        if sub_body_start > 0:
            tmpl_body_text = "\n".join(sub_lines[sub_body_start:])
        else:
            tmpl_body_text = substituted
        tmpl_sections = strip_template_h1(tmpl_body_text)

        h1_idx = None
        for i, line in enumerate(body):
            if line.strip() == "":
                continue
            if H1_RE.match(line):
                h1_idx = i
            break

        if h1_idx is None:
            pre_h1: list[str] = []
            h1_line = f"# {title}"
            post_h1 = [ln for ln in body if ln.strip() != ""]
        else:
            pre_h1 = body[:h1_idx]
            h1_line = body[h1_idx]
            post_h1 = list(body[h1_idx + 1:])

        while post_h1 and post_h1[0].strip() == "":
            post_h1.pop(0)
        while post_h1 and post_h1[-1].strip() == "":
            post_h1.pop()

        new_body_lines: list[str] = list(pre_h1) + [h1_line, ""]
        new_body_lines.extend(tmpl_sections.splitlines())
        if post_h1:
            if new_body_lines[-1].strip() != "":
                new_body_lines.append("")
            new_body_lines.append("## Capture")
            new_body_lines.append("")
            new_body_lines.extend(post_h1)

        new_lines = [FM_DELIM, *fm_lines, FM_DELIM, *new_body_lines]
        new_content = "\n".join(new_lines)
        if original.endswith("\n") and not new_content.endswith("\n"):
            new_content += "\n"

    if new_content == original:
        return False

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    # Post-apply: run fill to sync aliases[0] ↔ H1 and ensure H1.
    # Idempotent if already canonical.
    fill_file(path, vault_root, fallback_alias)

    return True


def reapply_file(
    path: str,
    vault_root: str,
    today: str,
    fallback_alias: str | None = None,
) -> bool:
    """Force-apply the folder-matched template, preserving captured content.

    Counterpart to apply_file for the promotion workflow (<leader>oM).
    Unlike --apply, --reapply does not honor the `## ` escape hatch:
    it rewrites the body's template sections even when the note
    already has `## ` headings.

    Behavior:
    - No frontmatter → fall back to apply_file (its branch 1).
    - Frontmatter present → split the body at the first `## Capture`
      heading. Content before the Capture (old template sections) is
      discarded; `## Capture` onward (user data) is preserved. If no
      `## Capture` exists, everything below H1 is wrapped in a new
      `## Capture`. Target template's body sections are inserted
      between H1 and the preserved/wrapped content.

    Idempotent: the `## Capture` block preserved on one run is
    preserved unchanged on the next, so repeated --reapply produces
    no further changes after the template is already the target's.

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

    # No frontmatter: full template application is exactly what we want.
    if fm_lines is None:
        return apply_file(path, vault_root, today, fallback_alias)

    body = lines[body_start:] if body_start > 0 else []

    folder_type = derive_folder_type(path, vault_root)
    template_path = os.path.join(vault_root, TEMPLATES_SUBDIR, f"{folder_type}.md") if folder_type else ""

    if not folder_type or not os.path.isfile(template_path):
        if folder_type and not os.path.isfile(template_path):
            print(f"[normalize] warning: template {template_path} not found; "
                  f"falling back to fill mode.", file=sys.stderr)
        return fill_file(path, vault_root, fallback_alias)

    with open(template_path, "r", encoding="utf-8") as fh:
        template_text = fh.read()

    stem = os.path.splitext(os.path.basename(path))[0]
    title = fallback_alias or stem
    substituted = substitute_placeholders(
        template_text, title=title, stem=stem, today=today
    )

    sub_lines = substituted.splitlines(keepends=False)
    _, sub_body_start = split_frontmatter(sub_lines)
    if sub_body_start > 0:
        tmpl_body_text = "\n".join(sub_lines[sub_body_start:])
    else:
        tmpl_body_text = substituted
    tmpl_sections = strip_template_h1(tmpl_body_text)

    # Locate H1.
    h1_idx = None
    for i, line in enumerate(body):
        if line.strip() == "":
            continue
        if H1_RE.match(line):
            h1_idx = i
        break

    if h1_idx is None:
        pre_h1: list[str] = []
        h1_line = f"# {title}"
        post_h1 = [ln for ln in body if ln.strip() != ""]
    else:
        pre_h1 = body[:h1_idx]
        h1_line = body[h1_idx]
        post_h1 = list(body[h1_idx + 1:])

    # Find the first `## Capture` below H1; everything from there onward
    # is preserved as user data.
    capture_idx = None
    for i, line in enumerate(post_h1):
        if line.strip() == "## Capture":
            capture_idx = i
            break

    if capture_idx is not None:
        preserved = list(post_h1[capture_idx:])
    else:
        trimmed = list(post_h1)
        while trimmed and trimmed[0].strip() == "":
            trimmed.pop(0)
        while trimmed and trimmed[-1].strip() == "":
            trimmed.pop()
        if trimmed:
            preserved = ["## Capture", ""] + trimmed
        else:
            preserved = []

    new_body_lines: list[str] = list(pre_h1) + [h1_line, ""]
    new_body_lines.extend(tmpl_sections.splitlines())
    if preserved:
        if new_body_lines and new_body_lines[-1].strip() != "":
            new_body_lines.append("")
        new_body_lines.extend(preserved)

    new_lines = [FM_DELIM, *fm_lines, FM_DELIM, *new_body_lines]
    new_content = "\n".join(new_lines)
    if original.endswith("\n") and not new_content.endswith("\n"):
        new_content += "\n"

    if new_content == original:
        return False

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    # Post-reapply: run fill to sync aliases[0] <-> H1 and canonicalize FM.
    fill_file(path, vault_root, fallback_alias)

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
    body = lines[body_start:] if body_start > 0 else []
    h1_title = extract_h1_title(body)

    for required in CANONICAL_ORDER:
        if required not in existing:
            issues.append(f"{path}: missing field '{required}'")

    # Catch unsubstituted template placeholders in any field value.
    placeholder_re = re.compile(r"\{\{[^}]*\}\}")
    for field_name, field_lines in existing.items():
        for line in field_lines:
            if placeholder_re.search(line):
                issues.append(
                    f"{path}: field '{field_name}' contains an unsubstituted "
                    f"placeholder (e.g. {{{{title}}}})"
                )
                break

    if "id" in existing:
        first = existing["id"][0]
        m = KEY_LINE_RE.match(first)
        value = m.group(2).strip() if m else ""
        unquoted = unquote_yaml(value)
        if unquoted != stem:
            issues.append(f"{path}: id '{unquoted}' does not match filename stem '{stem}'")

    if "aliases" in existing and not aliases_is_empty(existing["aliases"]):
        alias_values = extract_alias_values(existing["aliases"])
        if alias_values and h1_title and alias_values[0] != h1_title:
            issues.append(
                f"{path}: aliases[0] '{alias_values[0]}' does not match H1 '{h1_title}'"
            )

    return issues


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------


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
    group.add_argument("--reapply", action="store_true",
                       help="Force-apply folder-matched template, preserving "
                            "any `## Capture` block. Used by the <leader>oM "
                            "promotion orchestrator.")
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
                if fill_file(p, vault_root, args.fallback_alias):
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
        elif args.reapply:
            try:
                if reapply_file(p, vault_root, today, args.fallback_alias):
                    print(p)
                    changed += 1
            except OSError as exc:
                print(f"[normalize] error: {p}: {exc}", file=sys.stderr)
                return 1
        else:  # --check
            for issue in check_file(p, vault_root):
                print(issue, file=sys.stderr)
                issues_found += 1

    if (args.fill or args.apply or args.reapply) and changed > 0:
        print(f"[normalize] modified {changed} file(s).", file=sys.stderr)

    return 1 if issues_found > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
