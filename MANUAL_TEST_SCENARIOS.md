# Manual Test Scenarios -- Debug Mode Quick Switcher

Dev stack: `docker-compose up -d`, then open <http://localhost:13417> and use database `debug17`.
Log in as an Internal User with Settings access; the switcher is in the systray (top-right navbar).

## 1. The five modes
1. Click the systray bug icon.
2. The dropdown lists **Off**, **Developer**, **Assets**, **Tests**, **Assets + Tests**, each with its colour swatch.
3. Pick **Developer**: the page reloads, the URL carries `?debug=1`, and the active mode is marked in the dropdown.
4. Repeat for **Assets** (`?debug=assets`), **Tests** (`?debug=tests`) and **Assets + Tests** (`?debug=assets,tests`).

## 2. Off really turns it off
1. From any active mode, pick **Off**.
2. The page reloads with no `debug` parameter and Odoo's own developer tools disappear.

## 3. Page-edge stripe in heavy modes
1. Switch to **Assets**.
2. A coloured stripe runs along the page edge, so a forgotten heavy mode is visible at a glance.
3. Switch to **Developer**: the stripe is gone. Switch to **Assets + Tests**: the stripe is back.

## 4. Per-user default
1. **My Profile** > set **Default Debug Mode** to *Assets* > Save.
2. Log out and back in: the session starts in Assets mode without touching the dropdown.
3. Set it back to *Off* and re-login: the session starts clean.

## 5. The default is per user, not global
1. Set your own default to *Assets*.
2. Log in as a second internal user: that user starts at their own default, not yours.

## 6. Keyboard shortcut
1. Press **Ctrl+Shift+D**: the mode advances one step through the cycle.
2. The hint at the bottom of the dropdown matches the keys that actually work.

## 7. Master kill-switch
1. **Settings > Technical > System Parameters > New**: key `no_debug_quick_switcher.disabled`, value `True`.
2. Reload: the systray icon is gone and per-user defaults are ignored.
3. Delete the parameter and reload: the switcher is back.

## 8. Non-privileged users
1. Log in as a Portal user.
2. No systray entry appears and no debug parameter is applied.

## 9. Mobile layout
1. Narrow the browser to a phone width (or use device emulation).
2. The switcher stays reachable and the dropdown remains usable.

## 10. Uninstall is clean
1. **Apps > Debug Mode Quick Switcher > Uninstall**.
2. No systray entry, no stripe, no leftover error in the log; `res.users.x_debug_default_mode` is gone.
