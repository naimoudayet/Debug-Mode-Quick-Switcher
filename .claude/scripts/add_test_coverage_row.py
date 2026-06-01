"""Insert a 'Test Coverage' row into the Technical Details table.

Adds the row just before the existing 'Languages' row, with consistent
styling. Idempotent — refuses to insert if the row is already present.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path("N:/Apps/Debug-Mode-Quick-Switcher")
TARGET_REL = "no_debug_quick_switcher/static/description/index.html"
TARGET = ROOT / TARGET_REL

# The existing "Languages" row uses the closing-row style (no border-bottom
# attribute on the <tr>). We insert OUR row WITH border-bottom (since it's
# now no longer the last row) and bump Languages's <tr> to keep its style
# unchanged (it's still the closing row → no border-bottom).
ANCHOR = (
    '                    <tr>\n'
    '                        <td style="padding: 12px;"><strong style="color: #714B67;">Languages</strong></td>\n'
)

NEW_ROW = (
    '                    <tr style="border-bottom: 1px solid #E8DDE5;">\n'
    '                        <td style="padding: 12px;"><strong style="color: #714B67;">Test Coverage</strong></td>\n'
    '                        <td style="padding: 12px; color: #475569;">9 Python tests + 13 Hoot specs &mdash; run with <em>--test-tags=no_debug_quick_switcher</em> / <em>_js</em></td>\n'
    '                    </tr>\n'
)


def patch(text: str) -> str:
    if "Test Coverage" in text:
        return text  # already patched, no-op
    return text.replace(ANCHOR, NEW_ROW + ANCHOR, 1)


# Determine current branch
branch = subprocess.check_output(
    ["git", "-C", str(ROOT), "branch", "--show-current"],
    text=True,
).strip()
print(f"  on branch: {branch}")

text = TARGET.read_text(encoding="utf-8")
new_text = patch(text)
if new_text == text:
    print(f"  no-op: row already present (or anchor not found)")
    sys.exit(0)
TARGET.write_text(new_text, encoding="utf-8")
print(f"  inserted 'Test Coverage' row")
