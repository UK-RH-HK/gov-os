---
type: probe
task: DAEO-cy5o
reviewer_session: 5c605c2d-28ee-473e-a639-f42f87ccc3a8
implementer_session: 310f4f41-0e50-4ddd-9c2d-bb6c998cc96f
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 8d9d78d935299b0adf743f8a6f729194f9c267e1
---

# Probe record: DAEO-cy5o (W2-57), judgement-only re-probe after W2-07 round 2's merge (DEC-895)

## The lead's note

- **What was probed.** Head `8d9d78d935299b0adf743f8a6f729194f9c267e1` of `w2/W2-57`: the lead's merge of `w2/integrate` at `8555aafc0ba6` (merge `91f5b19af1af`, made for this re-probe) and the lead's checkpoint record `CP-DAEO-cy5o-0012`. This was a judgement-only re-probe (DEC-895 item 2), not a new review round. Its scope was every file the earlier probe judged that changed between that probe's head `8f61bda0eb5c` and this head: one file, `src/gov/close/command.py` (gate (h)'s `recorded` line), read with the change behind it in W2-07's `src/gov/close/gates.py`. Its question: does any change alter what the earlier probe found, or let the close pass something W2-57's change refused (the serial phase's entries, the nightly route, the order of the commit gates before any test)?
- **Why.** The earlier record, `PR-DAEO-cy5o-review-2.md`, is the last review of the ticket's one declared round (DEC-916), a pass at `8f61bda0eb5c`. It went stale when W2-07 round 2's merge into `w2/integrate` (`8555aafc0ba6`, 2026-10-28) changed that line; the orchestrator's probe-impact check on the lead's merge names it ("STALE PROBE: W2-57 (DAEO-cy5o): the merge changes 1 judged file(s): src/gov/close/command.py"). The earlier records stay as they are.
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, session `5c605c2d-28ee-473e-a639-f42f87ccc3a8`, 2026-10-28, effort max. It was started through `gov launch` under its OS sandbox with the reading tools alone (`Bash`, `Read`, `Grep`, `Glob`). The ticket lead, an orchestrator-role session (DEC-137), commissioned and judged it. It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree or in any other tree.
- **The lead's verification at the merge** (code identical at the probed head): full rebuild exit 0; keyword warning 0 files; `gov check` ok, 15 GREEN, 2 YELLOW (`core-decision-citations`, `openspec-validate`, both known at the earlier reviews), no RED; `tests/acceptance/W2-57/` and `tests/unit/close/` in the close's form, 466 passed, 0 failed, and the one serial entry in that scope, 1 passed; collection over `tests` in one process, `16690/16692 tests collected (2 deselected)`, no error. W2-07's run 5 verified the same merged code in full (16,479 passed, 0 failed; serial 180 passed).
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only "yes" with "fails open" or "loses work" fails the probe.
- **Verdict: pass.** Classification (DEC-809): no new finding; one observation, O1, yes / other. Review 2's F1 to F4 stand with their classification, since nothing they judged changed. The lead's judgement agrees with the reviewer's: the merge changed only the comment of the `recorded` line in `command.py`; W2-57's serial phase, its nightly route and the commit gates before any test behave as at `8f61bda0eb5c`, and the widened `recorded` set lets no commit touching W2-57's governed code escape gate (h) in ordinary work.

## The reviewer's record

Verdict: pass

**Head probed:** `8d9d78d93529` on `w2/W2-57`. Its code is identical to the merge `91f5b19af1af`, whose tree is exactly `w2/integrate` at `8555aafc0ba6` (W2-57 was merged into integrate first, W2-07 second). Since review 2's probed commit `8f61bda0eb5c` the branch has gained only review 2's record (`da0240e0563e`), that merge and the lead's checkpoint.

**Step 0:**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o` failed: `OSError: [Errno 30] Read-only file system`, exit 1.
- (b) `git hash-object -w --stdin` worked (exit 0, blob `1ae28402a109`), and so did `git update-index --refresh` (exit 0).
- Identity: `GOV_ROLE` is `independent-auditor` and `GOV_TICKET` is `DAEO-cy5o`; the toplevel is `/home/usain/gov-os-worktrees/W2-57` on `w2/W2-57`; HEAD is `8d9d78d93529`. `git status` showed the 11 placeholder mounts and nothing else, at the start and after every run.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`. The pytest process of the planted cases printed the same path, and their `gov close` ran through the suite's launcher with `PYTHONPATH` set to this worktree's `src/`.

**Classification (DEC-809):** no new finding, and one observation (O1, other). Review 2's F1 to F4 stand unchanged: F1 yes / fails open, feature-gated (DEC-803); F2 yes / other; F3 no / other; F4 no / fails open (a row). No finding is both "yes" and "fails open or loses work" in code in use at this head.

**Intersection of judged and changed files:**
- The judged files are those of the ticket's own commits up to `8f61bda0eb5c`: 25 commits, 48 paths. `git diff --name-only 8f61bda0eb5c HEAD` names 66 paths. They share one file: `src/gov/close/command.py`.
- In that file one line changed, gate (h)'s `recorded` line, and only its comment. Everything else is byte-identical to `8f61bda0eb5c`: the line's code, `_run_tests`, the serial-phase call, `serial.py`, the plugin and `tests/acceptance/serial-only.txt`.
- The change in behaviour is in W2-07's `src/gov/close/gates.py` (`RECORD_PREFIXES` widened, `owner_listed`, `_ever_accepted`). It is used once, at `command.py:201`, and feeds only gate (h) at line 202. The serial call is at `command.py:917`, in `_run_tests`, which the `recorded` set never reaches.
- The merge adds nothing of its own: `git show --cc` is empty for both files.

## Probed and found sound

**1. The serial phase's entries.**
- **P1:** a temporary project whose list has 8 lines, closed by `gov close`. The lines were:
  - a serial entry;
  - a nightly function whose file holds a sibling case;
  - a nightly whole file;
  - an entry with no comment;
  - an entry whose route word is unknown (`overnight:`);
  - an entry routed `Nightly:` (capital N);
  - one entry listed twice, once nightly and once serial;
  - beside them, a plain case and a decision-record commit that only the head's rule subtracts.
- **P1's result:** the ticket closed. The `serial-afterwards` run's `cases` were exactly the five entries not routed nightly, in the list's order: the serial entry, no comment, unknown word, `Nightly:` and the entry listed twice. That run passed 5, and each of the five ran exactly once, alone. So `test_runs` and `cases` state what ran.
- W2-57's own tests at the head pass: the route file 3, the serial unit test 11, the list file 2.
- The real list reads as at review 2: 63 entries, 15 nightly and 48 in the serial phase, which add up to the whole list.

**2. The nightly route.**
- In P1 the routed function and the routed whole file ran in neither phase. The routed function's sibling ran once in a worker, so the file was collected, not ignored. Every run counted 0 skips.
- Nothing outside the route drops a serial entry. The merge touched none of these: `_run_tests`'s filter, `serial.phase`, the plugin or the list.
- P4b: with a commit in range that only the new rule leaves to its decision, the serial phase still ran its one serial entry alone.

**3. The commit gates before any test, and the widened `recorded` set.**
- **P2, one close of a FULL ticket with every commit gate faulted.** It was refused with 10 findings: `PROBE_MISSING`, `TRAILER_MISSING`, `ACCEPTED_HISTORY_REFUSED`, `WORK_WITHOUT_TASK` (6 commits) and `ACCEPTED_RED_REFUSED`. The refusal shows `test_runs: []` and `counted: false`. No planted test ran, the iteration count stayed 0, and the ticket stayed in progress with no close record.
- **Gate (h) still refuses, under the head's rule, each of the six commits planted in P2:**
  - a commit that names no task and changes the governed code (`src/example/serial.py`, standing in for `src/gov/close/serial.py`);
  - a decision-record commit, under an owner's ACCEPTED decision, that changes that code beside the register;
  - a decision-record commit, under an owner's ACCEPTED decision, that changes `tests/acceptance/serial-only.txt` (placed in the ticket's allowed paths) beside the register;
  - a decision-record commit of records only (the ticket file and the register) that names one owner's ACCEPTED decision and one PROPOSED decision;
  - a commit that the exemption list names by a 12-digit id under an owner's decision;
  - a commit that the exemption list names by its full id under a delegated decision.

  Neither rule subtracted any of the six.
- **The only two ways a commit now leaves gate (h)'s input**, both named by DEC-923 item 2:
  - **(i) A decision-record commit of records only, under decisions each ever ACCEPTED.**
    - Of W2-57's own paths, only `.tickets/DAEO-cy5o.md` is a record. `serial.py`, `command.py` and the serial-only list are not records, so this way never carries them.
    - P4: the ticket file was changed under a delegated decision after the probed commit. The probe gate still refused it with `PROBE_INVALID` "the probe is stale", before any test: `counted: false`, no test ran, the count stayed 0. The head's rule subtracts that commit; the old rule did not.
    - P4b: the same change before the probed commit is one the reviewer sees, and the close passed.
  - **(ii) A commit the owner's lists name by its full id, under the owner's ACCEPTED decision naming it**, whatever it changes. P3: a commit with no task that changes the governed code, listed that way, closed. This needs the owner's own list entry and decision, not an agent's ordinary work.
- **W2-57's real range, read-only at the head:**
  - 330 commits besides the ticket's 30. The head's rule subtracts 68 of them and the rule at `8f61bda0eb5c` subtracted 23: 45 more and none fewer. None of the 45 touches W2-57's own paths (its allowed paths, its ticket file, `tests/acceptance/W2-57/`).
  - Gate (h) finds nothing with the subtraction, and also nothing with no subtraction at all.
  - The accepted history holds 45 accepted entries and 0 refused. The path map gained 39 entries under DEC-927 and no other key changed.
  - The probe gate passes.
- **The `recorded` line still sits outside the gate's catch, as it did at `8f61bda0eb5c`.** `owner_listed` adds no way to raise beyond what `judged_history` already ran earlier. An unreadable register reads as "not accepted", and a malformed exemption entry is skipped.
- **The serial-only list is not one of W2-57's own paths**, so gate (h) never judged changes to it for W2-57's close, before or after the merge alike.

**F1 to F4 stand.** None of these changed since `8f61bda0eb5c`: `nightly.py`, `_run_tests`, `serial.py`, the plugin, the list and `src/gov/doctor/command.py`. Their classification stands.

## Findings

None.

## Observations (other, no round)

- **O1. The close itself does not flag review 2's record as stale at this head.**
  - **Done:** I ran the close's probe gate read-only on the real head with review 2's record.
  - **Happened:** it passed. It measured the merges `57e363c589f4`, `855837aef69b`, `8555aafc0ba6` and `91f5b19af1af` as git's own merge on the probed paths (DEC-754).
  - **Should have:** this is the design. The fresh probe is required by DEC-895 item 2's probe-impact check, and this record answers it. Once committed with the head's full id as `probed_commit`, review 2 becomes an earlier round (W2-M209) and this record decides.
  - **Severity:** none.

  Ordinary work: yes, because every merge of integrate into a merged but not closed FULL ticket meets it.
  Consequence: other

## Scratch, refusals, retrieval

- **Scratch:** 10 inodes / 32 KB at start; 18 / 104 KB before the planted closes; 21 / 164 KB after them and at the end. pytest's retention removed every passing case's folder. I did not measure the peak during the runs; at most five small projects existed (about 3 MB and 350 files each), far inside my share of 6 GB and 300,000 files and folders.
- **How the planted projects were built:** with the suites' own builders (W2-07's, built on W2-01's and W1-30's), as W2-57's route case builds its project. Each builder copies this worktree's `src/` and the kernel templates into the temporary project. Nothing of `governance/project/` was copied, and nothing went under `.gov-runtime/`. Each refused planted close opened a repair ticket inside its own temporary project; the worktree stayed clean.
- **Read refusals (DEC-849):** 0.
- **Other refusals:** 1. The code-graph CLI (`codebase-memory-mcp cli list_projects`) could not start, because `/tmp/cbm-daemon-1000` is read-only in the sandbox (chmod, errno 30). One try, not retried.
- **`gov retrieve`:** used once, to ask how the close routes serial-only entries and what gate (h) subtracts. Both facets answered "stale", so I read the named files instead.
- **Code-graph tool:** not used, for the reason above. The callers were found with one targeted search of `src/`: `decision_records` is used only at `command.py:201`, and `serial.phase` only at `command.py:917`.
