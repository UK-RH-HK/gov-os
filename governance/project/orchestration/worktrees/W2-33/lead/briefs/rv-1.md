# Brief rv-1: independent reviewer for DAEO-lrre (W2-33), STANDARD, review round 1, read-only

You are a fresh, read-only reviewer (role independent-auditor) of ticket DAEO-lrre (W2-33: the three layers' role
files and the machine-readable defaults per role). You wrote none of this work. **You write nothing**: no file, no
commit, anywhere. Your last message is your report, and your lead writes the probe record from it.

## What to probe
- **Head:** `3b3a90d74` on branch w2/W2-33 in /home/usain/gov-os-worktrees/W2-33 (`git rev-parse HEAD` must agree;
  if it does not, say so and probe what is there). The base is `3df1ac2deb1b` (acceptance tests merged, red).
- **Commits:**
  - `aa8b0fc0f` product-spec, session 3ab69be5: the nine role files and the rulesync orchestrator source;
  - `4c6a47d8c` product-spec, session 1ddf88ff: "alone" → "only" in the install rule (S9);
  - `e7d1c833f` independent test designer, session 47dc5eaf: W1-35's three old-layout cases revised, merged at
    `27ffbe201`;
  - `d344b6418` w2/integrate merged in;
  - `3b3a90d74` the lead's CIT-P, `docs/changes/W2-33-CIT-P.md`.
  The tests, written earlier: `tests/acceptance/W2-33/` (`fea11dee4`, `d15357591`).
- **The ticket (current):** /home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/context/DAEO-lrre.ticket.md. Read it
  whole: the KPI lines S1-S9, F1, F2, and `## Interface`. The Interface routes some clauses to other tickets (S2's
  launcher plan → W2-60a; S3's guard refusal and S5's launcher refusal → W2-60b; S7's generated agents and F2's
  generation drift → W2-153). Judge only what stays here.
- **The approved roles spec:** governance/project/orchestration/packages/ROLES-SPEC-1.md §3.0-3.9, §5, §10
  (DEC-957). Decisions by id in docs/DECISION_REGISTER.md: DEC-954, DEC-957, DEC-959, DEC-963, DEC-1010, DEC-1087
  (13), DEC-1119, DEC-1120, DEC-1156 (3), (4), (7), DEC-971 item 4, DEC-236, DEC-820.
- **Threat model (DEC-801, DEC-808):** honest mistakes in ordinary work. A finding fails the review only when it is
  in the ticket's scope, reachable in ordinary work, and fails open or loses work. A finding out of scope, or one that
  needs an unusual construction, is a Wave 3 row, never a round (DEC-1010 item 1).

Search with Read, Grep and Glob, and git read commands (`git show`, `git diff`, `git log`). If a search does not
answer, search once more in different words. You may run, read-only, the acceptance folder through the heavy-slot
gate:
`TMPDIR=/tmp/gov-w2-33-rv bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-33/src python3 -m pytest tests/acceptance/W2-33 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(if `/tmp/gov-w2-33-rv` cannot be made, leave TMPDIR to the sandbox's own; never let pytest write in the worktree).
A gate refusal is a wait.

## The questions to answer, each with path:line evidence
1. **Per KPI line (S1-S9, F1, F2):** does the work meet the line as the ticket and the Interface state it, and as
   ROLES-SPEC-1 states the role? Do the tests check the line, and not vacuously? Name any test that would pass on a
   broken file.
2. **Spec fidelity (F2):** does each of the nine role files say what ROLES-SPEC-1 says of that role? Check reads,
   writes, skills, model, brief contents and handover for the CTO, the Senior Engineer and the ticket lead. Is
   anything stated that the spec or a decision does not support (an invented rule or permission)? Does any file
   grant a permission the guard does not give?
3. **Fail-open risk:** could any statement lead a session to do what the guard or a decision forbids? Examples: a
   QA engineer told it may write beyond its findings report; a lead told it may merge; a test designer or engineer
   told it may read the other's work; an install rule that reads as letting a non-CTO session be asked.
4. **The three revised W1-35 cases (the CTO asks for this, case by case):** compare
   `git show 3df1ac2de:tests/acceptance/W1-35/test_w1_35_orchestration.py` with HEAD's file. For each revised case:
   does it keep its point under DEC-1156 (3) and DEC-957 Q2? Does each carry a Rewrite-Reason? Is anything else in
   the file changed? The roster case dropped its half on `template/.rulesync/subagents/`. Say what that half
   guarded, and whether that guard now lives with the copies ACT and W2-153's generation check (see
   `src/gov/adapters/portability.py` and W1-33/W1-38's agreement cases), so that nothing is lost.
5. **S6's planted review brief (the Interface: run by the reviewer as a probe).** Take `qa-engineer.md` as your role
   and triage this planted review brief. The brief: ticket X, profile STANDARD, KPI S1 "the CLI prints the version";
   round 2 just ended; the findings are F-a (in scope: the version string misses its patch number) and F-b (out of
   scope: the help text's colours are wrong on one terminal). Return the structured verdict per KPI the file
   prescribes. Does it list F-b as a Wave 3 row? Does it start no third round? Quote the lines of `qa-engineer.md`
   that decided each step.
6. **The rulesync source:** is `template/.rulesync/subagents/orchestrator.md` exactly
   `gov.adapters.portability.compose(root, 'orchestrator')`, with its `claudecode.skills` equal to the kernel file's
   Skills line? Run the one-line Python check read-only.
7. **The CIT-P:** do its sha256 values equal those of the files at `4c6a47d8c` and `3df1ac2deb1b`? Does it misstate
   anything?

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE) / work_completed /
files_changed (must be none) / evidence / tests (what you ran, with summary lines) / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then:
- each finding, numbered R1..Rn: the behaviour described (never code), path:line, severity, in scope or a Wave 3
  row, and whether it fails open or loses work;
- the per-KPI verdict (S1..S9, F1, F2: pass or fail, with the findings that bear on each);
- the answers to questions 4 and 5 in full;
- this fenced block, exactly:
```verdict
verdict: PASS or FAIL
probed_commit: <the full 40-character hash you probed>
findings: <n>
```
- `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
