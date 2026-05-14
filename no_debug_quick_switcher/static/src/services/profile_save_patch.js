/** @odoo-module **/
// Copyright 2026 Naim OUDAYET
// License LGPL-3

/**
 * Reverse-sync from My Profile to the live debug mode.
 *
 * Hooks into Odoo's post-save lifecycle (`FormController.prototype.onRecordSaved`)
 * and delegates the actual mode switch to `activateDebug` — full-page navigation
 * to `?debug=<value>`, the same primitive Odoo 17's Settings → Developer Tools
 * anchors use.
 *
 * Covers both edit paths to the user record:
 *   - My Profile menu (target="new" → ActionDialog → FormController)
 *   - Settings → Users & Companies → Users (full page → FormController)
 *
 * `changes` is the diff that was just persisted, so we know exactly when the
 * field was touched. We compare against `odoo.debug` (the global Odoo sets at
 * boot from the URL) to skip a needless reload when the value didn't actually
 * move — same source v17's res_config_dev_tool.js reads.
 */
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { activateDebug } from "../systray/debug_switcher";

patch(FormController.prototype, {
    async onRecordSaved(record, changes) {
        await super.onRecordSaved(record, changes);
        const userService = this.env.services.user;
        if (record.resModel !== "res.users" || record.resId !== userService.userId) {
            return;
        }
        if (!changes || !("x_debug_default_mode" in changes)) {
            return;
        }
        const newValue = changes.x_debug_default_mode || "";
        const currentValue = (typeof odoo !== "undefined" && odoo.debug) || "";
        if (String(newValue) === currentValue) {
            return;
        }
        activateDebug(newValue);
    },
});
