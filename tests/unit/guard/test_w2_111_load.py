"""Builder tests for W2-111 r5 (DEC-1187, S9): a call pays only for the YAML and the imports it needs.

The duplicate-key loader parses through libyaml's CSafeLoader when it is installed and gives the pure-Python loader's
answer, refusal and text; the held-out list and the evaluation sets are parsed at most once per process for the same
text (a changed file is parsed again; nothing is kept on disk); a call that needs neither parses neither; the read
rules import the shell parser only for a Bash call. Regression evidence only (DEC-136).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard import heldout  # noqa: E402
from gov.guard.decide import decide  # noqa: E402
from gov.util import parts  # noqa: E402

HELD = "held_out_paths:\n- /nowhere/held-out-a\n- /nowhere/held-out-b/\n"
SETS = """roles: {}
evaluation_sets:
  bench:
    visible:
    - eval/bench/visible/**
    hidden:
    - eval/bench/hidden/**
    measures:
      roles: [engineer]
"""
TICKET = """---
id: DAEO-zz91
status: in_progress
wbs_id: W1-91
role: engineer
allowed_paths:
- src/**
---
# W1-91
"""
SAMPLES = [
    "a: 1\nb: [1, 2, {c: d}]\n",
    "base: &b {x: 1, y: [a, b]}\nderived:\n  <<: *b\n  y: [c]\n",
    "when: 2026-11-15\nstamp: 2026-11-15T18:42:21Z\nnum: 0o17\nf: 1.5e3\nn: ~\nt: yes\n",
    "text: |\n  two lines\n  here\nfolded: >\n  one\n  line\nq: 'it''s'\ndq: \"tab\\there\"\n",
    "- just\n- a\n- list\n",
    "",
    "# only a comment\n",
    "key with spaces: value: with colon\n",
    "unicode: \u00e9\u00e8 \u2603\nemoji: \"\\U0001F600\"\n",
]
BROKEN = ["a: 1\na: 2\n", "a: [1, 2\n", "a: b: c\n", "x:\n  - 1\n - 2\n", "k: {a: 1, a: 2}\n", "\t- tab\n"]


def python_loader(stream):
    """The loader before W2-111 r5: the pure-Python SafeLoader with the duplicate-key check."""
    class Loader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            mapping = super().construct_mapping(node, deep=deep)
            if len(mapping) != len(node.value):
                raise yaml.constructor.ConstructorError(None, None, "a key is written twice", node.start_mark)
            return mapping
    return yaml.load(stream, Loader=Loader)


def outcome(load, text):
    try:
        return "ok", load(text)
    except Exception as exc:
        return type(exc).__name__, str(exc)


@pytest.fixture
def parses(monkeypatch):
    """Every yaml.load of the process: (the kind of text, the Loader class)."""
    seen = []
    real = yaml.load

    def load(stream, Loader=None):
        text = stream if isinstance(stream, str) else str(getattr(stream, "name", ""))
        kind = ("held-out" if "held_out_paths" in text or text.endswith("held-out.yaml") else "parts" if "evaluation_sets" in text
                else "ticket" if "wbs_id" in text else "other")
        seen.append((kind, Loader))
        return real(stream, Loader=Loader)
    monkeypatch.setattr(yaml, "load", load)
    return seen


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "proj"
    for rel, text in {"governance/project/held-out.yaml": HELD, "governance/project/path-map.yaml": SETS,
                      ".tickets/DAEO-zz91.md": TICKET, "src/a.py": "x = 1\n", "README.md": "r\n"}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return root


# -- the loader --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text", SAMPLES)
def test_the_loader_gives_the_python_loaders_data(text):
    assert outcome(parts.load_yaml_unique, text) == outcome(python_loader, text)


@pytest.mark.parametrize("text", BROKEN)
def test_a_broken_text_is_refused_with_the_python_loaders_error_and_text(text):
    got, want = outcome(parts.load_yaml_unique, text), outcome(python_loader, text)
    assert got[0] != "ok" and got == want


def test_a_stream_is_read_as_its_text(tmp_path):
    f = tmp_path / "x.yaml"
    f.write_text(SAMPLES[2])
    with open(f, encoding="utf-8") as s:
        assert parts.load_yaml_unique(s) == python_loader(SAMPLES[2])


@pytest.mark.skipif(not hasattr(yaml, "CSafeLoader"), reason="libyaml is not installed")
def test_the_loader_parses_through_libyaml_when_it_is_installed(parses):
    parts.load_yaml_unique("a: 1\n")
    assert parses and all(issubclass(loader, yaml.CSafeLoader) for _kind, loader in parses)


# -- the held-out list -----------------------------------------------------------------------------------------

def test_the_held_out_list_is_parsed_once_for_the_same_text(project, parses):
    for _ in range(3):
        assert heldout.load_held_out(str(project)) == ["/nowhere/held-out-a", "/nowhere/held-out-b"]
    assert [k for k, _l in parses].count("held-out") == 1


def test_a_changed_held_out_file_is_parsed_again(project, parses):
    heldout.load_held_out(str(project))
    (project / "governance/project/held-out.yaml").write_text(HELD + "- /nowhere/held-out-c\n")
    assert heldout.load_held_out(str(project))[-1] == "/nowhere/held-out-c"
    assert [k for k, _l in parses].count("held-out") == 2


def test_a_caller_that_changes_the_held_out_list_does_not_change_the_next_answer(project):
    heldout.load_held_out(str(project)).append("/elsewhere")
    assert heldout.load_held_out(str(project)) == ["/nowhere/held-out-a", "/nowhere/held-out-b"]


@pytest.mark.parametrize("text", ["held_out_paths:\n- /a\n- /b\nheld_out_paths: []\n", "held_out_paths: [\n",
                                  "held_out_paths: relative\n", "other: 1\n"])
def test_a_broken_held_out_file_refuses_every_time_with_the_same_text(project, text):
    (project / "governance/project/held-out.yaml").write_text(text)
    msgs = []
    for _ in range(2):
        with pytest.raises(heldout.HeldOutError) as e:
            heldout.load_held_out(str(project))
        msgs.append(str(e.value))
    assert msgs[0] == msgs[1] and "governance/project/held-out.yaml" in msgs[0]


# -- the evaluation sets -----------------------------------------------------------------------------------------

def test_the_evaluation_sets_are_parsed_once_for_the_same_text(project, parses):
    for _ in range(3):
        assert set(parts.evaluation_sets(str(project))) == {"bench"}
    assert [k for k, _l in parses].count("parts") == 1


def test_a_changed_path_map_is_parsed_again(project, parses):
    parts.evaluation_sets(str(project))
    (project / "governance/project/path-map.yaml").write_text(SETS.replace("bench", "other"))
    assert set(parts.evaluation_sets(str(project))) == {"other"}
    assert [k for k, _l in parses].count("parts") == 2


def test_a_caller_that_changes_the_sets_does_not_change_the_next_answer(project):
    parts.evaluation_sets(str(project))["bench"]["hidden"].clear()
    assert parts.evaluation_sets(str(project))["bench"]["hidden"] == ["eval/bench/hidden/**"]


def test_a_path_map_with_a_key_written_twice_refuses_every_time(project):
    (project / "governance/project/path-map.yaml").write_text(SETS + "  bench:\n    hidden: [x]\n")
    for _ in range(2):
        with pytest.raises(parts.PolicyError):
            parts.evaluation_sets(str(project))


# -- the calls ---------------------------------------------------------------------------------------------------

def test_a_write_call_parses_the_held_out_list_once_and_never_the_evaluation_sets(project, parses):
    for _ in range(3):
        decide("Write", {"file_path": str(project / "src/a.py"), "content": "y\n"}, str(project), "engineer",
               "DAEO-zz91", None, str(project))
    kinds = [k for k, _l in parses]
    assert kinds.count("held-out") == 1 and kinds.count("parts") == 0


def test_a_read_call_parses_the_evaluation_sets_at_most_once(project, parses):
    for _ in range(3):
        assert decide("Read", {"file_path": str(project / "README.md")}, str(project), "engineer", "DAEO-zz91",
                      None, str(project))[0] == "allow"
    kinds = [k for k, _l in parses]
    assert kinds.count("held-out") == 1 and kinds.count("parts") == 1


def test_a_read_of_the_hidden_part_is_still_refused_after_the_parse_is_kept(project):
    hidden = project / "eval/bench/hidden/q.txt"
    hidden.parent.mkdir(parents=True)
    hidden.write_text("q\n")
    for _ in range(2):
        assert decide("Read", {"file_path": str(hidden)}, str(project), "engineer", "DAEO-zz91", None,
                      str(project))[0] == "deny"


def test_a_call_refused_before_the_held_out_rule_parses_no_yaml(project, parses):
    assert decide("Bash", {"command": "ls", "dangerouslyDisableSandbox": True}, str(project), "engineer",
                  "DAEO-zz91", None, str(project))[0] == "deny"
    assert decide("Read", {"file_path": "x\0y"}, str(project), "engineer", "DAEO-zz91", None,
                  str(project))[0] == "deny"
    assert parses == []


def test_the_read_rules_import_the_shell_parser_only_for_a_bash_call():
    code = ("import sys; import gov.guard.reads, gov.guard.heldout, gov.guard.decide; "
            "print(json.dumps(sorted(m for m in ('gov.guard.bash_writes', 'yaml') if m in sys.modules)))")
    out = subprocess.run([sys.executable, "-c", "import json; " + code], capture_output=True, text=True,
                         env={**os.environ, "PYTHONPATH": str(REPO / "src")}, check=True).stdout
    assert json.loads(out) == []
