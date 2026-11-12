"""Builder tests for W2-23, adoption safety on a real repository: S1, S3, S4, S5, S7 and F1. Regression evidence only.

Planted repositories in ``tmp_path`` (the ``root`` fixture and helpers of ``test_adopt``, which replace the code
graph and the index refresh). A failure or a kill inside a batch is planted by wrapping ``stages.git``: a
``GovError`` on the n-th move is a failed step, a ``KeyboardInterrupt`` there is a kill (nothing after it runs).
No parametrize: the suite keeps only the first case of each.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from gov.adopt import project, safety, stages
from gov.cli.errors import GovError

from .test_adopt import PATHS, VERDICT, commit, config, proposal, record, refused, root, sh, stage, verdict, write  # noqa: F401

THREE = ({"path": "lib/util.py", "action": "MOVE", "target": "pkg/util.py", "batch": 1},
         {"path": "lib/other.py", "action": "MOVE", "target": "pkg/other.py", "batch": 1},
         {"path": "scripts/run.py", "action": "MOVE", "target": "pkg/run.py", "batch": 1},
         {"path": "docs/old.md", "action": "DELETE_FROM_ACTIVE_TREE", "batch": 2})


def audited(root, *entries, conf=None):
    for name in ("A0", "A1", "A2"):
        stage(root, name, conf=conf)
    stage(root, "A3", conf=conf, map=proposal(root, *entries))
    stage(root, "A4", conf=conf)
    verdict(root)
    stage(root, "A5", conf=conf, verdict=VERDICT)


def at_move(monkeypatch, step, error, before=None):
    """Make the ``step``-th ``git mv`` of the stages raise ``error`` (``before`` runs first, inside the batch)."""
    moves = []

    def git(root, *args):
        if args and args[0] == "mv":
            moves.append(args)
            if len(moves) == step:
                if before:
                    before(root)
                raise error
        return project.git(root, *args)

    monkeypatch.setattr(stages, "git", git)


def staged(root):
    return sh(root, "diff", "--cached", "--no-renames", "--name-only")


def digests(root, rels):
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in rels}


# ---------------------------------------------------------------- S1: the restore deletes only what the tool wrote

def test_s1_restore_deletes_only_the_named_paths_and_an_untracked_folder_does_not_raise(tmp_path):
    repo = tmp_path / "repo"
    write(repo, "a.txt", "a\n")
    sh(repo, "init", "-q")
    sh(repo, "config", "user.name", "t")
    sh(repo, "config", "user.email", "t@example.invalid")
    head = commit(repo, "base")
    write(repo, "mine.txt", "the user's own\n")             # untracked, not the tool's
    write(repo, "notes/deep/n.md", "a folder of the user\n")  # an untracked folder
    nested = repo / "vendor"                                   # an untracked repository: git lists it as "vendor/"
    write(nested, "x", "x\n")
    subprocess.run(["git", "-C", str(nested), "init", "-q"], check=True)
    write(repo, "written.txt", "by the tool\n")
    write(repo, "a.txt", "changed\n")
    before = digests(repo, ["mine.txt", "notes/deep/n.md", "vendor/x"])
    project.restore(repo.resolve(), head, ["written.txt", "a.txt"])
    assert not (repo / "written.txt").exists() and (repo / "a.txt").read_text() == "a\n"
    assert digests(repo, before) == before and (repo / "vendor/.git").is_dir()


def test_s1_a_failed_batch_keeps_a_file_the_user_made_during_it_and_removes_the_batchs_own(root, monkeypatch):
    audited(root, *THREE)
    at_move(monkeypatch, 3, project.refuse("GIT_FAILED", "planted failure at the third step"),
            before=lambda where: write(where, "user-notes.txt", "written by the user during the batch\n"))
    refused("BATCH_FAILED", root, "A6")
    assert (root / "user-notes.txt").read_text() == "written by the user during the batch\n"
    assert not (root / "pkg").exists() and (root / "lib/util.py").is_file() and staged(root) == ""


def test_s1_a_stage_writes_nothing_over_an_untracked_file(root):
    write(root, ".gitignore", ".gov-runtime/\ngovernance/\n")
    commit(root, "ignore the records' folder")
    write(root, project.record_path("A0"), "the user's own, ignored\n")
    refused("WOULD_OVERWRITE", root, "A0")
    assert (root / project.record_path("A0")).read_text() == "the user's own, ignored\n"


# ---------------------------------------------------------------- S4: a failed or killed batch resumes

def test_s4_a_batch_failing_at_its_third_step_commits_a_failed_record_and_the_next_run_resumes(root, monkeypatch):
    audited(root, *THREE)
    at_move(monkeypatch, 3, project.refuse("GIT_FAILED", "planted failure at the third step"))
    error = refused("BATCH_FAILED", root, "A6")
    assert error.details["failed_batch"] == 1 and "--stage A6" in error.message
    failed = record(root, "A6")
    assert failed["status"] == "failed" and failed["failed_batch"] == 1 and failed["batches"][0]["status"] == "failed"
    assert staged(root) == "" and project.dirty(root) == []
    monkeypatch.setattr(stages, "git", project.git)
    stage(root, "A6")
    done = record(root, "A6")
    assert done["status"] == "done" and [item["batch"] for item in done["batches"]] == [1, 2]
    assert done["run_id"] != failed["run_id"] and failed["run_id"] in done["resumed_from"]
    points = [item["rollback_point"] for item in done["batches"]]
    assert all(f"/{done['run_id']}/" in point for point in points) and failed["batches"][0]["rollback_point"] not in points
    assert (root / "pkg/run.py").is_file() and not (root / "docs/old.md").exists() and staged(root) == ""


def test_s4_a_failure_in_a_later_batch_keeps_the_batches_done_and_resumes_after_them(root, monkeypatch):
    audited(root, {"path": "lib/util.py", "action": "MOVE", "target": "pkg/util.py", "batch": 1},
            {"path": "lib/other.py", "action": "MOVE", "target": "pkg/other.py", "batch": 2})
    at_move(monkeypatch, 2, project.refuse("GIT_FAILED", "planted"))
    refused("BATCH_FAILED", root, "A6")
    failed = record(root, "A6")
    assert [(item["batch"], item["status"]) for item in failed["batches"]] == [(1, "done"), (2, "failed")]
    assert failed["batches"][0]["commit"] and failed["batches"][0]["artefacts"][0]["target"] == "pkg/util.py"
    monkeypatch.setattr(stages, "git", project.git)
    stage(root, "A6")  # batch 1 is done, not "not at its origin"
    assert [item["batch"] for item in record(root, "A6")["batches"]] == [1, 2] and (root / "pkg/other.py").is_file()


def test_s4_a_batch_killed_between_steps_is_unstaged_by_the_next_run_which_continues(root, monkeypatch):
    audited(root, *THREE)
    at_move(monkeypatch, 3, KeyboardInterrupt())
    with pytest.raises(KeyboardInterrupt):
        stage(root, "A6")
    assert set(staged(root).split()) == {"lib/util.py", "lib/other.py", "pkg/util.py", "pkg/other.py"}
    saved = safety.load(root)  # the record the resume continues from: the batch in progress, before its moves
    assert saved["in_progress"]["batch"] == 1 and saved["in_progress"]["start"] == sh(root, "rev-parse", "HEAD")
    monkeypatch.setattr(stages, "git", project.git)
    stage(root, "A6")
    assert record(root, "A6")["status"] == "done" and staged(root) == "" and project.dirty(root) == []
    assert (root / "pkg/run.py").is_file() and safety.load(root) is None


def test_s4_a_killed_batch_with_anything_else_staged_is_refused_naming_it_and_nothing_is_reset(root, monkeypatch):
    audited(root, *THREE)
    at_move(monkeypatch, 2, KeyboardInterrupt())
    with pytest.raises(KeyboardInterrupt):
        stage(root, "A6")
    write(root, "README.md", "# changed by the user\n")
    sh(root, "add", "README.md")
    before = staged(root)
    monkeypatch.setattr(stages, "git", project.git)
    error = refused("TREE_NOT_CLEAN", root, "A6")
    assert "README.md" in error.details["paths"] and staged(root) == before
    assert (root / "README.md").read_text() == "# changed by the user\n"


def test_s4_a_run_killed_after_its_first_batch_resumes_at_the_second(root, monkeypatch):
    audited(root, {"path": "lib/util.py", "action": "MOVE", "target": "pkg/util.py", "batch": 1},
            {"path": "lib/other.py", "action": "MOVE", "target": "pkg/other.py", "batch": 2})
    at_move(monkeypatch, 2, KeyboardInterrupt())
    with pytest.raises(KeyboardInterrupt):
        stage(root, "A6")
    monkeypatch.setattr(stages, "git", project.git)
    stage(root, "A6")
    done = record(root, "A6")["batches"]
    assert [item["batch"] for item in done] == [1, 2] and done[0]["commit"] != done[1]["commit"]


def test_s4_a8_does_not_stand_on_a_failed_a6(root, monkeypatch):
    audited(root, *THREE)
    at_move(monkeypatch, 1, project.refuse("GIT_FAILED", "planted"))
    refused("BATCH_FAILED", root, "A6")
    refused("A6_NOT_DONE", root, "A8")


# ---------------------------------------------------------------- S5: set up at A0, refused by no later stage

def test_s5_a0_writes_gitleaks_and_the_ignore_line_in_its_commit_and_no_later_stage_refuses(root):
    write(root, ".gitignore", "*.pyc\n")
    commit(root, "an ignore file without .gov-runtime/")
    result = stage(root, "A0")
    assert result["set_up"] == [".gitignore", ".gitleaks.toml"]
    assert set(sh(root, "show", "--name-only", "--format=", "HEAD").split()) == {
        ".gitignore", ".gitleaks.toml", project.record_path("A0")}
    assert (root / ".gitleaks.toml").read_bytes() == safety.TEMPLATE_GITLEAKS.read_bytes()
    assert (root / ".gitignore").read_text() == "*.pyc\n.gov-runtime/\n"
    for name in ("A1", "A2"):  # the path map names neither file: they are not unknown
        stage(root, name)
    assert record(root, "A2")["unknown"] == []
    stage(root, "A3", map=proposal(root, THREE[0]))
    stage(root, "A4")
    verdict(root)
    stage(root, "A5", verdict=VERDICT)
    stage(root, "A6")
    write(root, ".gov-runtime/store.db", "derived")
    assert project.dirty(root) == []


def test_s5_an_existing_gitleaks_file_and_ignore_line_are_not_touched(root):
    write(root, ".gitleaks.toml", "# the programme's own\n")
    commit(root, "own gitleaks")
    stage(root, "A0")
    assert (root / ".gitleaks.toml").read_text() == "# the programme's own\n"
    assert sh(root, "show", "--name-only", "--format=", "HEAD").split() == [project.record_path("A0")]
    assert record(root, "A0")["set_up"] == []


# ---------------------------------------------------------------- S7: a target no namespace holds

def test_s7_a3_refuses_a_target_no_namespace_holds_before_its_record(root):
    for name in ("A0", "A1", "A2"):
        stage(root, name)
    head = sh(root, "rev-parse", "HEAD")
    error = refused("TARGET_UNHELD", root, "A3", map=proposal(
        root, {"path": "lib/util.py", "action": "MOVE", "target": "nowhere/util.py"}, THREE[1]))
    assert error.details["targets"] == ["nowhere/util.py"] and "nowhere/util.py" in error.message
    assert sh(root, "rev-parse", "HEAD") == head and not (root / project.record_path("A3")).exists()
    assert project.dirty(root) == []


def test_s7_a6_refuses_a_target_the_path_map_no_longer_holds_before_any_batch(root):
    audited(root, *THREE)
    tree = project.tree(root)
    narrow = config(paths=tuple(path for path in PATHS if path != "pkg/**") + ("pkg/util.py",))
    error = refused("TARGET_UNHELD", root, "A6", conf=narrow)
    assert error.details["targets"] == ["pkg/other.py", "pkg/run.py"]
    assert project.tree(root) == tree and project.dirty(root) == [] and not (root / "pkg").exists()


# ---------------------------------------------------------------- S3: the citation forms of the A8 proof

STORE = "legacy/memory/index.md"
LISTED = {  # form -> a citation of that form, as planted
    "a word character directly before the path": ("path", "seeoldlegacy/memory/index.md"),
    "a dash directly before the id": ("id", "x-MEM-7"),
    "backslashes": ("path", "legacy\\memory\\index.md"),
    "URL-encoding": ("path", "legacy%2Fmemory%2Findex.md"),
    "another letter case": ("path", "Legacy/Memory/INDEX.md"),
    "a path split across lines": ("path", "legacy/memory/\n   index.md"),
    "the store's folder alone": ("folder", "legacy/memory/"),
    "a glob": ("glob", "legacy/memory/*.md"),
    "../ and the tail": ("relative tail", "../../memory/index.md"),
    "an id in prose": ("id", "MEM-7"),
}


def test_s3_every_listed_form_is_found_and_printed_as_found():
    for name, (form, cited) in LISTED.items():
        found = safety.citations(f"Read {cited} before a vote.\n", [STORE], ["MEM-7"])
        shown = {"seeoldlegacy/memory/index.md": STORE, "x-MEM-7": "MEM-7"}.get(cited, cited)  # what is before is no part
        assert [(item["form"], item["found"]) for item in found] == [(form, shown)], name


def test_s3_a_form_outside_the_list_is_not_found():
    for cited in ("index.md", "legacy&#47;memory&#47;index.md", "**/*.md", "memory/index.md", "MEM-70"):
        assert safety.citations(f"Read {cited} before a vote.\n", [STORE], ["MEM-7"]) == [], cited


def test_s3_a_glob_followed_by_sentence_punctuation_is_found_without_it():
    record_ = "legacy/memory/decisions/leg-001.md"
    for text in ("The vote rules are in legacy/memory/**/*.md.\n", "See legacy/memory/**/*.md, then vote.\n",
                 "Rules: legacy/memory/**/*.md: read them.\n", "Rules (legacy/memory/**/*.md) first.\n",
                 "Read legacy/memory/**/*.md; then vote.\n", "Read “legacy/memory/**/*.md” first.\n",
                 "Read legacy/memory/**/*.md\n"):
        found = safety.citations(text, [record_], [])
        assert [(item["form"], item["found"]) for item in found] == [("glob", "legacy/memory/**/*.md")], text


def test_s3_a_glob_with_no_literal_first_folder_stays_not_found_before_punctuation():
    for text in ("Read **/*.md.\n", "Read *.md, then vote.\n", "Read **/*: first.\n"):
        assert safety.citations(text, ["legacy/memory/decisions/leg-001.md"], []) == [], text


def test_s3_the_a8_proof_prints_a_rule_files_url_encoded_citation(root):
    write(root, STORE, "# Legacy memory\n")
    write(root, ".windsurfrules", "Before a vote, read legacy%2Fmemory%2Findex.md.\n")
    commit(root, "a store and a rule that cites it, URL-encoded")
    conf = config(paths=(*PATHS, "legacy/**", ".windsurfrules", "governance/**"))
    audited(root, {"path": STORE, "action": "RETIRE", "kind": "memory-store"}, conf=conf)
    stage(root, "A6", conf=conf)
    error = refused("STORE_STILL_CITED", root, "A8", conf=conf)
    assert "'legacy%2Fmemory%2Findex.md'" in error.message and (root / STORE).is_file()


# ---------------------------------------------------------------- F1: instruction and untracked files survive

def test_f1_instruction_files_and_untracked_files_survive_an_adoption_and_its_rollback(root, monkeypatch):
    fixture = Path(__file__).resolve().parents[3] / "tests/unit/adapters/fixtures/programme"
    for rel in ("CLAUDE.md", "AGENTS.md"):
        write(root, rel, (fixture / rel).read_text(encoding="utf-8"))
    write(root, ".claude/settings.json", (fixture / "claude-settings.json").read_text(encoding="utf-8"))
    write(root, ".gitignore", ".gov-runtime/\n*.local\nscratch/\n")
    commit(root, "the programme's own instruction files")
    write(root, "me.local", "untracked, ignored\n")
    write(root, "scratch/a.txt", "an untracked folder\n")
    listed = ["CLAUDE.md", "AGENTS.md", ".claude/settings.json", "me.local", "scratch/a.txt"]
    conf = config(paths=(*PATHS, "CLAUDE.md", "AGENTS.md", ".claude/**"))
    before = digests(root, listed)
    audited(root, *THREE, conf=conf)
    at_move(monkeypatch, 3, project.refuse("GIT_FAILED", "planted"),
            before=lambda where: write(where, "during.txt", "made while the batch ran\n"))
    refused("BATCH_FAILED", root, "A6", conf=conf)
    after = digests(root, listed + ["during.txt"])
    assert {rel: after[rel] for rel in listed} == before, "an instruction or untracked file changed"
    assert (root / "during.txt").read_text() == "made while the batch ran\n"


def test_the_template_gitleaks_file_is_found():
    assert safety.TEMPLATE_GITLEAKS.is_file()


def test_a_commit_that_fails_removes_only_what_it_wrote(root, monkeypatch):
    monkeypatch.setattr(project, "_run", _failing_commit(project._run))
    write(root, "mine.txt", "x")  # the clean-tree check is not run by project.commit itself
    with pytest.raises(GovError):
        project.commit(root, "m", {"new/record.md": "r\n"})
    assert not (root / "new/record.md").exists() and (root / "mine.txt").read_text() == "x"


def _failing_commit(original):
    def run(root, args, ok, data=None):
        if args and args[0] == "commit":
            raise project.refuse("GIT_FAILED", "planted")
        return original(root, args, ok, data)
    return run
