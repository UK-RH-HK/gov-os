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


_EMPTY_HIDDEN = []  # this module's empty hidden folder, made by pytest's own temporary-folder factory


@pytest.fixture(scope="module", autouse=True)
def _no_hidden_questions(tmp_path_factory):
    """An empty hidden folder of this module's own, under pytest's temporary folders (round 3, item 1): never beside
    a run folder a case was handed, which may be one aimed inside this repository to show it refused. A case never
    falls back to the real hidden half, and a --hidden that names no folder is refused (round 2b, item 3)."""
    _EMPTY_HIDDEN[:] = [tmp_path_factory.mktemp("no-hidden-questions")]
    yield
    shutil.rmtree(_EMPTY_HIDDEN.pop())


def _options(folder, mode="read", **more):
    if "hidden" not in more:
        more["hidden"] = _EMPTY_HIDDEN[0]
    argv = ["--folder", str(folder), "--mode", mode, "--large-size", str(SMALL)]
    for key, value in more.items():
        for one in value if isinstance(value, list) else [value]:
            argv += [f"--{key.replace('_', '-')}", str(one)]
    return runner.parse(argv)


@pytest.fixture(autouse=True)
def _removed_after(tmp_path):
    """Round 2, item 4: each case removes what it built (repositories, the stand-in hidden half, its govs), pass or
    fail, and the check that nothing is left runs after every case of this module."""
    yield
    folder = tmp_path
    for child in folder.iterdir():
        shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()
    left = [p for p in folder.rglob("*")]
    assert not left, f"a runner case left {len(left)} paths it built"


@pytest.fixture(scope="module")
def ready_run(tmp_path_factory):
    """A run folder built with a fresh seed, adopted by the stand-in in place, a stand-in hidden half (10 questions
    per repository) and stand-in govs beside it, answering each repository from its own answers."""
    base = tmp_path_factory.mktemp("w2-81-runner")
    folder, tools = base / "run", base / "tools"
    hidden = standin.write_hidden_stand_in(base / "hidden-stand-in")
    sets = questions.sets_in(hidden)
    runner.run(_options(folder, "build", hidden=hidden))
    _, repos = runner._read_back(folder)
    good, bad = {}, {}
    for name, repo in repos.items():
        standin.render(standin.perfect(repo), repo, repo.root, folder / "outputs" / name)
        asked = questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), repo.manifest, repo.root,
                                  "visible") + questions.resolve(sets[name], repo.manifest, repo.root, "hidden")
        good.update(standin.ranking_for(name, asked, "gold"))
        bad.update(standin.ranking_for(name, asked, "forbidden"))
    govs = {"good": standin.write_gov(tools, "gov-good", good),
            "forbidden": standin.write_gov(tools, "gov-forbidden", bad),
            "close-fails": standin.write_gov(tools, "gov-close-fails", good, close_exit=3)}
    yield {"folder": folder, "repos": repos, "govs": govs, "base": base, "hidden": hidden}
    shutil.rmtree(gitlib.outside_this_repository(base))


def _read(ready_run, built=ALL, **more):
    more.setdefault("hidden", ready_run["hidden"])
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
    assert saved["hidden_half"] == "present and asked in 6 of 6 repositories"
    assert all(saved["repositories"][n]["hidden_half"] == {"questions": 10, "asked": 10, "needed": 10,
                                                           "present": True} for n in runner.EXPECTED)
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
                           "--gov", str(ready_run["govs"]["good"]), "--hidden", str(ready_run["hidden"])],
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
                      "removed_in": "{commit:2}"}},
        {"id": "o1", "repository": "python-app", "kind": "orphaned-test", "variant": "rates-module-removed",
         "paths": ["tests/test_quarry_rates.py", "src/{fact:product}/quarry_rates.py"],
         "steps": [{"message": "Quarry rates", "write": {
             "src/{fact:product}/quarry_rates.py": "def quarry_rate():\n    return 3\n",
             "tests/test_quarry_rates.py": "from {fact:product}.quarry_rates import quarry_rate\n\n\n"
                                           "def test_quarry_rate():\n    assert quarry_rate() == 3\n"}},
                   {"message": "Inline the quarry rates", "remove": ["src/{fact:product}/quarry_rates.py"]}],
         "evidence": {"test": "tests/test_quarry_rates.py", "subject": "src/{fact:product}/quarry_rates.py",
                      "definition": "def quarry_rate", "used_as": "from {fact:product}.quarry_rates import quarry_rate",
                      "removed_in": "{commit:2}"}},
        {"id": "l1", "repository": "rust-workspace", "kind": "large-file", "variant": "frame-capture",
         "paths": ["captures/frames-capture.bin"],
         "steps": [{"message": "A frame capture", "write": {"captures/frames-capture.bin": "f" * 6000}}],
         "evidence": {"path": "captures/frames-capture.bin", "size": 6000}}]}), encoding="utf-8")
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
    (folder / "repos" / "python-app" / "tests" / "test_quarry_rates.py").unlink()  # an adoption deleted it
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
    # round 2, item 6: a hidden variant is named by its number and id only, never by its paths, names or texts
    shown = {name: (folder / name).read_text() for name in ("report.json", "report.md", "run.log")}
    for name, text in shown.items():
        for word in ("docs/frames/frame-limits.md", "notes/handover.txt", "front-matter-status", "token-in-notes",
                     "Frame limits", "Handover notes", "Maximum frame: 512", "frame-limits"):
            assert word not in text, f"{name} shows a hidden variant's {word!r}"
    for label in ("hidden variant #1 (f1)", "hidden variant #2 (s1)", "hidden variant #3 (o1)",
                  "hidden variant #4 (l1)"):
        assert label in shown["report.json"] and label in shown["report.md"], label
    # round 2b, item 4: a visible entry's evidence names a hidden variant's file as that variant's file
    for name, text in shown.items():
        for word in ("test_quarry_rates", "quarry_rates.py", "quarry_rate", "rates-module-removed",
                     "frames-capture", "frame-capture"):
            assert word not in text, f"{name} shows a hidden variant's {word!r}"
    visible = next(p for p in report["repositories"]["python-app"]["judgement"]["planted"]
                   if p["id"] == "python-app.orphaned-test.module-removed")
    assert any("hidden variant #3 (o1)'s file" in str(s["record"]) + str(s["said"]) for s in visible["evidence"])
    # round 2b, item 5: no "not measured" line where only a hidden variant would need one
    assert report["repositories"]["rust-workspace"]["judgement"]["not_measured"] == []
    rust_section = shown["report.md"].split("## rust-workspace")[1].split("\n## ")[0]
    assert "Not measured" not in rust_section and "within the budget" not in rust_section
    assert report["repositories"]["legacy-docs"]["judgement"]["not_measured"], "the visible large files' line stays"


def test_the_markdown_report_says_what_the_json_says_is_not_measured(ready_run):
    """Round 2, item 5: the budget clause of the large files, in the markdown report too, in the JSON's words."""
    govs = ready_run["govs"]
    _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], close_ticket="PG-1")
    saved = json.loads((ready_run["folder"] / "report.json").read_text())
    markdown = (ready_run["folder"] / "report.md").read_text()
    said = [item for repo in saved["repositories"].values() for item in (repo["judgement"] or {}).get("not_measured")]
    assert said, "the JSON report names what is not measured"
    for item in said:
        assert item in markdown, f"the markdown report drops: {item}"


# --------------------------------------------------------------------------
# Round 2b (DEC-997): a secret anywhere in the run folder; the measurement half required; a template's error
# --------------------------------------------------------------------------

PLACES = ("outputs/summary.md", "outputs/secret-history.log", "session-notes.md", "run.json",
          "repos/python-app/NOTES.md")


@pytest.mark.parametrize("place", PLACES)
def test_a_secret_written_anywhere_in_the_run_folder_is_mishandled(ready_run, place):
    """Item 2: every file the adopting session can write in the run folder is compared with every held value."""
    folder, govs = ready_run["folder"], ready_run["govs"]
    repo = ready_run["repos"]["secret-history"]
    entry = next(e for e in repo.manifest["planted"] if e["kind"] == "secret")
    held = repo.secrets[0]
    target = folder / place
    before = target.read_bytes() if target.exists() else None
    try:
        if place == "run.json":
            record = json.loads(before)
            target.write_text(held.line(json.dumps({**record, "session_note": "{value}"})))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(held.line("summary of the adoption: found {value}\n"))
        report = _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], close_ticket="PG-1")
    finally:
        if before is None:
            target.unlink()
        else:
            target.write_bytes(before)
    assert report["reasons"] == [f"secret-history: {entry['id']} is MISHANDLED"], report["reasons"]
    judged = next(p for p in report["repositories"]["secret-history"]["judgement"]["planted"]
                  if p["id"] == entry["id"])
    named = [s["record"] for s in judged["evidence"] if s["status"] == judge.MISHANDLED]
    assert any(place in str(r) for r in named), named
    for name in ("report.json", "report.md", "run.log"):
        assert_absent(held, (folder / name).read_text(), f"the runner's {name}")


def test_a_hidden_folder_that_does_not_exist_is_refused(ready_run, tmp_path, capfd):
    """Item 3: a --hidden that names no existing folder is refused (exit 2), in build and in read mode."""
    missing = tmp_path / "no-such-hidden-folder"
    for argv in (["--folder", str(tmp_path / "run"), "--mode", "build", "--large-size", str(SMALL)],
                 ["--folder", str(ready_run["folder"]), "--mode", "read"]):
        assert runner.main(argv + ["--hidden", str(missing)]) == 2
        out, err = capfd.readouterr()
        assert err.startswith("refused: --hidden names no existing folder"), err
        assert str(missing) not in out + err
    assert not (tmp_path / "run" / "repos").exists()


@pytest.mark.parametrize("how", ["no-hidden-questions", "wrong-extension", "nine-questions"])
def test_a_repository_without_its_measurement_half_is_not_ready_naming_it(ready_run, tmp_path, capfd, how):
    """Item 3: a repository whose hidden half yields fewer than 10 hidden questions is not counted present; READY
    needs the half present and asked in every repository; the reports and the command line say so."""
    govs, hidden = ready_run["govs"], tmp_path / "hidden"
    shutil.copytree(ready_run["hidden"], hidden)
    names = list(runner.EXPECTED) if how == "no-hidden-questions" else ["rust-workspace"]
    if how == "no-hidden-questions":
        for path in hidden.glob("*.yaml"):
            path.unlink()
    elif how == "wrong-extension":
        (hidden / "rust-workspace.yaml").rename(hidden / "rust-workspace.yml")
    else:
        data = yaml.safe_load((hidden / "rust-workspace.yaml").read_text())
        data["questions"] = data["questions"][:9]
        (hidden / "rust-workspace.yaml").write_text(yaml.safe_dump(data))
    report = _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], close_ticket="PG-1", hidden=hidden)
    asked = 9 if how == "nine-questions" else 0
    wanted = [f"{n}: the measurement (hidden) half is not present and asked: {asked} hidden questions asked, at "
              f"least 10 needed" for n in names]
    assert report["verdict"] == judge.NOT_READY and report["reasons"] == wanted, report["reasons"]
    saved = json.loads((ready_run["folder"] / "report.json").read_text())
    assert saved["repositories"]["rust-workspace"]["hidden_half"]["present"] is False
    assert saved["hidden_half"] == f"absent in {len(names)} of 6 repositories"
    markdown = (ready_run["folder"] / "report.md").read_text()
    assert all(reason in markdown for reason in wanted) and f"hidden half absent in {len(names)} of 6" in markdown
    code = runner.main(["--folder", str(ready_run["folder"]), "--mode", "read", "--hidden", str(hidden),
                        "--gov", str(govs["good"])])
    out, _ = capfd.readouterr()
    assert code == 1 and f"hidden half: absent in {len(names)} of 6 repositories" in out, out


TEMPLATE_FORMS = {"attribute": "{product.upper}", "missing-attribute": "{product.nothing}", "index": "{product[x]}",
                  "conversion": "{product!z}", "format": "{product:>>9x}", "positional": "{0}",
                  "unmatched": "{product"}


@pytest.mark.parametrize("where", ["question", "forbidden"])
@pytest.mark.parametrize("form", sorted(TEMPLATE_FORMS))
def test_a_hidden_template_with_an_error_is_refused_naming_its_id(ready_run, tmp_path, capfd, form, where):
    """Item 7: any error filling a hidden template is refused as `refused: <id>: <reason>` with exit 2."""
    hidden = tmp_path / "hidden"
    shutil.copytree(ready_run["hidden"], hidden)
    data = yaml.safe_load((hidden / "rust-workspace.yaml").read_text())
    template = TEMPLATE_FORMS[form]
    if where == "question":
        data["questions"][0]["question"] = f"Quartzite question about {template}?"
    else:
        data["questions"][0]["forbidden"] = [f"docs/quartzite/{template}.md"]
    (hidden / "rust-workspace.yaml").write_text(yaml.safe_dump(data))
    code = runner.main(["--folder", str(ready_run["folder"]), "--mode", "read", "--hidden", str(hidden)])
    out, err = capfd.readouterr()
    assert code == 2, (code, out, err)
    assert err.startswith(f"refused: {data['questions'][0]['id']}: "), err
    product = ready_run["repos"]["rust-workspace"].manifest["facts"]["product"]
    for word in ("Quartzite", "quartzite", template, product):
        assert word not in out + err, f"the refusal shows {word!r}"



def test_a_hidden_forbidden_citation_with_a_mistyped_fact_is_refused(ready_run, tmp_path, capfd):
    """Round 3, item 2: one mistyped fact name in a hidden forbidden citation is refused by the command, naming the
    hidden question's id only: it can never silently remove a forbidden citation from the measurement."""
    hidden = tmp_path / "hidden"
    shutil.copytree(ready_run["hidden"], hidden)
    data = yaml.safe_load((hidden / "rust-workspace.yaml").read_text())
    data["questions"][2]["forbidden"] = ["{stael}"]
    (hidden / "rust-workspace.yaml").write_text(yaml.safe_dump(data))
    code = runner.main(["--folder", str(ready_run["folder"]), "--mode", "read", "--hidden", str(hidden),
                        "--gov", str(ready_run["govs"]["good"])])
    out, err = capfd.readouterr()
    assert code == 2, (code, out, err)
    assert err.startswith(f"refused: {data['questions'][2]['id']}: "), err
    assert "stael" not in out + err
