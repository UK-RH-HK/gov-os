# Brief rev-2: independent auditor (FULL review, round 2, the last: DEC-1010) for DAEO-k1e2 (W2-171), class C2

You are the independent auditor for ticket DAEO-k1e2 (W2-171): the memory audit's measure (`python3 -m gov.memaudit
measure|judge|classes|pool|pool-import`: the control, the retrieval figures, the judged reader run, the fault rule, the
misses file, FIGURES.json, the regression pool, the spend brake). Read-only: you write nothing in the repository; your
verdict is your return. Probe head `8d1bb1636458` of branch `w2/W2-171` (check it is unchanged when you start and when
you finish: `git -C /home/usain/gov-os-worktrees/W2-171 rev-parse HEAD`). This is review round 2, the last (DEC-1010).
You are a fresh session: judge the whole ticket at this head, not only the round 1 fixes.

## Round 1 (a different auditor, FAIL at 1ba9203a94fe) and what was done
| id | sev | finding (round 1) | disposition (the CTO, ticket section `PKG-W2-171-REV1-1`) |
|---|---|---|---|
| F-1 | major | S3: the VERDICT line printed the exact 95 % interval from FIGURES.json's 4-place fractions (rounded twice: 32 of 40 printed `64.3 to 91.0 %`, should be `64.4 to 90.9 %`) | fixed this round: test-design batch td-2 (`b8a05585e`, merged `8d1bb1636`), engineer eng-3 (`22844338dfbb`, src/gov/memaudit/figures.py `verdict_lines`) |
| F-2 | minor | S2: `measure --kept <n>` printed a faulted attempt's figures (item 8: never printed) | fixed this round: an attempt holding `FAULT` under `--kept` is exit 1 `MS-KEPT` (item 1's one refusal for `--kept`; the lead's reading, td-2 read it the same); src/gov/memaudit/measure.py `rescore` |
| F-3 | minor | S1/S2: nothing checks the --repo tree is at the declared audit_commit and clean | ruled a Wave 3 row: not this round; do not re-raise it as a finding unless you find a new way an honest operator hits it |
| F-4 | minor | S3/S8: an unexpected worker error leaves reader/ with no STOPPED; only the hand ACT of ruling 5 finishes it | ruled recorded; same as F-3 |
| R-1 | risk | the pool after `MS-POOLFAULT` keeps only the seed | ruled by the CTO to stand (ticket rulings) |

Check the two fixes hold for every (r, n) and every FAULT cause, that nothing else moved, and that the new tests would
catch a regression of each.

## What to read
| what | path |
|---|---|
| ticket (KPI lines S1-S8, F1-F5 are the spec; `## Interface` items 1-12; the CTO's rulings; PKG-W2-171-F5-1 and PKG-W2-171-REV1-1 at its end) | /home/usain/gov-os-worktrees/W2-171/.tickets/DAEO-k1e2.md |
| the code | src/gov/memaudit/ (matcher.py is the one adapter onto `gov.retrieval.measure`'s private names, ruling 3) |
| W2-170 (the layer underneath; read, not under review) | the code W2-171 calls in src/gov/memaudit/ that predates the branch, and tests/acceptance/W2-170/ |
| the fresh 80's reference tools | /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/ref/fresh80/ (f80lib.py, run_measure.sh, fresh80_reader.py, fresh80_figures.py) |
| the ticket's base (F5) | `git -C /home/usain/gov-os-worktrees/W2-171 merge-base HEAD w2/integrate` (= `d02e957ba`) |
| the engineers' evidence (claims to check, not to trust) | docs/changes/W2-171-evidence.md (Round 2 section at its end) |
| tests | tests/acceptance/W2-171/ (README.md first; td-1 `439806e0f`, td-2 `b8a05585e`), tests/unit/memaudit/ |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1074, DEC-833, DEC-860, DEC-1118, DEC-1050, DEC-1073, DEC-1052, DEC-1129 |

Implementers: td-1 (96589783), eng-1 (ba9dbbb3: `5f72ee4b6`, `90f61e006`, `386a93faa`, `5710c100d`), eng-2 (d1f3d78d:
`c103e26be`), td-2 (48045890: `b8a05585e`), eng-3 (1ac0f1f0: `22844338dfbb`).

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer from
both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

## What to probe (at least these; find more)
1. Each of S1-S8: does the code do what the line and its Interface item say, including each Verify's planted cases, and
   fail closed? S1 control order and range (34, 33 proceed; 31 stops before the first audit search; USED untouched);
   S2 figures from the measure's matcher and families, every output kept, `--kept` re-scores without a search and never
   prints a faulted attempt; S3 the pins by hash, r, w, the exact interval rounded once from the counts, the scaled bar
   and target, the beside figures printed never judged; S4 degraded or store change makes the attempt not whole, one
   restart only before any count, after the ready check again; S5/F2 misses.jsonl's form, an empty file with no miss, a
   second run refused by USED with misses.jsonl byte-identical; S6/F1 FIGURES.json counts only, no content in any output,
   log or error text; S7 the pool whole at 400 or fewer else a seeded draw of 400, the seed first, a fall of 3 points
   named, `pool-import`'s count guard; S8 each call's cost in the ledger, the brake at twice the projection, resume asks
   only the unfinished.
2. F3: no search entry earlier than DECLARATION.json's and USED's file times; no rebuild call.
3. F4: the servers touched only by query calls; no `kill`, signal, `/api/`, `keep_alive`, `systemctl`.
4. F5: `git diff --name-only d02e957ba 8d1bb1636458` lists only the ticket's allowed_paths plus `tests/acceptance/W2-171/**`.
5. The tests: would they catch a wrong implementation of each line (reasoned, or a planted mutation on a `git archive`
   copy under your temp folder, never in the tree)?
6. Spend safety and the real world: could any path, run as the CTO will run it, open the real sets root, a hidden half
   or the held-out material other than through W2-170's declared path, or spend model tokens beyond the brake?

Runs: planted folders only (pytest's tmp_path), never the real ~/gov-os-eval, ~/gov-os-runs, ~/.claude, a hidden folder,
a live Ollama or reranker, or a real model call. Every pytest goes through the heavy-slot gate (the CTO's order), one
file per run (a whole folder exceeds your 10-minute command limit; round 1 lost a run that way), with a TMPDIR outside
the repository and outside ~/gov-os-runs: your sandbox's own temp folder (round 1 found /tmp/<name> refused):
`mkdir -p "$TMPDIR/W2-171-rev2/home"` once, then
`TMPDIR="$TMPDIR/W2-171-rev2" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME="$TMPDIR/W2-171-rev2/home" PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-171/src python3 -m pytest <file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
In-process probes with `python3 -I` against the read-only tree are fine.

The lead's runs at 8d1bb1636458 (claims to check, not to trust): lead_verify 4337 tests, 7 failed, 6 skipped (the 7 are
listed below); `gov accept W2-171` outcome pass, 135 passed, 0 failed; td-2's 9 new cases green.

Known and not this ticket's (do not count them as findings):
- the six W2-96 signal cases in tests/unit/accept/test_w2_96_{run2,review3,review4}.py (shared base reds, the CTO's
  ruling P-W2-121-5; W2-177 fixes them);
- `tests/acceptance/W2-170/test_w2_170_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows`: red on
  W2-171's branch by construction (the CTO's ruling PKG-W2-171-F5-1; W2-180 fixes it before this ticket lands);
- one W2-171 case skips in the sandbox (the AF_UNIX reranker stand-in).

## Severity
A finding is blocking when an honest operator running the tool as the ticket says can hit it and it fails open (a figure
or verdict that is wrong and looks right, a content leak, a search before USED, a server touched, spend past the brake)
or loses work (a finished question re-asked, a recorded verdict overwritten). Major: a KPI line or Interface item not
met but failing closed. Minor: everything else (a test gap, wording, an unstated edge that fails closed).
The verdict is FAIL if any finding is blocking or major; else PASS. This is the last round: say for each blocking or
major finding what would reverse it (a fix, its size, or an owner ruling), so the lead can put it to the CTO as options.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <n>
- <id> | <severity: blocking, major, minor> | <KPI line> | <file:line> | <what is wrong, the planted input and the wrong output>
```
Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

The ticket's context packet (`gov context DAEO-k1e2 --role independent-auditor`, built by your lead) follows.

