"""W2-184, KPI success 1 (part 2) -- the ticket's criticality from ``governance/project/criticality.yaml``.

Interface 1: the file's form (``version`` 1, ``default``, ``opus``, ``rules``), ``ticket_criticality(root, ticket)`` (the
highest class among the matching rules, ``default`` when none matches; a ``profile`` rule matches the ticket's profile; a
``paths`` rule matches when a glob and an allowed path match either way as ``fnmatchcase`` patterns, the allowed path
having lost a trailing inline comment), ``opus_model(root)``, and when the file is read (1.3, 1.4 as amended: a file
that is present is read on every launch; with none the launch is as before W2-184).
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG = s.ENGINEER
SESSION = dict(effort_source="by criticality", model_source="by criticality")


def _engineer(project, launch, tk, cls):
    model, effort = s.TABLES[ENG][cls]
    return s.assert_session(launch(ENG, tk), model, effort, criticality=cls, **SESSION)


# --------------------------------------------------------------------------
# What the rules decide (through a launch: the record's criticality and the table line taken)
# --------------------------------------------------------------------------

def test_s1_the_default_class_applies_when_no_rule_matches(project, launch):
    s.write_criticality(project, s.crit_text(default="C1", rules=[]))
    _engineer(project, launch, s.ticket(project, ENG, "C0"), "C1")


@pytest.mark.parametrize("allowed,cls", [
    (["docs/guides/a/**", "src/critical/b/**"], "C3"), (["src/critical/b/**", "docs/guides/a/**"], "C3"),
    (["docs/guides/a/**", "src/product/b/**"], "C2"), (["notes/x/**", "docs/guides/a/**"], "C1"),
    (["notes/x/**", "notes/y/**"], "C0"),
])
def test_s1_the_ticket_takes_the_highest_class_among_the_rules_that_match(project, launch, allowed, cls):
    tk = s.ticket(project, ENG, allowed=allowed)
    _engineer(project, launch, tk, cls)


def test_s1_a_trailing_inline_comment_on_an_allowed_path_is_ignored(project, launch):
    tk = s.ticket(project, ENG, allowed=["src/critical/core/**  # the probe record"])
    _engineer(project, launch, tk, "C3")


def test_s1_a_broad_allowed_path_matches_a_narrower_rule_glob(project, launch):
    """``src/**`` read as a pattern matches the rule's glob ``src/critical/*`` as a string (interface 1.2)."""
    _engineer(project, launch, s.ticket(project, ENG, allowed=["src/**"]), "C3")


def test_s1_a_rule_glob_does_not_match_a_path_of_another_case(project, launch):
    tk = s.ticket(project, ENG, allowed=["SRC/critical/core/**"])
    _engineer(project, launch, tk, "C0")


@pytest.mark.parametrize("profile,allowed,cls", [
    ("FULL", "notes/x/**", "C2"), ("STANDARD", "notes/x/**", "C0"), ("LITE", "notes/x/**", "C0"),
    ("FULL", "src/critical/x/**", "C3"), ("FULL", "docs/guides/x/**", "C2"),
])
def test_s1_a_profile_rule_matches_the_ticket_s_profile(project, launch, profile, allowed, cls):
    s.write_criticality(project, s.crit_text(rules=[*s.RULES, {"class": "C2", "profile": "FULL"}]))
    tk = s.ticket(project, ENG, profile=profile, allowed=[allowed])
    _engineer(project, launch, tk, cls)


def test_s1_the_rules_are_read_at_each_launch(project, launch):
    tk = s.ticket(project, ENG, allowed=["notes/x/**"])
    _engineer(project, launch, tk, "C0")
    s.write_criticality(project, s.crit_text(default="C3"))
    _engineer(project, launch, tk, "C3")


def test_s1_a_criticality_file_is_read_and_recorded_for_a_role_with_only_a_default_line(project, launch):
    s.write_role(project, ENG, table=None)
    tk = s.ticket(project, ENG, "C1")
    s.assert_session(launch(ENG, tk), *s.DEFAULT, criticality="C1", model_source="role default",
                     effort_source="role default")


# --------------------------------------------------------------------------
# A missing, unreadable or malformed file refuses, when it is read (1.3, 1.4)
# --------------------------------------------------------------------------

# Rewrite-Reason: DEC-1246 (3)(b): MR-2: the file has no `opus` key; one that carries it is refused.
GOOD = {"version": 1, "default": "C2", "rules": []}


def _text(**changes):
    import yaml
    data = {**GOOD, **changes}
    for key in [key for key, value in changes.items() if value is s.MISSING]:
        del data[key]
    return yaml.safe_dump(data, sort_keys=False)


def _rule(**rule):
    return _text(rules=[rule])


BAD_FILE = {
    "not-yaml": "version: 1\ndefault: [C2\n",
    "not-a-map": "- C2\n",
    "empty": "",
    "a-key-written-twice": "version: 1\ndefault: C2\ndefault: C3\nopus: claude-opus-5-5\nrules: []\n",
    "version-2": _text(version=2),
    "version-a-string": _text(version="1"),
    "version-missing": _text(version=s.MISSING),
    "default-unknown": _text(default="C9"),
    "default-lower-case": _text(default="c2"),
    "default-missing": _text(default=s.MISSING),
    "opus-an-alias": _text(opus="opus"),
    "opus-not-an-opus-model": _text(opus=s.SONNET),
    "opus-an-opus-model": _text(opus=s.OPUS),
    "rules-missing": _text(rules=s.MISSING),
    "rules-not-a-list": _text(rules={}),
    "an-extra-top-level-key": _text(note="x"),
    "a-rule-that-is-not-a-map": _text(rules=["C3"]),
    "a-rule-with-neither-paths-nor-profile": _rule(**{"class": "C3"}),
    "a-rule-with-both-paths-and-profile": _rule(**{"class": "C3", "paths": ["src/*"], "profile": "FULL"}),
    "a-rule-class-unknown": _rule(**{"class": "C7", "paths": ["src/*"]}),
    "a-rule-without-class": _rule(paths=["src/*"]),
    "a-rule-with-an-extra-key": _rule(**{"class": "C3", "paths": ["src/*"], "note": "x"}),
    "paths-empty": _rule(**{"class": "C3", "paths": []}),
    "paths-with-an-empty-string": _rule(**{"class": "C3", "paths": [""]}),
    "paths-a-string": _rule(**{"class": "C3", "paths": "src/*"}),
    "profile-unknown": _rule(**{"class": "C3", "profile": "HUGE"}),
}


@pytest.mark.parametrize("case", sorted(BAD_FILE))
def test_s1_a_malformed_criticality_file_refuses_a_launch_that_reads_it(project, launch, case):
    s.write_criticality(project, BAD_FILE[case])
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk), s.CRITICALITY_REL)


@pytest.mark.parametrize("case", ["not-yaml", "a-key-written-twice", "a-rule-with-both-paths-and-profile",
                                  "default-unknown"])
def test_s1_a_malformed_file_refuses_even_a_role_with_only_a_default_line(project, launch, case):
    """Interface 1.4: a file that exists is read, whatever the role file says."""
    s.write_role(project, ENG, table=None)
    s.write_criticality(project, BAD_FILE[case])
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk), s.CRITICALITY_REL)


def test_s1_a_missing_criticality_file_launches_a_role_with_a_table_line_on_its_default_line(project, launch):
    """Interface 1.4 as amended (2026-11-14): no file, the launch as before W2-184. The table line is not applied.
    The earlier 1.4 refused here, naming the file."""
    s.drop_criticality(project)
    tk = s.ticket(project, ENG, "C2")
    s.assert_session(launch(ENG, tk), *s.DEFAULT, criticality=None, model_source="role default",
                     effort_source="role default")


def test_s1_an_unreadable_criticality_file_refuses(project, launch):
    s.drop_criticality(project)
    (project / s.CRITICALITY_REL).mkdir()
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk), s.CRITICALITY_REL)


def test_s1_a_missing_criticality_file_is_recorded_null_for_a_role_with_only_a_default_line(project, launch):
    s.write_role(project, ENG, table=None)
    s.drop_criticality(project)
    tk = s.ticket(project, ENG, "C2")
    s.assert_session(launch(ENG, tk), *s.DEFAULT, criticality=None, model_source="role default",
                     effort_source="role default")


# --------------------------------------------------------------------------
# gov.launch.criticality, called directly (interface 1.2): ticket_criticality(root, ticket) and opus_model(root)
# --------------------------------------------------------------------------

def _tree(tmp_path, text=None):
    root = tmp_path / "tree"
    s.b.write(root / s.CRITICALITY_REL, s.crit_text() if text is None else text)
    return root


def _front(root, tk, **kw):
    from gov.util.tickets import _load_ticket
    s.b.write(root / ".tickets" / f"{tk}.md", s.ticket_text(tk, ENG, kw.get("allowed", ["notes/x/**"]),
                                                            kw.get("profile", "STANDARD"), kw.get("kind", "implementation")))
    return _load_ticket(str(root), tk)


@pytest.mark.parametrize("allowed,profile,kind,cls", [
    (["src/critical/core/**"], "FULL", "C0", "C3"), (["src/product/app/**"], "LITE", "C3", "C2"),
    (["docs/guides/g/**"], "STANDARD", "C3", "C1"), (["notes/x/**"], "FULL", "C3", "C0"),
    (["src/**  # all of the source"], "STANDARD", "implementation", "C3"),
])
def test_s1_ticket_criticality_is_the_highest_matching_class(tmp_path, allowed, profile, kind, cls):
    from gov.launch import criticality
    root = _tree(tmp_path)
    ticket = _front(root, "DAEO-m001", allowed=allowed, profile=profile, kind=kind)
    assert criticality.ticket_criticality(root, ticket) == cls


def test_s1_the_criticality_function_reads_the_file_at_each_call(tmp_path):
    # Rewrite-Reason: DEC-1246 (3)(b): MR-2: there is no Opus model in the file to read.
    from gov.launch import criticality
    root = _tree(tmp_path)
    ticket = _front(root, "DAEO-m002")
    assert criticality.ticket_criticality(root, ticket) == "C0"
    s.write_criticality(root, s.crit_text(default="C2"))
    assert criticality.ticket_criticality(root, ticket) == "C2"


@pytest.mark.parametrize("what", ["missing", "malformed", "a-folder"])
def test_s1_the_criticality_functions_raise_launch_refused_naming_the_file(tmp_path, what):
    from gov.cli.errors import GovError
    from gov.launch import criticality
    root = _tree(tmp_path, "version: 1\ndefault: [C2\n" if what == "malformed" else None)
    ticket = _front(root, "DAEO-m003")
    if what == "missing":
        (root / s.CRITICALITY_REL).unlink()
    elif what == "a-folder":
        (root / s.CRITICALITY_REL).unlink()
        (root / s.CRITICALITY_REL).mkdir()
    # Rewrite-Reason: DEC-1246 (3)(b): MR-2: `opus_model` is retired with the key.
    for call in (lambda: criticality.ticket_criticality(root, ticket),):
        with pytest.raises(GovError) as raised:
            call()
        assert raised.value.code == "LAUNCH_REFUSED" and s.CRITICALITY_REL in raised.value.message, (
            f"{raised.value.code}: {raised.value.message}")
