"""Unify Selection-field labels with JS labels in every .po file.

After shortening the Python Selection labels (Off (no debug) -> Off, etc.)
the .po files still carry two separate entries per mode:

  #: model:ir.model.fields.selection,name:...x_debug_default_mode__<KEY>
  msgid "Off (no debug)"                <-- old long form, now orphan
  msgstr "Aus (kein Debug)"

  #: code:addons/.../debug_switcher.js:0
  msgid "Off"                            <-- correct short form
  msgstr "Aus"

We merge them into one entry with both references and the short msgid +
short msgstr, so:
  - The user form Selection picks the SAME translated text as the navbar
    dropdown (both surfaces now resolve through the same msgid).
  - The orphan long-form msgid disappears.

POT gets the same treatment (msgstr stays empty in POT).
"""
import re
from pathlib import Path

I18N = Path("N:/Apps/Debug-Mode-Quick-Switcher/no_debug_quick_switcher/i18n")

# Mapping: long-form msgid -> short-form msgid the JS _t() uses.
# Once unified, both surfaces translate via the short msgid.
LONG_TO_SHORT = {
    "Off (no debug)": "Off",
    "Developer Mode": "Developer",
    "Assets (non-minified JS)": "Assets",
    "Tests (QUnit / Hoot)": "Tests",
    # "Assets + Tests" was already identical in both surfaces, no change
}

# Selection xmlids per short msgid — used to build the merged reference.
SELECTION_XMLID = {
    "Off": "selection__res_users__x_debug_default_mode__",
    "Developer": "selection__res_users__x_debug_default_mode__1",
    "Assets": "selection__res_users__x_debug_default_mode__assets",
    "Tests": "selection__res_users__x_debug_default_mode__tests",
}


def parse_blocks(text: str) -> tuple[str, list[dict]]:
    """Split a .po into (header, [blocks]). Each block is
        {comments, refs, msgid, msgstr, raw}
    where `raw` is the original text (so we can rewrite faithfully).
    Blocks are separated by blank lines.
    """
    parts = text.split("\n\n")
    if not parts:
        return "", []
    header = parts[0]
    blocks = []
    for raw in parts[1:]:
        if not raw.strip():
            continue
        # Extract msgid (single-line form)
        m_msgid = re.search(r'^msgid "(.*)"$', raw, re.MULTILINE)
        if not m_msgid:
            # multi-line msgid (manifest description) — skip parsing, keep raw
            blocks.append({"msgid": None, "raw": raw})
            continue
        msgid = m_msgid.group(1)
        # Extract all reference lines (#: ...)
        refs = re.findall(r"^#: .*$", raw, re.MULTILINE)
        blocks.append({"msgid": msgid, "raw": raw, "refs": refs})
    return header, blocks


def serialize(header: str, blocks: list[dict]) -> str:
    parts = [header] + [b["raw"] for b in blocks]
    return "\n\n".join(parts) + "\n"


def unify_one(text: str) -> tuple[str, int]:
    """Returns (new_text, n_merges)."""
    header, blocks = parse_blocks(text)
    by_msgid: dict[str, dict] = {b["msgid"]: b for b in blocks if b.get("msgid")}
    merges = 0

    for long_msgid, short_msgid in LONG_TO_SHORT.items():
        long_block = by_msgid.get(long_msgid)
        short_block = by_msgid.get(short_msgid)
        if not long_block or not short_block:
            continue
        xmlid = SELECTION_XMLID[short_msgid]
        new_ref = f"#: model:ir.model.fields.selection,name:no_debug_quick_switcher.{xmlid}"
        # Add the Selection reference to the short block (right after the
        # last existing reference line).
        short_raw = short_block["raw"]
        # Append the new reference line to whatever ref lines already exist.
        # Pattern: find the last #: line and insert ours after it.
        ref_lines = re.findall(r"^#: .*$", short_raw, re.MULTILINE)
        if new_ref not in ref_lines:
            last_ref = ref_lines[-1]
            short_block["raw"] = short_raw.replace(
                last_ref, f"{last_ref}\n{new_ref}", 1
            )
        # Remove the long block.
        blocks.remove(long_block)
        merges += 1

    return serialize(header, blocks), merges


PO_FILES = ["ar.po", "de.po", "es.po", "fr.po", "it.po", "nl.po", "pt_BR.po", "zh_CN.po",
            "no_debug_quick_switcher.pot"]

for name in PO_FILES:
    path = I18N / name
    text = path.read_text(encoding="utf-8")
    new_text, n = unify_one(text)
    path.write_text(new_text, encoding="utf-8")
    print(f"  {name}: merged {n} long-form msgids into short-form entries")
