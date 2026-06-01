"""Translate the last identity-mapped msgstrs into proper native words.

After the regen + merge passes, six msgstrs across de/fr/nl/es/pt_BR
were still rendering identical to their English msgid. The user's
explicit ask was "make all strings translated to languages", so we
swap them for the most idiomatic native term, with one principled
exception:

  "Tests" / "Tests (QUnit / Hoot)" stays "Tests" in German + French
  because that IS the genuine German/French dev term (loanword, in
  Duden / Le Petit Robert, used by Odoo core's own translations).
  Dutch by contrast properly uses "Testen", so we DO swap there.
"""
import re
from pathlib import Path

I18N = Path("N:/Apps/Debug-Mode-Quick-Switcher/no_debug_quick_switcher/i18n")

# Per-language, per-msgid replacement.
# Only entries that need fixing — anything not listed here keeps its current value.
PATCHES: dict[str, dict[str, str]] = {
    "de.po": {
        "A+T": "R+T",
        "Assets": "Ressourcen",
        "Assets + Tests": "Ressourcen + Tests",
        # Tests / Tests (QUnit / Hoot): keep "Tests" — proper German loanword.
    },
    "fr.po": {
        "A+T": "R+T",
        "Assets": "Ressources",
        "Assets + Tests": "Ressources + Tests",
        # Tests / Tests (QUnit / Hoot): keep "Tests" — proper French loanword.
    },
    "nl.po": {
        "A+T": "B+T",
        "Assets": "Bronbestanden",
        "Assets + Tests": "Bronbestanden + Testen",
        "Tests": "Testen",
        "Tests (QUnit / Hoot)": "Testen (QUnit / Hoot)",
    },
    "es.po": {
        "Dev": "Desar",
    },
    "pt_BR.po": {
        "Dev": "Desenv",
    },
}


def replace_msgstr(text: str, msgid: str, new_msgstr: str) -> tuple[str, int]:
    """Replace the msgstr that follows `msgid "<msgid>"`. Only touches
    single-line msgid form. Returns (new_text, n_replacements)."""
    pattern = re.compile(
        rf'(^msgid "{re.escape(msgid)}"\n)msgstr "[^"]*"\n',
        re.MULTILINE,
    )
    return pattern.subn(rf'\1msgstr "{new_msgstr}"\n', text)


for fname, mapping in PATCHES.items():
    path = I18N / fname
    text = path.read_text(encoding="utf-8")
    for msgid, new in mapping.items():
        text, n = replace_msgstr(text, msgid, new)
        marker = "OK" if n == 1 else f"WARN (n={n})"
        print(f"  {fname}: {msgid!r:35s} -> {new!r:25s} {marker}")
    path.write_text(text, encoding="utf-8")
