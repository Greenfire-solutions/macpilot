"""Locates (and if needed builds) the macpilot binary, and runs it."""
from __future__ import annotations
import os, shutil, subprocess
from pathlib import Path

class PermissionError_(RuntimeError):
    """Accessibility not granted to the calling terminal app."""

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

def find_binary() -> Path:
    """bin/macpilot -> ~/.local/bin -> $PATH. Builds from source as a last resort."""
    cands = [_repo_root()/"bin"/"macpilot", Path.home()/".local/bin/macpilot"]
    which = shutil.which("macpilot")
    if which: cands.append(Path(which))
    for c in cands:
        if c.is_file() and os.access(c, os.X_OK): return c
    src = _repo_root()/"core"/"macpilot.c"
    if src.is_file():
        out = _repo_root()/"bin"/"macpilot"; out.parent.mkdir(exist_ok=True)
        subprocess.run(["clang","-O2","-o",str(out),str(src),
                        "-framework","ApplicationServices","-framework","Carbon"],check=True)
        return out
    raise FileNotFoundError("macpilot binary not found and core/macpilot.c is missing")

def run(*args: str, timeout: float = 30.0) -> str:
    r = subprocess.run([str(find_binary()), *map(str, args)],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"macpilot {' '.join(map(str,args))} failed: {r.stderr.strip()}")
    return r.stdout

def check_permission() -> bool:
    """True if Accessibility is granted. Probe must target a process, not System Events itself."""
    r = subprocess.run(["osascript","-e",
        'tell application "System Events" to tell process "Finder" to get position of window 1'],
        capture_output=True, text=True)
    return "not allowed assistive access" not in (r.stderr or "")

def require_permission() -> None:
    if not check_permission():
        raise PermissionError_(
            "Accessibility is not granted.\n"
            "  macOS 13+: System Settings > Privacy & Security > Accessibility\n"
            "  macOS 12 : System Preferences > Security & Privacy > Privacy > Accessibility\n"
            "Grant it to your TERMINAL app (Warp/Terminal/iTerm), not to python.")
