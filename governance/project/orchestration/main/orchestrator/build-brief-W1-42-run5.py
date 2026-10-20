"""Assemble the lead brief of the next run on W1-42 (the report's run 6): ORION's cycle completed, the semantic index, the corrected exit report (DEC-686 to DEC-693)."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
h3 = open(B + "W1-42-A5-head3.md", encoding="utf-8").read()
rules = h3[h3.index("## Rules (they override"):h3.index("## The clones")]
rules = rules.replace(
    "Another lead is working in the worktree `/home/usain/gov-os-worktrees/W1-38` and runs the whole of `tests/` there",
    "The main orchestrator may run the whole of `tests/` in the main tree at the same time",
)

TOP = """You are a fresh ticket lead continuing ticket `DAEO-gjjf` (`W1-42`, "Wave 1 exit run on the dev tiers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-42` on branch `w1/W1-42`. You are a headless session: nobody answers questions while you work, and only your final message is read. The exit report calls the last run "run 5"; **this is run 6. It ends with the exit report corrected and verified.**

**Read first:** `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree (run 5's state: the clones, the commits, every worker session, the logs, the helpers `mkticket.py`, `tkclose.py`, `regress.py`, `mkevidence.py`); `docs/plan/wave-1-exit/EXIT-REPORT.md` as it stands; and in `docs/DECISION_REGISTER.md` (the branch holds a new merge of `w1/integrate`): DEC-482, DEC-579, DEC-585, DEC-651, DEC-673, DEC-674, DEC-677, DEC-678, DEC-682, DEC-683, DEC-685 to DEC-693. What runs 1 to 5 finished stands as reported; you do not repeat it.

**The guard in this worktree is newer than in run 5 (DEC-685): a tool it does not know is refused, `Monitor` and every `mcp__` tool among them. Wait for background work with Bash (`until [ -s <file> ]; do sleep 20; done`), as the common part says. A foreground command that outlives the tool's limit is killed: start every long run in the background and wait for its exit-code file.**

"""

WORK = """## The clones

- `/tmp/claude-1000/-home-usain-gov-os-worktrees-W1-42/1be98491-a02b-4f3c-accf-41da4cc96c6b/scratchpad/clones/a-dev-exit` (feature branch `feature/dimension-checked-addition` at `30996b6`, its main at `2d3d098`, adopted to A8) and `.../clones/b-dev-exit` (at `fc28272`, A2). Check each head first. Keep working in these folders. If either is gone, return PACKAGES with that as the first line. You never read or list `~/gov-os-workbench/`.
- **b-dev: nothing is run there** (DEC-687). It stays as reported.

## Decided ground (the owner, 2026-10-14; apply as written)

- **DEC-687, a-dev:** the trailers base is set in a-dev's path map at a-dev's real adoption boundary, its A8 commit `bb1852e`, the way DEC-482 set this repository's base (`trailers_base:` in `governance/project/path-map.yaml` here shows the form). Not at `540004a`, not at any other commit. The a-dev clone gets a **local bare remote under the clone's own folder**, so that `gov ci push` and the evidence note work as the local gate of DEC-585. Then ORION's `gov ci` and the merge are re-run.
- **DEC-686 and DEC-693, the empty semantic index:** the cause is found. In a-dev's path map no namespace says `embedding_policy: embedded` (20 say "not stated by the programme"); only the exact value `embedded` embeds (`src/gov/retrieval/semantic.py`), so a rebuild embeds nothing and says nothing. **DEC-693 says which namespaces get `embedded` and which `not embedded`: apply it.** The product's own gap (adoption gives no valid value and nothing reports it) is a separate round of the main orchestrator's, not yours: you change nothing under `src/`, `template/` or `tests/`.
- **DEC-688 and DEC-693, the eleven containment restores of 2026-10-12:** traced by the main orchestrator; no MR-3 breach (each names the then non-existent folder `tests/acceptance` itself, on read commands; no acceptance test existed in either clone before 2026-10-13). The reading that the sandbox's placeholder caused them is not reproduced: see piece 4.
- **DEC-692:** this branch is not merged into the integration branch until its red cases are resolved; your report says which cases are still red and what each waits for.
- **ORION-im01 is not closed again by you**, even if the trailers base takes its refusal's reason away: whether it gets a further `gov close` is with the owner. Say in your return what `gov check` in a-dev says of it after the base is set.

## What you do, in this order

Every step in a-dev is a step of the product's own method (DEC-537): under a ticket, by the role the method gives the file to, every commit with `Task:`, `Role:` and `Implements:` naming ids a-dev's store holds, each checked the moment it exists. Workers only through `gov launch` (DEC-161), from inside the clone, one writing worker at a time. Make no commit in a-dev without a `Task:` trailer.

### Piece 1: a-dev's path map (the trailers base and the embedding policies)

1. One ticket in a-dev for both edits of the path map (your `mkticket.py`; a real ticket with role, allowed paths naming the path map, KPIs: the base stands at `bb1852e` and `gov check`'s trailers check judges only later commits; the namespaces of DEC-693 say `embedded`, the others `not embedded`; the semantic index holds vectors after a rebuild). Its `sources` name records a-dev's store holds; the owner's two decisions reach a-dev's records the way ADR-011 did in run 5 (the orchestration skill gives the record of an owner answer to the orchestrator): one ADR in the owner's words for the trailers base and the embedding policies, citing DEC-687 and DEC-693 of this repository's register by id.
2. The edit itself by the role the method gives the path map to (run 2 and run 3 show who edited it: follow the role file and the path map's own namespace). Claimed, done, checked, closed with the ticket tool and a note as adoption and repair tickets are (DEC-658).
3. **The repair ticket `ade-5rcs`** (written by `gov close` on ORION-im01's refusal, without role, allowed paths and KPIs; six check findings rest on it): its subject is the missing trailer that the base now settles. Complete it truthfully as the orchestrator (role, allowed paths, KPIs, a source), with a note that the trailers base of DEC-687 settles it, and close it with the ticket tool and that note. If the checks still refuse it for a reason you cannot settle inside the method, report the findings word for word and go on.
4. `gov rebuild` in a-dev **with embeddings, run by you, not by a sandboxed worker** (the embedding service is local; if it is not available the command says so: report its words and return that as a package, do not go on to piece 3). Then `gov check --json` in a-dev: report every family's colour, and each red finding counted by cause.

### Piece 2: ORION's CI and merge (DEC-687)

1. A bare remote under the clone's own folder (a folder the clone's `.gitignore` or its local exclude file keeps out of the tree and that no namespace needs to hold; say where you put it and how it is kept out of `git status`), added as the clone's remote. Nothing is pushed anywhere else.
2. `gov ci` in the full form of DEC-585: the checks, the job, the staged-secrets scan, the push, the evidence note; each answer kept. **A red CI is reported with its findings, not worked round.** If `job` still answers `CI_NOT_MEASURED` because a tool is not on the runner, report it word for word: an install is the owner's.
3. The merge of the feature branch into the clone's main (one committing command, `-m`, the three trailers), after CI, and the clone's tests on its main afterwards.

### Piece 3: the retrievals and the canary (DEC-686)

1. The two scenario questions RETR-A-04 and RETR-X-02 with `gov retrieve` in a-dev, once each, every answer to a file; report only the shape (batches, citations by id and hash, parent expansions, a synthesis note or none, the stopping reason, the facets' states, the validator's answer). The kept bundles under `docs/plan/wave-1-exit/evidence/` are replaced by the new answers, less the evidence text, as run 5 kept them; the old ones are kept beside them under a name that says "before the embedding policies".
2. `gov doctor --json` in a-dev: the canaries, lexical and semantic, by id, never by value (DEC-604).

### Piece 4: the placeholder reading of the restores (DEC-688, DEC-693), confirm or refute

In a stand-in project in your session's temporary folder (built from the template as the suites build them, with no `tests/acceptance` folder at HEAD and one in-progress ticket), launch one `product-spec` worker through `gov launch` whose brief asks only for three harmless read commands with Bash. Then read the stand-in's containment findings: does a finding name `tests/acceptance`, or the dot-files of the root, though the worker changed nothing? One paragraph in the report under criterion 3, saying "reproduced" or "not reproduced" and what you saw. Thirty minutes at most; if it does not reproduce, say so and leave the trace's facts as DEC-693 records them.

### Piece 5: the exit report corrected (in this worktree)

`docs/plan/wave-1-exit/EXIT-REPORT.md` and its evidence, corrected where the facts changed and nowhere else; each corrected verdict says what changed since run 5. The overall verdict is whatever the criteria then give: **do not turn a criterion to MET that the evidence does not carry.**

- **Criterion 1:** ORION's CI and merge as they now are; ARGUS exactly as before, named with its reason, and one line that the owner weighs it at the exit decision (DEC-687).
- **Criterion 2 and the canaries:** the re-run's results; the cause (DEC-686, DEC-693) and that the product gap has its own round.
- **Criterion 3:** the `MultiEdit` hole is closed: the W1-02 round of DEC-685 is merged on `w1/integrate` at `1b76e2ee` and is in this branch by the merge; the installed CLI offers no `MultiEdit`, so no worker or lead of the exit run could call it. The eleven restores explained as DEC-693 records, with piece 4's result. Your verdict follows from that.
- **Criterion 4:** unchanged unless a new close record exists; add the row of the new path-map ticket only if you measured it.
- **For the exit auditor, one line each from the register:** DEC-683 (DAEO-3ef2), DEC-689 (DAEO-6mk8), DEC-690 (DAEO-emkd) closed with the ticket tool and why; DEC-685 and its two named residuals (inline shell in skills, the launcher's wiring check); DEC-692.
- **Evidence list:** DEC-691's backup entry, quoted from the register (its heads are not yet given there: write what the register says); the live clones' paths and final heads after this run, with the note that they are newer than every backup.
- **Deviations:** run 6's own; and run 5's file of programme excerpts under this worktree's runtime folder (`.gov-runtime/scratch/lead/log/retr-a-dev-feature.json`), which run 5 left out of the list: **move it to your session's temporary folder now and say so (DEC-673).**

Commit: `--trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c"`.

### Piece 6: verify

W1-42's suite (name each case that is still red and what it waits for); every suite under `tests/acceptance` in the close's form (parallel with the close's plugin, then the serial-only entries, in the background with an exit-code file), `tests/unit`, the validator. `W1-49/test_w1_49_live_session.py` is flaky (DEC-676) and the W1-46 live-session cases need the network (DEC-689): a failure there is run alone once more and both results reported. Then a checkpoint (`gov checkpoint` for DAEO-gjjf), committed, and your return.

## Decision packages

You decide none. **A `gov close` of any ticket is not run in this run.** Anything about weakening a check, a base at another commit, an install, a role other than the test designer writing under a test folder, or the owner's steps: return at once.

## Return

`DONE` with: the branch head and commits; a-dev's commits of this run with the three trailers checked; which namespaces got which embedding value; `gov check` in a-dev family by family, and what it says of ORION-im01 and of `ade-5rcs`; the rebuild's words on the semantic index; CI answer by answer; the merge; the two retrievals' shapes and the canaries; piece 4's result; each corrected verdict and the overall verdict; W1-42's suite with the red cases named; each other suite's result; residuals for `bootstrap.md`; learning metrics; deviations; temp folders left; the clones' paths and heads. Or `PACKAGES`, `ESCALATION` or `LEAD_CHECKPOINT`. **Whatever the first word, the message carries the twelve fields below.**
"""
tail = "\n".join(open(B + name, encoding="utf-8").read() for name in ("TWELVE-FIELDS.md", "LEAD-common.md", "LEAD-steps.md"))
text = TOP + rules + WORK + "\n" + tail + "\n**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
with open(B + "W1-42-A5-run5.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
