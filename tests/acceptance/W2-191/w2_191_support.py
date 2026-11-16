"""Planted projects and readers for W2-191's acceptance tests (the test map accepts any project-relative target).

Every project is a temporary git repository built from nothing: a ticket, a test map, a few suites (some under
``tests/``, some not), and commits. Nothing is written in the tree the tests run in; git runs with no system or user
configuration (every call pinned). The schema read is the tree's own, as ``gov.close.select.load_map`` reads it where
the project has none.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

from gov.close import select

TREE = Path(__file__).resolve().parents[3]
SCHEMA_PATH = TREE / "template" / "governance" / "kernel" / "schemas" / "test-map.schema.json"

TICKET, WBS = "T-0001", "W-1"
PASS = "def test_ok():\n    assert True\n"

# The suites of the planted project, outside tests/ and under it.
SCRIPTS_SUITE = "governance/scripts/tests"
SCRIPTS_RECORDS = "governance/scripts/tests/test_records.py"
SCRIPTS_RECORDS_NODE = f"{SCRIPTS_RECORDS}::test_reads"
PRODUCT_FILE = "product/tests/test_a.py"
PRODUCT_NODE = f"{PRODUCT_FILE}::test_case"
COUPLED_INPUT = "governance/scripts/rules.txt"  # not Python, so no import places it: only a coupling can


def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def schema_errors(test_map: dict) -> list[str]:
    """What the tree's test-map schema says of ``test_map``: one message per error, none where it validates."""
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema())
    return [e.message for e in validator.iter_errors(test_map)]


def map_data(**more) -> dict:
    data = {"version": 1, "shared_core": ["governance/project/test-map.yaml"],
            "record_only": [".tickets/**.md", "docs/**.md", "docs/close/nightly/*.json"]}
    data.update(more)
    return data


def coupling(suites: list[str], paths: list[str] | None = None) -> dict:
    return {"paths": paths or ["governance/scripts/*.txt"], "suites": suites, "why": "the rules file is read as text"}


def with_target(position: str, target: str) -> dict:
    """A valid map whose ``position`` ('record_reading', 'every_close' or 'couplings') holds ``target`` alone."""
    if position == "couplings":
        return map_data(couplings=[coupling([target])])
    return map_data(**{position: [target]})


POSITIONS = ("record_reading", "every_close", "couplings")


class Project:
    """A planted git repository: ``root``, its own git, and the commits of a ticket's work."""

    def __init__(self, tmp_path: Path):
        self.tmp = Path(tmp_path)
        self.root = self.tmp / "project"
        self.root.mkdir(parents=True)
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        env = {"PATH": os.environ["PATH"], "HOME": str(self.tmp), "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull}
        pinned = ["-c", "user.name=A", "-c", "user.email=a@example.invalid", "-c", "commit.gpgsign=false"]
        return subprocess.run(["git", "-C", str(self.root), *pinned, *args], env=env, check=True,
                              capture_output=True, text=True).stdout

    def write(self, files: dict) -> None:
        for rel, text in files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def link(self, rel: str, target: Path) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)

    def commit(self, message: str, *trailers: str, files: dict | None = None) -> str:
        self.write(files or {})
        self.git("add", "-A")
        args = ["commit", "-q", "--allow-empty", "-m", message]
        for trailer in trailers:
            args += ["--trailer", trailer]
        self.git(*args)
        return self.git("rev-parse", "HEAD").strip()

    def work(self, files: dict) -> str:
        """A commit of the ticket's own work."""
        return self.commit("work", f"Task: {TICKET}", "Role: engineer", files=files)

    def green_night(self) -> str:
        """A green nightly record naming the head as it is now (committed as a record): the strict close's base."""
        head = self.git("rev-parse", "HEAD").strip()
        record = {"verdict": "green", "head": head, "secrets_full_scan": True}
        self.commit("night", files={f"docs/close/nightly/NR-20261101T010000Z-{head[:12]}.json": json.dumps(record)})
        return head


def ticket_text() -> str:
    front = {"id": TICKET, "status": "in_progress", "deps": [], "links": [], "created": "2026-11-16T00:00:00Z",
             "type": "task", "priority": 2, "wbs_id": WBS, "profile": "STANDARD", "role": "engineer",
             "allowed_paths": ["governance/scripts/**", f"tests/acceptance/{WBS}/**"],
             "acceptance_tests": {"path": f"tests/acceptance/{WBS}/"},
             "kpis": {"success": ["it works"], "failure": ["it breaks"]}}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n# A ticket\n"


def plant_files(test_map: dict) -> dict:
    return {
        ".gitignore": ".gov-runtime/\n__pycache__/\n*.pyc\n",
        "governance/project/close.yaml": "close: scoped\n",
        "governance/project/test-map.yaml": yaml.safe_dump(test_map, sort_keys=False),
        f".tickets/{TICKET}.md": ticket_text(),
        # suites outside tests/
        SCRIPTS_RECORDS: "def test_reads():\n    assert True\n",
        f"{SCRIPTS_SUITE}/test_scripts.py": "def test_scripts():\n    assert True\n",
        COUPLED_INPUT: "a rule\n",
        PRODUCT_FILE: ("def test_case():\n    assert True\n\n\nclass TestK:\n    def test_m(self):\n"
                       "        assert True\n"),
        "checks/test_c.py": PASS,
        # suites under tests/
        "tests/unit/test_records.py": PASS,
        "tests/unit/test_data_contract.py": PASS,
        "data/t.txt": "t\n",
        "docs/notes.md": "# notes\n",
    }


def plant(tmp_path: Path, test_map: dict, extra: dict | None = None) -> Project:
    """The project at its base: the map, the ticket and the suites, committed with no task, and a folder
    ``outside/`` beside the project (not in it) holding a suite an escaping target could name."""
    project = Project(tmp_path)
    outside = project.tmp / "outside"
    (outside / "suite").mkdir(parents=True)
    (outside / "suite" / "test_o.py").write_text(PASS, encoding="utf-8")
    (outside / "tests").mkdir()
    (outside / "tests" / "test_o2.py").write_text(PASS, encoding="utf-8")
    project.outside = outside
    project.commit("base", files={**plant_files(test_map), **(extra or {})})
    return project


def never_resolved(project: Project) -> tuple[bool, str]:
    """``(True, how)`` where the map's targets are refused, by the loader or by the scoped selection; ``(False,
    what)`` where they were taken: the map loaded and the selection was made."""
    given, why = select.load_map(project.root)
    if given is None:
        assert isinstance(why, str) and why, f"the loader refused the map with no reason: {why!r}"
        return True, f"the loader refused the map ({why})"
    try:
        chosen = select.scoped(project.root, TICKET)
    except select.SelectionRefused as refused:
        assert refused.reason, "the selection refused with no reason"
        return True, f"the selection was refused ({refused.reason})"
    return False, f"the map loaded and the selection took it: suites {chosen['suites']}"


def targets_of(plan: dict) -> dict:
    """``{target: [reasons]}`` of a plan's selected entries."""
    return {entry["target"]: [why["reason"] for why in entry["why"]] for entry in plan["selected"]}


def gov_select(project: Project) -> subprocess.CompletedProcess:
    """``gov close --select <ticket>`` as a process, from this tree's own ``src``."""
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(TREE / "src"), "HOME": str(project.tmp)}
    env.update({k: v for k, v in os.environ.items() if k == "PYTHONUSERBASE"})
    return subprocess.run([sys.executable, "-m", "gov.cli.main", "close", "--select", TICKET, "--root",
                           str(project.root)], capture_output=True, text=True, env=env, cwd=str(project.root))


# --- the close's run line (P-W2-191-1 (b)): what pytest collects with the arguments the close builds ---------------

def relaxed_schema_files() -> dict:
    """A project-local copy of the tree's test-map schema whose ``target`` takes any non-empty text. The loader reads
    the project's own kernel schema before the tree's (``select._schema``), so a planted project with this file
    reads a map naming targets outside ``tests/`` whatever the tree's kernel schema says of them (its new bytes come
    by the owner's approval, not by the ticket's code): the run-line case is then judged on the run line alone."""
    data = schema()
    data.setdefault("$defs", {})["target"] = {"type": "string", "minLength": 1}
    return {SCHEMA_PATH.relative_to(TREE).as_posix(): json.dumps(data, indent=2) + "\n"}


def collected(project: Project, args: list[str]) -> list[str]:
    """The project-relative node ids pytest collects, in the project's folder, from ``args`` (the arguments of the
    close's regression run): ``pytest --collect-only -q`` as a process, importlib import mode so that two files of one
    name (``tests/unit/test_records.py`` and ``governance/scripts/tests/test_records.py``) do not clash in the
    observation. The run must collect without an error."""
    env = {"PATH": "/usr/bin:/bin", "HOME": str(project.tmp), "PYTHONDONTWRITEBYTECODE": "1"}
    env.update({k: v for k, v in os.environ.items() if k == "PYTHONUSERBASE"})
    done = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider",
                           "--import-mode=importlib", "--rootdir", str(project.root), *args],
                          capture_output=True, text=True, env=env, cwd=str(project.root))
    assert done.returncode == 0, f"collecting {args} failed ({done.returncode}):\n{done.stdout}\n{done.stderr}"
    return sorted({line.strip() for line in done.stdout.splitlines()
                   if "::" in line and not line.startswith(("=", "_", "ERROR", "FAILED"))})
