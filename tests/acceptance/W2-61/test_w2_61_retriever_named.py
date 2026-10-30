"""W2-61, KPI success 3, 4 and 7 -- the retrieval the measure measures is named.

A figure means nothing without the retrieval that earned it: the baseline is recorded "with the pinned gov's
version and commit" (KPI 7), and each later run is set beside it (DEC-941, DEC-833 item 3). So every output (text,
JSON and record) states the retrieving gov: the executable's resolved path, its ``<gov> --version`` line, and the
``gov.__file__`` that the interpreter named on the executable's first line imports in the same environment as the
retrieval calls; and the measured root, its HEAD commit, the set, the part and the three budgets.

The retrieval runs as ``<gov> retrieve ... --json`` with the measured root as its working folder and an environment
from which ``PYTHONPATH`` and ``GOV_TICKET`` are removed (so that the pinned gov answers with its own code, not this
worktree's, and no ticket of the measuring session narrows it). The planted gov logs both.

Red now: ``gov.retrieval.measure`` does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402


@pytest.fixture
def world(tmp_path):
    w = s.make_world(tmp_path, commit=False)
    s.standard_questions(w)
    w.commit()
    return w


def _same_path(a, b):
    return a is not None and Path(str(a)).resolve() == Path(str(b)).resolve()


def test_the_json_names_the_retriever_the_root_the_commit_the_set_the_part_and_the_budgets(world):
    document = world.measure(s.SET, "--json").json()
    retriever = document.get("retriever")
    assert isinstance(retriever, dict), f"no retriever: {sorted(document)}"
    assert _same_path(retriever.get("executable"), world.gov), f"executable: {retriever.get('executable')!r}"
    assert str(retriever.get("version", "")).strip() == s.PLANTED_VERSION, f"version: {retriever.get('version')!r}"
    assert _same_path(retriever.get("gov_file"), world.package_file), (
        f"gov_file {retriever.get('gov_file')!r} is not the planted package's {world.package_file}")
    assert _same_path(document.get("root"), world.repo), f"root: {document.get('root')!r}"
    commit = str(document.get("commit") or "")
    assert len(commit) >= 12 and world.head().startswith(commit), f"commit: {commit!r}, HEAD {world.head()}"
    assert document.get("set") == s.SET and document.get("part") == "visible"
    assert document.get("budget") == {"batch_size": 10, "bundle_budget": 6000, "stack_budget": 24000}


def test_the_text_names_the_same(world):
    run = world.measure(s.SET, "--batch-size", 7, "--bundle-budget", 4321, "--stack-budget", 12345)
    assert run.returncode == 0, run.describe()
    out = run.stdout
    for what, value in (("executable", str(world.gov)), ("version", s.PLANTED_VERSION),
                        ("gov.__file__", str(world.package_file)), ("root", str(world.repo)),
                        ("commit", world.head()[:12]), ("set", s.SET), ("part", "visible"), ("batch size", "7"),
                        ("bundle budget", "4321"), ("stack budget", "12345")):
        assert value in out, f"the text output does not name the {what} ({value})\n{run.describe()}"


def test_the_record_names_the_same(world):
    out = world.base / "out"
    run = world.measure(s.SET, "--out", out)
    records = s.records_in(out)
    assert len(records) == 1, f"--out wrote {len(records)} records, not one\n{run.describe()}"
    (path, record), = records.items()
    retriever = record.get("retriever") or {}
    assert _same_path(retriever.get("executable"), world.gov) and _same_path(retriever.get("gov_file"),
                                                                             world.package_file), (
        f"{path.name}: retriever {retriever}")
    assert str(retriever.get("version", "")).strip() == s.PLANTED_VERSION
    assert record.get("set") == s.SET and record.get("part") == "visible"
    assert _same_path(record.get("root"), world.repo)


def test_the_retrieval_runs_in_the_root_without_pythonpath_or_gov_ticket(world):
    world.measure(s.SET, "--json", ticket=s.MEASURED_TICKET, role="orchestrator").json()
    calls = world.all_calls()
    assert any(call["argv"] == ["--version"] for call in calls), "the measure never asked the gov its version"
    retrieves = world.calls()
    assert retrieves, "no retrieve call was made"
    for call in calls:
        assert call["pythonpath"] is False, f"PYTHONPATH reached the planted gov: {call['argv']}"
        assert call["gov_ticket"] is False, f"GOV_TICKET reached the planted gov: {call['argv']}"
    assert {call["cwd"] for call in retrieves} == {str(world.repo)}, (
        f"the retrieval ran elsewhere than the root: {sorted({c['cwd'] for c in retrieves})}")


def test_the_retrieval_runs_in_the_root_from_another_working_folder(world):
    elsewhere = world.base / "elsewhere"
    elsewhere.mkdir()
    document = world.measure(s.SET, "--json", cwd=elsewhere).json()
    assert _same_path(document.get("root"), world.repo)
    assert {call["cwd"] for call in world.calls()} == {str(world.repo)}


def test_the_root_defaults_to_the_current_folder(world):
    document = world.measure(s.SET, "--json", root=False, cwd=world.repo).json()
    assert _same_path(document.get("root"), world.repo), f"root: {document.get('root')!r}"
    assert len(s.questions(document)) == 4


def test_the_gov_defaults_to_the_first_on_path(world):
    document = world.measure(s.SET, "--json", gov=False, path_first=str(world.gov.parent)).json()
    retriever = document.get("retriever") or {}
    assert _same_path(retriever.get("executable"), world.gov), f"executable: {retriever.get('executable')!r}"
    assert _same_path(retriever.get("gov_file"), world.package_file), f"gov_file: {retriever.get('gov_file')!r}"
    assert world.calls(), "the gov on PATH was not asked"
