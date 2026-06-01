"""Final i18n merge step.

The v19 `odoo i18n export` subcommand has two quirks vs the canonical
.po set we want for the App Store:

  (1) It ADDS five inherited-model auto-strings to the .po:
        Config Settings, Display Name, HTTP Routing, ID, User
      These collide with core Odoo's translations under the flat-dict
      last-write-wins merge (see memory feedback_odoo_translation_collision).
      We strip them out — core handles those for us.

  (2) It SKIPS the three manifest-meta strings entirely:
        ir.module.module,shortdesc/summary/description
      Those need to come back in or the module name / summary /
      description stay English in every other language on the App Store.

This script reads the committed .po (which had the manifest-meta with
hand-quality translations) plus the current on-disk .po (which has the
expanded msgid set), produces the merged final, and writes it back.

Both files are POT-syntax — we manipulate them as block-structured text,
not via msgmerge, because we only need surgical edits.

Idempotent: re-running on already-cleaned files is a no-op.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path("N:/Apps/Debug-Mode-Quick-Switcher")
I18N = ROOT / "no_debug_quick_switcher" / "i18n"
BRANCH = "19.0-dev"

# msgids to strip from the .po files (inherited-model auto-strings).
AUTO_STRINGS_TO_STRIP = {
    "Config Settings",
    "Display Name",
    "HTTP Routing",
    "ID",
    "User",
}

# The three manifest_meta msgids we need from the committed files.
META_REF_PATTERN = re.compile(
    r"#: model:ir\.module\.module,(?:shortdesc|summary|description):"
    r"no_debug_quick_switcher\.module_meta_information"
)


def git_show(path: Path) -> str:
    """Read a file from the branch tip in git (not the working tree)."""
    rel = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{BRANCH}:{rel}"],
        text=True,
        encoding="utf-8",
    )


def split_blocks(text: str) -> list[str]:
    """Split a .po body into entry blocks — one block per msgid (blank-line
    separated) — plus the leading header block. Blank line stays at the
    end of each block."""
    # Header is everything up to and including the first blank line.
    # Subsequent blocks are blank-line separated.
    # We keep trailing "\n\n" on each so re-joining is a no-op.
    blocks = []
    current = []
    for line in text.splitlines(keepends=True):
        current.append(line)
        if line.strip() == "":
            blocks.append("".join(current))
            current = []
    if current:
        blocks.append("".join(current))
    return blocks


def block_msgid(block: str) -> str | None:
    """Extract the bare msgid string from a block. Handles single-line and
    multi-line msgid (which starts with msgid "" then continuation lines
    of "..." form)."""
    lines = block.splitlines()
    # Find the msgid line
    for i, line in enumerate(lines):
        if line.startswith("msgid "):
            # Single line: msgid "value"
            single = re.match(r'^msgid "(.*)"$', line)
            if single and single.group(1) != "":
                return single.group(1)
            # Multi-line: msgid "" followed by continuation lines
            if line.strip() == 'msgid ""':
                parts = []
                for j in range(i + 1, len(lines)):
                    cont = re.match(r'^"(.*)"$', lines[j])
                    if not cont:
                        break
                    parts.append(cont.group(1))
                if parts:
                    return "".join(parts)
            break
    return None


def is_manifest_meta(block: str) -> bool:
    return bool(META_REF_PATTERN.search(block))


def is_header(block: str) -> bool:
    # The header has 'msgid ""' followed by 'msgstr ""' and Project-Id-Version etc.
    # The simplest signal: it's the FIRST block; or it contains 'Project-Id-Version'.
    return "Project-Id-Version" in block


def merge_one(committed_text: str, fresh_text: str) -> str:
    """Take committed (has manifest_meta) + fresh (has expanded msgid set,
    no manifest_meta, has auto-strings). Produce final: fresh without
    auto-strings, plus committed's manifest_meta blocks appended after
    the existing entries."""
    committed_blocks = split_blocks(committed_text)
    fresh_blocks = split_blocks(fresh_text)

    # 1. Filter fresh to drop auto-strings.
    kept = []
    for block in fresh_blocks:
        mid = block_msgid(block)
        if mid in AUTO_STRINGS_TO_STRIP:
            continue
        kept.append(block)

    # 2. Extract manifest_meta blocks from committed.
    meta_blocks = [b for b in committed_blocks if is_manifest_meta(b)]

    # 3. Make sure kept doesn't already have any manifest_meta (defensive).
    kept_filtered = [b for b in kept if not is_manifest_meta(b)]

    return "".join(kept_filtered + meta_blocks)


PO_FILES = ["ar.po", "de.po", "es.po", "fr.po", "it.po", "nl.po", "pt_BR.po", "zh_CN.po"]

for name in PO_FILES + ["no_debug_quick_switcher.pot"]:
    target = I18N / name
    committed = git_show(target)
    fresh = target.read_text(encoding="utf-8")
    merged = merge_one(committed, fresh)
    target.write_text(merged, encoding="utf-8")

    # Sanity stats
    blocks = split_blocks(merged)
    msgids = [b for b in blocks if block_msgid(b)]
    print(f"  {name}: {len(msgids)} msgids (incl. 3 manifest_meta)")
