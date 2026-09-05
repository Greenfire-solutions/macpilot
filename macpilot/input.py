"""Mouse and keyboard. HID-level, so every app receives these as genuine input."""
from __future__ import annotations
from . import engine

def move(x: float, y: float) -> None: engine.run("move", x, y)
def position() -> tuple[float,float]:
    a,b = engine.run("pos").split(); return float(a), float(b)

def click(x: float, y: float, count: int = 1, button: str = "left") -> None:
    engine.run("click", x, y, count, button)

def double_click(x: float, y: float) -> None: click(x, y, 2)
def triple_click(x: float, y: float) -> None: click(x, y, 3)
def right_click(x: float, y: float) -> None: click(x, y, 1, "right")

def drag(x1: float, y1: float, x2: float, y2: float, ms: int = 500) -> None:
    """Eased over `ms`; apps ignore instantaneous jumps. Give slow UIs more time."""
    engine.run("drag", x1, y1, x2, y2, ms)

def scroll(dx: int, dy: int, x: float | None = None, y: float | None = None) -> None:
    engine.run("scroll", dx, dy, *(( x, y) if x is not None and y is not None else ()))

def type_text(text: str) -> None:
    """Unicode into the focused field. Blocked in secure-input (password) fields."""
    engine.run("type", text)

def key(combo: str) -> None:
    """e.g. 'cmd+s', 'cmd+shift+4'. Modifiers: cmd shift alt ctrl fn."""
    engine.run("key", combo)
