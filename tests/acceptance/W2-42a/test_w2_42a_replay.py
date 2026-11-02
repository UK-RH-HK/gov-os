"""W2-42a, KPI line 11: every logged refusal replayed through the five-rule hook as it runs after re-pin window 2,
and every planted case of ACT-GUARD-FIX-3 still refused (DEC-1040 item 2, DEC-958).

The hook is the reviewed ``drafts/act-guard-fix-3/pretooluse.py`` with ``bash_writes.py`` beside it (copied to
fixtures/hook/, SHA-256 b7e96a89d092 and df7be57c6bdd, the same as the live ``.claude/hooks/`` today), run by
``python3`` with this tree's ``src`` on ``PYTHONPATH``, as the pinned judge runs it once this tree is pinned. Each
call is fed as Claude Code sends it: event JSON on stdin (``tool_name``, ``tool_input``, ``cwd``, ``agent_type``) and
the session's ``GOV_ROLE``, ``CLAUDE_PROJECT_DIR`` and ``TMPDIR`` in its environment (fixtures/refusals.json; how
each is found: tools/build_refusals.py).

- A refusal judged false must now be allowed; one judged true must still be refused, by the same rule (the hook's
  reason equal to the logged one).
- ``HELD``: five lines the log judges false that W2-42a cannot let pass without failing open or changing what is
  outside its paths (the hook itself, an owner ACT); each is expected still refused by its logged rule, and each is a
  decision package to the CTO (README, "Held refusals"). Taking a line out of ``HELD`` makes it a must-pass case.
- A planted case must be refused by its write rule (rule 1, or rule 5 for a reviewer), with exit 0: a refusal by an
  error is no judgement.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402

HELD = {
    47: "ACT-GUARD-FIX-3 leaves it refused by design (its row 46): an unquoted Python heredoc whose text the shell "
        "rewrites with $(echo \"$out\" | sed ...), in a command naming the tests; judged by the hook's own Python "
        "reading (bash_writes.py), which no change in src/gov/guard reaches",
    65: "cd $TMPDIR || cd $(ls -dt /tmp/tmp.* | head -1), then writes in that folder, in a command naming the tests: "
        "a write to a folder known only at run time; rule 1 refuses an unresolvable write when the command names the "
        "tests, so passing it is a fail-open",
    72: "the hook's own Python reading (ACT-GUARD-FIX-3 F4): an f-string path from sys.argv (the id tk create "
        "prints), in code whose text names the tests; the product's parser adds no target to it, so no change in "
        "src/gov/guard reaches it (a hook change is an owner ACT)",
    73: "the hook's own Python reading (F4): a computed path written while the code runs a module of the acceptance "
        "folder (exec_module of tests/acceptance/W1-01/w1_01_support.py); out of the product's reach, as line 72",
    76: "the log's verdict is the harvester's automatic one (judged as an engineer); the same reviewer's Write of the "
        "same file a few seconds later (line 77) is judged true: rule 5 keeps a reviewer to its record paths, and "
        "scratch/orchestrator/reviews/ is none of them",
}

REFUSALS = s.refusals()
PLANTED = s.planted()


def _id(r):
    return f"line{r['line']:02d}-{r['key']}"


@pytest.mark.parametrize("row", REFUSALS, ids=[_id(r) for r in REFUSALS])
def test_kpi11_each_logged_refusal_replayed(row):
    got, why, code = s.run_hook(row["tool"], row["input"], row["cwd"], row["root"], row["role"],
                                agent_type=row["agent_type"], tmpdir=row["tmpdir"])
    if row["verdict"] == "true" or row["line"] in HELD:
        assert (got, code) == ("deny", 0), f"line {row['line']}: want refused, got {got} ({why[:400]})"
        assert why == row["rule"], f"line {row['line']}: refused by another rule: {why[:400]}"
    else:
        assert got == "allow", f"line {row['line']} (judged false): still refused: {why[:400]}"


def test_kpi11_the_replay_holds_every_recoverable_line():
    data = s.load(s.REFUSALS)
    assert len(data["refusals"]) == 76 and [x["line"] for x in data["left_out"]] == [51, 52, 53, 54]
    assert sum(r["verdict"] == "true" for r in data["refusals"]) == 2
    assert set(HELD) <= {r["line"] for r in data["refusals"] if r["verdict"] == "false"}


@pytest.mark.parametrize("row", PLANTED, ids=[r["name"] for r in PLANTED])
def test_kpi11_each_planted_case_still_refused(row):
    got, why, code = s.run_hook(row["tool"], row["input"], s.REPO, s.REPO, row["role"])
    assert (got, code) == ("deny", 0), f"want refused by its write rule, got {got} ({why[:400]})"
    assert why in s.write_rule_reasons(row["role"]), f"refused by another rule: {why[:400]}"
