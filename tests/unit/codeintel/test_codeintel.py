"""Builder tests for the codebase-memory wrapper (W1-16).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: when the filter cannot decide, the earlier index is gone and
none is built; the tool is given the staged folder, the repository's home and
the caller's own runtime directory; and a tool that reports an error is not an
empty answer. The codebase-memory binary is not run: a stand-in script on
``PATH`` records how it is called. Every repository is a temporary directory.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import codeintel  # noqa: E402

MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
PLANTED = "_".join(["W116", "UNIT", "CAN" + "ARY", "6TR1"])
# A stand-in for the binary: it writes its arguments and two variables of its environment next to itself.
STAND_IN = ("#!/bin/sh\n"
            "here=$(dirname \"$0\")\n"
            "printf '%s\\n' \"$@\" \"$CBM_CACHE_DIR\" \"$CBM_RUNTIME_DIR\" > \"$here/call.txt\"\n"
            "cat \"$here/answer.json\"\n")


def _repository(root):
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for rel, text in {"governance/project/path-map.yaml": MAP, "app/clean.py": "def clean():\n    return 1\n",
                      "app/planted.py": f"def {PLANTED}():\n    return 2\n", ".gitignore": ".gov-runtime/\n"}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    return root


def _stand_in(tmp_path, monkeypatch, answer):
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / codeintel.TOOL).write_text(STAND_IN, encoding="utf-8")
    (tools / codeintel.TOOL).chmod(0o755)
    (tools / "answer.json").write_text(json.dumps(answer), encoding="utf-8")
    monkeypatch.setenv("PATH", str(tools), prepend=":")
    return tools / "call.txt"


def test_no_index_is_left_when_the_filter_cannot_decide(tmp_path):
    root = _repository(tmp_path / "repo")  # no .gitleaks.toml: the filter raises
    earlier = codeintel.home(root) / "code.db"
    earlier.parent.mkdir(parents=True)
    earlier.write_text("an earlier index", encoding="utf-8")
    with pytest.raises(RuntimeError):
        codeintel.index(root)
    assert not (root / codeintel.BASE_REL).exists()


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
def test_the_tool_is_given_the_staged_files_the_home_and_the_callers_runtime_directory(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    call = _stand_in(tmp_path, monkeypatch, {"isError": False, "content": [{"type": "text", "text": "{}"}]})
    monkeypatch.setenv("CBM_RUNTIME_DIR", str(tmp_path / "runtime"))
    codeintel.index(root)
    *_, tool, arguments, cache, runtime = call.read_text(encoding="utf-8").splitlines()
    staged = root / codeintel.BASE_REL / "files"
    assert tool == "index_repository" and json.loads(arguments)["repo_path"] == str(staged)
    assert cache == str(codeintel.home(root)) and runtime == str(tmp_path / "runtime")
    files = sorted(path.relative_to(staged).as_posix() for path in staged.rglob("*") if path.is_file())
    assert files == [".gitignore", ".gitleaks.toml", "app/clean.py", "governance/project/path-map.yaml"]


def test_an_error_of_the_tool_is_not_an_empty_answer(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    _stand_in(tmp_path, monkeypatch, {"isError": True, "content": [{"type": "text", "text": "{\"error\": \"x\"}"}]})
    with pytest.raises(RuntimeError):
        codeintel.definitions(root, "clean")
    with pytest.raises(RuntimeError):
        codeintel.projects(root)
