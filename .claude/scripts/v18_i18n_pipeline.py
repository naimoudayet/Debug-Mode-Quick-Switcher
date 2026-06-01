"""Single-pass i18n pipeline for v18.

Differences vs the v19 pipeline:
  * v18's --i18n-export ALREADY merges identical msgids across reference
    types, so the Selection-references are baked into the same blocks
    as the JS code: references. No unify_selection_labels step needed.
  * v18 still drops the three manifest_meta entries on export, so we
    splice them back in from the committed .po.
  * v18 includes only 3 of the 5 auto-generated inherited-model
    msgids (User, HTTP Routing, Config Settings) — we strip them all
    the same.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path("N:/Apps/Debug-Mode-Quick-Switcher")
FRESH = ROOT / ".claude" / "fresh_po_v18"
I18N = ROOT / "no_debug_quick_switcher" / "i18n"
BRANCH = "18.0-dev"

# Identical to the v19 mapping — same target translations, same convention.
TRANSLATIONS = {
    "de.po": {
        "A+T": "R+T",
        "Assets + Tests": "Ressourcen + Tests",
    },
    "es.po": {
        "Assets + Tests": "Recursos + Pruebas",
        "Dev": "Desar",
    },
    "fr.po": {
        "A+T": "R+T",
        "Assets + Tests": "Ressources + Tests",
    },
    "it.po": {
        "A+T": "A+T",
        "Assets + Tests": "Asset + Test",
    },
    "nl.po": {
        "A+T": "B+T",
        "Assets + Tests": "Bronbestanden + Testen",
    },
    "pt_BR.po": {
        "Assets + Tests": "Recursos + Testes",
        "Dev": "Desenv",
    },
    "zh_CN.po": {
        "Assets + Tests": "资源 + 测试",
    },
    "ar.po": {},
}

AUTO_STRINGS_TO_STRIP = {
    "Config Settings", "Display Name", "HTTP Routing", "ID", "User",
}

META_REF_PATTERN = re.compile(
    r"#: model:ir\.module\.module,(?:shortdesc|summary|description):"
    r"no_debug_quick_switcher\.module_meta_information"
)


def git_show(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{BRANCH}:{rel}"],
        text=True, encoding="utf-8",
    )


def fill_empty(text: str, mapping: dict[str, str]) -> int:
    """Replace empty msgstr that follows a known msgid. Returns count."""
    n_total = 0
    for msgid, msgstr in mapping.items():
        pattern = re.compile(
            rf'(^msgid "{re.escape(msgid)}"\n)msgstr ""\n', re.MULTILINE
        )
        text, n = pattern.subn(rf'\1msgstr "{msgstr}"\n', text)
        n_total += n
    return text, n_total


def split_blocks(text: str) -> list[str]:
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
    lines = block.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("msgid "):
            single = re.match(r'^msgid "(.*)"$', line)
            if single and single.group(1) != "":
                return single.group(1)
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


def process_one(committed_text: str, fresh_text: str, mapping: dict[str, str]) -> tuple[str, dict]:
    """Apply mapping fills → strip auto-strings → append manifest_meta blocks."""
    stats = {"filled": 0, "stripped": 0, "meta_added": 0}

    # 1. Fill empty msgstrs from mapping.
    fresh_text, stats["filled"] = fill_empty(fresh_text, mapping)

    # 2. Split into blocks, strip auto-strings.
    fresh_blocks = split_blocks(fresh_text)
    kept = []
    for b in fresh_blocks:
        mid = block_msgid(b)
        if mid in AUTO_STRINGS_TO_STRIP:
            stats["stripped"] += 1
            continue
        kept.append(b)

    # 3. Extract manifest_meta blocks from committed, append to kept.
    committed_blocks = split_blocks(committed_text)
    meta_blocks = [b for b in committed_blocks if is_manifest_meta(b)]
    stats["meta_added"] = len(meta_blocks)

    # Don't double-add if any already present (defensive).
    kept_no_meta = [b for b in kept if not is_manifest_meta(b)]
    return "".join(kept_no_meta + meta_blocks), stats


# Process each .po
for fname, mapping in TRANSLATIONS.items():
    target = I18N / fname
    fresh = FRESH / f"fresh_{fname.replace('.po', '')}.po"
    if not fresh.exists():
        # naming convention: fresh_ar.po, fresh_pt_BR.po, fresh_zh_CN.po — names already match
        print(f"  skip {fname}: {fresh} not found")
        continue
    committed = git_show(target)
    merged, stats = process_one(committed, fresh.read_text(encoding="utf-8"), mapping)
    target.write_text(merged, encoding="utf-8")
    msgid_count = sum(1 for b in split_blocks(merged) if block_msgid(b))
    print(f"  {fname:14s} filled={stats['filled']:2d} stripped={stats['stripped']:2d} "
          f"meta_added={stats['meta_added']:2d} -> {msgid_count} msgids")

# Process POT
pot_target = I18N / "no_debug_quick_switcher.pot"
pot_fresh = FRESH / "fresh.pot"
committed_pot = git_show(pot_target)
merged_pot, stats = process_one(committed_pot, pot_fresh.read_text(encoding="utf-8"), {})
pot_target.write_text(merged_pot, encoding="utf-8")
msgid_count = sum(1 for b in split_blocks(merged_pot) if block_msgid(b))
print(f"  {'POT':14s} filled={stats['filled']:2d} stripped={stats['stripped']:2d} "
      f"meta_added={stats['meta_added']:2d} -> {msgid_count} msgids")
