/** @odoo-module **/
// Copyright 2026 Naim OUDAYET
// License LGPL-3

/**
 * Debug Mode Quick Switcher — navbar systray dropdown.
 *
 * Five modes (matching Odoo's `?debug=` query parameter literals):
 *   ""             → Off
 *   "1"            → Developer
 *   "assets"       → Developer + non-minified JS bundles
 *   "tests"        → Developer + QUnit test assets
 *   "assets,tests" → Developer + assets + tests
 *
 * All mode switches mirror the canonical mechanism used by Odoo 17's own
 * Settings → Developer Tools section: a full-page navigation to
 * `?debug=<mode>`. We deliberately do NOT use `router.pushState` — in v17 the
 * router stores state in the URL *hash* (`#`), but Odoo selects the asset
 * bundles (assets / tests) at boot from the *query string* (`?`). A
 * router push would update the hash without switching the JS bundle, so the
 * mode change would silently fail to take effect. Plain anchor navigation
 * does a real page load and gets the right bundle. Same approach as
 * `addons/web/static/src/webclient/settings_form_view/widgets/res_config_dev_tool.xml`.
 *
 * Current-mode reads go through `odoo.debug` (the global string Odoo sets at
 * boot from the URL), again matching `res_config_dev_tool.js` exactly.
 *
 * Per-user default (`x_debug_default_mode` on res.users) is auto-applied on
 * first land if the URL has no ?debug= AND the master switch is off. Both
 * values are exposed via session_info for synchronous boot-time reads.
 *
 * Hotkeys are registered via Odoo's hotkey service in
 * services/debug_shortcut_service.js so we get namespacing + collision warnings
 * for free.
 */
import { Component, markup, useState, onMounted } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

// Labels are wrapped in _t() so the navbar dropdown + badge follow the
// user's UI language. _t returns a LazyTranslated at module load that
// resolves on stringification — safe to call at module top-level.
export const DEBUG_MODES = [
    { value: "", label: _t("Off"), short: _t("Off"), color: "#94A3B8" },
    { value: "1", label: _t("Developer"), short: _t("Dev"), color: "#00A09D" },
    { value: "assets", label: _t("Assets"), short: _t("Assets"), color: "#FF7F4F" },
    { value: "tests", label: _t("Tests"), short: _t("Tests"), color: "#714B67" },
    { value: "assets,tests", label: _t("Assets + Tests"), short: _t("A+T"), color: "#5A3A52" },
];

/**
 * The exact string Odoo's boot sets from the URL: "", "1", "assets", "tests",
 * or "assets,tests". Same global the v17 Settings dev-tool widget reads.
 *
 * Returns the entry from DEBUG_MODES, or "Off" when not in any debug mode.
 */
export function getCurrentMode() {
    const value = (typeof odoo !== "undefined" && odoo.debug) || "";
    return DEBUG_MODES.find((m) => m.value === value) || DEBUG_MODES[0];
}

/**
 * Activate a debug mode by navigating to `?debug=<value>` — the exact pattern
 * used by Odoo 17's Settings → Developer Tools anchors. Full page load is
 * required because the JS asset bundle (regular vs assets vs assets+tests) is
 * picked at boot from the query string, not at runtime.
 *
 *   - 0 / ""         → Off (matches "Deactivate the developer mode")
 *   - "1"            → Developer
 *   - "assets"       → Developer + assets
 *   - "tests"        → Developer + tests
 *   - "assets,tests" → Developer + assets + tests
 */
export function activateDebug(value) {
    const url = new URL(window.location.href);
    // Empty string for "off" — same literal as the Settings widget's
    // <a href="?debug="> "Deactivate the developer mode" anchor.
    url.searchParams.set("debug", value && value !== 0 ? String(value) : "");
    window.location.href = url.toString();
}

/**
 * Cycle to the next mode in DEBUG_MODES order. Used by the hotkey.
 */
export function cycleToNextMode() {
    const current = getCurrentMode();
    const idx = DEBUG_MODES.findIndex((m) => m.value === current.value);
    const next = DEBUG_MODES[(idx + 1) % DEBUG_MODES.length];
    activateDebug(next.value);
}

/** True when the current URL has no `?debug=` parameter at all (vs empty string). */
function urlHasDebugParam() {
    return new URL(window.location.href).searchParams.has("debug");
}

export class DebugModeSwitcher extends Component {
    static template = "no_debug_quick_switcher.DebugModeSwitcher";
    static components = { Dropdown, DropdownItem };
    static props = {};

    setup() {
        this.ui = useService("ui");
        this.orm = useService("orm");
        this.userService = useService("user");
        this.state = useState({
            current: getCurrentMode(),
        });
        this.modes = DEBUG_MODES;
        // On every boot, reconcile the URL's debug mode with the saved user
        // pref. Catches mode changes from any source — Odoo's Settings widget,
        // the bug-icon "Leave Debug Mode" item, hand-typed ?debug=, or our own
        // dropdown — without having to patch each one individually.
        onMounted(() => this._reconcileWithUserPref());
    }

    _reconcileWithUserPref() {
        if (session.x_debug_switcher_disabled) {
            return;
        }
        if (!urlHasDebugParam()) {
            // No explicit ?debug= → auto-apply the saved default if any. This
            // is what gives the "default mode" pref its meaning across sessions.
            const def = session.x_debug_default_mode;
            if (def) {
                // Defer one tick so we don't reload mid-render.
                setTimeout(() => activateDebug(def), 0);
            }
            return;
        }
        // URL drives the mode this session. Make sure the saved pref reflects
        // it — so the next fresh login (no ?debug= in URL) lands in the same
        // mode the user last activated, regardless of which UI they used.
        this._writePrefIfChanged();
    }

    _writePrefIfChanged() {
        const current = getCurrentMode();
        const fieldValue = current.value;
        const sessionValue = session.x_debug_default_mode || "";
        if (fieldValue === sessionValue) {
            return;
        }
        this.orm
            .write("res.users", [this.userService.userId], { x_debug_default_mode: fieldValue })
            .catch(() => {
                /* non-fatal — pref just stays out of sync until next change */
            });
    }

    async onSelectMode(modeValue) {
        // Persist to user pref so the choice survives login + so My Profile
        // and the dropdown stay in sync. Errors don't block the switch — the
        // URL change is what matters this session.
        try {
            await this.orm.write("res.users", [this.userService.userId], {
                x_debug_default_mode: modeValue,
            });
        } catch {
            /* ignore — page navigation still happens */
        }
        activateDebug(modeValue);
    }

    onCopyDebugUrl() {
        // Copy the current URL to clipboard so users can paste it in tickets.
        const url = window.location.href;
        if (navigator.clipboard?.writeText) {
            navigator.clipboard.writeText(url).catch(() => {});
        }
    }

    get tooltipText() {
        return _t("Current debug mode: %s", this.state.current.label);
    }

    // One translatable string for the whole hotkey hint — translators can move
    // verbs/objects around for natural word order (esp. RTL). Per
    // ODOO_GUIDELINES §12.6: NEVER split a sentence across multiple _t() calls.
    // markup() lets us keep <kbd> styling without t-raw / unsafe HTML risk.
    get hotkeyHintMarkup() {
        return markup(_t(
            "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>D</kbd> cycles · " +
            "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd> jumps to Assets"
        ));
    }
}

// Hide on production-disabled instances. We register unconditionally; the
// component's own template renders nothing when session says disabled.
registry.category("systray").add(
    "no_debug_quick_switcher.DebugModeSwitcher",
    {
        Component: DebugModeSwitcher,
        isDisplayed: () => !session.x_debug_switcher_disabled,
    },
    { sequence: 100 },
);
