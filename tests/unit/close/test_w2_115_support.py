"""Planted projects for W2-115's unit tests (the smart close). No test here: the helpers the other files share."""
from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from .conftest import TK, Repo

TICKET, WBS = "T-0001", "W-1"  # the kernel's ticket id grammar (the checkpoint reads it)
OTHER = "T-0002"
OWN_SUITE = f"tests/acceptance/{WBS}/"
OWN_TEST = f"{OWN_SUITE}test_w_1.py"

PASS = "def test_ok():\n    assert True\n"


def map_data(**more) -> dict:
    data = {"version": 1, "shared_core": ["src/pkg/core.py"],
            "record_only": [".tickets/**.md", "docs/**.md", "docs/close/nightly/*.json"],
            "record_reading": ["tests/unit/test_records.py"], "every_close": [],
            "couplings": [{"paths": ["src/pkg/core.py"], "suites": ["tests/unit/test_core_contract.py"],
                           "why": "the core's contract is read by a test that does not import it"}],
            "test_inputs": ["fixtures/**"], "per_test_timeout": 60, "distribution": "load"}
    data.update(more)
    return data


def ticket_text(ticket: str = TICKET, wbs: str = WBS, profile: str = "STANDARD", status: str = "in_progress",
                kpis: dict | None = None, paths: list[str] | None = None) -> str:
    front = {"id": ticket, "status": status, "deps": [], "links": [], "created": "2026-11-12T00:00:00Z",
             "type": "task", "priority": 2, "wbs_id": wbs, "profile": profile, "role": "engineer",
             "allowed_paths": paths or ["src/pkg/feature.py", f"tests/acceptance/{wbs}/**"],
             "acceptance_tests": {"path": f"tests/acceptance/{wbs}/"},
             "kpis": kpis or {"success": ["it works"], "failure": ["it breaks"]}}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n# A ticket\n"


def files(mode: str | None = "scoped", **ticket) -> dict:
    out = {
        ".gitignore": ".gov-runtime/\n__pycache__/\n*.pyc\n",
        "governance/project/test-map.yaml": yaml.safe_dump(map_data(), sort_keys=False),
        f".tickets/{TICKET}.md": ticket_text(**ticket),
        "src/pkg/__init__.py": "",
        "src/pkg/core.py": "def add(a, b):\n    return a + b\n",
        "src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)\n",
        "src/pkg/other.py": "def other():\n    return 1\n",
        "src/pkg/lonely.py": "VALUE = 1\n",
        OWN_TEST: "from pkg.feature import twice\n\n\ndef test_twice():\n    assert twice(2) == 4\n",
        "tests/unit/test_core.py": "from pkg import core\n\n\ndef test_add():\n    assert core.add(1, 2) == 3\n",
        "tests/unit/test_core_contract.py": PASS,
        "tests/unit/test_other.py": "from pkg.other import other\n\n\ndef test_other():\n    assert other() == 1\n",
        "tests/unit/test_records.py": PASS,
        "docs/notes.md": "# notes\n",
    }
    if mode is not None:
        out["governance/project/close.yaml"] = f"close: {mode}\n"
    return out


def project(tmp_path: Path, mode: str | None = "scoped", extra: dict | None = None, **ticket) -> Repo:
    """A planted project: base committed without a task; the ticket tool in its kernel's place."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    repo = Repo(tmp_path / "project")
    tool =repo.root / "governance" / "kernel" / "bin" / "tk"
    tool.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TK, tool)
    tool.chmod(0o755)
    planted = files(mode, **ticket)
    planted.update(extra or {})
    repo.commit("base", files=planted)
    return repo


def change(repo: Repo, planted: dict, ticket: str = TICKET, message: str = "work") -> str:
    return repo.commit(message, f"Task: {ticket}", "Role: engineer", files=planted)


def green_night(repo: Repo, stamp: str = "20261101T010000Z") -> str:
    """A green nightly record naming the head as it is now, committed as a record (no task): the last green base."""
    import json

    head = repo.git("rev-parse", "HEAD").strip()
    record = {"verdict": "green", "head": head, "secrets_full_scan": True}
    repo.commit("night", files={f"docs/close/nightly/NR-{stamp}-{head[:12]}.json": json.dumps(record) + "\n"})
    return head


def write(repo: Repo, rel: str, text: str) -> None:
    path = repo.root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
