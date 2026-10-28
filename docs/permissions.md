# Permissions

## Accessibility (required)
Granted to the **process that posts events**, which macOS attributes to your *terminal
application*: not to `python3` and not to `macpilot`.

- macOS 13+: System Settings > Privacy & Security > Accessibility
- macOS 12: System Preferences > Security & Privacy > Privacy > Accessibility (unlock padlock)

Add Warp / Terminal / iTerm2 / VS Code: whichever launches the command.

## Checking it
```bash
bin/macpilot access
```
- `granted`, exit code 0: MacPilot did a harmless read that only works with the grant.
- `not granted`, exit code 3: turn it on, quit the terminal app completely, reopen it.

It never prompts and never clicks. Scripts should check the exit code.
In Python: `macpilot.check_permission()` (True only on exit code 0; a missing program,
a crash or a timeout all count as not granted) / `macpilot.require_permission()`.

## Screen Recording
Only needed for `screencapture` to capture *other apps'* windows. Not needed for input.

## What no permission can unlock
- Secure input fields (passwords) reject synthetic keyboard events by design.
- Login window and screensaver are outside any app's reach.
