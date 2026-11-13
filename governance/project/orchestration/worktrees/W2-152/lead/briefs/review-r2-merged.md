# W2-152 (DAEO-o5x1) — the independent review on the merged head, round 2's re-probe, the last (DEC-1010)

You are a fresh, read-only independent reviewer (role `independent-auditor`), launched by the ticket lead through
`gov launch` in the OS sandbox. You read everything; you write nothing in any tree.

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-o5x1','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return. Also `printenv GOV_ROLE GOV_TICKET` (expect
`independent-auditor`, `DAEO-o5x1`) and `git -C /home/usain/gov-os-worktrees/W2-152 rev-parse HEAD` must start with
`e25bdca86bc1`; if not, stop and say so.

## Why this review
- W2-152 is `gov brief`: a filled brief from the ticket and `governance/project/facts.yaml`, refused when the ticket is
  not READY by code (DEC-1050, DEC-1052, DEC-1083, DEC-1088 (3), DEC-1112). Ticket: `.tickets/DAEO-o5x1.md` (read it in
  full: KPI lines S1 to S10 and F1 to F3, `allowed_paths`, its "Interface" and "Clarified after the test design").
  Design: `governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §B and §D TPL-3, TPL-5. The templates it
  fills: `template/governance/kernel/templates/`.
- Round 1 (`16d052d2fda7`): NOT READY on F1, record `governance/project/orchestration/reviews/w2-152-r1.md`.
- Round 2 (2026-11-09, on `09fc68645c0c`): READY. Its full record is the last JSON object's `result` in
  `/home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/W2-152-review-r2.json` (session `57de2180`).
  Read it: its findings F2, F7 to F15 and their classes.
- Since then the branch was merged into `w2/integrate` and `w2/integrate` merged back twice (`6dc3db850050`,
  `e25bdca86bc1`, both without a conflict). Two things reach this ticket:
  1. the designer's commit `32b89d25a578` (one comment line in `tests/acceptance/W2-152/test_w2_152_rev2.py`) lies
     after round 2's probed commit, so the close's probe gate needs a record of the head that holds it;
  2. three days of landings changed what `gov brief` reads: the kernel role templates (W2-128 rounds 2a and 2b,
     W2-153's template delivered at launch, W2-177, ACT-CLAUDE-COPIES-1), possibly `facts.yaml` and the ticket files.

## What to check (on the head `e25bdca86bc1`, against `09fc68645c0c` and `w2/integrate`)
- `git diff 09fc68645c0c e25bdca86bc1 -- src/gov/brief tests/unit/brief tests/acceptance/W2-152 governance/project/facts.yaml template/governance/kernel/schemas/facts.schema.json docs/changes/W2-152-evidence.md`:
  is the only change in the ticket's own paths the one comment line, and does it change no test's behaviour?
- `git diff --stat 09fc68645c0c e25bdca86bc1 -- template/governance/kernel/templates/`: does `gov brief` still hold
  every KPI line on today's templates? In particular S1 (byte-identical, golden files), S2 (no slot left:
  `role-lead.md` now carries STEP and CMD slots in braces: are they filled or refused by name, never left in a
  printed brief), S4 (no role-template line in a worker brief), S5 (the "until <ticket>" check over every role's whole
  template, the lead's common part included), S6 (one run block per lead run kind), and F2/F3.
- Did anything that landed break round 2's closed findings (F1, F3, F4, F5, F6)? A brief spot check is enough where
  nothing in the read paths changed.
- Every KPI line S1 to S10 and F1 to F3 again, briefly: a pass stays a pass only if the code still holds it.

## The lead's results (read them; re-run nothing the lead ran)
- `gov accept W2-152` on `e25bdca86bc1`: 67/67, every line pass (`.gov-runtime/scratch/lead/log/accept.log`).
- The scoped run (`select_tests.py`: scope scoped, `core_changed` [], `unplaced` []): `.gov-runtime/scratch/lead/log/parallel.log`
  and `serial.log` with their `.exit` files (it may still be running when you start; read what is there).
- You may run `gov brief` itself and small probes on throwaway fixture repositories in your sandbox's own TMPDIR, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-152/src` per command. Code under test (DEC-732), word for word: in this
  worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-152/src` set per command (never in a session's `--settings` env); show it
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-152/src python3 -c "import gov; print(gov.__file__)"`.
  Any pytest you run, only of `tests/acceptance/W2-152` or `tests/unit/brief`, read-only, with `-p no:cacheprovider
  -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`,
  `HOME` set to an empty folder in your TMPDIR, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONDONTWRITEBYTECODE=1`.
  Your scratch budget: 2 GB and 100,000 files, in your TMPDIR only; remove it before you return and give its measure.

## Memory and search
- `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-152/src python3 -m gov.cli.main retrieve "<question>" --json`)
  is the way to ask what you need to know before reading files at random, but inside the sandbox it would start a
  private CPU embedder (DEC-1064, DEC-1065 (1)): do not run it here; read with grep and the Read tool, in named folders.
  Never one giant query or context (DEC-860); a code question uses small, targeted reads (DEC-859).
- Search again once (DEC-1092 (1)): when a search does not answer, or its answer may be incomplete, search once more in
  your own, different words, then answer from both with path and lines, or say "not found"; two searches in all.
- Until W2-58 lands the guard refuses some reads Policy 2 opened (searches from the repository root, `governance/project/`
  or `.claude/`): take the refusal, never another form; search named folders instead; count the refusals in your return.
- Before you return: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing of yours: report it.

## What you never do
- Write nothing in any tree, run nothing that writes there (`git -C /home/usain/gov-os-worktrees/W2-152 status --short`
  empty when you finish; the only write allowed is step 0's git blob). No merge, commit, checkout or stash.
- Reads (DEC-820): never secrets or keys (never print one); never the contents of the held-out qualification material
  (its file names may be seen); never the hidden half of any evaluation set (`~/gov-os-eval/`, `~/gov-os-runs/`, any
  `hidden`, `memory-verdict` or `memory-verdict-2` folder). You are the reviewer: you read both the tests and the code.
  Never write in `~/gov-os-workbench`; never copy the tree (no `cp -r`, `rsync`, `git archive`, `git worktree`,
  `git clone` of this repository); fixtures are built from scratch or from single named files.
- Under `.gov-runtime/`, and in your return, write commit hashes as 12 digits, never the full 40, and never write the
  keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule" (DEC-911).
- Single simple Bash commands; no here-documents, no backticks, no `bash -c '…'`, no long inline `python3 -c` with
  braces; anything longer goes into a script file in your TMPDIR (the guard's command forms, DEC-941 item 4a).
- Refused twice for the same call: stop and say so; no third try. That covers the same effect in another form: a
  session refused twice for an action does not reach it by another command, form, file or tool (DEC-1142 (9)).

## Judgement (`governance/project/briefs/JUDGEMENT.md`, word for word)

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

Also: state, per finding, the evidence that would reverse it (DEC-1014); describe each finding as behaviour (what was
done, what happened, what should have), never as code (DEC-136); say what you probed and found sound. Keep round 2's
finding ids (F2, F7 to F15) where a finding carries over; number new ones from F16.

## Write and return
Your record is your session's final message, in full: it becomes the probe record the lead commits. Give it
`task: DAEO-o5x1` and `decisions:` (the ids your findings rest on). Then your verdict per line with every finding's
lines, `scope: in|out`, its two judgement lines and its reversing evidence; and at the end the fenced block, one entry
per line (S1 to S10, F1 to F3):

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word;
"none" where there is nothing), the sandbox check and the `ps` check before them, any payload after them. Refused twice
for the same call: stop and say so.

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
