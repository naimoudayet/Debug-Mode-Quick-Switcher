# Copyright 2026 Naim OUDAYET
# License LGPL-3
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """Expose the user's default-mode preference + the global production
        kill-switch so the OWL component can read both synchronously at boot
        without an extra RPC.
        """
        result = super().session_info()
        params = self.env["ir.config_parameter"].sudo()
        result["x_debug_default_mode"] = self.env.user.x_debug_default_mode or ""
        result["x_debug_switcher_disabled"] = bool(
            params.get_param("no_debug_quick_switcher.disabled", False)
        )
        return result
