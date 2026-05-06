/** @odoo-module **/
// Copyright 2026 Naim OUDAYET
// License LGPL-3

/**
 * Reverse-sync from My Profile to the live debug mode.
 *
 * Hooks into Odoo's post-save lifecycle (`FormController.prototype.onRecordSaved`)
 * and delegates the actual mode switch to `activateDebug` — our thin wrapper
 * around Odoo's canonical `router.pushState({ debug, reload: true })`. Same
 * primitive used by Settings → Developer Tools, the bug-icon menu, and the
 * Ctrl+H debug provider.
 *
 * Covers both edit paths to the user record:
 *   - My Profile menu (target="new" → ActionDialog → FormController)
 *   - Settings → Users & Companies → Users (full page → FormController)
 *
 * `changes` is the diff that was just persisted, so we know exactly when the
 * field was touched. We compare against `router.current.debug` (Odoo's parsed
 * router state) to skip a needless reload when the value didn't actually move.
 */
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { router } from "@web/core/browser/router";
import { user } from "@web/core/user";
import { activateDebug } from "../systray/debug_switcher";

patch(FormController.prototype, {
    async onRecordSaved(record, changes) {
        await super.onRecordSaved(record, changes);
        if (record.resModel !== "res.users" || record.resId !== user.userId) {
            return;
        }
        if (!changes || !("x_debug_default_mode" in changes)) {
            return;
        }
        const newValue = changes.x_debug_default_mode || 0;
        const currentRaw = router.current.debug;
        const currentNorm = !currentRaw || currentRaw === "0" ? 0 : currentRaw;
        if (String(newValue) === String(currentNorm)) {
            return;
        }
        activateDebug(newValue);
    },
});
