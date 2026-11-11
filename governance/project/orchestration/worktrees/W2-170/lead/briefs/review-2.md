# Review 2 of W2-170 (DAEO-61vm), the memory audit's set record: a fresh, read-only FULL probe, the last round (DEC-1010, DEC-1131, DEC-1133)

Budget: projection 6 USD.

You are a fresh, read-only independent reviewer (role `independent-auditor`, class C2, Opus at effort high, RUBRIC-2). You read everything and change nothing. You probe the head of `/home/usain/gov-os-worktrees/W2-170` against the ticket's KPI lines S1-S6 and F1-F5, its `## Interface` sections 1-10, and above all **the fix of review round 1's finding RV1**. This is review 2, **the last** (DEC-1131, DEC-1010 item 1): if something still blocks, it goes to the owner once.

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-61vm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (both in `/home/usain/gov-os-worktrees/W2-170`) must work.
If (a) wrote the file or (b) failed, stop there and return. Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-61vm`).

## The head you probe
`6ba5a6edab5b` on branch `w2/W2-170`. `git -C /home/usain/gov-os-worktrees/W2-170 rev-parse HEAD` must begin with it **at your start and at your end**; if it differs, stop and say so. Since round 1's head `ad664fc87755`: the lead's merge of `w2/integrate` (`fcfe85cb1`, the ticket's Interface section 10 reading 9 and records, nothing under the ticket's code paths), the test designer's second batch (`4591ebf62`, `adc3013dc`, merged at `c0202ce81`) and the engineer's one fix pass `6ba5a6eda` (`common.py`, `declare.py`, `preflight.py`, two unit test files, the evidence file).

## Round 1, in short (the full record: `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/lead/log/review-1.result.md`)
- **RV1 (blocked; scope in, S1; ordinary work yes; fails open):** a set pre-flighted clean, then its `hidden/` files replaced as the writer's round 2 does, notes accepting all, `void` exit 0, `declare` exit 0 and `USED` for a set never pre-flighted.
- **The CTO's decision (a delegated stricter-only decision, written into the ticket as section 10 reading 9):** `PREFLIGHT.json` records each delivered file's sha256 by id; `DC-PREFLIGHT` also refuses when a kept file is not byte-equal to a pre-flighted one; such a set is never marked `USED` until it is pre-flighted again.
- **Rows, not rounds (already classified "no" or "other"; do not re-raise them as new unless the fix changed them):** RV2 (`./`-prefixed source under an evaluation namespace passes), RV3 (empty heading with lines outside the file passes), RV4 (after a crash halfway through `void`, `DROPS.json` under-counts the drops), RV5 (PF-IDEXISTS refuses a nonexistent-id question that also names a real id; fails closed).
- **The test designer's open point, a package to the CTO, not a finding for you to settle (PKG-W2-170-TD2-1):** after `void`, a replaced set that a pre-flight refuses has no stated way back (fixing its files makes `DC-DROPS` refuse and `void` refuses a second run with `DR-DONE`); it fails closed. You may say whether you see it otherwise.

## What you judge
- The ticket file `/home/usain/gov-os-worktrees/W2-170/.tickets/DAEO-61vm.md`: KPI lines S1-S6, F1-F5 and `## Interface` sections 1-10 (section 10 readings 1-9). The whole design: `governance/project/orchestration/packages/MEMORY-AUDIT-1.md` (section 3.3's order: writer round 1, pre-flight, checker round 1, writer round 2, checker round 2, drop) and the briefs under `governance/project/indep-briefs/memory-audit/`.
- The code: `src/gov/memaudit/**` (about 1,380 lines), the unit tests `tests/unit/memaudit/**` (84 cases), `governance/project/test-map.yaml`'s coupling, `docs/changes/W2-170-evidence.md`. The acceptance tests `tests/acceptance/W2-170/**` (179 cases, the independent test designer's two batches) only as far as you need to say what they miss.
- Read `git -C /home/usain/gov-os-worktrees/W2-170 diff ad664fc87755 6ba5a6edab5b -- src/gov/memaudit tests/unit/memaudit` first.
- The engineer's readings P1-P5 of round 1 stand as built (round 1's brief lists them; the record above judged them sound).
- **Out of this review:** the measure (W2-171), the cycle and the schedule (W2-172), the launch script's follow-ups (W2-173), and the files the merges of `w2/integrate` brought in. A finding there is `scope: out`, a row.

## What the lead ran (do not re-run these)
- On head `6ba5a6edab5b`: the engineer's unit folder 84 passed and acceptance 179 passed; the lead's `lead_verify` (the scoped run plus the wider net) and `gov accept W2-170` beside you; the lead reports them.

## What to show (the open points)
1. **RV1's fix, in the cycle's real order:** pre-flight clean, then a round-2 replacement of `hidden/` (each defect the ten checks catch; a byte change that still passes every check; a new id; a removed id; a file replaced then dropped), checker round-2 notes, `void`, `declare`: is any set whose kept files were not byte-for-byte the pre-flighted ones declared or marked `USED`? Does a re-pre-flight let an honest cycle go on? Does `DC-PREFLIGHT` write nothing (no map entry, no `DECLARATION.json`, no ledger line, no `USED`)?
2. **What the fix could have broken:** the S3 flow (pre-flight, `void` with drops, `declare`: order of the five writes, file times, ledger), `void`'s behaviour, the exit codes, S5/F1 for the new record in `PREFLIGHT.json` (ids and digests only), a `PREFLIGHT.json` from before the fix (no record): refused, not passed.
3. **Ordinary-work false refusals the fix adds** (a clean, honest cycle refused): say so; a false refusal fails closed, consequence `other`.
4. **F5:** `git -C /home/usain/gov-os-worktrees/W2-170 diff --name-only w2/integrate...6ba5a6edab5b` lists only the allowed paths and the designer's acceptance tests.
5. Anything else in S1-S6, F1-F5 that round 1 did not probe and you find reachable in ordinary work.

## How you work
- Read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains (use `git -C` or full paths); no here-documents, backticks or `$(…)`; anything longer goes in a script file under your sandbox's TMPDIR, run by its path. **`gov retrieve` is not available in your sandbox** (no private embedder, DEC-1064/1065): read the code with Read and Grep; if a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all. Read the register only by id (`docs/DECISION_REGISTER.md`).
- **Re-run nothing the lead ran.** Run code only to reproduce or probe a finding, in planted roots built from nothing under your sandbox's TMPDIR (you may import `tests/acceptance/W2-170/w2_170_world.py` or `tests/unit/memaudit/conftest.py` read-only to build a planted repository, sets root, runs folder, pool and store), every Python process with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src` per command (DEC-732), `HOME` an empty folder under your TMPDIR, no network, no real embedder or model, no GPU, never the full suite, no installs. Show the code under test once: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src python3 -c "import gov; print(gov.__file__)"`.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-170 status --porcelain` must be empty when you finish. Clean your TMPDIR as you go; name what you cannot remove. Budget: 2 GB and 100,000 files and folders (DEC-898); report `du -sh` and `du -s --inodes` of your TMPDIR in `evidence`.
- **Read refusals (DEC-849):** the guard may refuse some reads. Take the refusal, never look for another form; search named folders instead. Count the refusals you met in your return. A Write-tool refusal is also not worked around: report it.
- **Protected material (DEC-820, DEC-1097):** never read secrets or keys, never print one; never open the real sets root `~/gov-os-eval` or the real run folders `~/gov-os-runs` (every probe plants its own roots under your TMPDIR and passes every root flag explicitly); never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- **Row W2-L423's rule (DEC-911):** in your return write commit hashes as 12 digits, never the full 40, except the one `probed_commit` line, and never write the keywords of the secrets rule that takes a bare 40-hex string; call it "row W2-L423's rule".
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal.
- Estimate: about 30 minutes.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

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
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## Your record (your session's final message, in full; you write no file)
The twelve fields first, each a labelled line ("none" where nothing):
```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
Put step 0's result first in `evidence`, then the head at start and end, the `gov.__file__` line, your session id if you know it, your TMPDIR's measures, the read refusals counted.

Then the probe record body:
- `task: DAEO-61vm` and `decisions:` (the ids your findings rest on); `probed_commit: <the full id of 6ba5a6edab5b>`.
- **Scope** and **Method** (what you planted and ran, how many times).
- **Probed and found sound**, per open point 1-5 above.
- **Findings**, each described as behaviour (what was done, what happened, what should have happened), never as code (DEC-136), each with `scope: in|out`, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and what evidence would reverse it (DEC-1014). Name both ids where a superseded or PROPOSED rule is in use (DEC-1073).
- The classification on one line (counts of yes/fails open or loses work; yes/other; rows).
- At the end, the fenced block, one entry per KPI line, ids exactly `S1`, `S2`, `S3`, `S4`, `S5`, `S6`, `F1`, `F2`, `F3`, `F4`, `F5`, each finding listed under the line it concerns (a finding on no line goes under the nearest one, `scope: out`):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Refused twice for the same call: stop and say so.
