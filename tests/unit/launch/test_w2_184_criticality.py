"""W2-184 builder tests: ``governance/project/criticality.yaml`` and ``gov.launch.criticality`` (interface 1).

Regression evidence only (DEC-136): the file's form, the ticket's class by profile and allowed paths, the refusals.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import criticality  # noqa: E402

FILE = """version: 1
default: C2
opus: claude-opus-5-5
rules:
  - class: C3
    paths: [".claude/hooks/*", "src/gov/guard/*"]
  - class: C1
    paths: ["docs/*"]
  - class: C0
    paths: ["notes/*"]
  - class: C2
    profile: FULL
"""


def _write(root: Path, text: str) -> Path:
    path = root / criticality.REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return root


def _ticket(profile="STANDARD", *paths):
    return {"profile": profile, "allowed_paths": list(paths), "class": "implementation"}


@pytest.mark.parametrize("ticket, expected", (
    (_ticket("STANDARD", "src/gov/guard/x.py"), "C3"),
    (_ticket("STANDARD", ".claude/hooks/pretooluse.py"), "C3"),
    (_ticket("STANDARD", "docs/a.md"), "C1"),
    (_ticket("STANDARD", "notes/a.md"), "C0"),
    (_ticket("STANDARD", "elsewhere/a.py"), "C2"),  # the default
    (_ticket("LITE"), "C2"),
    (_ticket("FULL", "notes/a.md"), "C2"),  # the highest of C0 and the FULL rule's C2
    (_ticket("FULL", "docs/a.md"), "C2"),
    (_ticket("FULL", "src/gov/guard/a.py", "docs/a.md"), "C3"),
    (_ticket("STANDARD", "docs/a.md", "notes/a.md"), "C1"),
))
def test_the_ticket_s_class_is_the_highest_of_the_rules_that_match(tmp_path, ticket, expected):
    assert criticality.ticket_criticality(_write(tmp_path, FILE), ticket) == expected


def test_the_default_is_the_class_when_no_rule_matches(tmp_path):
    text = FILE.replace("default: C2", "default: C1")
    assert criticality.ticket_criticality(_write(tmp_path, text), _ticket("STANDARD", "zzz/a")) == "C1"


def test_a_trailing_inline_comment_of_an_allowed_path_is_dropped(tmp_path):
    ticket = _ticket("STANDARD", "docs/probes/T/**  # the probe record")
    assert criticality.ticket_criticality(_write(tmp_path, FILE), ticket) == "C1"


def test_the_comment_tail_matters_where_the_rule_names_the_path_exactly(tmp_path):
    text = FILE.replace('paths: ["docs/*"]', 'paths: ["docs/exact.md"]')
    assert criticality.ticket_criticality(_write(tmp_path, text), _ticket("STANDARD", "docs/exact.md  # a note")) == "C1"
    assert criticality.ticket_criticality(_write(tmp_path, text), _ticket("STANDARD", "docs/other.md  # a note")) == "C2"


def test_a_broad_allowed_path_matches_a_narrower_rule_glob(tmp_path):
    assert criticality.ticket_criticality(_write(tmp_path, FILE), _ticket("STANDARD", "src/**")) == "C3"


def test_a_star_crosses_a_slash(tmp_path):
    assert criticality.ticket_criticality(_write(tmp_path, FILE), _ticket("STANDARD", "docs/a/b/c.md")) == "C1"


def test_the_ticket_s_class_key_is_never_read(tmp_path):
    ticket = {"profile": "STANDARD", "allowed_paths": ["elsewhere/a"], "class": "C3"}
    assert criticality.ticket_criticality(_write(tmp_path, FILE), ticket) == "C2"


@pytest.mark.parametrize("ticket", ({}, {"allowed_paths": None}, {"allowed_paths": "docs/a.md"},
                                    {"allowed_paths": [None, 3]}))
def test_a_ticket_without_a_list_of_paths_has_no_path_match(tmp_path, ticket):
    assert criticality.ticket_criticality(_write(tmp_path, FILE), ticket) == "C2"


def test_the_opus_model_is_the_file_s(tmp_path):
    assert criticality.opus_model(_write(tmp_path, FILE)) == "claude-opus-5-5"


def test_the_file_is_read_at_each_call(tmp_path):
    _write(tmp_path, FILE)
    assert criticality.opus_model(tmp_path) == "claude-opus-5-5"
    _write(tmp_path, FILE.replace("claude-opus-5-5", "claude-opus-6-0"))
    assert criticality.opus_model(tmp_path) == "claude-opus-6-0"


def test_a_missing_file_refuses_naming_it(tmp_path):
    with pytest.raises(GovError, match="governance/project/criticality.yaml") as caught:
        criticality.ticket_criticality(tmp_path, _ticket())
    assert caught.value.code == "LAUNCH_REFUSED"
    with pytest.raises(GovError, match="governance/project/criticality.yaml"):
        criticality.opus_model(tmp_path)


GOOD = {"version": 1, "default": "C2", "opus": "claude-opus-5-5", "rules": []}


def _yaml(**change):
    import yaml
    data = {**GOOD, **change}
    return yaml.safe_dump({k: v for k, v in data.items() if v is not ...})


@pytest.mark.parametrize("text", (
    "",
    "- a\n- b\n",
    "version: 1\n  bad: [\n",
    "version: 1\nversion: 1\ndefault: C2\nopus: claude-opus-5-5\nrules: []\n",  # a key written twice
    _yaml(version=2),
    _yaml(version="1"),
    _yaml(version=True),
    _yaml(default="C4"),
    _yaml(default="c2"),
    _yaml(opus="claude-sonnet-5-5"),
    _yaml(opus="claude-opus"),
    _yaml(opus="Claude-Opus-5-5"),
    _yaml(rules=...),
    _yaml(rules={"class": "C3"}),
    _yaml(rules=["C3"]),
    _yaml(rules=[{"class": "C3"}]),  # neither paths nor profile
    _yaml(rules=[{"class": "C3", "paths": ["a"], "profile": "FULL"}]),  # both
    _yaml(rules=[{"class": "C9", "paths": ["a"]}]),
    _yaml(rules=[{"class": "C3", "paths": []}]),
    _yaml(rules=[{"class": "C3", "paths": [""]}]),
    _yaml(rules=[{"class": "C3", "paths": "a"}]),
    _yaml(rules=[{"class": "C3", "paths": [1]}]),
    _yaml(rules=[{"class": "C3", "profile": "HUGE"}]),
    _yaml(rules=[{"class": "C3", "paths": ["a"], "note": "x"}]),
    _yaml(extra=1),
))
def test_a_malformed_file_refuses(tmp_path, text):
    with pytest.raises(GovError, match="governance/project/criticality.yaml") as caught:
        criticality.opus_model(_write(tmp_path, text))
    assert caught.value.code == "LAUNCH_REFUSED"


def test_a_file_with_no_rules_is_well_formed(tmp_path):
    assert criticality.ticket_criticality(_write(tmp_path, _yaml()), _ticket("FULL", "src/a")) == "C2"


def test_the_project_s_own_file_is_well_formed_and_places_this_ticket_at_c2():
    from gov.util.tickets import _load_ticket
    assert criticality.opus_model(REPO).startswith("claude-opus")
    ticket = _load_ticket(str(REPO), "DAEO-6f0s")
    if ticket is None:  # the ticket lives in the main checkout's .tickets
        ticket = {"profile": "FULL", "allowed_paths": ["src/gov/launch/launcher.py"]}
    assert criticality.ticket_criticality(REPO, ticket) == "C2"


@pytest.mark.parametrize("paths, expected", (
    (["src/gov/guard/decide.py"], "C3"), ([".claude/hooks/pretooluse.py"], "C3"),
    (["governance/project/path-map.yaml"], "C3"), (["governance/project/operator/x.md"], "C3"),
    (["template/governance/kernel/roles/x.md"], "C3"), (["governance/kernel/x.md"], "C3"),
    (["docs/contract/x.md"], "C3"),
    # F1: hidden sets (the path map's hidden halves); F8: permissions beside .claude/settings.json and held-out.yaml
    (["fixtures/evaluation/examin/hidden/**"], "C3"),
    (["fixtures/evaluation/adoption-proving-ground/hidden/cases/a.json"], "C3"),
    (["fixtures/evaluation/**"], "C3"),  # a broad path over the hidden halves is C3 as well
    ([".claude/settings.json"], "C3"), ([".claude/settings.local.json"], "C3"),
    (["governance/project/secrets.yaml"], "C3"), (["governance/project/held-out.yaml"], "C3"),
    (["governance/project/indep-walls/**"], "C3"), (["governance/project/indep-walls/W2-1.yaml"], "C3"),
    (["fixtures/evaluation/examin/visible/**"], "C2"),  # a visible half is no hidden set: the default
    (["src/gov/launch/launcher.py"], "C2"), (["governance/project/test-map.yaml"], "C2"),
    (["docs/changes/x.md"], "C1"), (["governance/project/orchestration/x.md"], "C1"),
))
def test_the_project_s_own_rules_place_the_named_paths(paths, expected):
    assert criticality.ticket_criticality(REPO, {"profile": "STANDARD", "allowed_paths": paths}) == expected


@pytest.mark.parametrize("profile", ("STANDARD", "FULL", "LITE"))
@pytest.mark.parametrize("path", ("fixtures/evaluation/examin/hidden/**", "governance/project/secrets.yaml",
                                  ".claude/settings.local.json", "governance/project/indep-walls/**"))
def test_a_hidden_set_or_permission_ticket_stays_c3_beside_a_probe_record_path_with_its_comment(profile, path):  # F1, F8
    ticket = {"profile": profile, "allowed_paths": [path, "docs/probes/DAEO-xxxx/**  # the probe record"]}
    assert criticality.ticket_criticality(REPO, ticket) == "C3"
