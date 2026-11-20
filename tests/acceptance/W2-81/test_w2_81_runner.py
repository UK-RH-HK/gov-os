"""The runner: one command, stand-ins for the adoption, ``gov retrieve``, the pinned ``gov queue`` and the reader and
grader sessions (DEC-728, DEC-1221 (1)).

The run folder is built once per module (and per worker) and read again by each case. The stand-in adoption is the
judge's perfect model, written in place in each built repository; the stand-in ``gov`` answers from a known ranking
and exits as told; the stand-in session starter answers as a model would, and no model runs. The hidden half is a
stand-in written in the case's own temporary folder: the real hidden folder is never read.
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
import w2_81_score as score
import w2_81_standin as standin
from gov.memaudit import claude as product_claude
from gov.memaudit import prompts
from w2_81_secret import assert_absent

ALL = set(judge.CAPABILITIES)
RUNNER = Path(runner.__file__)
SMALL = 4096  # the large files' size in these cases
SONNET = "claude-sonnet-5-5"
NO_CLAUDE = "/nonexistent/claude-is-not-installed"  # a session a case forgot to stand in fails loudly, never runs


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
    more.setdefault("claude", NO_CLAUDE)
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
    good, bad, late, golds = {}, {}, {}, {}
    for name, repo in repos.items():
        standin.render(standin.perfect(repo), repo, repo.root, folder / "outputs" / name)
        asked = questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), repo.manifest, repo.root,
                                  "visible") + questions.resolve(sets[name], repo.manifest, repo.root, "hidden")
        good.update(standin.ranking_for(name, asked, "gold"))
        bad.update(standin.ranking_for(name, asked, "forbidden"))
        late.update(standin.ranking_for(name, asked, "late"))
        for q in asked:  # two repositories may ask one text: the reader cites every gold source of that text
            golds.setdefault(q.question, [])
            golds[q.question] += [(p, line) for p, line, _ in q.sources if (p, line) not in golds[q.question]]
    govs = {"good": standin.write_gov(tools, "gov-good", good),
            "forbidden": standin.write_gov(tools, "gov-forbidden", bad),
            "late": standin.write_gov(tools, "gov-late", late),
            "queue-fails": standin.write_gov(tools, "gov-queue-fails", good, queue_exit=3),
            "queue-refused": standin.write_gov(tools, "gov-queue-refused", good, queue_exit=1)}
    yield {"folder": folder, "repos": repos, "govs": govs, "base": base, "hidden": hidden, "golds": golds,
           "claude": standin.write_claude(tools)}
    shutil.rmtree(gitlib.outside_this_repository(base))


def _read(ready_run, built=ALL, session=None, **more):
    """A read of the ready run folder with the model line of a good run (Sonnet adopter, the pinned stand-in gov) and
    a stand-in session starter: the reader cites the first item of the last bundle, the grader says correct."""
    more.setdefault("hidden", ready_run["hidden"])
    more.setdefault("adopter_model", SONNET)
    more.setdefault("pinned_gov", ready_run["govs"]["good"])
    return runner.run(_options(ready_run["folder"], "read", **more), built=built,
                      session=session or standin.Sessions())


def _worked(gov):
    """How many times a stand-in gov was asked for anything but its version."""
    return len([c for c in standin.calls_of(gov) if c != "--version"])


def _flags(ready_run, **more):
    """The command line's flags for a read that gets as far as the sessions: the stand-in model CLI, the model line."""
    flags = {"--adopter-model": SONNET, "--pinned-gov": str(ready_run["govs"]["good"]),
             "--claude": str(ready_run["claude"]), **{k: str(v) for k, v in more.items()}}
    return [x for pair in flags.items() for x in pair]


def test_a_build_records_a_fresh_seed_and_keeps_the_manifests_outside_the_repositories(ready_run):
    record = json.loads((ready_run["folder"] / "run.json").read_text())
    assert isinstance(record["seed"], int) and record["large_size"] == SMALL
    for name, repo in ready_run["repos"].items():
        assert repo.manifest["seed"] == record["seed"], name
        assert not gitlib._inside(repo.manifest_path, repo.root), name
        assert repo.root == ready_run["folder"] / "repos" / name


def test_all_handled_and_every_end_to_end_figure_at_the_bar_is_ready(ready_run):
    """DEC-1221 (1): READY with everything handled, each repository's questions judged right end to end at 95 or
    more, the model line stated, and each ticket landed with ``gov queue`` at exit 0."""
    govs = ready_run["govs"]
    calls = len(standin.calls_of(govs["good"]))
    report = _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], queue_ticket="PG-1")
    assert report["verdict"] == judge.READY, report["reasons"]
    saved = json.loads((ready_run["folder"] / "report.json").read_text())
    assert saved["verdict"] == judge.READY and saved["seed"] == report["seed"]
    assert saved["hidden_half"] == "present and asked in 6 of 6 repositories"
    assert saved["bar"] == 95.0 and "floor" not in json.dumps(saved)
    assert saved["models"] == {"adopter": SONNET, "reader": SONNET, "grader": SONNET} and saved["release"] == "0.1.4"
    assert all(saved["repositories"][n]["hidden_half"] == {"questions": 10, "asked": 10, "needed": 10,
                                                           "present": True} for n in runner.EXPECTED)
    for name in runner.EXPECTED:
        repo = saved["repositories"][name]
        figures = repo["figures"]
        assert figures["end_to_end"] == 100.0 and figures["right"] == figures["questions"] >= 10, name
        assert figures["bar"] == 95.0 and figures["met"] is True
        assert figures["diagnostic"] == {"hit_at_5": 100.0, "stacked_share": 100.0}, "diagnostic, beside the figure"
        assert "hit_at_5" not in figures and "stacked_share" not in figures
        assert all(q["right"] for q in figures["per_question"]) and all(q["id"] for q in figures["per_question"])
        assert repo["queue"] == {"run": True, "ticket": "PG-1", "exit": 0} and "close" not in repo
        assert all(p["status"] == judge.FOUND and p["evidence"] for p in repo["judgement"]["planted"]), name
        assert all(c["status"] == judge.CLEAN for c in repo["judgement"]["controls"]), name
        assert repo["not_built"] == []
    markdown = (ready_run["folder"] / "report.md").read_text()
    assert markdown.startswith("# W2-81 proving ground: READY") and f"Seed {report['seed']}" in markdown
    assert f"adopter {SONNET}, reader {SONNET}, grader {SONNET}" in markdown and "Release 0.1.4" in markdown
    section = markdown.split("## python-app")[1].split("\n## ")[0]
    assert "End-to-end figure 100.0 (bar 95" in section and "diagnostic, never a bar" in section
    assert section.index("End-to-end figure") < section.index("hit@5"), "the figure first, the diagnostics beside it"
    assert "gov close" not in markdown and "gov queue:" in section
    seen = standin.calls_of(govs["good"])[calls:]
    assert "queue" in seen and "close" not in seen, "the landing is gov queue; gov close is never run"


def test_the_models_block_and_the_release_version_are_in_the_run_record(ready_run, tmp_path):
    """S-RERUN's record: the adopter, reader and grader model ids, and the release read from the pinned install."""
    pinned = standin.write_gov(tmp_path / "tools", "gov-pinned", {}, version="0.2.7")
    _read(ready_run, gov=ready_run["govs"]["good"], pinned_gov=pinned)
    record = json.loads((ready_run["folder"] / "run.json").read_text())
    assert record["models"] == {"adopter": SONNET, "reader": SONNET, "grader": SONNET}
    assert record["release"] == "0.2.7", "read from the pinned install, never a fixed number"
    assert score.check_models(record) == []
    assert isinstance(record["seed"], int) and record["heads"], "the build's own record is kept"
    report = json.loads((ready_run["folder"] / "report.json").read_text())
    assert report["release"] == "0.2.7"
    other = _read(ready_run, gov=ready_run["govs"]["good"], adopter_model=SONNET,
                  pinned_gov=standin.write_gov(tmp_path / "tools", "gov-pinned-b", {}, version="0.1.9"))
    assert other["release"] == "0.1.9"


@pytest.mark.parametrize("failure, said", [
    ("queue-fails", "gov queue PG-1 ended with exit 3"),
    ("queue-refused", "gov queue PG-1 ended with exit 1"),
    ("queue-not-run", "gov queue was not run"),
    ("forbidden-first", "below its bar of 95"),
    ("no-retrieval", "the end-to-end figure is missing"),
    ("wrong-grade", "below its bar of 95"),
    ("reader-error", "below its bar of 95"),
    ("second-search-asked", "below its bar of 95"),
    ("todays-code", "is NOT_BUILT"),
])
def test_each_failure_is_not_ready_naming_it(ready_run, failure, said):
    govs = ready_run["govs"]
    more = {"pinned_gov": govs["good"], "queue_ticket": "PG-1"}  # retrieval only where the case is about it
    built, session = ALL, standin.Sessions()
    if failure == "queue-fails":
        more["pinned_gov"] = govs["queue-fails"]
    elif failure == "queue-refused":
        more["pinned_gov"] = govs["queue-refused"]
    elif failure == "queue-not-run":
        del more["queue_ticket"]
    elif failure == "forbidden-first":
        more["gov"] = govs["forbidden"]
    elif failure == "todays-code":
        built = None
    if failure in ("wrong-grade", "reader-error", "second-search-asked"):
        more["gov"] = govs["good"]
        session = {"wrong-grade": standin.Sessions(grade={"*": "wrong"}), "reader-error": standin.Sessions("error"),
                   "second-search-asked": standin.Sessions("search-twice")}[failure]
    elif failure in ("queue-fails", "queue-refused", "queue-not-run", "todays-code"):
        more["gov"] = govs["good"]
    report = _read(ready_run, built=built, session=session, **more)
    assert report["verdict"] == judge.NOT_READY
    assert any(said in reason for reason in report["reasons"]), report["reasons"]


def test_hit_at_5_of_zero_beside_a_figure_at_the_bar_is_ready(ready_run):
    """EMERGENCY-2 5.2: five fillers rank before every gold source (hit@5 is 0); the reader cites the gold source it
    finds in the whole bundle, the grader says correct: the end-to-end figure is 100 and READY stands."""
    govs = ready_run["govs"]
    session = standin.Sessions("cite-gold", gold=ready_run["golds"])
    report = _read(ready_run, gov=govs["late"], pinned_gov=govs["late"], queue_ticket="PG-1", session=session)
    assert report["verdict"] == judge.READY, report["reasons"]
    for name in runner.EXPECTED:
        figures = report["repositories"][name]["figures"]
        assert figures["diagnostic"]["hit_at_5"] == 0.0 and figures["diagnostic"]["stacked_share"] == 100.0, name
        assert figures["end_to_end"] == 100.0


def test_a_retrieval_that_gives_no_gold_source_does_not_by_itself_make_the_run_not_ready(ready_run, tmp_path):
    """hit@5 and the stacked share are both 0 (retrieval answers nothing), the reader's answer still cites the gold
    source right and the grader says correct: judged right end to end, so READY: the diagnostics carry no line."""
    none = standin.write_gov(tmp_path / "tools", "gov-none", {})
    session = standin.Sessions("cite-gold", gold=ready_run["golds"])
    report = _read(ready_run, gov=none, pinned_gov=none, queue_ticket="PG-1", session=session)
    assert report["verdict"] == judge.READY, report["reasons"]
    for name in runner.EXPECTED:
        figures = report["repositories"][name]["figures"]
        assert figures["diagnostic"] == {"hit_at_5": 0.0, "stacked_share": 0.0} and figures["end_to_end"] == 100.0


def test_a_forbidden_citation_drops_exactly_one_question_of_its_repository(ready_run):
    """The reader answers right (the grader says correct) but also cites the planted stale spec: that question is
    wrong, the repository's figure drops by exactly it, and the other repositories are untouched."""
    govs = ready_run["govs"]
    repo = ready_run["repos"]["python-app"]
    asked = questions.resolve(questions.load_set(questions.VISIBLE / "python-app.yaml"), repo.manifest, repo.root,
                              "visible") + questions.resolve(questions.sets_in(ready_run["hidden"])["python-app"],
                                                             repo.manifest, repo.root, "hidden")
    target = next(q for q in asked if q.forbidden)
    session = standin.Sessions(forbid={target.question: target.forbidden[0]})
    report = _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], queue_ticket="PG-1", session=session)
    figures = report["repositories"]["python-app"]["figures"]
    n = len(asked)
    assert figures["questions"] == n and figures["right"] == n - 1
    assert figures["end_to_end"] == 100.0 * (n - 1) / n
    wrong = [q for q in figures["per_question"] if not q["right"]]
    assert [q["id"] for q in wrong] == [target.id] and wrong[0]["reason"] == "forbidden citation"
    assert all(report["repositories"][o]["figures"]["end_to_end"] == 100.0 for o in runner.EXPECTED if o != "python-app")
    assert (report["verdict"] == judge.READY) == (figures["end_to_end"] >= 95.0), report["reasons"]
    if figures["end_to_end"] < 95.0:
        assert f"python-app: the end-to-end figure is {figures['end_to_end']:g}, below its bar of 95" in report["reasons"]


def test_the_reader_and_the_grader_are_started_on_sonnet_with_the_products_flags(ready_run):
    """Every session of the run is claude-sonnet-5-5: the argv of each reader and grader session names the model,
    and is the product's ``claude -p`` argv with the model forced."""
    session = standin.Sessions()
    gov = ready_run["govs"]["good"]
    report = _read(ready_run, gov=gov, claude="/some/where/claude", session=session)
    asked = sum(r["figures"]["questions"] for r in report["repositories"].values())
    assert session.roles().count("reader") == asked and session.roles().count("grader") == asked
    assert "other" not in session.roles()
    for role, system, schema in (("reader", prompts.READER_SYS, prompts.READER_SCHEMA),
                                 ("grader", prompts.GRADER_SYS, prompts.GRADER_SCHEMA)):
        for argv in session.argvs(role):
            assert argv[argv.index("--model") + 1] == "claude-sonnet-5-5", argv[:8]
            budget = float(argv[argv.index("--max-budget-usd") + 1])
            assert argv == product_claude.argv_of("/some/where/claude", "claude-sonnet-5-5", system, schema, budget)
    every = [a for _, argv in session.calls for a in argv]
    assert not [a for a in every if a.startswith("claude-") and a != "claude-sonnet-5-5"]
    assert "opus" not in " ".join(every).lower().replace(prompts.READER_SYS.lower(), "").replace(
        prompts.GRADER_SYS.lower(), "")


def test_the_reader_searches_once_more_and_a_second_search_is_not_an_answer(ready_run):
    """The reader may ask for one more search in its own words (a second ``gov retrieve``), then must answer."""
    gov = ready_run["govs"]["good"]
    once = standin.Sessions("search-first")
    before = standin.calls_of(gov).count("retrieve")
    report = _read(ready_run, gov=gov, pinned_gov=gov, queue_ticket="PG-1", session=once)
    asked = sum(r["figures"]["questions"] for r in report["repositories"].values())
    assert report["verdict"] == judge.READY, report["reasons"]
    assert once.roles().count("reader") == 2 * asked and once.roles().count("grader") == asked
    assert standin.calls_of(gov).count("retrieve") - before == 2 * asked, "one more search a question, no more"
    twice = standin.Sessions("search-twice")
    report = _read(ready_run, gov=gov, pinned_gov=gov, queue_ticket="PG-1", session=twice)
    assert twice.roles().count("reader") == 2 * asked, "a second search is never run: the reader's cap is two attempts"
    assert all(r["figures"]["end_to_end"] == 0.0 for r in report["repositories"].values())


def test_a_run_record_without_the_sonnet_model_line_is_refused_before_any_session(ready_run, tmp_path, capfd):
    """No model line, an adopter or another session on another model, or no release read: refused (exit 2) before
    any stage, search or session runs; the run record keeps no model line it was refused on."""
    gov, folder = ready_run["govs"]["good"], ready_run["folder"]
    record = (folder / "run.json").read_text()
    bare = {k: v for k, v in json.loads(record).items() if k not in ("models", "release")}  # as a build leaves it
    garbled = standin.write_gov(tmp_path / "tools", "gov-garbled", {}, version="unknown")
    for how in ("no-adopter-model", "adopter-opus", "adopter-haiku", "no-pinned-gov", "version-unreadable",
                "record-reader-opus", "record-grader-opus", "record-models-not-a-mapping"):
        session = standin.Sessions()
        calls = _worked(gov)
        more = {"gov": gov, "pinned_gov": gov, "adopter_model": SONNET}
        (folder / "run.json").write_text(json.dumps(bare))
        if how == "no-adopter-model":
            del more["adopter_model"]
        elif how.startswith("adopter"):
            more["adopter_model"] = "claude-" + how.split("-")[1] + "-5-5"
        elif how == "no-pinned-gov":
            del more["pinned_gov"]
        elif how == "version-unreadable":
            more["pinned_gov"] = garbled
        else:
            data = dict(bare)
            data["models"] = ["claude-sonnet-5-5"] if how.endswith("mapping") else {
                "adopter": SONNET, "reader": SONNET, "grader": SONNET, how.split("-")[1]: "claude-opus-5-5"}
            (folder / "run.json").write_text(json.dumps(data))
        try:
            with pytest.raises(runner.RunnerError) as refused:
                runner.run(_options(folder, "read", hidden=ready_run["hidden"], **more), built=ALL, session=session)
            assert str(refused.value).startswith("the run record's model line: "), (how, str(refused.value))
            assert not session.calls and _worked(gov) == calls, f"{how}: a session or a search ran"
        finally:
            (folder / "run.json").write_text(record)
    # through the command: refused, exit 2, on standard error alone; the model CLI named is never started
    (folder / "run.json").write_text(json.dumps(bare))
    try:
        code = runner.main(["--folder", str(folder), "--mode", "read", "--hidden", str(ready_run["hidden"]),
                            "--gov", str(gov), "--pinned-gov", str(gov), "--claude", NO_CLAUDE])
        out, err = capfd.readouterr()
        assert code == 2 and not out and err.startswith("refused: the run record's model line: the model line has "
                                                        "no adopter"), (code, err)
        assert json.loads((folder / "run.json").read_text()) == bare, "a refused run writes no model line"
    finally:
        (folder / "run.json").write_text(record)


def test_the_run_mode_refuses_before_it_builds_when_the_model_line_is_missing(tmp_path):
    gov = standin.write_gov(tmp_path / "tools", "gov", {})
    session = standin.Sessions()
    with pytest.raises(runner.RunnerError) as refused:
        runner.run(_options(tmp_path / "run", "run", seed=11, gov=gov, pinned_gov=gov, adopter_model="claude-opus-5-5"),
                   session=session)
    assert "adopter" in str(refused.value) and not session.calls
    assert not (tmp_path / "run" / "repos").exists(), "nothing was built on a refused model line"
    assert _worked(gov) == 0, "only the version was asked of the pinned gov"


def test_the_report_log_and_output_hold_no_question_answer_or_secret_text(ready_run, capfd):
    """The answer text is in the verdict rows of the run folder alone; the reports, the log and the output hold ids,
    verdicts and the figures."""
    gov = ready_run["govs"]["good"]
    session = standin.Sessions("search-first")
    _read(ready_run, gov=gov, pinned_gov=gov, queue_ticket="PG-1", session=session)
    code = runner.main(["--folder", str(ready_run["folder"]), "--mode", "read", "--hidden", str(ready_run["hidden"]),
                        "--gov", str(gov), *_flags(ready_run)])
    out, err = capfd.readouterr()
    assert code == 1  # today's code: handlings not built
    texts = {name: (ready_run["folder"] / name).read_text() for name in ("report.json", "report.md", "run.log")}
    texts["stdout"], texts["stderr"] = out, err
    asked = []
    for name, repo in ready_run["repos"].items():
        asked += questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), repo.manifest, repo.root,
                                   "visible") + questions.resolve(questions.sets_in(ready_run["hidden"])[name],
                                                                  repo.manifest, repo.root, "hidden")
    for where, text in texts.items():
        for q in asked:
            assert q.question not in text and q.gold_answer not in text, f"{where} shows a question or its answer"
        assert "STAND-IN ANSWER" not in text and "the stand-in grader's reason" not in text, where
    rows = sorted((ready_run["folder"] / "e2e").rglob("*.json"))
    assert len(rows) == len(asked) and {r.stem for r in rows} == {q.id for q in asked}
    row = json.loads(rows[0].read_text())
    assert row["id"] == rows[0].stem and row["grade"] == "correct" and row["reader"]["verdict"] == "answer"
    assert all(isinstance(c, list) and len(c) == 3 for c in row["reader"]["citations"])
    for repo in ready_run["repos"].values():
        for held in repo.secrets:
            for where, text in texts.items():
                assert_absent(held, text, f"the runner's {where}")


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
                                                   "report.json", "report.md", ".home", ".tmp", "e2e"}


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
                           "--gov", str(ready_run["govs"]["good"]), "--hidden", str(ready_run["hidden"]),
                           *_flags(ready_run)], capture_output=True, text=True, env=env)
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
    report = runner.run(_options(tmp_path / "run", "run", seed=11, gov=gov, pinned_gov=gov, adopter_model=SONNET),
                        session=standin.Sessions())
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
    report = runner.run(_options(folder, "read", gov=gov, hidden=hidden, pinned_gov=gov, adopter_model=SONNET),
                        session=standin.Sessions())
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
    _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], queue_ticket="PG-1")
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
        report = _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], queue_ticket="PG-1")
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
    report = _read(ready_run, gov=govs["good"], pinned_gov=govs["good"], queue_ticket="PG-1", hidden=hidden)
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
                        "--gov", str(govs["good"]), *_flags(ready_run)])
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
    code = runner.main(["--folder", str(ready_run["folder"]), "--mode", "read", "--hidden", str(hidden),
                        *_flags(ready_run)])
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
                        "--gov", str(ready_run["govs"]["good"]), *_flags(ready_run)])
    out, err = capfd.readouterr()
    assert code == 2, (code, out, err)
    assert err.startswith(f"refused: {data['questions'][2]['id']}: "), err
    assert "stael" not in out + err


# --------------------------------------------------------------------------
# W2-93 (DEC-1144 (6)): --sets-root <root>, the hidden half found under the evaluation sets' root
# --------------------------------------------------------------------------

REL = runner.HIDDEN_UNDER_SETS_ROOT


def _sets_root(tmp_path, source=None, name="sets"):
    """A stand-in evaluation sets' root in the case's own folder, holding a stand-in hidden half under REL."""
    root = tmp_path / name
    if source is None:
        standin.write_hidden_stand_in(root / REL)
    else:
        shutil.copytree(source, root / REL)
    return root


def _with_sets_root(folder, mode, root, *more):
    return ["--folder", str(folder), "--mode", mode, "--large-size", str(SMALL), "--sets-root", str(root), *more]


def test_the_sets_root_constant_is_the_one_relative_path():
    assert runner.HIDDEN_UNDER_SETS_ROOT == "fixtures/evaluation/adoption-proving-ground/hidden"


def test_a_sets_root_is_found_and_its_hidden_half_read_with_only_the_sets_root_given(ready_run, tmp_path, capfd):
    """The hidden half sits under the root; no --hidden is named; the verdict line says it is present and asked."""
    root = _sets_root(tmp_path, ready_run["hidden"])
    govs = ready_run["govs"]
    code = runner.main(_with_sets_root(ready_run["folder"], "read", root, "--gov", str(govs["good"]),
                                       *_flags(ready_run)))
    out, err = capfd.readouterr()
    assert code == 1 and "hidden half: present and asked in 6 of 6 repositories" in out, (code, out, err)
    saved = json.loads((ready_run["folder"] / "report.json").read_text())
    assert saved["hidden_half"] == "present and asked in 6 of 6 repositories"
    assert all(saved["repositories"][n]["hidden_half"] == {"questions": 10, "asked": 10, "needed": 10,
                                                           "present": True} for n in runner.EXPECTED)
    assert str(root) not in out + err


def test_a_sets_root_is_read_exactly_as_the_hidden_folder_is(ready_run, tmp_path):
    """Same folder, same report: --sets-root and --hidden give one verdict, one list of reasons, one hidden half."""
    govs = ready_run["govs"]
    root = _sets_root(tmp_path, ready_run["hidden"])
    more = {"gov": govs["good"], "pinned_gov": govs["good"], "queue_ticket": "PG-1"}
    direct = _read(ready_run, **more)
    argv = _with_sets_root(ready_run["folder"], "read", root, "--gov", str(govs["good"]), "--pinned-gov",
                           str(govs["good"]), "--queue-ticket", "PG-1", "--adopter-model", SONNET, "--claude", NO_CLAUDE)
    through = runner.run(runner.parse(argv), built=ALL, session=standin.Sessions())
    assert through["verdict"] == direct["verdict"] == judge.READY, (through["reasons"], direct["reasons"])
    assert through["reasons"] == direct["reasons"] and through["hidden_half"] == direct["hidden_half"]
    assert {n: r["hidden_half"] for n, r in through["repositories"].items()} == \
        {n: r["hidden_half"] for n, r in direct["repositories"].items()}


def test_a_sets_root_with_nine_questions_in_one_repository_is_not_ready_naming_it(ready_run, tmp_path):
    """The same refusal as --hidden's: a repository with 9 hidden questions is not counted present."""
    root = _sets_root(tmp_path, ready_run["hidden"])
    data = yaml.safe_load((root / REL / "rust-workspace.yaml").read_text())
    data["questions"] = data["questions"][:9]
    (root / REL / "rust-workspace.yaml").write_text(yaml.safe_dump(data))
    govs = ready_run["govs"]
    report = runner.run(runner.parse(_with_sets_root(ready_run["folder"], "read", root, "--gov", str(govs["good"]),
                                                     "--pinned-gov", str(govs["good"]), "--queue-ticket", "PG-1",
                                                     "--adopter-model", SONNET, "--claude", NO_CLAUDE)),
                        built=ALL, session=standin.Sessions())
    assert report["verdict"] == judge.NOT_READY
    assert report["reasons"] == ["rust-workspace: the measurement (hidden) half is not present and asked: 9 hidden "
                                 "questions asked, at least 10 needed"], report["reasons"]
    assert report["hidden_half"] == "absent in 1 of 6 repositories"


def test_a_build_reads_the_hidden_variants_from_the_sets_root(tmp_path, capfd):
    """Build mode finds the variants under the root too: four hidden variants in the run's record and manifests."""
    root = tmp_path / "sets"
    _hidden_stand_in(root / REL)
    folder = tmp_path / "run"
    code = runner.main(_with_sets_root(folder, "build", root, "--seed", "23"))
    out, err = capfd.readouterr()
    assert code == 0 and out.startswith("BUILT (seed 23)"), (code, out, err)
    record = json.loads((folder / "run.json").read_text())
    assert record["hidden_variants"] == 4
    _, repos = runner._read_back(folder)
    rust = repos["rust-workspace"].manifest["planted"]
    assert any(e.get("hidden") and e["variant"] == "front-matter-status" for e in rust)
    assert HIDDEN_QUESTION not in out + err and str(root) not in out + err


@pytest.mark.parametrize("how", ["empty-root", "no-such-root", "hidden-is-a-file", "another-set-only",
                                 "set-folder-without-hidden"])
@pytest.mark.parametrize("mode", ["build", "run", "read"])
def test_a_sets_root_without_the_hidden_half_exits_2_naming_the_missing_folder(ready_run, tmp_path, capfd, how, mode):
    """A root without the hidden folder is refused in every mode, before anything is built, never by falling back to
    another hidden folder; the refusal names the folder relative to the root, never the root."""
    root = tmp_path / "sets"
    if how == "empty-root":
        root.mkdir()
    elif how == "hidden-is-a-file":
        (root / REL).parent.mkdir(parents=True)
        (root / REL).write_text("not a folder")
    elif how == "another-set-only":
        standin.write_hidden_stand_in(root / "fixtures" / "evaluation" / "examin" / "hidden")
    elif how == "set-folder-without-hidden":
        (root / REL).parent.mkdir(parents=True)
    folder = ready_run["folder"] if mode == "read" else tmp_path / "run"
    listing = sorted(p.name for p in ready_run["folder"].iterdir())
    code = runner.main(_with_sets_root(folder, mode, root))
    out, err = capfd.readouterr()
    assert code == 2, (code, out, err)
    assert err.startswith(f"refused: --sets-root holds no hidden half: {REL}"), err
    assert str(root) not in out + err
    if mode != "read":
        assert not folder.exists(), "something was built before the refusal"
    else:
        assert sorted(p.name for p in folder.iterdir()) == listing


@pytest.mark.parametrize("mode", ["build", "run", "read"])
def test_a_sets_root_with_a_hidden_folder_is_refused(ready_run, tmp_path, capfd, mode):
    """--sets-root and --hidden together are refused (exit 2), in every mode, even when both name a hidden half."""
    root = _sets_root(tmp_path, ready_run["hidden"])
    folder = ready_run["folder"] if mode == "read" else tmp_path / "run"
    code = runner.main(_with_sets_root(folder, mode, root, "--hidden", str(ready_run["hidden"])))
    out, err = capfd.readouterr()
    assert code == 2, (code, out, err)
    assert err.startswith("refused: ") and "--sets-root" in err and "--hidden" in err, err
    assert str(root) not in out + err and str(ready_run["hidden"]) not in out + err
    if mode != "read":
        assert not folder.exists(), "something was built before the refusal"


def test_a_sets_root_whose_variants_file_cannot_be_read_is_refused_naming_the_file(tmp_path, capfd):
    """Read as --hidden is read: a variants file of bad YAML is refused naming the file only (exit 2)."""
    root = _sets_root(tmp_path)
    (root / REL / "variants.yaml").write_text("variants: [unclosed\n  - Zephyr-bad: text", encoding="utf-8")
    code = runner.main(_with_sets_root(tmp_path / "run", "build", root))
    out, err = capfd.readouterr()
    assert code == 2 and err.startswith("refused: the hidden file variants.yaml cannot be read"), (code, out, err)
    assert "Zephyr" not in out + err
