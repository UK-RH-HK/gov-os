You are a fresh product-spec worker, in ticket mode. Ticket: DAEO-ha8z (W2-49, "Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-49` on branch `w2/W2-49`.

The ticket's change-impact proposal (CIT-P), `docs/changes/W2-49-CIT-P.md`, was written and committed at `9dd15777`. A fresh, read-only independent auditor reviewed it, as CAP-33 requires before the owner's approval, and recommended ACCEPT_WITH_FINDINGS. Your task is the one answer round: revise the CIT-P so that it answers each finding below, and record how each was answered.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-ha8z`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-49` and `w2/W2-49`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Read nothing that `docs/SOURCES.md` excludes from agents (the originals under `docs/source/`).
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. **Do not run `docs/plan/tools/validate_s1.py`:** by default it reads the workbench and `docs/source/`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`.
- **The git hooks are uninstalled until W2-08.** Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).

## Owner decision in force that is not yet in this worktree's register

- **DEC-737 (owner, 2026-10-16; staged for the owner's commit):** the rule "W2-01 goes first, alone" (DEC-721) binds the **closes**, not the work. W2-49's paths do not overlap W2-01's, so W2-49 runs beside W2-01, and closes after W2-01's close; its `tk` dependency on W2-01 reads "closes after W2-01", not "starts after". After the owner approves the CIT-P, a fresh lead applies it; the ticket is then held for the close order. Cite it as DEC-737 (staged), never as a register entry.

## What you read

- The CIT-P as it stands: `docs/changes/W2-49-CIT-P.md`.
- The ticket file `.tickets/DAEO-ha8z.md` (read-only); the acceptance tests and README, `tests/acceptance/W2-49/` (read-only).
- Whatever each finding below cites: Contract v4 (`docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md`), `docs/contract/SOURCE_MAP.csv` (the rows named), Charter v5, `docs/plan/WAVE_2_WBS.md` (§0, §1, §2 cards W2-02, W2-16, W2-17, W2-18, W2-23, W2-24, W2-27 to W2-30, W2-46, W2-47, W2-49; §3, §4, §5, §6, §7), `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md` (row W2-I017), the ticket files of W2-02 (`.tickets/DAEO-zflj.md`) and W2-16 (`.tickets/DAEO-49o5.md`), `docs/plan/tools/validate_s1.py` (read only, never run), and in `docs/DECISION_REGISTER.md` the entries each finding names, plus DEC-722, DEC-105, DEC-006, DEC-058, DEC-064, DEC-090, DEC-092, DEC-614, DEC-620, DEC-712, DEC-714, DEC-718, DEC-720, DEC-721, DEC-724, DEC-727, DEC-728, DEC-729. Cite a decision for a rule only after reading that it says it.

## The review's findings (verbatim from the reviewer, at head `9dd15777`)

**MAJOR-1: the lite verdict defines one outcome, not three.**
- **Where:** §3.1, lines 56–88; §6.1, CAP-44.h text, lines 279–285; §7 has no question on this.
- **What it says:** it names the three verdicts and lists the conditions for ADOPTED_HEALTHY.
- **What is missing:** it never says what yields ADOPTED_WITH_ACCEPTED_EXCEPTIONS rather than NOT_ADOPTED_HEALTHY, which conditions may be excepted, or who accepts an exception.
- **What the sources say:** remediation, finding states and human gates stay in Wave 3 (CAP-44.g, which the §3.1 table marks "does not check"). MR-6 makes the owner the final authority. W2-28's card says only that anything short of ADOPTED_HEALTHY goes to the owner.
- **Why it matters:** KPI line 1 asks for "the three verdicts and the conditions". W2-02 must type "the conditions behind them", and W2-28 and W2-30 must choose among the three. Without a rule, the auditor in effect decides what an accepted exception is.
- **What would resolve it:** a stated rule for each verdict, or a question in §7 that names the owner as the only one who accepts an exception.

**MAJOR-2: the lite healthy conditions are narrower than the plan's own health checks on EXAMIN.**
- **Where:** §3.1 table, lines 69–84; §6.1, CAP-44.h text.
- **What it says:** the only operational condition is "gov doctor MATCH for the pinned framework.lock".
- **What the sources say:** W2-27 and W2-29 require `gov doctor` and `gov check` green, and a first ticket closed by `gov close` at exit 0. Exit criterion 3 requires `gov doctor` green on EXAMIN. CAP-54's acceptance requires "passes `gov doctor` at the minimal level". CAP-48.b (W3) has a healthy-repo definition that the CIT-P does not mention.
- **Why it matters:** under the proposed text, ADOPTED_HEALTHY could be issued with `gov check` red. That is the verdict exit criterion 6 cites, and the owner's go for the real repository (Q-9) rests on W2-28's verdict.
- **What would resolve it:** an owner question on whether these checks are lite conditions, or explicitly listed as not checked with a reason.

**MAJOR-3: F-1 and F-2 are found but not put to the owner.**
- **Where:** §10, lines 453–459; §2 apply-now cost, line 48; §7 has no matching question.
- **What was verified:** F-1: no ticket cites CAP-44.f except W2-49. W2-27 is an orchestrator integration ticket with 0 estimated LOC. W2-I017's list row names the role "engineer". F-2: W2-02 is `in_progress`, depends only on W2-01, and its KPI types the verdict "in the lite form Contract v4.2 states".
- **Why it matters:** exit criterion 7 needs CAP-44.f lite "delivered by a closed ticket". WBS §6 says new work that breaks an exit criterion goes to the owner as a package. W2-02 can close before Q-14.
- **What would resolve it:** questions in §7, or separate packages, on which ticket builds the lite A7 and A10 stage records, and on W2-02's ordering against W2-49. Each should come with a recommendation.

**MINOR-1: CAP-43.b lite overlaps Wave 1 items without saying what it adds.** §3.3, lines 120–130; §6.1, CAP-43.b text. CAP-02.a (W1, "File-hash manifest in framework.lock; gov doctor MATCH/DRIFT") and CAP-43's W1 acceptance already require a file-hash manifest. The CIT-P does not say that the lite item means the release's own manifest, built by the release step, as opposed to the lock on the install side. An exit auditor (W2-47) could read CAP-43.b lite as already delivered in Wave 1. Resolve with a statement of the distinction.

**MINOR-2: the lite A10 leaves out two parts the source map gives it, without saying so.** §3.2, lines 108–117. The CIT-P cites source map row 237 (Role F) but not row 283, "Stage A10 … + CAP-55 canaries" (CAP-55 is W1 and available), nor Role F's "Test Author" part. Resolve by including both in the lite A10, or naming them in "what stays for Wave 3" with a reason.

**MINOR-3: §8's list of source-map rows that state Wave 3 is incomplete.** §8, line 423 lists the protocol section rows only; it misses rows 235 and 237 (Roles D and F) and rows 280 and 283 (Distribution Protocol Stages A7 and A10), which also say W3.

**MINOR-4: §8 understates the state of the validator.** §8, line 422 says only the version check fails on 4.2. The code shows the validator is already red at the base (line 72 expects exactly W1-01 to W1-50 across all of `.tickets/`, which now also holds 50 W2 tickets), and by default it reads `~/gov-os-workbench` (DEC-723) and `docs/source/` through `git show` (excluded by `docs/SOURCES.md`). The proposed accepted red, and any agent run of the validator, rest on that understatement. Resolve with an accurate account, folded into the P-W2-11 point (F-5 already notes P-W2-11 is not on record).

**MINOR-5: Question A is missing one option.** §7 A, lines 339–352. The option: the lite A7 and A10 become conditions inside the lite CAP-44.h, and CAP-44.f stays in W3 with a note. It matches DEC-722's title ("two Wave 3 items") and exit criterion 7's grouping ("CAP-44.h with A7 and A10, CAP-43.b"); the reviewer's in-memory check shows it passes the A7 and A10 placement tests, which are satisfied by the CAP-44.h text alone. It changes the move from 17 to 20 items, and part of F-1's closure need. Resolve by adding the option with its cost.

**MINOR-6: the DEC-105 costs are qualitative, and the apply-now cost leaves things out.** §2, lines 46–50. The apply-now cost leaves out the build of the lite A7 and A10 stage records (F-1), regenerating 273 records with no generator in the repository, and the source-map update. Resolve with costs at least in tickets and days, using the WBS §4 method.

**MINOR-7: §5.3's "marks the row in part" is a row state no rule defines.** §5.3, lines 197–199. WBS rule 10 and exit criterion 10 allow closed with a commit, carried to Wave 3 or the backlog with a reason, or an owner-accepted exception. W2-49 claims W2-I017 in `list_rows`, but the lite delivery is W2-27 to W2-30. Resolve with a stated owner of the row's close and its form.

**MINOR-8: the §9 reversal covers only the two Contract files and the records.** It does not cover the owner's Q-14 entry and any DEC-090 amendment (Question E), any SOURCE_MAP or W2-I017 changes, a CAP-45.a rewording under Question D (ii), and a W2-02 schema already built against the lite text.

**NOTE-1: the proposed CAP-43 wave note puts plan content into the Contract.** §6.1, lines 244–246 name W2-16 and what that ticket builds, which would go stale if W2-16 changes. Question B's table (lines 357–362) also leaves out W2-16's "vendored skills carry their licence and version", which arguably falls under CAP-43.b's "adapter/capability versions".

**NOTE-2: no tests, code or radius in the impact list.** CAP-33's acceptance asks the impact to list tests and code "with a radius". The CIT-P lists no tests and no radius. At this base no other W2 acceptance tests exist, so the gap is small but unstated.

**NOTE-3: DEC-006 is still PROPOSED in the register.** Question E leans on CAP-54.a, which is Contract text sourced to DEC-006. DEC-090, which is ACCEPTED, refines DEC-006. The reasoning still holds, but the status is worth naming.

**NOTE-4: the header's `decisions_read` is incomplete.** It omits DEC-058, DEC-620, DEC-712, DEC-714, DEC-720 and DEC-724, which the body cites.

## Ticket mode: what you write

- Only `docs/changes/W2-49-CIT-P.md`. **Do not edit `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md` or anything else: nobody edits the Contract before the owner approves this CIT-P.**
- Answer each finding once, in the CIT-P itself: fix the text where a source settles it; where no source settles it, add a plainly marked question for the owner in §7 (with options, costs, your recommendation and confidence), never a rule of your own. The owner alone decides what an accepted exception is and anything else that is the owner's (MR-6).
- Also bring §11's order line in line with DEC-737 (staged), quoted above.
- Add a section at the end, "Review and answers", that names the review (independent auditor, read-only, at `9dd15777`, recommendation ACCEPT_WITH_FINDINGS) and gives, for each finding by its id, how it was answered: changed (where), or put to the owner (which question), or not taken (why, with the source). Keep every earlier section number stable where you can, so the review's line references still make sense.
- Keep the frontmatter's status PROPOSED (pending the owner's approval, Q-14), and add a line recording the review and this answer round.
- Proportion: answer the findings; add no new scope. Every rule you write comes from a named source, by id. Never the acceptance tests (MR-3): a test you think is wrong is returned as a package, never edited.

Run the ticket's acceptance tests in the foreground, to the end (never `-x`):
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m pytest tests/acceptance/W2-49 -q -p no:cacheprovider -rs`
The 24 CIT-P tests (`test_w2_49_cit_p.py`) must still pass. The Contract tests (42) and the CIT-E tests (10) stay red by design until the owner approves; report their counts and do nothing for them.

## Commit (ticket mode)

Commit only `docs/changes/W2-49-CIT-P.md`, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-49 (DAEO-ha8z): the CIT-P answers its independent review (DEC-722, CAP-33)" --trailer "Task: DAEO-ha8z" --trailer "Role: product-spec" --trailer "Implements: DEC-722" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your commit's hash; the file written; for each finding by id, how it was answered (changed / put to the owner / not taken, one line each); the full list of the CIT-P's questions for the owner after this round, each with its recommendation and confidence; the result of each suite you ran; anything you could not place or were refused, as a package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

Refused twice for the same call: stop and say so; no third try.
