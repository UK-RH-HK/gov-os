"""A tiny Gov OS-like source with numbered releases, for the pinned install's builder tests (W2-18, DAEO-057v).

The package is named ``gov`` and has the console script ``gov`` (``--version`` prints its version), so a pin made from
its wheel is a pin as the interface states it; it is a few files, so its wheel builds in a second.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from gov import release

MAIN = """import sys
def main():
    if sys.argv[1:] == ["--version"]:
        print("gov {version} (commit unknown)")
        return 0
    print("tiny gov", sys.prefix)
    return 0
"""


def git(repo: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env=env).stdout


def write_version(source: Path, version: str) -> None:
    (source / "pyproject.toml").write_text(
        "[build-system]\nrequires = [\"setuptools\"]\nbuild-backend = \"setuptools.build_meta\"\n\n"
        f"[project]\nname = \"gov\"\nversion = \"{version}\"\n\n[project.scripts]\ngov = \"gov.cli.main:main\"\n\n"
        "[tool.setuptools.packages.find]\nwhere = [\"src\"]\n", encoding="utf-8")
    (source / "src/gov/cli/main.py").write_text(MAIN.format(version=version), encoding="utf-8")


def cut_release(source: Path, version: str, *, wheel_sha256: str | None = None, template_note: str = "") -> dict:
    """Commit the version, write its record (manifest and sha256) on a commit of its own, tag it ``v<version>``."""
    write_version(source, version)
    (source / "template/governance/kernel/note.md").write_text(f"release {version}\n{template_note}", encoding="utf-8")
    git(source, "add", "-A")
    git(source, "commit", "-q", "-m", f"version {version}")
    commit = git(source, "rev-parse", "HEAD").strip()
    wheel = release._wheel(source, commit)
    if wheel_sha256:
        wheel = {**wheel, "sha256": wheel_sha256}
    files = {rel[len("template/"):]: hashlib.sha256(data).hexdigest()
             for rel, data in release._blobs(source, commit, "template").items()}
    manifest = {"version": version, "commit": commit, "cli_version": version, "wheel": wheel, "files": files}
    data = (json.dumps(manifest, indent=2) + "\n").encode()
    folder = source / "docs/releases" / version
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_bytes(data)
    (folder / "manifest.sha256").write_text(f"{hashlib.sha256(data).hexdigest()}  manifest.json\n", encoding="utf-8")
    git(source, "add", "-A")
    git(source, "commit", "-q", "-m", f"record {version}")
    git(source, "tag", f"v{version}")
    return manifest


def new_source(base: Path) -> Path:
    source = base / "source"
    (source / "src/gov/cli").mkdir(parents=True)
    (source / "template/governance/kernel").mkdir(parents=True)
    (source / "src/gov/__init__.py").write_text("", encoding="utf-8")
    (source / "src/gov/cli/__init__.py").write_text("", encoding="utf-8")
    git(source, "init", "-q", "-b", "main")
    return source


@pytest.fixture(scope="session")
def tiny_source(tmp_path_factory) -> dict:
    """A source holding releases 1.0.0 and 1.0.1, and 1.0.2 whose manifest names a wheel sha256 it does not build."""
    source = new_source(tmp_path_factory.mktemp("tiny"))
    manifests = {version: cut_release(source, version) for version in ("1.0.0", "1.0.1")}
    manifests["1.0.2"] = cut_release(source, "1.0.2", wheel_sha256="0" * 64)
    return {"source": source, "manifests": manifests}


def new_project(base: Path, source: Path) -> Path:
    project = base / "project"
    project.mkdir()
    git(project, "init", "-q", "-b", "main")
    (project / ".copier-answers.yml").write_text(f"_commit: v1.0.0\n_src_path: {source}\n", encoding="utf-8")
    return project
