"""Builder tests for W2-95: core-pathmap reads the mapping form and fails closed (DEC-959 item 9).

Regression evidence only; planted path maps in temporary git repositories, never this repository's own.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check.pathmap import PATH_MAP_REL, check  # noqa: E402

NAMESPACE = (
    "    memory_class: governance\n    sensitivity: internal\n    permitted_roles: [engineer]\n"
    "    retention: r\n    export_policy: e\n    embedding_policy: n\n    provenance: p\n    deletion_rebuild: d\n"
)


def _repo(root: Path, path_map: str | bytes | None, files=("README.md", "src/a.py", "src/sub/b.py")) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], capture_output=True, check=True)
    for rel in files:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("x\n", encoding="utf-8")
    (root / "governance" / "project").mkdir(parents=True, exist_ok=True)
    if path_map is not None:
        target = root / PATH_MAP_REL
        target.write_bytes(path_map if isinstance(path_map, bytes) else path_map.encode("utf-8"))
    subprocess.run(["git", "-C", str(root), "add", "-A"], capture_output=True, check=True)
    return root


def _mapping(**namespaces: list[str]) -> str:
    text = "namespaces:\n"
    for name, paths in namespaces.items():
        text += f"  {name}:\n    paths: {json.dumps(paths)}\n" + NAMESPACE
    return text


def _codes(findings):
    return sorted((f["code"], f["path"]) for f in findings)


def test_mapping_form_green(tmp_path):
    root = _repo(tmp_path / "r", _mapping(root=["*"], src=["src/**"], gov=["governance/**"]))
    assert check(root) == []


def test_mapping_form_names_unplaced_and_doubly_placed(tmp_path):
    root = _repo(tmp_path / "r", _mapping(root=["*"], src=["src/*"], also=["src/a.py"], gov=["governance/**"]))
    findings = check(root)
    assert _codes(findings) == [("PATH_MULTIPLE_NAMESPACES", "src/a.py"), ("PATH_NO_NAMESPACE", "src/sub/b.py")]
    double = next(f for f in findings if f["code"] == "PATH_MULTIPLE_NAMESPACES")
    assert sorted(double["namespaces"]) == ["also", "src"]


def test_single_star_stays_inside_one_folder(tmp_path):
    root = _repo(tmp_path / "r", _mapping(everything=["*"]))
    assert _codes(check(root)) == [
        ("PATH_NO_NAMESPACE", PATH_MAP_REL), ("PATH_NO_NAMESPACE", "src/a.py"), ("PATH_NO_NAMESPACE", "src/sub/b.py")]


def test_list_form_still_read(tmp_path):
    path_map = ("namespaces:\n  - name: all\n    paths: ['**']\n  - name: src\n    paths: ['src/sub/**']\n")
    findings = check(_repo(tmp_path / "r", path_map))
    assert _codes(findings) == [("PATH_MULTIPLE_NAMESPACES", "src/sub/b.py")]


@pytest.mark.parametrize("path_map, cause", [
    (None, "missing"),
    (b"namespaces: {a: \xff}\n", "UTF-8"),
    ("namespaces: [unclosed\n", "parsed"),
    ("- just\n- a list\n", "map"),
    ("", "map"),
    ("state_class: AUTHORITATIVE\n", "no namespaces"),
    ("namespaces: everything\n", "neither"),
    ("namespaces:\n  a: '**'\n", "a"),
    ("namespaces:\n  a: {paths: '**'}\n", "a"),
    ("namespaces:\n  a: {paths: []}\n", "a"),
    ("namespaces:\n  a: {paths: [3]}\n", "a"),
    ("namespaces:\n  - paths: ['**']\n", "None"),
    ("namespaces:\n  - '**'\n", "None"),
])
def test_unusable_path_map_is_a_finding(tmp_path, path_map, cause):
    findings = check(_repo(tmp_path / "r", path_map))
    assert len(findings) == 1
    assert findings[0]["path"] == PATH_MAP_REL
    assert findings[0]["code"].startswith("PATH_MAP_")
    assert cause in findings[0]["message"]


def test_unreadable_path_map_is_a_finding(tmp_path):
    root = _repo(tmp_path / "r", None)
    (root / PATH_MAP_REL).mkdir()
    findings = check(root)
    assert [f["code"] for f in findings] == ["PATH_MAP_UNREADABLE"]


def test_git_not_answering_is_a_finding(tmp_path, monkeypatch):
    root = tmp_path / "r"
    (root / "governance" / "project").mkdir(parents=True)
    (root / PATH_MAP_REL).write_text(_mapping(all=["**"]), encoding="utf-8")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    assert [f["code"] for f in check(root)] == ["TRACKED_PATHS_UNLISTED"]


def test_no_gov_project_stays_silent(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], capture_output=True, check=True)
    assert check(root) == []


def test_command_prints_json_and_exits_non_zero(tmp_path):
    root = _repo(tmp_path / "r", "namespaces: everything\n")
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    result = subprocess.run([sys.executable, "-P", "-m", "gov.check.pathmap"], cwd=root, env=env,
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert json.loads(result.stdout)[0]["code"] == "PATH_MAP_INVALID"
    green = _repo(tmp_path / "g", _mapping(all=["**"]))
    result = subprocess.run([sys.executable, "-P", "-m", "gov.check.pathmap"], cwd=green, env=env,
                            capture_output=True, text=True)
    assert (result.returncode, result.stdout) == (0, "")
