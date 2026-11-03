"""DEC-1045 in the CTO's tools: the secrets-scan switch (secrets_switch.py), the landing's and the close's gitleaks
step (land.py, close_build.py), and the nightly-only list in the selection (select_tests.py, nightly_only.txt).

Each tool is loaded from its candidate (<name>.candidate.py) while one stands beside it, else from the live file, so
the same tests hold after the CTO switches the candidates on. A stand-in `gitleaks` first on PATH logs each call.
Run: PYTHONPATH=<tree>/src python3 -m pytest -q -p no:cacheprovider tools/test_dec1045_switch.py
(GOV_TEST_TREE=<tree> names the tree the real list is checked against; default: this repository's root)."""
import importlib.util
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import secrets_switch as ss  # noqa: E402

TREE = Path(os.environ.get("GOV_TEST_TREE", HERE.parents[3]))


def load(name):
    path = HERE / f"{name}.candidate.py"
    path = path if path.is_file() else HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def fake(monkeypatch, tmp_path):
    """A stand-in gitleaks on PATH: logs its arguments, exits with the code in tmp_path/rc (0 by default)."""
    bindir, log = tmp_path / "bin", tmp_path / "calls.log"
    bindir.mkdir()
    (bindir / "gitleaks").write_text(f"#!/bin/sh\necho \"$@\" >> '{log}'\nexit $(cat '{tmp_path}/rc' 2>/dev/null || echo 0)\n")
    (bindir / "gitleaks").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")

    class F:
        def calls(self):
            return log.read_text().splitlines() if log.exists() else []

        def leaks(self):
            (tmp_path / "rc").write_text("1")
    return F()


def write_switch(root, text):
    p = Path(root) / ss.REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


# -- the switch
@pytest.mark.parametrize("text, on", [(None, True), ("", True), ("other: 1\n", True), ("scan: on\n", True),
                                      ("scan: off\n", False), ("scan: 'off'\n", False), ("# DEC-1045\nscan: off\n", False)])
def test_the_switch_absent_is_on_and_reads_on_and_off(tmp_path, text, on):
    if text is not None:
        write_switch(tmp_path, text)
    assert ss.scan_on(tmp_path) is on


@pytest.mark.parametrize("text", ["scan: maybe\n", "scan: 0\n", "scan: null\n", "scan: [\n", "- scan\n"])
def test_the_switch_refuses_any_other_value(tmp_path, text):
    write_switch(tmp_path, text)
    with pytest.raises(ss.SwitchError):
        ss.scan_on(tmp_path)


# -- land.py
@pytest.fixture
def land(monkeypatch, tmp_path):
    mod = load("land")
    (tmp_path / "orch/log").mkdir(parents=True)
    monkeypatch.setattr(mod, "ORCH", tmp_path / "orch")
    monkeypatch.setattr(mod, "git", lambda *a: "+ a changed line\n")
    return mod


def test_land_on_scans_the_change(land, fake):
    land.SCAN = True
    assert land.scan_change("W2-01", "c0ffee") is False
    assert [c.split()[0] for c in fake.calls()] == ["detect"]
    fake.leaks()
    assert land.scan_change("W2-01", "c0ffee") is True
    assert "gitleaks on the change: clean" in land.gitleaks_line()


def test_land_off_makes_no_gitleaks_call_and_its_record_names_it(land, fake):
    land.SCAN = False
    fake.leaks()
    assert land.scan_change("W2-01", "c0ffee") is False
    assert fake.calls() == []
    rec = land.close_record("W2-01", "DAEO-x", "LITE", {"commit": "a" * 40, "merge": "b" * 40, "record": "r"},
                            {"base": "c" * 40, "head": "d" * 40}, "not required", "given")
    assert "- gitleaks: off by configuration (DEC-1045)" in rec and "clean (checked" not in rec


def _land_main(land, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(land, "ROOT", tmp_path)
    monkeypatch.setattr(land, "sh", lambda *a, **k: pytest.fail(f"ran {a} before the switch refused"))
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-01", "--check", "--base", "HEAD"])
    with pytest.raises(SystemExit) as e:
        land.main()
    return e.value.code, capsys.readouterr().out


def test_land_bad_value_refuses_before_anything(land, fake, monkeypatch, tmp_path, capsys):
    write_switch(tmp_path, "scan: maybe\n")
    code, out = _land_main(land, monkeypatch, tmp_path, capsys)
    assert code == 2 and "REFUSED before anything was queued: the secrets-scan switch" in out
    assert fake.calls() == []


def test_land_off_is_named_at_the_start(land, monkeypatch, tmp_path, capsys):
    write_switch(tmp_path, "scan: off\n")
    monkeypatch.setattr(land, "ROOT", tmp_path)
    monkeypatch.setattr(land, "git", lambda *a: (_ for _ in ()).throw(SystemExit(9)))  # stop just after the switch
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-01", "--check", "--base", "HEAD"])
    with pytest.raises(SystemExit):
        land.main()
    assert "gitleaks: off by configuration (DEC-1045)" in capsys.readouterr().out and land.SCAN is False


# -- close_build.py
@pytest.fixture
def cb(monkeypatch, tmp_path):
    mod = load("close_build")
    monkeypatch.setattr(mod, "git", lambda *a, **k: "+ a changed line\n")
    return mod


def test_close_on_scans_the_merges_change(cb, fake, tmp_path):
    cb.SCAN = True
    assert cb.change_scan(tmp_path / "c.diff", ["m1"]) == "clean"
    assert [c.split()[0] for c in fake.calls()] == ["detect"] and not (tmp_path / "c.diff").exists()
    fake.leaks()
    assert cb.change_scan(tmp_path / "c.diff", ["m1"]) == "LEAKS"
    assert cb.gitleaks_line("clean") == "- gitleaks on the merge's change: clean"


def test_close_off_makes_no_gitleaks_call_and_its_record_names_it(cb, fake, tmp_path):
    cb.SCAN = False
    state = cb.change_scan(tmp_path / "c.diff", ["m1"])
    assert fake.calls() == [] and not (tmp_path / "c.diff").exists()
    assert cb.gitleaks_line(state).startswith("- gitleaks: off by configuration (DEC-1045)")


@pytest.mark.parametrize("text, code", [("scan: maybe\n", 4), ("scan: off\n", 7)])
def test_close_reads_the_switch_before_the_disk_gate_and_any_clone(cb, fake, monkeypatch, tmp_path, capsys, text, code):
    write_switch(tmp_path, text)
    monkeypatch.setenv("GOV_HEAVY_PRIORITY", "1")  # main() sets it; restored after the test
    monkeypatch.setattr(cb, "ROOT", tmp_path)
    monkeypatch.setattr(cb, "ORCH", tmp_path / "orch")
    monkeypatch.setattr(cb, "ticket_of", lambda w2: ("DAEO-x", "LITE"))
    monkeypatch.setattr(cb, "merge_of", lambda w2: "m1")
    monkeypatch.setattr(cb, "sh", lambda *a, **k: (_ for _ in ()).throw(SystemExit(7)))  # the disk gate: stop here
    monkeypatch.setattr(sys, "argv", ["close_build.py", "W2-01", "--dry"])
    with pytest.raises(SystemExit) as e:
        cb.main()
    out = capsys.readouterr().out
    assert e.value.code == code and fake.calls() == []
    if code == 4:
        assert "CLOSE REFUSED: the secrets-scan switch" in out
    else:
        assert "gitleaks: off by configuration (DEC-1045)" in out


# -- select_tests.py and nightly_only.txt
@pytest.fixture
def st():
    pytest.importorskip("gov.close.select")
    return load("select_tests")


def _tree(root):
    files = {"tests/unit/a/test_x.py": "def test_one():\n    pass\n",
             "tests/unit/secrets_check/test_real.py": "def test_g():\n    pass\n",
             "tests/unit/secrets_check/test_keep.py": "def test_k():\n    pass\n",
             "tests/unit/secrets_check/test_pool.py": "def test_width():\n    pass\n\ndef test_real_scan():\n    pass\n",
             "tests/unit/secrets_check/helper.py": "",
             "tests/acceptance/W2-69/test_a.py": "def test_a():\n    pass\n",
             "tests/acceptance/W2-69/conftest.py": "",
             "tests/acceptance/W2-70/test_b.py": "def test_b():\n    pass\n"}
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)


ENTRIES = [("tests/acceptance/W2-69/test_a.py", "runs gitleaks"), ("tests/unit/secrets_check/test_real.py", "real"),
           ("tests/unit/secrets_check/test_pool.py::test_real_scan", "one case"), ("tests/gone/test_old.py", "moved")]


def sel(*targets):
    return [{"target": t, "why": [{"reason": "OWN"}]} for t in targets]


def test_a_target_inside_an_entry_is_dropped_and_named(st, tmp_path):
    _tree(tmp_path)
    out = st.leave_out_nightly(tmp_path, sel("tests/acceptance/W2-69/test_a.py", "tests/acceptance/W2-70"), ENTRIES)
    assert [s["target"] for s in out["selected"]] == ["tests/acceptance/W2-70"]
    assert out["left_out"] == [{"entry": "tests/acceptance/W2-69/test_a.py", "why": "runs gitleaks",
                                "target": "tests/acceptance/W2-69/test_a.py"}]
    assert out["absent"] == ["tests/gone/test_old.py"]


def test_a_target_holding_entries_is_split_into_its_other_parts(st, tmp_path):
    _tree(tmp_path)
    out = st.leave_out_nightly(tmp_path, sel("tests/unit", "tests/acceptance/W2-69"), ENTRIES)
    assert [s["target"] for s in out["selected"]] == [
        "tests/unit/a", "tests/unit/secrets_check/test_keep.py", "tests/unit/secrets_check/test_pool.py::test_width"]
    assert {d["entry"] for d in out["left_out"]} == {e for e, _ in ENTRIES[:3]}
    assert all({"reason": "NIGHTLY_ONLY_SPLIT", "from": "tests/unit"} in s["why"] for s in out["selected"])
    assert out["ignore"] == ["tests/acceptance/W2-69/test_a.py", "tests/unit/secrets_check/test_real.py"]
    assert out["deselect"] == ["tests/unit/secrets_check/test_pool.py::test_real_scan"]


def test_a_selection_without_entries_is_unchanged(st, tmp_path):
    _tree(tmp_path)
    s = sel("tests/unit/a", "tests/acceptance/W2-70")
    out = st.leave_out_nightly(tmp_path, s, ENTRIES)
    assert out["selected"] == s and out["left_out"] == []


def test_the_list_is_read_with_its_reasons_and_an_absent_list_leaves_nothing_out(st, tmp_path):
    p = tmp_path / "list.txt"
    p.write_text("# a comment  # with a hash\n\ntests/a/test_x.py  # why x\ntests/b/test_y.py::test_z # why z\n")
    assert st.nightly_only(p) == [("tests/a/test_x.py", "why x"), ("tests/b/test_y.py::test_z", "why z")]
    assert st.nightly_only(tmp_path / "none.txt") is None


def test_every_entry_of_the_real_list_has_a_reason_exists_and_runs_gitleaks(st):
    entries = st.nightly_only()
    assert entries, "nightly_only.txt is empty or absent"
    for entry, why in entries:
        file = TREE / entry.partition("::")[0]
        assert why, f"{entry}: no reason"
        assert file.is_file(), f"{entry}: not in {TREE}"
        text = file.read_text(encoding="utf-8")
        suite = file.parent
        support = " ".join(p.read_text(encoding="utf-8") for p in suite.glob("*.py") if not p.name.startswith("test_"))
        assert "gitleaks" in text or "gitleaks" in support, f"{entry}: nothing in it or its suite runs gitleaks"
        if "::" in entry:
            assert entry.partition("::")[2] in st._test_names(file), f"{entry}: no such test"
