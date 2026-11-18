"""F1: an update to a release that fails hash verification refuses and changes nothing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_17_support as support

MANIFEST, FILE, WHEEL = "manifest", "files", "wheel"


def _tamper(source, base, kind):
    """A copy of the source whose tag ``vB`` is moved onto a commit that tampers with release B."""
    repo = support.w216.clone_folder(source.repo, base / f"gov-os-{kind}")
    if kind == MANIFEST:
        path = repo / support.w216.RELEASES_REL / support.B / "manifest.json"
        data = json.loads(path.read_bytes())
        data["release_notes"] = [*data.get("release_notes", []), "- W2-17: a line added after the hash was taken"]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    else:
        path = repo / "template" / support.UPDATED
        path.write_text(path.read_text(encoding="utf-8") + "W2-17: a line added after the hash was taken\n",
                        encoding="utf-8")
    support.commit_all(repo, f"W2-17: release B tampered ({kind})")
    support.git(repo, "tag", "-f", support.TAG_B, "HEAD")
    return repo


@pytest.fixture(scope="module")
def tampered(source, tmp_path_factory):
    base = tmp_path_factory.mktemp("w2-17-tampered")
    return {kind: _tamper(source, base, kind) for kind in (MANIFEST, FILE)}


def _arguments(kind, tampered, source, sandbox):
    if kind in (MANIFEST, FILE):
        return ("--source", str(tampered[kind])), ()
    wheel = source.manifest_b["wheel"]
    fake = Path(sandbox.elsewhere) / wheel["name"]
    fake.write_bytes(b"W2-17: not the wheel of release B\n")
    return ("--wheel", str(fake)), (wheel["sha256"], support.sha256(fake))


@pytest.mark.parametrize("mode", ["update", "check"])
@pytest.mark.parametrize("kind", [MANIFEST, FILE, WHEEL])
def test_a_release_failing_hash_verification_is_refused_and_nothing_changes(kind, mode, tampered, source,
                                                                            own_project, sandbox):
    project = own_project
    args, hashes = _arguments(kind, tampered, source, sandbox)
    before, before_pin = support.tree_state(project), support.pin_state(project)

    run = support.update(project, sandbox, *args, *(("--check",) if mode == "check" else ()))

    what = f"`gov update {support.B}{' --check' if mode == 'check' else ''}` with a {kind} mismatch"
    assert run.returncode != 0, f"{what} exited 0\n{run.describe()}"
    error = run.error()
    details = error.get("details") or {}
    assert error.get("code") == support.UPDATE_REFUSED and details.get("reason") == kind, (
        f"{what} is not refused as {support.UPDATE_REFUSED} with reason {kind!r}\n{run.describe()}")
    message = str(error.get("message", ""))
    if kind == MANIFEST:
        assert "manifest" in message.lower(), f"{what}: the refusal does not name the manifest\n{run.describe()}"
    elif kind == FILE:
        assert support.UPDATED in message, f"{what}: the refusal does not name {support.UPDATED}\n{run.describe()}"
    else:
        assert "wheel" in message.lower() and any(digest in message for digest in hashes), (
            f"{what}: the refusal does not name the wheel with the mismatching sha256\n{run.describe()}")
    changed = support.tree_difference(before, support.tree_state(project))
    assert not changed, f"{what} changed HEAD or files outside .git: {changed[:20]}"
    assert support.pin_state(project) == before_pin, f"{what} changed <common>/gov/: {support.pin_state(project)!r}"
    support.assert_never_applied(run, what)
