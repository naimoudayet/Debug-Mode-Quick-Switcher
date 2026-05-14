# Copyright 2026 Naim OUDAYET
# License LGPL-3
"""Coverage for the ir.http.session_info() override.

Runs as HttpCase because core's session_info() reads
`request.session.uid`, which only exists during a real HTTP request.

We verify the override CONTRACT — that our two extra keys appear in
the JSON payload with the expected types — not their dynamic values.
Value round-trips are already covered at the model level in
test_models.py; testing them again here would be testing Odoo's own
read machinery, not our code, and runs into HttpCase cross-cursor
visibility quirks.
"""
import json

import odoo.tests
from odoo.tests import HttpCase


@odoo.tests.tagged("post_install", "-at_install", "no_debug_quick_switcher")
class TestSessionInfoOverride(HttpCase):
    def _read_session_info(self):
        """Hit Odoo's public session payload endpoint and parse the JSON."""
        self.authenticate("admin", "admin")
        resp = self.url_open(
            "/web/session/get_session_info",
            data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": {}}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()
        self.assertNotIn("error", body, body)
        return body["result"]

    def test_default_mode_key_is_present(self):
        """OWL boot reads session.x_debug_default_mode synchronously —
        the key must always be present in the payload (the value is
        empty string when unset; non-empty otherwise)."""
        result = self._read_session_info()
        self.assertIn("x_debug_default_mode", result)
        # An unset preference must serialize as empty string, not False —
        # the JS `session.x_debug_default_mode || ""` check depends on it.
        self.assertIsInstance(result["x_debug_default_mode"], str)

    def test_killswitch_key_is_present(self):
        """Bootstrap service reads session.x_debug_switcher_disabled
        before registering hotkeys — the key must always be present
        as a Python bool (not None / missing)."""
        result = self._read_session_info()
        self.assertIn("x_debug_switcher_disabled", result)
        self.assertIsInstance(result["x_debug_switcher_disabled"], bool)
