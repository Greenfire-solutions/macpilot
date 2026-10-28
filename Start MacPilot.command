#!/bin/bash
# Double-click this file to set up MacPilot. It never clicks or types anything on your screen.
# It: 1) checks the ready-made macpilot program runs on this Mac,
#     2) checks the Accessibility permission and opens the right settings page if it is off,
#     3) offers to install the "macpilot" command so you can type it from any folder.
cd "$(dirname "$0")" || exit 1
HERE="$(pwd)"
BIN="$HERE/bin/macpilot"
say() { printf '\n%s\n' "$*"; }
pause() { printf '\nPress Enter to close this window.'; read -r _; }

say "MacPilot setup"
say "Step 1 of 3: checking the macpilot program..."
if [ ! -f "$BIN" ]; then
  say "bin/macpilot is missing from this folder. Unzip MacPilot again and run this file from the new folder."
  pause; exit 1
fi
# A program downloaded in a zip is marked "from the internet"; this file was already opened
# with your OK, so clear that mark from MacPilot's own files only.
xattr -dr com.apple.quarantine "$HERE" 2>/dev/null
chmod +x "$BIN" 2>/dev/null
if ! SCREEN="$("$BIN" screen 2>&1)"; then
  say "The macpilot program would not run on this Mac:"
  echo "$SCREEN"
  say "If you have Apple's free Command Line Tools (xcode-select --install) you can rebuild it with: make"
  pause; exit 1
fi
echo "OK. Your screen:"
echo "$SCREEN" | grep '^display'

say "Step 2 of 3: checking the Accessibility permission..."
while ! "$BIN" access >/dev/null 2>&1; do
  cat <<'TXT'

MacPilot needs the Accessibility permission. Without it macOS ignores its clicks and typing.
The permission is given to the app you run MacPilot from. For this window that is Terminal.

  macOS 13 or newer: System Settings > Privacy & Security > Accessibility
  macOS 12:          System Preferences > Security & Privacy > Privacy > Accessibility
                     (click the padlock first and type your Mac password)

Turn the switch on for Terminal (press + and add it from Applications > Utilities if it is not listed).
If you later run MacPilot from iTerm, Warp or another app, turn it on for that app too.
TXT
  if [ -z "$MACPILOT_NO_OPEN" ]; then
    open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null
    echo "(The settings page has been opened for you.)"
  fi
  printf '\nWhen it is on: quit Terminal completely (Terminal menu > Quit Terminal), then double-click\n'
  printf 'Start MacPilot again. Or press Enter to check again now, or type q and Enter to stop: '
  read -r ans
  [ "$ans" = "q" ] && { say "Stopped. Run this file again once the permission is on."; exit 0; }
done
echo "OK. Accessibility is on."

say "Step 3 of 3: the macpilot command"
TARGET="$HOME/.local/bin/macpilot"
printf 'Install the "macpilot" command so you can type it in any Terminal window? (y/n) '
read -r ans
if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
  mkdir -p "$HOME/.local/bin" && cp "$BIN" "$TARGET" && chmod +x "$TARGET"
  if ! grep -qs 'HOME/.local/bin' "$HOME/.zprofile"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zprofile"
  fi
  echo "Installed. In a NEW Terminal window you can type: macpilot screen"
else
  echo "Skipped. You can always run it from this folder as: bin/macpilot"
fi

say "All set. Try this in Terminal (it only looks, it never clicks):"
echo "  cd \"$HERE\""
echo "  bin/macpilot peek          (tells you what is under your mouse)"
echo "  python3 examples/look_then_click.py --look"
echo
echo "READ ME FIRST.txt explains what each command does."
pause
