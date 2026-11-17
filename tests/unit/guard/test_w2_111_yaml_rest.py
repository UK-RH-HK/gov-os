"""Builder tests for W2-111 r5 (P-W2-111-YAML-REST (a), P-W2-111-YAML-REST-FRONT (a)): the guard's other YAML reads.

The path map's ``role_paths:`` block and the session ticket's front matter are parsed by libyaml's CSafeLoader only for
a text ``gov.util.parts.libyaml_reads_as_python`` passes (no tab, no ``?``, no BOM after the start); any other text,
and any libyaml error, goes to the pure-Python SafeLoader (rv-3 F1's fail-open class). Five reads: ``role_paths.section``,
``role_paths.ticket_front``, ``parts._front`` and the live hook's ``role_reads.section`` and ``role_reads.ticket_front``
(in docs/changes/W2-111-live-hook/live-hook.diff). A block the pure loader refuses is refused; front matter it refuses
refuses the call (fail closed: an empty front would hand a test designer the engineer's code); a clean text is read as
before. Regression evidence only (DEC-136).
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import decide  # noqa: E402
from gov.util import parts, role_paths  # noqa: E402

E, TD = "engineer", "independent-test-designer"
PATH_MAP = "governance/project/path-map.yaml"

BLOCK = """role_paths:
  engineer:
    reads_denied:
    - "{ticket_tests}"
    - docs/private/**
  independent-test-designer:
    reads_denied: ["{ticket_impl}"]
"""
# Each one libyaml reads and the pure SafeLoader refuses (rv-3 F1), planted in the block.
BLOCKS = {
    "tab-inside-an-entry": BLOCK.replace("    - docs/private/**\n", "    - docs/private\t/**\n"),
    "tab-after-an-entry": BLOCK.replace("    - docs/private/**\n", "    - docs/private/**\t\n"),
    "tab-after-the-key": BLOCK.replace("  engineer:\n    reads_denied:\n", "  engineer:\n    reads_denied:\t\n"),
    "question-in-a-flow-item": BLOCK.replace('["{ticket_impl}"]', '["{ticket_impl}", docs/a? b]'),
}

FRONT = """id: DAEO-zz91
status: in_progress
wbs_id: W1-91
role: engineer
allowed_paths:
- src/app/new.py
- docs/changes/W1-91-evidence.md
"""
FRONTS = {
    "tab-inside-an-entry": FRONT.replace("- src/app/new.py\n", "- src/app\t/new.py\n"),
    "tab-after-an-entry": FRONT.replace("- src/app/new.py\n", "- src/app/new.py\t\n"),
    "tab-after-the-key": FRONT.replace("allowed_paths:\n", "allowed_paths:\t\n"),
    "question-in-a-flow-item": FRONT.replace("allowed_paths:\n- src/app/new.py\n- docs/changes/W1-91-evidence.md\n",
                                             "allowed_paths: [src/app/new.py? x, docs/changes/W1-91-evidence.md]\n"),
    "bom-after-a-line-break": FRONT.replace("role: engineer\n", "role: engineer\n﻿# a note\n"),
}


def outcome(fn, *args):
    try:
        return "ok", fn(*args)
    except Exception as exc:
        return type(exc).__name__, str(exc)


@pytest.fixture
def pure(monkeypatch):
    """libyaml absent: every parse is the pure-Python SafeLoader's."""
    def off():
        if hasattr(yaml, "CSafeLoader"):
            monkeypatch.delattr(yaml, "CSafeLoader")
    return off


def ticket_text(front):
    return "---\n" + front + "---\n# W1-91\n"


def plant(root: Path, block=BLOCK, front=FRONT) -> str:
    files = {PATH_MAP: "state_class: AUTHORITATIVE\n" + block, "governance/project/held-out.yaml":
             "held_out_paths:\n- /nowhere/held-out\n", ".tickets/DAEO-zz91.md": ticket_text(front),
             "docs/notes.md": "n\n", "src/app/new.py": "x = 1\n", "README.md": "r\n"}
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    return os.path.realpath(root)


def test_the_planted_texts_are_ones_libyaml_reads_and_the_pure_loader_refuses():
    for text in [*BLOCKS.values(), *FRONTS.values()]:
        assert not parts.libyaml_reads_as_python(text)
        with pytest.raises(yaml.YAMLError):
            yaml.load(text, Loader=yaml.SafeLoader)
    if hasattr(yaml, "CSafeLoader"):  # the fail-open these reads had: libyaml answered
        for text in [*BLOCKS.values(), *FRONTS.values()]:
            assert isinstance(yaml.load(text, Loader=yaml.CSafeLoader), dict)


# -- the checked loader ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text", [BLOCK, FRONT, "", "# c\n", "a: [1, 2]\nb: {c: d}\n", "a: 1\na: 2\n", "- x\n"])
def test_the_checked_loader_gives_yaml_safe_loads_answer_for_a_clean_text(text):
    assert outcome(parts.load_yaml, text) == outcome(yaml.load, text, yaml.SafeLoader)


@pytest.mark.parametrize("text", [*BLOCKS.values(), *FRONTS.values(), "a: [1, 2\n", "a: b: c\n"])
def test_the_checked_loader_refuses_as_the_pure_loader_refuses(text):
    got = outcome(parts.load_yaml, text)
    assert got[0] != "ok" and got == outcome(yaml.load, text, yaml.SafeLoader)


@pytest.mark.skipif(not hasattr(yaml, "CSafeLoader"), reason="libyaml is not installed")
def test_the_checked_loader_parses_a_clean_text_through_libyaml(monkeypatch):
    seen = []
    real = yaml.load
    monkeypatch.setattr(yaml, "load", lambda s, Loader=None: seen.append(Loader) or real(s, Loader=Loader))
    parts.load_yaml(FRONT)
    assert seen == [yaml.CSafeLoader]


# -- role_paths.section: the path map's role_paths: block ------------------------------------------------------------

@pytest.mark.parametrize("name", BLOCKS)
def test_a_block_the_pure_loader_refuses_is_refused(tmp_path, pure, name):
    root = plant(tmp_path, block=BLOCKS[name])
    got = outcome(role_paths.section, root)
    assert got == ("RolePathsError", f"{PATH_MAP}: role_paths cannot be read")
    pure()
    assert outcome(role_paths.section, root) == got


def test_a_clean_block_is_read_as_before(tmp_path):
    root = plant(tmp_path)
    assert role_paths.section(root) == yaml.safe_load(BLOCK)["role_paths"]


@pytest.mark.parametrize("name", BLOCKS)
def test_the_engineers_filter_is_refused_for_a_block_the_pure_loader_refuses(tmp_path, monkeypatch, name):
    root = plant(tmp_path, block=BLOCKS[name])
    monkeypatch.setenv("GOV_ROLE", E)
    with pytest.raises(role_paths.RolePathsError):
        role_paths.caller(root, ticket="DAEO-zz91", main=root, links=lambda *a: set())


# -- role_paths.ticket_front: the session ticket's front matter ------------------------------------------------------

@pytest.mark.parametrize("name", FRONTS)
def test_front_matter_the_pure_loader_refuses_refuses(tmp_path, pure, name):
    root = plant(tmp_path, front=FRONTS[name])
    with pytest.raises(role_paths.RolePathsError):
        role_paths.ticket_front(root, "DAEO-zz91")
    with pytest.raises(role_paths.RolePathsError):
        role_paths.ticket_front(root, "W1-91")  # found by its wbs_id line
    pure()
    with pytest.raises(role_paths.RolePathsError):
        role_paths.ticket_front(root, "DAEO-zz91")


def test_clean_front_matter_is_read_as_before(tmp_path):
    root = plant(tmp_path)
    assert role_paths.ticket_front(root, "DAEO-zz91") == yaml.safe_load(FRONT)
    assert role_paths.ticket_front(root, "W1-91") == yaml.safe_load(FRONT)


@pytest.mark.parametrize("front", ["", "# only a comment\n"])
def test_empty_front_matter_is_still_no_front(tmp_path, front):
    root = plant(tmp_path, front=front)
    assert role_paths.ticket_front(root, "DAEO-zz91") == {}


def test_no_ticket_is_still_no_front(tmp_path):
    root = plant(tmp_path)
    assert role_paths.ticket_front(root, "DAEO-none") == {}
    assert role_paths.ticket_front(root, None) == {}


@pytest.mark.parametrize("role", [TD, E])
@pytest.mark.parametrize("name", FRONTS)
def test_the_filter_is_refused_for_front_matter_the_pure_loader_refuses(tmp_path, monkeypatch, name, role):
    """The designer's {ticket_impl} reads the front; the engineer's {ticket_tests} reads it for its links (a malformed
    front never narrows them to the own folder)."""
    root = plant(tmp_path, front=FRONTS[name].replace("wbs_id: W1-91", "wbs_id: 'W1-91'"))
    monkeypatch.setenv("GOV_ROLE", role)
    with pytest.raises(role_paths.RolePathsError):
        role_paths.caller(root, ticket="DAEO-zz91", main=root)


@pytest.mark.parametrize("role", [TD, E])
def test_the_filter_is_made_for_clean_front_matter(tmp_path, monkeypatch, role):
    root = plant(tmp_path)
    monkeypatch.setenv("GOV_ROLE", role)
    found = role_paths.caller(root, ticket="DAEO-zz91", main=root, links=lambda *a: set())
    assert found is None or isinstance(found, role_paths.Filter)


# -- parts._front: the ticket's WBS id and id, as the product hook reads them ----------------------------------------

@pytest.mark.parametrize("quote", ["", "'"])
@pytest.mark.parametrize("name", FRONTS)
def test_front_matter_the_pure_loader_refuses_is_read_as_the_pure_loader_reads_it(pure, name, quote):
    """Through the line reader, as with libyaml absent: a plain wbs_id is given, a quoted one refuses."""
    text = ticket_text(FRONTS[name].replace("wbs_id: W1-91", f"wbs_id: {quote}W1-91{quote}"))
    got = outcome(parts._front, text)
    pure()
    assert outcome(parts._front, text) == got


@pytest.mark.parametrize("name", FRONTS)
def test_a_wbs_id_the_line_reader_cannot_give_refuses_with_front_matter_the_pure_loader_refuses(name):
    text = ticket_text(FRONTS[name].replace("wbs_id: W1-91", "wbs_id: 'W1-91'"))
    assert outcome(parts._front, text) == ("PolicyError", parts._TICKET_FAULT)


def test_clean_front_matter_gives_its_ids_as_before():
    assert parts._front(ticket_text(FRONT)) == ("W1-91", "DAEO-zz91")
    assert parts._front(ticket_text(FRONT.replace("wbs_id: W1-91", "wbs_id: 'W1-91'"))) == ("W1-91", "DAEO-zz91")


@pytest.mark.parametrize("name", FRONTS)
def test_the_product_hook_refuses_the_engineers_read_for_front_matter_the_pure_loader_refuses(tmp_path, name):
    root = plant(tmp_path, block="", front=FRONTS[name].replace("wbs_id: W1-91", "wbs_id: 'W1-91'"))
    verdict, why = decide("Read", {"file_path": root + "/docs/notes.md"}, root, E, "DAEO-zz91", None, root)[:2]
    assert verdict == "deny" and parts._TICKET_FAULT in why


def test_the_product_hook_allows_the_engineers_read_for_clean_front_matter(tmp_path):
    root = plant(tmp_path, block="", front=FRONT.replace("wbs_id: W1-91", "wbs_id: 'W1-91'"))
    assert decide("Read", {"file_path": root + "/docs/notes.md"}, root, E, "DAEO-zz91", None, root)[0] == "allow"


# -- the live hook's role_reads.py, with the diff applied ------------------------------------------------------------

@pytest.fixture(scope="module")
def patched(tmp_path_factory):
    """The applied hooks (ACT-GUARD-FIX-6's bytes, this tree's .claude/hooks/) with the diff applied."""
    base = tmp_path_factory.mktemp("hook")
    (base / ".claude/hooks").mkdir(parents=True)
    for name in ("pretooluse.py", "bash_writes.py", "role_reads.py"):
        shutil.copy(REPO / ".claude/hooks" / name, base / ".claude/hooks" / name)
    diff = str(REPO / "docs/changes/W2-111-live-hook/live-hook.diff")
    # After ACT-GUARD-FIX-7 the tree's hooks already carry the diff (DEC-1198 (6), DEC-1156 (7)): used as they are.
    if subprocess.run(["git", "apply", "--reverse", "--check", diff], cwd=base, capture_output=True).returncode:
        subprocess.run(["git", "apply", diff], cwd=base, check=True, capture_output=True)
    return base / ".claude/hooks"


@pytest.fixture(scope="module")
def role_reads(patched):
    spec = importlib.util.spec_from_file_location("w2_111_patched_role_reads", patched / "role_reads.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name", BLOCKS)
def test_the_live_hooks_block_the_pure_loader_refuses_is_refused(tmp_path, role_reads, name):
    root = plant(tmp_path, block=BLOCKS[name])
    assert outcome(role_reads.section, root) == ("ValueError", f"{PATH_MAP}: role_paths cannot be read")


def test_the_live_hooks_clean_block_is_read_as_before(tmp_path, role_reads):
    root = plant(tmp_path)
    assert role_reads.section(root) == yaml.safe_load(BLOCK)["role_paths"]


@pytest.mark.parametrize("name", FRONTS)
def test_the_live_hooks_front_matter_the_pure_loader_refuses_refuses_with_a_named_reason(tmp_path, role_reads, name):
    root = plant(tmp_path, front=FRONTS[name])
    got = outcome(role_reads.ticket_front, root, "DAEO-zz91")
    assert got[0] == "ValueError" and got[1].startswith("the session's ticket file cannot be read")
    assert root not in got[1]


def test_the_live_hooks_clean_front_matter_is_read_as_before(tmp_path, role_reads):
    root = plant(tmp_path)
    assert role_reads.ticket_front(root, "DAEO-zz91") == yaml.safe_load(FRONT)
    assert role_reads.ticket_front(plant(tmp_path / "e", front=""), "DAEO-zz91") == {}


@pytest.mark.parametrize("text", [*BLOCKS.values(), *FRONTS.values(), BLOCK, FRONT, "", "a: 1\na: 2\n", "a: [1\n"])
def test_the_live_hooks_loader_is_the_products_rule(role_reads, text):
    assert outcome(role_reads.load_yaml, text) == outcome(parts.load_yaml, text)


# -- the patched live hook as a process ----------------------------------------------------------------------------

def git_plant(root: Path, block=BLOCK, front=FRONT) -> str:
    at = plant(root, block=block, front=front)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x",
               GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    for args in (["init", "-q", "-b", "w2/integrate"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run(["git", "-C", at, *args], check=True, env=env, capture_output=True)
    return at


def run_hook(hooks: Path, root: str, role: str, path: str):
    event = {"tool_name": "Read", "tool_input": {"file_path": path}, "cwd": root, "session_id": "w2-111",
             "hook_event_name": "PreToolUse"}
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update(PYTHONPATH=str(REPO / "src"), GOV_ROLE=role, GOV_TICKET="DAEO-zz91", CLAUDE_PROJECT_DIR=root)
    p = subprocess.run([sys.executable, str(hooks / "pretooluse.py")], input=json.dumps(event), capture_output=True,
                       text=True, env=env, timeout=60)
    if p.returncode == 2:
        return "deny", p.stderr
    assert p.returncode == 0, p.stderr
    return ("allow", "") if not p.stdout.strip() else (
        json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"], p.stdout)


@pytest.mark.parametrize("name", BLOCKS)
def test_the_patched_hook_refuses_the_engineers_read_for_a_block_the_pure_loader_refuses(tmp_path, patched, name):
    root = git_plant(tmp_path / "p", block=BLOCKS[name])
    verdict, why = run_hook(patched, root, E, root + "/docs/notes.md")
    assert verdict == "deny" and "role_paths cannot be read" in why, why


@pytest.mark.parametrize("name", FRONTS)
def test_the_patched_hook_refuses_the_designers_read_for_front_matter_the_pure_loader_refuses(tmp_path, patched,
                                                                                               name):
    root = git_plant(tmp_path / "p", front=FRONTS[name])
    verdict, why = run_hook(patched, root, TD, root + "/docs/notes.md")
    assert verdict == "deny" and "the session's ticket file cannot be read" in why, why


@pytest.mark.parametrize("role", [E, TD])
def test_the_patched_hook_allows_an_ordinary_read_for_clean_texts(tmp_path, patched, role):
    root = git_plant(tmp_path / "p")
    assert run_hook(patched, root, role, root + "/docs/notes.md")[0] == "allow"
