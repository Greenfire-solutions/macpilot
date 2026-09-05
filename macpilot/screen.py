"""Screenshots and the Retina coordinate conversion that everything else depends on."""
from __future__ import annotations
import re, subprocess, tempfile
from dataclasses import dataclass
from pathlib import Path
from . import engine

@dataclass(frozen=True)
class Display:
    index: int; width: float; height: float
    x: float; y: float; scale: float

def displays() -> list[Display]:
    out, res = engine.run("screen"), []
    for m in re.finditer(
        r"display (\d+): logical (\d+)x(\d+) at \((-?\d+),(-?\d+)\).*?scale ([\d.]+)", out):
        i,w,h,x,y,s = m.groups()
        res.append(Display(int(i),float(w),float(h),float(x),float(y),float(s)))
    return res

def scale() -> float:
    d = displays()
    return d[0].scale if d else 1.0

def capture(path: str | Path | None = None) -> Path:
    """Full-screen capture. NOTE: this writes BACKING pixels, not logical points."""
    p = Path(path) if path else Path(tempfile.mkstemp(suffix=".png")[1])
    subprocess.run(["screencapture","-x",str(p)], check=True)
    return p

def to_points(px: float, py: float, s: float | None = None) -> tuple[float,float]:
    """Screenshot pixel -> logical point. THE conversion; getting it wrong halves/doubles clicks."""
    s = s if s is not None else scale()
    return px/s, py/s

def from_points(x: float, y: float, s: float | None = None) -> tuple[float,float]:
    s = s if s is not None else scale()
    return x*s, y*s
