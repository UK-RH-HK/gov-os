"""IT-3 (plan item 1-9; ``.tickets/DAEO-j9z6.md`` "Fix: a close record that holds what happened"): the close record
the landing writes holds ``evidence`` in the close schema's form and the landing's notices, path-map line and impact;
the schema refuses a ``close: queue`` record without it; other close records validate as before (README, "Fix: a close
record that holds what happened").

Each planted landing is built once per session (a file lock in pytest's shared folder). The planted projects hold the
worktree's kernel schemas and a ``core-schema`` declaration that runs the product's check (``gov.check.schema``, from
the worktree's ``src/``: the planted project has no ``gov`` of its own), so ``gov check --structural`` and the same
check run alone, which lists every finding, judge the landed record with the worktree's close schema.
"""

from __future__ import annotations

import copy
import fcntl
import json
import os
import shlex
import shutil
import subprocess
import sys
import traceback

import pytest
import yaml

import w2_115b_support as support
from w2_115b_support import A, B, module_rel

CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
SPEC_REL, SPEC_ID = "docs/x/SPEC-001.md", "SPEC-001"     # a record nothing places: RECORD_PLACED; outside A's paths
NEW_TICKET = ".tickets/PROJ-newt.md"                     # a new ticket that is no feature: a ticket notice
SKIPS = "tests/unit/test_skips.py"                       # imports the widget; skips
SKIP_NODE = support.node(SKIPS)
SKIP_REASON = "planted skip"
SCHEMAS_REL = "governance/kernel/schemas"
DECLARATION_REL = "governance/kernel/checks/core-schema.yaml"
CLOSE_SCHEMA = "close.schema.json"
KERNEL = support.REPO_ROOT / "template" / "governance" / "kernel"


def _record(record_id, kind):
    front = {"id": record_id, "type": kind, "status": "ACTIVE", "state_class": "AUTHORITATIVE"}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {record_id}\n\nText.\n"


def _project(folder):
    extra = {f"{SCHEMAS_REL}/{path.name}": path.read_text(encoding="utf-8")
             for path in sorted((KERNEL / "schemas").glob("*.schema.json"))}
    declared = yaml.safe_load((KERNEL / "checks" / "core-schema.yaml").read_text(encoding="utf-8"))
    run = f"import sys; sys.path.insert(0, {str(support.SRC)!r}); from gov.check.schema import main; sys.exit(main())"
    extra[DECLARATION_REL] = yaml.safe_dump({**declared, "command": shlex.join(["python3", "-c", run])},
                                            sort_keys=False)
    skip = f"    _tell(True)\n    import pytest\n    pytest.skip({SKIP_REASON!r})\n"
    extra[SKIPS] = support.telling(SKIPS, folder / "told", ["widget"], skip)
    extra[support.KNOWN_RED] = support.telling(support.KNOWN_RED, folder / "told", ["widget"], support.RED_ALWAYS)
    return support.Planted(folder / "project", folder / "told", extra=extra)


def _check_fixture(p, tips):
    assert shutil.which("check-jsonschema"), "fixture: check-jsonschema is not on PATH"
    support.self_check(p, {
        p.base: {support.KNOWN_RED_NODE: "failed", SKIP_NODE: "skipped"},
        **tips})


def _core_schema(p, scratch):
    """``python3 -m gov.check.schema`` in ``scratch``: its findings."""
    env = support.base_env(scratch.parent / f"{scratch.name}-env")
    done = subprocess.run([sys.executable, "-m", "gov.check.schema"], cwd=str(scratch), env=env, capture_output=True,
                          text=True, timeout=300)
    try:
        found = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"core-schema printed no JSON:\n{done.stdout}\n{done.stderr}") from None
    findings = found.get("findings", [])
    assert not [f for f in findings if str(f.get("code", "")).startswith("SCHEMA_VALIDATOR")], \
        f"fixture: the validator did not measure: {findings}"
    return findings


def _scratch(p, revision, name):
    scratch = p.root.parent / f"{p.root.name}-{name}"
    shutil.rmtree(scratch, ignore_errors=True)
    support.git(p.root.parent, "clone", "-q", "--no-checkout", str(p.root), str(scratch))
    support.git(scratch, "checkout", "-q", "--detach", revision)
    return scratch


def _text(front):
    return "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n\n# A close record\n"


def _taken(p, args):
    """The landing ``args``, and what it left: the answer, each landed ticket's close record, core-schema's findings
    and the structural pass at the landed head, the changed paths of each branch and the kept JUnit files' cases."""
    old_head = support.rev(p.root, "main")
    run = support.run_queue(p, *args)
    data = {"root": str(p.root), "old_head": old_head, "run": run, "records": {}}
    try:
        result = json.loads(run["stdout"]).get("result") or {}
    except ValueError:
        result = {}
    if not result.get("landed"):
        return data
    head = support.rev(p.root, "main")
    for tid in result["landed"]:
        data["records"][tid] = json.loads(json.dumps(support.close_record(p, head, tid), default=str))
    data["tree"] = support.git(p.root, "rev-parse", f"{result['tested']}^{{tree}}").strip()
    data["changed"] = {
        tid: sorted(support.git(p.root, "diff", "--no-renames", "--name-only",
                                f"{result['base']}...{p.tips[tid]}").split())
        for tid in result["landed"]}
    junit = {}
    for tid, front in data["records"].items():
        evidence = front.get("evidence")
        for rel in (evidence or {}).get("junit_xml") or []:
            found = [at / rel for at in (p.root, p.root / support.CLONE_REL) if (at / rel).is_file()]
            junit[rel] = support.junit_outcomes(found[0]) if found else None
    data["junit"] = junit
    scratch = _scratch(p, head, "schema")
    data["findings"] = _core_schema(p, scratch)
    env = {**support.base_env(scratch.parent / f"{scratch.name}-env"), support.SELF_CHECK: "1"}
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "check", "--structural", old_head, "--root",
                           str(scratch)], cwd=str(scratch), env=env, capture_output=True, text=True, timeout=300)
    data["structural"] = {"code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}
    # the same record, evidence removed and null, judged by the same command
    data["mutated"] = {}
    tid = result["landed"][0]
    rel = f"docs/close/{tid}/CL-{tid}.md"
    for kind in ("removed", "null"):
        front = copy.deepcopy(support.close_record(p, head, tid))
        front.pop("evidence", None)
        if kind == "null":
            front["evidence"] = None
        (scratch / rel).write_text(_text(front), encoding="utf-8")
        data["mutated"][kind] = [f for f in _core_schema(p, scratch) if f.get("path") == rel]
    shutil.rmtree(scratch, ignore_errors=True)
    return data


def build_scoped(folder):
    """A changes the widget, adds a record outside its paths and a ticket that is no feature; B changes the gadget.
    The landing ``A B``."""
    p = _project(folder)
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED, SPEC_REL: _record(SPEC_ID, "specification"),
                                     NEW_TICKET: _record("PROJ-newt", "task")}, "engineer", True)])
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): CHANGED}, "engineer", True)])
    _check_fixture(p, {p.tips[A.id]: {A.node: "passed", support.USES_WIDGET_NODE: "passed"},
                       p.tips[B.id]: {B.node: "passed"}})
    return _taken(p, (f"{A.id}=topic/aa", f"{B.id}=topic/bb"))


def build_full(folder):
    """A changes the widget. The landing ``A --full``."""
    p = _project(folder)
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True)])
    _check_fixture(p, {p.tips[A.id]: {A.node: "passed", support.USES_WIDGET_NODE: "passed"}})
    return _taken(p, (f"{A.id}=topic/aa", "--full"))


BUILDS = {"scoped": build_scoped, "full": build_full}


def _shared(factory, name):
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-115b-it3-{name}"
    with open(root / f"w2-115b-it3-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "data.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return json.loads(done.read_text(encoding="utf-8"))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = BUILDS[name](folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return data


@pytest.fixture(scope="session")
def taken(tmp_path_factory):
    return lambda name: _shared(tmp_path_factory, name)


def _answer(data):
    result = support.answer(data["run"], support.EXIT_LANDED)
    assert A.id in (result.get("landed") or []), support.describe(data["run"])
    return result


def _evidence(data, tid=A.id):
    front = data["records"].get(tid) or {}
    evidence = front.get("evidence")
    assert isinstance(evidence, dict), \
        f"{tid}'s close record holds no evidence block: evidence {evidence!r}; keys {sorted(front)}"
    return evidence


def _covers(target, rel):
    target = target.split("::")[0].rstrip("/")
    return rel == target or rel.startswith(target + "/")


# -- the evidence block ------------------------------------------------------------------------------------------------

def test_it3_the_evidence_says_scoped_and_names_the_base_the_tested_commit_and_its_tree(taken):
    data = taken("scoped")
    result = _answer(data)
    for tid in (A.id, B.id):
        evidence = _evidence(data, tid)
        got = {key: evidence.get(key) for key in ("scope", "base", "head", "tree")}
        want = {"scope": "scoped", "base": result["base"], "head": result["tested"], "tree": data["tree"]}
        assert got == want, f"{tid}'s evidence: {got}, not {want}"
        assert result["base"] == data["old_head"], "the base is not the integration head the run merged onto"


def test_it3_changed_is_each_ticket_s_own_changed_paths(taken):
    data = taken("scoped")
    _answer(data)
    for tid in (A.id, B.id):
        changed = _evidence(data, tid).get("changed")
        assert sorted(changed or []) == data["changed"][tid], \
            f"{tid}'s evidence.changed {changed} is not its own change {data['changed'][tid]}"


def test_it3_selected_names_what_the_run_ran_for_the_ticket(taken):
    data = taken("scoped")
    _answer(data)
    selected = _evidence(data).get("selected")
    assert selected, f"selected: {selected!r}"
    targets = [item.get("target") or "" for item in selected]
    assert any(_covers(t, support.USES_WIDGET[0]) for t in targets), \
        f"selected names no target holding {support.USES_WIDGET[0]}, which the run ran for the widget: {targets}"


def test_it3_the_skips_the_failures_and_the_kept_junit_files_are_those_of_the_runs(taken):
    data = taken("scoped")
    _answer(data)
    evidence = _evidence(data)
    skips = evidence.get("skips") or []
    mine = [s for s in skips if "test_skips" in s.get("test", "")]
    assert mine and SKIP_REASON in mine[0].get("reason", ""), f"skips: {skips}"
    assert evidence.get("skip_count") == len(skips), f"skip_count {evidence.get('skip_count')}, skips {skips}"
    failures = evidence.get("failures") or []
    assert any("test_known_red" in f.get("test", "") and f.get("text") for f in failures), f"failures: {failures}"
    kept = evidence.get("junit_xml") or []
    assert kept, "no JUnit file is named"
    missing = [rel for rel in kept if not data["junit"].get(rel)]
    assert not missing, f"named JUnit files that are not there or hold no test case: {missing}"
    cases = {node for rel in kept for node in data["junit"][rel]}
    assert any("test_uses_widget" in node for node in cases), f"the kept files do not hold the run's cases: {cases}"


def test_it3_a_full_run_s_evidence_says_full_with_a_reason(taken):
    data = taken("full")
    result = _answer(data)
    evidence = _evidence(data)
    assert evidence.get("scope") == "full", f"scope: {evidence.get('scope')!r}"
    why = evidence.get("why_full")
    assert why and all(item.get("reason") for item in why), f"why_full: {why!r}"
    got = {key: evidence.get(key) for key in ("base", "head", "tree")}
    assert got == {"base": result["base"], "head": result["tested"], "tree": data["tree"]}, got
    assert evidence.get("junit_xml") and evidence.get("selected"), evidence
    assert evidence.get("skip_count", 0) >= 1, f"the full run's skip is not counted: {evidence.get('skips')}"


# -- the schema ---------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", ("scoped", "full"))
def test_it3_the_landed_close_records_hold_evidence_and_the_structural_pass_finds_nothing_on_them(taken, name):
    data = taken(name)
    result = _answer(data)
    for tid in result["landed"]:
        _evidence(data, tid)
        rel = f"docs/close/{tid}/CL-{tid}.md"
        mine = [f for f in data["findings"] if f.get("path") == rel]
        assert not mine, f"core-schema finds on {rel}: {mine}"
        said = data["structural"]["stdout"]
        assert data["structural"]["code"] == 0, data["structural"]
        line = next((x for x in said.splitlines() if x.startswith("schema:")), "")
        assert line and "skipped" not in line and "Error" not in line, f"fixture: the schema family did not run:\n{said}"
        assert rel not in said, said


@pytest.mark.parametrize("kind", ("removed", "null"))
def test_it3_the_same_record_with_evidence_removed_or_null_fails_the_close_schema(taken, kind):
    data = taken("scoped")
    _answer(data)
    mine = data["mutated"][kind]
    assert any(CLOSE_SCHEMA in json.dumps(f) and "evidence" in json.dumps(f) for f in mine), \
        f"with evidence {kind}, no finding on the record names {CLOSE_SCHEMA} and evidence: {mine}"


OTHERS = {
    "gov_close_with_null_evidence": {"close": "scoped", "evidence": None},
    "written_before_w2_66": {},
    "a_fix_landing_s_own_form": {"fixes": [{"line": "a fix", "branch": "fix/one", "tip": "a" * 40,
                                            "tested": "b" * 40, "landed": "2026-11-01T12:00:00Z"}]},
}


@pytest.mark.parametrize("kind", sorted(OTHERS))
def test_it3_other_close_records_validate_as_before(tmp_path, kind):
    p = _project(tmp_path)
    rel = f"docs/close/{A.id}/CL-{A.id}.md"
    front = {"id": f"CL-{A.id}", "type": "close", "status": "ACTIVE", "state_class": "AUTHORITATIVE", "task": A.id,
             "created": "2026-11-01T12:00:00Z", **OTHERS[kind]}
    p.write(rel, _text({key: value for key, value in front.items() if key != "task"}))
    assert [f for f in _core_schema(p, p.root) if f.get("path") == rel], "fixture: the record is not measured"
    p.write(rel, _text(front))
    mine = [f for f in _core_schema(p, p.root) if f.get("path") == rel]
    assert not mine, f"{kind} no longer validates: {mine}"


# -- the notices, the path-map line and the impact ------------------------------------------------------------------------

def test_it3_the_close_record_holds_the_landing_s_notices_path_map_and_impact(taken):
    data = taken("scoped")
    result = _answer(data)
    placed = f"RECORD_PLACED {SPEC_REL}"
    assert placed in (result.get("notices") or []), f"fixture: the answer's notices: {result.get('notices')}"
    assert result.get("path_map"), "fixture: the answer holds no path_map"
    for tid in (A.id, B.id):
        front = data["records"][tid]
        for key in ("path_notices", "ticket_notices"):
            own = [n for n in result.get(key) or [] if n.get("ticket") == tid]
            assert front.get(key) == own, f"{tid}'s {key}: {front.get(key)!r}, the ticket's own: {own}"
        assert front.get("notices") == result["notices"], \
            f"{tid}'s notices: {front.get('notices')!r}, the landing's: {result['notices']}"
        assert front.get("path_map") == result["path_map"], f"{tid}'s path_map: {front.get('path_map')!r}"
    mine = data["records"][A.id]
    assert [n for n in mine["path_notices"] if n.get("path") == SPEC_REL], "fixture: no path notice for the record"
    assert mine["ticket_notices"], "fixture: no ticket notice for the new ticket that is no feature"
    entry = (result.get("impact") or {}).get(A.id)
    assert isinstance(entry, dict), f"the answer holds no impact entry for {A.id}: {result.get('impact')!r}"
    assert SPEC_ID in [r.get("id") for r in entry.get("records") or []], entry
    for tid in (A.id, B.id):
        assert data["records"][tid].get("impact") == result["impact"][tid], \
            f"{tid}'s impact: {data['records'][tid].get('impact')!r}"
