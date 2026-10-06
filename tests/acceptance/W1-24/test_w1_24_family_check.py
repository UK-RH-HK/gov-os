"""S6: registers the context-reproducibility family check: the same ticket and commit give the same packet
hash [CAP-38.b].

Red reason: the check declaration file does not exist yet (nothing matches
``template/governance/kernel/checks/context-reproducibility*``).
"""

from __future__ import annotations

import w1_24_support as S


def test_the_context_reproducibility_check_is_registered(family_check):
    """``gov check --list --json`` lists exactly one check whose family is ``context-reproducibility``."""
    assert family_check["family"] == S.FAMILY


def test_the_check_declaration_has_the_required_fields(family_check):
    """The check YAML has the fields the check runner needs: id, family, tier, severity, command."""
    for field in S.CHECK_FIELDS:
        assert field in family_check, f"the check declaration lacks the field {field!r}"
        assert isinstance(family_check[field], str) and family_check[field], \
            f"the field {field!r} is empty or not a string"


def test_the_same_ticket_and_commit_give_the_same_packet_hash(api, project):
    """The context-reproducibility invariant: same ticket, same commit, same packet hash (CAP-38.b).
    Tested by calling twice and comparing the hashes."""
    h1 = api.context(project, S.TK_NORMAL)[S.K_HASH]
    h2 = api.context(project, S.TK_NORMAL)[S.K_HASH]
    assert h1 == h2, f"same ticket, same commit, different hash: {h1} vs {h2}"


def test_the_check_command_is_runnable(family_check):
    """The declared command in the check YAML is a runnable Python module invocation."""
    command = family_check.get("command", "")
    assert command.startswith("python3 -m ") or command.startswith("python -m "), \
        f"the check command is not a Python module invocation: {command!r}"
    module_name = command.split("-m", 1)[-1].strip().split()[0]
    assert module_name, "the check command has no module name"


def test_the_same_hash_across_separate_processes_and_directories(api, base, tmp_path_factory):
    """The family invariant holds across two completely separate clones in different directories:
    same commit, same ticket, same packet hash. This tests cross-process reproducibility (CAP-38.b)."""
    clone_a = S.clone(base, tmp_path_factory.mktemp("fam-a") / "repo")
    clone_b = S.clone(base, tmp_path_factory.mktemp("fam-b") / "repo")
    api.build_store(clone_a)
    api.build_store(clone_b)
    h_a = api.context(clone_a, S.TK_NORMAL)[S.K_HASH]
    h_b = api.context(clone_b, S.TK_NORMAL)[S.K_HASH]
    assert h_a == h_b, \
        f"the packet hash differs across two clones of the same commit: {h_a} vs {h_b}"
