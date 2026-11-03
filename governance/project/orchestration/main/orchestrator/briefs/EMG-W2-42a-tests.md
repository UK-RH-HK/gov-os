# Emergency task: W2-42a's acceptance tests, the replay of every logged refusal and the planted cases (independent test designer)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** independent test designer (MR-3). **Worktree:** `/home/usain/gov-os-worktrees/W2-42a-tests`, branch
`w2/W2-42a-tests` (from `w2/integrate` at `a58ba344`). **Ticket:** `DAEO-03ub` (W2-42a, FULL). TMPDIR
`/tmp/gov-os-emg-w242a-tests`. Write only under `tests/acceptance/W2-42a/`.

## Why (the owner, DEC-1040 item 2, 2026-11-02 ~20:15)
72 of 78 guard refusals since ACT 1 were false. The owner brought W2-42a into the emergency: the parser's misreadings
fixed (heredocs, loops and substitutions, and the read-listing rule's misreads of literal paths), "replayed against
every logged refusal (each false one must now pass, each true one must still be refused) and the planted cases, with
one review"; live with re-pin window 2. **The five rules stay as they are; only the misreadings go.**

## Independence
An engineer builds the fix in parallel in `~/gov-os-worktrees/W2-42a`. **Never read that worktree, nor any file its
branch `w2/W2-42a` changes** (DEC-820 (c)). Read the ticket `.tickets/DAEO-03ub.md` (its 11 success lines and 2
failure lines are your spec), DEC-1040, DEC-1028 item 4, DEC-958 and DEC-953 item 2 in `docs/DECISION_REGISTER.md`,
the package `governance/project/orchestration/packages/P1-GUARD-PARSER-W2.md`, and the existing code at its base
(`git show w2/integrate:src/gov/guard/reads.py`, `decide.py`). Retrieval only from the integration store:
`cd ~/gov-os-worktrees/W2-00-store && gov retrieve "<question>"` (it may lag; the base's files are the authority).

## The fixtures
- **The logged refusals:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl`
  (one JSON line each: `key` = the tool-use id, `transcript`, `cwd`, `tool`, `form` = the first 200 characters only,
  `rule`, `verdict` true | false-positive). Recover each refusal's **full** tool input from its transcript (the
  `tool_use` block whose id is the key) with a script. Keep, per refusal: tool, full input, cwd, the session's role
  (from the transcript's subagent type when it is a subagent, else the session's `GOV_ROLE`), its verdict and the
  rule that refused it. Leave out any line you cannot recover, named with the reason. **Secrets:** run gitleaks on the
  fixture file before you commit it (`gitleaks dir <file> --no-banner --redact`); a hit is replaced by a harmless
  literal of the same shape, named in the README; never print a secret.
- **The planted cases:** ACT-GUARD-FIX-3's test file and corpus, reviewed copies in
  `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-3/`
  (`test_guard_fix_3.py`; `ACT-GUARD-FIX-3.md` §7 states the eight parser lines and its planted writes). Take its
  planted writes (into an acceptance folder, outside a reviewer's record place) and every unknown or unparseable form,
  which must still be refused (fail closed).

## The tests (FULL: thorough, but no combinatorial expansion past the KPIs)
1. **The replay:** each refusal judged false must now be allowed; each judged true must still be refused, by the same
   rule. Drive the product's guard as the five-rule hook calls it: the hook is the reviewed
   `drafts/act-guard-fix-3/pretooluse.py` (with `bash_writes.py` beside it), run as a subprocess under `python3` with
   `PYTHONPATH=<tree>/src` (the tree under test), fed the tool call as Claude Code sends it (JSON on stdin: `tool_name`,
   `tool_input`, `cwd`, the role's environment), its answer read from its exit code and output. Work out the hook's
   input and output form from that file; copy the two files into your test's fixtures so the test does not depend on
   scratch. Parametrise by refusal key, so each case's id names its refusal.
2. One case per KPI line (lines 1 to 10, as the ticket states them), success and failure, through public interfaces:
   the read judge and the write parser as `gov.guard` exposes them today (the ticket names them), and the hook.
3. The failure lines: a planted write the base parser catches is still caught; an unknown form still refuses.
Red first: run against the base (`w2/integrate`) through the gate; state in the README each case's expected red
reason (most false refusals are red today, by design). Write the README mapping each KPI line to its cases.

Commit only under `tests/acceptance/W2-42a/`: `Task: DAEO-03ub`, `Implements: DEC-1040,DEC-1028`,
`Role: independent-test-designer`. Return DONE with the head (12 digits), the cases by KPI line, the replay's counts
(recovered, false, true, left out with reasons) and the red run's result. Estimate: 2 hours.
