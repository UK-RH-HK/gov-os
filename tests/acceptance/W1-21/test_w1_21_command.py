"""``gov retrieve`` as the command convention defines it (DEC-317): the same bundle as the function, in the
API-0002 envelope [CAP-16.a, CAP-55.a].

Every case here depends on ``src/gov/retrieve/command.py``, which is outside the ticket's allowed paths; until
the file exists each fails at the ``cli`` fixture with that reason.

    gov retrieve [--json] [--root <dir>] [--ticket <id>] [--id <id>]... [--radius <R>] [--batch-size <N>]
                 [--bundle-budget <N>] [--continue <token>] <query>
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")

SMALL = ("--batch-size", "2", "--radius", str(support.RADIUS_LITE), "--bundle-budget", "0")


def answered(run):
    assert "Traceback" not in run.output, f"gov retrieve ended with a traceback\n{run.describe()}"
    return run


def test_the_command_returns_the_bundle_of_the_function(cli, api, project, ollama):
    """The same arguments, the same bundle: the command is the function behind an envelope."""
    run = answered(cli.command(project, "--ticket", support.TICKET_IN_SCOPE, "--radius", "2", "--batch-size", "3",
                               "--bundle-budget", str(support.BUDGET_SMALL), support.PHRASE, host=ollama.host))
    bundle = support.check_bundle(run.bundle(), root=project)
    assert bundle == api.retrieve(project, support.PHRASE, host=ollama.host, ticket=support.TICKET_IN_SCOPE,
                                  radius=2, batch_size=3, bundle_budget=support.BUDGET_SMALL)


def test_the_command_without_options_answers_with_a_checked_bundle(cli, project, ollama):
    support.check_bundle(answered(cli.command(project, support.PHRASE, host=ollama.host)).bundle(), root=project)


def test_a_bundle_cut_by_the_budget_is_continued_by_its_token(cli, project, ollama):
    """KPI failure 1 through the command: exit code 0, the reason of the budget, and ``--continue`` leads through
    everything once."""
    runs = [answered(cli.command(project, *SMALL, support.PHRASE, host=ollama.host))]
    bundles = [support.check_bundle(runs[0].bundle(), root=project)]
    assert bundles[0][support.K_REASON] == support.BUDGET_EXHAUSTED and bundles[0][support.K_GAPS]
    while bundles[-1][support.K_CONTINUATION] is not None:
        assert len(bundles) < 40, "the continuation did not end"
        run = answered(cli.command(project, *SMALL, "--continue", bundles[-1][support.K_CONTINUATION],
                                   support.PHRASE, host=ollama.host))
        bundles.append(support.check_bundle(run.bundle(), root=project))
    seen = [chunk for bundle in bundles for chunk in support.chunk_ids(bundle)]
    assert len(bundles) > 2 and len(seen) == len(set(seen)), "a chunk is cited by two bundles of one continuation"
    assert set(support.PAGING) <= {rel for bundle in bundles for rel in support.paths(bundle)}
    assert bundles[-1][support.K_REASON] in support.NOTHING_LEFT


def test_ids_are_given_one_by_one(cli, project, ollama):
    run = answered(cli.command(project, "--id", "ADR-0032", "--id", "ADR-0012", "--batch-size",
                               str(support.BATCH_LARGE), support.NO_SUCH_TEXT, host=ollama.host))
    assert {support.CHAIN[2], support.CURRENT[1]} <= set(support.paths(run.bundle()))


def test_without_a_reranker_environment_the_command_says_nothing_was_reranked(cli, project, ollama):
    """The scratch HOME has no reranker environment (DEC-397): the fused order, stated (DEC-374)."""
    bundle = answered(cli.command(project, support.PHRASE, host=ollama.host)).bundle()
    assert bundle[support.K_MERGE].get(support.M_RERANKED) is False


def test_without_the_embedding_endpoint_the_command_still_answers(cli, project):
    run = answered(cli.command(project, "--batch-size", str(support.BATCH_LARGE), support.PHRASE))
    bundle = support.check_bundle(run.bundle(), root=project)
    assert bundle[support.K_REASON] == support.FACET_UNAVAILABLE and set(support.PAGING) <= set(support.paths(bundle))


def test_a_call_without_a_question_is_a_usage_error(cli, project):
    run = cli.gov("retrieve", "--json", "--root", str(project))
    assert run.returncode == 2 and "Traceback" not in run.output, run.describe()


@pytest.mark.parametrize("option", ["--radius", "--batch-size", "--bundle-budget"])
def test_an_option_that_is_no_number_is_a_usage_error(cli, project, option):
    run = cli.command(project, option, "many", support.PHRASE)
    assert run.returncode == 2 and "Traceback" not in run.output, run.describe()


def test_a_continuation_that_is_no_token_is_an_error_envelope(cli, project, ollama):
    run = answered(cli.command(project, "--continue", "not-a-continuation", support.PHRASE, host=ollama.host))
    envelope = run.envelope()
    assert run.returncode == 1 and envelope.get("ok") is False, run.describe()
    assert isinstance(envelope.get("error"), dict) and envelope["error"].get("code"), run.describe()


def test_repeated_runs_print_the_same_bytes(cli, project, ollama, tmp_path):
    """Non-deterministic output: each run is a new process with another hash seed, time zone and directory."""
    outputs = []
    for seed, zone in (("0", "UTC"), ("4242", "Pacific/Kiritimati"), ("random", "America/Anchorage")):
        cwd = tmp_path / f"cwd-{seed}"
        cwd.mkdir()
        env = cli.scratch_env(ollama.host, PYTHONHASHSEED=seed, TZ=zone)
        run = answered(cli.command(project, "--ticket", support.TICKET_IN_SCOPE, "--batch-size", "3", "--radius",
                                   "2", support.PHRASE, env=env, cwd=cwd))
        assert run.returncode == 0 and run.stdout.strip(), run.describe()
        outputs.append(run.stdout)
    assert len(set(outputs)) == 1, "gov retrieve printed different bytes for the same question, commit and store"


def test_the_command_writes_nothing(cli, repo, ollama):
    cli.build(repo, ollama.host)
    before = support.tree(repo)
    answered(cli.command(repo, "--ticket", support.TICKET_IN_SCOPE, support.PHRASE, host=ollama.host)).bundle()
    assert support.tree(repo) == before, "gov retrieve wrote or changed a file of the project"


def test_in_a_project_without_an_index_the_command_answers_and_builds_nothing(cli, repo, ollama):
    """An envelope with exit code 0 (a bundle that says FACET_UNAVAILABLE and cites nothing) or 1 (an error with
    its code); no traceback, no runtime folder."""
    run = answered(cli.command(repo, support.PHRASE, host=ollama.host))
    envelope = run.envelope()
    assert run.returncode in (0, 1), run.describe()
    if run.returncode == 0:
        bundle = support.check_bundle(run.bundle(), root=repo)
        assert bundle[support.K_REASON] == support.FACET_UNAVAILABLE and not bundle[support.K_EVIDENCE]
    else:
        assert envelope.get("ok") is False and envelope["error"].get("code"), run.describe()
    assert not (repo / support.RUNTIME_REL).exists(), "gov retrieve made the runtime folder"
