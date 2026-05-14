/** @odoo-module **/
// Copyright 2026 Naim OUDAYET
// License LGPL-3

/**
 * Hoot specs for Debug Mode Quick Switcher.
 *
 * Scope: the pure functions and the cycling/mode-mapping logic in
 * static/src/systray/debug_switcher.js. The DOM-bound DebugModeSwitcher
 * component (dropdown rendering, orm.write) is covered manually via the
 * docker dev stack; here we focus on what can be tested without mounting
 * the OWL tree, which is where regressions most often live.
 */
import { describe, expect, test } from "@odoo/hoot";
import { patchWithCleanup } from "@web/../tests/web_test_helpers";
import { router } from "@web/core/browser/router";

import {
    DEBUG_MODES,
    activateDebug,
    cycleToNextMode,
    getCurrentMode,
} from "@no_debug_quick_switcher/systray/debug_switcher";

describe("DEBUG_MODES table", () => {
    test("contains exactly the 5 modes matching Odoo's ?debug= values", () => {
        expect(DEBUG_MODES.map((m) => m.value)).toEqual([
            "",
            "1",
            "assets",
            "tests",
            "assets,tests",
        ]);
    });

    test("each mode has a valid 6-digit hex colour swatch", () => {
        // We don't introspect mode.label / mode.short here: they are
        // LazyTranslated objects from _t(), which Hoot's matchers force-
        // evaluate, and the translation registry isn't yet bound during
        // the pre-mount phase where this test runs.
        for (const mode of DEBUG_MODES) {
            expect(mode.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
        }
    });
});

describe("getCurrentMode()", () => {
    test("returns Off when router has no ?debug= param", () => {
        patchWithCleanup(router, { current: { debug: undefined } });
        expect(getCurrentMode().value).toBe("");
    });

    test("returns Off when ?debug=0 (explicit deactivation)", () => {
        patchWithCleanup(router, { current: { debug: 0 } });
        expect(getCurrentMode().value).toBe("");
    });

    test("returns Off when ?debug= (empty string)", () => {
        patchWithCleanup(router, { current: { debug: "" } });
        expect(getCurrentMode().value).toBe("");
    });

    test("returns Developer when ?debug=1", () => {
        patchWithCleanup(router, { current: { debug: "1" } });
        expect(getCurrentMode().value).toBe("1");
    });

    test("returns Assets when ?debug=assets", () => {
        patchWithCleanup(router, { current: { debug: "assets" } });
        expect(getCurrentMode().value).toBe("assets");
    });

    test("returns Tests when ?debug=tests", () => {
        patchWithCleanup(router, { current: { debug: "tests" } });
        expect(getCurrentMode().value).toBe("tests");
    });

    test("returns Assets + Tests when ?debug=assets,tests", () => {
        patchWithCleanup(router, { current: { debug: "assets,tests" } });
        expect(getCurrentMode().value).toBe("assets,tests");
    });

    test("falls back to Off when ?debug=<unknown> (hand-typed garbage)", () => {
        patchWithCleanup(router, { current: { debug: "garbage" } });
        // unknown router value → no match in DEBUG_MODES → fallback Off
        expect(getCurrentMode().value).toBe("");
    });
});

describe("cycleToNextMode()", () => {
    test("cycles Off → Developer → Assets → Tests → Assets+Tests → Off", () => {
        const calls = [];
        patchWithCleanup(router, {
            current: { debug: undefined },
            pushState: (state) => calls.push(state.debug),
        });

        // Start at Off → cycle pushes Developer
        cycleToNextMode();
        expect(calls.at(-1)).toBe("1");

        // Pretend the URL is now Developer
        router.current.debug = "1";
        cycleToNextMode();
        expect(calls.at(-1)).toBe("assets");

        router.current.debug = "assets";
        cycleToNextMode();
        expect(calls.at(-1)).toBe("tests");

        router.current.debug = "tests";
        cycleToNextMode();
        expect(calls.at(-1)).toBe("assets,tests");

        // Last mode wraps back to Off — activateDebug coerces "" → 0
        router.current.debug = "assets,tests";
        cycleToNextMode();
        expect(calls.at(-1)).toBe(0);
    });
});

describe("activateDebug()", () => {
    test("passes the value straight through to router.pushState with reload", () => {
        const calls = [];
        patchWithCleanup(router, {
            current: { debug: undefined },
            pushState: (state, opts) => calls.push({ state, opts }),
        });

        activateDebug("assets");
        expect(calls).toHaveLength(1);
        expect(calls[0].state).toEqual({ debug: "assets" });
        expect(calls[0].opts).toEqual({ reload: true });
    });

    test("normalises empty / falsy values to 0 (Odoo's 'off' literal)", () => {
        const calls = [];
        patchWithCleanup(router, {
            current: { debug: undefined },
            pushState: (state) => calls.push(state.debug),
        });

        activateDebug("");
        expect(calls.at(-1)).toBe(0);

        activateDebug(null);
        expect(calls.at(-1)).toBe(0);

        activateDebug(undefined);
        expect(calls.at(-1)).toBe(0);
    });
});
