# Changelog

All notable changes to **Debug Mode Quick Switcher** for Odoo 17.0 are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
Versions use Odoo's `<odoo_version>.<module_major>.<module_minor>.<module_patch>` scheme.

## [17.0.1.3.0] - 2026-05-14

### Added
- **Backport from 18.0.1.3.0** — full feature parity with the 18.0 release: 9 languages with native translations, unified Selection labels matching the navbar dropdown, App Store storefront, full Python test coverage.

### Changed
- **v17-compatible service wiring** — replaced v18+ singleton imports (`import { router } from "@web/core/browser/router"`, `import { user } from "@web/core/user"`) with v17 service patterns. Component layer uses `useService("router")` / `useService("user")`; the bootstrap service declares `router` and `user` as dependencies and injects them into the systray module so the parameter-less helpers (`getCurrentMode`, `activateDebug`, `cycleToNextMode`) keep their shape. The `FormController` patch reads them from `this.env.services` at call time.
- **Dropdown template adjusted for v17** — v17 inverts the slot API (default slot is the menu, named slot is the toggler). Wrapped the badge button in `<t t-set-slot="toggler">` and moved the menu items to the default slot. `DropdownItem` now uses the `class` prop directly (v17 has no `attrs` prop).
- Hoot test suite removed (Hoot was introduced in v18). Python tests (9) cover the model, the kill-switch round-trip, and the `ir.http.session_info` override contract — unchanged from 18.0.
- Dockerfile slimmed: dropped Chromium + `python3-websocket` since there's no Hoot suite to run headlessly.
- Module version: `17.0.1.3.0`. Port: `13417`.

## [18.0.1.3.0] - 2026-05-14

### Added
- **Full test coverage** — 9 Python tests (TransactionCase for the 3 models + HttpCase for `ir.http.session_info` override contract) and 13 Hoot specs (the pure functions in `debug_switcher.js`). Wired up via `web.assets_unit_tests` in the manifest plus a `tests/test_js_suite.py` HttpCase runner. Run with `--test-tags=no_debug_quick_switcher` (Python) or `--test-tags=no_debug_quick_switcher_js` (browser).
- Chromium + `python3-websocket` in the Dockerfile so the Hoot suite runs headlessly in the dev stack.

### Changed
- **Selection labels shortened to match the navbar dropdown** — `("", "Off (no debug)")` → `("", "Off")`, `Developer Mode` → `Developer`, `Assets (non-minified JS)` → `Assets`, `Tests (QUnit / Hoot)` → `Tests`. The user form and the navbar systray now resolve through the same five msgids, so users see identical translated text in both surfaces.
- **i18n regenerated with native-language translations across the board** — previously a number of `msgstr` entries were identity-translations (e.g. Dutch `Assets + Tests` → `Assets + Tests`). All 9 languages now use proper native terms (e.g. `nl: Bronbestanden + Testen`, `de: Ressourcen + Tests`, `es: Recursos + Pruebas`). Stale long-form translations baked into short msgids by the v18 exporter (e.g. `msgid "Tests"` / `msgstr "Tests (QUnit / Hoot)"`) were corrected to the proper short translations. Three auto-generated inherited-model msgids (`User`, `HTTP Routing`, `Config Settings`) stripped from the .po files to avoid the flat-dict translation-collision trap against Odoo core.
- App Store flag grid switched from 4-per-line (`col-md-3 col-sm-4 col-6`) to 3-per-line (`col-md-4 col-sm-6 col-12`) so the 9 language cards lay out evenly across 3 rows.
- Dropped the trailing "Standard PO translation files…" footnote from the App Store description — gettext mechanics are not buyer-facing.
- Module version bumped from `18.0.1.2.0` to `18.0.1.3.0`.

### Fixed
- **Ctrl+Shift+A hotkey was throwing `applyMode is not a function`** — the bootstrap service imported `applyMode` from `debug_switcher.js`, which only exports `activateDebug`. Renamed the import + the re-export + the call site.

## [18.0.1.2.0] - 2026-05-13

### Added
- **Arabic translation** (`ar.po`) — module now ships in 9 languages.
- Arabic flag card in App Store description (`static/description/flags/ar.png`).

### Changed
- App Store hero badge updated from `8 Languages` to `9 Languages`.
- Section header changed to "Available in 9 Languages".
- Module version bumped from `18.0.1.1.0` to `18.0.1.2.0`.

## [18.0.1.1.0] - 2026-05-12

### Added
- **Internationalization (i18n) support** with 8 languages: English (source), French, Spanish, German, Dutch, Portuguese (Brazil), Italian, Chinese (Simplified).
- POT template + 7 PO files under `no_debug_quick_switcher/i18n/`.
- `static/description/flags/` folder with 8 PNG flags.
- **"Available in 8 Languages"** section in App Store description.
- **"8 Languages"** badge in App Store hero banner.
- **Version** + **Languages** rows in the Technical Details table (the §4 2-place rule — index.html version now mirrors the manifest).
- `CHANGELOG.md` at repo root.

### Changed
- All "Odoo 19" references in `index.html` (hero badge, footer, cross-promo, tech details) updated to Odoo 18 for this branch.
- Module version bumped to `18.0.1.1.0`.

## [18.0.1.0.0] - Initial release

### Added
- Navbar systray dropdown with the 5 Odoo debug modes (Off / Dev / Assets / Tests / Assets+Tests).
- Per-user `x_debug_default_mode` selection on `res.users` (default starting mode).
- `Ctrl+Shift+D` cycles modes, `Ctrl+Shift+A` jumps to Assets — both via Odoo's `hotkey` service.
- Page-edge stripe in heavy modes (Assets / Tests) via SCSS.
- "Copy debug URL" menu item.
- "Disable Debug Switcher in Production" master kill-switch (`ir.config_parameter`).
- Two `session_info` flags so the switcher boots without an extra RPC.
- Reverse-sync from My Profile via `FormController.onRecordSaved` patch.
