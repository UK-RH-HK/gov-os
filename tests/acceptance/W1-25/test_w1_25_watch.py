"""W1-25 -- KPI success 3 [CAP-37.c]: the provider-independent watchdog.

"gov checkpoint --watch marks the latest checkpoint stale by policy (age,
commits since, context utilisation) without relying on harness hooks; lefthook
and the orchestrator can run it."

Recommended option of DP-5: the thresholds are arguments with kernel defaults;
the caller passes the context utilisation, because no harness hook does; a
stale checkpoint is the error ``CHECKPOINT_STALE`` with exit code 3 (API-0002:
"verification failed / unhealthy") and its reasons in ``error.details``; the
watchdog only reads. Every test runs the command as a plain process with a
bare environment: no hook and no harness variable is present. Another answer to
DP-5 changes this file only.
"""

from __future__ import annotations

import w1_25_support as support

cli_support = support.cli_support


def _watch(gov, *extra, json=True):
    return gov("checkpoint", "--watch", "--ticket", support.TICKET, *extra, *(("--json",) if json else ()))


def _stale(run, interface, reason):
    error = support.refused(run, interface, exit_codes=(support.EXIT_UNHEALTHY,))
    assert error["code"] == support.STALE, f"expected {support.STALE}\n{run.describe()}"
    assert reason in support.reasons(error), f"the reason '{reason}' is not reported\n{run.describe()}"
    return error


def test_a_new_checkpoint_is_fresh_under_the_default_policy(project, gov, interface, checkpoint):
    path = checkpoint()
    result = support.succeeded(_watch(gov), interface)
    assert result.get("stale") is False, result
    assert result.get("path") == path.relative_to(project).as_posix(), \
        f"the watchdog does not name the latest checkpoint: {result}"


def test_a_checkpoint_within_every_threshold_is_fresh(gov, interface, checkpoint):
    checkpoint()
    run = _watch(gov, "--max-age-minutes", "600", "--max-commits", "5",
                 "--context-utilisation", "0.10", "--max-context", "0.30")
    assert support.succeeded(run, interface).get("stale") is False, run.describe()


def test_an_old_checkpoint_is_stale_by_age(project, gov, interface, checkpoint):
    support.backdate(checkpoint(commit=False))
    cli_support.commit_all(project, "an old checkpoint")
    _stale(_watch(gov, "--max-age-minutes", "60", "--max-commits", "50"), interface, support.REASON_AGE)


def test_a_checkpoint_is_stale_by_the_commits_since(project, gov, interface, checkpoint):
    """Two commits are allowed; three follow the commit that carries the checkpoint."""
    checkpoint()
    limits = ("--max-age-minutes", "600", "--max-commits", "2")
    support.succeeded(_watch(gov, *limits), interface)
    for number in range(3):
        cli_support.commit_all(project, f"work {number}")
    _stale(_watch(gov, *limits), interface, support.REASON_COMMITS)


def test_a_checkpoint_is_stale_by_context_utilisation(gov, interface, checkpoint):
    """The caller states the utilisation; no harness hook is asked."""
    checkpoint()
    error = _stale(_watch(gov, *support.LOOSE, "--context-utilisation", "0.50", "--max-context", "0.30"),
                   interface, support.REASON_CONTEXT)
    assert support.REASON_AGE not in support.reasons(error) and support.REASON_COMMITS not in support.reasons(error)


def test_every_violated_threshold_is_reported(project, gov, interface, checkpoint):
    support.backdate(checkpoint(commit=False))
    cli_support.commit_all(project, "an old checkpoint")
    run = _watch(gov, "--max-age-minutes", "60", "--max-commits", "50",
                 "--context-utilisation", "0.50", "--max-context", "0.30")
    error = _stale(run, interface, support.REASON_AGE)
    assert support.REASON_CONTEXT in support.reasons(error), error


def test_the_watchdog_only_reads(project, gov, checkpoint):
    """lefthook can run it: neither a fresh nor a stale verdict changes a file, the index or a ref."""
    checkpoint()
    before = support.state(project)
    fresh = _watch(gov, *support.LOOSE)
    stale = _watch(gov, *support.LOOSE, "--context-utilisation", "0.50", "--max-context", "0.30")
    assert (fresh.returncode, stale.returncode) == (0, support.EXIT_UNHEALTHY), \
        f"{fresh.describe()}\n{stale.describe()}"
    assert support.state(project) == before, "gov checkpoint --watch changed the project"


def test_without_json_the_exit_code_and_one_message_carry_the_verdict(gov, checkpoint):
    """lefthook reads the exit code and shows the output; the orchestrator reads the envelope."""
    checkpoint()
    fresh = _watch(gov, *support.LOOSE, json=False)
    assert fresh.returncode == 0, fresh.describe()
    stale = _watch(gov, *support.LOOSE, "--context-utilisation", "0.50", "--max-context", "0.30", json=False)
    assert stale.returncode == support.EXIT_UNHEALTHY, stale.describe()
    assert support.STALE in stale.stderr and support.REASON_CONTEXT in stale.stderr, stale.describe()


def test_a_latest_checkpoint_with_an_input_without_its_hash_is_not_fresh(project, gov, interface, checkpoint):
    """KPI failure 2, on a record edited by hand: the watchdog does not pass it."""
    path = checkpoint(commit=False)

    def drop_hashes(document):
        for item in document[support.KEY_INPUTS]:
            item.pop("hash", None)

    support.rewrite_frontmatter(path, drop_hashes)
    cli_support.commit_all(project, "a checkpoint without hashes")
    support.refused(_watch(gov, *support.LOOSE), interface, exit_codes=(1, support.EXIT_UNHEALTHY))
