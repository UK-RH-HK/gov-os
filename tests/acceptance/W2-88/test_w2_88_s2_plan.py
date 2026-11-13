"""S2 (success-2) and F1 (failure-1, plan half); I1, I4: the refactoring plan from the assessment.

One planted repository with one case of each of the seven kinds yields one ``RP-<nn>-<kind>.md`` per blocker, each in
the kernel ticket form, citing the assessment's sha256; no ``tk`` call, nothing written or committed in the repository;
a clean repository yields ``NOTHING-TO-REFACTOR.md``.
"""

from __future__ import annotations

import re

import pytest

import w2_88_plan_support as P
import w2_88_support as W


@pytest.fixture
def planned(box, host):
    """A function (called in the case): MA on the blockers repository with a logging ``tk`` first on PATH."""
    def make():
        orchard = P.plant_blockers(box.base)
        tools = W.logging_tool(box.base / "tools-tk", "tk", box.base / "tk-calls.log")
        W.settle(orchard.root)
        before = W.repo_state(orchard.root)
        tickets_before = sorted(p.name for p in (orchard.root / ".tickets").iterdir())
        out = box.base / "plan-out"
        run = W.run_adopt(orchard.root, W.env(box, host, tools=[tools]), "MA", "--out", str(out))
        W.assert_offered(run, "MA")
        W.assert_ok(run, "MA on the blockers repository")
        return {"orchard": orchard, "out": out, "run": run, "before": before, "tickets": tickets_before,
                "tk_log": box.base / "tk-calls.log"}
    return make


def test_the_plan_module_states_its_entry_point():
    """I4: ``refactor_plan.plan(assessment, path_map, out)`` (red: no gov.adopt.refactor_plan on the base)."""
    from gov.adopt import refactor_plan
    assert callable(refactor_plan.plan)


def test_s2_one_proposed_ticket_per_blocker_of_the_seven_kinds(planned):
    got = planned()
    files = P.plan_files(got["out"])
    assert sorted(files) == sorted(W.KINDS), f"the plan holds kinds {sorted(files)}, the seven are {sorted(W.KINDS)}"
    assert all(len(v) == 1 for v in files.values()), f"one proposal per blocker: {({k: len(v) for k, v in files.items()})}"
    numbers = sorted(int(P.RP_NAME.match(p.name).group(1)) for v in files.values() for p in v)
    assert numbers == list(range(1, 8)), f"the proposals are numbered 01..07: {numbers}"


def test_s2_every_proposal_is_in_the_kernel_ticket_form_citing_the_assessment(planned):
    got = planned()
    digest = W.sha256_file(got["out"] / W.ASSESSMENT)
    files = P.plan_files(got["out"])
    assert files, "no proposal was written"
    for kind, (path,) in files.items():
        problems = P.ticket_problems(path.read_text(encoding="utf-8"), digest)
        assert not problems, f"{path.name}: {problems}"


def test_s2_each_proposal_reaches_the_file_it_is_about(planned):
    got = planned()
    for kind, (path,) in P.plan_files(got["out"]).items():
        head = P.split_frontmatter(path.read_text(encoding="utf-8")) or {}
        rel = P.BLOCKER_PATHS[kind]
        assert P.covers(head.get("allowed_paths"), rel), f"{path.name}: allowed_paths {head.get('allowed_paths')} reach no {rel}"


def test_s2_plan_md_lists_every_proposal_and_a_vendored_folder_is_no_blocker(planned):
    got = planned()
    text = (got["out"] / W.PLAN_DIR / "PLAN.md").read_text(encoding="utf-8")
    for kind, (path,) in P.plan_files(got["out"]).items():
        assert path.name in text or path.stem in text, f"PLAN.md does not list {path.name}"
    assert not (got["out"] / W.PLAN_DIR / "NOTHING-TO-REFACTOR.md").exists(), "NOTHING-TO-REFACTOR.md beside real blockers"
    allowed = " ".join(str(P.split_frontmatter(p.read_text(encoding="utf-8")).get("allowed_paths"))
                       for v in P.plan_files(got["out"]).values() for p in v)
    assert "vendor/acme" not in allowed and "gen/tables.py" not in allowed, \
        "a vendored or generated folder that holds its code in a folder of its own is proposed as a blocker"


def test_s2_f1_no_tk_call_and_the_repository_is_unchanged(planned):
    got = planned()
    log = got["tk_log"]
    assert not log.exists() or log.read_text(encoding="utf-8").strip() == "", f"tk was called: {log.read_text()}"
    after = W.repo_state(got["orchard"].root)
    W.assert_state_equal(got["before"], after, "the assessment and the plan")
    assert sorted(p.name for p in (got["orchard"].root / ".tickets").iterdir()) == got["tickets"], "the .tickets/ set changed"
    assert after["porcelain"] == "", f"git status of the repository: {after['porcelain']}"


def test_s2_no_proposal_holds_the_secrets_value(planned):
    got = planned()
    W.assert_no_secret(got["orchard"].secret, W.all_text(got["out"], runs=(got["run"],)), "the plan's outputs")
    rps = P.plan_files(got["out"])
    assert rps, "no proposal was written, so none could be searched"


def test_s2_a_clean_repository_says_there_is_nothing_to_refactor(box, host):
    root = P.plant_clean(box.base)
    out = box.base / "clean-out"
    run = W.run_adopt(root, W.env(box, host), "MA", "--out", str(out))
    W.assert_offered(run, "MA")
    W.assert_ok(run, "MA on the clean repository")
    folder = out / W.PLAN_DIR
    assert (folder / "NOTHING-TO-REFACTOR.md").is_file(), f"no NOTHING-TO-REFACTOR.md: {sorted(p.name for p in folder.glob('*'))}"
    assert not list(folder.glob("RP-*")), f"a clean repository got proposals: {[p.name for p in folder.glob('RP-*')]}"
    assert not (folder / "PLAN.md").exists(), "PLAN.md beside NOTHING-TO-REFACTOR.md (it is 'instead')"
    assert re.search(r"nothing to refactor", (folder / "NOTHING-TO-REFACTOR.md").read_text(encoding="utf-8"), re.I)
