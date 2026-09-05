"""High-level driver enforcing the look -> verify -> act -> confirm loop.

The failure mode this exists to prevent: clicking a coordinate you never checked and
reporting success you never observed.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from pathlib import Path
from . import engine, screen, input as _input, inspect as _inspect

@dataclass
class Session:
    app: str | None = None
    scale: float = field(default_factory=screen.scale)
    shots: list[Path] = field(default_factory=list)
    strict: bool = True          # refuse clicks on points with no AX element

    def __post_init__(self) -> None:
        engine.require_permission()

    def focus(self, app: str | None = None) -> "Session":
        target = app or self.app
        if target:
            _inspect.activate(target); time.sleep(1.0); self.app = target
        return self

    def look(self, name: str | None = None) -> Path:
        p = screen.capture(name); self.shots.append(p); return p

    def at(self, px: float, py: float) -> tuple[float,float]:
        """Screenshot pixel -> logical point."""
        return screen.to_points(px, py, self.scale)

    def peek(self, x: float, y: float) -> dict[str,str]:
        return _inspect.peek(x, y)

    def click(self, x: float, y: float, count: int = 1, button: str = "left",
              expect: str | None = None, settle: float = 1.0) -> dict[str,str]:
        """Peek, optionally assert what's there, click, then let the UI settle.

        `expect` is matched case-insensitively against the element's role/title/value.
        Returns what was under the point before clicking.
        """
        el = self.peek(x, y)
        if expect is not None:
            blob = " ".join(el.values()).lower()
            if expect.lower() not in blob:
                raise AssertionError(
                    f"expected {expect!r} at ({x},{y}) but found {el or 'no AX element'}")
        elif self.strict and not el:
            raise AssertionError(
                f"no accessibility element at ({x},{y}). This is normal for web/canvas "
                f"content - pass strict=False or use expect=None with Session(strict=False).")
        _input.click(x, y, count, button); time.sleep(settle)
        return el

    def drag(self, x1,y1,x2,y2, ms: int = 500, settle: float = 0.6):
        _input.drag(x1,y1,x2,y2,ms); time.sleep(settle)

    def type_text(self, text: str, settle: float = 0.3):
        _input.type_text(text); time.sleep(settle)

    def key(self, combo: str, settle: float = 0.3):
        _input.key(combo); time.sleep(settle)

    def scroll(self, dx: int, dy: int, x=None, y=None, settle: float = 0.4):
        _input.scroll(dx,dy,x,y); time.sleep(settle)
