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
 * Mode switches use direct URL navigation so we don't depend on Odoo's router
 * module (which moved between v16/v17 -> v18/v19). Reading the current mode
 * uses `odoo.debug` (the canonical global Odoo populates from the URL at boot).
 *
 * Per-user default (`x_debug_default_mode` on res.users) is auto-applied on
 * first land if the URL has no ?debug= AND the master switch is off. Both
 * values are exposed via session_info for synchronous boot-time reads.
 *
 * Hotkeys are registered via Odoo's hotkey service in
 * services/debug_shortcut_service.js so we get namespacing + collision warnings
 * for free.
 */
import { Component, useState, onMounted } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export const DEBUG_MODES = [
    { value: "", label: "Off", short: "Off", color: "#94A3B8" },
    { value: "1", label: "Developer", short: "Dev", color: "#00A09D" },
    { value: "assets", label: "Assets", short: "Assets", color: "#FF7F4F" },
    { value: "tests", label: "Tests", short: "Tests", color: "#714B67" },
    { value: "assets,tests", label: "Assets + Tests", short: "A+T", color: "#5A3A52" },
];

/**
 * Read the current debug mode from the URL — works across all Odoo versions.
 * Odoo populates `odoo.debug` from the URL at boot, so we use that when
 * available and fall back to reading the URL directly.
 */
function readCurrentDebugRaw() {
    if (typeof odoo !== "undefined" && odoo.debug !== undefined) {
        return odoo.debug;
    }
    const params = new URLSearchParams(window.location.search);
    return params.get("debug") ?? "";
}

/**
 * True when the raw debug value represents "off". Covers undefined, 0, "0", "".
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
 * Read the current debug mode. Returns the matching entry from DEBUG_MODES,
 * or "Off" when not in any debug mode.
 */
export function getCurrentMode() {
    const fieldValue = debugValueToFieldValue(readCurrentDebugRaw());
    return DEBUG_MODES.find((m) => m.value === fieldValue) || DEBUG_MODES[0];
}

/**
 * True when the URL has no explicit `?debug=` parameter at all (so the saved
 * user pref can be applied without overriding an explicit URL).
 */
function urlHasDebugParam() {
    return new URLSearchParams(window.location.search).has("debug");
}

/**
 * Activate a debug mode by navigating to the same URL with `?debug=<value>`.
 * Same end-result as Odoo's canonical `?debug=` URL pattern used by Settings ->
 * Developer Tools (see odoo/addons/web/.../res_config_dev_tool.xml: `<a href="?debug=assets">`).
 *
 *   - 0 / "" / undefined -> Off (`?debug=`)
 *   - 1                  -> Developer (`?debug=1`)
 *   - "assets"           -> Developer + assets
 *   - "tests"            -> Developer + tests
 *   - "assets,tests"     -> Developer + assets + tests
 *
 * Always reloads the page so the new bundle is fetched.
 */
export function activateDebug(value) {
    const url = new URL(window.location.href);
    const debugValue = value === 0 || value === undefined || value === null ? "" : String(value);
    url.searchParams.set("debug", debugValue);
    window.location.href = url.toString();
}

/**
 * Alias used by debug_shortcut_service.js (Ctrl+Shift+A).
 */
export function applyMode(value) {
    activateDebug(value);
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
        this.user = useService("user");
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
        if (!urlHasDebugParam()) {
            // No explicit ?debug= -> auto-apply the saved default if any.
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
        const fieldValue = debugValueToFieldValue(readCurrentDebugRaw());
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
            .write("res.users", [this.user.userId], { x_debug_default_mode: fieldValue })
            .catch(() => {
                /* non-fatal — pref just stays out of sync until next change */
            });
    }

    async onSelectMode(modeValue) {
        // Persist to user pref so the choice survives login + so My Profile
        // and the dropdown stay in sync. Errors don't block the switch — the
        // URL change is what matters this session.
        try {
            await this.orm.write("res.users", [this.user.userId], {
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
}

// Hide on production-disabled instances. We register unconditionally; the
// component itself bails when session says disabled.
registry.category("systray").add(
    "no_debug_quick_switcher.DebugModeSwitcher",
    {
        Component: DebugModeSwitcher,
        isDisplayed: () => !session.x_debug_switcher_disabled,
    },
    { sequence: 100 },
);
