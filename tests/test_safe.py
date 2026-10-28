#!/usr/bin/env python3
"""MacPilot checks that are safe to run on any Mac: they never click, type, move or scroll.

Run:  python3 tests/test_safe.py     (or: make test)
The only real binary commands used are read-only: access, screen, pos, and the usage text.
"""
import io, os, subprocess, sys, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import macpilot
from macpilot import engine
BIN = ROOT / "bin" / "macpilot"

# Anything that would act on the real screen fails the test instead.
def _forbidden(*a, **k):
    raise AssertionError("a test tried to act on the real screen")


class Binary(unittest.TestCase):
    def test_prebuilt_binary_is_in_the_folder(self):
        self.assertTrue(BIN.is_file() and os.access(BIN, os.X_OK), "bin/macpilot must ship ready-made")

    def test_binary_is_universal(self):
        out = subprocess.run(["lipo", "-info", str(BIN)], capture_output=True, text=True).stdout
        self.assertIn("x86_64", out); self.assertIn("arm64", out)

    def test_binary_is_signed_adhoc_at_least(self):
        # Apple Silicon refuses to run an arm64 program with no signature at all.
        r = subprocess.run(["codesign", "-v", str(BIN)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_binary_matches_source(self):
        self.assertGreaterEqual(BIN.stat().st_mtime, (ROOT / "core" / "macpilot.c").stat().st_mtime - 1,
                                "core/macpilot.c is newer than bin/macpilot: run make")

    def test_usage_says_macpilot(self):
        r = subprocess.run([str(BIN)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertTrue(r.stderr.startswith("macpilot "), r.stderr[:40])
        self.assertNotIn("macuse", r.stderr)
        self.assertIn("access", r.stderr)

    def test_screen_is_read_only_and_parses(self):
        d = macpilot.screen.displays()
        self.assertTrue(d and d[0].width > 0 and d[0].scale >= 1)

    def test_access_exit_code_is_honest(self):
        r = subprocess.run([str(BIN), "access"], capture_output=True, text=True)
        self.assertIn(r.returncode, (0, 3))
        self.assertEqual(r.stdout.startswith("granted"), r.returncode == 0)


class Permission(unittest.TestCase):
    def _run_with(self, **kw):
        res = mock.Mock(**kw)
        with mock.patch.object(engine.subprocess, "run", return_value=res) as m:
            ok = engine.check_permission()
        self.assertEqual(m.call_args[0][0][1], "access")
        return ok

    def test_granted_only_on_exit_zero(self):
        self.assertTrue(self._run_with(returncode=0, stdout="granted\n", stderr=""))

    def test_not_granted_on_exit_three(self):
        self.assertFalse(self._run_with(returncode=3, stdout="not granted\n", stderr=""))

    def test_any_other_failure_is_not_granted(self):
        # The old probe returned True whenever osascript failed for a reason other than
        # "not allowed assistive access". Every failure must now count as NOT granted.
        for code in (1, 2, 139, -9):
            self.assertFalse(self._run_with(returncode=code, stdout="", stderr="boom"))

    def test_missing_binary_or_timeout_is_not_granted(self):
        for exc in (FileNotFoundError("gone"), subprocess.TimeoutExpired("x", 10), OSError("x")):
            with mock.patch.object(engine.subprocess, "run", side_effect=exc):
                self.assertFalse(engine.check_permission())

    def test_require_permission_raises_plain_message(self):
        with mock.patch.object(engine, "check_permission", return_value=False):
            with self.assertRaises(engine.PermissionError_) as cm:
                engine.require_permission()
        self.assertIn("Privacy & Security > Accessibility", str(cm.exception))


class Example(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "examples"))
        import look_then_click
        self.ex = look_then_click
        self.patches = [
            mock.patch.object(look_then_click.engine, "check_permission", return_value=True),
            mock.patch.object(look_then_click.mp_input, "position", return_value=(120.0, 80.0)),
            mock.patch.object(look_then_click.inspect, "peek", return_value={"role": "AXButton", "title": "Save"}),
        ]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in self.patches: p.stop()

    def _run(self, answers, argv=()):
        out = io.StringIO()
        with mock.patch("builtins.input", side_effect=list(answers)), mock.patch("sys.stdout", out):
            code = self.ex.main(list(argv))
        return code, out.getvalue()

    def test_no_fixed_coordinates(self):
        src = (ROOT / "examples" / "look_then_click.py").read_text()
        self.assertNotIn("767", src); self.assertNotIn("1285", src)
        self.assertFalse((ROOT / "examples" / "open_app_project.py").exists())

    def test_saying_no_never_clicks(self):
        with mock.patch.object(self.ex.mp_input, "click", side_effect=_forbidden):
            for ans in ("n", "", "yes please", "N"):
                code, out = self._run(["", ans])
                self.assertEqual(code, 0); self.assertIn("Nothing was clicked", out)

    def test_look_only_never_asks_or_clicks(self):
        with mock.patch.object(self.ex.mp_input, "click", side_effect=_forbidden):
            code, out = self._run([""], ["--look"])
        self.assertEqual(code, 0); self.assertIn("Save", out); self.assertIn("nothing was clicked", out)

    def test_yes_clicks_once_at_the_checked_spot(self):
        with mock.patch.object(self.ex.mp_input, "click") as click, mock.patch.object(self.ex.time, "sleep"):
            code, _ = self._run(["", "y"])
        self.assertEqual(code, 0); click.assert_called_once_with(120.0, 80.0)

    def test_target_changed_means_no_click(self):
        with mock.patch.object(self.ex.inspect, "peek", side_effect=[{"title": "Save"}, {"title": "Delete"}]), \
             mock.patch.object(self.ex.mp_input, "click", side_effect=_forbidden):
            code, out = self._run(["", "y"])
        self.assertEqual(code, 2); self.assertIn("did not click", out)

    def test_without_permission_it_stops(self):
        with mock.patch.object(self.ex.engine, "check_permission", return_value=False), \
             mock.patch.object(self.ex.mp_input, "click", side_effect=_forbidden):
            code, out = self._run([])
        self.assertEqual(code, 1); self.assertIn("Accessibility", out)


class BuyerText(unittest.TestCase):
    FILES = ["README.md", "READ ME FIRST.txt", "Start MacPilot.command",
             "skills/mac-ui-control/SKILL.md", "docs/permissions.md"]

    def test_no_em_dashes_and_no_private_paths(self):
        for f in self.FILES:
            t = (ROOT / f).read_text()
            self.assertNotIn("—", t, f)
            self.assertNotIn("~/dev/macpilot", t, f)
            self.assertNotIn("git clone https://github.com/Greenfire-solutions", t, f)

    def test_readme_states_the_mit_license(self):
        t = (ROOT / "README.md").read_text()
        self.assertIn("MIT", t); self.assertNotIn("do not resell", t)
        self.assertTrue((ROOT / "LICENSE").read_text().startswith("MIT License"))

    def test_start_script_never_acts_on_screen(self):
        t = (ROOT / "Start MacPilot.command").read_text()
        for verb in ("click", "type ", "key ", "drag", "scroll", "move "):
            self.assertNotIn(f'"$BIN" {verb}', t)


if __name__ == "__main__":
    unittest.main(verbosity=1)
