"""Replace the stale long-form msgstr on short msgids (v18-specific).

v18's --i18n-export merged Selection-references into JS-code references
under a single short msgid (e.g. "Tests"), but inherited the OLD
long-form translation as the msgstr (e.g. "Tests (QUnit / Hoot)").

We swap them for the canonical short translations — pulled directly
from the v19-committed .po files where the same short msgids carry the
correct short translations.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path("N:/Apps/Debug-Mode-Quick-Switcher")
I18N = ROOT / "no_debug_quick_switcher" / "i18n"

# Canonical short translations per language. Mirrors what's already
# committed on 19.0-dev's .po files for the same short msgids.
SHORT_TRANSLATIONS = {
    "ar.po": {
        "Off": "متوقف",
        "Developer": "مطوّر",
        "Assets": "أصول",
        "Tests": "اختبارات",
    },
    "de.po": {
        "Off": "Aus",
        "Developer": "Entwickler",
        "Assets": "Ressourcen",
        "Tests": "Tests",
    },
    "es.po": {
        "Off": "Desactivado",
        "Developer": "Desarrollador",
        "Assets": "Recursos",
        "Tests": "Pruebas",
    },
    "fr.po": {
        "Off": "Désactivé",
        "Developer": "Développeur",
        "Assets": "Ressources",
        "Tests": "Tests",
    },
    "it.po": {
        "Off": "Disattivato",
        "Developer": "Sviluppatore",
        "Assets": "Asset",
        "Tests": "Test",
    },
    "nl.po": {
        "Off": "Uit",
        "Developer": "Ontwikkelaar",
        "Assets": "Bronbestanden",
        "Tests": "Testen",
    },
    "pt_BR.po": {
        "Off": "Desativado",
        "Developer": "Desenvolvedor",
        "Assets": "Recursos",
        "Tests": "Testes",
    },
    "zh_CN.po": {
        "Off": "关闭",
        "Developer": "开发者",
        "Assets": "资源",
        "Tests": "测试",
    },
}


def replace_msgstr(text: str, msgid: str, new_msgstr: str) -> tuple[str, int]:
    pattern = re.compile(
        rf'(^msgid "{re.escape(msgid)}"\n)msgstr "[^"]*"\n',
        re.MULTILINE,
    )
    return pattern.subn(rf'\1msgstr "{new_msgstr}"\n', text)


for fname, mapping in SHORT_TRANSLATIONS.items():
    path = I18N / fname
    text = path.read_text(encoding="utf-8")
    fixed = 0
    for msgid, msgstr in mapping.items():
        text, n = replace_msgstr(text, msgid, msgstr)
        fixed += n
    path.write_text(text, encoding="utf-8")
    print(f"  {fname}: fixed {fixed} short msgids")
