"""One-shot helper: fill empty msgstrs in the fresh .po exports with
language-specific translations, then write the result to the module's
i18n/ folder.

Run once after exporting fresh .po files from a running v19 instance.
Idempotent — re-running on an already-filled .po is a no-op.

Style choices per language follow the conventions established in the
previous committed .po files:
  * de/fr/nl: dev tech terms (Assets, Tests, A+T) stay English
  * es/pt_BR: native words (Recursos, Pruebas/Testes) but "Dev" stays
  * it: shortened native (Asset, Test, Svil) — singular convention
  * zh_CN: full native
  * ID: universal acronym, identical in every language
"""
import re
from pathlib import Path

FRESH = Path("N:/Apps/Debug-Mode-Quick-Switcher/.claude/fresh_po")
TARGET = Path("N:/Apps/Debug-Mode-Quick-Switcher/no_debug_quick_switcher/i18n")

TRANSLATIONS = {
    "de": {
        "A+T": "A+T",
        "Assets": "Assets",
        "Assets + Tests": "Assets + Tests",
        "ID": "ID",
        "Tests": "Tests",
        "Tests (QUnit / Hoot)": "Tests (QUnit / Hoot)",
    },
    "es": {
        "Assets + Tests": "Recursos + Pruebas",
        "Dev": "Dev",
        "ID": "ID",
        "Tests (QUnit / Hoot)": "Pruebas (QUnit / Hoot)",
    },
    "fr": {
        "A+T": "A+T",
        "Assets": "Assets",
        "Assets + Tests": "Assets + Tests",
        "ID": "ID",
        "Tests": "Tests",
        "Tests (QUnit / Hoot)": "Tests (QUnit / Hoot)",
    },
    "it": {
        "A+T": "A+T",
        "Assets + Tests": "Asset + Test",
        "ID": "ID",
        "Tests (QUnit / Hoot)": "Test (QUnit / Hoot)",
    },
    "nl": {
        "A+T": "A+T",
        "Assets": "Assets",
        "Assets + Tests": "Assets + Tests",
        "ID": "ID",
        "Tests": "Tests",
        "Tests (QUnit / Hoot)": "Tests (QUnit / Hoot)",
    },
    "pt_BR": {
        "Assets + Tests": "Recursos + Testes",
        "Dev": "Dev",
        "ID": "ID",
        "Tests (QUnit / Hoot)": "Testes (QUnit / Hoot)",
    },
    "zh_CN": {
        "Assets + Tests": "资源 + 测试",
        "ID": "ID",
    },
    "ar": {},  # already complete; written for completeness
}


def fill_po(src: Path, dst: Path, mapping: dict[str, str]) -> tuple[int, int]:
    """Read src .po, replace empty msgstrs for any msgid in mapping,
    write to dst. Returns (filled, kept_empty)."""
    text = src.read_text(encoding="utf-8")
    filled = 0
    for msgid, msgstr in mapping.items():
        # Match: msgid "X"\nmsgstr ""\n  (empty only — never overwrite existing)
        # Escape msgid for regex literal match.
        pattern = re.compile(
            rf'(^msgid "{re.escape(msgid)}"\n)msgstr ""\n', re.MULTILINE
        )
        new_text, n = pattern.subn(rf'\1msgstr "{msgstr}"\n', text)
        if n:
            text = new_text
            filled += n
    dst.write_text(text, encoding="utf-8")
    # count remaining empties (excluding the header)
    empties = re.findall(r'^msgid "[^"\n]+"\nmsgstr ""$', text, re.MULTILINE)
    return filled, len(empties)


for lang, mapping in TRANSLATIONS.items():
    src = FRESH / f"fresh_{lang}.po"
    dst = TARGET / f"{lang}.po"
    if not src.exists():
        print(f"  skip {lang}: {src} not found")
        continue
    filled, remaining_empty = fill_po(src, dst, mapping)
    status = "OK" if remaining_empty == 0 else f"WARN ({remaining_empty} still empty)"
    print(f"  {lang}: filled={filled}, still_empty={remaining_empty} {status}")

# POT too — leave empty msgstrs everywhere (that's normal for a template)
pot_src = FRESH / "fresh.pot"
pot_dst = TARGET / "no_debug_quick_switcher.pot"
pot_dst.write_text(pot_src.read_text(encoding="utf-8"), encoding="utf-8")
print(f"  pot: copied {pot_src.name} -> {pot_dst.name}")
