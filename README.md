# MacPilot

**What it is for:** MacPilot lets a script, or an AI assistant like Claude Code, press buttons
on your Mac for you (click, double-click, drag, scroll, type, key combinations) in any app,
and tells you what is under a spot on the screen before anything is clicked. It works in apps
that normal Mac automation cannot press, such as CapCut, Slack and Discord.

It is a small command you run in Terminal or call from Python. It has no window, and it only
does something when you or your script tells it to.

**New here? Open `READ ME FIRST.txt` and double-click `Start MacPilot`.** That is the whole setup.

## Install

1. On GitHub press the green **Code** button, then **Download ZIP** (or `git clone
   https://github.com/Greenfire-solutions/macpilot.git`). Unzip it and move the folder
   somewhere you keep your work, for example Documents.
2. Double-click **Start MacPilot** (first time: right-click > Open > Open on macOS 12 to 14;
   on macOS 15+ allow it under System Settings > Privacy & Security > Open Anyway).
3. It checks the program runs, walks you through the Accessibility permission, and offers to
   install the `macpilot` command. It never clicks anything.

The program is already built: `bin/macpilot` runs on both Intel and Apple Silicon Macs
(macOS 12 or newer). **No Xcode, no developer tools, nothing to compile.**

### The Accessibility permission
macOS ignores clicks from any program until you allow it. Turn it on for the app you type
commands in (Terminal, iTerm or Warp), not for python and not for MacPilot:
- macOS 13+: System Settings > Privacy & Security > Accessibility
- macOS 12 : System Preferences > Security & Privacy > Privacy > Accessibility (unlock the padlock)

Then quit that app completely and reopen it. Check it with `bin/macpilot access`
(prints `granted`, exit code 0) or in Python `macpilot.check_permission()`.

### Optional: rebuild from source
Only if you change `core/macpilot.c`. Needs Apple's free Command Line Tools
(`xcode-select --install`), then `make` (and `make install` to copy it to `~/.local/bin`).

## Why

`osascript -e 'tell application "System Events" to click at {x,y}'` returns a window
reference and clicks *nothing* in Chromium-based apps: they render their UI as web content
and expose no accessibility elements to press. Only synthesized HID events reach them.

The modern alternative (computer-use MCP servers) requires **macOS 13+**; see
[docs/compatibility.md](docs/compatibility.md). On Monterey, this is the working option.

## CLI

Inside the MacPilot folder use `bin/macpilot`; after the optional install, just `macpilot`.

```bash
macpilot access                  # is Accessibility granted? exit 0 = yes
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

Run Python from inside the MacPilot folder (or add the folder to `PYTHONPATH`).
Start with the safe example, which looks first and asks before it clicks:

```bash
python3 examples/look_then_click.py --look   # only describes what is under the mouse
python3 examples/look_then_click.py          # describes it, then asks before clicking
```

Never click a fixed position you have not checked: positions differ on every Mac and layout.
Find the target first (`peek`, `inspect.window_bounds`, a screenshot), then click:

```python
from macpilot import Session, inspect

s = Session(app="TextEdit").focus()              # refuses to start without Accessibility
box = inspect.window_bounds("TextEdit")          # (x, y, w, h) of its front window
x, y = box[0] + box[2] / 2, box[1] + 40          # a spot worked out from the window
print(s.peek(x, y))                              # check what is there first
s.click(x, y, expect="AXButton")                 # refuses if it is not what you expected
```

Segmented for embedding in a larger tool:

```python
from macpilot import input, screen, inspect, engine

engine.require_permission()
screen.scale()                 # 2.0 on Retina
screen.to_points(767, 1285)    # (383.5, 642.5)
inspect.peek(383, 642)         # {'role': 'AXMenuBarItem', 'title': 'Warp'}
inspect.window_bounds("CapCut")
input.click(383, 642)            # only after peek showed the right thing
```

| module | role |
|---|---|
| `engine`  | finds bin/macpilot, runs it, proves the Accessibility grant |
| `screen`  | screenshots, display geometry, Retina point and pixel math |
| `input`   | move, click, drag, scroll, type, key combos |
| `inspect` | accessibility peek, frontmost app, window bounds |
| `session` | `Session`: enforces look, verify, act, confirm |

## THE coordinate rule

`screencapture` writes **backing pixels** (3584×2240). macpilot takes **logical points**
(1792×1120). **Divide screenshot coordinates by the scale factor.** `macpilot screen`
prints it. Getting this wrong is the single most common failure: clicks land at half or
double the intended position.

## Limits

- **Secure input** (password fields) blocks synthetic *keyboard* events. Mouse still works.
- **Login window / screensaver**: off limits.
- **It sees pixels, not a DOM.** For web pages prefer browser automation that reads the DOM.
- **It moves your real cursor** and needs the target app frontmost.
- `peek` returns nothing inside web/canvas content: that is expected, and tells you you're in
  pixel-only territory.

## Docs
- [compatibility.md](docs/compatibility.md): macOS version findings, tested matrix
- [permissions.md](docs/permissions.md): what to grant and how to check it
- [coordinates.md](docs/coordinates.md): Retina math, multi-display
- [prior-art.md](docs/prior-art.md): cliclick, Hammerspoon, MCP servers, and when to use them

## Using it with Claude Code
Copy `skills/mac-ui-control` into `~/.claude/skills/`. Claude Code then knows to look,
check and only then click.

## License
MIT, see `LICENSE`: free to use, change and share.
