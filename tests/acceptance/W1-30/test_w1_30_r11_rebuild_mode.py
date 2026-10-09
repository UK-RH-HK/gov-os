"""A store rebuilt without embeddings is a store of the commit being closed (DEC-530).

"`gov rebuild` gets a mode without embeddings, for closes and checks that need only fresh lexical and graph
indexes."

``gov close`` refuses with ``STORE_STALE`` when the record store was built from another commit than the one
being closed, and says "run gov rebuild, then close again" (DEC-487). The mode (``gov rebuild
--no-embeddings``; ``tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py`` holds what it builds)
must leave a store that this check accepts: the ticket closes. And the check still reads that store: one
commit later it is stale, as any store is.

The rebuild runs in the suite's sandbox with an embedding endpoint that is down and a stand-in for its
program that records a start: the mode starts nothing.

Red reason: ``gov rebuild`` takes no ``--no-embeddings`` (a usage error, exit code 2).
"""

import socket

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-lean"
WBS = "W1-lean"
MODE = "--no-embeddings"
STORE_STALE = "STORE_STALE"


@pytest.fixture()
def project(built, tmp_path):
    """The suite's project without a path map, as it was when these cases were written. Since round 12 the
    suite's projects carry one for the close's number of workers (README, round 12), and a rebuild of a
    project with a path map also builds the lexical index, which needs the project's ``.gitleaks.toml`` and
    reads every tracked file. These cases hold the store check of a close, not that index."""
    return support.Project(tmp_path / "project", settings=None)


@pytest.fixture()
def rebuild_without_embeddings(project, sandbox, interface, tmp_path):
    """``rebuild_without_embeddings()`` runs ``gov rebuild --no-embeddings --json`` in the project; it must
    succeed, and must not start the endpoint's program."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        dead = f"127.0.0.1:{probe.getsockname()[1]}"
    program = tmp_path / "program" / "ollama"
    program.parent.mkdir()
    program.write_text(f"#!/bin/sh\necho started >> '{program.parent / 'started'}'\n", encoding="utf-8")
    program.chmod(0o755)
    env = {**support.sandbox_env(sandbox), "OLLAMA_HOST": dead, "GOV_OLLAMA_BIN": str(program)}

    def rebuild():
        run = project.gov(sandbox, "rebuild", MODE, "--json", env=env)
        envelope = cli_support.assert_envelope(run, interface, command="rebuild")
        assert envelope["ok"] is True and run.returncode == 0, f"gov rebuild {MODE} failed\n{run.describe()}"
        assert not (program.parent / "started").exists(), "the rebuild without embeddings started the endpoint's program"
        assert project.waiting_paths() == [], f"the rebuild left {project.waiting_paths()} in the working tree"
        return envelope["result"]

    return rebuild


def test_a_ticket_closes_on_a_store_rebuilt_without_embeddings(project, sandbox, interface,
                                                               rebuild_without_embeddings):
    support.build_ticket(project, TICKET, WBS)
    rebuild_without_embeddings()

    run = support.run_close(project, sandbox, TICKET, store=False)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed", run.describe()


def test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later(project, sandbox, interface,
                                                                      rebuild_without_embeddings):
    support.build_ticket(project, TICKET, WBS)
    rebuild_without_embeddings()
    project.write("notes/later.txt", "a later commit\n")
    project.commit("a later commit", who=support.ORCHESTRATOR)

    run = support.run_close(project, sandbox, TICKET, store=False)

    support.assert_error(run, interface, STORE_STALE, exit_code=support.EXIT_GOV_ERROR)
    support.assert_not_closed(project, TICKET)
    support.assert_nothing_counted(project, TICKET, run)
