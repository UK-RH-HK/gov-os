"""KPI S5: an owner decision that lives only in the archive still counts in gov close's lookups (EMERGENCY-2 11.3).

A planted project of its own: the archive alone holds the owner's decision that the path map's four lists name
(``accepted_reds``, ``load_sensitive``, ``acceptance_exemptions``, ``accepted_history``) and that a closed ticket's
commit implements; beside each stands an entry or commit naming an id no file holds. The clone case compares this
repository's lists and closed tickets with the base's.
"""

from __future__ import annotations

import json

import pytest
import yaml

import w2_203_support as s

CLOSED = "TKT-cd34"
RED, FLAKY, OTHER = (f"{s.TEST_REL}::test_rule", f"{s.TEST_REL}::test_tide", f"{s.TEST_REL}::test_other")


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    """``(root, commits)``: the planted project of this module."""
    root = tmp_path_factory.mktemp("w2-203-close") / "repo"
    root.mkdir()
    s.git(root, "init", "-q", "-b", "main")
    commits = {}
    s.write(root, ".gitignore", ".gov-runtime/\n")
    s.write(root, s.PATH_MAP_REL, s.path_map())
    s.write(root, s.REGISTER_REL, s.register_text())
    s.commit(root, "The register")
    for name in ("accepted", "other"):
        s.write(root, s.LOG_REL, f"# Log\n\nThe {name} line.\n")
        commits[name] = s.commit(root, f"A commit of history ({name})")
    owner = (f"### {s.A_OWNER} — The skerrywell exception\n"
             "- **Status:** ACCEPTED (owner, 2026-10-05) · **Class:** history\n"
             f"- **Decision:** the commit `{commits['accepted'][:12]}` is accepted history and its change of the tests "
             f"stands; the reds `{RED}` and `{FLAKY}` (test_rule and test_tide, in {s.TEST_REL}) are accepted.")
    s.write(root, s.ARCHIVE_REL, s.archive_text(entry={**s.ENTRY, s.A_OWNER: owner}))
    s.write(root, f".tickets/{CLOSED}.md", s.record(CLOSED, "task", "closed", "# The closed ticket\n"))
    s.write(root, s.TEST_REL, "def test_rule():\n    assert True\n")
    s.commit(root, "The archive")
    lists = {
        "accepted_reds": [{"test": RED, "decision": s.A_OWNER, "reason": "named", "fixed_by": "W9-01"},
                          {"test": OTHER, "decision": s.NEITHER, "reason": "named", "fixed_by": "W9-01"}],
        "load_sensitive": [{"test": FLAKY, "decision": s.A_OWNER, "reason": "under load"},
                           {"test": OTHER, "decision": s.NEITHER, "reason": "under load"}],
        "acceptance_exemptions": [{"commit": commits["accepted"], "decision": s.A_OWNER},
                                  {"commit": commits["other"], "decision": s.NEITHER}],
        "accepted_history": [{"commit": commits["accepted"], "decision": s.A_OWNER},
                             {"commit": commits["other"], "decision": s.NEITHER}],
    }
    s.write(root, s.PATH_MAP_REL, s.path_map(**lists))
    s.commit(root, "The owner's lists\n\nRole: owner")
    for name, decision in (("archived", s.A_OWNER), ("neither", s.NEITHER)):
        s.write(root, s.LOG_REL, f"# Log\n\nThe {name} work.\n")
        commits[name] = s.commit(root, f"Work ({name})\n\nTask: {CLOSED}\nImplements: {decision}")
    return root, commits, owner


def _path_map(root) -> dict:
    return yaml.safe_load((root / s.PATH_MAP_REL).read_text(encoding="utf-8"))


def test_s5_the_register_reader_returns_the_archives_entry_with_its_status_line_and_text(project):
    from gov.close import history

    root, _, owner = project
    entries = history.register_entries(root, s.REGISTER_REL)
    assert isinstance(entries, dict), f"the register cannot be read: {entries}"
    stripped = {record_id: [text.rstrip() for text in texts] for record_id, texts in entries.items()}
    assert stripped.get(s.A_OWNER) == [owner], f"{s.A_OWNER}, held by the archive alone: {entries.get(s.A_OWNER)}"
    why, text = history.owner_decision(s.A_OWNER, entries)
    assert why is None and text.rstrip() == owner
    assert stripped.get(s.K_FIRST) == [s.ENTRY[s.K_FIRST]], "an entry both files hold is the register's, once"
    assert s.NEITHER not in entries and history.owner_decision(s.NEITHER, entries)[0]


@pytest.mark.parametrize("key, test", [("accepted_reds", RED), ("load_sensitive", FLAKY)])
def test_s5_a_ratchet_entry_whose_decision_lives_only_in_the_archive_counts(project, key, test):
    from gov.close import ratchet

    counted, findings = ratchet.counted_entries(project[0], key)
    assert [entry["test"] for entry in counted] == [test], f"{key}: counted {counted}, refused {findings}"
    assert [finding["test"] for finding in findings] == [OTHER] and s.NEITHER in findings[0]["message"], \
        f"the entry of a decision in neither file is refused, and only it: {findings}"


def test_s5_an_acceptance_exemption_whose_decision_lives_only_in_the_archive_counts(project):
    from gov.close import gates

    root, commits, _ = project
    settings = {key: value for key, value in _path_map(root).items() if key != "accepted_history"}
    assert gates.owner_listed(root, settings) == {commits["accepted"]}


def test_s5_accepted_history_whose_decision_lives_only_in_the_archive_counts(project):
    from gov.close import history

    root, commits, _ = project
    accepted, refused = history.accepted_history(root, _path_map(root))
    assert accepted == {commits["accepted"]: s.A_OWNER}, f"accepted {accepted}, refused {refused}"
    assert [finding["decision"] for finding in refused] == [s.NEITHER]


def test_s5_a_closed_tickets_trailer_id_resolves_through_the_archive(project, home):
    root, commits, _ = project
    done = s.child(s.src(), root, home / "trace", "-m", "gov.close.traceability")
    unresolved = [f["message"] for f in s.json_of(done).get("findings", []) if f["code"] == "IMPLEMENTS_UNRESOLVED"]
    assert not [message for message in unresolved if s.A_OWNER in message], f"unresolved: {unresolved}"
    assert len(unresolved) == 1 and s.NEITHER in unresolved[0] and commits["neither"][:12] in unresolved[0], \
        f"the id in neither file stays unresolved, and only it: {unresolved}"


_LISTS = ("import json, pathlib, yaml; from gov.close import gates, history, ratchet; "
          "root = pathlib.Path('{root}'); "
          "path_map = yaml.safe_load((root / 'governance/project/path-map.yaml').read_text(encoding='utf-8')); "
          "lists = [ratchet.counted_entries(root, key) for key in ('accepted_reds', 'load_sensitive')]; "
          "print(json.dumps({'counted': [counted for counted, _ in lists], "
          "'refused': [sorted(f['test'] for f in findings) for _, findings in lists], "
          "'owner_listed': sorted(gates.owner_listed(root, path_map)), "
          "'accepted_history': sorted(history.accepted_history(root, path_map)[0])}, sort_keys=True))")


def test_s5_real_the_lists_count_what_the_base_counted(base_clone, head_clone, home, moved):
    from gov.close import history

    entries = history.register_entries(head_clone, s.REGISTER_REL)
    text_of = dict(moved["archive"])
    sample = sorted(moved["only"], key=s.number_of)[0]
    assert isinstance(entries, dict) and len(entries.get(sample, [])) == 1 \
        and entries[sample][0].startswith(text_of[sample].split("\n", 1)[0]), \
        f"gov close's register reader does not find {sample}, which the archive alone holds"
    base, head = s.both(base_clone, head_clone, home, "-c", _LISTS)
    assert all(base["counted"]) and base["owner_listed"], f"premise: the base counts entries of each list: {base}"
    assert head == base, ("the counted and refused entries differ from the base's:\n"
                          f"{json.dumps(base)[:1500]}\n{json.dumps(head)[:1500]}")


def test_s5_real_no_closed_tickets_trailer_id_is_unresolved_that_the_base_resolved(base_clone, head_clone, home, moved):
    base, head = s.both(base_clone, head_clone, home, "-m", "gov.close.traceability", cwd_is_root=True)

    def unresolved(answer):
        return {f["message"] for f in answer.get("findings", []) if f["code"] == "IMPLEMENTS_UNRESOLVED"}

    assert "findings" in base and "findings" in head, f"not judged: {str(base)[:300]} {str(head)[:300]}"
    new = sorted(unresolved(head) - unresolved(base))
    lost = [message for message in new if set(message.replace(":", " ").split()) & moved["only"]]
    assert not lost, f"{len(lost)} trailer ids the base resolved are unresolved: {lost[:5]}"
