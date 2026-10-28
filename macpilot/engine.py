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
        try:
            subprocess.run(["clang","-O2","-o",str(out),str(src),
                            "-framework","ApplicationServices","-framework","Carbon"],check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            raise FileNotFoundError(
                "bin/macpilot is missing and could not be rebuilt (rebuilding needs Apple's "
                "Command Line Tools: run  xcode-select --install ). The easiest fix is to "
                "unzip MacPilot again so bin/macpilot is back.") from e
        return out
    raise FileNotFoundError("macpilot binary not found and core/macpilot.c is missing")

def run(*args: str, timeout: float = 30.0) -> str:
    r = subprocess.run([str(find_binary()), *map(str, args)],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"macpilot {' '.join(map(str,args))} failed: {r.stderr.strip()}")
    return r.stdout

def check_permission() -> bool:
    """True only when Accessibility is PROVEN granted to the calling terminal app.

    Runs `macpilot access`, which does a harmless read that only works with the grant
    (it never clicks and never pops up a dialog). Exit code 0 means granted; anything
    else, including a missing binary, a crash or a timeout, counts as NOT granted.
    """
    try:
        r = subprocess.run([str(find_binary()), "access"],
                           capture_output=True, text=True, timeout=10)
    except Exception:
        return False
    return r.returncode == 0

def require_permission() -> None:
    if not check_permission():
        raise PermissionError_(
            "Accessibility is not granted (or could not be proven).\n"
            "  macOS 13+: System Settings > Privacy & Security > Accessibility\n"
            "  macOS 12 : System Preferences > Security & Privacy > Privacy > Accessibility\n"
            "Turn it on for the app you type commands in (Terminal, iTerm or Warp), not for python.\n"
            "Then quit that app completely and open it again.")
