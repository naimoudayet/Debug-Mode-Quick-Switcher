# Copyright 2026 Naim OUDAYET
# License LGPL-3
"""Python-side coverage for Debug Mode Quick Switcher (in-process).

These tests run in a plain TransactionCase — no HTTP, no browser. The
ir.http.session_info override is exercised separately in test_session_info.py
because it reads the Werkzeug request object, which only exists during
a real HTTP request cycle.

Note on Selection field semantics: Odoo represents an unset / empty
Selection value as Python `False` when reading back, regardless of
whether the column literally stores `""`. We therefore assert
falsy / truthy rather than `== ""`.
"""
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "no_debug_quick_switcher")
class TestDebugSwitcherModels(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = cls.env["res.users"].create({
            "name": "Debug Switcher Test User",
            "login": "debug_switcher_test_user",
        })
        cls.IrConfig = cls.env["ir.config_parameter"].sudo()
        cls.KILLSWITCH_KEY = "no_debug_quick_switcher.disabled"

    # ------------------------------------------------------------------
    # res.users.x_debug_default_mode
    # ------------------------------------------------------------------
    def test_default_value_is_off(self):
        """Brand-new users should not boot into a debug mode."""
        # Odoo coerces an empty Selection value to Python False on read.
        self.assertFalse(self.test_user.x_debug_default_mode)

    def test_all_five_selection_values_accepted(self):
        """The 5 Selection literals match Odoo's `?debug=` parameter values
        verbatim — no mapping layer between them and the URL."""
        # Empty string maps to falsy on read-back (Selection field semantic).
        self.test_user.x_debug_default_mode = ""
        self.test_user.invalidate_recordset()
        self.assertFalse(self.test_user.x_debug_default_mode)

        # Non-empty values round-trip exactly.
        for value in ("1", "assets", "tests", "assets,tests"):
            self.test_user.x_debug_default_mode = value
            self.test_user.invalidate_recordset()
            self.assertEqual(
                self.test_user.x_debug_default_mode,
                value,
                f"Selection value {value!r} did not persist",
            )

    def test_field_in_self_readable(self):
        """Users must be able to read their own preference (My Profile)."""
        self.assertIn(
            "x_debug_default_mode",
            self.test_user.SELF_READABLE_FIELDS,
        )

    def test_field_in_self_writeable(self):
        """Users must be able to write their own preference (My Profile)."""
        self.assertIn(
            "x_debug_default_mode",
            self.test_user.SELF_WRITEABLE_FIELDS,
        )

    def test_users_can_write_own_preference(self):
        """End-to-end: the user record itself, acting as itself, can save."""
        self.test_user.with_user(self.test_user).write({
            "x_debug_default_mode": "assets",
        })
        self.test_user.invalidate_recordset()
        self.assertEqual(self.test_user.x_debug_default_mode, "assets")

    # ------------------------------------------------------------------
    # res.config.settings.x_debug_switcher_disabled  →  ir.config_parameter
    # ------------------------------------------------------------------
    def test_killswitch_default_is_off(self):
        """Fresh installs must NOT hide the switcher — defaulting to 'off'
        keeps the module visible on dev DBs out of the box."""
        self.IrConfig.search([("key", "=", self.KILLSWITCH_KEY)]).unlink()
        settings = self.env["res.config.settings"].create({})
        self.assertFalse(settings.x_debug_switcher_disabled)

    def test_killswitch_round_trips_through_config_parameter(self):
        """Saving from Settings UI → row in ir.config_parameter;
        re-reading the Settings → same value."""
        settings = self.env["res.config.settings"].create({
            "x_debug_switcher_disabled": True,
        })
        settings.execute()
        stored = self.IrConfig.get_param(self.KILLSWITCH_KEY, "")
        self.assertEqual(stored, "True")

        # Flip back to False and confirm round-trip.
        settings = self.env["res.config.settings"].create({
            "x_debug_switcher_disabled": False,
        })
        settings.execute()
        stored = self.IrConfig.get_param(self.KILLSWITCH_KEY, "")
        # When unset/false, value is either missing or literal "False"
        self.assertIn(stored, ("False", "", False))
