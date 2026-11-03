# PR-EMG-nightly-dec1045: review of the nightly's full-scan setting taken from the DEC-1045 switch

Reviewer: fresh, read-only. Judged by JUDGEMENT.md (ADR-0001 threat model; the two questions; the two lines per finding).
Change: uncommitted diff of `governance/project/orchestration/nightly/nightly.sh` and `test_nightly.sh`.

## Answers to the questions

1. Same suites and steps as before? Yes. The diff touches only the lines before the rebuild: it adds a `FULL_SCAN=$(...)` assignment, one note line to run.txt when off, and swaps the literal `1` for `"$FULL_SCAN"` on the rebuild line. The suites, the seed step, the gates, the parallel and serial runs and the verdict are unchanged. N11 still holds (the setting appears only on the rebuild line).
2. Can it fail the night without a verdict?
   - Reader missing: `secrets_switch.py` lives in the git-ignored `.gov-runtime/scratch/orchestrator/tools/` (it is present now). If it were missing, `python3` fails, the `||` writes a line to run.txt and exits 2. The EXIT trap then sends the P1 NIGHTLY-NOT-RUN ping. That is a loud stop, not silent, and by design (fails closed). See F1.
   - `$ORCH` unset: no. `ORCH=` is assigned at line 26, well before; there is no `set -u`.
   - `set -e`: there is no `set -e`/`set -u` in the script, so no interaction. The `$(...) || {...}` form catches the failure explicitly. A failing assignment's status is the substitution's status, so `||` works.
   - Quoting of `$CLONE`: the clone path is interpolated into a single-quoted Python literal inside a double-quoted shell string. Spaces are fine. A path containing a single quote would break it, but `RUNS` and `STAMP` are fixed, machine-controlled names, so this is not reachable in ordinary work.
   - Python `yaml` is available to the system `python3` (PyYAML 6.0.1).
   - I ran the exact command against the main tree: it printed `0` (the switch is `scan: off`, tracked in `w2/integrate`, so the clone has it).
3. Value passed: exactly `1` or `0` (`print(1 if ... else 0)`). cache.py's `full_scan()` treats "" and "0" as off and anything else as on, so `0` is off and `1` is on. `$(...)` strips the trailing newline. If the reader printed anything else the stop would not catch it, but it cannot print anything else without raising (a raise gives a non-zero exit).
4. Lost work: none. The stop happens after the clone and the seed and before any suite, and nothing is written that a later run needs; a rerun starts fresh.

## Verification
- `bash -n nightly.sh`: OK.
- `test_nightly.sh` (one run): PASS, N1-N19, C1-C3, K1-K17, G1-G11, E1-E2, S1-S7, R1-R3.

## Findings

### F1: the switch reader is an untracked, git-ignored scratch file the nightly now depends on
Scope: in (the change introduces the dependency).
Ordinary work: no, because the file exists and is the CTO's own tool. It would go missing only if someone deleted or renamed the scratch tool (or `NIGHTLY_SEED`-style relocation). Even then the night stops loudly (exit 2 and a P1 ping), not silently, and the stop is the intended fail-closed behaviour.
Consequence: other (a night that does not run, announced by the ping; no work lost, nothing passes open).

### F2: N10 checks the text of the script, not the behaviour
Scope: in.
Ordinary work: no, because it is a test-strength note, not a path an honest agent hits; the rebuild line, the reader line and the stop line are each asserted, and the value was checked by hand above.
Consequence: other.

## Verdict

```verdict
{"kpis": [{"kpi": "nightly-dec1045", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
