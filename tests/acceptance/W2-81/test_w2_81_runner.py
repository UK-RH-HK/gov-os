"""The runner: one command, stand-ins for the adoption, ``gov retrieve`` and the pinned ``gov close`` (DEC-728, DEC-953).

The run folder is built once per module (and per worker) and read again by each case. The stand-in adoption is the
judge's perfect model, written in place in each built repository; the stand-in ``gov`` answers from a known ranking
and exits as told. The hidden half is a stand-in written in the case's own temporary folder: the real hidden folder
is never read.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import w2_81_build as build
import w2_81_git as gitlib
import w2_81_judge as judge
import w2_81_questions as questions
import w2_81_run as runner
import w2_81_standin as standin
from w2_81_secret import assert_absent

ALL = set(judge.CAPABILITIES)
RUNNER = Path(runner.__file__)
SMALL = 4096  # the large files' size in these cases


NO_HIDDEN = Path(os.devnull) / "no-hidden-half"  # not a folder: a case never falls back to the real hidden half


def _options(folder, mode="read", **more):
    more.setdefault("hidden", NO_HIDDEN)
    argv = ["--folder", str(folder), "--mode", mode, "--large-size", str(SMALL)]
    for key, value in more.items():
        for one in value if isinstance(value, list) else [value]:
            argv += [f"--{key.replace('_', '-')}", str(one)]
    return runner.parse(argv)


@pytest.fixture(scope="module")
def ready_run(tmp_path_factory):
    """A run folder built with a fresh seed, adopted by the stand-in in place, and stand-in govs beside it."""
    base = tmp_path_factory.mktemp("w2-81-runner")
    folder, tools = base / "run", base / "tools"
    runner.run(_options(folder, "build"))
    _, repos = runner._read_back(folder)
    good, bad = {}, {}
    for name, repo in repos.items():
        standin.render(standin.perfect(repo), repo, repo.root, folder / "outputs" / name)
        asked = questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), repo.manifest, repo.root,
                                  "visible")
        good.update(standin.ranking_for(asked, "gold"))
        bad.update(standin.ranking_for(asked, "forbidden"))
    govs = {"good": standin.write_gov(tools, "gov-good", good),
            "forbidden": standin.write_gov(tools, "gov-forbidden", bad),
            "close-fails": standin.write_gov(tools, "gov-close-fails", good, close_exit=3)}
    yield {"folder": folder, "repos": repos, "govs": govs, "base": base}
    shutil.rmtree(gitlib.outside_this_repository(base))


def _read(ready_run, built=ALL, **more):
    options = _options(ready_run["folder"], "read", **more)
    return runner.run(options, built=built)


def test_a_build_records_a_fresh_seed_and_keeps_the_manifests_outside_the_repositories(ready_run):
    record = json.loads((ready_run["folder"] / "run.json").read_text())
    assert isinstance(record["seed"], int) and record["large_size"] == SMALL
    for name, repo in ready_run["repos"].items():
        assert repo.manifest["seed"] == record["seed"], name
        assert not gitlib._inside(repo.manifest_path, repo.root), name
        assert repo.root == ready_run["folder"] / "repos" / name


def test_all_handled_and_both_figures_met_is_ready(ready_run):
    govs = ready_run["govs"]
    report = _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], close_ticket="PG-1")
    assert report["verdict"] == judge.READY, report["reasons"]
    saved = json.loads((ready_run["folder"] / "report.json").read_text())
    assert saved["verdict"] == judge.READY and saved["seed"] == report["seed"]
    for name in runner.EXPECTED:
        repo = saved["repositories"][name]
        assert repo["figures"]["hit_at_5"] == 100.0 and repo["figures"]["stacked_share"] == 100.0, name
        assert repo["figures"]["questions"] >= 10
        assert repo["close"] == {"run": True, "ticket": "PG-1", "exit": 0}
        assert all(p["status"] == judge.FOUND and p["evidence"] for p in repo["judgement"]["planted"]), name
        assert all(c["status"] == judge.CLEAN for c in repo["judgement"]["controls"]), name
        assert repo["not_built"] == []
    markdown = (ready_run["folder"] / "report.md").read_text()
    assert markdown.startswith("# W2-81 proving ground: READY") and f"Seed {report['seed']}" in markdown


@pytest.mark.parametrize("failure, said", [
    ("close-fails", "gov close PG-1 ended with exit 3"),
    ("close-not-run", "gov close was not run"),
    ("forbidden-first", "below its floor of 85"),
    ("no-retrieval", "the figure hit_at_5 is missing"),
    ("todays-code", "is NOT_BUILT"),
])
def test_each_failure_is_not_ready_naming_it(ready_run, failure, said):
    govs = ready_run["govs"]
    more = {"pinned_gov": govs["good"], "close_ticket": "PG-1"}  # retrieval only where the case is about it
    built = ALL
    if failure == "close-fails":
        more["pinned_gov"] = govs["close-fails"]
    elif failure == "close-not-run":
        del more["close_ticket"]
    elif failure == "forbidden-first":
        more["gov"] = govs["forbidden"]
    elif failure == "todays-code":
        built = None
    report = _read(ready_run, built=built, **more)
    assert report["verdict"] == judge.NOT_READY
    assert any(said in reason for reason in report["reasons"]), report["reasons"]


def test_the_run_writes_only_in_its_folder(ready_run):
    base, folder = ready_run["base"], ready_run["folder"]
    around = sorted(p.name for p in base.parent.iterdir())
    listing = sorted(p.name for p in base.iterdir())
    suite, artefacts = gitlib.porcelain_here(str(RUNNER.parent)), gitlib.w2_81_artefacts(gitlib.porcelain_here())
    _read(ready_run, gov=ready_run["govs"]["good"])
    assert sorted(p.name for p in base.parent.iterdir()) == around
    assert sorted(p.name for p in base.iterdir()) == listing, "the run wrote beside its folder"
    assert gitlib.porcelain_here(str(RUNNER.parent)) == suite
    assert gitlib.w2_81_artefacts(gitlib.porcelain_here()) == artefacts
    assert {p.name for p in folder.iterdir()} <= {"repos", "manifests", "outputs", "run.json", "run.log",
                                                   "report.json", "report.md", ".home", ".tmp"}


def test_a_folder_inside_this_repository_or_another_work_tree_or_not_empty_is_refused(tmp_path):
    inside = gitlib.REPO_ROOT / "tests" / "acceptance" / "W2-81" / "w2-81-run"
    with pytest.raises(gitlib.InsideThisRepository):
        runner.run(_options(inside, "build"))
    assert not inside.exists()
    tree = tmp_path / "someone-elses-tree"
    tree.mkdir()
    gitlib.run_git(tree, "init", "-q")
    with pytest.raises(runner.RunnerError):
        runner.run(_options(tree / "run", "build"))
    assert not (tree / "run").exists()
    full = tmp_path / "full"
    full.mkdir()
    (full / "something").write_text("x")
    with pytest.raises(runner.RunnerError):
        runner.run(_options(full, "build"))


def test_the_command_prints_the_verdict_and_never_a_secret(ready_run):
    env = {**os.environ, "PYTHONPATH": str(gitlib.REPO_ROOT / "src")}
    env.pop("GOV_DEV" + "_TIERS", None)
    done = subprocess.run([sys.executable, str(RUNNER), "--folder", str(ready_run["folder"]), "--mode", "read",
                           "--gov", str(ready_run["govs"]["good"]), "--hidden", str(NO_HIDDEN)],
                          capture_output=True, text=True, env=env)
    assert done.returncode == 1 and done.stdout.startswith("NOT_READY (seed "), (done.returncode, done.stdout)
    refused = subprocess.run([sys.executable, str(RUNNER), "--folder", str(RUNNER.parent / "w2-81-run"),
                              "--mode", "build"], capture_output=True, text=True, env=env)
    assert refused.returncode == 2 and "refused" in refused.stderr
    folder = ready_run["folder"]
    for repo in ready_run["repos"].values():
        for held in repo.secrets:
            for name in ("report.json", "report.md", "run.log", "run.json"):
                assert_absent(held, (folder / name).read_text(), f"the runner's {name}")
            for text, where in ((done.stdout, "standard output"), (done.stderr, "standard error")):
                assert_absent(held, text, f"the command's {where}")
    assert any(r.secrets for r in ready_run["repos"].values())


def test_run_mode_runs_the_stages_and_names_a_failing_one(tmp_path):
    gov = standin.write_gov(tmp_path / "tools", "gov-adopt-fails", {}, adopt_exit=5)
    report = runner.run(_options(tmp_path / "run", "run", seed=11, gov=gov))
    assert report["verdict"] == judge.NOT_READY
    assert all(r["stages_run"] == [{"stage": "A0", "run": True, "exit": 5}] for r in report["repositories"].values())
    assert "python-app: gov adopt --lite --stage A0 ended with exit 5" in report["reasons"]


HIDDEN_QUESTION = "Zephyr-hidden question: which quiet harbour keeps the frame?"
HIDDEN_ANSWER = "Zephyr-hidden answer: the quiet harbour"


def _hidden_stand_in(folder):
    """A stand-in hidden half in the case's own folder: one question set and two variants the builders do not make."""
    folder.mkdir(parents=True)
    (folder / "rust-workspace.yaml").write_text(yaml.safe_dump({
        "form": questions.FORM, "repository": "rust-workspace", "questions": [
            {"id": "rust-workspace-h01", "category": "which-spec-governs", "question": HIDDEN_QUESTION,
             "gold_answer": HIDDEN_ANSWER, "sources": [{"path": "{governing}", "holds": "{spec_line}"}],
             "forbidden": ["{stale}", "docs/frames/frame-limits.md"]}]}), encoding="utf-8")
    (folder / "variants.yaml").write_text(yaml.safe_dump({"variants": [
        {"id": "f1", "repository": "rust-workspace", "kind": "stale-spec", "variant": "front-matter-status",
         "paths": ["docs/frames/frame-limits.md", "{fact:governing}"],
         "steps": [{"message": "Frame limits, reviewed", "write": {
             "docs/frames/frame-limits.md": "---\nstatus: current\nreviewed: 2026-10-01\n---\n# Frame limits\n\n"
                                            "- Maximum frame: 512 bytes\n"}}],
         "evidence": {"stale": "docs/frames/frame-limits.md", "governing": "{fact:governing}",
                      "code": "{fact:lib_a}", "status_line": "status: current", "review_line": "reviewed: 2026-10-01",
                      "reviewed": "2026-10-01", "claim_line": "- Maximum frame: 512 bytes",
                      "governing_line": "{fact:spec_line}", "code_line": "{fact:frame_code}", "names": "frame"}},
        {"id": "s1", "repository": "legacy-docs", "kind": "secret", "variant": "token-in-notes",
         "paths": ["notes/handover.txt"],
         "steps": [{"message": "Handover notes", "write": {"notes/handover.txt": "token: {value}\n"}},
                   {"message": "Handover notes, without the token", "write": {"notes/handover.txt": "token: ask\n"}}],
         "evidence": {"path": "notes/handover.txt", "form": "forge-token", "added_in": "{commit:1}",
                      "removed_in": "{commit:2}"}}]}), encoding="utf-8")
    return folder


def test_the_hidden_half_is_read_from_the_folder_given_and_never_shown(tmp_path, capfd):
    hidden = _hidden_stand_in(tmp_path / "hidden-stand-in")
    folder = tmp_path / "run"
    runner.run(_options(folder, "build", seed=23, hidden=hidden))
    _, repos = runner._read_back(folder)
    rust, legacy = repos["rust-workspace"].manifest, repos["legacy-docs"].manifest
    assert any(e.get("hidden") and e["variant"] == "front-matter-status" for e in rust["planted"])
    secret = next(e for e in legacy["planted"] if e["kind"] == "secret")
    assert secret["evidence"]["rule"] == "github-pat" and len(secret["evidence"]["added_in"]) == 12
    assert repos["legacy-docs"].secrets, "the variant's secret is held in memory"
    gov = standin.write_gov(tmp_path / "tools", "gov", {})
    report = runner.run(_options(folder, "read", gov=gov, hidden=hidden))
    ids = [q["id"] for q in report["repositories"]["rust-workspace"]["figures"]["per_question"]]
    assert "rust-workspace-h01" in ids
    out, err = capfd.readouterr()
    texts = [out, err]
    for path in folder.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            texts.append(path.read_bytes().decode("utf-8", "replace"))
    for text in texts:
        assert HIDDEN_QUESTION not in text and HIDDEN_ANSWER not in text, "a hidden question or answer was shown"
    for held in repos["legacy-docs"].secrets:
        for name in ("report.json", "report.md", "run.log"):
            assert_absent(held, (folder / name).read_text(), f"the runner's {name}")
