# Copyright 2026 Naim OUDAYET
# License LGPL-3
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # x_ prefix per the portfolio convention for fields added to existing models.
    # Selection values match Odoo's `?debug=` URL parameter literals so we can
    # plug them straight into the switcher's navigation logic without mapping.
    x_debug_default_mode = fields.Selection(
        selection=[
            ("", "Off (no debug)"),
            ("1", "Developer Mode"),
            ("assets", "Assets (non-minified JS)"),
            ("tests", "Tests (QUnit / Hoot)"),
            ("assets,tests", "Assets + Tests"),
        ],
        string="Default Debug Mode",
        default="",
        help="Starting debug mode whenever you log in. Off by default. The "
             "switcher in the navbar will land on this mode automatically — "
             "no more typing ?debug=assets in the URL bar 30 times a day.",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["x_debug_default_mode"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["x_debug_default_mode"]
