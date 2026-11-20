"""The judge and its mutation self-tests: adoption's own mutation check (DEC-936 item 3.6, DEC-941, DEC-833).

Every stand-in is written in a temporary folder: a copy of a built repository's
working tree (no .git) with the outputs an adoption would leave. No adoption runs.
``ALL`` treats every capability as built, so the READY path and each mutant are
judged on the stand-in's provisional records. ``built=None`` is today's code, on
which those handlings are NOT_BUILT; A7 and A10 are built there (``gov.adopt.command.STAGES``
lists them: S-STAGES, DEC-1197 (2)), so their records are measured.
"""

from __future__ import annotations

import json
import shutil

import pytest

import w2_81_build as build
import w2_81_judge as judge
import w2_81_standin as standin
from w2_81_secret import assert_absent

ALL = set(judge.CAPABILITIES)
FIGURES = {name: dict(standin.PERFECT_FIGURES) for name in (*build.SHAPES, build.CLEAN)}
EXPECTED = (*build.SHAPES, build.CLEAN)
LITE = ("A7", "A10")  # the lite gates' stages: built when gov.adopt.command.STAGES lists them (S-STAGES)
MISSED_FORMS = ("ABSENT", "UNREADABLE", "MALFORMED")  # a stage's record states that show nothing (README)

# One killed mutant per planted problem: each id below is missed alone, and the judge must name it (README).
PLANTED_IDS = (
    "python-app.misleading-name.live-under-old-name", "python-app.misleading-name.dead-under-current-name",
    "python-app.orphaned-test.module-removed", "python-app.superseded-plan.names-it",
    "python-app.stale-spec.newer-version",
    "rust-workspace.orphaned-test.function-removed", "rust-workspace.superseded-plan.by-version",
    "rust-workspace.stale-spec.newer-rfc",
    "typescript-monorepo.misleading-name.live-under-old-name",
    "typescript-monorepo.misleading-name.dead-under-current-name", "typescript-monorepo.secret.token-in-script",
    "typescript-monorepo.orphaned-test.file-removed", "typescript-monorepo.stale-spec.newer-adr",
    "legacy-docs.legacy-document.extract", "legacy-docs.legacy-document.retire", "legacy-docs.large-file.dataset",
    "legacy-docs.large-file.media", "legacy-docs.superseded-plan.names-it",
    "secret-history.misleading-name.live-under-old-name", "secret-history.misleading-name.dead-under-current-name",
    "secret-history.secret.key-in-config",
)
CONTROL_IDS = tuple(f"{name}.control.{kind}" for name in EXPECTED
                    for kind in ("current-spec-looks-old", "live-file-in-legacy-folder"))


@pytest.fixture(autouse=True)
def _removed_after(tmp_path):
    """Each case removes the stand-in outputs it rendered (pytest keeps only the empty folder)."""
    yield
    for child in tmp_path.iterdir():
        shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()


def _entry(ground, ident):
    name = ident.split(".")[0]
    return ground[name], next(e for e in ground[name].manifest["planted"] + ground[name].manifest["controls"]
                              if e["id"] == ident)


def _judge(built_repo, model, tmp_path, built=ALL):
    """Render ``model`` and judge that one repository."""
    root, beside = standin.render(model, built_repo, tmp_path / "adopted", tmp_path / "beside")
    return judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, built)


def _reasons(judgement, name):
    return judge.overall([judgement], {name: FIGURES[name]}, [name])


def _status(judgement, ident):
    return next(p for p in judgement["planted"] + judgement["controls"] if p["id"] == ident)["status"]


def _never_the_value(built_repo, result):
    for held in built_repo.secrets:
        assert_absent(held, json.dumps(result, sort_keys=True), "the judge's result")


# --------------------------------------------------------------------------
# The READY path, and today's NOT_BUILT
# --------------------------------------------------------------------------

def test_the_mutant_lists_are_the_manifests(ground):
    assert sorted(PLANTED_IDS) == sorted(e["id"] for b in ground.values() for e in b.manifest["planted"])
    assert sorted(CONTROL_IDS) == sorted(c["id"] for b in ground.values() for c in b.manifest["controls"])


def test_a_stand_in_that_handles_everything_is_ready(ground, tmp_path):
    cases = []
    for name, built_repo in ground.items():
        root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / name / "adopted",
                                      tmp_path / name / "beside")
        cases.append((built_repo.manifest_path, root, beside, built_repo.secrets))
    result = judge.judge(cases, FIGURES, EXPECTED, built=ALL)
    assert result["verdict"] == judge.READY, result["reasons"]
    for repository in result["repositories"]:
        assert all(p["status"] == judge.FOUND for p in repository["planted"]), repository["repository"]
        assert all(p["evidence"] and p["evidence"][0]["record"] for p in repository["planted"])
        assert all(c["status"] == judge.CLEAN for c in repository["controls"]), repository["repository"]
    for built_repo in ground.values():
        _never_the_value(built_repo, result)


def test_on_todays_code_the_handlings_not_built_are_named_and_never_passed(ground, tmp_path):
    cases = []
    for name, built_repo in ground.items():
        root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / name / "adopted",
                                      tmp_path / name / "beside")
        cases.append((built_repo.manifest, root, beside, built_repo.secrets))
    result = judge.judge(cases, FIGURES, EXPECTED)  # built=None: today's code
    assert result["verdict"] == judge.NOT_READY
    for repository in result["repositories"]:
        for problem in repository["planted"]:
            if problem["kind"] == "large-file":
                assert problem["status"] == judge.FOUND, problem  # its capabilities are built today
            else:
                assert problem["status"] == judge.NOT_BUILT, problem
                named = [s["field"] for s in problem["evidence"] if s["status"] == judge.NOT_BUILT]
                assert set(named) <= set(judge.NEEDS[problem["kind"]]) and named, problem
        for stage in ("VERDICT", "findings"):
            assert repository["stages"][stage]["status"] == judge.NOT_BUILT, (repository["repository"], stage)
        for stage in LITE:  # S-STAGES: built today (gov.adopt.command.STAGES), so measured: the stand-in's record
            assert repository["stages"][stage]["status"] == "PRESENT", (repository["repository"], stage)
        assert {"VERDICT", "findings"} <= set(repository["not_built"])
        assert not set(LITE) & set(repository["not_built"]), repository["repository"]
    assert any("stage VERDICT is NOT_BUILT" in r for r in result["reasons"])
    assert not [r for r in result["reasons"] for s in LITE if f"stage {s} is" in r], result["reasons"]


def test_todays_built_capabilities_follow_the_code():
    from gov.adopt import command, lite_gates, project

    today = judge.built_today()
    assert {"A2-namespace", "index", "A3", "A5", "A6"} <= today
    assert not today & {"A2-content-class", "findings", "A8-documents", "VERDICT"}
    for stage in LITE:  # S-STAGES: the adoption command's own stage list decides, not project.STAGES
        assert (stage in today) == (stage in command.STAGES), stage
        assert stage in command.STAGES and stage not in project.STAGES, f"{stage}: today's code has moved"
        assert stage in today, stage
        assert judge.record_name(stage) == lite_gates.record_path(stage), stage  # the name the lite gate writes
    for stage in judge.BUILT_STAGES:
        assert judge.record_name(stage) == project.record_path(stage)


def test_a7_and_a10_count_as_built_from_the_commands_stage_list_never_the_projects(monkeypatch):
    """S-STAGES: each lite stage is built exactly when ``gov.adopt.command.STAGES`` lists it, whatever
    ``gov.adopt.project.STAGES`` says (kills a judge that reads project.STAGES, or both lists, or neither)."""
    from gov.adopt import command, project

    monkeypatch.setattr(project, "STAGES", (*project.STAGES, "A7", "A10"))  # the project's list names both
    monkeypatch.setattr(command, "STAGES", tuple(s for s in command.STAGES if s != "A7"))  # the command's, A10 only
    today = judge.built_today()
    assert "A7" not in today and "A10" in today, sorted(today & set(LITE))
    monkeypatch.setattr(command, "STAGES", tuple(s for s in command.STAGES if s != "A10"))  # neither
    assert not judge.built_today() & set(LITE)
    monkeypatch.setattr(project, "STAGES", tuple(s for s in project.STAGES if s not in LITE))
    monkeypatch.setattr(command, "STAGES", (*command.STAGES, "A7", "A10"))  # the command's names both again
    assert set(LITE) <= judge.built_today()


def test_an_adoption_that_ran_nothing_is_not_ready_in_every_repository(ground, tmp_path):
    for name, built_repo in ground.items():
        empty = {"files": [], "records": {}, "findings": [], "path_map": None, "index": None, "extra": {},
                 "removed": [], "beside": {}, "raw": {}}
        judgement = _judge(built_repo, empty, tmp_path / name, built=None)
        assert all(p["status"] in (judge.MISSED, judge.NOT_BUILT) for p in judgement["planted"]), name
        assert all(c["status"] == judge.CLEAN for c in judgement["controls"]), name
        assert all(v["status"] in ("ABSENT", judge.NOT_BUILT) for v in judgement["stages"].values()), name
        for stage in LITE:  # S-STAGES: built today, so its absent record is the missed form, never NOT_BUILT
            assert judgement["stages"][stage]["status"] == "ABSENT", (name, stage)
        result = _reasons(judgement, name)
        assert result["verdict"] == judge.NOT_READY
        assert {f"{name}: stage {s} is ABSENT" for s in LITE} <= set(result["reasons"]), name


# --------------------------------------------------------------------------
# One killed mutant per planted problem
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ident", PLANTED_IDS)
def test_a_stand_in_that_misses_exactly_one_planted_problem_is_not_ready_naming_it(ground, tmp_path, ident):
    built_repo, entry = _entry(ground, ident)
    name = built_repo.name
    judgement = _judge(built_repo, standin.miss(standin.perfect(built_repo), entry), tmp_path)
    result = _reasons(judgement, name)
    assert result["verdict"] == judge.NOT_READY
    assert result["reasons"] == [f"{name}: {ident} is MISSED"], result["reasons"]


# --------------------------------------------------------------------------
# Mishandling
# --------------------------------------------------------------------------

def _first(ground, kind):
    for built_repo in ground.values():
        for entry in built_repo.manifest["planted"]:
            if entry["kind"] == kind:
                yield built_repo, entry


def _mishandled(ground, tmp_path, kind, change, label):
    checked = 0
    for n, (built_repo, entry) in enumerate(_first(ground, kind)):
        model = standin.perfect(built_repo)
        change(model, entry, built_repo)
        judgement = _judge(built_repo, model, tmp_path / f"{label}-{n}")
        result = _reasons(judgement, built_repo.name)
        assert result["verdict"] == judge.NOT_READY
        assert f"{built_repo.name}: {entry['id']} is MISHANDLED" in result["reasons"], (label, result["reasons"])
        _never_the_value(built_repo, judgement)
        checked += 1
    assert checked >= 2 or kind in judge.manifest_form.LEGACY_KINDS, f"{label}: {checked} instances"


def _value(built_repo, entry):
    return next(h for h in built_repo.secrets if h.form == entry["evidence"]["form"])


def test_the_secret_found_but_its_value_in_a_record_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["raw"]["governance/adoption/notes/secret.md"] = _value(built_repo, entry).line("---\nsaw: {value}\n---\n")
    _mishandled(ground, tmp_path, "secret", change, "record")


def test_the_secret_found_but_its_value_in_an_index_store_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["index_text"] = {model["files"][0]: _value(built_repo, entry).line("chunk {value} chunk")}
    _mishandled(ground, tmp_path, "secret", change, "index")


def test_the_secret_found_but_its_value_in_a_log_or_report_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["beside"]["report.md"] = _value(built_repo, entry).line("found {value} in history\n")
    _mishandled(ground, tmp_path, "secret", change, "log")


def test_the_secret_reported_with_more_than_path_commit_and_rule_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        next(f for f in model["findings"] if f["kind"] == "secret")["line"] = 3
    _mishandled(ground, tmp_path, "secret", change, "extra-field")


def test_adopted_healthy_with_the_secret_open_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["records"]["VERDICT"]["verdict"] = "ADOPTED_HEALTHY"
    _mishandled(ground, tmp_path, "secret", change, "healthy")


def test_the_misleading_file_moved_not_proposed_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["removed"].append(entry["paths"][0])
        model["extra"][entry["paths"][0] + ".moved"] = "moved by adoption on its own\n"
    _mishandled(ground, tmp_path, "misleading-name", change, "moved")


def test_a_rename_proposed_and_reviewed_at_a5_is_not_mishandled(ground, tmp_path):
    built_repo = ground["python-app"]
    entry = next(e for e in built_repo.manifest["planted"] if e["variant"] == "live-under-old-name")
    model = standin.perfect(built_repo)
    model["removed"].append(entry["paths"][0])
    model["raw"]["src/renamed.py"] = (built_repo.root / entry["paths"][0]).read_bytes()  # the batch moved it
    standin.a3_entry(model, entry["paths"][0]).update(action="RENAME", target="src/renamed.py", batch=1)
    judgement = _judge(built_repo, model, tmp_path)
    assert _status(judgement, entry["id"]) == judge.FOUND


def test_the_superseded_plan_deleted_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["removed"].append(entry["evidence"]["plan"])
    _mishandled(ground, tmp_path, "superseded-plan", change, "deleted")


def test_the_superseded_plan_proposed_for_deletion_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        standin.a3_entry(model, entry["evidence"]["plan"]).update(action="DELETE_FROM_ACTIVE_TREE", batch=1)
    _mishandled(ground, tmp_path, "superseded-plan", change, "proposed-delete")


def test_the_orphaned_test_deleted_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["removed"].append(entry["evidence"]["test"])
    _mishandled(ground, tmp_path, "orphaned-test", change, "deleted")


def test_the_orphaned_test_silently_skipped_is_mishandled(ground, tmp_path):
    marks = {".py": "import pytest\npytestmark = pytest.mark." + "skip\n", ".rs": "#[" + "ignore]\n",
             ".ts": "test." + "skip(\"x\", () => {});\n"}

    def change(model, entry, built_repo):
        rel = entry["evidence"]["test"]
        text = (built_repo.root / rel).read_text()
        model["raw"][rel] = marks[rel[rel.rindex("."):]] + text
        model["findings"] = [f for f in model["findings"] if f.get("test") != rel]
    _mishandled(ground, tmp_path, "orphaned-test", change, "skipped")


def test_the_stale_spec_cited_as_governing_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        standin.a2_entry(model, entry["evidence"]["governing"])["superseded_by"] = entry["evidence"]["stale"]
    _mishandled(ground, tmp_path, "stale-spec", change, "cited")


def test_the_stale_spec_classed_current_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        standin.a2_entry(model, entry["evidence"]["stale"])["class"] = "current"
    _mishandled(ground, tmp_path, "stale-spec", change, "current")


def test_a_large_file_in_the_semantic_index_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        model["index"][entry["evidence"]["path"]] = True
    _mishandled(ground, tmp_path, "large-file", change, "embedded")


def test_a_legacy_document_given_the_other_disposition_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        for item in model["records"]["A8"]["documents"]:
            if item["path"] == entry["evidence"]["path"]:
                item["disposition"] = "retired" if item["disposition"] == "extracted" else "extracted"
                item.pop("into", None)
    _mishandled(ground, tmp_path, "legacy-document", change, "disposition")


def test_a_misleading_name_classed_by_its_looks_is_mishandled(ground, tmp_path):
    def change(model, entry, built_repo):
        standin.a2_entry(model, entry["paths"][0])["class"] = "dead" if entry["evidence"]["live"] else "live"
    _mishandled(ground, tmp_path, "misleading-name", change, "misclassed")


# --------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ident", CONTROL_IDS)
def test_a_stand_in_that_flags_a_control_is_not_ready_naming_it(ground, tmp_path, ident):
    built_repo, control = _entry(ground, ident)
    judgement = _judge(built_repo, standin.flag(standin.perfect(built_repo), control), tmp_path)
    result = _reasons(judgement, built_repo.name)
    assert result["reasons"] == [f"{built_repo.name}: {ident} is FLAGGED"], result["reasons"]


def test_a_control_proposed_for_retirement_or_named_by_a_finding_is_flagged(ground, tmp_path):
    built_repo = ground["rust-workspace"]
    for n, control in enumerate(built_repo.manifest["controls"]):
        model = standin.perfect(built_repo)
        standin.a3_entry(model, control["paths"][0]).update(action="RETIRE", kind="rule-file")
        assert _status(_judge(built_repo, model, tmp_path / f"retire-{n}"), control["id"]) == judge.FLAGGED
        model = standin.perfect(built_repo)
        model["findings"].append({"id": "FINDING-900", "type": "finding", "kind": "drift", "state": "OPEN",
                                  "human_gate": "owner", "paths": [control["paths"][0]], "newer_source": "x"})
        assert _status(_judge(built_repo, model, tmp_path / f"finding-{n}"), control["id"]) == judge.FLAGGED


# --------------------------------------------------------------------------
# Failing closed
# --------------------------------------------------------------------------

def _a2_problems(judgement):
    return [p for p in judgement["planted"] if p["kind"] in ("superseded-plan", "misleading-name", "large-file")]


@pytest.mark.parametrize("how", ["missing", "binary", "bad-yaml", "no-front-matter", "not-a-list", "no-path",
                                 "unknown-class"])
def test_a_missing_unreadable_or_malformed_record_is_missed_never_handled(ground, tmp_path, how):
    built_repo = ground["python-app"]
    model = standin.perfect(built_repo)
    rel = judge.record_name("A2")
    if how == "missing":
        model["records"]["A2"] = None
    elif how == "binary":
        model["records"]["A2"], model["raw"][rel] = None, b"\xff\xfe\x00\x01 not text"
    elif how == "bad-yaml":
        model["records"]["A2"], model["raw"][rel] = None, b"---\nartefacts: [\n---\n"
    elif how == "no-front-matter":
        model["records"]["A2"], model["raw"][rel] = None, b"# A2\n\nartefacts: none\n"
    elif how == "not-a-list":
        model["records"]["A2"]["artefacts"] = "every file"
    elif how == "no-path":
        model["records"]["A2"]["artefacts"][0].pop("path")
    elif how == "unknown-class":
        model["records"]["A2"]["artefacts"][0]["class"] = "fine"
    judgement = _judge(built_repo, model, tmp_path)
    problems = _a2_problems(judgement)
    assert problems and all(p["status"] == judge.MISSED for p in problems), [(p["id"], p["status"]) for p in problems]
    assert judgement["stages"]["A2"]["status"] in ("ABSENT", "UNREADABLE", "MALFORMED")
    assert _reasons(judgement, built_repo.name)["verdict"] == judge.NOT_READY


def test_a_control_whose_record_cannot_be_read_is_flagged(ground, tmp_path):
    built_repo = ground["python-app"]
    model = standin.perfect(built_repo)
    model["records"]["A3"], model["raw"][judge.record_name("A3")] = None, b"\x00\x01"
    judgement = _judge(built_repo, model, tmp_path)
    assert all(c["status"] == judge.FLAGGED for c in judgement["controls"])


def test_an_unreadable_finding_or_output_rules_nothing_out_for_the_secret(ground, tmp_path):
    built_repo = ground["secret-history"]
    entry = next(e for e in built_repo.manifest["planted"] if e["kind"] == "secret")
    model = standin.perfect(built_repo)
    model["raw"][f"{judge.FINDINGS}/FINDING-999.md"] = b"\xff\xfe"
    assert _status(_judge(built_repo, model, tmp_path / "finding"), entry["id"]) == judge.MISSED
    root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / "link" / "adopted",
                                  tmp_path / "link" / "beside")
    (beside / "elsewhere.log").symlink_to(tmp_path / "nowhere")
    judgement = judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, ALL)
    assert _status(judgement, entry["id"]) == judge.MISSED
    no_value = judge.judge_repository(built_repo.manifest, root, None, [], ALL)
    assert _status(no_value, entry["id"]) == judge.MISSED, "no value to compare with rules nothing out"


def test_an_absent_stage_is_named(ground, tmp_path):
    built_repo = ground["python-app"]
    model = standin.perfect(built_repo)
    model["records"]["A7"] = None
    judgement = _judge(built_repo, model, tmp_path)
    assert judgement["stages"]["A7"]["status"] == "ABSENT"
    assert f"{built_repo.name}: stage A7 is ABSENT" in _reasons(judgement, built_repo.name)["reasons"]
    model["records"]["VERDICT"]["verdict"] = "FINE"
    judgement = _judge(built_repo, model, tmp_path / "verdict")
    assert judgement["stages"]["VERDICT"]["status"] == "MALFORMED"


# --------------------------------------------------------------------------
# S-STAGES (DEC-1197 (2)): A7 and A10 on today's code (built=None), built from gov.adopt.command.STAGES
# --------------------------------------------------------------------------

# How a lite record is spoiled, and the stage state the judge must give (the missed form, README "Today's list").
SPOILED = {"absent": "ABSENT", "not-a-mapping": "UNREADABLE", "bad-yaml": "UNREADABLE", "no-front-matter": "UNREADABLE"}


def _spoil(model, stage, how):
    rel = judge.record_name(stage)
    model["records"][stage] = None
    if how == "not-a-mapping":
        model["raw"][rel] = f"---\n- stage: {stage}\n- result: pass\n---\n".encode()
    elif how == "bad-yaml":
        model["raw"][rel] = f"---\nstage: {stage}\nresult: [pass\n---\n".encode()
    elif how == "no-front-matter":
        model["raw"][rel] = f"# ADOPT-{stage}\n\nstage: {stage}\nresult: pass\n".encode()


@pytest.mark.parametrize("how", sorted(SPOILED))
@pytest.mark.parametrize("stage", LITE)
def test_on_todays_code_a_lite_record_absent_or_malformed_is_missed_and_named_never_not_built(ground, tmp_path,
                                                                                               stage, how):
    """Kills a judge that gives the lite stage NOT_BUILT on today's code (it reads project.STAGES), or passes it
    PRESENT on a record that is missing or cannot be read, or leaves it out of the verdict's reasons."""
    built_repo = ground["python-app"]
    name = built_repo.name
    whole = _judge(built_repo, standin.perfect(built_repo), tmp_path / "whole", built=None)
    model = standin.perfect(built_repo)
    _spoil(model, stage, how)
    spoiled = _judge(built_repo, model, tmp_path / "spoiled", built=None)
    status = spoiled["stages"][stage]["status"]
    assert status == SPOILED[how] and status in MISSED_FORMS, (stage, how, status)  # never NOT_BUILT, never PRESENT
    assert spoiled["stages"][stage]["record"] == judge.record_name(stage)
    assert stage not in spoiled["not_built"], spoiled["not_built"]
    assert whole["stages"][stage]["status"] == "PRESENT"
    result, before = _reasons(spoiled, name), _reasons(whole, name)
    assert result["verdict"] == judge.NOT_READY
    added = [f"{name}: stage {stage} is {SPOILED[how]}"]
    assert sorted(result["reasons"]) == sorted(before["reasons"] + added), result["reasons"]
    other = next(s for s in LITE if s != stage)
    assert spoiled["stages"][other]["status"] == "PRESENT", other  # the spoiled record names its own stage only
    assert [(p["id"], p["status"]) for p in spoiled["planted"]] == [(p["id"], p["status"]) for p in whole["planted"]]


@pytest.mark.parametrize("stage", LITE)
def test_on_todays_code_a_lite_record_absent_alone_is_not_ready_naming_it(ground, tmp_path, stage):
    """With every other capability given as built and every other record whole, the lite record absent is the one
    reason: today's built set for the stage itself (built_today()), not ALL, decides that the stage is measured."""
    built_repo = ground["python-app-clean"]
    name = built_repo.name
    others = (ALL - set(LITE)) | (judge.built_today() & set(LITE))  # the lite stages as today's code has them
    model = standin.perfect(built_repo)
    model["records"][stage] = None
    result = _reasons(_judge(built_repo, model, tmp_path, built=others), name)
    assert result["verdict"] == judge.NOT_READY
    assert result["reasons"] == [f"{name}: stage {stage} is ABSENT"], result["reasons"]


# A lite gate commits its record even when it fails, with `result: fail` (S-STAGES: a failed gate is never passed).
# How the record's `result` is spoiled: the value written, or None for the field removed. Each is MALFORMED.
GATE_RESULT = {"fail": "fail", "removed": None, "other": "met"}


@pytest.mark.parametrize("how", sorted(GATE_RESULT))
@pytest.mark.parametrize("stage", LITE)
def test_on_todays_code_a_lite_record_whose_gate_result_is_not_pass_is_malformed_and_named(ground, tmp_path,
                                                                                           stage, how):
    """A lite record whose front matter parses but whose `result` is not exactly `pass` (a failed gate's record, the
    field removed, another word) is MALFORMED: missed and named, NOT_READY, never PRESENT and never NOT_BUILT, and
    every other status unchanged. Kills a judge that counts a failed A7 or A10 gate's record as found."""
    built_repo = ground["python-app"]
    name = built_repo.name
    whole = _judge(built_repo, standin.perfect(built_repo), tmp_path / "whole", built=None)
    model = standin.perfect(built_repo)
    if GATE_RESULT[how] is None:
        del model["records"][stage]["result"]
    else:
        model["records"][stage]["result"] = GATE_RESULT[how]
    spoiled = _judge(built_repo, model, tmp_path / "spoiled", built=None)
    rel = judge.record_name(stage)
    front = judge.read_record(tmp_path / "spoiled" / "adopted", rel, stage)
    assert front.state == "MALFORMED" and front.data["stage"] == stage, (stage, how, front.state, front.why)
    assert "result" in front.why and "pass" in front.why, front.why  # the why names the gate's own result
    assert whole["stages"][stage] == {"status": "PRESENT", "record": rel}, whole["stages"][stage]
    assert spoiled["stages"][stage] == {"status": "MALFORMED", "record": rel}, spoiled["stages"][stage]
    assert stage not in spoiled["not_built"], spoiled["not_built"]
    result, before = _reasons(spoiled, name), _reasons(whole, name)
    assert result["verdict"] == judge.NOT_READY
    assert sorted(result["reasons"]) == sorted(before["reasons"] + [f"{name}: stage {stage} is MALFORMED"]), \
        result["reasons"]
    assert {s: v for s, v in spoiled["stages"].items() if s != stage} == \
        {s: v for s, v in whole["stages"].items() if s != stage}  # every other stage unchanged
    assert [(p["id"], p["status"]) for p in spoiled["planted"]] == [(p["id"], p["status"]) for p in whole["planted"]]
    assert [(c["id"], c["status"]) for c in spoiled["controls"]] == [(c["id"], c["status"]) for c in whole["controls"]]


def test_on_todays_code_both_lite_records_in_the_stages_front_matter_are_present(ground, tmp_path):
    """Both lite records as the stand-in writes them (the stages' front matter, at the names the lite gates write)
    are PRESENT on today's code: the found form; kills a judge that still names them NOT_BUILT or cannot read them."""
    built_repo = ground["secret-history"]
    judgement = _judge(built_repo, standin.perfect(built_repo), tmp_path, built=None)
    for stage in LITE:
        rel = judge.record_name(stage)
        front = judge.read_record(tmp_path / "adopted", rel, stage)
        assert front.state == "PRESENT" and front.data["stage"] == stage, (stage, front.state, front.why)
        assert front.data["result"] == "pass", (stage, front.data)  # the gate's own word: the found form needs it
        assert judgement["stages"][stage] == {"status": "PRESENT", "record": rel}, judgement["stages"][stage]
    assert not set(LITE) & set(judgement["not_built"]), judgement["not_built"]
    reasons = _reasons(judgement, built_repo.name)["reasons"]
    assert not [r for r in reasons for s in LITE if f"stage {s} is" in r], reasons


def test_a_judge_error_is_an_error_never_ready(ground, tmp_path, monkeypatch):
    built_repo = ground["python-app"]
    root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / "adopted", tmp_path / "beside")
    gone = judge.judge([(tmp_path / "no-manifest.json", root, beside, [])], FIGURES, ["python-app"], ALL)
    assert gone["verdict"] == judge.ERROR
    broken = dict(built_repo.manifest, form="something else")
    assert judge.judge([(broken, root, beside, [])], FIGURES, ["python-app"], ALL)["verdict"] == judge.ERROR

    def explode(root):
        raise RuntimeError("the index exploded")
    monkeypatch.setattr(judge, "read_index", explode)
    result = judge.judge([(built_repo.manifest, root, beside, [])], FIGURES, ["python-app"], ALL)
    assert result["verdict"] == judge.ERROR and result["error"] == "RuntimeError"


def test_a_repository_not_judged_is_not_ready(ground, tmp_path):
    built_repo = ground["python-app-clean"]
    root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / "adopted", tmp_path / "beside")
    result = judge.judge([(built_repo.manifest, root, beside, [])], FIGURES, EXPECTED, ALL)
    assert result["verdict"] == judge.NOT_READY
    assert "python-app: not judged" in result["reasons"]


# --------------------------------------------------------------------------
# The figures, and the value never in the judge's output
# --------------------------------------------------------------------------

@pytest.mark.parametrize("figures, said", [
    ({"end_to_end": 94.0}, "the end-to-end figure is 94, below its bar of 95"),
    ({"end_to_end": 94.9}, "the end-to-end figure is 94.9, below its bar of 95"),
    ({"end_to_end": 0.0}, "the end-to-end figure is 0, below its bar of 95"),
    ({"end_to_end": 94.0, "hit_at_5": 100.0, "stacked_share": 100.0}, "the end-to-end figure is 94, below its bar"),
    ({"hit_at_5": 100.0, "stacked_share": 100.0}, "the end-to-end figure is missing"),
    ({"end_to_end": True}, "the end-to-end figure is missing"),
    ({"end_to_end": float("nan")}, "the end-to-end figure is missing"),
    ({"end_to_end": "99"}, "the end-to-end figure is missing"),
    ({}, "the end-to-end figure is missing"),
    (None, "the end-to-end figure is missing"),
])
def test_a_figure_below_its_bar_or_missing_is_not_ready(ground, tmp_path, figures, said):
    """DEC-1221 (1): a repository's end-to-end figure under 95, or missing, is NOT_READY naming the repository."""
    built_repo = ground["python-app-clean"]
    judgement = _judge(built_repo, standin.perfect(built_repo), tmp_path)
    result = judge.overall([judgement], {built_repo.name: figures}, [built_repo.name])
    assert result["verdict"] == judge.NOT_READY
    assert any(reason.startswith(f"{built_repo.name}: ") and said in reason for reason in result["reasons"]), \
        result["reasons"]
    at_bar = judge.overall([judgement], {built_repo.name: standin.PERFECT_FIGURES}, [built_repo.name])
    assert at_bar["verdict"] == judge.READY, at_bar["reasons"]


@pytest.mark.parametrize("figures", [
    {"end_to_end": 95.0}, {"end_to_end": 100.0},
    {"end_to_end": 95.0, "hit_at_5": 0.0, "stacked_share": 0.0},
    {"end_to_end": 100.0, "hit_at_5": 0.0},
    {"end_to_end": 100.0, "hit_at_5": None, "stacked_share": None},
    {"end_to_end": 96.0, "stacked_share": 3.0},
])
def test_hit_at_5_and_the_stacked_share_are_diagnostics_and_never_make_anything_not_ready(ground, tmp_path, figures):
    """EMERGENCY-2 5.2: hit@k is not a floor anywhere: low or absent beside a figure at the bar, READY stands."""
    built_repo = ground["python-app-clean"]
    judgement = _judge(built_repo, standin.perfect(built_repo), tmp_path)
    result = judge.overall([judgement], {built_repo.name: figures}, [built_repo.name])
    assert result["verdict"] == judge.READY, result["reasons"]
    assert not hasattr(judge, "FLOORS")


def test_a_repository_at_94_is_not_ready_naming_it_and_at_95_in_every_repository_it_is_ready(ground, tmp_path):
    """The whole judge over six repositories: 95 each is READY; one at 94 is NOT_READY naming that one alone."""
    cases = []
    for name, built_repo in ground.items():
        root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / name / "adopted",
                                      tmp_path / name / "beside")
        cases.append((built_repo.manifest, root, beside, built_repo.secrets))
    at_95 = {name: {"end_to_end": 95.0} for name in EXPECTED}
    ready = judge.judge(cases, at_95, EXPECTED, built=ALL)
    assert ready["verdict"] == judge.READY, ready["reasons"]
    judgements = ready["repositories"]  # the same judgements, read again against other figures
    for name in EXPECTED:
        one_low = {**at_95, name: {"end_to_end": 94.0}}
        result = judge.overall(judgements, one_low, EXPECTED)
        assert result["verdict"] == judge.NOT_READY
        assert result["reasons"] == [f"{name}: the end-to-end figure is 94, below its bar of 95"], result["reasons"]
    missing = {k: v for k, v in at_95.items() if k != "rust-workspace"}
    assert judge.overall(judgements, missing, EXPECTED)["reasons"] == [
        "rust-workspace: the end-to-end figure is missing (its bar is 95)"]


def test_the_judge_never_writes_the_value_even_when_an_output_is_named_by_it(ground, tmp_path, capfd):
    built_repo = ground["typescript-monorepo"]
    entry = next(e for e in built_repo.manifest["planted"] if e["kind"] == "secret")
    held = _value(built_repo, entry)
    model = standin.perfect(built_repo)
    model["beside"][held.line("{value}.log")] = "a log named by the value\n"
    root, beside = standin.render(model, built_repo, tmp_path / "adopted", tmp_path / "beside")
    result = judge.judge([(built_repo.manifest, root, beside, built_repo.secrets)], FIGURES, [built_repo.name], ALL)
    assert result["verdict"] == judge.NOT_READY
    assert f"{built_repo.name}: {entry['id']} is MISHANDLED" in result["reasons"]
    out, err = capfd.readouterr()
    for text, where in ((json.dumps(result), "the result"), (out, "standard output"), (err, "standard error")):
        assert_absent(held, text, where)


# --------------------------------------------------------------------------
# Fix T2 (W2-81's proving run on 0.1.4): stage AS, the spec audit (CAP-44.m), is a required stage of the judge
# --------------------------------------------------------------------------

AS_RECORD = "governance/adoption/AS-spec-audit.md"  # the name `gov adopt --lite --stage AS` commits its record under
AS_DATA = {"stands_on": "0" * 64, "specs": [], "modules": [], "tickets": [], "gaps": []}


def _with_as(model):
    model["records"]["AS"] = dict(AS_DATA)
    return model


def test_stage_as_is_in_the_stage_list_between_a2_and_a3_and_in_the_capability_table():
    from gov.adopt import spec_audit

    assert spec_audit.RECORD == AS_RECORD, "today's code names the record as this suite does"
    assert "AS" in judge.STAGES
    stages = judge.STAGES
    assert stages.index("A2") + 1 == stages.index("AS") and stages.index("AS") + 1 == stages.index("A3"), stages
    assert judge.record_name("AS") == AS_RECORD
    contract, built, why = judge.CAPABILITIES["AS"]
    assert contract == "CAP-44.m" and built is True and why
    assert "AS" in judge.built_today()


def test_a_present_as_record_is_present_and_gives_no_reason(ground, tmp_path):
    built_repo = ground["python-app"]
    judgement = _judge(built_repo, _with_as(standin.perfect(built_repo)), tmp_path)
    assert judgement["stages"]["AS"] == {"status": "PRESENT", "record": AS_RECORD}
    result = _reasons(judgement, built_repo.name)
    assert result["verdict"] == judge.READY, result["reasons"]
    assert not any("stage AS" in r for r in result["reasons"]), result["reasons"]


@pytest.mark.parametrize("built", [ALL, None], ids=["all-built", "todays-code"])
@pytest.mark.parametrize("how, status", [("absent", "ABSENT"), ("no-front-matter", "UNREADABLE"),
                                         ("front-matter-not-a-mapping", "UNREADABLE"), ("bad-yaml", "UNREADABLE")])
def test_an_as_record_that_is_absent_or_unreadable_is_named_and_the_run_is_not_ready(ground, tmp_path, how, status,
                                                                                    built):
    """The missed form of a stage the judge builds (its record's own state: ABSENT, UNREADABLE or MALFORMED), never
    NOT_BUILT and never PRESENT: ``stage AS is <state>`` in the reasons, NOT_READY, and no other stage touched."""
    built_repo = ground["python-app-clean"]
    model = standin.perfect(built_repo)
    model["records"]["AS"] = None
    model["raw"] = {} if how == "absent" else {AS_RECORD: {
        "no-front-matter": b"# the spec audit, with no front matter\n",
        "front-matter-not-a-mapping": b"---\n- one\n- two\n---\n",
        "bad-yaml": b"---\nspecs: [unclosed\n---\n"}[how]}
    judgement = _judge(built_repo, model, tmp_path, built=built)
    assert judgement["stages"]["AS"]["status"] == status and status in MISSED_FORMS
    assert judgement["stages"]["AS"]["record"] == AS_RECORD
    assert all(v["status"] == "PRESENT" for s, v in judgement["stages"].items() if s in ("A0", "A1", "A2", "A3", "A7"))
    result = _reasons(judgement, built_repo.name)
    assert result["verdict"] == judge.NOT_READY
    assert f"{built_repo.name}: stage AS is {status}" in result["reasons"], result["reasons"]
    if built is ALL:
        assert result["reasons"] == [f"{built_repo.name}: stage AS is {status}"], "AS alone is what is named"


def test_an_adoption_that_ran_nothing_names_stage_as_absent(ground, tmp_path):
    built_repo = ground["python-app-clean"]
    empty = {"files": [], "records": {}, "findings": [], "path_map": None, "index": None, "extra": {},
             "removed": [], "beside": {}, "raw": {}}
    judgement = _judge(built_repo, empty, tmp_path, built=None)
    assert judgement["stages"]["AS"]["status"] == "ABSENT" and "AS" not in judgement["not_built"]
    assert f"{built_repo.name}: stage AS is ABSENT" in _reasons(judgement, built_repo.name)["reasons"]
