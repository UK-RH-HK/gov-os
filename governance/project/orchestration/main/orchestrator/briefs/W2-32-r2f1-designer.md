# W2-32 R2-F1 — re-point a strict xfail's reason to W3-P22 (DAEO-0pyc; DEC-1083 (3), D9-FATES)

You are an independent test designer for **W2-32** (`.tickets/DAEO-0pyc.md`). The job is small and exact.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-32-r2f1`, branch `w2/W2-32-r2f1`, made from `w2/integrate`.
- You write only `tests/acceptance/W2-32/test_w2_32_s7_dec1067.py` and `tests/acceptance/W2-32/README.md`.

## What to do
D9-FATES (DEC-1083 (3)) parked W2-32's round-2 finding R2-F1 (nested parents) in Wave 3 as row **W3-P22**
(`docs/plan/WAVE_3_PARKING.md`, line 28; read it). Its case
`test_w2_32_s7_dec1067.py::test_nested_parents_send_no_line_twice_and_name_every_span_left_out` stays
`xfail(strict=True)`, so it still turns red when R2-F1 is fixed. Only its reason changes:
1. The `reason=` of its `xfail` mark (line 195) and the `Rewrite-Reason:` comment above it (line 193) name **W3-P22**
   and **DEC-1083 (3)** in place of "deferred to D-9". Keep `park/W2-32-R2-F1`. The comment line reads
   `# Rewrite-Reason: DEC-1083 (3)`, followed by one plain line on what changed.
2. The README's S7 row (line 137) and its Round 11 section (line 369 onwards) say the same: parked as W3-P22 by
   DEC-1083 (3), strict xfail kept.
3. Nothing else changes: no other case, no marker, no assertion.
4. Run the one file through the heavy slot that `EMG-common.md` names. Record that the case is still `xfailed` and the
   rest of the file passes as before.

## Rules
- No GPU, no model, no measure. Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-32-r2f1` with
  `git commit -m "..." --trailer "Task: DAEO-0pyc" --trailer "Implements: DEC-1083" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1083 (3)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with the commit, the file's test counts, and the diff's line count.
