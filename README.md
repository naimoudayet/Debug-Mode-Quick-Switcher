# Debug Mode Quick Switcher

One-click navbar dropdown for Odoo's 5 debug modes — Off, Dev, Assets, Tests, Assets+Tests — with per-user default, hotkey, mobile support, and a page-edge stripe in heavy modes.

## Why

Odoo ships one debug button (Settings → Activate Developer Mode) that toggles `?debug=1`. Real devs need `?debug=assets` for unminified JS, `?debug=tests` for QUnit, and `?debug=assets,tests` for both — and most of the time they type these into the URL bar by hand. This module replaces that with a navbar dropdown.

## Features

- **5 modes, one click** — Off / Developer / Assets / Tests / Assets+Tests, each with a coloured badge so you always see which mode is active.
- **Per-user default** — set your preferred starting mode on `res.users.x_debug_default_mode`. Lands on it whenever you log in. Travels across browsers, follows you to client servers.
- **Hotkeys** — `Ctrl+Shift+D` cycles modes; `Ctrl+Shift+A` jumps straight to Assets. Registered through Odoo's `hotkey` service so they don't fire while typing.
- **Page-edge stripe** — when in Assets or Tests mode, a thin coloured bar lights up the top of the page. You don't forget you're in heavy mode.
- **Copy debug URL** — one-click copy of the current URL with `?debug=...` for sharing in tickets.
- **Production master switch** — global "disable" param hides the switcher and ignores per-user defaults. Recommended ON for production.
- **Mobile-ready** — works on small viewports.

## How It Works

- A persistent OWL component is registered into `registry.category("systray")` and renders the dropdown in the navbar.
- A boot service sets `<body data-debug="...">` based on the current `?debug=` URL parameter; the SCSS uses that attribute to draw the page-edge stripe.
- Mode changes navigate to the same URL with a new `?debug=` value. Odoo's router treats `debug` as a "locked key", so it survives subsequent navigation.
- Per-user default + master kill-switch are exposed in `session_info` for synchronous read at boot.

## Technical Details

| Field | Value |
|---|---|
| Odoo Version | 16.0 |
| License | LGPL-3 |
| Dependencies | `web` |
| Field Prefix | `x_` |
| Backend assets | OWL component + SCSS + service (~280 lines) |

## Fields Added

| Model | Field | Type | Description |
|---|---|---|---|
| `res.users` | `x_debug_default_mode` | Selection | Per-user starting debug mode. Off by default. |

## System Parameter

| Key | Type | Description |
|---|---|---|
| `no_debug_quick_switcher.disabled` | Boolean | Set "True" to hide the switcher and ignore defaults — typically on production. |

## Installation

1. Copy `no_debug_quick_switcher` into your Odoo addons path.
2. **Apps → Update Apps List** → search "Debug Mode Quick Switcher" → **Install**.
3. (Optional) Open **My Profile** → set your default debug mode → save.

## Docker Setup (Development)

```bash
docker-compose up -d
```

Odoo: http://localhost:13416

## Compatibility

- Odoo 16.0 Community + Enterprise

## Author

**Naim OUDAYET** — Tunisia.

## License

LGPL-3.
