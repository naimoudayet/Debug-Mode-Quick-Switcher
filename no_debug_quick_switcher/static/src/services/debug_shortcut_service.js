/** @odoo-module **/
// Copyright 2026 Naim OUDAYET
// License LGPL-3

/**
 * Debug Mode Quick Switcher — bootstrap service.
 *
 * Two responsibilities at web-client boot:
 *   1. Set <body data-debug="..."> based on the current URL so the SCSS
 *      can paint the page-edge stripe in heavy modes (assets / tests).
 *   2. Register two hotkeys via Odoo's hotkey service:
 *        Ctrl+Shift+D  → cycle through all 5 modes
 *        Ctrl+Shift+A  → jump straight to Assets
 *
 * Using the hotkey service (rather than raw addEventListener) gives us
 * Odoo's namespaced collision detection + automatic disable in input fields,
 * so power users don't fire the cycle while typing into the search bar.
 */
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import {
    DEBUG_MODES,
    cycleToNextMode,
    activateDebug,
    getCurrentMode,
} from "../systray/debug_switcher";

const debugShortcutService = {
    dependencies: ["hotkey"],

    start(env, { hotkey }) {
        // 1. Reflect current mode on <body> so the SCSS stripe lights up.
        try {
            const current = getCurrentMode();
            document.body.dataset.debug = current.value;
        } catch {
            /* SSR / non-browser env — never happens in Odoo backend. */
        }

        // 2. Honour the kill-switch — register no hotkeys when disabled in production.
        if (session.x_debug_switcher_disabled) {
            return;
        }

        // 3. Hotkeys.
        hotkey.add("control+shift+d", () => cycleToNextMode(), {
            global: true,
            bypassEditableProtection: false,
        });
        hotkey.add("control+shift+a", () => activateDebug("assets"), {
            global: true,
            bypassEditableProtection: false,
        });
    },
};

registry.category("services").add("no_debug_quick_switcher.shortcuts", debugShortcutService);

// Sanity exports — available for tests + browser console.
export { DEBUG_MODES, cycleToNextMode, activateDebug, getCurrentMode };
