# Review 1 of W2-170 (DAEO-61vm), the memory audit's set record: a fresh, read-only FULL probe (DEC-1010, DEC-1131, DEC-1133)

You are a fresh, read-only independent reviewer (role `independent-auditor`, class C2, Opus at effort high, RUBRIC-2). You read everything and change nothing. You probe the head of `/home/usain/gov-os-worktrees/W2-170` for behaviour the acceptance tests miss, against the ticket's KPI lines S1-S6 and F1-F5 and its `## Interface` sections 1-10. This is review 1 of at most two (DEC-1131); a blocking finding gets one engineer fix pass in this same round (DEC-1133 (4)).

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-61vm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (both in `/home/usain/gov-os-worktrees/W2-170`) must work.
If (a) wrote the file or (b) failed, stop there and return. Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-61vm`).

## The head you probe
`ad664fc87755` on branch `w2/W2-170`. `git -C /home/usain/gov-os-worktrees/W2-170 rev-parse HEAD` must begin with it **at your start and at your end**; if it differs, stop and say so. It is the lead's merge of `w2/integrate` (records, ACT-W1-01-EXEMPT-3's exemption line, two orchestration tools) onto the build's head `5795081004a8`; nothing under the ticket's paths changed in that merge.

## What you judge
- The ticket file `/home/usain/gov-os-worktrees/W2-170/.tickets/DAEO-61vm.md`: its KPI lines S1-S6, F1-F5 (the whole text) and its `## Interface` sections 1-10 (section 10 holds the CTO's readings 1-8, delegated decisions). The whole design: `governance/project/orchestration/packages/MEMORY-AUDIT-1.md` and its briefs under `governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/` (the writer brief's form, the rubric's R5 item 6 quotas, R8, R9).
- The code: `src/gov/memaudit/**` (about 1,350 lines: `__main__.py`, `layout.py`, `say.py`, `ledger.py`, `preflight.py`, `drops.py`, `declare.py`, `tables.py`, `common.py`), the unit tests `tests/unit/memaudit/**` (65 cases), the coupling added to `governance/project/test-map.yaml`, and `docs/changes/W2-170-evidence.md`. The acceptance tests `tests/acceptance/W2-170/**` (165 cases, the independent test designer's) only as far as you need to say what they miss.
- The ticket's commits: `a3fb52d6e`, `564c397b2`, `579508100` (engineer); the tests `2f07cf66c` merged at `79a8fb87f`. Read `git log c07a3a941..ad664fc87755 -- src/gov/memaudit tests/unit/memaudit governance/project/test-map.yaml`.
- The KPI lines in short (the ticket file holds the whole text):
  - S1: pre-flight before any search, ten refusals each with its own code (count < 36; form; commit; quotas; domain < 4 / subsystem > 10 scaled; drawn not in `selection.json`; source missing / heading lost and lines outside; evaluation namespace (R8); gold-source set equal to a pool question's (R9); a nonexistent-id question whose id exists); clean set ends `PRE-FLIGHT: every check as expected`.
  - S2: every non-`accept` verdict after the second pass moved to `dropped/` (never deleted); counts and scales recomputed from the kept; kept < 36 or a domain < 4 is VOID: nothing measured, no `USED`, counts say `void` with the cause code.
  - S3: `DECLARATION.json` then `USED`, before any search; the declaration's fields (audit commit, store commit and sha256, gov pin, `retrieval.yaml` digest, the four standard settings by name, the set digest over the kept, n, the bar scaled to n and how it rounds); refusal while `USED` exists; pool off is named and not ok without a decision id.
  - S4: one `evaluation_sets` entry in the sets root's own path map, of `memory-verdict-2`'s shape, accepted by `gov.retrieval.measure`; the repository's path map, the guard and the hook never written; no ACT for a new name.
  - S5: only ids, counts, codes and digests leave (stdout, `PREFLIGHT.json`); a line naming the sets root's folders refused before it is printed; the command line names only `--sets-root <root>`.
  - S6: test-map places `src/gov/memaudit/**` and its tests; `python3 -m gov.memaudit preflight|void|declare`, each `--help` exit 0.
  - F1: no question, gold answer, answer, source path or heading in any output, log or error text. F2: no set measured twice or without both files first. F3: no write to the repository's path map, guard, hook, `.claude/`, the walls' template; no test opens the real sets root or run folders. F4: no dropped question deleted; no VOID audit that wrote `USED`. F5: no change outside the allowed paths.
- **The engineer's readings P1-P5, kept as built by the CTO (a delegated decision); judge them against the KPI lines and the Interface like any other code:** P1 `say` exits 4 on a refused line and returns `("ok", {"printed": 1})` when it prints; P2 a dropped line whose codes field is `-` adds nothing to `by_code` (it still counts in `dropped`); P3 the printed forms as built (`ERROR: UsageError`, `PF-COUNT refused <k>`, `PF-QUOTA refused <k> <category> <count>…`, `PF-SPREAD refused <k> domain|subsystem <name> <count>…`) are the reference until the Interface states them; P4 `DC-DECISION` writes `DECLARATION.json` with `ok: false` and no ledger line; P5 `--repo`, `--store`, `--gov` inside the sets root exit 4.
- **Out of this review (the ticket names no non-goals, so the lead names them):** the measure itself (W2-171), the cycle and the schedule (W2-172), the launch script's follow-ups (W2-173), and the files the merge of `w2/integrate` brought in. A finding there is `scope: out`, a row.

## What the lead ran (do not re-run these)
- Build run (head `5795081004a8`): `gov accept W2-170` (the pinned judge), outcome pass: 165 passed, 0 failed, 0 skipped, every line S1-S6 and F1-F5 its own pass; the unit folder 65 passed. `lead_verify` (the scoped run plus the wider net): reds only outside this ticket (W1-01's history case, repaired on integrate by `7b5c3cb94fd9`, now merged in; six W2-96 signal cases that fail only in an empty-HOME, signal-ignoring shell and pass with HOME set).
- On your head `ad664fc87755` the lead re-runs `gov accept W2-170` beside you and reports it.

## What to show (the open points)
1. **Fail-open in S1:** a set with each defect of the ten that an honest writer can plausibly make (a typo'd category, a source path renamed at the commit, a heading reworded, a source under an evaluation namespace by a near spelling, a pool question's gold sources in a different order, a nonexistent id that exists as a substring or in another case) — does pre-flight pass any of them? And the reverse in ordinary use: does a clean set from the writer brief's form get refused (say so, but a false refusal fails closed: consequence `other`)?
2. **S2 and F4:** a non-`accept` verdict kept (`Accept`, `accept ` with spaces, a verdict line for an id not in the set, a question with no line in the notes, notes of round 1 only, two rounds); a dropped file deleted or overwritten when a file of that name is already in `dropped/`; a re-run of `void` after a crash halfway; kept count and the scales recomputed from the kept only; a VOID audit that can still be declared.
3. **S3 and F2:** the order `DECLARATION.json` → `USED` → anything a search could start from; `USED` present and any subcommand still writing; a crash between the two files (what does a re-run do: measure without a declaration, or refuse forever?); the bar for n = 36..40 (ceil / floor as the KPI line says); the set digest over the kept questions only, reproducible with `LC_ALL=C sha256sum *.yaml | sha256sum`; pool off, reranker off, a different bundle size: named, `ok: false` without `--decision`.
4. **S4 and F3:** the entry's shape against `memory-verdict-2`'s and against `gov.retrieval.measure`'s own check of a set; a second audit's entry beside the first; the repository's `governance/project/path-map.yaml`, the guard, the hook and `.claude/` untouched; whether any code path can reach the real `~/gov-os-eval` or `~/gov-os-runs` when a flag is left out (a default that points at a real root).
5. **S5 and F1:** every path a question, gold answer, source path or heading could leave by: an exception's text, a YAML parse error quoting the file, a git error quoting the path, `PREFLIGHT.json`, `DROPS.json`, `DECLARATION.json`, the ledger, the map entry; a line holding the root's folders refused before printing (P1).
6. **S6:** the test-map coupling by `gov.close.select`'s own matching; each `--help`.
7. **P1-P5** as above, and **F5**: `git diff --name-only w2/integrate ad664fc87755` lists only the allowed paths.

## How you work
- Read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains (use `git -C` or full paths); no here-documents, backticks or `$(…)`; anything longer goes in a script file under your sandbox's TMPDIR, run by its path. **`gov retrieve` is not available in your sandbox** (no private embedder, DEC-1064/1065): read the code with Read and Grep; if a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all. Read the register only by id (`docs/DECISION_REGISTER.md`).
- **Re-run nothing the lead ran.** Run code only to reproduce or probe a finding, in planted roots built from nothing under your sandbox's TMPDIR (you may import `tests/acceptance/W2-170/w2_170_world.py` or `tests/unit/memaudit/conftest.py` read-only to build a planted repository, sets root, runs folder, pool and store), every Python process with `PYTHONDONTWRITEBYTECODE=1` (a `PYTHONPATH=src` import otherwise writes `__pycache__` beside `src/`), `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src` per command (DEC-732: every test run and every `gov` command used for verification runs this worktree's own `src/`, set per command, never in settings), `HOME` an empty folder under your TMPDIR, no network, no real embedder or model, no GPU, never the full suite, no installs. Show the code under test once: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src python3 -c "import gov; print(gov.__file__)"`.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-170 status --porcelain` must be empty when you finish. Clean your TMPDIR as you go; name what you cannot remove. Budget: 2 GB and 100,000 files and folders (your share of the lead's 20 GB / 1,000,000, DEC-898); report `du -sh` and `du -s --inodes` of your TMPDIR in `evidence`.
- **Read refusals (DEC-849):** the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`). Take the refusal, never look for another form; search named folders instead. Count the refusals you met in your return.
- **Protected material (DEC-820, DEC-1097):** never read secrets or keys, never print one; never open the real sets root `~/gov-os-eval` or the real run folders `~/gov-os-runs` (every probe plants its own roots under your TMPDIR and passes every root flag explicitly); never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- **Row W2-L423's rule (DEC-911):** in your return write commit hashes as 12 digits, never the full 40, except the one `probed_commit` line, and never write the keywords of the secrets rule that takes a bare 40-hex string; call it "row W2-L423's rule".
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal.
- Estimate: about 40 minutes.

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
- `task: DAEO-61vm` and `decisions:` (the ids your findings rest on); `probed_commit: <the full id of ad664fc87755>`.
- **Scope** and **Method** (what you planted and ran, how many times).
- **Probed and found sound**, per open point 1-7 above.
- **Findings**, each described as behaviour (what was done, what happened, what should have happened), never as code (DEC-136), each with `scope: in|out`, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and what evidence would reverse it (DEC-1014). Name both ids where a superseded or PROPOSED rule is in use (DEC-1073).
- The classification on one line (counts of yes/fails open or loses work; yes/other; rows).
- At the end, the fenced block, one entry per KPI line, ids exactly `S1`, `S2`, `S3`, `S4`, `S5`, `S6`, `F1`, `F2`, `F3`, `F4`, `F5`, each finding listed under the line it concerns (a finding on no line goes under the nearest one, `scope: out`):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Refused twice for the same call: stop and say so.
