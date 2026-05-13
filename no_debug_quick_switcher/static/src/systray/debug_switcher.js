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
 *   "tests"        → Developer + QUnit / Hoot test assets
 *   "assets,tests" → Developer + assets + tests
 *
 * All mode switches go through `activateDebug()` — a thin wrapper that calls
 * Odoo's canonical `router.pushState({ debug, reload: true })`, the exact same
 * primitive used by Settings → Developer Tools, the bug-icon debug menu, and
 * core/debug/debug_menu_items.js. We do not reinvent the navigation; we just
 * decide *when* to call it.
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
import { router } from "@web/core/browser/router";
import { session } from "@web/session";
import { user } from "@web/core/user";
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
 * True when `router.current.debug` represents the "off" state. Covers all the
 * shapes Odoo's router can produce: undefined (no param), 0 / "0" (what
 * activateDebug(0) writes), and "" (legacy `?debug=` with empty value).
 */
function isDebugOff(raw) {
    return raw === undefined || raw === null || raw === 0 || raw === "0" || raw === "";
}

/**
 * Map a router-style debug value to the literal stored in our Selection field
 * on res.users (which uses "" for off, not 0).
 */
function debugValueToFieldValue(raw) {
    return isDebugOff(raw) ? "" : String(raw);
}

/**
 * Read the current debug mode from Odoo's router state. Returns the matching
 * entry from DEBUG_MODES, or "Off" when not in any debug mode.
 *
 * `router.current.debug` is Odoo's own parsed view of the URL — same source
 * of truth used by core/debug/debug_menu_items.js.
 */
export function getCurrentMode() {
    const fieldValue = debugValueToFieldValue(router.current.debug);
    return DEBUG_MODES.find((m) => m.value === fieldValue) || DEBUG_MODES[0];
}

/**
 * Activate a debug mode — direct adoption of Odoo's canonical one-liner from
 * odoo/addons/web/static/src/webclient/settings_form_view/widgets/
 * res_config_dev_tool.js. Same call signature, same semantics:
 *
 *   - 0              → Off (matches "Deactivate the developer mode")
 *   - 1              → Developer
 *   - "assets"       → Developer + assets
 *   - "tests"        → Developer + tests
 *   - "assets,tests" → Developer + assets + tests
 *
 * We accept "" as an alias for 0 since our Selection field stores the empty
 * string for off.
 */
export function activateDebug(value) {
    router.pushState({ debug: value || 0 }, { reload: true });
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

export class DebugModeSwitcher extends Component {
    static template = "no_debug_quick_switcher.DebugModeSwitcher";
    static components = { Dropdown, DropdownItem };
    static props = {};

    setup() {
        this.ui = useService("ui");
        this.orm = useService("orm");
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
        if (router.current.debug === undefined) {
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
        const fieldValue = debugValueToFieldValue(router.current.debug);
        // Don't overwrite the pref with a value the field can't represent
        // (e.g. someone hand-typed ?debug=foo).
        if (!DEBUG_MODES.find((m) => m.value === fieldValue)) {
            return;
        }
        const sessionValue = session.x_debug_default_mode || "";
        if (fieldValue === sessionValue) {
            return;
        }
        this.orm
            .write("res.users", [user.userId], { x_debug_default_mode: fieldValue })
            .catch(() => {
                /* non-fatal — pref just stays out of sync until next change */
            });
    }

    async onSelectMode(modeValue) {
        // Persist to user pref so the choice survives login + so My Profile
        // and the dropdown stay in sync. Errors don't block the switch — the
        // URL change is what matters this session.
        try {
            await this.orm.write("res.users", [user.userId], {
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
