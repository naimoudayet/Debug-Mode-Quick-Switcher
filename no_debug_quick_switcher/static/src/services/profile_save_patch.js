/** @odoo-module **/
// Copyright 2026 Naim OUDAYET
// License LGPL-3

/**
 * Reverse-sync from My Profile to the live debug mode.
 *
 * Hooks into Odoo's post-save lifecycle (`FormController.prototype.onRecordSaved`)
 * and delegates the actual mode switch to `activateDebug` — which just
 * navigates to the same URL with the new `?debug=` value and reloads. Same
 * canonical `?debug=` mechanism Odoo's Settings page uses.
 *
 * Covers both edit paths to the user record:
 *   - My Profile menu (target="new" → ActionDialog → FormController)
 *   - Settings → Users & Companies → Users (full page → FormController)
 *
 * `changes` is the diff that was just persisted, so we know exactly when the
 * field was touched. We compare against the current URL's debug param to skip
 * a needless reload when the value didn't actually move.
 */
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { activateDebug } from "../systray/debug_switcher";

function currentDebugFromUrl() {
    const raw = new URLSearchParams(window.location.search).get("debug");
    return raw === null ? 0 : raw === "" || raw === "0" ? 0 : raw;
}

patch(FormController.prototype, {
    async onRecordSaved(record, changes) {
        await super.onRecordSaved(record, changes);
        if (record.resModel !== "res.users") {
            return;
        }
        // Use env.services.user — works on both v16/v17 (where there's no
        // singleton import) and v18+ (where there is one).
        const userId = this.env.services.user.userId;
        if (record.resId !== userId) {
            return;
        }
        if (!changes || !("x_debug_default_mode" in changes)) {
            return;
        }
        const newValue = changes.x_debug_default_mode || 0;
        const currentNorm = currentDebugFromUrl();
        if (String(newValue) === String(currentNorm)) {
            return;
        }
        activateDebug(newValue);
    },
});
