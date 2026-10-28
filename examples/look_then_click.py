#!/usr/bin/env python3
"""Safe example: YOU point at the target, MacPilot checks what is there, and asks before clicking.

Nothing here uses a fixed screen position, so it works on any Mac and any layout.

    python3 examples/look_then_click.py            # asks before it clicks
    python3 examples/look_then_click.py --look     # only looks, never clicks

Steps:
  1. Put your mouse over the button you want pressed (in any app) and come back here.
  2. Press Enter. MacPilot reads where the mouse is and what is under it.
  3. It tells you, then asks "Click it?". Only "y" clicks. Anything else stops.
"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from macpilot import engine, input as mp_input, inspect


def describe(el: dict) -> str:
    if not el:
        return "no named button here (normal inside web pages, videos and canvases)"
    return ", ".join(f"{k}: {v}" for k, v in el.items())


def main(argv: list[str]) -> int:
    look_only = "--look" in argv
    if not engine.check_permission():
        print("MacPilot does not have Accessibility permission yet.")
        print("Open System Settings > Privacy & Security > Accessibility (on macOS 12:")
        print("System Preferences > Security & Privacy > Privacy > Accessibility),")
        print("turn it on for Terminal (or the app you typed this in), quit it, open it again.")
        return 1

    input("Move your mouse over the thing you want to click, then press Enter here... ")
    x, y = mp_input.position()
    el = inspect.peek(x, y)
    print(f"\nThe mouse is at {x:.0f}, {y:.0f}.")
    print(f"Under it: {describe(el)}")

    if look_only:
        print("Look-only mode: nothing was clicked.")
        return 0
    answer = input("Click it once? Type y and press Enter to click, anything else to stop: ")
    if answer.strip().lower() != "y":
        print("Stopped. Nothing was clicked.")
        return 0
    # The mouse may have moved while you typed; check the same spot is still the same thing.
    if inspect.peek(x, y) != el:
        print("What is under that spot changed, so MacPilot did not click. Try again.")
        return 2
    mp_input.click(x, y)
    time.sleep(0.5)
    print("Clicked once.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
