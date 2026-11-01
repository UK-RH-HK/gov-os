# Brief: engineer, W2-92 (DAEO-n0wb), run 2, batch 7 (the measure's record, updated)

You are a fresh engineer. Ticket: DAEO-n0wb (W2-92), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-92` on branch `w2/W2-92`. Your one job: update `docs/research/W2-92-memory-measure.md` (written in run 1, commit `6a47d598670b`) with run 2's re-measure, from the run's own outputs, in W2-61's form, and commit it. You run no measure, no rebuild and no retrieval of the measured questions yourself: the lead ran them. Your budget is about 45 minutes.

## Step 0, before any work

Run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-n0wb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-92` and `w2/W2-92`). If anything differs, stop and say so. You were started in the old launch form (not sandboxed), as the earlier batches were; a tripwire compares the trees before and after you.

## What changed since run 1 (DEC-1006, on `w2/integrate`'s register)

Run 1's record measured the head `fb0c8c430171` (hit@5 10/20, full evidence 12/20, in the bundle 15/20; Q17 lost, 42 min). The CTO decided four packages (DEC-1006): P-1 a store whose record graph is missing or unreadable fails only the record and closure routes; P-3 a plain word joins the code route only with a code cue in the question (calls, callers, callees, defined, function, method, class and their inflections, or backticks or call form; a word shaped as code still joins without one); P-4 one code-graph tool session per process (and, found while building it, a per-process cache of the record titles' front matter), with the context-reproducibility check well under its 600 s limit. Run 2's code is `d72c96fc029c` (`git log -p 264a9965ca4e..d72c96fc029c -- src` shows it; you may read it, as the record's author). The record keeps run 1's measure as history and adds run 2's as the result: the ticket's figures are run 2's.

## The run's outputs (read-only)

- The clones (`git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached): `/home/usain/gov-os-runs/W2-92/base` at `7ca16b19df3f` (the control, unchanged since run 1: its store and its record are reused, DEC-833's kept control), `/home/usain/gov-os-runs/W2-92/head` now at `d72c96fc029c` (`/tmp/gov-os-lead-W2-92/log/rebuild-head2.commit`), `/home/usain/gov-os-runs/W2-92/measure` now at `w2/integrate`'s `160736409bc4` (the measure's code and the visible set; `src/gov/retrieval/measure.py` and the visible set are unchanged since run 1's `c38a5b49bc86`: check with `git -C /home/usain/gov-os-runs/W2-92/measure diff --stat c38a5b49bc86 HEAD -- src/gov/retrieval/measure.py fixtures/evaluation/memory-retrieval/visible`).
- The retrievers: `/tmp/gov-os-lead-W2-92/bin/gov-base` and `gov-head` (each clone's own code builds and answers, because the change is code).
- Run 2's head rebuild: `/tmp/gov-os-lead-W2-92/bin/rebuild-head2.sh`, outputs `/tmp/gov-os-lead-W2-92/log/rebuild-head2.{json,err,exit,start,end,commit,disk}`. Give its digest and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db` in the head clone (`sha256sum`; never open the stores for writing).
- Run 2's head measure: `/tmp/gov-os-lead-W2-92/bin/measure-head2.sh`, outputs `/tmp/gov-os-lead-W2-92/log/measure-head2.{json,err,exit,start,end}`; its record `/home/usain/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T205024907715Z.json`, written with `--compare` on the control's `measure-memory-retrieval-visible-20261101T140024036524Z.json` (13:47-14:00 UTC). Run 1's head record `measure-memory-retrieval-visible-20261101T161333491429Z.json` stays as history. Visible half only (`--part visible`); the hidden half was neither read nor run.
- The context-reproducibility check alone at `d72c96fc029c` (as the runner runs it): `/tmp/gov-os-lead-W2-92/log/ctx-head2.{start,end,exit,out}` (20:39:15-20:44:08, green, 293 s; run 1: head 1,761 s, base 476 s; limit 600 s). The engineer's count during building: 180 tickets, 2 context questions on the code route (code-shaped words), one tool session for the process.
- The earlier figures to keep beside these: W2-61's baseline (`docs/research/W2-61-baseline.md`, §5 and §8) and W2-86's record (`docs/research/W2-86-memory-measure.md` on `w2/integrate`: `git show w2/integrate:docs/research/W2-86-memory-measure.md`).

## What the record holds (KPI 5 and its failure line)

- In W2-61's form, as run 1's record has it: clones and retrievers; stores, digests and hashes; the runs (tree, retriever, start, end, length, exit, stderr, record, `--compare`); the totals; the per-question table (hit@5, first gold rank, in the bundle, full evidence with pieces found of needed: control, run 1's head and run 2's head); what changed and why; deviations; how to repeat it.
- **Both figures together, every time either is given (DEC-833):** hit@5 against CAP-10's floor of 85 and the owner's target of 95 % (DEC-957), and full evidence against the target of 99 %; plus the in-the-bundle count. Never one figure without the other, in the totals or in prose.
- **The graph and code-graph questions named:** which visible questions name a record or a symbol so that the record route or the code route takes them at run 2's code (a plain name counts only with a code cue now), and what each route did for each. Say plainly where a question moved up, moved down or stayed against the control and against run 1's head, and why, as far as the records show (in particular Q10, Q11, Q17, Q09, Q08, Q14); where they do not show why, say so.
- The run's length against the control's and run 1's head, and the context check's time.
- One table beside W2-86's and W2-61's figures.
- The scope note: the visible half only; the cue gate was tuned on the visible half and is to be judged again on W2-61h's set (DEC-1006), not measured here; the hidden half is neither read nor run.

## Standing rules (read first)

- Write nothing in this worktree but `docs/research/W2-92-memory-measure.md`, and nothing elsewhere but `/tmp/gov-os-lead-W2-92/eng7/` (your temp folder). Never write under `/home/usain/gov-os-runs/`.
- Run everything in the foreground, one command after another; return only after your commit exists. Never wait in the foreground past a few minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory first (DEC-836):** for what you need to know about the repository (W2-61's record form, DEC-833's two figures), ask `gov retrieve` before reading files at random: `cd /home/usain/gov-os-worktrees/W2-92 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src python3 -m gov.cli.main retrieve "<question>" --json`. **DEC-860:** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked; never one giant query or context. **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Never ask `gov retrieve` the measured questions themselves.
- **Policy 2 (DEC-820):** reads are open, writes closed. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-92/`; (d) the hidden half of any evaluation set: never read or run it, never `--part hidden`. You may read the visible half's questions and gold (`/home/usain/gov-os-runs/W2-92/measure/fixtures/evaluation/memory-retrieval/visible/`) and the run's records.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never another form; search named folders instead; count the refusals in your return.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under `/tmp/gov-os-lead-W2-92/eng7/` written with the Write tool. A refused form is not retried in another disguise. No `rm`.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Never copy the repository or a folder of it. Install nothing. No subagents that write. Never write `tests/acceptance/**` or `.gov-runtime/**`. Never write in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). In the record itself, also write commits as 12 digits, and never a full 40-hex hash beside a key-like word.
- **Scratch budget (DEC-898):** your share is 1 GB and 50,000 files and folders; measure `du -s --inodes /tmp/gov-os-lead-W2-92/eng7` and `du -sh` before you return.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`. Commit only that file:

    git commit -m "W2-92: the re-measure of memory after DEC-1006, visible half, control and head (KPI 5)" --trailer "Task: DAEO-n0wb" --trailer "Role: engineer" --trailer "Implements: DEC-957, DEC-833, DEC-860" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/W2-92-memory-measure.md

After it, `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the totals as written (both figures together); the graph and code-graph questions you named and what changed for each; anything the records could not tell you; the guard refusals you met; whether you used `gov retrieve` and for what; your scratch measure.

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

Your final message gives these twelve fields first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), with any machine-readable payload after them. Refused twice for the same call: stop and say so.
