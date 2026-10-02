# Copyright 2026 Naim OUDAYET
# License LGPL-3
"""The page-edge stripe needs <body data-debug="..."> in a heavy mode.

Odoo 16 starts the web client's services before the document body exists, so
the service that sets the attribute must wait for the DOM; setting it at once
failed silently and the stripe never showed.
"""
import odoo.tests
from odoo.tests import HttpCase


@odoo.tests.tagged("post_install", "-at_install", "no_debug_quick_switcher")
class TestPageEdgeStripe(HttpCase):
    def test_assets_mode_marks_the_body_for_the_stripe(self):
        self.browser_js(
            "/web?debug=assets",
            "const v = document.body.dataset.debug;"
            "if (v === 'assets') { console.log('test successful'); }"
            "else { console.error('body data-debug is ' + v + ', expected assets'); }",
            "odoo.isReady === true",
            login="admin",
            timeout=180,
        )
