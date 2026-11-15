"""W2-174 F2 and F3: the pass touches nothing of gov brief, the templates or the schemas; it reads and writes only
``.tickets/`` and the answers file, and calls no model or network (README)."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

import w2_174_support as s

FORBIDDEN_IMPORTS = {"socket", "http", "urllib", "requests", "httpx", "anthropic", "openai", "subprocess"}
CODE_SUFFIXES = (".py", ".pyc", ".so", ".pyd")
# L15 (DEC-1188): the pass also reads the kernel's ticket schema shipped with gov (this tree's, never a copy in the repository)
SHIPPED = (s.SCHEMAS.resolve(), (s.REPO / "governance/kernel/schemas").resolve())
GUARDED = ("src/gov/brief/", "template/governance/kernel/templates/", "template/governance/kernel/schemas/")
UNCHANGED = ("src/gov/adopt/stages.py", "tests/acceptance/W2-152/")


# --- F2 -------------------------------------------------------------------------------------------------------------

def _git(*args: str) -> subprocess.CompletedProcess:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(s.REPO), *args], capture_output=True, text=True, timeout=60, env=env)


def _names_changed_since_base() -> list[str]:
    top = _git("rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != s.REPO.resolve():
        pytest.skip(f"{s.REPO} is not the top of a git checkout: the close's diff cannot be taken")
    base = os.environ.get("W2_174_BASE", s.BASE_COMMIT)
    if _git("cat-file", "-e", f"{base}^{{commit}}").returncode != 0:
        pytest.skip(f"the base commit {base} is not in this checkout: the close's diff cannot be taken")
    names = set(_git("diff", "--name-only", base, "HEAD").stdout.split())
    names |= set(_git("diff", "--name-only", base).stdout.split())  # tracked changes not yet committed
    names |= {line[3:].split(" -> ")[-1] for line in _git("status", "--porcelain").stdout.splitlines()}
    return sorted(names)


def test_f2_the_diff_against_the_base_names_no_file_of_gov_brief_the_templates_or_the_schemas():
    names = _names_changed_since_base()
    hits = [name for name in names if name.startswith(GUARDED)]
    assert not hits, f"the diff against the base names files the pass must not change: {hits}"


def test_f2_the_adoption_stages_and_w2_152s_acceptance_folder_are_unchanged():
    names = _names_changed_since_base()
    hits = [name for name in names if name.startswith(UNCHANGED)]
    assert not hits, f"the diff against the base names files that stay as they are (adoption stages, W2-152's cases): {hits}"


# --- F3 -------------------------------------------------------------------------------------------------------------

def _plant(repo) -> None:
    repo.ticket("DAEO-sc01", "W2-931", "open", [s.lacking("The widget has a line [DEC-1].")],
                [s.verified("The widget never crashes [DEC-1].")])
    repo.ticket("DAEO-sc02", "W2-932", "in_progress", [s.verified("Another line [DEC-1].")],
                [s.lacking("Another failure [DEC-1].")])
    repo.file("README.md", "# the adopted project\n")
    repo.file("docs/DECISION_REGISTER.md", "### DEC-1\nsomething decided\n")
    repo.file("src/widget/widget.py", "def widget():\n    return 'name'\n")
    repo.file("governance/project/facts.yaml", "paths: {main: /x}\n")
    repo.file("notes/todo.txt", "TBD\n")
    (repo.outside / "decoy.txt").write_text("a decoy beside the answers file\n", encoding="utf-8")
    (repo.outside / "other-answers.yaml").write_text("DAEO-sc01: {S1: not applied}\n", encoding="utf-8")


def _outside_tickets(repo) -> dict:
    """The tree but for ``.tickets/``: the repository's other files and the answers folder, with their metadata."""
    state = s.snapshot(repo.tmp)
    return {key: value for key, value in state.items() if not key.startswith(f"{repo.root.name}/.tickets")}


def test_f3_a_decoy_outside_tickets_is_byte_identical_after_list_and_apply_cli(repo):
    _plant(repo)
    answers = repo.answers({"DAEO-sc01": {"S1": s.CLAUSE}, "DAEO-sc02": {"F1": s.CLAUSE}})
    before = _outside_tickets(repo)
    tickets_before = sorted(path.name for path in repo.tickets.iterdir())
    s.result_of(repo.verify_list())
    assert _outside_tickets(repo) == before, "--verify-list changed something outside .tickets/"
    changed = s.result_of(repo.verify_apply(answers)).get("changed")
    assert changed == ["DAEO-sc01", "DAEO-sc02"], f"changed is {changed!r}"
    assert _outside_tickets(repo) == before, \
        f"--verify-apply changed something outside .tickets/: {s.changed_entries(before, _outside_tickets(repo))}"
    assert sorted(path.name for path in repo.tickets.iterdir()) == tickets_before, \
        "the apply left a file (a temporary or a backup) in .tickets/ or removed one"


def test_f3_a_decoy_outside_tickets_is_byte_identical_after_list_and_apply_function(repo):
    _plant(repo)
    answers = repo.answers({"DAEO-sc01": {"S1": s.CLAUSE}, "DAEO-sc02": {"F1": s.CLAUSE}})
    before = _outside_tickets(repo)
    module = s.verify_pass()
    module.missing(repo.root)
    assert _outside_tickets(repo) == before
    assert module.apply(repo.root, answers, s.SESSION, s.TODAY) == ["DAEO-sc01", "DAEO-sc02"]
    assert _outside_tickets(repo) == before
    assert sorted(path.name for path in repo.tickets.iterdir()) == ["DAEO-sc01.md", "DAEO-sc02.md"]


def test_f3_the_module_imports_no_network_or_model_package():
    path = s.SRC / "gov/adopt/verify_pass.py"
    assert path.is_file(), "src/gov/adopt/verify_pass.py is missing"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and getattr(node.func, "id", None) == "__import__":
            pytest.fail("verify_pass.py imports by name at run time (__import__): its imports cannot be read")
    assert not imported & FORBIDDEN_IMPORTS, f"verify_pass.py imports {sorted(imported & FORBIDDEN_IMPORTS)}"
    assert "gov.brief.build" in {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} \
        | {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}, \
        "verify_pass.py does not import gov.brief.build (kpi_rows), so its list may disagree with the ready check"


class _Spy:
    """An audit hook that records every ``open`` while switched on; the hook stays installed but inert afterwards."""

    on = False
    events: list[tuple[str, object]] = []
    installed = False

    @classmethod
    def hook(cls, event, args):
        if cls.on and event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            cls.events.append((str(args[1]), args[0]))
        if cls.on and event in ("socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system"):
            cls.events.append((event, args[0] if args else ""))

    @classmethod
    def watch(cls):
        if not cls.installed:
            sys.addaudithook(cls.hook)
            cls.installed = True
        cls.events = []
        cls.on = True

    @classmethod
    def stop(cls) -> list[tuple[str, object]]:
        cls.on = False
        return cls.events


def _stray_opens(events, allowed: list[Path], allowed_folder: Path) -> tuple[list, list]:
    """(opens outside the allowed paths, every file opened inside them); code files Python loads are not counted."""
    stray, inside = [], []
    for mode, raw in events:
        if mode in ("socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system"):
            stray.append((mode, raw))
            continue
        path = Path(os.fsdecode(raw))
        path = (path if path.is_absolute() else Path.cwd() / path).resolve()
        if path.suffix in CODE_SUFFIXES:
            continue
        if path in allowed or allowed_folder in path.parents or any(folder in path.parents for folder in SHIPPED):
            inside.append(path)
        else:
            stray.append((mode, str(path)))
    return stray, inside


def test_f3_list_and_apply_open_nothing_outside_tickets_and_the_answers_file_and_start_no_connection(repo):
    _plant(repo)
    answers = repo.answers({"DAEO-sc01": {"S1": s.CLAUSE}, "DAEO-sc02": {"F1": s.CLAUSE}})
    module = s.verify_pass()
    import gov.brief.build  # noqa: F401  (loaded before the watch, so import-time reads are not counted)
    import yaml  # noqa: F401

    _Spy.watch()
    try:
        listed = module.missing(repo.root)
    finally:
        events = _Spy.stop()
    assert listed, "the fixture lists nothing"
    stray, inside = _stray_opens(events, [], (repo.root / ".tickets").resolve())
    assert not stray, f"list opened {stray} outside {repo.root / '.tickets'}"
    assert inside, "the spy saw no ticket opened by the list: it does not watch the opens the tool makes"

    _Spy.watch()
    try:
        module.apply(repo.root, answers, s.SESSION, s.TODAY)
    finally:
        events = _Spy.stop()
    stray, inside = _stray_opens(events, [answers.resolve()], (repo.root / ".tickets").resolve())
    assert not stray, f"apply opened {stray}: only {repo.root / '.tickets'} and {answers} are allowed"
    assert answers.resolve() in inside, "the spy saw no read of the answers file by the apply"
    assert any((repo.root / ".tickets").resolve() in path.parents for path in inside), "the apply opened no ticket"


def test_f3_a_refusal_opens_nothing_outside_either(repo):
    from gov.cli.errors import GovError

    _plant(repo)
    answers = repo.answers({"DAEO-sc01": {"S1": "TBD"}})
    module = s.verify_pass()
    _Spy.watch()
    try:
        with pytest.raises(GovError):
            module.apply(repo.root, answers, s.SESSION, s.TODAY)
    finally:
        events = _Spy.stop()
    stray, _ = _stray_opens(events, [answers.resolve()], (repo.root / ".tickets").resolve())
    assert not stray, f"a refused apply opened {stray}"
