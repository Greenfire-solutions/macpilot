"""Look before you click: accessibility introspection and app/window geometry."""
from __future__ import annotations
import subprocess
from . import engine

def peek(x: float | None = None, y: float | None = None) -> dict[str,str]:
    """What UI element is under this point.

    Empty dict means no accessibility element - typically web/canvas content, where only
    pixel coordinates work. That is information, not an error.
    """
    out = engine.run("peek", *(( x, y) if x is not None else ()))
    if "no accessibility element" in out: return {}
    d = {}
    for line in out.splitlines()[1:]:
        parts = line.strip().split(None, 1)
        if len(parts) == 2: d[parts[0]] = parts[1]
    return d

def _osa(script: str) -> str:
    r = subprocess.run(["osascript","-e",script], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""

def frontmost_app() -> str:
    return _osa('tell application "System Events" to name of first process whose frontmost is true')

def activate(app: str) -> None:
    _osa(f'tell application "{app}" to activate')

def window_bounds(app: str, index: int = 1) -> tuple[float,float,float,float] | None:
    """(x, y, w, h) in logical points, or None if the app has no such window."""
    pos = _osa(f'tell application "System Events" to tell process "{app}" '
               f'to get position of window {index}')
    siz = _osa(f'tell application "System Events" to tell process "{app}" '
               f'to get size of window {index}')
    if not pos or not siz: return None
    px,py = [float(v) for v in pos.split(", ")]
    sw,sh = [float(v) for v in siz.split(", ")]
    return px,py,sw,sh

def is_running(app: str) -> bool:
    return subprocess.run(["pgrep","-x",app], capture_output=True).returncode == 0
