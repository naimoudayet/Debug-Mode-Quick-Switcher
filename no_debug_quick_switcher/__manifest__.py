# Copyright 2026 Naim OUDAYET
# License LGPL-3
{
    "name": "Debug Mode Quick Switcher",
    "summary": "One-click navbar switcher for Odoo's 5 debug modes — Off, Dev, Assets, Tests, Assets+Tests — with per-user default, hotkey, and mobile support",
    "description": "Debug Mode Quick Switcher replaces the URL-typing dance. A "
                   "navbar dropdown shows the current debug mode with a colour "
                   "badge and lets you jump to any of the 5 modes in one click. "
                   "Per-user default is remembered across sessions on your "
                   "res.users record. Ctrl+Shift+D cycles modes; Ctrl+Shift+A "
                   "jumps to Assets. Mobile-ready. A page-edge stripe in heavy "
                   "modes (Assets / Tests) keeps you from forgetting you're "
                   "slowing the app down. Global 'disable in production' master "
                   "switch keeps the module dormant on prod databases.",
    "version": "19.0.1.3.1",
    "category": "Productivity",
    "website": "https://www.oudayet.com",
    "author": "Naim OUDAYET",
    "maintainers": ["naimoudayet"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": ["web"],
    "data": [
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "no_debug_quick_switcher/static/src/systray/debug_switcher.scss",
            "no_debug_quick_switcher/static/src/systray/debug_switcher.xml",
            "no_debug_quick_switcher/static/src/systray/debug_switcher.js",
            "no_debug_quick_switcher/static/src/services/debug_shortcut_service.js",
            "no_debug_quick_switcher/static/src/services/profile_save_patch.js",
        ],
        "web.assets_unit_tests": [
            "no_debug_quick_switcher/static/tests/**/*.test.js",
        ],
    },
    "images": [
        "static/description/banner.png",
    ],
    "price": 0,
    "currency": "USD",
    "support": "contact@oudayet.com",
}
