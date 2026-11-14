---
type: probe
task: DAEO-drhj
reviewer_session: 71669588-4473-4c9d-a058-772b769930dd
implementer_session: 64096c62-be03-471e-be62-87ed0bd9b6ab
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ac18ac2ab7c80b90183d5d37ef9130065f034a65
decisions_applied: [DEC-959, DEC-820, DEC-1164, DEC-968, DEC-801, DEC-808, DEC-1010]
---

# Probe record: W2-104 run 5, the narrow check of `scenario-summaries.md` left out of the session

A fresh independent-auditor session (`71669588-4473-4c9d-a058-772b769930dd`) ran on Opus at high effort, class C2,
with read-only tools. It probed head `ac18ac2ab7c8` of `w2/W2-104` and wrote nothing in the tree. The tree was clean
and at the same head when it finished, and the launcher's tripwire shows no change in this ticket's trees. The only
lines it shows are in `W2-100`'s tree, which is that ticket's own concurrent work. Its brief carried JUDGEMENT.md word
for word.

The implementer was engineer eng-6 (`64096c62-be03-471e-be62-87ed0bd9b6ab`), commit `ac18ac2ab`. It added
`SUMMARIES = "scenario-summaries.md"` beside `SCENARIOS` and `RECORD` in `src/gov/skilleval/harness.py` and passed it
to the session copy's `shutil.ignore_patterns(...)`. It also added one unit case,
`test_w2_104_session_folder_leaves_out_scenarios_records_and_summaries`. The lead made the merge `3ef7c62c4`
(`w2/integrate` at `c82335a401df`). It had no conflicts, and its tree is integrate's tree exactly.

Why: W2-101's review F1 (fails open) found that a hand-written `scenario-summaries.md` was copied into the session
under test (W2-100's and W2-101's interface). The CTO reopened the ticket under DEC-1164 (18).

Scope: only `ac18ac2ab`, plus check 4 on the merge. The harness's other behaviour (runs 1 and 2), runs 3 and 4
(checked at `39ceaec2a` and `97b06de4eba1`) and what integrate brought are out of scope. The verdict is PASS, with no
findings.

## What was probed and found sound (the reviewer's)

1. **The fix:** `run_scenario` leaves out `scenarios.md`, `scenario-records.yaml` and `scenario-summaries.md` when it
   copies the skill folder into the session's `.claude/skills/<name>/` (`harness.py:35,168-169`), and it keeps
   `SKILL.md` and every other file. Nothing else reaches the session. The session prompt carries only the name and
   the situation, and the judgement runs in an empty folder of its own. There is no other copy. `ignore_patterns` also
   matches these names in subfolders. That only keeps more files out (fails closed), and no nested files with these
   names exist.
2. **The unit case:** it plants all five files (`SKILL.md`, `reference.md` and the three left out) and checks the
   stub's file list for scenario 1's session call. The reviewer ran it in a clone. With `3ef7c62c4`'s harness it fails
   with `assert 'scenario-summaries.md' not in ['SKILL.md', 'reference.md', 'scenario-summaries.md']`, and it passes at
   the head.
3. **Nothing else:** the diff is two files. In the harness it is the constant plus one argument; in the tests it is
   the one added case.
4. **The merge:** `git diff c82335a401df 3ef7c62c4` is empty. The marker search finds only string fixtures in
   `tests/unit/hooks/test_live_hook.py`, which came from integrate.
5. **Tests in a clone:** `tests/unit/skilleval` gave 35 passed.
6. **Trailers:** both commits carry `Task: DAEO-drhj`, the matching `Role:` and `Implements: DEC-959, DEC-820` in one
   final paragraph.

## Findings

None. Classification: 0 findings (none reachable in ordinary work that fails open or loses work; no rows).

## The verdict block (the reviewer's, as returned)

```verdict
{"kpis": [{"kpi": "w2-104-run5-narrow", "verdict": "pass", "findings": []}]}
```

## What would reverse it (the reviewer's)

- Summaries found anywhere other than the skill folder's top-level `scenario-summaries.md`, while the interface puts
  them there.
- Any other route that puts the skill folder's files in front of the session under test.

## The lead's verification at the probed head

- `gov accept W2-104 --root /home/usain/gov-os-worktrees/W2-104`: pass, 43 passed, 0 failed, 0 skipped. The code
  under test was this tree's `src/` (`gov.__file__`: `/home/usain/gov-os-worktrees/W2-104/src/gov/__init__.py`).
- `tests/unit/skilleval`: 35 passed, including the new case.
- The rebuild (`rebuild_slot.sh`) exited 0.
- The scoped run (DEC-968, `lead_verify.sh`, 140 selected files) gave 5732 tests: 5725 passed, 1 failed, 6 skipped. The
  failure was `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`:
  2 of 3 `released` lines were written while the machine was under load. Run again alone with a short TMPDIR, it
  passed (1 passed). It is load-sensitive and outside this ticket's paths.
