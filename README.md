# Debug Mode Quick Switcher

![License](https://img.shields.io/badge/license-LGPL--3-blue)
![Odoo](https://img.shields.io/badge/Odoo-16.0%20%7C%2017.0%20%7C%2018.0%20%7C%2019.0-blueviolet)
![Languages](https://img.shields.io/badge/languages-9-orange)

**Author: Naim OUDAYET**

One-click navbar dropdown for Odoo's 5 debug modes — Off, Developer, Assets, Tests, Assets + Tests — with per-user default, hotkey, mobile support, and a page-edge stripe in heavy modes. Available in 9 languages.

## Choose Your Odoo Version

Each Odoo major version lives on its own branch. Pick the one matching your server.

| Odoo Version | Stable | Development |
|---|---|---|
| 19.0 | [`19.0`](../../tree/19.0) | [`19.0-dev`](../../tree/19.0-dev) |
| 18.0 | [`18.0`](../../tree/18.0) | [`18.0-dev`](../../tree/18.0-dev) |
| 17.0 | [`17.0`](../../tree/17.0) | [`17.0-dev`](../../tree/17.0-dev) |
| 16.0 | [`16.0`](../../tree/16.0) | [`16.0-dev`](../../tree/16.0-dev) |

The technical module name is **`no_debug_quick_switcher`** on every version branch.

## What It Does

- **5 modes, one click** — Off / Developer / Assets / Tests / Assets + Tests, each with a coloured badge in the navbar so you always see which mode is active.
- **Per-user default** — set your preferred starting mode on `res.users.x_debug_default_mode`. Lands on it whenever you log in. Stays in sync whether you switch from the navbar, **My Profile**, or Odoo's own debug menu.
- **Hotkeys** — `Ctrl+Shift+D` cycles modes; `Ctrl+Shift+A` jumps straight to Assets. Both auto-disable while typing.
- **Page-edge stripe** — in Assets or Tests mode, a thin coloured bar lights up the top of the page so you don't forget you're slowing things down.
- **Copy debug URL** — one-click copy of the current URL with `?debug=...` for sharing in tickets.
- **Production master switch** — global "disable" param hides the switcher and ignores per-user defaults. Recommended ON for production databases.
- **Mobile-ready** — works on small viewports.
- **Translated into 9 Languages** — English, French, Spanish, German, Dutch, Portuguese (BR), Italian, Chinese (Simplified), Arabic. Each user sees mode labels and tooltips in their own Odoo language.

## Quick Install

1. Check out the branch matching your Odoo version (see table above).
2. Copy the `no_debug_quick_switcher/` folder into a directory listed in your Odoo `addons_path`.
3. **Apps → Update Apps List → search "Debug Mode Quick Switcher" → Install**.
4. (Optional) Open **My Profile** → set your default debug mode → Save.

Full per-version installation, configuration, and test instructions live in each branch's own README.

## Languages

Ships with translations for:

| Code     | Language                |
|----------|-------------------------|
| `en_US`  | English (source)        |
| `fr`     | French                  |
| `es`     | Spanish                 |
| `de`     | German                  |
| `nl`     | Dutch                   |
| `pt_BR`  | Portuguese (Brazil)     |
| `it`     | Italian                 |
| `zh_CN`  | Chinese (Simplified)    |
| `ar`     | Arabic                  |

Regional variants (e.g. `fr_BE`, `nl_BE`) inherit from the base language via Odoo's standard fallback. To add a new language, drop a `<code>.po` file into the branch's `i18n/` folder — the canonical template is `i18n/no_debug_quick_switcher.pot`.

## Compatibility

Works on **Odoo 16.0, 17.0, 18.0, and 19.0**, Community and Enterprise editions. Python dependencies: none. Required Odoo module: `web`.

## Repository Layout

This `main` branch is a landing page only. Module code, the development Docker stack, and per-version tests live on the per-version branches above.

## Author

**Naim OUDAYET** — Odoo developer based in Tunisia.

- Website: [oudayet.com](https://www.oudayet.com)
- Email: contact@oudayet.com
- GitHub: [@naimoudayet](https://github.com/naimoudayet)

## License

[LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html).
