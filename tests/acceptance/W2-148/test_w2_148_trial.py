"""W2-148 S23: the trial on past ACTs, measured by the engineer, recorded in docs/changes/W2-148-evidence.md (its
tables' form is stated in README.md). Red until the engineer writes it. The pinned subset: every ACT the package's §2
table names in its example column, at no lower class than its row (README, N-6)."""

from __future__ import annotations

import re
import subprocess

import pytest

import w2_148_support as support

ORDER = {"a": 0, "b": 1, "O": 2}

# The ACTs §2's table names by example, at their row's class: the trial may class them higher, never lower.
PINNED = {
    **{f"ACT-{n}": "b" for n in (
        "1-GUARD", "GUARD-FIX-1", "GUARD-FIX-2", "GUARD-FIX-3", "GUARD-FIX-4", "G14", "G14b", "INDEP-WALLS-1",
        "GUARD-SETS-1", "PERMISSIONS-1", "PERMISSIONS-2", "QUIET-DENY-1", "STOP-WAITER-1", "PUSH-INPUT-1",
        "SELECT-HOOK-1", "SELECT-FIXES-1", "GATE-CONFIG-1", "NIGHTLY-1", "NIGHTLY-STOP-1", "SCHEDULE-STOP-2",
        "DISPATCH-CRON-2", "DISPATCHER-1", "RUNS-SWEEP-1", "DEADMAN-1", "SENTINEL-1", "RERANK-TRIAL-1",
        "RERANK-TRIAL-2")},
    **{f"ACT-{n}": "O" for n in (
        "W1-01-EXEMPT-1", "W2-57-LS-1", "P-TRACE-IMPL-1", "REPIN-1", "REPIN-2", "REPIN-EMERGENCY-1", "REPIN-W2",
        "REPIN-W3", "REPIN-W4", "WSL-INTEROP-1", "NIGHTLY-0400", "D8")},
}

REPLAYS = {"SELECT-FIXES-1": "b", "SELECT-HOOK-1": "b", "GUARD-SETS-1": "b", "PERMISSIONS-2": "b",
           "NIGHTLY-STOP-1": "b", "OLLAMA-CAP-1": "a", "W1-01-EXEMPT-1": "O", "D8": "O"}

FAULTS = ("after review", "class", "unlisted", "red", "undo", "missing", "older")


@pytest.fixture(scope="module")
def record():
    assert support.EVIDENCE.is_file(), "docs/changes/W2-148-evidence.md does not exist yet (the trial's record)"
    return support.EVIDENCE.read_text(encoding="utf-8")


def cls(cell):
    m = re.search(r"\((a|b|O)\)", cell)
    return m.group(1) if m else None


def act_rows(text):
    (i_act, i_cls), rows = support.find_table(text, "act", "class")
    assert i_act is not None, "no table with an `ACT file` and a `Class` column"
    out = {}
    for row in rows:
        m = re.search(r"(ACT-[A-Za-z0-9-]+)", row[i_act]) if i_act < len(row) else None
        if m:
            out[m.group(1)] = cls(row[i_cls]) if i_cls < len(row) else None
    return out


def named(name, cell):
    return re.search(r"(?<![\w-])(?:ACT-)?" + re.escape(name) + r"(?![\w-])", cell) is not None


def acts_at_the_package():
    p = subprocess.run(["git", "-C", str(support.ROOT), "ls-tree", "--name-only", "116c2b413",
                        "governance/project/orchestration/packages/"], capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr
    names = {re.sub(r"\.md$", "", line.rsplit("/", 1)[-1]) for line in p.stdout.splitlines()
             if re.fullmatch(r".*/ACT-[^/]+\.md", line)}
    assert len(names) == 54, len(names)
    return names


def test_s23_the_record_has_a_row_per_act_file_with_its_class(record):
    rows = act_rows(record)
    wanted = acts_at_the_package() | {"ACT-GATE-CONFIG-1", "ACT-D4-RESTORE-1"}
    assert wanted <= set(rows), sorted(wanted - set(rows))
    assert all(rows[a] in ORDER for a in wanted), {a: rows[a] for a in wanted if rows[a] not in ORDER}


def test_s23_the_counts_per_class_match_the_rows(record):
    rows = act_rows(record)
    (i_cls, i_n), counts = support.find_table(record, "class", "count")
    assert i_cls is not None, "no table with a `Class` and a `Count` column"
    got = {cls(r[i_cls]): int(re.sub(r"\D", "", r[i_n]) or -1) for r in counts if cls(r[i_cls])}
    tally = {k: sum(1 for v in rows.values() if v == k) for k in ORDER}
    assert got == tally, (got, tally)


def test_s23_no_pinned_act_is_classed_lower_than_the_table(record):
    rows = act_rows(record)
    low = {a: (rows.get(a), want) for a, want in PINNED.items() if rows.get(a) not in ORDER or
           ORDER[rows[a]] < ORDER[want]}
    assert low == {}


def test_s23_the_rises_are_listed(record):
    assert re.search(r"^#+ .*\brises?\b", record, re.I | re.M), "no section listing the rises"


def test_s23_eight_replays_give_their_expected_class_and_outcome(record):
    (i_r, i_c, i_o), rows = support.find_table(record, "replay", "class", "outcome")
    assert i_r is not None, "no table with `Replay`, `Class` and `Outcome` columns"
    for name, want in REPLAYS.items():
        row = next((r for r in rows if i_r < len(r) and named(name, r[i_r])), None)
        assert row, f"no replay row for {name}"
        assert cls(row[i_c]) == want, (name, row)
        assert re.search(r"refused" if want == "O" else r"applied", row[i_o], re.I), (name, row)


def test_s23_seven_planted_faults_are_each_refused(record):
    (i_f, i_o), rows = support.find_table(record, "fault", "outcome")
    assert i_f is not None, "no table with `Fault` and `Outcome` columns"
    assert len(rows) >= 7
    for key in FAULTS:
        assert any(key in r[i_f].lower() for r in rows), f"no planted fault row naming {key!r}"
    for r in rows:
        assert re.search(r"refused|undone|lock held", r[i_o], re.I), r


def test_s23_no_live_file_changed_before_and_after_hashes(record):
    (i_p, i_b, i_a), rows = support.find_table(record, "path", "before", "after")
    assert i_p is not None, "no table with `Path`, `Before` and `After` columns"
    assert len(rows) >= 3
    for r in rows:
        before, after = (re.search(r"[0-9a-f]{64}", r[i]) for i in (i_b, i_a))
        assert before and after and before.group(0) == after.group(0), r
    assert any("gov-os-operator" in r[i_p] for r in rows) and any(".claude" in r[i_p] for r in rows)
