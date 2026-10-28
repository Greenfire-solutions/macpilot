"""macpilot - control macOS apps from Python or the shell.

HID-level input via CGEvent, so it works with apps that expose no accessibility tree
(Electron/CEF: CapCut, Slack, Discord) where AppleScript clicking silently fails.

    from macpilot import Session
    s = Session(app="CapCut").focus()
    s.look("before.png")
    x, y = s.at(px, py)           # a screenshot pixel you checked -> logical points
    s.click(x, y, count=2, strict=False)
    s.look("after.png")

Low-level:
    from macpilot import input, screen, inspect
    inspect.peek(383, 642)
    input.click(383, 642, 2)
"""
from . import engine, screen, input, inspect, session
from .session import Session
from .engine import check_permission, require_permission

__all__ = ["engine","screen","input","inspect","session","Session",
           "check_permission","require_permission"]
__version__ = "0.1.0"
