---
name: mac-ui-control
description: Control any macOS app from the terminal - click, double-click, right-click, drag, scroll, type text, send key combos, and inspect what UI element is under a screen point. Works with apps that expose no accessibility tree (Electron/CEF like CapCut, Slack, Discord) where AppleScript clicking fails. Use when asked to automate, click, drive, or interact with a Mac app, GUI, or desktop UI.
---

# macOS UI Control

`macpilot` posts real HID-level events via CGEvent, so **every** app receives them as genuine
input: native apps, Electron/CEF apps, browsers, and web page content inside them.

## Build (once)
```bash
cd ~/dev/macpilot && make && make install
```

## Permission (required)
Accessibility must be granted to **the terminal app** running this (Warp/Terminal/iTerm),
not to python or to macpilot itself.

- macOS 13+: System Settings → Privacy & Security → Accessibility
- macOS 12:  System Preferences → Security & Privacy → Privacy → Accessibility

Probe it:
```bash
osascript -e 'tell application "System Events" to tell process "Finder" to get position of window 1'
```
Failure is `(-25211) ... not allowed assistive access`. Some System Events calls succeed
*without* the grant, so always probe with a process-targeted call like this one.

## Commands
```bash
./macpilot screen                  # displays + Retina scale  <- run this FIRST
./macpilot pos                     # cursor position
./macpilot peek [X Y]              # what element is under the point
./macpilot move X Y
./macpilot click X Y [n] [left|right|middle]
./macpilot drag X1 Y1 X2 Y2 [ms]
./macpilot scroll DX DY [X Y]
./macpilot type "hello"
./macpilot key cmd+shift+4         # cmd shift alt ctrl fn
```

## THE COORDINATE RULE
`screencapture` writes **backing pixels** (e.g. 3584x2240). macpilot takes **logical points**
(e.g. 1792x1120). On a Retina display **divide screenshot coordinates by the scale factor**
(usually 2). `./macpilot screen` prints the exact factor. Getting this wrong is the single
most common failure — clicks land at half or double the intended position.

## Workflow: look, verify, then click
```bash
./macpilot screen                          # 1. learn the scale
screencapture -x /tmp/s.png              # 2. see the screen
# 3. find target in the image, divide pixel coords by scale
./macpilot peek 383 642                    # 4. CONFIRM what is there before clicking
./macpilot click 383 642 2                 # 5. act
screencapture -x /tmp/after.png          # 6. VERIFY it happened
```
Always `peek` before clicking somewhere new, and always screenshot after. Never claim an
action succeeded without visual confirmation.

## Why not AppleScript
`tell application "System Events" to click at {x,y}` returns a window reference and clicks
nothing in Chromium/CEF apps. Those apps render their UI as web content and expose no
AX elements to press. Only synthesized HID events work. This is why `macpilot` exists.

`peek` returns nothing for the same reason inside web/canvas content — that's expected and
tells you you're in a region where only pixel coordinates work.

## Gotchas
- **Secure input**: password fields block synthetic *keyboard* events. Mouse still works.
- **Login window / screensaver**: off limits entirely.
- **Drags are eased** over time — apps ignore instantaneous jumps. Give slow UIs more ms.
- **Focus**: activate the target app first (`osascript -e 'tell application "X" to activate'`),
  since events go to whatever is frontmost at that point.
- **Multi-display**: coordinates are global; `./macpilot screen` prints each display's origin.

## For web pages, prefer the browser
If the target is a page in Chrome, use the `claude-in-chrome` skill instead. It reads the
DOM, so it can click a named button rather than a pixel, and survives reflow and scrolling.
Use `macpilot` for native/Electron apps that expose nothing.

## Alternatives worth knowing
- **cliclick** (`brew install cliclick`) — mature, more complete, same CGEvent approach.
  Use it if you want something maintained; `macpilot` adds `peek` and the scale reporting.
- **Hammerspoon** — Lua desktop scripting, good for persistent hotkeys/daemons.
- **computer-use MCP servers** — accessibility-first with pixel fallback, exposed as agent
  tools. Better than shelling out if you'll do this a lot. See `reference/prior-art.md`.
