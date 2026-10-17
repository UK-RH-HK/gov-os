"""Unit tests for gov.release (DEC-135: regression evidence). Every repository is built from scratch in tmp_path."""

from __future__ import annotations

import hashlib
import json
import subprocess

import pytest

from gov.release import HASH_NAME, MANIFEST_NAME, RELEASES_REL, ReleaseError, build, verify


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def _repo(root):
    files = {
        "pyproject.toml": '[build-system]\nrequires = ["setuptools"]\nbuild-backend = "setuptools.build_meta"\n'
                          '[project]\nname = "demo"\nversion = "0.7.3"\n'
                          '[tool.setuptools.packages.find]\nwhere = ["src"]\n',
        "src/demo/__init__.py": "",
        "template/governance/kernel/schemas/ticket.schema.json": "{}\n",
        "template/governance/kernel/skills/superpowers/vendored.yaml": 'version: "v6.4.2"\n',
        "template/governance/kernel/vendor/superpowers/LICENSE": "MIT licence text\n",
    }
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "init", "-q", "-b", "w2/integrate")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "first")
    return root


def test_a_release_records_its_manifest_and_the_manifest_hash(tmp_path):
    repo = _repo(tmp_path)
    folder = build(repo, "1.4.0")
    data = (folder / MANIFEST_NAME).read_bytes()
    manifest = json.loads(data)
    assert manifest["version"] == "1.4.0" and manifest["commit"] == _git(repo, "rev-parse", "HEAD").strip()
    assert manifest["cli_version"] == "0.7.3" and manifest["schema_versions"] == {
        "ticket": hashlib.sha256(b"{}\n").hexdigest()}
    assert manifest["vendored"]["superpowers"]["version"] == "v6.4.2"
    assert manifest["wheel"]["name"].endswith(".whl") and len(manifest["wheel"]["sha256"]) == 64
    assert (folder / HASH_NAME).read_text().split()[0] == hashlib.sha256(data).hexdigest()
    assert _git(repo, "tag", "--list") == ""
    assert verify(repo, "1.4.0")[1] == hashlib.sha256(data).hexdigest()
    with pytest.raises(ReleaseError, match="immutable"):
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
        _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "record")
        build(repo, "1.4.0")


@pytest.mark.parametrize("version", ("1.4", "v1.4.0", "01.4.0", "1.4.0-"))
def test_a_version_that_is_not_semantic_is_refused(tmp_path, version):
    with pytest.raises(ReleaseError, match="semantic"):
        build(_repo(tmp_path), version)


def test_an_unclean_tree_or_another_branch_is_refused(tmp_path):
    repo = _repo(tmp_path)
    (repo / "notes.txt").write_text("x\n", encoding="utf-8")
    with pytest.raises(ReleaseError, match="uncommitted"):
        build(repo, "1.4.0")
    (repo / "notes.txt").unlink()
    _git(repo, "checkout", "-q", "-b", "other")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "x")
    with pytest.raises(ReleaseError, match="w2/integrate"):
        build(repo, "1.4.0")
    assert not (repo / RELEASES_REL).exists()


@pytest.mark.parametrize("how", ("changed", "added", "removed", "manifest hash"))
def test_verify_refuses_a_release_that_does_not_match_its_hashes(tmp_path, how):
    repo = _repo(tmp_path)
    folder = build(repo, "1.4.0")
    schema = repo / "template/governance/kernel/schemas/ticket.schema.json"
    if how == "changed":
        schema.write_text("{ }\n", encoding="utf-8")
    elif how == "added":
        (schema.parent / "added.schema.json").write_text("{}\n", encoding="utf-8")
    elif how == "removed":
        schema.unlink()
    else:
        (folder / HASH_NAME).write_text("0" * 64 + f"  {MANIFEST_NAME}\n", encoding="utf-8")
    with pytest.raises(ReleaseError, match="added.schema.json" if how == "added" else
                       ("manifest" if how == "manifest hash" else "ticket.schema.json")):
        verify(repo, "1.4.0")
