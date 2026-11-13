# Brief: independent review, round 1 of at most 2, DAEO-ifgf (W2-121b), gov dispatch part b

You are a fresh, read-only **independent-auditor** session, started by the ticket lead. You write nothing in the
worktree: no file, no commit. Your last message is your record; the lead commits it as the probe record. This brief
was written by hand (`gov context DAEO-ifgf` is over its ceiling for this ticket).

## Identity
- Check: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-ifgf`); `git rev-parse --show-toplevel --abbrev-ref HEAD HEAD` (expect `/home/usain/gov-os-worktrees/W2-121b`, `w2/W2-121b`, head `951dbcfa5cc7…`). Different: stop and say so.
- **Step 0, the sandbox check, reported first in your record:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf','w').write('x')"` must FAIL; (b) `git update-index --refresh` must work. If (a) wrote the file, stop and return.
- Read-only probes are allowed (DEC-1144 (7)): any probe script, planted project or temp state goes under your session's temp folder (`printenv TMPDIR`), never in the worktree. Any pytest you run goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with `TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-121b/src` and `-p no:cacheprovider -o tmp_path_retention_policy=failed` (a busy slot is a wait, not a refusal).

## What you review (the head `951dbcfa5cc7` of `w2/W2-121b`)
The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ifgf.md`. Read all of it: the four KPI lines S1 to S4, the non-goals, and the sections "K9 decided" and "## Interface" (binding, items 1 to 4 and the exit codes). It builds on part a's Interface, in `.tickets/DAEO-cb2b.md`'s `## Interface` section. The CTO's dispatcher `governance/project/orchestration/tools/dispatch/` is a reference for meaning only, never a target. Nothing in `src/` may name it or this repository.
- `git diff 3476e8628..ab5799760 -- src/ tests/unit/` is the engineer's code, commit `ab5799760`: `src/gov/dispatch/landing.py` (new), `heavy.py` (new), changes to `config.py`, `procs.py`, `run.py`, `state.py` and `status.py`, a read helper in `src/gov/resources/slots.py`, and unit tests in `tests/unit/dispatch/test_w2_121b_landing.py`.
- `tests/acceptance/W2-121b/` holds the independent test designer's 48 cases: `a60ee938c`, plus two cases fixed in `ed8aa4904` after the engineer's findings, merged at `951dbcfa5`. You read everything, tests and code alike [DEC-820].
- `git diff --name-only w2/integrate...HEAD` must list only the ticket's `allowed_paths`, plus `tests/acceptance/W2-121b/`, which is the designer's and allowed.

## Questions to answer (each KPI line gets a verdict)
1. S1: does a pass claim only under all four conditions? Is the claim an atomic rename made before the launch? Is a line never sent twice (`land-done.txt`, and a second pass while the batch runs)? Is an unapproved or malformed line never sent, with the malformed one named in the status? Is the finalisation (land-done lines, one inbox item in the Interface's fields, claimed file removed) correct for exit 0 and for a failing exit? What happens when the launch fails, when the dispatcher dies between the claim and the launch, or when `land.txt` is rewritten while a landing is claimed? Can an approval be lost without an inbox item?
2. S2: does a running close block only on a shared ticket (W2 id or ticket id) or while it commits its records (`index.lock`, or tracked changes all under `close_record_paths`)? Does a non-sharing close let the landing go? Does `commit_records(root, paths, message, trailers, attempts=3, wait_s=2)` retry only on another holder's `index.lock`, commit only the given paths, and surface a final failure rather than hide it? Two at once: do both land?
3. S3: is the hold window right: `from` to the marker's mtime after today's `from`, or to `until`; `from` > `until` crossing midnight; no marker meaning until `until`? Is a claimed landing finalised and never stopped during the hold? Are starts and the inbox not held? Do `land_hold` and the status line match the Interface's wording, with exit 0?
4. S4: are the heavy steps the four `job_markers` kinds? Is "in a slot" judged by the step or an ancestor being a held slot's runner (the `/proc` walk honours `GOV_RESOURCES_PROC`, and holders are counted only while flock-held)? Does `heavy_steps: [{kind, pid, slot}]` match, and does a step with no slot add exactly the finding `heavy step outside a slot: <kind> pid <pid>` without changing the exit code? Is the `slots.py` change only a read helper, with `command.py` untouched?
5. Exit codes: is every held landing (busy, unclean tree, wrong branch, conflicting close, nightly) exit 0 with a `land: <reason>` status? Part a's behaviour: is anything in part a's Interface changed?
6. The tests: do the W2-121b cases test the KPI lines as written? Could one pass while its KPI line is false? Are the two fixed cases (`ed8aa4904`) right against the ticket?
7. Generic: does any new key live outside `dispatch.yaml`'s `dispatch:`? Does anything in `src/` name this repository or the CTO's tool?

## The lead's own results (do not re-run the whole suites)
- Store rebuilt at `951dbcfa5cc7` (exit 0).
- `gov accept W2-121b` at `951dbcfa5cc7`: pass, 48 passed, 0 failed (success-1 to -4).
- lead_verify at `951dbcfa5cc7`: 4,694 tests, 2 failed, 7 skipped. Neither red is in this ticket's paths. (1) `tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository`: `docs/changes/W2-176-CIT-P.md`'s front matter is not YAML at the branch's base `e395dd430`, and `w2/integrate` fixed it in `5289bec52`. (2) `tests/unit/resources/test_w2_157_backstop.py::test_l5b_…[last]`: load-sensitive; re-run alone it gave 3 passed.
- The engineer's own reported risks are not given here, so that your reading stays your own.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

For this dispatcher, "fails open" means one of these happens when it must not:
- a landing is sent while it should be held (unapproved, twice, a conflicting close, the nightly hold, an unclean tree or the wrong branch);
- a heavy step outside a slot goes unreported.

"Loses work" means one of these:
- an approval vanishes without being landed or reported;
- a running landing is stopped;
- a record commit is lost;
- the nightly is kept from starting.

A wording or style preference is `other`.

## Rules
- Policy 2: (a) never print a secret or key; (b) never the held-out qualification material's contents; (d) never the hidden half of an evaluation set (`~/gov-os-eval`). You read everything else, tests and code alike.
- DEC-732: any `gov` or Python check runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-121b/src` per command.
- Memory: Read and Grep only (no `gov retrieve` in the sandbox, DEC-1065). Search again once in different words: two searches in all. Grep the register (`docs/DECISION_REGISTER.md`) only by id.
- Command forms: one simple command per Bash call. No `cd ... &&`, here-documents, backticks or `$(...)`. Longer probes go in a script file under your TMPDIR.
- Row W2-L423's rule (DEC-911): write hashes in your record as 12 digits.
- **Refused twice for the same call: stop and say so. Never work around a refusal: report it.**

## Return (your last message; nothing else is read)
1. The twelve fields, each a labelled line.
2. Each finding as `RV<n>: <file:line> <what>`, with its two lines (`Ordinary work: …`, `Consequence: …`) and `Scope: in|out`.
3. Last, exactly one fenced block opened by ```verdict, holding JSON in this form, with one entry per KPI line S1, S2, S3, S4:

```
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "RV1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
In `evidence` give:
- step 0's output;
- the head at your start and at your end;
- `git status --porcelain` at the end;
- `gov.__file__`;
- the read refusals you met.

Refused twice for the same call: stop and say so.
