"""Support for W2-111's F1 (rv-3) as a described behaviour (DEC-136, DEC-802): the guard's YAML loader answers every
text as the pure-Python ``yaml.SafeLoader`` does; standard library and PyYAML only.

The behaviour (brief td-7, P-W2-111-R5-ROWS (a)): the guard reads ``held-out.yaml`` (and the path map's blocks) with a
loader that refuses a key written twice. A text the pure ``yaml.SafeLoader`` refuses must still be refused, and a text
it reads must be read to the same data, whatever faster parser is used. The classes rv-3 found, where libyaml's parser
is more lenient than the pure one: a tab inside or after a plain value and after ``key:``, a ``? `` inside a flow item,
and a byte order mark after the start of the text. A held-out entry so written must never stop protecting its folder
where the pure loader's refusal used to stop every call (DEC-218).

Two interfaces:

- **The product's loader**, ``gov.util.parts.load_yaml_unique(stream)`` (``gov.guard.heldout.load_yaml_unique`` is the
  same name): its answer (the data, or the exception's type and text) must equal ``pure_answer``'s, ``yaml.load`` with
  ``PureUnique`` below, given the same text, or the same file opened the way the guard opens ``held-out.yaml``.
- **The live hook's copy**: the engineer's diff applied to a clean copy of ``.claude/hooks/``
  (``w2_111_live_hook.make_copies``; the diff is used by its path at run time and never opened here). The applied
  (before) copy and the patched (after) copy are run as processes, as ``.claude/settings.json``'s PreToolUse command
  runs them (the pinned interpreter, ``-E``), on a **planted project**: ``CLAUDE_PROJECT_DIR`` and the working folder a
  temporary git repository whose ``governance/project/held-out.yaml`` is the text under test; the call log in the
  temporary folder. For each text, a Read of a planted file under the folder the entry names and a Read of an ordinary
  file of the project must be decided alike by both copies. The before copy reads ``held-out.yaml`` through the pinned
  gov's pure loader.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

import w2_111_live_hook as live
from w2_111_support import guard

HELD_OUT_REL = "governance/project/held-out.yaml"
PLANTED_NAME = "notes.txt"
ORDINARY_REL = "docs/guide.md"


class PureUnique(yaml.SafeLoader):
    """The pure loader the guard's answers are judged against: ``yaml.SafeLoader`` (pure Python), refusing a mapping
    whose length differs from its node's (a key written twice)."""

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        if len(mapping) != len(node.value):
            raise yaml.constructor.ConstructorError(None, None, "a key is written twice", node.start_mark)
        return mapping


def answer_of(load, source):
    """A loader's answer: ("data", the value) or ("refused", the exception's qualified type, its text)."""
    try:
        return ("data", load(source))
    except Exception as exc:  # the answer is the exception itself
        return ("refused", f"{type(exc).__module__}.{type(exc).__qualname__}", str(exc))


def pure_load(source):
    """``yaml.load`` with the pure loader."""
    return yaml.load(source, Loader=PureUnique)


def pure_answer(source):
    return answer_of(pure_load, source)


# --------------------------------------------------------------------------------------------------------------------
# The texts, each under held_out_paths:. ``{p}`` is the absolute folder the planted material lies under. ``named`` is
# the folder a lenient parser reads the entry as (where the planted file is put); ``refused`` says whether the pure
# loader refuses the text (asserted by the fixture case, so the fixture is sound).
# --------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Text:
    id: str
    template: str
    named: str        # relative to {p}
    refused: bool

    def text(self, p):
        return self.template.format(p=p)


TEXTS = [
    Text("tab-inside-an-entry", "held_out_paths:\n- {p}/held\tmat\n", "held\tmat", True),
    Text("tab-after-an-entry", "held_out_paths:\n- {p}/held\t\n", "held", True),
    Text("tab-after-the-key", "held_out_paths:\t\n- {p}/held\n", "held", True),
    Text("question-in-a-flow-item", "held_out_paths: [{p}/held? mat]\n", "held? mat", True),
    Text("bom-after-a-line-break", "held_out_paths:\n﻿- {p}/held\n", "held", True),
    Text("key-written-twice", "held_out_paths:\n- {p}/held\nheld_out_paths:\n- {p}/other\n", "held", True),
    Text("clean-control", "held_out_paths:\n- {p}/held\n", "held", False),
]
TEXT_IDS = [t.id for t in TEXTS]
REFUSED_BY_CLASS = ("tab-inside-an-entry", "tab-after-an-entry", "tab-after-the-key", "question-in-a-flow-item",
                    "bom-after-a-line-break")
CLEAN = "clean-control"


def write_exact(path, text):
    """The text's bytes as UTF-8, exactly (no newline translation, a BOM kept where it stands)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


# --------------------------------------------------------------------------------------------------------------------
# The planted project and one call of a live-hook copy
# --------------------------------------------------------------------------------------------------------------------

@dataclass
class Planted:
    project: Path
    material: Path     # {p}
    planted: Path      # the planted file under the folder the entry names
    ordinary: Path     # an ordinary file of the project


def plant_project(base, text):
    """A temporary git repository whose held-out.yaml is ``text``'s, the planted file under the folder its entry
    names (outside the project), and an ordinary file in the project."""
    base = Path(base)
    project = base / "project"
    material = base / "material"
    planted = material / text.named / PLANTED_NAME
    planted.parent.mkdir(parents=True, exist_ok=True)
    planted.write_text("W2-111 planted material\n", encoding="utf-8")
    ordinary = project / ORDINARY_REL
    ordinary.parent.mkdir(parents=True, exist_ok=True)
    ordinary.write_text("# an ordinary file\n", encoding="utf-8")
    (project / "README.md").write_text("# W2-111 planted project\n", encoding="utf-8")
    write_exact(project / HELD_OUT_REL, text.text(str(material)))
    guard.git(project, "init", "-q", "-b", "main")
    guard.git(project, "add", "-A")
    guard.git(project, "commit", "-q", "-m", "W2-111 planted project")
    return Planted(project, material, planted, ordinary)


def run_copy(interpreter, hook, project, scratch, file_path):
    """One Read of ``file_path`` by ``hook`` (a copy's pretooluse.py), as settings.json's command runs it, no role
    set; (decision, what the hook said)."""
    scratch = Path(scratch)
    (scratch / "tmp").mkdir(parents=True, exist_ok=True)
    (scratch / "calls").mkdir(parents=True, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
           "HOME": os.environ.get("HOME", str(scratch)), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC",
           "TMPDIR": str(scratch / "tmp"), "CLAUDE_PROJECT_DIR": str(project), "PYTHONDONTWRITEBYTECODE": "1",
           "GOV_GUARD_CALLS_DIR": str(scratch / "calls")}
    payload = json.dumps({"session_id": "w2-111-yaml-parity", "cwd": str(project), "hook_event_name": "PreToolUse",
                          "tool_name": "Read", "tool_input": {"file_path": str(file_path)},
                          "permission_mode": "default", "tool_use_id": "toolu_w2_111_yaml_parity"})
    proc = subprocess.run(["sh", "-c", '"$0" -E "$1"', interpreter, str(hook)], input=payload, capture_output=True,
                          text=True, cwd=str(project), env=env, timeout=60, check=False)
    return guard.classify(proc.returncode, proc.stdout), (proc.stderr or proc.stdout).strip()[:300]


def make_live(base):
    """The before and after copies and the pinned interpreter; ``live.LiveHookUnavailable`` names what is missing."""
    copies = live.make_copies(Path(base) / "copies")
    return copies, live.pinned_interpreter()
