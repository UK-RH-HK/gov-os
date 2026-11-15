"""Builder tests for W2-88 run 9 (DEC-1183 (2)): the assessment's scan uses gov.secrets' folder-mode core, so no text is
joined to another in one gitleaks input and each finding names its own file.

Regression evidence only (DEC-136). The oracle where a verdict is judged is the one-per-file form (``gov.secrets._scan``
over one text). No secret stands whole in this file and none is printed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from gov import secrets
from gov.adopt import assess
from gov.cli.errors import GovError

REPO = Path(__file__).resolve().parents[3]
PASSWORD = "".join(["Hx7", "q2Lm", "Pz9", "Rt4"])
TOKEN = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"  # planted, built from parts
CURL_A = b"Check the service:\ncurl https://api.example.com/health\n"
CURL_B = (f"curl -u deploy:{PASSWORD} https://api.example.com/deploy\necho ok\n"
          "curl -u user:$PASSWORD https://api.example.com/other\n").encode()

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


@pytest.fixture()
def rules(tmp_path):
    (tmp_path / "r").mkdir()
    shutil.copy(REPO / "template/.gitleaks.toml", tmp_path / "r" / ".gitleaks.toml")
    return secrets._rules(tmp_path / "r")


@pytest.fixture()
def root(tmp_path):
    (tmp_path / "repo").mkdir()
    return tmp_path / "repo"


@pytest.fixture()
def runs(monkeypatch):
    seen = []
    real = secrets.subprocess.run

    def spy(command, **options):
        if command and command[0] == "gitleaks":
            seen.append((command[1], options.get("cwd"), sorted(os.listdir(options["cwd"])) if options.get("cwd") else None))
        return real(command, **options)

    monkeypatch.setattr(secrets.subprocess, "run", spy)
    return seen


def _held_alone(rules, data):
    return secrets._scan(rules, secrets._forms(data))


def test_the_curl_pair_in_one_batch_in_both_orders(rules, root, runs):
    assert _held_alone(rules, CURL_B) and not _held_alone(rules, CURL_A), "the plant"
    runs.clear()
    for order in ([("a.md", CURL_A), ("b.sh", CURL_B)], [("b.sh", CURL_B), ("a.md", CURL_A)]):
        scan = assess._Scan(rules, root)
        for rel, data in [(f"n{number}.md", b"Plain.\n") for number in range(5)] + order:
            scan.add(rel, data)
        scan.flush()
        assert {rel for rel, _ in scan.found} == {"b.sh"}, order
    assert {kind for kind, _, _ in runs} == {"dir"}
    assert all(names and all(name.isdigit() for name in names) for _, _, names in runs)
    assert not any(Path(cwd).exists() for _, cwd, _ in runs)


def test_a_finding_names_its_own_file_and_rule(rules, root):
    scan = assess._Scan(rules, root)
    scan.add("x/one.md", b"Plain.\n")
    scan.add("x/cfg env", f"TOKEN={TOKEN}\n".encode())
    scan.add("x/three.md", b"Plain.\n")
    scan.flush()
    assert {rel for rel, _ in scan.found} == {"x/cfg env"} and all(rule for _, rule in scan.found)


def test_a_report_that_cannot_be_placed_names_every_file_of_the_batch(rules, root, monkeypatch):
    def run(command, **options):
        return subprocess.CompletedProcess(command, 3, json.dumps([{"File": "7", "RuleID": "x"}]).encode(), b"")

    monkeypatch.setattr(secrets.subprocess, "run", run)
    scan = assess._Scan(rules, root)
    for rel in ("a.md", "b.md"):
        scan.add(rel, b"Plain.\n")
    scan.flush()
    assert {rel for rel, _ in scan.found} == {"a.md", "b.md"}


def test_a_scan_that_cannot_decide_is_assess_scan_failed_and_the_folder_is_removed(rules, root, monkeypatch):
    folders = []

    def run(command, **options):
        folders.append(Path(options["cwd"]))
        return subprocess.CompletedProcess(command, 2, b"", b"")

    monkeypatch.setattr(secrets.subprocess, "run", run)
    scan = assess._Scan(rules, root)
    scan.add("a.md", b"Plain.\n")
    with pytest.raises(GovError) as raised:
        scan.flush()
    assert raised.value.code == "ASSESS_SCAN_FAILED"
    assert folders and not any(folder.exists() for folder in folders)


def test_batches_follow_the_caps_and_close_removes_an_open_folder(rules, root, monkeypatch, runs):
    monkeypatch.setattr(secrets, "_BATCH_TEXTS", 3)
    scan = assess._Scan(rules, root)
    for number in range(7):
        scan.add(f"n{number}.md", b"Plain.\n")
    scan.flush()
    sizes = [len(names) for _, _, names in runs[::len(rules)]]
    assert sizes == [3, 3, 1]
    scan.add("left.md", b"Plain.\n")
    left = Path(scan.folder.path)
    assert left.is_dir()
    scan.close()
    assert scan.folder is None and not left.exists()


def test_assess_end_to_end_names_the_secret_by_rule_and_leaves_no_folder(tmp_path, monkeypatch):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args):
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)

    git("init", "-q")
    (repo / "docs").mkdir()
    (repo / "docs/a.md").write_bytes(CURL_A)
    (repo / "docs/b.sh").write_bytes(CURL_B)
    (repo / "docs/with space.env").write_text("TOKEN=" + TOKEN + "\n")
    (repo / ".gitleaks.toml").write_text((REPO / "template/.gitleaks.toml").read_text(encoding="utf-8"))
    git("add", "-A")
    git("commit", "-q", "-m", "one")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    result = assess.assess(repo, tmp_path / "out")
    assert {item["path"] for item in result["secrets"]} == {"docs/b.sh", "docs/with space.env"}
    assert list(scratch.iterdir()) == []
