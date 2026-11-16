"""W2-192: the fixture repository the spec audit's builder tests share (regression evidence only, DEC-136). A git
repository built in ``tmp_path``; nothing is replaced: AS reads the inventory, the classes, the blobs and git history."""
from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from gov.adopt import project, spec_audit, stages  # noqa: F401
from gov.cli.errors import GovError

from .test_adopt import commit, sh, write  # noqa: F401

PATHS = ("src/**", "tests/**", "specs/**", "docs/**", ".tickets/**", ".gitignore", "README.md")


def config(extra=None):
    spaces = {**(extra or {}), "all": {"paths": list(PATHS), "embedding_policy": "embedded"}}
    return {"path-map.yaml": {"namespaces": spaces, "capabilities": {"code_intelligence": {"enabled": False}}}}


def spec(text, **front):
    head = yaml.safe_dump(front, sort_keys=False) if front else ""
    return (f"---\n{head}---\n\n" if front else "") + text


TICKET = "---\nid: {id}\nstatus: {status}\n{more}---\n# {id}\n"

FILES = {
    ".gitignore": ".gov-runtime/\n",
    "README.md": "# project\n",
    "src/alpha.py": "def alpha():\n    return 1\n",
    "src/beta.py": "def beta():\n    return 2\n",
    "src/orphan.py": "ORPHAN = 3\n",
    "src/__init__.py": "",
    "tests/test_alpha.py": "from alpha import alpha\n\n\ndef test_alpha():\n    assert alpha() == 1\n",
    "specs/built.md": spec("# Built spec\n\nThe code is `src/alpha.py`.\n", type="spec", wave=1, status="established"),
    "specs/partly.md": spec("# Partly built spec\n\nThe code is `src/beta.py` and `src/gamma.py`.\n"),
    "docs/unbuilt.md": spec("The code will be `src/nothing.py`.\n", type="spec", title="An unbuilt spec", wave=2),
    ".tickets/T-1.md": TICKET.format(id="T-1", status="closed", more="wave: 1\n"),
    ".tickets/T-2.md": TICKET.format(id="T-2", status="open", more="tags: [wave-2, other]\n"),
}


def build(tmp_path: Path, files=FILES) -> Path:
    root = tmp_path / "project"
    for rel, text in files.items():
        write(root, rel, text)
    sh(root, "init", "-q")
    sh(root, "config", "user.name", "t")
    sh(root, "config", "user.email", "t@example.invalid")
    commit(root, "fixture")
    return root.resolve()


@pytest.fixture()
def repo(tmp_path):
    return build(tmp_path)


def stage(root, name, conf=None, session="adopter", **more):
    args = SimpleNamespace(**{"lite": True, "stage": name, "map": None, "verdict": None, "session": session, **more})
    return stages.run(root, args, conf or config())


def through_a2(root, conf=None):
    for name in ("A0", "A1", "A2"):
        stage(root, name, conf)


def audited(root, conf=None):
    through_a2(root, conf)
    return stage(root, "AS", conf)


def record(root, name="AS") -> dict:
    return project.frontmatter((root / project.record_path(name)).read_text(encoding="utf-8"))


def refusal(root, name, code, conf=None, **more) -> GovError:
    with pytest.raises(GovError) as caught:
        stage(root, name, conf, **more)
    assert caught.value.code == "ADOPT_" + code, caught.value.message
    return caught.value


def keep_all(root) -> str:
    file = root.parent / "proposal.yaml"
    file.write_text(yaml.safe_dump({"artefacts": []}), encoding="utf-8")
    return str(file)


def rewrite(root, change) -> None:
    """Edit the committed AS record's front matter by ``change(head)`` and commit it (a record not as AS wrote it)."""
    head = record(root)
    for key in ("id", "type", "status", "state_class", "stage"):
        head.pop(key)
    change(head)
    (root / project.record_path("AS")).write_text(project.record_text("AS", head), encoding="utf-8")
    commit(root, "edit the AS record")


def by_path(rows) -> dict:
    return {row["path"]: row for row in rows}


def head_commits(root, *paths) -> list[str]:
    done = subprocess.run(["git", "-C", str(root), "log", "--format=%H", "--", *paths], capture_output=True, text=True,
                          check=True)
    return done.stdout.split()
