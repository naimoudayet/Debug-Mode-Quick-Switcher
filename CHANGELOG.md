# Changelog

All notable changes to **Debug Mode Quick Switcher** for Odoo 16.0 are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
Versions use Odoo's `<odoo_version>.<module_major>.<module_minor>.<module_patch>` scheme.

## [16.0.1.1.0] - 2026-05-12

### Added
- **Internationalization (i18n) support** with 8 languages: English (source), French, Spanish, German, Dutch, Portuguese (Brazil), Italian, Chinese (Simplified).
- POT template + 7 PO files under `no_debug_quick_switcher/i18n/`.
- `static/description/flags/` folder with 8 PNG flags.
- **"Available in 8 Languages"** section in App Store description.
- **"8 Languages"** badge in App Store hero banner.
- **Version** + **Languages** rows in the Technical Details table (the §4 2-place rule — index.html version now mirrors the manifest).
- `CHANGELOG.md` at repo root.

### Changed
- All "Odoo 19" references in `index.html` (hero badge, footer, cross-promo, tech details) updated to Odoo 16 for this branch.
- Module version bumped to `16.0.1.1.0`.

## [16.0.1.0.0] - Initial release

### Added
- Navbar systray dropdown with the 5 Odoo debug modes (Off / Dev / Assets / Tests / Assets+Tests).
- Per-user `x_debug_default_mode` selection on `res.users` (default starting mode).
- `Ctrl+Shift+D` cycles modes, `Ctrl+Shift+A` jumps to Assets — both via Odoo's `hotkey` service.
- Page-edge stripe in heavy modes (Assets / Tests) via SCSS.
- "Copy debug URL" menu item.
- "Disable Debug Switcher in Production" master kill-switch (`ir.config_parameter`).
- Two `session_info` flags so the switcher boots without an extra RPC.
- Reverse-sync from My Profile via `FormController.onRecordSaved` patch.
