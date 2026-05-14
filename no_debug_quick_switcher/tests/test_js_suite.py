# Copyright 2026 Naim OUDAYET
# License LGPL-3
"""Hoot-suite runner.

Spins headless Chromium, runs every spec under static/tests/ via Odoo's
canonical /web/tests endpoint, and reports results back through Odoo's
standard test plumbing. Tagged so it can be opted into with
`--test-tags no_debug_quick_switcher_js`.
"""
import odoo.tests
from odoo.tests import HttpCase


@odoo.tests.tagged("post_install", "-at_install", "no_debug_quick_switcher_js")
class DebugSwitcherJsSuite(HttpCase):
    """Runs the Hoot specs scoped to this module only — not the full Odoo
    Hoot suite, which would take ~30 minutes."""

    @odoo.tests.no_retry
    def test_js_suite(self):
        self.browser_js(
            "/web/tests?headless&loglevel=2&preset=desktop&timeout=30000"
            "&filter=no_debug_quick_switcher",
            "",
            "",
            login="admin",
            timeout=300,
            success_signal="[HOOT] Test suite succeeded",
        )
