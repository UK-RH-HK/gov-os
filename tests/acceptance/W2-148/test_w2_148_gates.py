"""W2-148 S1-S5, S9, S11-S13: each gate refusing on its own, every other gate passing in the same planted bundle, and
nothing applied (the live planted tree, HOME, HEAD, index, crontab and remote unchanged); G9's holds wait, then proceed.
"""

from __future__ import annotations

import json

import pytest

import w2_148_support as support
from w2_148_support import last_json, wait_for


def refused(w, r, snap, gate=None, gates=None, phrase=None):
    assert r.out.get("result") == "refused", (r.out, r.stderr[-3000:])
    assert r.code != 0
    if gate:
        assert r.out.get("gate") == gate, r.out
    if gates:
        assert r.out.get("gate") in gates, r.out
    if phrase:
        assert phrase in str(r.out.get("reason", "")), r.out
    assert r.out.get("approved_sha256") == w.approved_sha()
    assert w.snapshot() == snap, "a refused run changed the live planted state"
    assert w.forbidden_calls() == ""


def applied(w, r, b):
    assert r.out.get("result") == "applied", (r.out, r.stderr[-3000:])
    assert r.code == 0
    for t in b.manifest["touched"]:
        data = w.read(t["root"], t["path"])
        assert (None if data is None else support.sha256_bytes(data)) == t["after"], t["path"]


# --- S1 G1 Frozen ---------------------------------------------------------------------------------------------------

def test_s1_g1_a_byte_changed_before_the_copy_refuses(world):
    b = world.ready("ACT-T-G1A", [world.optin_removal()])
    with open(b.dir / "apply.sh", "a") as f:
        f.write("# one byte more\n")
    snap = world.snapshot()
    refused(world, world.run(b), snap, gate="G1")


def test_s1_g1_the_run_uses_its_frozen_copy_not_the_source_edited_after_it(world, tmp_path):
    b = world.ready("ACT-T-G1B", [world.optin_removal()])
    marker = world.marks / "source-edit-ran"
    hook = tmp_path / "hook.py"
    hook.write_text(
        f"#!{support.PY}\nimport sys\n"
        "if sys.argv[1] != 'after-G1':\n    sys.exit(0)\n"
        f"p = {str(b.dir / 'apply.sh')!r}\n"
        "head, rest = open(p).read().split('\\n', 1)\n"
        f"open(p, 'w').write(head + '\\ntouch {marker}\\n' + rest)\n")
    hook.chmod(0o755)
    r = world.run(b, env_extra={"GOV_OPERATOR_TEST_HOOK": hook})
    applied(world, r, b)
    assert "touch" in (b.dir / "apply.sh").read_text(), "the test hook did not edit the source after the copy"
    assert not marker.exists(), "the run used the source bundle edited after the copy"
    frozen = world.frozen_dirs(b)
    assert len(frozen) == 1, "no frozen copy acts/<id>-<sha12>/ under the operator root"
    for p in [frozen[0], *frozen[0].rglob("*")]:
        assert p.stat().st_mode & 0o222 == 0, f"{p} is writable"


# --- S2 G2 Under a decision -----------------------------------------------------------------------------------------

@pytest.mark.parametrize("dec", ["DEC-9002", "DEC-9999", None], ids=["proposed", "not-in-the-register", "missing"])
def test_s2_g2_refuses_a_decision_not_accepted_in_the_register(world, dec):
    b = world.ready("ACT-T-G2", [world.optin_removal()], dec=dec)
    snap = world.snapshot()
    refused(world, world.run(b), snap, gate="G2")


# --- S3 G3 Rehearsed ------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("case", ["missing", "hash-mismatch", "ends-with-failures"])
def test_s3_g3_refuses_a_rehearsal_log_missing_mismatched_or_failing(world, case):
    kw = {"missing": {"rehearsal": None, "rehearsal_field": False},
          "hash-mismatch": {"rehearsal_sha": "c" * 64},
          "ends-with-failures": {"rehearsal": support.REHEARSAL_OK.replace("failures: 0", "failures: 2")}}[case]
    b = world.ready("ACT-T-G3", [world.optin_removal()], **kw)
    snap = world.snapshot()
    refused(world, world.run(b), snap, gate="G3")


# --- S4 G4 READY ----------------------------------------------------------------------------------------------------

BLOCKING = [{"kpi": "S1", "verdict": "fail",
             "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]
FAIL_NOT_BLOCKING = [{"kpi": "S1", "verdict": "fail",
                      "findings": [{"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}]


@pytest.mark.parametrize("case", ["not-ready", "malformed-block", "no-block", "fail-with-no-blocking-finding",
                                  "changed-reviewer-brief", "reviewer-is-the-author", "third-round"])
def test_s4_g4_refuses_a_review_that_is_not_ready_for_an_act(world, case):
    review = {"not-ready": {"kpis": BLOCKING},
              "malformed-block": {"raw_block": '{"kpis": [ {"kpi": "S1", "verdict": '},
              "no-block": {"no_block": True},
              "fail-with-no-blocking-finding": {"kpis": FAIL_NOT_BLOCKING},
              "changed-reviewer-brief": {"brief_sha": "a" * 64},
              "reviewer-is-the-author": {"reviewer": "orchestrator"},
              "third-round": {"rounds": 3}}[case]
    b = world.ready("ACT-T-G4", [world.optin_removal()], review_kw=review)
    snap = world.snapshot()
    refused(world, world.run(b), snap, gate="G4", phrase="to the owner" if case == "third-round" else None)


def test_s4_g4_a_block_naming_another_manifest_sha_refuses(world):
    b = world.ready("ACT-T-G4S", [world.optin_removal()], review_kw={"sha": "f" * 64})
    snap = world.snapshot()
    refused(world, world.run(b), snap, gates=("G4", "G5"))


def test_s4_guard_a_ready_review_of_two_rounds_passes(world):
    b = world.ready("ACT-T-G4R", [world.optin_removal()], review_kw={"rounds": 2})
    applied(world, world.run(b), b)


def test_s4_the_install_pins_verdict_py_byte_for_byte():
    support.require_operator()
    pinned = support.OPERATOR_SRC / "verdict.py"
    assert pinned.is_file(), "no pinned verdict.py in governance/project/operator/"
    assert support.sha256_file(pinned) == support.REF_VERDICT_SHA256


# --- S5 G5 Hashes match ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("pair", ["request-differs", "verdict-differs", "manifest-edited-after-review"])
def test_s5_g5_any_sha_differing_refuses_changed_after_review(world, pair):
    b = world.ready("ACT-T-G5", [world.optin_removal()],
                    review_kw={"sha": "d" * 64} if pair == "verdict-differs" else None)
    sha = b.sha
    if pair == "request-differs":
        sha = "e" * 64
    if pair == "manifest-edited-after-review":
        manifest = json.loads((b.dir / "manifest.json").read_text())
        manifest["checks"].append({"cmd": "test -f README.md", "exit": 0, "count": None})
        (b.dir / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    snap = world.snapshot()
    refused(world, world.run(b, sha=sha), snap, gates=("G1", "G4", "G5"), phrase="changed after review")


# --- S9 G6 for (a) and (O) ------------------------------------------------------------------------------------------

def test_s9_g6_an_a_act_proceeds_with_no_yes(world):
    b = world.ready("ACT-T-A1", [world.optin_removal()])
    assert world.transcript().read_text() == ""
    r = world.run(b)
    applied(world, r, b)
    assert not [n for n in world.notices(b.act) if n.get("kind") == "disagreement"]


def test_s9_g6_an_o_act_is_refused_as_yours(world):
    b = world.ready("ACT-T-O1", [world.src_change()], claimed="O")
    snap = world.snapshot()
    refused(world, world.run(b), snap, gate="G6", phrase="yours")


# --- S11 G7 Live state as stated ------------------------------------------------------------------------------------

def test_s11_g7_a_moved_live_file_refuses_rebuild_rehearse_re_review(world):
    b = world.ready("ACT-T-G7", [world.optin_removal()])
    with open(world.repo / "tests/optin-lifted.txt", "a") as f:
        f.write("tests/acceptance/W1-53/test_moved.py  # moved after the rehearsal\n")
    snap = world.snapshot()
    refused(world, world.run(b), snap, gate="G7", phrase="rebuild, rehearse, re-review")


# --- S12 G8 Dry run, undo and the touched-file check ----------------------------------------------------------------

@pytest.mark.parametrize("case", ["unlisted-file-in-the-tree", "unlisted-file-in-the-planted-home",
                                  "undo-not-byte-for-byte", "listed-file-not-changed"])
def test_s12_g8_the_dry_run_refuses(world, case):
    changes = [world.optin_removal()]
    kw = {}
    if case == "unlisted-file-in-the-tree":
        kw["apply_extra"] = "echo stray > stray.txt"
    elif case == "unlisted-file-in-the-planted-home":
        kw["apply_extra"] = 'echo stray > "$HOME/.stray"'
    elif case == "undo-not-byte-for-byte":
        kw["undo_extra"] = "printf ' ' >> ./tests/optin-lifted.txt"
    else:
        changes.append(world.optin_removal("tests/optin-lifted-guard.txt"))
        kw["skip_apply"] = {"tests/optin-lifted-guard.txt"}
    b = world.ready("ACT-T-G8", changes, **kw)
    snap = world.snapshot()
    refused(world, world.run(b), snap, gate="G8")
    assert not (world.home / ".stray").exists() and not (world.repo / "stray.txt").exists()


# --- S13 G9 Holds ---------------------------------------------------------------------------------------------------

def _night_hold(w, holding):
    """The CTO's night hold state file (log/night-hold.state.json), fresh, with `holding` as given."""
    p = w.scratch / "log/night-hold.state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"pid": 1, "at": "2026-11-10 05:30:00", "holding": holding, "in_window": True, "nightly": "n"}))


HOLDS = {
    # DEC-1157 (2), ACT-OPERATOR-HOURS-3: no time hold; at night the nightly's own flag holds (05:30, cleared when it ends)
    "nightly-running": (lambda w: (w.set_clock("2026-11-10T05:30:00+00:00"),
                                   (w.scratch / "NIGHTLY-RUNNING").write_text("2026-11-10 04:00:05 nightly: running\n")),
                        lambda w: (w.scratch / "NIGHTLY-RUNNING").unlink()),
    "nightly-window": (lambda w: w.set_clock("2026-11-10T21:30:00+00:00"),
                       lambda w: w.set_clock("2026-11-10T22:30:00+00:00")),
    "close-queue-running": (lambda w: w.close_flag.write_text("running\n"), lambda w: w.close_flag.unlink()),
    "act-in-progress": (lambda w: (w.scratch / "log/act-in-progress.txt").write_text("ACT-HAND-1 by hand\n"),
                        lambda w: (w.scratch / "log/act-in-progress.txt").unlink()),
}


@pytest.mark.parametrize("hold", list(HOLDS))
def test_s13_g9_a_hold_waits_then_proceeds_once_cleared(world, hold):
    setup, clear = HOLDS[hold]
    b = world.ready("ACT-T-G9", [world.optin_removal()], review_kw={"at": "2026-11-09T09:00:00+00:00"})
    before = world.read("repo", "tests/optin-lifted.txt")
    setup(world)
    proc = world.start(b)
    try:
        held = wait_for(lambda: proc.poll() is not None or any(
            line.get("gate") == "G9" and line.get("result") == "held" for line in world.gate_lines(b.act)), 90)
        assert proc.poll() is None, f"the run ended during a hold: {proc.communicate()}"
        assert held, "no G9 held line in log/operator.jsonl"
        assert world.read("repo", "tests/optin-lifted.txt") == before, "applied during a hold"
        clear(world)
        out, err = proc.communicate(timeout=120)
    finally:
        world.stop(proc)
    assert proc.returncode == 0, err[-3000:]
    assert last_json(out).get("result") == "applied"
    assert world.read("repo", "tests/optin-lifted.txt") == b.dir.joinpath(
        "after/repo/tests/optin-lifted.txt").read_bytes()


# DEC-1157 (2), ACT-OPERATOR-HOURS-3: the night hold is removed; G9 holds no hour of the night, whatever its old state file says
NIGHT = {
    "0230-no-state-file": ("2026-11-10T02:30:00+00:00", None),
    "0530-night-hold-true": ("2026-11-10T05:30:00+00:00", True),
}


@pytest.mark.parametrize("night", list(NIGHT))
def test_s13_g9_no_time_hold_at_night(world, night):
    clock, holding = NIGHT[night]
    b = world.ready("ACT-T-G9N", [world.optin_removal()], review_kw={"at": "2026-11-09T09:00:00+00:00"})
    world.set_clock(clock)
    if holding is not None:
        _night_hold(world, holding)
    r = world.run(b)
    applied(world, r, b)
    g9 = [line for line in world.gate_lines(b.act) if line.get("gate") == "G9"]
    assert g9 and all(line.get("result") != "held" for line in g9), g9
