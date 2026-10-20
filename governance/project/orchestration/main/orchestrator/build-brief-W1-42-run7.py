"""Assemble the lead brief of run 7 on W1-42: run 6's clone work, lost on the restart, redone in the restored clones; ORION-im01's further close; the report corrected again (DEC-694 to DEC-699)."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
h3 = open(B + "W1-42-A5-head3.md", encoding="utf-8").read()
rules = h3[h3.index("## Rules (they override"):h3.index("## The clones")]
rules = rules.replace(
    "Another lead is working in the worktree `/home/usain/gov-os-worktrees/W1-38` and runs the whole of `tests/` there",
    "Another lead is working in the worktree `/home/usain/gov-os-worktrees/W1-41` and runs the whole of `tests/` there",
)
assert "W1-41" in rules

CLONES = "/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones"

TOP = """You are a fresh ticket lead continuing ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. **This is run 7. It redoes in the restored clones the clone work of run 6 that a restart of the machine destroyed, closes ORION-im01 once more, and ends with the exit report corrected from the new results and verified.**

**What happened (DEC-699).** Run 6 committed its corrected report (`42add8c9`) and was in its final verify when the machine was restarted. The restart cleared `/tmp`, and both live clones with it. The operator has restored them from the archive at the paths they had: a-dev at the heads of the end of run 5 (feature branch `30996b6`, main `2d3d098`), b-dev at `fc28272`. **Everything run 6 did inside the a-dev clone is gone**: ADR-012, the ticket ORION-ad04 and its path-map edit, the repair ticket ade-5rcs completed and closed, the two rebuilds with embeddings, the bare remote and its pushes, `gov ci`, the merge `0aef4b9`, the two retrievals and `gov doctor`. The clone commits the report names for run 6 (`8efdecc` to `0aef4b9`, `c063857`) no longer exist anywhere. **The report at `42add8c9` is unverified:** every fact it states about run 6's work in a-dev is re-measured in this run and replaced by what this run measures. Run 6's stand-in project of the placeholder check (piece 4) was not in a clone: its kept evidence (`docs/plan/wave-1-exit/evidence/containment-placeholder-probe.json`, `launch/p4-probe.json`) stands and is not run again.

**Read first:** `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree (run 5's state; run 6 wrote none), the commit `42add8c9` (`git show --stat 42add8c9`, then the report's text), run 6's helpers and logs under `.gov-runtime/scratch/lead/` (`mkticket.py`, `tkclose.py`, `ci-a.sh`, `shape.py`, `mkevidence6.py`, `report6.py`, `report6b.py`, `verify6.sh`, `briefs/` and `tickets/` for ORION-ad04, `log/a-ad4.json`, `log/a-ci-r6-*`, `log/a-rebuild-r6-*`, `log/check-a-r6.json`, `log/doctor-a-r6.json`): they show how run 6 did each step, and you may reuse them, checking each path and head first. In `docs/DECISION_REGISTER.md` (the branch holds a new merge of `w1/integrate`): DEC-482, DEC-579, DEC-585, DEC-651, DEC-658, DEC-673, DEC-674, DEC-677, DEC-678, DEC-682, DEC-683, DEC-685 to DEC-701. What runs 1 to 5 finished stands as reported.

**The guard in this worktree refuses a tool it does not know (DEC-685), `Monitor` and every `mcp__` tool among them. Wait for background work with Bash (`until [ -s <file> ]; do sleep 20; done`), as the common part says. A foreground command that outlives the tool's limit is killed: start every long run in the background and wait for its exit-code file.**

"""

WORK = f"""## The clones

- `{CLONES}/a-dev-exit` (feature branch `feature/dimension-checked-addition` at `30996b6`, its main at `2d3d098`, adopted to A8) and `{CLONES}/b-dev-exit` (at `fc28272`, A2). **Check each head and `git status` first.** If either is missing or at another head, return PACKAGES with that as the first line. Keep working in these folders: under the guard a lead writes only in its worktree and under `/tmp`, so they stay there (DEC-699). You never read or list `~/gov-os-workbench/`.
- **b-dev: nothing is run there** (DEC-687). It stays as reported.
- **The machine can be restarted again.** Keep every answer you will need for the report in this worktree's `.gov-runtime/scratch/lead/log/` as soon as you have it (shapes and counts, never a programme's text, DEC-673), so that a lost clone loses no measurement.

## Decided ground (the owner, 2026-10-14; apply as written)

- **DEC-687, a-dev:** the trailers base is set in a-dev's path map at a-dev's real adoption boundary, its A8 commit `bb1852e`, the way DEC-482 set this repository's base. Not at `540004a`, not at any other commit. The clone gets a **local bare remote under the clone's own folder**; run 6 found that the harness refuses an edit of the clone's local exclude file and a `git init` inside its git folder, and put the bare repository at `target/ci-remote.git` (kept out of the tree by the clone's own `.gitignore`), added as the remote `ci-local`: do the same, and push nowhere else.
- **DEC-693, accepted by the owner as DEC-696:** `embedded` for code, orion-specifications, specification, decisions, documents, interfaces, examples, benchmarks, research, tickets, adoption-records; `not embedded` for kernel, project, generated-agent-files, ci, datasets, root; the namespace of the two secret-named files unchanged. For the three namespaces DEC-693 does not name (adapters, repository, tests) run 6 chose `not embedded` by its reading: do the same and say so again.
- **DEC-695: one further `gov close ORION-im01` (count 2 of 3)**, run by you in the clone, once, after the trailers base stands at `bb1852e` and the embedding policies are in the clone's path map, both committed and the rebuild done. ORION-im01 is ORION's feature ticket: its close completes ORION's cycle for criterion 1. **If it refuses for any reason other than history from before the adoption boundary, stop: start nothing more on it, write your checkpoint and return PACKAGES with the envelope word for word. An exit 4 always stops for the owner (DEC-651).** A refusal on history from before the boundary alone is reported word for word and you go on with the rest.
- **DEC-692:** this branch is not merged into the integration branch until its red cases are resolved; your report says which cases are still red and what each waits for.
- **DEC-697:** run 6's stand-in did not reproduce the placeholder reading of the eleven restores; the report keeps that result and says that, under DEC-697, it is reported and not recorded as a residual.
- The product's own gap (adoption gives no valid value, nothing reports it) has its round on W1-41 (DEC-694), running in another worktree: you change nothing under `src/`, `template/` or `tests/`.

## What you do, in this order

Every step in a-dev is a step of the product's own method (DEC-537): under a ticket, by the role the method gives the file to, every commit with `Task:`, `Role:` and `Implements:` naming ids a-dev's store holds, each checked the moment it exists. Workers only through `gov launch` (DEC-161), from inside the clone, one writing worker at a time. Make no commit in a-dev without a `Task:` trailer.

### Piece 1: a-dev's path map (the trailers base and the embedding policies), as run 6 did it

1. ADR-012 in the owner's words for the trailers base and the embedding policies, citing DEC-687, DEC-693 and DEC-696 of this repository's register by id (by the orchestrator, as ADR-011 was).
2. One ticket ORION-ad04 for both edits of the path map (role product-spec, the allowed path the path map, KPIs as run 6 wrote them), started; the edit by one product-spec session through `gov launch`; checked; closed with the ticket tool and a note (DEC-658).
3. The repair ticket `ade-5rcs` completed truthfully as the orchestrator (role, allowed paths, KPIs, a source) with a note that the trailers base settles it, and closed with the ticket tool and that note.
4. `gov rebuild` in a-dev **with embeddings, run by you** (the embedding service is local; if it is not available the command says so: report its words and return that as a package). Then `gov check --json` in a-dev: every family's colour, each red finding counted by cause, and what it says of ORION-im01 and of `ade-5rcs`.

### Piece 2: ORION-im01's close (DEC-695)

`gov close ORION-im01` once, in the clone, on its feature branch, every answer to a file. Report the envelope's code, every finding by cause and commit, the test runs and the governance share it states. If it closes with exit 0, take the telemetry of ORION-im01 once, the way run 5 took ORION-im02's (`log/share-ORION-im02.json` shows the form), so that criterion 4 can hold a second row.

### Piece 3: ORION's CI and merge (DEC-687)

1. The bare remote as above.
2. `gov ci` in the full form of DEC-585: the checks, the job, the staged-secrets scan, the push, the evidence note; each answer kept. **A red CI is reported with its findings, not worked round.** `job` answering `CI_NOT_MEASURED` because openspec is not on the runner is reported word for word: the install is the owner's.
3. The merge of the feature branch into the clone's main (one committing command, `-m`, the three trailers), after CI, and the clone's tests on its main afterwards.

### Piece 4: the retrievals and the canary (DEC-686)

1. The two scenario questions RETR-A-04 and RETR-X-02 with `gov retrieve` in a-dev, once each, asked as run 6 asked them, every answer to a file in your session's temporary folder (they hold programme text); report only the shape (batches, citations by id and hash, parent expansions, a synthesis note or none, the stopping reason, the facets' states, the validator's answer). The kept bundles under `docs/plan/wave-1-exit/evidence/` are replaced by the new answers, less the evidence text; the files "before the embedding policies" stay as they are.
2. `gov doctor --json` in a-dev: the canaries, lexical and semantic, by id, never by value (DEC-604).

### Piece 5: the exit report corrected again (in this worktree)

`docs/plan/wave-1-exit/EXIT-REPORT.md` and its evidence, with every fact of run 6's work in a-dev replaced by run 7's measurement: the clone commits, the namespaces and values, the rebuild's figures, `gov check`, CI answer by answer, the merge, the retrievals, the canaries, the W1-42 suite's red cases. Where run 7 measured the same as run 6, say so; where it differs, say how. The overall verdict is whatever the criteria then give: **do not turn a criterion to MET that the evidence does not carry.**

- **Criterion 1:** ORION's cycle as it now is, with ORION-im01's close as it went; ARGUS exactly as before, named with its reason, and one line that the owner weighs it at the exit decision (DEC-687).
- **Criterion 4:** a row for ORION-im01 only if its close and telemetry exist.
- **Deviations:** a line for the restart (DEC-699): run 6's clone work lost and redone in run 7, run 6's clone commits gone; and run 7's own deviations.
- **For the exit auditor:** DEC-694 (the W1-41 round), DEC-695, DEC-697, DEC-699 one line each, beside the lines run 6 wrote.
- **Evidence list:** the backups as DEC-698 records them, quoted; the live clones' paths and final heads after this run, with the note that they are newer than every backup until the operator's next copy (DEC-698).

Commit: `--trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c"`.

### Piece 6: verify

W1-42's suite (name each case that is still red and what it waits for); every suite under `tests/acceptance` in the close's form (parallel with the close's plugin, then the serial-only entries, in the background with an exit-code file; run 6's `verify6.sh` shows the form), `tests/unit`, the validator. `W1-49/test_w1_49_live_session.py` is flaky (DEC-676) and the W1-46 live-session cases need the network (DEC-689): a failure there is run alone once more and both results reported. Then a checkpoint (`gov checkpoint` for DAEO-gjjf), committed, and your return.

## Decision packages

You decide none. **The one `gov close` of this run is ORION-im01's (DEC-695).** Anything about weakening a check, a base at another commit, an install, a role other than the test designer writing under a test folder, or the owner's steps: return at once.

## Return

`DONE` with: the branch head and commits; a-dev's commits of this run with the three trailers checked; which namespaces got which embedding value; `gov check` in a-dev family by family, and what it says of ORION-im01 and of `ade-5rcs`; the rebuild's words on the semantic index; ORION-im01's close, word for word, and its telemetry if taken; CI answer by answer; the merge; the two retrievals' shapes and the canaries; each corrected verdict and the overall verdict, and what differs from run 6; W1-42's suite with the red cases named; each other suite's result; residuals for `bootstrap.md`; learning metrics; deviations; temp folders left; the clones' paths and heads (the operator backs them up after this run, DEC-698). Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`. **Whatever the first word, the message carries the twelve fields below.**
"""
tail = "\n".join(open(B + name, encoding="utf-8").read() for name in ("TWELVE-FIELDS.md", "LEAD-common.md", "LEAD-steps.md"))
text = TOP + rules + WORK + "\n" + tail + "\n**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
with open(B + "W1-42-A5-run7.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
