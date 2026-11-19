"""F1, F2 and F3: no real session and no true set; the reader's and graders' prompts untouched; counts only."""

from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

import w2_204_support as K
from w2_204_support import HIDDEN, VISIBLE, W171

TRUE = (str(W171.TRUE_HOME / "gov-os-eval"), str(W171.TRUE_HOME / "gov-os-runs"))
OPEN_LOG = K.ACCEPT / "W2-170" / "w2_170_open_log.py"
# git blob ids at the base bfde928f5 (F2: the comparability does not break)
PINNED = {"src/gov/memaudit/prompts.py": "c3307d843d62dc464ff8eadb9575fd53fc5b6396",
          "src/gov/memaudit/claude.py": "4adfb050dd2cfa96c09ad0ee57706b694c593668",
          "tests/unit/memaudit/test_prompts.py": "df8c5f492c566b7acd2117c9978d762bcb8a6645"}


# -- F1 ----------------------------------------------------------------------------------------------------------------
def _logged(world: K.World, tmp_path, name: str, *args) -> tuple[int, list[str]]:
    """``python3 -m gov.memaudit <args>`` under W2-170's open log: its exit code and every path it opened or named."""
    log = tmp_path / f"{name}.log"
    done = subprocess.run([sys.executable, str(OPEN_LOG), str(log), *map(str, args)], cwd=world.work,
                          capture_output=True, text=True, timeout=300,
                          env=W171.child_env(world.home, {"W171_STATE": str(world.state)}))
    entries = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return done.returncode, [x.split("\t", 1)[1] for x in entries if "\t" in x]


@pytest.mark.parametrize("step, code", [("check", 0), ("brief", 0), ("fresh", 5)])
def test_f1_a_new_step_opens_nothing_under_the_true_home_s_sets_or_runs(world, tmp_path, step, code):
    found, paths = _logged(world, tmp_path, step, step, *world.step_flags(step, HIDDEN))
    assert found == code, f"{step} ended {found}, not {code}"
    assert paths and not [p for p in paths if p.startswith(TRUE)]


def test_f1_no_call_of_a_whole_planted_run_names_the_true_sets_or_runs(stage):
    run = stage("right")
    world = run.world
    assert run["final"].code == 0, run["final"]
    said = json.dumps([run.record["calls"], world.gov_calls(), world.rebuilds(),
                       [call["argv"] for call in world.claude_calls()]])
    assert not [t for t in TRUE if t in said]
    assert str(W171.TRUE_HOME) != str(world.home) and not (world.home / "gov-os-eval").exists()
    assert {call["argv"][0] for call in world.gov_calls()} <= {"retrieve"}, "the fake gov was asked for more than a search"


# -- F2 ----------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("path", sorted(PINNED))
def test_f2_the_prompts_the_model_calls_and_their_test_are_the_base_s_bytes(path):
    done = subprocess.run(["git", "hash-object", str(K.TREE / path)], capture_output=True, text=True, timeout=60)
    assert done.stdout.strip() == PINNED[path], f"{path} is not the base's file"


# -- F3 ----------------------------------------------------------------------------------------------------------------
def _run_files(world: K.World, audit: str) -> list:
    folder = world.run_dir(audit)
    return [folder / name for name in ("FIGURES.json", "ledger.jsonl", "PREFLIGHT.json", "DROPS.json",
                                       "DECLARATION.json", "USED")]


@pytest.mark.parametrize("name", ["right", "misses"])
def test_f3_no_line_of_a_whole_run_holds_a_question_an_answer_or_a_source(stage, name):
    run = stage(name)
    assert run["final"].code == 0, run["final"]
    sources = {K.first_path(doc) for audit in (VISIBLE, HIDDEN) for doc in run.world.docs(audit).values()}
    for label, call in run.calls.items():
        for word in (*K.planted_words(), *sorted(sources - {K.REGISTER_REL})):
            assert word not in call.text, (label, word)


@pytest.mark.parametrize("name", ["right", "misses"])
def test_f3_the_figures_the_ledger_and_the_records_hold_counts_only(stage, name):
    run = stage(name)
    world = run.world
    assert run["final"].code == 0, run["final"]
    for audit in (VISIBLE, HIDDEN):
        for path in _run_files(world, audit):
            assert path.exists(), path.name
            text = path.read_text(encoding="utf-8")
            assert not [w for w in K.planted_words() if w in text], path.name
    assert (world.fresh_dir / "COUNTS.json").is_file()


def test_f3_no_file_outside_the_sets_and_the_run_folders_holds_a_planted_word(stage):
    """Outside each half's set and run folder, the released visible half and the briefs' own folders, nothing holds a
    question, a gold answer, an answer or a note's sentence; the hidden half's words are nowhere but its set and run."""
    world = stage("right").world
    assert stage("right")["final"].code == 0
    own = [world.set_dir(VISIBLE), world.set_dir(HIDDEN), world.run_dir(VISIBLE), world.run_dir(HIDDEN)]
    assert K.files_holding(world.sets, K.planted_words(), skip=own) == []
    assert K.files_holding(world.runs, K.planted_words(), skip=[world.fresh_dir / "visible"]) == []
    assert K.files_holding(world.runs, K.planted_words("h")) == []
    for folder in (world.home, world.work, world.repo):
        assert K.files_holding(folder, K.planted_words()) == []


def test_f3_say_stays_the_only_printer():
    """No module of the memory audit prints but ``say`` (and the ``gov memaudit`` command module's own output)."""
    printer = re.compile(r"\bprint\(|sys\.std(?:out|err)\.write\(")
    found = [str(path.relative_to(K.TREE)) for path in sorted((K.SRC / "gov" / "memaudit").rglob("*.py"))
             if path.name not in ("say.py", "command.py") and printer.search(path.read_text(encoding="utf-8"))]
    assert found == []
