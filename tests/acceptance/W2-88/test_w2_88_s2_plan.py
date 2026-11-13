"""S2 (success-2) and F1 (failure-1, plan half); I1, I4: the refactoring plan from the assessment.

One planted repository with one case of each of the seven kinds yields one ``RP-<nn>-<kind>.md`` per blocker, each in
the kernel ticket form, citing the assessment's sha256; no ``tk`` call, nothing written or committed in the repository;
a clean repository yields ``NOTHING-TO-REFACTOR.md``.
"""

from __future__ import annotations

import json
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


# ---- B-1.5 (RV1-3): the secrets scan did not run -----------------------------------------------------------------------
#
# When the secrets scan did not run (no ``gitleaks`` on PATH) or skipped files (a blob over ``assess.SCAN_LIMIT_BYTES``, 16 MiB), MA
# still writes ``memory-assessment.json`` and the ``RP-*.md`` proposals it finds; it writes no ``NOTHING-TO-REFACTOR.md``; it writes
# ``refactor-plan/PLAN.md`` holding the line ``secrets: not scanned (<reason>)`` and the unscanned paths (or ``all <n> tracked files``
# when the scanner did not run); its result is not ok, error ``SECRETS_UNSCANNED``, ``details`` ``{reason, unscanned}`` (exit non-zero).
# The repository is still byte-identical before and after (F1), and the secret's value is in no output (F5).

NOT_SCANNED = re.compile(r"secrets: not scanned \(([^)\n]+)\)")


def assess_unscanned(box, host, root, name, *, environment=None):
    """MA on ``root`` (settled, its state taken) with no gitleaks on PATH (or with ``environment``); returns ``(run, out, before)``."""
    W.settle(root)
    before = W.repo_state(root)
    out = box.base / name
    run = W.run_adopt(root, environment if environment is not None else W.env_without_gitleaks(box, host), "MA", "--out", str(out))
    W.assert_offered(run, "MA")
    return run, out, before


def assert_unscanned_refusal(run, what):
    W.assert_refused(run, "SECRETS_UNSCANNED", what, "MA")
    details = run.error.get("details") or {}
    assert isinstance(details, dict) and {"reason", "unscanned"} <= set(details), f"details is {details!r}, not {{reason, unscanned}}"
    assert str(details["reason"]).strip(), "details['reason'] is empty"
    return details


def test_s2_ma_with_no_gitleaks_writes_what_it_found_names_the_scan_not_run_and_is_not_ok(box, host):
    """B-1.5: no ``gitleaks`` on PATH, on a repository with one secret line (and the other blockers): the assessment and the
    proposals it finds (the over-limit one) are written; no ``NOTHING-TO-REFACTOR.md``; ``PLAN.md`` holds ``secrets: not scanned
    (<reason>)`` and ``all <n> tracked files``; the result is not ok with ``SECRETS_UNSCANNED``; the repository is byte-identical
    before and after; the secret's value is in no output."""
    orchard = P.plant_blockers(box.base)
    run, out, before = assess_unscanned(box, host, orchard.root, "no-scanner-out")
    details = assert_unscanned_refusal(run, "MA with no gitleaks on PATH")
    record = out / W.ASSESSMENT
    assert record.is_file(), f"MA wrote no {W.ASSESSMENT} when the scan did not run (it still writes what it found)"
    tracked = len(W.git(orchard.root, "ls-files").splitlines())
    assert W.read_json(record)["tracked_files"] == tracked
    assert "over-limit" in P.plan_files(out), f"the proposals MA finds are not written: {sorted(P.plan_files(out))}"
    folder = out / W.PLAN_DIR
    assert not (folder / "NOTHING-TO-REFACTOR.md").exists(), "NOTHING-TO-REFACTOR.md is written though the secrets scan did not run"
    plan = (folder / "PLAN.md").read_text(encoding="utf-8")
    found = NOT_SCANNED.search(plan)
    assert found, "PLAN.md does not hold the line `secrets: not scanned (<reason>)`"
    assert f"all {tracked} tracked files" in plan, f"PLAN.md does not say `all {tracked} tracked files` (the scanner did not run)"
    W.assert_state_equal(before, W.repo_state(orchard.root), "MA with no gitleaks")
    W.assert_no_secret(orchard.secret, W.all_text(out, runs=(run,)), "MA's outputs with no gitleaks")
    assert details["reason"] and found.group(1), "the reason is not named"


def test_s2_a_clean_repository_is_not_called_clean_when_the_secrets_scan_did_not_run(box, host):
    """B-1.5: nothing to refactor is a claim about secrets too. With no gitleaks, a repository with no other blocker gets no
    ``NOTHING-TO-REFACTOR.md``: ``PLAN.md`` says the scan was not run, and the result is not ok."""
    root = P.plant_clean(box.base)
    run, out, before = assess_unscanned(box, host, root, "clean-no-scanner-out")
    assert_unscanned_refusal(run, "MA on a clean repository with no gitleaks on PATH")
    folder = out / W.PLAN_DIR
    assert (out / W.ASSESSMENT).is_file(), "no assessment was written"
    assert not (folder / "NOTHING-TO-REFACTOR.md").exists(), "a clean repository whose secrets were not scanned is said to have nothing to refactor"
    assert not list(folder.glob("RP-*")), f"proposals for a clean repository: {[p.name for p in folder.glob('RP-*')]}"
    assert NOT_SCANNED.search((folder / "PLAN.md").read_text(encoding="utf-8")), "PLAN.md does not hold `secrets: not scanned (<reason>)`"
    W.assert_state_equal(before, W.repo_state(root), "MA on a clean repository with no gitleaks")


def test_s2_a_blob_over_the_scan_limit_is_named_unscanned_and_the_run_is_not_ok(box, host):
    """B-1.5: the scan ran (gitleaks on PATH) but skipped a blob over ``assess.SCAN_LIMIT_BYTES`` (16 MiB): the result is not ok
    (``SECRETS_UNSCANNED``, ``details.unscanned`` naming the file and not a scanned one), ``PLAN.md`` names the file under
    ``secrets: not scanned (<reason>)``, no ``NOTHING-TO-REFACTOR.md``, the assessment is written, the repository unchanged."""
    try:
        from gov.adopt import assess
        limit = int(getattr(assess, "SCAN_LIMIT_BYTES", W.SCAN_LIMIT_FALLBACK))
    except ImportError:
        limit = W.SCAN_LIMIT_FALLBACK
    root = P.plant_clean(box.base, "huge")
    W.write(root, "data/huge.log", "row of the long table\n" * ((limit // 22) + 400))
    W.commit_all(root, "a blob over the scan limit")
    run, out, before = assess_unscanned(box, host, root, "huge-out", environment=W.env(box, host))
    details = assert_unscanned_refusal(run, "MA with a blob over the scan limit")
    assert "data/huge.log" in json.dumps(details["unscanned"]), f"details['unscanned'] does not name the skipped blob: {details['unscanned']!r}"
    assert "README.md" not in json.dumps(details["unscanned"]), f"a scanned file is named unscanned: {details['unscanned']!r}"
    folder = out / W.PLAN_DIR
    assert (out / W.ASSESSMENT).is_file() and not (folder / "NOTHING-TO-REFACTOR.md").exists()
    plan = (folder / "PLAN.md").read_text(encoding="utf-8")
    assert NOT_SCANNED.search(plan) and "data/huge.log" in plan, "PLAN.md does not name the secrets not scanned and the skipped path"
    W.assert_state_equal(before, W.repo_state(root), "MA with a blob over the scan limit")


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
