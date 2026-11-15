---
type: probe
id: PR-DAEO-2bdu-s27-p1
task: DAEO-2bdu
round: "run 9b: the narrow independent check (DEC-1154) of run 9's P-1 path case, the DEC-1045 switch's recorder re-pointed at folder mode (DEC-1156 (7))"
reviewer_session: c5957926-d7b4-4cc5-94fc-be47f6e8f8b8
implementer_session: "eng-17 ba8fa46f-fb51-40ad-be2e-c55c28a34834"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: f0a377b5ba0452fc911072b54c748daabafb7bc8
decisions_applied: [DEC-1154, DEC-1156, DEC-1183, DEC-1178, DEC-1010, DEC-820, DEC-1065, DEC-1142]
---

# Probe record: W2-88 (DAEO-2bdu), run 9b: the DEC-1045 switch's recorder sees folder mode: PASS

## The lead's judgement and runs
- **What changed.** Run 9's verify found `tests/unit/secrets_check/test_dec1045_switch.py::test_on_the_filter_gives_every_governance_file_to_gitleaks` red: its `scans` fixture recorded `_holds_secret`, which folder mode's `indexable` no longer calls. The CTO widened the allowed paths by that one file (DEC-1156 (7), `4b78914fb`). A fresh engineer (eng-17, `ba8fa46f-fb51-40ad-be2e-c55c28a34834`, claude-opus-5-5, effort high, launched through `launch_worker.sh` / `gov launch` under the OS sandbox, the promotion "a fail-open finding" applying), given the failing output only, re-pointed the recorder: a text is recorded when its batch folder is judged (`_Folder.judge` stood in, `_Folder.add` wrapped and still writing), and the record of clean texts is switched off in the fixture. Commit `f0a377b5ba04` changes that one file (+21 -1), no test function and no `src/` file, `Rewrite-Reason: DEC-1183 (2), DEC-1156 (7)`.
- **Who checked.** A fresh, read-only Independent Auditor (`c5957926-d7b4-4cc5-94fc-be47f6e8f8b8`, claude-opus-5-5, effort high, started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-15 20:05 with `--owner-named DEC-1154`, TMPDIR under `/tmp/`), its brief carrying `governance/project/briefs/JUDGEMENT.md` word for word (`.gov-runtime/scratch/lead/briefs/nc-s27p1.md`). Its tripwire shows no change in this ticket's trees (one untracked file in W2-111's tree, that ticket's own lead's).
- **The verdict stands as PASS** (success-27, failure-6), no finding. The revised case is red on six planted copies (a text never added, a folder never judged, answered as remembered, a batch skipped, the product file handed over, the bytes altered) and green on the unplanted copy and on the head. N1 to N3 are notes; N3 (the rebuild report case's `on` half does not by itself show content hand-over) can be a Wave 3 row.
- **The lead's verification at the head `f0a377b5ba04` (outside the sandbox, through heavy_slot):**
  - the file: **22 passed**; `tests/unit/secrets_check`, `tests/unit/secrets` and `tests/unit/adopt/test_w2_88_folder_assess.py`: **77 passed**; the S27 acceptance modules (`test_w2_88_scan_folder.py`, `test_w2_88_scan_speed.py`): **38 passed** (`.gov-runtime/scratch/lead/log/t9b.txt`);
  - the rebuild (`rebuild_slot.sh`): ok, complete, four digests (`log/rebuild-9c.txt`);
  - lead_verify: parallel 7,474 tests, **1 failed**, 7 skipped; serial 49 passed (`log/verify-9c-f0a377b/`). The one red, `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`, passes alone (`log/alone-9c-w2112.txt`, 1 passed): load-sensitive, as at run 9's `ab333d523` (no retrieval file changed since). The run 9 red `test_dec1045_switch` is green.

## The auditor's return (unchanged)

task: DAEO-2bdu (W2-88), run 9b: the narrow check of the DEC-1045 switch's recorder (DEC-1154)
status: DONE. The revised case is red on all six planted copies and green on the unplanted copy and on the head. I found no finding.
work_completed: Ran the step-0 sandbox check and the identity checks. Read the diff and the ticket's two commits. Planted six honest mistakes in copies of the head's `src` and ran the case on each, on the unplanted copy, on the head tree, on the head copy with a cache file named, and on the base's old recorder against the head code. Checked that no assertion was weakened and that the commits stay in scope.
files_changed: none
evidence: `git diff ab333d523cff f0a377b5b -- tests/unit/secrets_check/test_dec1045_switch.py` (only the `scans` fixture changes); `src/gov/secrets/__init__.py:188-190,326-415,490-558`; `src/gov/secrets/cache.py:53-62,94-114`; `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-2bdu.md:45,100+`; the probe copies are under `$TMPDIR/aud9b/` (p1 to p6, h, base)
tests: the one case, through heavy_slot with `-m "not local_only" -k "not real and not green_here and not time_limit"`: p1 to p6 each failed (6 of 6 red); the unplanted copy passed; the head tree passed; the head copy with `GOV_SECRETS_CACHE` named passed; the base recorder on the head code failed (the run 9 red, reproduced). The `-k`/`-m` exclusion leaves nothing out of this single case. I did not re-run the whole file or the suites; the lead runs those.
discoveries: The `scans` fixture's `GOV_SECRETS_CACHE=""` overrides a cache path set by the caller. Proof: with a path named and gitleaks on PATH (`/home/usain/.local/bin/gitleaks`), no record file was created. The rebuild report case's `on` half would still pass if folder mode never judged its folder, because path scans and `_count` fill `scans` and `secrets_counts` anyway (see Notes).
risks: none for this change
lessons: A recorder that records at the judge step, with the folder's listing checked against what was written, catches skipped writes, skipped judges, cache shortcuts, skipped batches, wrong files and altered bytes in one exact-equality assertion.
proposed_decisions: none
unresolved: none
recommended_next_action: The lead adds this check and its own runs (t9b, verify-9c) to the probe record. If those are green, land run 9b.

# W2-88 (DAEO-2bdu): narrow check of run 9b's path case (the DEC-1045 switch's recorder, DEC-1154)
probed_commit: f0a377b5ba0452fc911072b54c748daabafb7bc8
base: ab333d523cff

## Sandbox and identity
- **Step 0 (EMG-d4b-launched.md):**
  - (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` was refused with `OSError: [Errno 30] Read-only file system`, and no file exists.
  - (b) `git hash-object -w --stdin` worked (object `1ae28402a1…`) and `git update-index --refresh` exited 0.
- **Environment:** `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`.
- **Identity:** HEAD was f0a377b5ba0452fc911072b54c748daabafb7bc8 with an empty `status --porcelain`, at the start and again at the end.
- **ps check:** `ps … | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- Every probe ran in `$TMPDIR/aud9b` (`/tmp/gov-launch-fh_4ud23/claude-1000/aud9b`) through heavy_slot. Nothing was written in any repository apart from step 0's object and index refresh.

## The planted copies
Each copy is `git archive` of the head (`src`, `tests/unit/secrets_check`, `template/.gitleaks.toml`). Each plant changes one line of `gov.secrets.indexable` in `src/gov/secrets/__init__.py`. The test's `REPO = parents[3]` runs the copy's own `src`.

| Copy | Plant | Case result |
|---|---|---|
| p1_never_added | `folder.add(...)` replaced by `verdicts[index] = True`: allowed, never written to the batch folder | **red**: `[] == [('content', b'Ordinary text.\n')]` |
| p2_never_judged | `found = folder.judge(rules) if given else []` replaced by `found = [[] for _ in given]`: written, folder never judged | **red**: `[] == [...]` |
| p3_remembered_no_scan | `if True or cache.remembered("content", …)`: answered as remembered clean, no scan | **red**: `[] == [...]` |
| p4_batch_skipped | the first batch's candidates set allowed, only `batches[1:]` submitted | **red**: `[] == [...]` |
| p5_product_handed | the content read from the first non-governance asked path (`exports/b.md`) in place of the governance file | **red**: `[('content', b'Product.\n')] != [('content', b'Ordinary text.\n')]` |
| p6_text_altered (extra) | `folder.add(_forms(content.strip()))`: the bytes handed over are not the file's | **red**: `b'Ordinary text.' != b'Ordinary text.\n'` |
| h (the unplanted copy) | none | **green**, 1 passed |
| the head tree (`/home/usain/gov-os-worktrees/W2-88`) | none | **green**, 1 passed |
| h with `GOV_SECRETS_CACHE=$W/c.db` | none | **green**; no record file created |
| base (ab333d523cff's test file on the head code) | none | **red**: `[] == [...]` (run 9's red reproduced) |

In every red, the first assertion (`indexable(...) == ["notes/a.md"]`) held and the recorder assertion failed. So each red is "allowed but not handed over", not a changed verdict.

## What I probed and found sound
- **The recorder sits where the hand-over happens.**
  - `written` (wrapping `_Folder.add`) only notes `chunks[0]` on the folder instance and then calls the real `add`, which writes the file.
  - Only `judged` (standing in for `_Folder.judge`) appends to `given`. A text written but never judged is not recorded; p2 shows this.
  - `judged` also checks that the folder's listing is exactly `0..n-1` for the texts noted, so a text noted but not written, or an extra entry, fails.
  - It returns one empty finding list per text, so the real `_held` and `cache.remember` paths still run.
- **The cache cannot decide the case.**
  - The fixture sets `GOV_SECRETS_CACHE=""`. `cache.location()` then returns None, `cache.engine()` returns None, `remembered()` returns False and `remember()` does nothing (`cache.py:53-62,94-114,175-208`).
  - Without the fixture, pytest's `PYTEST_CURRENT_TEST` gives None as well.
  - Probed: with a cache path named by the caller and a real gitleaks on PATH, the case stayed green and no record was created, so the fixture's override wins.
  - A plant that answers from the record (p3) is red.
- **`chunks[0]` is the file's bytes as they are.** `_forms(content)` returns `[content]`, or `[content, content without NUL bytes]` when NULs are present (`__init__.py:188-190`). `indexable` passes `_forms(content)` of `real.read_bytes()` (`:527,537`). p6 shows that altered bytes are caught.
- **Nothing weakened.**
  - The diff touches only the `scans` fixture: its docstring, `setenv`, `written`, `judged` and two `monkeypatch.setattr`.
  - Every test function, including the case's four assertions (`:139-144`), is byte for byte as at ab333d523cff.
  - The `holds` and `scan` stand-ins are kept, so `path_holds_secret`'s `("path", …)` record and the store scan's `("store", …)` record are as before.
  - The off cases' `scans == []` (`:147-172`) and the rebuild case (`:277-301`) keep their assertions. They now also fail if folder mode writes or judges anything while the switch is off.
  - No case removed, skipped or marked. The engineer's commit changes only this file (`git show --stat f0a377b5b`: 1 file, +21 −1).
- **Scope.**
  - The engineer's commit f0a377b5b changes `tests/unit/secrets_check/test_dec1045_switch.py`, which is in the ticket's `allowed_paths` (`.tickets/DAEO-2bdu.md:45`, added under DEC-1156 (7)).
  - Its trailers form one final paragraph: `Task: DAEO-2bdu`, `Role: engineer`, `Implements: DEC-1183, DEC-1178, DEC-954, CAP-44.b, CAP-17`, `Rewrite-Reason: DEC-1183 (2), DEC-1156 (7)`, `Co-Authored-By`. Every `Implements:` id is in `sources:`.
  - The CTO's widening commit 4b78914fb is an orchestrator record (see Notes).
- `_Folder`'s only other user is `gov.adopt.assess:177`. It is outside this case and untouched by this change.

## Findings
None.

## Notes, not findings
- **N1 (the CTO's widening commit 4b78914fb):**
  - It reached `w2/W2-88` through the merge of `w2/integrate` (68b678206), not on the first-parent line.
  - It changes `.tickets/DAEO-2bdu.md` and `governance/project/orchestration/packages/DECIDED-NOT-DONE.md`, which are not in the ticket's `allowed_paths`, and its `Implements:` names DEC-1156, which is not in `sources:`.
  - It is the orchestrator's record of a widening under DEC-1156 (7) (`Role: orchestrator`, `Task: DAEO-2bdu` in the final trailer paragraph), not a worker's commit. The `allowed_paths` and `sources:` rule binds the ticket's workers, so I read it as in order.
  - Ordinary work: no, because recording a widening is the CTO's own act under DEC-1156 (7) and touches no product or test code. Consequence: other.
- **N2:** DEC-1156 (7) says "a test designer writes the revision". Here an engineer revised a unit test, which is not under `tests/acceptance/**` (MR-3). This matches the ticket's earlier unit-test path cases (R8-1: "an engineer revises only that case").
  - Ordinary work: no, because the file is a builder unit test, not an acceptance test, and the routing is the CTO's, recorded at `.tickets/DAEO-2bdu.md:384`. Consequence: other.
- **N3:** The rebuild report case's `on` half (`assert scans and … set(result["secrets_counts"]) == {"content", "path"}`) would still pass under p2. Path scans fill `scans`, and `_count("content", "scanned")` runs before the judge. That case's assertions are unchanged and were never meant to show content hand-over; the case under check does show it. This could be a Wave 3 row if anyone wants the rebuild case to show content hand-over too.
  - Ordinary work: no, because only a mistake that is already caught by the case under check would get past it. Consequence: other.

```verdict
{"kpis": [{"kpi": "success-27", "verdict": "pass", "findings": []}, {"kpi": "failure-6", "verdict": "pass", "findings": []}], "overall": "pass"}
```
