"""Helpers for the W2-22 fix F2 cases (audit 3, M-04): ``gov doctor``'s ``tools`` part for a tool installed in its
own folder, and for a ``PATH=`` prefix that must never answer for another tool of the same binary.

Every case builds, under its own ``tmp_path``: a sandbox (HOME, bin), a small committed repository with a tool
registry of its own, and stand-in tools (shell scripts echoing a version). The machine's own home, Node and tools are
never read as answers: a stand-in ``node`` printing another version is first on the ``PATH`` ``gov`` runs with.
No registry key is added: each entry holds name, version, sha256, install, uninstall, date, approved_by, note.
"""

from __future__ import annotations

import hashlib
import stat
from pathlib import Path

import w2_22_support as base

w1_27 = base.w1_27

NVM = ".nvm/versions/node"
REA_FOLDER = "gov-os-runs/study-startup-launchpad/tool"
PATH_NODE_VERSION = "v18.20.8"   # what the stand-in ``node`` first on the PATH prints: an answer nobody here wants


def stand_in_text(version: str) -> str:
    return f"#!/bin/sh\necho '{version}'\n"


def stand_in_sha(version: str) -> str:
    return hashlib.sha256(stand_in_text(version).encode("utf-8")).hexdigest()


def write_stand_in(path: Path, version: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stand_in_text(version), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def node_bin(sandbox, version: str) -> Path:
    """The nvm folder of a Node under the sandbox's HOME (``<HOME>/.nvm/versions/node/<version>/bin``)."""
    return sandbox.home / NVM / version / "bin"


def rea_folder(sandbox) -> Path:
    return sandbox.home / REA_FOLDER


def rea_binary(sandbox) -> Path:
    return rea_folder(sandbox) / "node_modules" / ".bin" / "rea"


def _form(text: str, sandbox, form: str) -> str:
    """``text`` as the real registry writes it (``real``: ``~`` and ``$HOME``) or with the sandbox home spelled out
    (``abs``): the same places either way, since the case runs with HOME set to the sandbox's home."""
    return text if form == "real" else text.replace("$HOME", str(sandbox.home)).replace("~", str(sandbox.home))


def entry(name: str, version: str, sha: str, install: str, uninstall: str = "echo uninstall", note: str = "") -> str:
    extra = {"install": install, "uninstall": uninstall, "date": "2026-11-22", "approved_by": "test"}
    if note:
        extra["note"] = note
    return w1_27.tool_entry_yaml(name, version, sha, **extra)


def node_entry(sandbox, form: str, version: str = "v22.23.3", name: str = "node") -> str:
    """The registry's Node entries: no PATH prefix in the install line, the place only in the note."""
    number = version.lstrip("v")
    alias = " && nvm alias default 18" if number == "22.23.5" else ""
    return entry(name, version, stand_in_sha(version),
                 _form(f"bash -c '. ~/.nvm/nvm.sh && nvm install {number}{alias}'", sandbox, form),
                 note=_form(f"Node at ~/.nvm/versions/node/{version}/bin/node (sha256 of that binary).", sandbox, form))


def rea_entry(sandbox, form: str, version: str = "6.10.1") -> str:
    """The registry's REA entry as it stands: ``cd`` into the study's folder, the v22.23.5 prefix, a local npm install."""
    line = (f"cd ~/{REA_FOLDER} && PATH=$HOME/{NVM}/v22.23.5/bin:$PATH npm install --save-exact --omit=optional "
            f"--ignore-scripts rea-agents@{version}")
    return entry("rea-agents", version, stand_in_sha(version), _form(line, sandbox, form),
                 uninstall=_form(f"rm -rf ~/{REA_FOLDER}/node_modules", sandbox, form),
                 note="Installed locally in the study's folder, never globally.")


def openspec_entry(sandbox, form: str, version: str = "1.13.2") -> str:
    """A tool of the stack pin's Node: its install line carries that Node's prefix (DEC-448, DEC-452)."""
    line = f"PATH=$HOME/{NVM}/v22.23.3/bin:$PATH npm install -g @fission-ai/openspec@{version}"
    return entry("openspec", version, stand_in_sha(version), _form(line, sandbox, form))


def doctor_tools(tmp_path, sandbox, monkeypatch, entries: list[str]):
    """``gov doctor --json`` on a small committed repository holding a registry of ``entries``, with the case's
    stand-in ``node`` (another version) first on the ``PATH``. Returns ``(run, {name: entry})`` of the ``tools``
    part."""
    write_stand_in(sandbox.bin / "node", PATH_NODE_VERSION)
    run = base.doctor(tmp_path, sandbox, monkeypatch, "--json", registry="\n".join(entries))
    env = base.envelope(run)
    found = env.get("result") if env.get("ok") is True else (env.get("error") or {}).get("details")
    part = (found or {}).get("tools") if isinstance(found, dict) else None
    assert isinstance(part, dict), f"gov doctor reported no tools part\n{run.describe()}"
    return run, {item.get("name"): item for item in part.get("tools", []) if isinstance(item, dict)}


def tool(run, tools: dict, name: str) -> dict:
    assert name in tools, f"doctor's tools part has no entry for {name}: {sorted(tools)}\n{run.describe()}"
    return tools[name]


def number(entry_: dict) -> str | None:
    found = entry_.get("found_version")
    return None if found is None else str(found).lstrip("v")
