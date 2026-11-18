"""W2-201 F2: no usage brake or budget is added.

A worker launch with plan readings at 100 percent planted (``log/usage.txt`` in the project and in the CTO's scratch
log folder, in ``usage_log.sh``'s line form) starts as before, with the same record as the same launch without them
(the keys that differ between any two launches, the session's id and times, left out); and neither the launcher's
package nor the hook names ``usage.txt``, ``spend.jsonl`` or ``usage_log``.
"""

from __future__ import annotations

import w2_201_support as k

s = k.s
READING = ("2026-11-18 23:00:00 session=100% (resets 2am);week (all models)=100% (resets Nov 21);"
           "week (Opus)=100% (resets Nov 21); last 24h: 900 requests, 40 sessions\n")
PLACES = ("log/usage.txt", ".gov-runtime/scratch/orchestrator/log/usage.txt")
PER_LAUNCH = ("session_id", "started_at", "ended_at", "pid", "exit_code", "worktree_pid", "temp_folder", "tmpdir")
NAMES = ("usage.txt", "spend.jsonl", "usage_log")


def _comparable(record):
    return {key: value for key, value in record.items() if key not in PER_LAUNCH and not key.endswith("_at")}


def test_f2_a_worker_launch_with_plan_readings_at_100_percent_starts_with_the_same_record(project, launch):
    """Guard on the base."""
    tk = s.ticket(project, k.ENGINEER, "C2")
    before = launch(k.ENGINEER, tk)
    s.b.assert_launched(before)
    for rel in PLACES:
        s.b.write(project / rel, READING * 3)
    after = launch(k.ENGINEER, tk)
    s.b.assert_launched(after)
    one, two = _comparable(before.record()), _comparable(after.record())
    differ = {key: (one.get(key), two.get(key)) for key in sorted(set(one) | set(two)) if one.get(key) != two.get(key)}
    assert not differ, f"the launch record changed with the plan readings at 100 percent: {differ}"
    assert after.values("--model") == before.values("--model") and after.values("--effort") == before.values("--effort")


def test_f2_neither_the_launcher_nor_the_hook_names_a_usage_file():
    """Guard on the base."""
    files = sorted((k.REPO_ROOT / "src/gov/launch").rglob("*.py")) + [k.HOOK]
    found = [(str(path.relative_to(k.REPO_ROOT)), name) for path in files
             for name in NAMES if name in path.read_text(encoding="utf-8")]
    assert not found, f"the launcher or the hook names a usage file: {found}"
