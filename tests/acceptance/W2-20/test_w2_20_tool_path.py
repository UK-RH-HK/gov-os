"""W2-20 fix SP-1 (plan item 1-13, FINDINGS I-6): the product's test runs prepend the registry's pinned Node bin to
``PATH``, read from the tool registry of the tree under test.

The runs: ``gov resources --slot test`` (nested runs too), ``gov accept`` (and so ``gov queue``'s acceptance), the
runs ``gov close`` and ``gov queue`` make (``gov.close.attribution.run_alone``; ``gov.close.command``'s test run,
reached through ``python3 -m gov.close.nightly``) and the nightly's run alone.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import w2_20_tool_path_support as t

EXIT_OF_THE_JOB = 7


# --- gov resources --slot --------------------------------------------------------------------------------------------

def _slot(machine, repo: Path, kind: str = "test", *, tree: Path | None = None, path: str | None = None,
          exit_code: int = 0, env_extra: dict | None = None) -> tuple[int, dict, str]:
    """One heavy job that records its environment: ``(exit code, record, the caller's PATH)``."""
    machine.located(repo)  # the registry is the planted home's before any job is entered
    probe = t.write(machine.scripts, "probe.py", t.PROBE)
    record = machine.marks / "probe.json"
    env = machine.env(**(env_extra or {}))
    if path is not None:
        env["PATH"] = path
    args = ["--slot", kind] + (["--tree", str(tree)] if tree is not None else [])
    argv = machine.argv(repo, *args, json_output=False,
                        passthrough=[sys.executable, str(probe), str(record), str(exit_code)])
    done = subprocess.run(argv, cwd=str(repo), env=env, capture_output=True, text=True, timeout=t.RUN_TIMEOUT_S)
    assert record.is_file(), f"the job did not run: exit {done.returncode}\n{done.stdout}\n{done.stderr}"
    return done.returncode, json.loads(record.read_text()), env["PATH"]


def _assert_prefixed(record: dict, folder: Path, caller_path: str) -> None:
    assert t.first_folder(record) == str(folder), f"{folder} is not first on the run's PATH: {record}"
    assert record["node"] == str(folder / "node"), f"node is not the pinned one: {record}"
    assert record["openspec"] == str(folder / t.TOOL), f"the tool beside node is not found: {record}"
    assert record["path"].endswith(caller_path), f"the caller's PATH is not kept after the prefix: {record}"


@pytest.mark.parametrize("version", [t.PIN, t.OTHER_PIN])
def test_a_test_slot_puts_the_registrys_pinned_node_first_on_path(machine, repo, version):
    folder = t.install_node(t.nvm_bin(machine.home, version), version)
    t.write_registry(repo, [t.entry("node", version)])
    t.stand_in(machine.bin / "node", "v18.20.8")  # a Node of the caller's, first on its PATH
    code, record, caller = _slot(machine, repo)
    assert code == 0
    _assert_prefixed(record, folder, caller)


def test_a_test_slot_takes_the_folder_of_the_node_entrys_path_prefix(machine, repo):
    folder = t.install_node(machine.home / "own-node" / "bin")
    t.install_node(t.nvm_bin(machine.home))  # the nvm folder of the same version: the prefix wins
    line = "PATH=$HOME/own-node/bin:$PATH node --version"
    t.write_registry(repo, [t.entry("node", t.PIN, line)])
    code, record, caller = _slot(machine, repo)
    assert code == 0
    _assert_prefixed(record, folder, caller)


@pytest.mark.parametrize("given", ["--tree", "--root"])
def test_a_test_slot_reads_the_registry_of_the_tree_under_test(machine, repo, given):
    other = machine.repo("other-tree")
    root_folder = t.install_node(t.nvm_bin(machine.home, t.PIN), t.PIN)
    tree_folder = t.install_node(t.nvm_bin(machine.home, t.OTHER_PIN), t.OTHER_PIN)
    t.write_registry(repo, [t.entry("node", t.PIN)])
    t.write_registry(other, [t.entry("node", t.OTHER_PIN)])
    code, record, caller = _slot(machine, repo, tree=other if given == "--tree" else None)
    assert code == 0
    _assert_prefixed(record, tree_folder if given == "--tree" else root_folder, caller)


def test_a_second_node_entry_never_answers_for_node(machine, repo):
    folder = t.install_node(t.nvm_bin(machine.home, t.PIN), t.PIN)
    t.install_node(t.nvm_bin(machine.home, "v22.23.5"), "v22.23.5")
    t.write_registry(repo, [t.entry("node-22.23.5", "v22.23.5"), t.entry("node", t.PIN)])
    code, record, caller = _slot(machine, repo)
    assert code == 0
    _assert_prefixed(record, folder, caller)


def test_a_nested_test_run_gets_the_prefix_too(machine, repo):
    folder = t.install_node(t.nvm_bin(machine.home))
    t.write_registry(repo, [t.entry("node", t.PIN)])
    code, record, caller = _slot(machine, repo, env_extra={"GOV_HEAVY_ADMITTED": "1"})
    assert code == 0
    _assert_prefixed(record, folder, caller)


@pytest.mark.parametrize("kind", ["rebuild", "measure"])
def test_other_slot_kinds_keep_the_callers_path(machine, repo, kind):
    t.install_node(t.nvm_bin(machine.home))
    t.write_registry(repo, [t.entry("node", t.PIN)])
    code, record, caller = _slot(machine, repo, kind)
    assert code == 0 and record["path"] == caller, record
    assert record["openspec"] is None, record


@pytest.mark.parametrize("case", ["no registry", "no node entry", "only a second node entry", "folder without node"])
def test_a_test_slot_without_a_pinned_node_runs_with_the_callers_path(machine, repo, case):
    t.install_node(t.nvm_bin(machine.home, "v22.23.5"), "v22.23.5")
    t.stand_in(t.nvm_bin(machine.home) / t.TOOL, "1.13.2")  # the pinned folder holds a tool and no node
    entries = {"no node entry": [t.entry("uv", "0.12.21", "echo install")],
               "only a second node entry": [t.entry("node-22.23.5", "v22.23.5")],
               "folder without node": [t.entry("node", t.PIN)]}
    if case != "no registry":
        t.write_registry(repo, entries[case])
    code, record, caller = _slot(machine, repo, exit_code=EXIT_OF_THE_JOB)
    assert code == EXIT_OF_THE_JOB, "the job's exit code is not the command's"
    assert record["path"] == caller, record


# --- gov accept (and gov queue's acceptance) -------------------------------------------------------------------------

TICKET = "---\nid: PROJ-sp01\nstatus: in_progress\nwbs_id: W9-sp\nacceptance_tests:\n" \
         "  path: tests/acceptance/W9-sp/\n---\n# A planted ticket\n"
MAP = "# W9-sp\n\n| KPI | Test |\n|---|---|\n| success-1 | `test_tool.py::test_tool` |\n"


def _accept(tmp_path: Path, registry: list[dict] | None, test_text: str):
    home = t.plant_home(tmp_path / "home")
    env = t.caller_env(tmp_path, home)
    root = tmp_path / "project"
    t.write(root, ".tickets/PROJ-sp01.md", TICKET)
    t.write(root, "tests/acceptance/W9-sp/README.md", MAP)
    t.write(root, "tests/acceptance/W9-sp/test_tool.py", test_text)
    if registry is not None:
        t.write_registry(root, registry)
    return t.gov(root, env, "accept", "PROJ-sp01")


def test_gov_accept_runs_the_acceptance_tests_with_the_pinned_node_first(tmp_path):
    folder = t.nvm_bin(tmp_path / "home")
    record = tmp_path / "seen.jsonl"
    t.install_node(folder)
    code, envelope, said = _accept(tmp_path, [t.entry("node", t.PIN)], t.telling_test(record, folder))
    seen = t.records(record)
    assert seen, f"the planted acceptance test did not run\n{said}"
    assert t.first_folder(seen[0]) == str(folder), f"the pinned Node bin is not first on PATH: {seen[0]}"
    assert seen[0]["openspec"] == str(folder / t.TOOL), seen[0]
    assert code == 0 and t.body(envelope).get("outcome") == "pass", said


@pytest.mark.parametrize("registry", [None, [t.entry("node", t.PIN)]], ids=["no registry", "node not installed"])
def test_gov_accept_passes_in_a_project_without_a_node(tmp_path, registry):
    code, envelope, said = _accept(tmp_path, registry, "def test_tool():\n    assert True\n")
    assert code == 0 and t.body(envelope).get("outcome") == "pass", said


# --- the runs gov close and gov queue make ---------------------------------------------------------------------------

def _caller(monkeypatch, tmp_path: Path) -> Path:
    """This process as a caller without Node: a planted ``HOME`` with no slot configuration, no Node folder and no
    ``openspec`` on ``PATH``."""
    home = t.plant_home(tmp_path / "home")
    for name, value in t.caller_env(tmp_path, home).items():
        monkeypatch.setenv(name, value)
    for name in ("GOV_HEAVY_ADMITTED", "GOV_HEAVY_SLOT", "GOV_HEAVY_PRIORITY"):
        monkeypatch.delenv(name, raising=False)
    return home


def test_a_run_alone_of_gov_close_and_gov_queue_gets_the_pinned_node(tmp_path, monkeypatch):
    from gov.close import attribution

    home = _caller(monkeypatch, tmp_path)
    folder = t.install_node(t.nvm_bin(home))
    record = tmp_path / "seen.jsonl"
    clone = tmp_path / "clone"
    t.write_registry(clone, [t.entry("node", t.PIN)])
    t.write(clone, "tests/test_tool.py", t.telling_test(record, folder))
    red = attribution.run_alone(clone, "tests/test_tool.py::test_tool", ["-p", "no:cacheprovider"],
                                tmp_path / "alone", 180, "sp1")
    seen = t.records(record)
    assert seen, f"the run alone did not run the test: {red}"
    assert t.first_folder(seen[0]) == str(folder), f"the pinned Node bin is not first on PATH: {seen[0]}"
    assert red is None, f"the test is red in its run alone ({red}): {seen[0]}"


def test_a_run_alone_without_a_pinned_node_is_not_failed_by_it(tmp_path, monkeypatch):
    from gov.close import attribution

    _caller(monkeypatch, tmp_path)
    clone = tmp_path / "clone"
    t.write(clone, "tests/test_plain.py", "def test_plain():\n    assert True\n")
    red = attribution.run_alone(clone, "tests/test_plain.py::test_plain", ["-p", "no:cacheprovider"],
                                tmp_path / "alone", 180, "sp1")
    assert red is None, f"a project without a registry has its run alone red: {red}"


# Red in its first run, whatever the PATH, so that the nightly runs it again alone; green after that only with the tool.
RED_ONCE = '''

def test_red_once():
    first = not os.path.exists({marker!r})
    if first:
        open({marker!r}, "w").close()
    else:
        with open({alone!r}, "a", encoding="utf-8") as out:
            out.write(json.dumps({{"path": os.environ.get("PATH", ""), "node": shutil.which("node"),
                                   "openspec": shutil.which("openspec")}}) + "\\n")
    assert not first, "red in the first run"
    assert shutil.which("openspec") == {tool!r}
'''


def test_the_nightlys_test_run_and_its_run_alone_get_the_pinned_node(tmp_path):
    home = t.plant_home(tmp_path / "home")
    folder = t.install_node(t.nvm_bin(home))
    record, alone, marker = tmp_path / "seen.jsonl", tmp_path / "alone.jsonl", tmp_path / "first-run-done"
    ollama = t.stand_in(tmp_path / "stand-ins" / "ollama", "none")
    env = t.caller_env(tmp_path, home, OLLAMA_HOST="127.0.0.1:1", GOV_QUERY_OLLAMA_HOST="127.0.0.1:1",
                       GOV_OLLAMA_BIN=str(ollama))
    text = t.telling_test(record, folder) + RED_ONCE.format(marker=str(marker), alone=str(alone),
                                                            tool=str(folder / t.TOOL))
    root = t.git_project(tmp_path / "project", env, {
        ".gitignore": ".gov-runtime/\n", "tests/test_tool.py": text,
        "governance/project/tool-registry.yaml": t.registry_text([t.entry("node", t.PIN)])})
    code, envelope, said = t.gov(root, env, "main", module="gov.close.nightly")
    seen, again = t.records(record), t.records(alone)
    assert seen, f"the nightly ran no planted test\n{said}"
    assert t.first_folder(seen[0]) == str(folder), f"the nightly's test run lacks the pinned Node: {seen[0]}"
    failures = {f["test"].split("::")[-1]: f for f in t.body(envelope).get("failures") or []}
    assert set(failures) == {"test_red_once"}, f"only the test planted red once fails the run\n{said}"
    assert again, f"the nightly did not run the red test alone\n{said}"
    assert t.first_folder(again[0]) == str(folder), f"the nightly's run alone lacks the pinned Node: {again[0]}"
    assert failures["test_red_once"]["alone"] == "passed", f"the run alone is red\n{said}"
