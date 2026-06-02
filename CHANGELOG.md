# Changelog

All notable changes to **Debug Mode Quick Switcher** for Odoo 19.0 are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
Versions use Odoo's `<odoo_version>.<module_major>.<module_minor>.<module_patch>` scheme.

## [19.0.1.3.2] - 2026-06-02

### Changed
- Removed the cross-promotion ("More Modules") section from the store description (index.html).

## [19.0.1.3.1] - 2026-06-01

### Changed
- Updated the Access Pass cross-promo card price from $79 to $99 to match its current price.

## [19.0.1.3.0] - 2026-05-14

### Added
- **Full test coverage** — 9 Python tests (TransactionCase for the 3 models + HttpCase for `ir.http.session_info` override contract) and 13 Hoot specs (the pure functions in `debug_switcher.js`). Wired up via `web.assets_unit_tests` in the manifest plus a `tests/test_js_suite.py` HttpCase runner. Run with `--test-tags=no_debug_quick_switcher` (Python) or `--test-tags=no_debug_quick_switcher_js` (browser).
- Chromium + `python3-websocket` in the Dockerfile so the Hoot suite runs headlessly in the dev stack.

### Changed
- **Selection labels shortened to match the navbar dropdown** — `("", "Off (no debug)")` → `("", "Off")`, `Developer Mode` → `Developer`, `Assets (non-minified JS)` → `Assets`, `Tests (QUnit / Hoot)` → `Tests`. The user form and the navbar systray now resolve through the same five msgids, so users see identical translated text in both surfaces.
- **i18n regenerated with native-language translations across the board** — previously a number of `msgstr` entries were identity-translations (e.g. Dutch `Assets + Tests` → `Assets + Tests`). All 9 languages now use proper native terms (e.g. `nl: Bronbestanden + Testen`, `de: Ressourcen + Tests`, `es: Recursos + Pruebas`). Five auto-generated inherited-model msgids (`User`, `ID`, `HTTP Routing`, `Display Name`, `Config Settings`) stripped from the .po files to avoid the flat-dict translation-collision trap against Odoo core.
- App Store flag grid switched from 4-per-line (`col-md-3 col-sm-4 col-6`) to 3-per-line (`col-md-4 col-sm-6 col-12`) so the 9 language cards lay out evenly across 3 rows.
- Dropped the trailing "Standard PO translation files…" footnote from the App Store description — gettext mechanics are not buyer-facing.
- Module version bumped from `19.0.1.2.0` to `19.0.1.3.0`.

### Fixed
- **Ctrl+Shift+A hotkey was throwing `applyMode is not a function`** — the bootstrap service imported `applyMode` from `debug_switcher.js`, which only exports `activateDebug`. Renamed the import + the re-export + the call site.

## [19.0.1.2.0] - 2026-05-13

### Added
- **Arabic translation** (`ar.po`) — module now ships in 9 languages.
- Arabic flag card in App Store description (`static/description/flags/ar.png`).

### Changed
- App Store hero badge updated from `8 Languages` to `9 Languages`.
- Section header changed to "Available in 9 Languages".
- Module version bumped from `19.0.1.1.0` to `19.0.1.2.0`.

## [19.0.1.1.0] - 2026-05-12

### Added
- **Internationalization (i18n) support** with 8 languages: English (source), French, Spanish, German, Dutch, Portuguese (Brazil), Italian, Chinese (Simplified).
- POT template + 7 PO files under `no_debug_quick_switcher/i18n/`.
- `static/description/flags/` folder with 8 PNG flags.
- **"Available in 8 Languages"** section in App Store description.
- **"8 Languages"** badge in App Store hero banner.
- **Version** + **Languages** rows in the Technical Details table (the §4 2-place rule — index.html version now mirrors the manifest).
- `CHANGELOG.md` at repo root.

### Changed
- All "Odoo 19" references in `index.html` (hero badge, footer, cross-promo, tech details) updated to Odoo 19 for this branch.
- Module version bumped to `19.0.1.1.0`.

## [19.0.1.0.0] - Initial release

### Added
- Navbar systray dropdown with the 5 Odoo debug modes (Off / Dev / Assets / Tests / Assets+Tests).
- Per-user `x_debug_default_mode` selection on `res.users` (default starting mode).
- `Ctrl+Shift+D` cycles modes, `Ctrl+Shift+A` jumps to Assets — both via Odoo's `hotkey` service.
- Page-edge stripe in heavy modes (Assets / Tests) via SCSS.
- "Copy debug URL" menu item.
- "Disable Debug Switcher in Production" master kill-switch (`ir.config_parameter`).
- Two `session_info` flags so the switcher boots without an extra RPC.
- Reverse-sync from My Profile via `FormController.onRecordSaved` patch.
