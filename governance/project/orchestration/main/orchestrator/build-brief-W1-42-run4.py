"""Assemble the lead brief of run 4 on W1-42: a new top, head3's rules and clones sections, run 4's work, the twelve fields, the common part, the steps."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
h3 = open(B + "W1-42-A5-head3.md", encoding="utf-8").read()
rules = h3[h3.index("## Rules (they override"):h3.index("## The clones")]
rules = rules.replace(
    "Another lead is working in the worktree `/home/usain/gov-os-worktrees/W1-38` and runs the whole of `tests/` there",
    "Another lead may be working in the worktree `/home/usain/gov-os-worktrees/W1-38` and running the whole of `tests/` there",
)

TOP = """You are a fresh ticket lead continuing run 3 of ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. **This is the last run: it ends with the exit report written and verified.**

**Run 3 returned PACKAGES; they are answered.** Read `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree first (run 3's state: the clones, the commits, the worker sessions of all three runs, the logs, run 3's helpers `mkticket.py` and `tkclose.py`). The branch now holds a merge of `w1/integrate` (`0b608121`) that brings the register to DEC-681. Read in `docs/DECISION_REGISTER.md`, before anything else: DEC-511, DEC-651, DEC-658, DEC-662, DEC-664 to DEC-668, DEC-670, DEC-671, DEC-673, DEC-674, DEC-676 to DEC-681. What runs 1 to 3 finished stands as reported; you do not repeat it.

"""

CLONES = """## The clones

- `/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/a-dev-exit` (branch `feature/dimension-checked-addition`, head `82dca10`, adopted to A8) and `.../clones/b-dev-exit` (branch `feature/data-retention-rule`, head `fc28272`, at A2). Check each head first. Keep working in these two folders: the workers' session logs are filed by the clone's path.
- If either folder is gone, stop and return PACKAGES with that as the first line: the owner's operator holds backups (DEC-681), and the main orchestrator has one brought back. You never read or list `~/gov-os-workbench/`.

## The answers to run 3's packages (decided ground; apply them as written)

- **PKG-A, the a-dev close (the owner, DEC-678): option (d).** No trailers base is set (the offending commit `540004a` is not a-dev's adoption boundary: A6 and A8 were committed after it), nobody classes the finding with `--disposition`, and **`gov close ORION-im01` is not run again**: ORION-im01 stays in progress, its refused close and its repair ticket `ade-5rcs` reported as they are. **Instead: one small new implementation ticket in a-dev, a real, minimal ORION change, done entirely by the book, and closed with `gov close`, with no exception and no disposition. That ticket is the DEC-511 proof.** See piece 1.
- **PKG-B, b-dev (DEC-674, accepted by the owner in DEC-680):** no further close in b-dev. ARGUS-im01 stays in progress with its refusal (`CONTEXT_FAILED`, the source `REQ-004` not in the store at A2) and its repair ticket `bde-0kr6` reported. No correction of the ticket, no further adoption.
- **PKG-7 and the other items of DEC-674** (the ARGUS audit's major finding, a closed specification edited in place, b-dev's audit report form, the close gate judging the lead's own ticket commits, repair tickets left untracked, `heldout --help` executing, the audits' lesser findings): no work; each is one line among the exit report's residuals, marked "Wave 2 list".
- **The A5 verdict hash (DEC-674):** left; `verdict_commit` is the anchor.
- **The a-dev namespace of the two secret-named files (the owner, DEC-679):** left as written; a named residual.

## What you do, in this order

### Piece 1: the DEC-511 proof, a new implementation ticket in a-dev, by the book (DEC-678)

Every step below is a step of the product's own method (the kernel's orchestration skill and brief templates, DEC-537). Nothing is skipped, nothing is done by hand that a role does, and nothing is repaired after the fact.

1. **Choose the change.** A real, minimal change to ORION's code that the closed specification ORION-SPEC-DIMADD and the owner's recorded answers (DEC-656, DEC-662) already settle, so that it needs no new answer from anyone: for example a behaviour the specification states and ORION-im01's cases and code do not yet reach, or one of the ORION audit's lesser findings that is a code change. It has an observable behaviour a test can hold, and it is a few lines. A documentation-only or ticket-only change is not a real change. **If nothing qualifies without a new feature answer, return PACKAGES at once with the candidates you weighed and your recommendation; do not invent a requirement.**
2. **The ticket.** Create it in a-dev with the ticket tool and your `mkticket.py` (planned id `ORION-im02`): KPIs (success and failure lines), the acceptance tests' path, `allowed_paths`, `sources` naming only records a-dev's store holds, its dependencies. **Its creating commit carries `Task: ORION-im02`, `Role: orchestrator` and `Implements:` with ids the store holds. Every later commit that names the ticket carries all three trailers too; check each the moment it exists (`git log -1 --format='%(trailers)'`), and have a worker of the same kind amend its own commit while it is still the unpushed tip if one is missing. A commit of yours you check before you make it.** Before anything else, read how the close's trailers gate picks its commits (`src/gov/close/` in this worktree) so that you know exactly which commits it will judge for the new ticket; if it would judge a commit that already exists and lacks a trailer, return that as a package before starting the ticket.
3. **Claim it** (`tk start`), committed.
4. **Tests first (MR-3):** a fresh `independent-test-designer` launched on the ticket; behaviour and sources only in its brief; you check red for the stated reason.
5. **A fresh engineer** inside the ticket's `allowed_paths`; you verify green: the new cases, ORION-im01's 84 cases, the programme's existing tests. **MR-3 check:** no commit of the engineer touches a tests path; the clone's guard findings hold no new containment finding.
6. **`gov checkpoint` for the ticket in the clone, committed; `gov rebuild` in the clone; then `gov check --json` in the clone and read it before the close.** If a hard-block family is red for a reason that is not this ticket's (run 3 left product traceability red with 43 findings on the commits of runs 1 and 2), do not close yet: read in `src/gov/close/` whether the close refuses on it. If it would, **return PACKAGES at once, before running the close**, with the family, its findings counted by cause, and this fact for the owner: a-dev's adoption's last commit is `bb1852e` (A8, 2026-10-13 17:41). The close counter in a-dev stands at 1 of 3, and a close that is known to refuse is not run.
7. **`gov close ORION-im02`, once.** Report the envelope word for word: exit code, each gate, each check, the test runs. **Clean means `ok` true with no disposition, no exception, no baseline entry made for it.** If it refuses, return PACKAGES at once with the envelope; no repair and no second close in this run; exit 4 follows DEC-651.
8. **After a clean close:** measure the ticket once, `PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH" PYTHONPATH=src python3 -m gov.cli.main telemetry ORION-im02 --json --root <a-dev path> --ticket-session <session id>=<role>` with one `--ticket-session` for each of its worker sessions, run from this worktree (the command reads the session logs; you do not). Report the envelope's `governance_tokens`, `governance_share`, `not_measured` and `agent` word for word. This is the one `gov telemetry` you run.

### Piece 2: the rest of a-dev's cycle

`gov ci` in the form the clone supports without a remote; the merge of the feature branch into the clone's main branch (one committing command, `-m`, the trailers `Task:`, `Role: orchestrator`, `Implements:`); one `gov retrieve` on a question of the feature, with the bundle's shape reported (batches, citations by id and hash, parent expansions, a synthesis note or none, the stopping reason, the validator's answer). ORION-im01 being open does not stop these; say in the report that it is open. b-dev: nothing more.

### Piece 3: the exit report (in this worktree)

`docs/plan/wave-1-exit/EXIT-REPORT.md`, written by you (the ticket's role is `orchestrator` and its only path is `docs/plan/wave-1-exit/**`), to what `tests/acceptance/W1-42/README.md` asks, case by case. Read the suite's README and its 24 cases' names first, so that the report holds what they read. Besides what the earlier heads listed (the commit of the exit run; each exit criterion of `docs/plan/WAVE_1_WBS.md` section 4 with its evidence; per programme the feature, the tickets, the cycle steps, the adoption stage reached, the close results; the retrieval measurements of run 1 and the one real retrieval; per ticket, all 50, the three learning metrics; the parallel-ticket evidence; the residuals; every run's deviations), it says:

- **The clean close (DEC-511, DEC-678):** ORION-im02's envelope; and, beside it and as plainly, that ORION-im01's close refused with `TRAILER_MISSING` on the lead's own commit `540004a` and ARGUS-im01's with `CONTEXT_FAILED`, both left without a disposition.
- **Governance share (DEC-677):** per ticket, the estimated share, the measured parts, and the measured total wherever a close record exists, with "not measured" and its reason elsewhere. The table for runs 1 to 3 is at `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/share-table.md` (measured by the main orchestrator): copy it in whole, add ORION-im02's row from your own measurement, and list every worker session of all four runs (programme, ticket, role, session id). State that the exit auditor judges exit criterion 4 on this (DEC-677), and that the threshold is 15 %.
- **Owner steps (DEC-668, DEC-670):** B1 done at `71ae763f`, with the outputs DEC-668 quotes; B2 part 1 done on a throwaway repository, with the five outputs DEC-668 quotes; **B2 part 2 (the freeze on this repository) and B3 (the lefthook install) open**, the owner's, after the leads have finished.
- **The doctor (DEC-667):** exits 3; version drift alone makes it unhealthy, against DEC-210; Wave 2 list; named so that a red doctor caused by drift alone is not misread.
- **For the exit auditor, one line each, from the register:** the six red cases on the integration branch and their repair (DEC-665, DEC-669, DEC-675); the W1-49 live-session case, flaky, no user-level hooks (DEC-671, DEC-676); the secrets-indexing red of 2026-10-13 caused by the orchestrator's safety copies under the runtime folder (DEC-673); the items of DEC-674; the a-dev namespace (DEC-679).
- **Evidence list:** the backups of the exit clones (DEC-681): the six entries with their heads, under `~/gov-os-workbench/archive/w1-42-exit-clones/`, quoted from the register; the live clones' paths and final heads.

Commit: `--trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c"`.

### Piece 4: verify

W1-42's suite (the cases that wait on the owner's open steps stay red, each named with what it waits for; any other red is yours to put right in the report, never in a test); every earlier suite under `tests/acceptance/`, `tests/unit`, the validator, in the form the close uses (parallel with the close's plugin, then the serial-only entries). Known on this branch, not yours and not to be touched: `W1-49/test_w1_49_threshold.py` (two cases) and `W1-33/test_w1_33_agent_definitions.py::test_the_research_definition_is_unchanged` are red until the W1-38 round merges (DEC-665); `W1-49/test_w1_49_live_session.py` is flaky (DEC-676): if it fails, run it alone once more and report both. Then a checkpoint (`gov checkpoint` for DAEO-gjjf), committed, and your return.

Workers are started only through `gov launch` (DEC-161), from inside the clone, one writing worker at a time.

## Decision packages

You decide none. **Anything about a `gov close` that refuses or would refuse, about weakening a check to get a close, about a role other than the test designer writing under a test folder, or about the owner's steps: return at once.**

## Return

`DONE` with: the branch head and commits; which change ORION-im02 is and why it qualified; its every commit with the three trailers checked; the close envelope and whether it was clean; its share measurement; CI, the merge, the retrieval; W1-42's suite with the waiting cases named; each other suite's result; the exit report's path; residuals for `bootstrap.md`; learning metrics for ORION-im02 and for the run; deviations; temp folders left; the clones' paths and heads. Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`. **Whatever the first word, the message carries the twelve fields below.**
"""
tail = "\n".join(open(B + name, encoding="utf-8").read() for name in ("TWELVE-FIELDS.md", "LEAD-common.md", "LEAD-steps.md"))
text = TOP + rules + CLONES + "\n" + tail + "\n**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
with open(B + "W1-42-A5-run4.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
