# Permissions

## Accessibility (required)
Granted to the **process that posts events**, which macOS attributes to your *terminal
application* — not to `python3` and not to `macpilot`.

- macOS 13+: System Settings → Privacy & Security → Accessibility
- macOS 12 : System Preferences → Security & Privacy → Privacy → Accessibility (unlock padlock)

Add Warp / Terminal / iTerm2 / VS Code — whichever launches the command.

## Probing it correctly
Some System Events calls succeed *without* the grant, so a generic probe gives false
positives. Probe with a **process-targeted** call:

```bash
osascript -e 'tell application "System Events" to tell process "Finder" to get position of window 1'
```
- Success → prints coordinates.
- Denied  → `(-25211) osascript is not allowed assistive access`

In Python: `macpilot.check_permission()` / `macpilot.require_permission()`

## Screen Recording
Only needed for `screencapture` to capture *other apps'* windows. Not needed for input.

## What no permission can unlock
- Secure input fields (passwords) reject synthetic keyboard events by design.
- Login window and screensaver are outside any app's reach.
