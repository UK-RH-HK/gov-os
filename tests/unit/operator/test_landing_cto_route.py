"""ACT-LANDING-CTO-ROUTE-1 (DEC-1167 (5)): the landing check's route for the CTO's (b) ACTs.

A commit outside a ticket on a (b) or (O) control path is a P1 unless it carries `Role: owner`, or `Role: operator` with
`Act:`. The one added route: `Role: orchestrator` with `Act: <ACT id>` and `Act-sha: <manifest sha256>` passes when, and
only when, (1) the CTO's approvals log holds a line for that ACT and manifest whose route names the CTO as the applier,
(2) the ACT is class (b) (its manifest, the classifier's vote on its bundle, and the class of the commit's paths: never
(O)), and (3) the commit's paths are the manifest's touched list. Each condition has a case that passes and cases where
it alone is missing. Everything is planted under tmp_path: the module is given the approvals log and the acts folder as
arguments, and the command line cannot be given either."""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import OPDIR, sh, write  # noqa: E402

_spec = importlib.util.spec_from_file_location("landing_check_under_test", OPDIR / "landing_check.py")
lc = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(OPDIR))
_spec.loader.exec_module(lc)

ACT = "ACT-T-ROUTE-1"
HOOK = ".claude/hooks/pretooluse.py"                       # (b), the guard-hook row
AGENT = ".claude/agents/engineer.md"                       # (b), the agents-skills-kernel row
OPERATOR = "governance/project/operator/opcommon.py"       # (O), the operator-own row, a control path
SRC = "src/gov/x.py"                                       # (O), the catch-all, not a control path
CTO_ROUTE = "the CTO (class (b), a watchers path), the owner's word"
OP_ROUTE = "the owner's operator agent (class (b)), queued by the CTO"


def sha(b):
    return hashlib.sha256(b).hexdigest()


class World:
    def __init__(self, tmp):
        self.tmp = tmp
        self.repo = tmp / "repo"
        self.acts = tmp / "orch" / "acts"
        self.approvals = tmp / "orch" / "log" / "act-approvals.jsonl"
        self.repo.mkdir()
        sh("git", "init", "-q", "-b", "main", cwd=self.repo)
        sh("git", "config", "user.email", "t@t", cwd=self.repo)
        sh("git", "config", "user.name", "t", cwd=self.repo)
        write(self.repo / "README", "x")
        sh("git", "add", "-A", cwd=self.repo)
        sh("git", "commit", "-q", "-m", "base", cwd=self.repo)
        self.base = self.head()
        self.n = 0

    def head(self):
        return sh("git", "rev-parse", "HEAD", cwd=self.repo).stdout.decode().strip()

    def bundle(self, act=ACT, paths=(HOOK,), claimed="b", name=None, apply_sh="#!/bin/bash\nexit 0\n", manifest_act=None,
               roots=None, approve=CTO_ROUTE, contents=None):
        """Plant acts/<name>/ with a manifest touching `paths`; returns its manifest sha256. `approve`: the approvals
        line's route (None: no line)."""
        d = self.acts / (name or act)
        touched = []
        for i, p in enumerate(paths):
            before, after = (contents or {}).get(p, (None, f"after {p}\n".encode()))
            write(d / "after" / "repo" / p, after)
            if before is not None:
                write(d / "before" / "repo" / p, before)
            touched.append({"root": (roots or {}).get(p, "repo"), "path": p, "before": sha(before) if before is not None else None,
                            "after": sha(after)})
        write(d / "apply.sh", apply_sh)
        raw = json.dumps({"act": manifest_act or act, "dec": "DEC-1167 (5)", "author": "cto", "claimed_class": claimed,
                          "touched": touched, "files": {}, "checks": [], "commands": []}, indent=1)
        write(d / "manifest.json", raw)
        h = sha(raw.encode())
        if approve is not None:
            self.approve(act, h, approve)
        return h

    def approve(self, act, h, route, key="manifest"):
        entry = {"at": "2026-11-13 13:52:47", "act": act, key: h, "reply": f"yes {act} {h[:8]}", "session": "s"}
        if route is not None:
            entry["route"] = route
        self.approvals.parent.mkdir(parents=True, exist_ok=True)
        with open(self.approvals, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def commit(self, paths, trailers):
        self.n += 1
        for p in paths:
            write(self.repo / p, f"after {p} {self.n}\n")
        sh("git", "add", "-A", cwd=self.repo)
        sh("git", "commit", "-q", "-m", f"commit {self.n}", "-m", "\n".join(trailers), cwd=self.repo)
        return self.head()

    def flagged(self):
        """The commits of base..HEAD the check flags, {commit: item}."""
        items = lc.check(str(self.repo), f"{self.base}..HEAD", approvals=str(self.approvals), acts_dir=str(self.acts))
        return {i["commit"]: i for i in items}


@pytest.fixture
def w(tmp_path):
    return World(tmp_path)


def route(h, act=ACT):
    return ["Task: DAEO-sdxk", "Role: orchestrator", f"Act: {act}", f"Act-sha: {h}"]


# ------------------------------------------------------------------------------------------------------- the pass
def test_a_commit_with_all_three_conditions_passes(w):
    h = w.bundle()
    c = w.commit([HOOK], route(h))
    assert w.flagged() == {}, c


def test_it_passes_without_a_task_trailer_and_with_several_paths(w):
    h = w.bundle(paths=(HOOK, AGENT))
    w.commit([HOOK, AGENT], ["Role: orchestrator", f"Act: {ACT}", f"Act-sha: {h}"])
    assert w.flagged() == {}


def test_a_later_rebuild_folder_of_the_same_act_is_found_by_the_manifest_hash(w):
    h = w.bundle(name=ACT + ".r1-abcdef12")
    w.commit([HOOK], route(h))
    assert w.flagged() == {}


def test_the_acts_before_the_route_stay_flagged_as_they_were(w):
    """The form of commit 7cc654e49f9b (Role: orchestrator, no Act:), no trailers, Role: operator without Act:, and a wrong role."""
    h = w.bundle()
    c1 = w.commit([HOOK], ["Task: DAEO-sdxk", "Role: orchestrator"])
    c2 = w.commit([HOOK], [])
    c3 = w.commit([HOOK], ["Role: operator"])
    c4 = w.commit([HOOK], ["Role: engineer", f"Act: {ACT}", f"Act-sha: {h}"])
    got = w.flagged()
    assert set(got) == {c1, c2, c3, c4}
    assert all(i["priority"] == "P1" for i in got.values())
    assert "the CTO's route refuses" not in got[c1]["reason"]
    assert got[c1]["reason"].endswith("neither Role: owner nor Role: operator with Act:")
    assert got[c3]["reason"].endswith("Role: operator without an Act: trailer")


def test_the_owner_and_operator_routes_are_unchanged(w):
    w.commit([HOOK], ["Role: owner"])
    w.commit([HOOK], ["Role: operator", "Act: ACT-X"])
    w.commit([HOOK], ["Task: DAEO-abcd", "Role: engineer"])
    assert w.flagged() == {}


# --------------------------------------------------------------------------------- (1) the approvals log, each missing
@pytest.mark.parametrize("why", ["no log", "empty log", "another act", "another manifest", "no route", "operator route",
                                 "route mentions the CTO late", "other route", "route not text"])
def test_without_condition_1_the_commit_stays_flagged(w, why):
    h = w.bundle(approve=None)
    if why == "empty log":
        write(w.approvals, "")
    elif why == "another act":
        w.approve("ACT-OTHER-1", h, CTO_ROUTE)
    elif why == "another manifest":
        w.approve(ACT, "0" * 64, CTO_ROUTE)
    elif why == "no route":
        w.approve(ACT, h, None)
    elif why == "operator route":
        w.approve(ACT, h, OP_ROUTE)
    elif why == "route mentions the CTO late":
        w.approve(ACT, h, "an agent, for the CTO")
    elif why == "other route":
        w.approve(ACT, h, "the owner, by hand")
    elif why == "route not text":
        w.approve(ACT, h, ["the CTO"])
    c = w.commit([HOOK], route(h))
    got = w.flagged()
    assert set(got) == {c}
    assert "approvals log" in got[c]["reason"] and "the CTO's route refuses" in got[c]["reason"]


def test_a_malformed_line_is_skipped_and_the_good_line_after_it_counts(w):
    h = w.bundle(approve=None)
    write(w.approvals, "{not json\n[1]\n\n")
    w.approve(ACT, h, CTO_ROUTE)
    w.commit([HOOK], route(h))
    assert w.flagged() == {}


def test_the_operators_own_line_key_names_the_manifest_too(w):
    h = w.bundle(approve=None)
    w.approve(ACT, h, CTO_ROUTE, key="manifest_sha256")
    w.commit([HOOK], route(h))
    assert w.flagged() == {}


# -------------------------------------------------------------------- the trailers and the manifest it names
@pytest.mark.parametrize("why", ["no Act-sha", "Act-sha not a sha", "Act-sha of nothing", "two Act-sha", "two Act", "bad Act id",
                                 "Act of another id"])
def test_a_trailer_that_is_missing_or_wrong_stays_flagged(w, why):
    h = w.bundle()
    t = {"no Act-sha": ["Role: orchestrator", f"Act: {ACT}"],
         "Act-sha not a sha": ["Role: orchestrator", f"Act: {ACT}", "Act-sha: 12345678"],
         "Act-sha of nothing": ["Role: orchestrator", f"Act: {ACT}", "Act-sha: " + "a" * 64],
         "two Act-sha": ["Role: orchestrator", f"Act: {ACT}", f"Act-sha: {h}", f"Act-sha: {h}"],
         "two Act": ["Role: orchestrator", f"Act: {ACT}", "Act: ACT-Y-1", f"Act-sha: {h}"],
         "bad Act id": ["Role: orchestrator", "Act: ../x", f"Act-sha: {h}"],
         "Act of another id": ["Role: orchestrator", "Act: ACT-OTHER-1", f"Act-sha: {h}"]}[why]
    c = w.commit([HOOK], t)
    assert set(w.flagged()) == {c}


def test_a_manifest_changed_after_its_approval_stays_flagged(w):
    h = w.bundle()
    m = w.acts / ACT / "manifest.json"
    m.write_text(m.read_text() + "\n")
    c = w.commit([HOOK], route(h))
    got = w.flagged()
    assert set(got) == {c} and "no manifest of " + ACT in got[c]["reason"]


def test_a_manifest_that_names_another_act_stays_flagged(w):
    h = w.bundle(manifest_act="ACT-OTHER-1")
    c = w.commit([HOOK], route(h))
    assert set(w.flagged()) == {c}


def test_a_manifest_folder_that_is_a_link_is_not_followed(w):
    h = w.bundle(name="elsewhere")
    (w.acts / ACT).symlink_to(w.acts / "elsewhere")
    c = w.commit([HOOK], route(h))
    assert set(w.flagged()) == {c}


# ------------------------------------------------------------------------------------ (2) class (b), each missing
@pytest.mark.parametrize("claimed", ["a", "O", None])
def test_a_manifest_that_does_not_claim_b_stays_flagged(w, claimed):
    h = w.bundle(claimed=claimed)
    c = w.commit([HOOK], route(h))
    got = w.flagged()
    assert set(got) == {c} and "claims class" in got[c]["reason"]


def test_a_bundle_the_classifier_votes_above_b_stays_flagged(w):
    h = w.bundle(apply_sh="#!/bin/bash\nsudo true\n")           # a script hit: sudo raises the class to (O)
    c = w.commit([HOOK], route(h))
    got = w.flagged()
    assert set(got) == {c} and "classifier's vote" in got[c]["reason"]


def test_an_act_on_an_O_control_path_stays_flagged_whatever_it_claims(w):
    """The operator's own files are (O): the owner's, by hand. A manifest claiming (b) over them does not make it (b)."""
    h = w.bundle(paths=(OPERATOR,))
    c = w.commit([OPERATOR], route(h))
    assert set(w.flagged()) == {c}


PATH_MAP = "governance/project/path-map.yaml"
PM_BEFORE = b"version: 1\nsets_root_hidden:\n  root: x\n  hidden: [a]\n  refused_roles: [engineer]\n"
PM_AFTER = b"version: 1\nsets_root_hidden:\n  root: x\n  hidden: [a, b]\n  refused_roles: [engineer]\n"


def test_a_path_map_change_beside_a_b_path_stays_flagged_though_the_classifier_reads_it_as_a_tightening(w):
    """The classifier reads the content: an item added to a refusal list is (a), so the bundle's vote is (b) through the hook
    file. The path map is the owner's ratchet row (its class by path is (O)), and 'never O' is read on the paths."""
    h = w.bundle(paths=(HOOK, PATH_MAP), contents={PATH_MAP: (PM_BEFORE, PM_AFTER)})
    bundle_vote = lc.act_class.classify(str(w.acts / ACT))
    assert bundle_vote["class"] == "b" and {f["path"]: f["class"] for f in bundle_vote["files"]}[PATH_MAP] == "a"
    c = w.commit([HOOK, PATH_MAP], route(h))
    got = w.flagged()
    assert set(got) == {c} and "class of the commit's paths" in got[c]["reason"]


def test_a_commit_that_adds_an_O_path_beside_a_b_path_stays_flagged(w):
    h = w.bundle(paths=(HOOK, SRC))
    c = w.commit([HOOK, SRC], route(h))
    assert set(w.flagged()) == {c}


def test_the_path_class_is_b_for_b_rows_and_O_for_the_operators_own_and_unknown_paths():
    rules = lc.act_class.load_rules()
    assert lc.path_class(rules, HOOK) == "b" and lc.path_class(rules, AGENT) == "b"
    assert lc.path_class(rules, ".rulesync/rules/governance.md") == "b"
    assert lc.path_class(rules, "governance/project/orchestration/tools/dispatch/dispatcher.py") == "b"
    assert lc.path_class(rules, OPERATOR) == "O"
    assert lc.path_class(rules, "governance/project/operator/landing_check.py") == "O"
    assert lc.path_class(rules, SRC) == "O"
    assert lc.path_class(rules, "governance/project/path-map.yaml") == "O"      # its ratchet class
    assert lc.path_class(rules, ".claude/settings.json") == "b"                 # a list-shaped row: its else


# ---------------------------------------------------------------------- (3) the paths are the touched list, each off
@pytest.mark.parametrize("why", ["an extra path", "a path short", "another path", "a root that is not the repository"])
def test_a_commit_whose_paths_are_not_the_touched_list_stays_flagged(w, why):
    if why == "an extra path":
        h = w.bundle(paths=(HOOK,))
        paths = [HOOK, AGENT]
    elif why == "a path short":
        h = w.bundle(paths=(HOOK, AGENT))
        paths = [HOOK]
    elif why == "another path":
        h = w.bundle(paths=(HOOK,))
        paths = [AGENT]
    else:
        h = w.bundle(paths=(HOOK, AGENT), roots={AGENT: "home"})
        paths = [HOOK, AGENT]
    c = w.commit(paths, route(h))
    got = w.flagged()
    assert set(got) == {c}
    assert "the CTO's route refuses" in got[c]["reason"]


# ----------------------------------------------------------------------------------- the command line takes no seam
def test_the_command_line_reads_the_fixed_approvals_and_cannot_be_redirected(w):
    """landing_select.sh runs `landing_check.py --repo <repo> <range>`: no option, no environment variable names another
    approvals log or acts folder, so a commit is judged by the CTO's real log (which holds no line for this ACT)."""
    h = w.bundle()
    c = w.commit([HOOK], route(h))
    env = dict(os.environ, LANDING_APPROVALS=str(w.approvals), LANDING_ACTS=str(w.acts), APPROVALS=str(w.approvals),
               ACTS_DIR=str(w.acts))
    r = subprocess.run([sys.executable, "-I", str(OPDIR / "landing_check.py"), "--repo", str(w.repo), f"{w.base}..HEAD"],
                       capture_output=True, env=env)
    items = json.loads(r.stdout.decode().strip().splitlines()[-1])
    assert [i["commit"] for i in items] == [c]
    assert re.match(r"^[0-9a-f]{40}$", items[0]["commit"])
    for extra in (["--approvals", str(w.approvals)], ["--acts", str(w.acts)]):
        r = subprocess.run([sys.executable, "-I", str(OPDIR / "landing_check.py"), "--repo", str(w.repo), f"{w.base}..HEAD",
                            *extra], capture_output=True)
        assert r.returncode == 2 and not r.stdout


def test_the_fixed_inputs_are_the_ctos_log_and_acts_folder():
    assert lc.APPROVALS.endswith("/.gov-runtime/scratch/orchestrator/log/act-approvals.jsonl")
    assert lc.ACTS_DIR.endswith("/.gov-runtime/scratch/orchestrator/acts")
    text = Path(lc.__file__).read_text()
    for name in ("CTO_ORCH", "APPROVALS", "ACTS_DIR"):
        line = next(ln for ln in text.splitlines() if ln.startswith(name + " = "))
        assert "environ" not in line and "getenv" not in line and "argv" not in line, line
    assert "getenv" not in text
