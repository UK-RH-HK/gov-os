# Brief eng-3: engineer for DAEO-k1e2 (W2-171), review round 2 fix, profile FULL, class C2

You are a fresh engineer for ticket DAEO-k1e2 (W2-171: the memory audit's measure, `python3 -m gov.memaudit
measure|judge|classes|pool|pool-import`). The code exists on your branch (earlier engineers' commits) and the
independent test designer's acceptance tests are merged at tests/acceptance/W2-171/ and green. The FULL review round 1
returned FAIL with the two findings below; the CTO ruled them fixed in this round (ticket, section `PKG-W2-171-REV1-1`).
A test designer is writing acceptance cases for them in parallel in another tree; you will not see them before you
finish. Fix the two behaviours, conforming to the ticket's `## Interface` (items 1-12) and the CTO's rulings under it,
with unit cases in tests/unit/memaudit.

You never edit tests/acceptance/ (the test designer's). If the Interface does not settle a behaviour, do not invent:
return PACKAGES with the question, the options with cost, your recommendation, your confidence and what it blocks. Keep
every case of tests/acceptance/W2-171, tests/unit/memaudit and tests/acceptance/W2-170 as it is (green, except W2-170's
`test_f5_the_branch_changes_only_paths_the_ticket_allows`, which is red on any W2-171 branch until W2-180 lands: leave
it alone).

## The two behaviours to fix

**F-1 (major, S3, Interface item 8; the reviewer's place: src/gov/memaudit/figures.py:154 with :117).** The VERDICT
line prints its exact 95 % interval from `FIGURES.json`'s 4-place fractions, so it is rounded twice: 32 of 40 prints
`64.3 to 91.0 %` where the exact bounds (64.352 %, 90.948 %) print `64.4 to 90.9 %`; 78 of 79 prints `93.2` where
`f80lib.exact_interval` gives 93.148 (printed 93.1 by fresh80_figures.py). At n = 40, r = 8, 31 and 32 are wrong.
The behaviour: the printed `lo`/`hi` are the exact Clopper-Pearson bounds of (r, n), computed from the counts and
rounded once to one decimal; `FIGURES.json`'s `verdict.interval_exact` stays `[lo, hi]` as fractions to 4 places
(item 10). Unit cases: at least r = 32, n = 40 (`64.4 to 90.9 %`) and r = 78, n = 79 (`93.1 to 100.0 %`), and a sweep
that the printed bounds equal `f"{100*x:.1f}"` of the unrounded bounds for every r at n = 40.

**F-2 (minor, S2, Interface items 1, 2 and 8; the reviewer's place: src/gov/memaudit/measure.py:181).** `measure --kept
<n>` re-scores and prints `RETRIEVAL attempt <n>: ...` for an attempt that holds `FAULT` (for example a degraded
attempt-1 whose kept count is whole, after which attempt-2 counted). Item 8: "a faulted attempt's figures are never
printed"; item 1: `--kept` exits 0 or 1 `MS-KEPT`, never 3. The behaviour (the lead's reading, the one refusal item 1
gives `--kept`): an attempt folder holding `FAULT` gives exit 1 and `MS-KEPT`, no `RETRIEVAL` line, nothing written,
nothing searched; a whole attempt's `--kept` is unchanged. Unit case for each.

Change only what these need. Do not touch F-3 (the --repo tree against audit_commit: a Wave 3 row) or F-4 (a worker
error leaving reader/ without STOPPED: recorded).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-171 |
| branch | w2/W2-171 |
| your allowed paths | src/gov/memaudit/**, tests/unit/memaudit/**, docs/changes/W2-171-evidence.md |
| the ticket (read its Interface whole, then PKG-W2-171-REV1-1 at the end) | /home/usain/gov-os-worktrees/W2-171/.tickets/DAEO-k1e2.md |
| the acceptance tests (read, never edit) | tests/acceptance/W2-171/ (README.md first) |
| the fresh 80's reference tools (exact_interval) | /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/ref/fresh80/ |

Search with the Read, Grep and Glob tools; search once more in different words if the first does not answer, then
answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the
real sets root (`~/gov-os-eval`), the real runs folder, a hidden half or the held-out material; never a real search
or model call.

## Rules
- Every pytest through the heavy-slot gate (the CTO's order), one folder or one file per run, with a TMPDIR outside the
  repository and outside ~/gov-os-runs (your sandbox's own temp folder: `mkdir -p "$TMPDIR/W2-171-eng3"` once):
  `TMPDIR="$TMPDIR/W2-171-eng3" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-171/src python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Run your unit cases first; then tests/unit/memaudit, tests/acceptance/W2-171 and tests/acceptance/W2-170 once each
  before your last commit.
- Update docs/changes/W2-171-evidence.md with what changed and why (round 2, F-1 and F-2).
- Literal paths only as write targets. No merge, no push, no edit outside your paths.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-k1e2" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1097, DEC-833, DEC-860" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line of each folder run) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

The ticket's context packet (`gov context DAEO-k1e2 --role engineer`, built by your lead) follows.

