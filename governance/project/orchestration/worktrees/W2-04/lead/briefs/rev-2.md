# Review 2 of 2 (the last) of W2-04 (DAEO-u4oz), `gov context` bounded and reproducible: a fresh, read-only FULL probe (DEC-1025 (1), DEC-1010, DEC-1131)

You are a fresh, read-only independent reviewer (role `independent-auditor`, class C2, Opus at effort high; review 1 ran at max, so this one differs, as DEC-1025 (1) asks). You read everything and change nothing. You probe the head of `/home/usain/gov-os-worktrees/W2-04` for behaviour the acceptance tests miss, against the ticket's KPI lines. This is the **second and last** review: a fail goes to the owner once with options, never a third round (DEC-1010, DEC-1131).

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (both in `/home/usain/gov-os-worktrees/W2-04`) must work.
If (a) wrote the file or (b) failed, stop there and return. Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-u4oz`).

## The head you probe
`4c55f14179be` on branch `w2/W2-04`. `git -C /home/usain/gov-os-worktrees/W2-04 rev-parse HEAD` must begin with it **at your start and at your end**; if it differs, stop and say so. (`w2/integrate` is one commit ahead, `35f4eb9943a5`, a CTO record commit touching only `governance/project/orchestration/packages/DECIDED-NOT-DONE.md`; it changes nothing you judge.)

## What you judge
- Paths: `src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`, `tests/acceptance/W2-04/**`, and the ticket file `/home/usain/gov-os-worktrees/W2-04/.tickets/DAEO-u4oz.md` (its KPI lines S1-S7 and F1).
- **Second caller (a review-1 gap):** the session-start hook `template/governance/kernel/hooks/sessionstart.py` (line ~153) calls `gov.context.context(..., brief=True)` at every start, resume and compaction. Judge what the hook's caller sees of S2 and S5 (refusal, emptied input); the hook itself is outside this ticket's paths, so a finding about the hook's own handling is `scope: out` unless the context's result itself is wrong.
- The KPI lines (the ticket file holds the whole text):
  - S1: holds the packet ceiling (≈ 6k tokens) and never drops the ticket's own text.
  - S2: mandatory inputs alone over the ceiling refuse with a named error and a non-zero exit; never `ok: true` over the budget.
  - S3: each decision named by its own hash (W2-03).
  - S4: two builds on stores rebuilt from one commit give the same packet hash with or without a live semantic index; ties ordered deterministically.
  - S5: an unreadable mandatory record blocks or is marked not read; never shown as read with an empty hash.
  - S6: the supplementary query built from the KPIs and title, not the first long word.
  - S7: never one giant query or context: supplementary evidence in batches, ranked and stacked within the ceiling; the packet names what it left for a further batch.
  - F1: DAEO-03pw's context (814,821 tokens at the audit) refuses or fits; a RETIRED or REJECTED record does not satisfy a mandatory source.
- **Out of this review (non-goals; the ticket states none, so the lead names them):** review 1's F4 (31 open tickets refuse their context at 6,000 tokens; the close builds the context after its runs; the hook drops the error: DEC-1025 (4), a matter for a new ticket the owner files, DEC-974), F5 and F6 (Wave 3 rows), and anything under `src/gov/context/**` that the KPI lines do not name. A finding there is `scope: out`, a row.

## History (what review 1 found and what was repaired)
- **Review 1** (probed `b37b5c8f1741`, Opus at max, 11-02) FAILED on F1:
  - **F1** (in scope, ordinary work yes, fails open): a mandatory capability file or a dependency ticket emptied in the working tree (what a truncating write leaves) was shown as read, with the sha256 of empty content and 0 tokens (S5); `--brief` listed it as present; the check was green. Register entries already blocked (their span is read from the store).
  - **F2** (row, ridden along): when the room ended exactly on a batch boundary, or was 0, `further_batch` was empty although ranked items remained; S7 and the specification's S7a say it starts at the first ranked item not stacked.
  - **F3** (row, ridden along): the context-reproducibility check read green when every ticket refused ("0 built, 2 refused"); it should say unmeasured.
  - F4, F5, F6: out of this review (above).
- **The repair round (DEC-1025):** the test designer's `42e73adb7` (round 3 of `tests/acceptance/W2-04/`, `Rewrite-Reason: DEC-1025`: an emptied mandatory file, `further_batch` on an exact fit or no room, the check when every ticket refuses); the engineer's `de81824be` ("an emptied mandatory file blocks, the room ending exactly names what is left, an all-refused check is unmeasured"); the merge `a0c79a6c9`; then `fcfb9150b` and `98993db4e` (integrate merged in: W2-54's packet-hash case keeps W2-04's reads and W2-126's two caches); then `70965cf61`, the merge into `w2/integrate`, "accepted as built" (DEC-1052 M-1). **No review of the repair has happened, and the repair round's lead left no record.**
- **Changes to judged files after `70965cf61`, by other tickets (judge them too; read `git log 70965cf61..4c55f14179be -- <the paths>`):**
  - W2-13 S5: `5b42e9810`, `f54decffc`, `23bef297a`, `6e6922439` (the supplementary block filtered by the caller's role paths; `--role` passed to `context()`; the packet's own ticket judged as well as `GOV_TICKET`) in `src/gov/context/__init__.py`, `command.py`, `src/gov/retrieval/supplementary.py`;
  - W2-150: `28c586930`, `b85efb879` (imports moved into `gov.util` / `gov.store`) in `supplementary.py`;
  - D-4's cut: `ccc108c8c`, `3b6c27f32`, `f551589dd`, `cb96180d1` (W2-04's suite 90 → 74 cases in the full run, 16 in the `breadth` opt-in; README's KPI map regenerated);
  - D-10 run 2: `3e403a285` (the damaged-index case also takes "the lexical index is unreadable" as naming the kind).
  Say whether any of these weakened S3, S4 (packet hash, with W2-126's two caches), S5 or S7.

## What the lead ran (do not re-run these)
- Store rebuilt in this tree at `4c55f14179be` (exit 0, 43.6 s).
- `gov accept W2-04 --root /home/usain/gov-os-worktrees/W2-04` (the pinned judge), exit 0, outcome pass, opt-in `breadth`:
  success-1 8 passed; success-2 8; success-3 5; success-4 7 passed, 1 skipped; success-5 35; success-6 2; success-7 13; unmapped 11; totals 89 passed, 0 failed, 1 skipped. (The runner reports no separate `failure-1` line; the F1 case `test_w2_04_refusal.py::test_daeo_03pw_shape_fits_or_refuses` is mapped in the README under S2's section and in the KPI map under F1. Say whether that hides anything.)
- The scoped verification (`select_tests.py`: scope `scoped`, own acceptance folder plus the unit folders) runs beside you; the lead reports it.

## What to show (the open points)
1. **F1 repaired in ordinary use:** a cited capability file and a dependency ticket named in `deps`, each emptied and each reduced to whitespace in the working tree after a store built from `HEAD`, in the plain mode (`--json`), `--dry-run`, `--brief` and `--brief --dry-run`, and through `gov.context.context` as the hook calls it: BLOCKED naming the id and file, or `"read": false`, never shown as read. Look also for the neighbours of F1 an honest agent can hit: a file edited legitimately in the working tree (must not block wrongly), a decision file of its own, a file with only a BOM or only a comment line, a dependency ticket truncated to its front matter.
2. **F2 repaired:** the exact-fit and zero-room batch cases; `further_batch` begins at the first ranked item not stacked, at most one batch long, its items in `dropped` as `budget exceeded`.
3. **F3 repaired:** the all-refused check prints `unmeasured:` and exits non-zero; one refused and one fitting stays green with its `REFUSED:` line.
4. **The later merges kept S3 and S4:** the packet hash is the same across two stores rebuilt from one commit, with or without the semantic route, with W2-126's two caches and W2-13's role filter in place (does the role filter or `--role` change the packet hash between callers in a way S4 forbids for one ticket and one role?).
5. S1, S2, S6, F1 (the RETIRED/REJECTED half included) as built.

## How you work
- Read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains (use `git -C` or full paths); no here-documents, backticks or `$(…)`; anything longer goes in a script file under your sandbox's TMPDIR, run by its path. **`gov retrieve` is not available in your sandbox** (no private embedder, DEC-1064/1065): read the code with Read and Grep; if a search does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both with path and lines, or say "not found". Two searches in all.
- **Re-run nothing the lead ran.** Run code only to reproduce or probe a finding, in a temporary project built from nothing under your sandbox's TMPDIR (you may import `tests/acceptance/W2-04/w2_04_support.py` read-only to build fixture projects), every Python process with `PYTHONDONTWRITEBYTECODE=1` (a `PYTHONPATH=src` import otherwise writes `__pycache__` beside `src/`), `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src` per command (DEC-732: every test run and every `gov` command used for verification runs this worktree's own `src/`, set per command, never in settings), `HOME` an empty folder under your TMPDIR, no network, no real embedder or model, no GPU, never the full suite, no installs. Show the code under test once: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -c "import gov; print(gov.__file__)"`.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-04 status --porcelain` must be empty when you finish. Clean your TMPDIR as you go; name what you cannot remove. Budget: 2 GB and 100,000 files and folders (your share of the lead's 20 GB / 1,000,000, DEC-898); report `du -sh` and `du -s --inodes` of your TMPDIR in `evidence`.
- **Read refusals (DEC-849):** the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`). Take the refusal, never look for another form; search named folders instead. Count the refusals you met in your return.
- **Protected material (DEC-820):** never read secrets or keys, never print one; never read the contents of the held-out qualification material or the hidden half of any evaluation set (`~/gov-os-eval`); never read or name the qualification oracle; never write in `~/gov-os-workbench`.
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
- `task: DAEO-u4oz` and `decisions:` (the ids your findings rest on); `probed_commit: <the full id of 4c55f14179be>`.
- **Scope** and **Method** (what you planted and ran, how many times).
- **Probed and found sound**, per open point 1-5 above.
- **Findings**, each described as behaviour (what was done, what happened, what should have happened), never as code (DEC-136), each with `scope: in|out`, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and what evidence would reverse it (DEC-1014). Name both ids where a superseded or PROPOSED rule is in use (DEC-1073).
- The classification on one line (counts of yes/fails open or loses work; yes/other; rows).
- At the end, the fenced block, one entry per KPI line, ids exactly `S1`, `S2`, `S3`, `S4`, `S5`, `S6`, `S7`, `F1`, each finding listed under the line it concerns (a finding on no line goes under the nearest one, `scope: out`):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Refused twice for the same call: stop and say so.
