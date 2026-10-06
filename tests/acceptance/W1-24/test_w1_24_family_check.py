"""S6: registers the context-reproducibility family check: the same ticket and commit give the same packet
hash [CAP-38.b].

Red reason: the check declaration file does not exist yet (nothing matches
``template/governance/kernel/checks/context-reproducibility*``).
"""

from __future__ import annotations

import subprocess
import sys

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


# ---- fail-open guards (DEC-425: unmeasured is never green)


def test_all_ticket_computations_fail_is_not_green(box, tmp_path):
    """(a) DEC-425: when every ticket's context computation raises, nothing was measured.
    A check that measured nothing is 'unmeasured', a warning, never green.
    Red reason: the current check swallows all exceptions (``except Exception: continue``)
    and exits 0 when no hash mismatch was detected, even though no hash was computed."""
    project = tmp_path / "repo"
    project.mkdir()
    S.git(project, "init", "-q", "-b", "main")
    S.adopt(project)
    S.write(project, ".gitignore", ".gov-runtime/\n")
    S.write(project, ".tickets/TK-ALLFAIL-1.md",
            S.ticket_file("TK-ALLFAIL-1", sources=["NONEXISTENT-1"]))
    S.write(project, ".tickets/TK-ALLFAIL-2.md",
            S.ticket_file("TK-ALLFAIL-2", sources=["NONEXISTENT-2"]))
    S.commit(project, "setup")
    box.build_store(project)

    done = subprocess.run(
        [sys.executable, "-m", "gov.context.context_check"],
        cwd=str(project), env=box.scratch_env(),
        capture_output=True, text=True, timeout=S.CALL_TIMEOUT_S,
        stdin=subprocess.DEVNULL,
    )
    assert done.returncode != 0, \
        f"every computation failed and the check is green\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    assert "unmeasured" in done.stdout.lower(), \
        f"every computation failed and the output does not say 'unmeasured'\nstdout:\n{done.stdout}"


def test_some_ticket_computations_fail_names_each_failure(box, tmp_path):
    """(b) DEC-425: when some tickets succeed and some fail, each failure is named in the
    output and the check is not green. A partial measurement with failures is not green.
    Red reason: the current check swallows the exception and exits 0."""
    project = tmp_path / "repo"
    project.mkdir()
    S.git(project, "init", "-q", "-b", "main")
    S.adopt(project)
    S.write(project, ".gitignore", ".gov-runtime/\n")
    S.write(project, "docs/charter/charter.md",
            S.record("CHARTER-FC", "charter", "ACTIVE", "A charter for the family check test."))
    S.write(project, ".tickets/TK-FC-OK.md",
            S.ticket_file("TK-FC-OK", sources=["CHARTER-FC"]))
    failing_id = "TK-FC-FAIL"
    S.write(project, ".tickets/" + failing_id + ".md",
            S.ticket_file(failing_id, sources=["NONEXISTENT-SOURCE"]))
    S.commit(project, "setup")
    box.build_store(project)

    done = subprocess.run(
        [sys.executable, "-m", "gov.context.context_check"],
        cwd=str(project), env=box.scratch_env(),
        capture_output=True, text=True, timeout=S.CALL_TIMEOUT_S,
        stdin=subprocess.DEVNULL,
    )
    assert done.returncode != 0, \
        f"a ticket computation failed and the check is green\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    assert failing_id in done.stdout, \
        f"the failing ticket {failing_id!r} is not named in the output\nstdout:\n{done.stdout}"


def test_no_tickets_reports_unmeasured_and_is_not_green(box, tmp_path):
    """(c) DEC-425: when the store has no tickets, nothing was measured.
    The check reports 'unmeasured' and is not green.
    Red reason: the current check prints 'no tickets in the store' and exits 0."""
    project = tmp_path / "repo"
    project.mkdir()
    S.git(project, "init", "-q", "-b", "main")
    S.adopt(project)
    S.write(project, ".gitignore", ".gov-runtime/\n")
    S.write(project, "docs/charter/charter.md",
            S.record("CHARTER-EMPTY", "charter", "ACTIVE",
                     "A charter in a project with no tickets."))
    S.commit(project, "setup")
    box.build_store(project)

    done = subprocess.run(
        [sys.executable, "-m", "gov.context.context_check"],
        cwd=str(project), env=box.scratch_env(),
        capture_output=True, text=True, timeout=S.CALL_TIMEOUT_S,
        stdin=subprocess.DEVNULL,
    )
    assert done.returncode != 0, \
        f"no tickets to measure and the check is green\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    assert "unmeasured" in done.stdout.lower(), \
        f"no tickets and the output does not say 'unmeasured'\nstdout:\n{done.stdout}"
