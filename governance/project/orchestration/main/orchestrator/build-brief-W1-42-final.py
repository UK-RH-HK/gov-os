"""Assemble the lead brief of the final pass on W1-42: the owner's steps B1 to B3 recorded, the ticket-tool closes in a-dev reflected, a-dev re-measured, the red cases settled or named, verified (DEC-703 to DEC-709)."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
h3 = open(B + "W1-42-A5-head3.md", encoding="utf-8").read()
rules = h3[h3.index("## Rules (they override"):h3.index("## The clones")]
old = ("Nobody runs `gov close`, `gov rebuild`, `gov adopt` or `gov pause` against this worktree or the main tree; nobody pushes (DEC-465). "
       "**Nobody runs `gov pause` anywhere, the clones included (DEC-428, DEC-660).** Another lead is working in the worktree "
       "`/home/usain/gov-os-worktrees/W1-38` and runs the whole of `tests/` there; the main tree is not yours.")
new = ("Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree; nobody pushes (DEC-465). "
       "**Nobody runs `gov pause` anywhere, the clones included (DEC-428, DEC-660).** No other lead is running; the main tree is not yours.\n"
       "- **The lefthook pre-commit hook now runs on every commit in this worktree (B3, DEC-706).** It runs `gov ci checks G1 G2` "
       "(about 5 minutes) and a scan of what is staged. **Before each commit here: stage, then "
       "`PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json` in this worktree, then commit (DEC-709).** That is the only "
       "`gov rebuild` run against this worktree. Never `--no-verify`, never `core.hooksPath`, no other way past the hook: **a refused commit "
       "is not worked round; return PACKAGES at once with the hook's output word for word** (keep it in `.gov-runtime/scratch/lead/log/`). "
       "Run each commit in the background with an exit-code file, since the hook can outlive the tool's limit. The clones have no hook installed: "
       "their commits are unchanged.")
assert old in rules
rules = rules.replace(old, new)

CLONES = "/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones"

TOP = """You are a fresh ticket lead continuing ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. **This is the final pass of the exit run. It records the owner's steps, reflects the owner's decisions since run 7 in the exit report, re-measures a-dev after two ticket-tool closes, settles the red cases of W1-42's suite that a record can settle and names exactly what each other one waits for, and ends verified.** No worker writes code; no `gov close` runs in this pass.

**Read first:** `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree, run 7's state file `.gov-runtime/scratch/lead/log/r7-state.txt`, the exit report `docs/plan/wave-1-exit/EXIT-REPORT.md` as run 7 left it (`5eb3b012`), and run 7's helpers under `.gov-runtime/scratch/lead/` (you may reuse them, checking each path and head first). Then merge `w1/integrate` into this branch (one committing command, `-m`, trailers `Task: DAEO-gjjf` and `Role: orchestrator`; the merge-base rule of the common part applies; the hook runs on it: rebuild first, as the rules say) and read in `docs/DECISION_REGISTER.md`: DEC-428, DEC-442, DEC-458, DEC-668, DEC-692, DEC-698, DEC-703 to DEC-709.

**The guard in this worktree refuses a tool it does not know (DEC-685), `Monitor` and every `mcp__` tool among them. Wait for background work with Bash (`until [ -s <file> ]; do sleep 20; done`). A foreground command that outlives the tool's limit is killed: start every long run, every commit included, in the background and wait for its exit-code file.**

"""

WORK = f"""## The clones

- `{CLONES}/a-dev-exit`: feature branch `feature/dimension-checked-addition` at `127227c` (checked out), its main at `736669f`. `{CLONES}/b-dev-exit`: at `fc28272`, main `3b1ad56`. **Check each head and `git status` first**; if either is missing or at another head, return PACKAGES with that as the first line. Under the guard a lead writes only in its worktree and under `/tmp`, so they stay there (DEC-699). You never read or list `~/gov-os-workbench/`.
- **b-dev: nothing is run there** (DEC-687). **a-dev: no commit, no push, no merge in this pass**; you only measure there (`gov check`, below).
- Keep every answer you need for the report in `.gov-runtime/scratch/lead/log/` as soon as you have it (shapes and counts, never a programme's text, DEC-673).

## Decided ground since run 7 (the owner, 2026-10-14 and 2026-10-15; apply as written)

- **DEC-704:** ORION-im01 was closed in a-dev with `tk close` by the owner's decision (`5fb754d`), named for the exit auditor: its second `gov close` refused only with TRAILER_MISSING on `540004a`, before a-dev's base `bb1852e`, because `gov close`'s trailer gate does not read `trailers_base` (on the Wave 2 list). **ORION's cycle proof for criterion 1 stands on ORION-im02's clean `gov close`, CI and merge.**
- **DEC-708:** the repair ticket `ade-ke2y` was closed with `tk close` (`127227c`), accepted by the owner.
- **DEC-703:** DAEO-cdoi (W1-41) was closed in this repository with `tk close` after the round of DEC-694 (probe PASS, merge `945643ec`, every test green); its worktree is removed.
- **DEC-668, DEC-706, DEC-707, the owner's steps:** B1 (Stop and SubagentStop) done at `71ae763f`; B3 (the lefthook install) done; B2 (the manual freeze, pause and lift from a plain terminal) done in two parts, on a throwaway repository (DEC-668) and on this one (DEC-707), with a write refused while frozen. W1-42's KPI line for it is met.
- **DEC-709:** every commit here is staged, rebuilt (`--no-embeddings`), then committed through the hook; a refusal is returned, not worked round.
- **DEC-692 stands:** this branch is not merged into the integration branch until its red cases are resolved; the merge and the worktree's removal are the main orchestrator's, after your return.
- **Criterion 4:** a `tk close` gives no close record and no telemetry, so ORION-im01 still has no row; say so.

## What you do, in this order

### Piece 1: a-dev re-measured after the two ticket-tool closes

`gov check --json` in a-dev on its feature head `127227c` (as run 7 ran it, with embeddings available; rebuild there only if the check says the index is stale, and say so). Report every family's colour, each red finding counted by cause, and how each differs from run 7's three red checks (context reproducibility, core-claims through ade-ke2y, core-schema). Do not run `gov ci`, push or merge again: run 7's CI and merge stand as reported, and the report says that the closes came after them.

### Piece 2: the owner's steps as records (in this worktree)

1. `docs/plan/wave-1-exit/evidence/owner-freeze-check.json`, in the form W1-42's suite reads (`tests/acceptance/W1-42/test_w1_42_exit_report.py`, the case `test_owner_froze_paused_and_lifted_on_a_throwaway_repository_and_on_this_one`, and `w1_42_support.py`): an entry `throwaway` and an entry `this`, each with `repository`, `terminal: "plain"` and the four steps in the order `gov pause`, `gov status`, `gov pause --off`, `gov status`, each with its answer **exactly as the owner reported it** in DEC-668 (throwaway: `~/gov-b2-throwaway`, a copy of the a-dev-exit clone, since deleted) and DEC-707 (this repository). The owner's report gives each command's output; the commands follow from those outputs (`{{"ok": true, "command": "pause", ...}}` is `gov pause`; the `"pause": {{...}}` status lines are `gov status`; the prompt `type LIFT-… to lift the freeze` is `gov pause --off`, `src/gov/pause/command.py`). Put the status before the freeze, which comes before the four steps, in a field of its own (`status_before`). Say in a `note` field that the commands are read from the outputs the owner reported. `this` carries `refused_write`: `PreToolUse:Write hook error: frozen: all writes denied` (on a Write of `.gov-runtime/scratch/orchestrator/b2-probe.txt`, not created). Nothing invented: a value the records do not give is left out and named in your return.
2. The report's "Owner's steps" table: B1, B2, B3 each `done`, each with its record named (the register entries by id, the evidence file for B2).

### Piece 3: the exit report brought to the owner's decisions

`docs/plan/wave-1-exit/EXIT-REPORT.md` and its evidence:
- **Criterion 1:** ORION's cycle with ORION-im01's close as it went (`tk close` by DEC-704, after a refused `gov close` on pre-base history), the proof standing on ORION-im02 (DEC-704); `ade-ke2y` closed (DEC-708); ARGUS exactly as before, with the line that the owner weighs it at the exit decision (DEC-687).
- **Piece 1's measurement** beside run 7's.
- **For the exit auditor:** one line each for DEC-703, DEC-704, DEC-706, DEC-707, DEC-708, DEC-709, beside the lines earlier runs wrote.
- **Evidence list:** the backups as DEC-698, DEC-705 and DEC-706 record them, quoted (live-run7 for both clones; live-run7b for a-dev at `127227c`/`736669f`); the live clones' paths and heads, which this pass does not change.
- The overall verdict is whatever the criteria then give: **do not turn a criterion to MET that the evidence does not carry.**

The report and its evidence are written the way run 7 wrote them. Commit (rebuild first): `--trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c"`.

### Piece 4: verify and the red cases

W1-42's suite: name each case still red and exactly what it waits for. Run 7 had four:
- the owner's freeze: piece 2 should settle it; if it stays red, say which assertion and why;
- the worktree list (`git-worktree-list.txt`): it waits for this ticket's own worktree to be removed, which follows the merge DEC-692 holds back; say so, and write nothing for it;
- RETR-X-02's parent expansion and the governance share on each programme: say again, from the cases' own assertions, what each one needs, and what in the evidence would or would not give it. Change nothing to make them pass.

Then every suite under `tests/acceptance` in the close's form (parallel with the close's plugin, then the serial-only entries, in the background with an exit-code file; run 7's helpers show the form), `tests/unit`, the validator. Latency cases and the W1-46/W1-49 live-session cases: a failure there is run alone once more and both results reported (DEC-372, DEC-676, DEC-689). Then a checkpoint (`gov checkpoint` for DAEO-gjjf), committed (rebuild first), and your return.

## Decision packages

You decide none. A hook refusal, a head that is not as stated, anything about weakening a check or a test, an install, or the owner's steps: return at once.

## Return

`DONE` with: the branch head and commits, each with its hook result; a-dev's `gov check` family by family against run 7's; the evidence file's fields and anything the records did not give; each verdict and the overall verdict, and what differs from run 7; W1-42's suite with each red case and what it waits for; each other suite's result; residuals for `bootstrap.md`; learning metrics; deviations; temp folders left; the clones' paths and heads. Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`. **Whatever the first word, the message carries the twelve fields below.**
"""
tail = "\n".join(open(B + name, encoding="utf-8").read() for name in ("TWELVE-FIELDS.md", "LEAD-common.md", "LEAD-steps.md"))
text = TOP + rules + WORK + "\n" + tail + "\n**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
with open(B + "W1-42-A5-final.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
