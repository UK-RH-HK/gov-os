"""KPI success 2 and KPI failure 1: the output is byte-identical on repeated runs over the same commit [CAP-57.a].

What is compared is the raw standard output of ``gov closure``: with ``--json`` the API-0002 envelope, without it
the printed result. Each run is a new process with another hash seed, time zone and working directory, so an
order taken from a set, a time or a path shows as a difference.
"""

from __future__ import annotations

import pytest

import w1_20_support as support

# start ids, depth: a complete closure, a depth cut with eight gaps, and unresolved ids
SCENARIOS = {
    "complete": ([support.CHAIN[0], support.HUB, support.CYCLE[1]], 50),
    "depth-cut": ([support.HUB, support.CHAIN[0], support.CYCLE[0]], 0),
    "unresolved": ([support.DANGLING_START, support.UNKNOWN, support.HUB], 5),
}
SEEDS = ("0", "1", "4242", "random")
ZONES = ("UTC", "Pacific/Kiritimati", "America/Anchorage", "Asia/Kolkata")


def _outputs(root, ids, depth, box, form, tmp_path):
    """The standard output of four runs, each with its own hash seed, time zone and working directory."""
    outputs = []
    for seed, zone in zip(SEEDS, ZONES):
        cwd = tmp_path / f"cwd-{seed}"
        cwd.mkdir(exist_ok=True)
        run = support.closure(root, ids, box, depth=depth, form=form, cwd=cwd, PYTHONHASHSEED=seed, TZ=zone)
        assert run.returncode == 0 and run.stdout.strip(), f"gov closure did not answer\n{run.describe()}"
        outputs.append(run.stdout)
    return outputs


@pytest.mark.parametrize("form", ["json", "plain"])
@pytest.mark.parametrize("scenario", list(SCENARIOS))
def test_repeated_runs_print_the_same_bytes(graph, box, tmp_path, scenario, form):
    ids, depth = SCENARIOS[scenario]
    outputs = _outputs(graph, ids, depth, box, form, tmp_path)
    assert len(set(outputs)) == 1, "gov closure printed different bytes on repeated runs of one commit:\n" + \
        "\n---\n".join(output.decode("utf-8", "replace") for output in sorted(set(outputs)))


def test_the_compared_output_is_a_closure_and_not_an_empty_answer(graph, box):
    """The premise of the byte comparison: the scenarios give closures, gaps and three different answers."""
    found = {name: support.ask(graph, ids, box, depth=depth) for name, (ids, depth) in SCENARIOS.items()}
    assert found["complete"]["stopping_reason"] == support.COMPLETE and len(found["complete"]["closure"]) > 10
    assert found["depth-cut"]["stopping_reason"] == support.DEPTH_LIMIT and len(found["depth-cut"]["gaps"]) == 10
    assert len(found["unresolved"]["gaps"]) == 3


def test_two_clones_of_one_commit_print_the_same_bytes(built, base, box, tmp_path):
    """The same commit in two places, each with its own store: nothing of the place is in the output."""
    outputs = []
    for name in ("one", "another/place/further/down"):
        root = support.clone(base, tmp_path / name / "repo")
        support.load_store(root, box)
        assert support.head(root) == support.head(base)
        ids, depth = SCENARIOS["unresolved"]
        outputs.append(support.closure(root, ids, box, depth=depth).stdout)
    assert outputs[0] == outputs[1] and outputs[0].strip()
    assert str(tmp_path).encode() not in outputs[0], "the output holds an absolute path of the repository"


def test_the_order_of_the_start_ids_does_not_change_the_closure(graph, box):
    """The same ids in another order are the same question: the closure and the gap list are the same."""
    ids, depth = SCENARIOS["unresolved"]
    one, other = (support.ask(graph, order, box, depth=depth) for order in (ids, list(reversed(ids))))
    assert (one["closure"], one["gaps"], one["stopping_reason"]) == \
        (other["closure"], other["gaps"], other["stopping_reason"])


def test_the_python_interface_returns_what_the_command_prints(graph, box):
    """Package DP-1: ``gov.closure.closure(root, ids, depth=N)`` is the result of ``gov closure --json``."""
    for ids, depth in SCENARIOS.values():
        returned = support.call("gov.closure", "closure", graph, box, list(ids), depth=depth)
        assert returned == support.ask(graph, ids, box, depth=depth)
