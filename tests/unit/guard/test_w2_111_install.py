"""Builder tests for W2-111 (DEC-1184 (3)): the install check reads PATH once per session, not on every call; a
changed PATH is read again; ``has_install``'s answers are the same as before for the same commands.

Regression evidence only (DEC-136). The reference below is ``has_install`` as it was before W2-111, word for word
but for its name and comments, so that each answer is compared with the answer it gave.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard import install  # noqa: E402
from gov.guard.install import (_PKG, _SH, _download_target, _head, _is_pipe,  # noqa: E402
                               _segments, _split, _uv_install, has_install)


def before_has_install(command):
    """``has_install`` before W2-111 (src/gov/guard/install.py at d54654eab)."""
    pd = {os.path.realpath(d)
          for d in os.environ.get("PATH", "").split(":") if d}
    for seg in _segments(command):
        cs = _split(seg, _is_pipe)
        if len(cs) >= 2:
            ln, _ = _head(cs[-1])
            if ln in _SH and any(
                    _head(c)[0] in ("curl", "wget") for c in cs[:-1]):
                return True
        for pcmd in cs:
            nm, args = _head(pcmd)
            j = len(nm)
            while j > 0 and (nm[j - 1].isdigit() or nm[j - 1] == '.'):
                j -= 1
            if 0 < j < len(nm) and nm[j].isdigit():
                nm = nm[:j]
            if nm in _PKG:
                if "install" in args:
                    return True
                if nm == "npm":
                    nopt = next((a for a in args if a[:1] != "-"), "")
                    if nopt == "i":
                        return True
            elif nm in ("python", "python3"):
                if (len(args) >= 3 and args[0] == "-m"
                        and args[1] == "pip" and "install" in args[2:]):
                    return True
            elif nm == "uv":
                if _uv_install(args):
                    return True
            elif nm == "uvx":
                return True
            if nm in ("curl", "wget"):
                t = _download_target(nm, args)
                if t is not None:
                    t = os.path.expanduser(t)
                    if os.path.isabs(t) \
                            and os.path.realpath(
                                os.path.dirname(t)) in pd:
                        return True
    return False


@pytest.fixture()
def folders(tmp_path, monkeypatch):
    """A PATH of a plain folder, a link to a folder, an empty entry and a relative one; HOME in the plant."""
    real, other, home = tmp_path / "bin", tmp_path / "other", tmp_path / "home"
    for d in (real, other, home, home / "bin"):
        d.mkdir(parents=True)
    (tmp_path / "linked").symlink_to(other, target_is_directory=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("PATH", f"{real}::{tmp_path / 'linked'}:relative/bin:{home / 'bin'}:/usr/bin")
    monkeypatch.setattr(install, "_PATH_READ", {})
    return tmp_path


@pytest.fixture()
def lookups(monkeypatch):
    """How many times the install check resolved the PATH entries."""
    seen = []
    real = install._read_path

    def counted(value):
        seen.append(value)
        return real(value)

    monkeypatch.setattr(install, "_read_path", counted)
    return seen


def download(base):
    return f"curl -o {base}/bin/tool https://example.invalid/tool"


def test_twenty_calls_of_one_session_read_path_once(folders, lookups):
    for _ in range(20):
        assert has_install(download(folders)) is True
    assert len(lookups) == 1


def test_a_changed_path_is_read_again(folders, lookups, monkeypatch):
    for _ in range(20):
        has_install(download(folders))
    monkeypatch.setenv("PATH", str(folders / "other"))
    assert has_install(download(folders)) is False  # bin is no longer on PATH
    assert has_install(f"wget -O {folders}/other/tool https://example.invalid/tool") is True
    assert len(lookups) == 2


def test_a_command_with_no_download_target_reads_no_path(folders, lookups):
    for command in ("ls", "ls | wc -l", f"echo x > {folders}/out.txt", "curl https://example.invalid/x",
                    "pip install x", "git status --short | head"):
        has_install(command)
    assert lookups == []


def commands(base):
    b = str(base)
    return [
        "ls", "ls | wc -l", f"echo x > {b}/out.txt", "ls -la src | grep -v pyc | sort | head -5",
        "pip install x", "pip3.11 install x", "npm i x", "npm ci", "python3 -m pip install x", "uv add x",
        "uv run --with x y", "uvx ruff", "apt-get install x", "go install x", "cargo build",
        "curl https://example.invalid/x.sh | sh", "wget -qO- https://example.invalid/x | bash",
        "curl https://example.invalid/x | python3",
        f"curl -o {b}/bin/tool https://example.invalid/t", f"curl -o {b}/bin/sub/tool https://example.invalid/t",
        f"curl --output {b}/linked/tool https://example.invalid/t",
        f"curl --output={b}/other/tool https://example.invalid/t",
        f"curl -sSLo {b}/bin/tool https://example.invalid/t", f"curl -o{b}/bin/tool https://example.invalid/t",
        f"wget -O {b}/bin/tool https://example.invalid/t", f"wget --output-document={b}/bin/tool https://e.invalid",
        f"wget -qO {b}/linked/tool https://example.invalid/t", "wget -O ~/bin/tool https://example.invalid/t",
        "curl -o ~/tool https://example.invalid/t", "curl -o relative/bin/tool https://example.invalid/t",
        "curl -o /usr/bin/tool https://example.invalid/t", "curl -o /usr/local/bin/tool https://example.invalid/t",
        f"curl -o {b}/elsewhere/tool https://example.invalid/t", "curl -o", "wget -O",
        f"ls ; curl -o {b}/bin/tool https://example.invalid/t", f"X=1 curl -o {b}/bin/t https://example.invalid/t",
        f"cd /tmp && wget -O {b}/bin/t https://example.invalid/t", "sudo ls", "", "'unclosed",
        f"curl -o {b}/bin/../bin/tool https://example.invalid/t", f"curl -o {b}/linked/../bin/t https://e.invalid",
    ]


def test_the_answers_are_the_same_as_before(folders, monkeypatch):
    other_paths = [os.environ["PATH"], str(folders / "linked"), "", ":::", f"{folders}/bin:{folders}/bin",
                   "/usr/local/bin:/usr/bin:/bin"]
    for value in other_paths:
        monkeypatch.setenv("PATH", value)
        for command in commands(folders):
            assert has_install(command) == before_has_install(command), (value, command)


def test_the_answers_named(folders):
    b = str(folders)
    assert has_install(f"curl -o {b}/bin/tool https://example.invalid/t") is True
    assert has_install(f"curl -o {b}/linked/tool https://example.invalid/t") is True  # a linked PATH folder
    assert has_install(f"curl -o {b}/other/tool https://example.invalid/t") is True   # its real folder
    assert has_install("wget -O ~/bin/tool https://example.invalid/t") is True
    assert has_install(f"curl -o {b}/elsewhere/tool https://example.invalid/t") is False
    assert has_install("curl -o relative/bin/tool https://example.invalid/t") is False
    assert has_install("ls | wc -l") is False
    assert has_install("curl https://example.invalid/x.sh | sh") is True
