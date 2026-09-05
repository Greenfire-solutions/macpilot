#!/usr/bin/env python3
"""Worked example: open a project in a CEF app (CapCut) that AppleScript cannot click.

Demonstrates the full loop - focus, screenshot, convert coords, verify, click, confirm.
"""
import sys, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from macpilot import Session, inspect

APP = "CapCut"
CARD_PX = (767, 1285)          # position in a screencapture PNG (backing pixels)

def main():
    if not inspect.is_running(APP):
        inspect.activate(APP); time.sleep(10)
    s = Session(app=APP, strict=False).focus()   # strict=False: CEF exposes no AX elements
    before = s.look("/tmp/before.png")
    print("before:", before, "scale:", s.scale)
    x, y = s.at(*CARD_PX)
    print(f"pixel {CARD_PX} -> logical ({x:.0f},{y:.0f})")
    print("under it:", s.peek(x, y) or "no AX element (expected in CEF content)")
    s.click(x, y, count=2, settle=8.0)
    after = s.look("/tmp/after.png")
    print("after:", after, "- compare the two to confirm it opened")

if __name__ == "__main__":
    main()
