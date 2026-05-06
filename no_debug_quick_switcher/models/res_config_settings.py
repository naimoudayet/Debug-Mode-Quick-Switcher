# Copyright 2026 Naim OUDAYET
# License LGPL-3
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Master switch for production databases. Stored as ir.config_parameter so
    # it persists across server restarts and is read at request-time.
    x_debug_switcher_disabled = fields.Boolean(
        string="Disable Debug Switcher in Production",
        config_parameter="no_debug_quick_switcher.disabled",
        help="When enabled, the navbar switcher hides and the per-user default "
             "is ignored. Recommended ON for production databases — it keeps "
             "users from accidentally landing in Tests mode (which slows page "
             "loads dramatically by loading QUnit assets).",
    )
