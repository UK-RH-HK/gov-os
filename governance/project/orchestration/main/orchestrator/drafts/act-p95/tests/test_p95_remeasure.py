"""ACT-P95-1's tests: red on the maximum, green on the p95.

The planted day (tools/plant_samples.py) has a maximum of 9.5 GB and a p95 under 2.5 GB. Every test that pins the
figure fails on a tool that writes the maximum (the rehearsal runs the suite against such a mutant and expects it red).

Environment: P95_TOOLS (the folder holding p95_remeasure.py, apply.sh and plant_samples.py; default: ../tools),
P95_SRC (a copy of the repository's src/, for the product's own reader and `--remeasure`; the rehearsal sets it).
Nothing here touches the real HOME: every home is a planted folder under pytest's tmp_path.
"""
import datetime
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
TOOLS = Path(os.environ.get("P95_TOOLS", HERE.parent / "tools"))
SRC = os.environ.get("P95_SRC")
REAL_GATE = os.environ.get("P95_GATE")  # a copy of the live gate file, when the rehearsal has one; else a planted one


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module


tool, plant = load("p95_remeasure"), load("plant_samples")

PLANTED_GATE = {
    "memory_floor_bytes": {"value": 3221225472, "date": "2026-10-29", "source": "DEC-942 item 2"},
    "working_size_bytes": {"value": 2191601664, "date": "2026-10-29", "source": "DEC-947 item 2"},
    "verification_peak_bytes": {"value": 7582199808, "date": "2026-10-29", "source": "DEC-947 item 1"},
    "rebuild_peak_bytes": {"value": 7582199808, "date": "2026-11-01", "source": "DEC-1001 (d)"},
    "disk_floor_bytes": {"value": 107374182400, "date": "2026-10-28", "source": "DEC-898 item 1"},
    "inode_floor": {"value": 10000000, "date": "2026-10-28", "source": "DEC-898 item 1"},
    "verification_lock": {"value": "/tmp/gov-os-verify.lock", "date": "2026-10-29", "source": "DEC-947 item 1"},
    "gpu_margin": {"value": 0.1, "date": "2026-10-29", "source": "DEC-950 item 2"},
    "oom_floor_bytes": {"value": 2147483648, "date": "2026-10-29", "source": "DEC-947 item 5"},
    "heavy_slots": {"value": 3, "date": "2026-10-31", "source": "DEC-979 item 1 D1"},
    "gpu_shares": {"value": {"embedder_mib": 3584, "reranker_mib": 3584}, "date": "2026-11-02", "source": "DEC-1032"},
    "embedding_servers": {"shared": {"cpus": "12-19", "nice": 10}, "query": {"cpus": "8-11", "nice": 0, "device": "gpu"},
                          "date": "2026-11-02", "source": "ACT-OLLAMA-CAP-1"},
}
TODAY = "2099-01-01"
PARAMS = {"since": None, "date": TODAY, "min_samples": 40, "min_hours": 6.0, "pct": 95, "method": "nearest rank"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def gate_bytes() -> bytes:
    if REAL_GATE:
        return Path(REAL_GATE).read_bytes()
    return tool.dumps(PLANTED_GATE)


def clean_env(home, **extra):
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": str(home), "PYTHONDONTWRITEBYTECODE": "1"}
    env.update(extra)
    return env


@pytest.fixture
def day(tmp_path):
    """A planted home with the gate file and the planted day's samples; the samples' bytes and lines."""
    home = tmp_path / "home"
    machine = home / ".gov-os" / "machine"
    machine.mkdir(parents=True)
    (machine / "gate.json").write_bytes(gate_bytes())
    os.chmod(machine / "gate.json", 0o600)
    samples = plant.text()
    (machine / "samples.jsonl").write_text(samples)
    return home, samples


def build(tmp_path, home, **over):
    out = tmp_path / "bundle"
    params = {**PARAMS, **over}
    argv = ["build", "--out", str(out), "--samples", str(home / ".gov-os/machine/samples.jsonl"),
            "--gate", str(home / ".gov-os/machine/gate.json"), "--date", params["date"],
            "--min-samples", str(params["min_samples"]), "--min-hours", str(params["min_hours"])]
    if params["since"]:
        argv += ["--since", params["since"]]
    rc = tool.main(argv)
    return rc, out


def apply_sh(bundle, home, step):
    p = subprocess.run(["bash", str(bundle / "apply.sh"), step], env=clean_env(home), capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# --- the percentile and the population ---------------------------------------------------------------------------------

def test_nearest_rank_is_the_ceil_of_95_percent_of_n_th_smallest():
    assert tool.nearest_rank(list(range(1, 21))) == 19          # ceil(19.0) = 19th of 20
    assert tool.nearest_rank(list(range(1, 101))) == 95
    assert tool.nearest_rank(list(range(100, 0, -1))) == 95     # order does not matter
    assert tool.nearest_rank([7]) == 7
    assert tool.nearest_rank([5, 5, 5, 9]) == 9                 # ceil(3.8) = 4th: with n < 20 the p95 is the maximum
    assert tool.nearest_rank(list(range(1, 193))) == 183        # the planted day: ceil(182.4) = 183


def test_the_percentile_of_the_planted_day_is_not_its_maximum():
    lines = tool.read_lines(plant.text().encode())
    _, outside, _ = tool.populations(lines)
    assert len(outside) == 192
    assert max(outside) == 9_500_000_000
    p95 = tool.nearest_rank(outside)
    assert p95 < 2_500_000_000 < max(outside)
    assert p95 in outside  # an observed size


def test_the_population_is_the_products_own():
    """Slot holders, verification-time samples, bools and strings are out; parity with measure.figures()."""
    lines = tool.read_lines(plant.text().encode())
    every, outside, by_role = tool.populations(lines)
    assert len(every) == 192 + 6  # six verification-time samples (i = 9, 25, 41, 57, 73, 89)
    assert len(outside) == 192
    assert sum(len(v) for v in by_role.values()) == 192
    assert 12_000_000_000 not in every and 15_000_000_000 in every and 15_000_000_000 not in outside
    if not SRC:
        pytest.skip("P95_SRC (a copy of src/) is not set: the parity with the product is not checked here")
    sys.path.insert(0, SRC)
    sys.dont_write_bytecode = True
    from gov.resources import measure
    product = measure.figures(lines)
    assert product["working_size_bytes"] == (max(outside), len(outside))
    assert product["verification_peak_bytes"] == (max(every), len(every))


def test_since_cuts_the_day():
    lines = tool.read_lines(plant.text().encode(), since="2026-11-11T12:00:00+00:00")
    assert 0 < len(lines) < 96
    assert min(line["time"] for line in lines) >= "2026-11-11T12:00:00+00:00"


# --- the figure the bundle writes --------------------------------------------------------------------------------------

def test_the_product_writes_the_maximum_and_the_bundle_writes_the_p95(tmp_path, day):
    if not SRC:
        pytest.skip("P95_SRC is not set")
    home, samples = day
    # the product's own --remeasure, in a copy of the planted home: the maximum (the fault this ACT works round)
    twin = tmp_path / "twin"
    (twin / ".gov-os").mkdir(parents=True)
    import shutil
    shutil.copytree(home / ".gov-os" / "machine", twin / ".gov-os" / "machine")
    p = subprocess.run([sys.executable, "-m", "gov.cli.main", "resources", "--remeasure", "--json"], cwd=SRC + "/..",
                       env=clean_env(twin, PYTHONPATH=SRC), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    written = json.loads((twin / ".gov-os/machine/gate.json").read_text())["working_size_bytes"]["value"]
    assert written == 9_500_000_000
    # the bundle: the p95
    rc, bundle = build(tmp_path, home)
    assert rc == 0
    after = json.loads((bundle / "after" / "home" / ".gov-os/machine/gate.json").read_text())
    assert after["working_size_bytes"]["value"] == 2_475_000_000
    assert after["working_size_bytes"]["value"] != written


def test_the_after_file_differs_from_the_before_in_one_key_only(tmp_path, day):
    home, _ = day
    rc, bundle = build(tmp_path, home)
    assert rc == 0
    before = json.loads((bundle / "before/home/.gov-os/machine/gate.json").read_text())
    after = json.loads((bundle / "after/home/.gov-os/machine/gate.json").read_text())
    assert list(before) == list(after)  # same keys, same order
    changed = [k for k in before if before[k] != after[k]]
    assert changed == ["working_size_bytes"]
    entry = after["working_size_bytes"]
    assert entry["date"] == TODAY and entry["value"] == 2_475_000_000
    assert entry["source"].startswith("ACT-P95-1") and "192 session samples" in entry["source"]
    assert "p95 (nearest rank)" in entry["source"]
    assert (bundle / "after/home/.gov-os/machine/gate.json").read_bytes() == tool.dumps(after)


def test_the_bundle_is_reproduced_by_verify_and_a_tamper_is_caught(tmp_path, day):
    home, _ = day
    rc, bundle = build(tmp_path, home)
    assert tool.verify(bundle) == []
    after = bundle / "after/home/.gov-os/machine/gate.json"
    good = after.read_bytes()
    after.write_bytes(good.replace(b"2475000000", b"9500000000"))  # the maximum slipped in
    assert tool.verify(bundle) != []
    after.write_bytes(good)
    ev = bundle / "evidence/samples.jsonl"
    ev.write_bytes(ev.read_bytes().replace(b"6000000000", b"1600000000"))  # the evidence altered
    assert tool.verify(bundle) != []


@pytest.mark.parametrize("over,words", [
    ({"min_samples": 500}, "fewer than the 500"),
    ({"min_hours": 20.0}, "span"),
])
def test_a_thin_or_short_day_is_refused_and_nothing_is_written(tmp_path, day, capsys, over, words):
    home, _ = day
    rc, bundle = build(tmp_path, home, **over)
    assert rc == 2
    assert words in capsys.readouterr().err
    assert not bundle.exists()


def test_a_day_of_nineteen_samples_is_refused_by_the_default_floor(tmp_path, day, capsys):
    home, _ = day
    (home / ".gov-os/machine/samples.jsonl").write_text(plant.text(count=10))  # 20 session samples, 45 minutes
    rc, _ = build(tmp_path, home)
    assert rc == 2


def test_an_unreadable_or_oddly_formed_input_is_refused(tmp_path, day, capsys):
    home, _ = day
    machine = home / ".gov-os/machine"
    (machine / "samples.jsonl").write_text(plant.text() + "not json\n")
    assert build(tmp_path, home)[0] == 2
    (machine / "samples.jsonl").write_text(plant.text())
    gate = json.loads((machine / "gate.json").read_text())
    (machine / "gate.json").write_text(json.dumps(gate))  # not the product's form: one line
    assert build(tmp_path, home)[0] == 2
    del gate["working_size_bytes"]
    (machine / "gate.json").write_bytes(tool.dumps(gate))
    assert build(tmp_path, home)[0] == 2


def test_the_after_file_loads_clean_in_the_product_and_is_not_due(tmp_path, day):
    if not SRC:
        pytest.skip("P95_SRC is not set")
    home, _ = day
    rc, bundle = build(tmp_path, home, date="2026-11-11")
    probe = ("import datetime, json, sys\n"
             f"sys.path.insert(0, {SRC!r})\n"
             "from gov.resources import config\n"
             "c = config.load(today=datetime.date(2026, 11, 12))\n"
             "print(json.dumps([c['faults'], c['values']['working_size_bytes'], c['due']]))\n")
    gate = bundle / "after/home/.gov-os/machine/gate.json"
    target = tmp_path / "loadhome" / ".gov-os" / "machine"
    target.mkdir(parents=True)
    (target / "gate.json").write_bytes(gate.read_bytes())
    p = subprocess.run([sys.executable, "-B", "-c", probe], env=clean_env(tmp_path / "loadhome"), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    faults, value, due = json.loads(p.stdout)
    assert faults == [] and value == 2_475_000_000 and "working_size_bytes" not in due


# --- apply.sh ---------------------------------------------------------------------------------------------------------

def test_apply_check_apply_verify_undo_cycle_keeps_the_mode_and_leaves_no_temp_file(tmp_path, day):
    home, _ = day
    rc, bundle = build(tmp_path, home)
    gate = home / ".gov-os/machine/gate.json"
    before = gate.read_bytes()
    entries = sorted(os.listdir(gate.parent))
    assert apply_sh(bundle, home, "check")[0] == 0
    assert apply_sh(bundle, home, "verify")[0] == 3
    assert apply_sh(bundle, home, "undo")[0] == 0 and gate.read_bytes() == before  # nothing to undo
    assert apply_sh(bundle, home, "apply")[0] == 0
    assert gate.read_bytes() == (bundle / "after/home/.gov-os/machine/gate.json").read_bytes()
    assert stat.S_IMODE(gate.stat().st_mode) == 0o600
    assert sorted(os.listdir(gate.parent)) == entries  # no temp file left
    assert apply_sh(bundle, home, "verify")[0] == 0
    assert apply_sh(bundle, home, "apply")[0] == 0  # again: nothing to do
    assert apply_sh(bundle, home, "undo")[0] == 0
    assert gate.read_bytes() == before and stat.S_IMODE(gate.stat().st_mode) == 0o600
    assert sorted(os.listdir(gate.parent)) == entries


def test_apply_and_undo_refuse_a_file_that_moved(tmp_path, day):
    home, _ = day
    rc, bundle = build(tmp_path, home)
    gate = home / ".gov-os/machine/gate.json"
    moved = gate.read_bytes().replace(b"2026-10-28", b"2026-10-27", 1)
    gate.write_bytes(moved)
    rc, out = apply_sh(bundle, home, "apply")
    assert rc == 3 and gate.read_bytes() == moved
    assert apply_sh(bundle, home, "check")[0] == 3
    assert apply_sh(bundle, home, "undo")[0] == 3 and gate.read_bytes() == moved
    # applied, then changed later: undo refuses and keeps the later change
    gate.write_bytes((bundle / "before/home/.gov-os/machine/gate.json").read_bytes())
    assert apply_sh(bundle, home, "apply")[0] == 0
    later = gate.read_bytes().replace(b"2026-10-28", b"2026-10-27", 1)
    gate.write_bytes(later)
    assert apply_sh(bundle, home, "undo")[0] == 3 and gate.read_bytes() == later


def test_apply_refuses_a_missing_file_a_link_and_a_tampered_frozen_copy(tmp_path, day):
    home, _ = day
    rc, bundle = build(tmp_path, home)
    gate = home / ".gov-os/machine/gate.json"
    # tampered frozen after copy: exit 4, nothing touched
    frozen = bundle / "after/home/.gov-os/machine/gate.json"
    good = frozen.read_bytes()
    frozen.write_bytes(good + b" ")
    before = gate.read_bytes()
    assert apply_sh(bundle, home, "apply")[0] == 4 and gate.read_bytes() == before
    frozen.write_bytes(good)
    # a link
    real = gate.with_name("real.json")
    gate.rename(real)
    gate.symlink_to(real)
    assert apply_sh(bundle, home, "apply")[0] == 3
    gate.unlink()
    # missing
    assert apply_sh(bundle, home, "apply")[0] == 3 and not gate.exists()


def test_the_manifest_has_the_operators_form_and_names_no_live_path(tmp_path, day):
    home, _ = day
    rc, bundle = build(tmp_path, home)
    log = tmp_path / "log.txt"
    log.write_text("ok   a fixed line\nfailures: 0\n")
    tool.manifest(bundle, log)
    m = json.loads((bundle / "manifest.json").read_text())
    assert m["act"] == "ACT-P95-1" and m["claimed_class"] == "b" and m["commands"] == []
    assert m["touched"] == [{"root": "home", "path": ".gov-os/machine/gate.json", "before": sha((bundle / "before/home/.gov-os/machine/gate.json").read_bytes()),
                             "after": sha((bundle / "after/home/.gov-os/machine/gate.json").read_bytes())}]
    assert m["rehearsal"]["sha256"] == m["files"]["rehearsal.log"]
    assert len(m["checks"]) == 3 and all(c["exit"] == 0 and c["count"] is None for c in m["checks"])
    text = (bundle / "apply.sh").read_text() + "".join(c["cmd"] for c in m["checks"])
    for live in ("/home/", "~", "${HOME}/Dyn", "$HOME/Dyn"):
        assert live not in text
    assert tool.verify(bundle) == []


def test_the_checks_pass_on_the_after_file_and_fail_on_the_before_and_on_the_maximum(tmp_path, day):
    home, _ = day
    rc, bundle = build(tmp_path, home, date=datetime.date.today().isoformat())
    log = tmp_path / "log.txt"
    log.write_text("failures: 0\n")
    tool.manifest(bundle, log)
    checks = json.loads((bundle / "manifest.json").read_text())["checks"]
    clone = tmp_path / "clone"
    clone.mkdir()
    if SRC:
        os.symlink(SRC, clone / "src")
    gate = home / ".gov-os/machine/gate.json"

    def run(which):
        env = clean_env(home)
        p = subprocess.run(["bash", "-c", checks[which]["cmd"]], cwd=clone, env=env, capture_output=True, text=True)
        return p.returncode

    needed = [0, 1, 2] if SRC else [0, 1]
    # the before file: the figure check is red
    assert run(1) == 1
    apply_sh(bundle, home, "apply")
    assert [run(i) for i in needed] == [0] * len(needed)
    # the maximum written in its place: red
    data = json.loads(gate.read_text())
    data["working_size_bytes"]["value"] = 9_500_000_000
    gate.write_bytes(tool.dumps(data))
    assert run(1) == 1
    if SRC:
        assert run(2) == 1
