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
            ("", "Off"),
            ("1", "Developer"),
            ("assets", "Assets"),
            ("tests", "Tests"),
            ("assets,tests", "Assets + Tests"),
        ],
        string="Default Debug Mode",
        default="",
        # Odoo 20: each user reads and saves this on their own record (19 used
        # the SELF_READABLE_FIELDS / SELF_WRITEABLE_FIELDS properties, gone on 20).
        user_writeable=True,
        # Labels deliberately kept short so they match the navbar systray
        # dropdown exactly (it uses the same five _t() strings). The help
        # text stays unchanged from the previous release so existing
        # translations don't break.
        help="Starting debug mode whenever you log in. Off by default. The "
        "switcher in the navbar will land on this mode automatically — "
        "no more typing ?debug=assets in the URL bar 30 times a day.",
    )
