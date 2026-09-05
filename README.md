# macpilot

Control macOS apps from the shell or from Python. HID-level input via CGEvent, so **every**
app receives it as genuine input — including Electron/CEF apps (CapCut, Slack, Discord) and
browser page content, where AppleScript clicking silently does nothing.

Zero dependencies. One C file and a small Python package.

## Why

`osascript -e 'tell application "System Events" to click at {x,y}'` returns a window
reference and clicks *nothing* in Chromium-based apps — they render their UI as web content
and expose no accessibility elements to press. Only synthesized HID events reach them.

The modern alternative (computer-use MCP servers) requires **macOS 13+**; see
[docs/compatibility.md](docs/compatibility.md). On Monterey, this is the working option.

## Install

```bash
git clone https://github.com/Greenfire-solutions/macpilot.git
cd macpilot && make && make install     # -> ~/.local/bin/macpilot
```

Grant **Accessibility** to your *terminal app* (Warp/Terminal/iTerm), not to python:
- macOS 13+: System Settings → Privacy & Security → Accessibility
- macOS 12 : System Preferences → Security & Privacy → Privacy → Accessibility

Verify: `python3 -c "import macpilot; print(macpilot.check_permission())"`

## CLI

```bash
macpilot screen                  # displays + Retina scale   <- run this FIRST
macpilot peek 383 642            # what element is under the point
macpilot click 383 642 2         # double-click
macpilot drag 100 200 400 600 800
macpilot type "hello"
macpilot key cmd+shift+4
macpilot scroll 0 -300 900 500
macpilot pos / move X Y
```

## Python

```python
from macpilot import Session

s = Session(app="CapCut").focus()
s.look("before.png")
x, y = s.at(767, 1285)                 # screenshot pixels -> logical points
s.click(x, y, count=2, strict=False)   # peeks, asserts, clicks, waits
s.look("after.png")
```

Segmented for embedding in a larger tool:

```python
from macpilot import input, screen, inspect, engine

engine.require_permission()
screen.scale()                 # 2.0 on Retina
screen.to_points(767, 1285)    # (383.5, 642.5)
inspect.peek(383, 642)         # {'role': 'AXMenuBarItem', 'title': 'Warp'}
inspect.window_bounds("CapCut")
input.click(383, 642, 2)
```

| module | role |
|---|---|
| `engine`  | binary discovery/build, subprocess, permission probe |
| `screen`  | screenshots, display geometry, Retina point↔pixel math |
| `input`   | move, click, drag, scroll, type, key combos |
| `inspect` | accessibility peek, frontmost app, window bounds |
| `session` | `Session`: enforces look → verify → act → confirm |

## THE coordinate rule

`screencapture` writes **backing pixels** (3584×2240). macpilot takes **logical points**
(1792×1120). **Divide screenshot coordinates by the scale factor.** `macpilot screen`
prints it. Getting this wrong is the single most common failure — clicks land at half or
double the intended position.

## Limits

- **Secure input** (password fields) blocks synthetic *keyboard* events. Mouse still works.
- **Login window / screensaver**: off limits.
- **It sees pixels, not a DOM.** For web pages prefer browser automation that reads the DOM.
- **It moves your real cursor** and needs the target app frontmost.
- `peek` returns nothing inside web/canvas content — expected, and tells you you're in
  pixel-only territory.

## Docs
- [compatibility.md](docs/compatibility.md) — macOS version findings, tested matrix
- [permissions.md](docs/permissions.md) — what to grant and how to probe it
- [coordinates.md](docs/coordinates.md) — Retina math, multi-display
- [prior-art.md](docs/prior-art.md) — cliclick, Hammerspoon, MCP servers, and when to use them

## License
MIT
