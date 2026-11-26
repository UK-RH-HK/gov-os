"""Helpers for the W2-20 fix SP-1 and SP-2 cases: the product's test runs put the registry's pinned Node bin first on
``PATH``; ``gov doctor`` names that folder.

Every case builds, under its own ``tmp_path``: a planted ``HOME`` with stand-in tools (shell scripts) in a Node
folder of its own, a small project with a tool registry of its own, and a caller environment built from scratch whose
``PATH`` holds none of those folders. A probe in the child records the ``PATH`` it got and what ``node`` and
``openspec`` resolve to. The real ``~/.gov-os``, the real Node and the real tools are never what answers: this
machine's ``/usr/bin/node``, where there is one, is only what must not answer first.
"""

from __future__ import annotations

import json
import os
import site
import stat
import subprocess
import sys
from pathlib import Path

import w2_20_support as base

SRC = base.SRC
PIN = "v22.23.3"          # as the real registry writes a Node version
OTHER_PIN = "v97.1.4"     # a pin no code could have fixed in itself
TOOL = "openspec"         # the tool installed beside Node; on none of the caller's PATH folders
NVM = ".nvm/versions/node"
RUN_TIMEOUT_S = 240.0     # a wait under parallel load, not a time the ticket promises

# What a child writes about its environment: argv[1] is the record file.
PROBE = """import json, os, shutil, sys
record = {"path": os.environ.get("PATH", ""), "node": shutil.which("node"), "openspec": shutil.which("openspec")}
with open(sys.argv[1], "w", encoding="utf-8") as out:
    json.dump(record, out)
sys.exit(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
"""


def nvm_bin(home: Path, version: str = PIN) -> Path:
    return home / NVM / version / "bin"


def stand_in(path: Path, says: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!/bin/sh\necho '{says}'\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def install_node(folder: Path, version: str = PIN) -> Path:
    """A stand-in ``node`` and the stand-in tool beside it in ``folder``."""
    stand_in(folder / "node", version)
    stand_in(folder / TOOL, "1.13.2")
    return folder


def entry(name: str, version: str, install: str | None = None) -> dict:
    """A registry entry with the real registry's keys; the install line, by default, is the real Node's form (no
    ``PATH=`` prefix)."""
    if install is None:
        install = f"bash -c '. ~/.nvm/nvm.sh && nvm install {version.lstrip('v')}'"
    return {"name": name, "version": version, "sha256": "0" * 64, "install": install, "uninstall": "echo uninstall",
            "date": "2026-11-26", "approved_by": "test"}


def registry_text(entries: list[dict]) -> str:
    lines = ["tools:"]
    for item in entries:
        for number, (key, value) in enumerate(item.items()):
            lines.append(f"  {'- ' if number == 0 else '  '}{key}: {json.dumps(value)}")
    return "\n".join(lines) + "\n"


def write(root: Path, rel: str, text: str) -> Path:
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_registry(root: Path, entries: list[dict]) -> None:
    write(root, "governance/project/tool-registry.yaml", registry_text(entries))


def plant_home(home: Path) -> Path:
    """``home`` with a git identity and the user site's ``lib`` linked in, where pytest is installed."""
    (home / ".local").mkdir(parents=True, exist_ok=True)
    (home / ".local" / "lib").symlink_to(Path(site.getuserbase()) / "lib")
    write(home, ".gitconfig", "[user]\n\tname = W2-20 tests\n\temail = w2-20@example.invalid\n")
    return home


def caller_env(tmp_path: Path, home: Path, **extra) -> dict:
    """A caller's environment built from scratch: no Node folder and no ``openspec`` on its ``PATH``."""
    temp = tmp_path / "tmp"
    temp.mkdir(exist_ok=True)
    env = {"PATH": base.SAFE_PATH, "HOME": str(home), "TMPDIR": str(temp), "LC_ALL": "C.UTF-8",
           "PYTHONPATH": str(SRC), "PYTHONDONTWRITEBYTECODE": "1", "GIT_CONFIG_NOSYSTEM": "1",
           "PYTHONUSERBASE": site.getuserbase(), "PYTEST_XDIST_AUTO_NUM_WORKERS": "1"}
    env.update(extra)
    return env


def git_project(root: Path, env: dict, files: dict) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        write(root, rel, text)
    for args in (("init", "-q", "-b", "main"), ("add", "-A"), ("commit", "-q", "-m", "initial")):
        subprocess.run(["git", "-C", str(root), *args], env=env, check=True, capture_output=True,
                       timeout=RUN_TIMEOUT_S)
    return root


def gov(root: Path, env: dict, *argv: str, module: str = "gov.cli.main"):
    """``python3 -m <module> <argv> --root <root> --json``: ``(exit code, envelope, text for a failure)``."""
    command = [sys.executable, "-m", module, *argv, "--root", str(root), "--json"]
    done = subprocess.run(command, cwd=str(root), env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          timeout=RUN_TIMEOUT_S)
    said = f"exit {done.returncode}\nstdout: {done.stdout[-3000:]}\nstderr: {done.stderr[-3000:]}"
    try:
        envelope = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"no JSON envelope from {' '.join(argv)}\n{said}") from None
    return done.returncode, envelope, said


def body(envelope: dict) -> dict:
    """``result`` of a passed command, else ``error.details``."""
    found = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    return found if isinstance(found, dict) else {}


def telling_test(record: Path, expected: Path) -> str:
    """A planted test file: it appends what it resolved to ``record`` and passes only when the tool and ``node`` are
    the ones in ``expected``."""
    return f'''import json
import os
import shutil


def test_tool():
    seen = {{"path": os.environ.get("PATH", ""), "node": shutil.which("node"), "openspec": shutil.which("openspec")}}
    with open({str(record)!r}, "a", encoding="utf-8") as out:
        out.write(json.dumps(seen) + "\\n")
    assert seen["openspec"] == {str(expected / TOOL)!r}, seen
    assert seen["node"] == {str(expected / "node")!r}, seen
'''


def records(record: Path) -> list[dict]:
    if not record.is_file():
        return []
    return [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines() if line.strip()]


def first_folder(record: dict) -> str:
    return record["path"].split(os.pathsep)[0]
