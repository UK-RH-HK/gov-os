"""Planted projects for ``gov queue``'s unit tests (W2-115b): a git repository with a package ``pkg``, one ticket,
its acceptance suite, the test map and the kernel's ticket tool in its place."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
TK = REPO_ROOT / "template" / "governance" / "kernel" / "bin" / "tk"
TICKET, WBS = "T-aaaa", "W-1"
OTHER, OTHER_WBS = "T-bbbb", "W-2"
PASS = "def test_ok():\n    assert True\n"
ENV = {"GIT_AUTHOR_NAME": "A", "GIT_AUTHOR_EMAIL": "a@example.invalid", "GIT_COMMITTER_NAME": "A",
       "GIT_COMMITTER_EMAIL": "a@example.invalid"}


class Repo:
    def __init__(self, root: Path, branch: str = "main"):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q", "-b", branch)
        self.git("config", "user.name", "A")
        self.git("config", "user.email", "a@example.invalid")

    def git(self, *args: str, check: bool = True) -> str:
        env = {"PATH": os.environ["PATH"], "HOME": str(self.root.parent), "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull, **ENV}
        return subprocess.run(["git", "-C", str(self.root), *args], env=env, check=check,
                              capture_output=True, text=True).stdout

    def sha(self, rev: str = "HEAD") -> str:
        return self.git("rev-parse", rev).strip()

    def commit(self, message: str = "work", *trailers: str, files: dict | None = None) -> str:
        for rel, text in (files or {}).items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.git("add", "-A")
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for trailer in trailers:
            args += ["--trailer", trailer]
        self.git(*args)
        return self.sha()

    def branch(self, name: str, planted: dict, *trailers: str, base: str = "main", message: str = "work") -> str:
        start = self.git("symbolic-ref", "--quiet", "--short", "HEAD", check=False).strip() or self.sha()
        self.git("checkout", "-q", "-b", name, base)
        tip = self.commit(message, *trailers, files=planted)
        self.git("checkout", "-q", start)
        return tip

    def status_of(self, ticket: str, rev: str = "HEAD") -> str:
        text = self.git("show", f"{rev}:.tickets/{ticket}.md")
        return str(yaml.safe_load(text.split("---")[1]).get("status"))


def ticket_text(ticket: str = TICKET, wbs: str = WBS, paths: list[str] | None = None, status: str = "open",
                acceptance: str | None = None, **more) -> str:
    front = {"id": ticket, "status": status, "deps": [], "links": [], "created": "2026-11-17T00:00:00Z",
             "type": "task", "priority": 2, "wbs_id": wbs, "role": "engineer",
             "allowed_paths": paths or ["src/pkg/feature.py", f"tests/acceptance/{wbs}/**"],
             "acceptance_tests": {"path": acceptance or f"tests/acceptance/{wbs}/"}}
    front.update(more)
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n# A ticket\n"


def readme_text(wbs: str, case: str) -> str:
    """An acceptance folder's README with the KPI map ``gov accept`` reads: two lines on the suite's one test."""
    return f"# {wbs}\n\n| KPI | tests |\n|---|---|\n| success-1 | `{case}` |\n| failure-1 | `{case}` |\n"


def map_text() -> str:
    data = {"version": 1, "shared_core": ["src/pkg/core.py"], "record_only": [".tickets/**.md", "docs/**.md"],
            "record_reading": [], "every_close": [], "couplings": [], "test_inputs": [],
            "per_test_timeout": 60, "distribution": "load"}
    return yaml.safe_dump(data, sort_keys=False)


def path_map_text(*patterns: str) -> str:
    return yaml.safe_dump({"namespaces": {"all": {"paths": list(patterns)}}})


def files() -> dict:
    return {
        ".gitignore": ".gov-runtime/\n__pycache__/\n*.pyc\n",
        "governance/project/test-map.yaml": map_text(),
        "governance/project/path-map.yaml": path_map_text("**"),
        f".tickets/{TICKET}.md": ticket_text(),
        f".tickets/{OTHER}.md": ticket_text(OTHER, OTHER_WBS, ["src/pkg/gadget.py", f"tests/acceptance/{OTHER_WBS}/**"]),
        "src/pkg/__init__.py": "",
        "src/pkg/feature.py": "def twice(x):\n    return x + x\n",
        "src/pkg/gadget.py": "def gadget():\n    return 1\n",
        "src/pkg/other.py": "def other():\n    return 1\n",
        "src/pkg/lonely.py": "VALUE = 1\n",
        f"tests/acceptance/{WBS}/test_w1.py": "from pkg.feature import twice\n\n\ndef test_twice():\n"
                                               "    assert twice(2) == 4\n",
        f"tests/acceptance/{OTHER_WBS}/test_w2.py": "from pkg.gadget import gadget\n\n\ndef test_gadget():\n"
                                                     "    assert gadget() == 1\n",
        f"tests/acceptance/{WBS}/README.md": readme_text(WBS, "test_w1.py::test_twice"),
        f"tests/acceptance/{OTHER_WBS}/README.md": readme_text(OTHER_WBS, "test_w2.py::test_gadget"),
        "tests/unit/test_other.py": "from pkg.other import other\n\n\ndef test_other():\n    assert other() == 1\n",
        "tests/unit/test_lonely.py": "from pkg.lonely import VALUE\n\n\ndef test_lonely():\n    assert VALUE == 1\n",
    }


def plant(tmp_path: Path, branch: str = "main", extra: dict | None = None) -> Repo:
    repo = Repo(tmp_path / "project", branch)
    tool = repo.root / "governance" / "kernel" / "bin" / "tk"
    tool.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TK, tool)
    tool.chmod(0o755)
    planted = files()
    planted.update(extra or {})
    repo.commit("base", files=planted)
    return repo
