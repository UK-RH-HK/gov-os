"""P0-3: ``install_hook`` writes the kit's reference-transaction, executable and byte-equal, once per state."""

import os
import subprocess

from gov.adapters import merge


def _repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    kit = tmp_path / "governance" / "kernel" / "githooks"
    kit.mkdir(parents=True)
    (kit / "reference-transaction").write_bytes(b"#!/bin/sh\nexit 0\n")
    return tmp_path


def test_installs_the_kit_file_executable_and_byte_equal(tmp_path):
    root = _repo(tmp_path)
    assert merge.install_hook(root) == ".git/hooks/reference-transaction"
    hook = root / ".git" / "hooks" / "reference-transaction"
    assert hook.read_bytes() == b"#!/bin/sh\nexit 0\n" and os.access(hook, os.X_OK)


def test_replaces_a_changed_hook_and_leaves_the_local_file(tmp_path):
    root = _repo(tmp_path)
    hooks = root / ".git" / "hooks"
    hooks.mkdir(exist_ok=True)
    (hooks / "reference-transaction").write_text("old")
    (hooks / "reference-transaction.local").write_text("mine")
    merge.install_hook(root)
    assert (hooks / "reference-transaction").read_bytes() == b"#!/bin/sh\nexit 0\n"
    assert (hooks / "reference-transaction.local").read_text() == "mine"


def test_a_kit_without_the_file_installs_nothing(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    assert merge.install_hook(tmp_path) is None
