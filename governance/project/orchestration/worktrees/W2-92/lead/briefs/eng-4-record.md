# Brief: engineer, W2-92 (DAEO-n0wb), run 1, batch 4 (the measure's record)

You are a fresh engineer. Ticket: DAEO-n0wb (W2-92), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-92` on branch `w2/W2-92`. Your one job: write `docs/research/W2-92-memory-measure.md`, the record of the ticket's re-measure (KPI 5), from the run's own outputs, in W2-61's form, and commit it. You run no measure, no rebuild and no retrieval of the measured questions yourself: the lead ran them. Your budget is about 45 minutes.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-n0wb`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-92` and `w2/W2-92`). If anything differs, stop and say so.
- You were started in the old launch form (not sandboxed), as the earlier engineer batches were. A tripwire compares the trees before and after you: write nothing in this worktree but `docs/research/W2-92-memory-measure.md`, and nothing elsewhere but `/tmp/gov-os-lead-W2-92/eng4/` (your temp folder). Never write under `/home/usain/gov-os-runs/`.
- Run everything in the foreground, one command after another; return only after your commit exists. Never wait in the foreground past a few minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory first (DEC-836):** for what you need to know about the repository (for example W2-61's record form, DEC-833's two figures), ask `gov retrieve` before reading files at random: `cd /home/usain/gov-os-worktrees/W2-92 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-92/src python3 -m gov.cli.main retrieve "<question>" --json`. **DEC-860:** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked; never one giant query or context. **DEC-859:** a code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Never ask `gov retrieve` the measured questions themselves.
- **Policy 2 (DEC-820):** reads are open, writes closed. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-92/` (nor the branch `w2/W2-92-tests` or its worktree); (d) the hidden half of any evaluation set: never read or run it, never `--part hidden`. You may read the visible half's questions and gold (`/home/usain/gov-os-runs/W2-92/measure/fixtures/evaluation/memory-retrieval/visible/`) and the run's records.
- **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never another form; search named folders instead; count the refusals in your return.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; write files with the Write and Edit tools and literal absolute paths; anything longer goes in a script file under `/tmp/gov-os-lead-W2-92/eng4/` written with the Write tool. A refused form is not retried in another disguise. No `rm`.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Never copy the repository or a folder of it. Install nothing. No subagents that write. Never write `tests/acceptance/**` or `.gov-runtime/**`.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits; never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). In the record itself, also write commits as 12 digits, and never a full 40-hex hash beside a key-like word.
- **Scratch budget (DEC-898):** your share is 1 GB and 50,000 files and folders; measure `du -s --inodes /tmp/gov-os-lead-W2-92/eng4` and `du -sh` before you return.

## The run's outputs (read-only)

- The two clones and the measure's tree, each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached: `/home/usain/gov-os-runs/W2-92/base` at `7ca16b19df3f` (the ticket's base), `/home/usain/gov-os-runs/W2-92/head` at the ticket's final code commit (`/tmp/gov-os-lead-W2-92/log/rebuild-head.commit`), `/home/usain/gov-os-runs/W2-92/measure` at `w2/integrate`'s head `c38a5b49bc86` (the measure's code and the visible set).
- The retrievers: `/tmp/gov-os-lead-W2-92/bin/gov-base` and `/tmp/gov-os-lead-W2-92/bin/gov-head` (the pinned launcher's body under a first line that sets `PYTHONPATH` to that clone's `src/`): each clone's stores were built by, and its questions answered by, that clone's own code, because the change is code (the code under test builds and answers).
- The rebuilds: `/tmp/gov-os-lead-W2-92/bin/rebuild-base.sh` and `rebuild-head.sh`; their outputs `/tmp/gov-os-lead-W2-92/log/rebuild-base.{json,err,exit,start,end}` and `rebuild-head.*` (the start is when the command began to wait on the shared lock `/tmp/gov-os-rebuild.lock`; the JSON's own timing gives the rebuild's length). Give each digest and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db` in each clone (read them with `sha256sum`; do not open the stores for writing).
- The measures: `/tmp/gov-os-lead-W2-92/bin/measure-base.sh` and `measure-head.sh`; their outputs `/tmp/gov-os-lead-W2-92/log/measure-base.*` and `measure-head.*`; the records under `/home/usain/gov-os-runs/W2-92/records/` (the control's is `measure-memory-retrieval-visible-20261101T140024036524Z.json`; the head's is the other, written with `--compare` on the control). Visible half only (`--part visible`); the hidden half was neither read nor run.
- The earlier figures to put beside these: W2-61's baseline (`docs/research/W2-61-baseline.md`, §5 and §8); W2-86's record (`/home/usain/gov-os-worktrees/W2-86/docs/research/W2-86-memory-measure.md`, not yet on `w2/integrate`: hit@5 11/20, full evidence 11/20, in the bundle 15/20, and its per-question table).

## What the record holds (KPI 5 and its failure line)

In W2-61's form (its baseline and W2-86's record are the models): the clones and retrievers; the stores and their digests and hashes; the runs (tree, retriever, start, end, length, exit, stderr, record, `--compare`); the totals; the per-question table (hit@5, first gold rank, in the bundle, full evidence with pieces found of needed, control against head); what changed and why; deviations; how to repeat it.
- **Both figures together, every time either is given (DEC-833):** hit@5 against CAP-10's floor of 85 and the owner's target of 95 % (DEC-957), and full evidence against the target of 99 %; plus the in-the-bundle count. Never one figure without the other, in the totals or in prose.
- **The graph and code-graph questions named:** which visible questions name a record (an id, a W2 id or a record title) or a symbol, so that the record route or the code route takes them, and what each route did for each (from the head record's own calls and evidence, and the questions' text; for the code route, a plain name counts when the head code's rule takes it). Say plainly where a question moved up, moved down or stayed, and why, as far as the records show; where they do not show why, say so.
- Beside W2-86's and W2-61's figures, in one table.
- The scope note: the visible half only; W2-61h's enlarged set (graph and code-graph categories) is not yet in, so the hidden half and the new categories are not measured here.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`. Commit only that file:

    git commit -m "W2-92: the re-measure of memory on the visible half, control and head (KPI 5)" --trailer "Task: DAEO-n0wb" --trailer "Role: engineer" --trailer "Implements: DEC-957, DEC-833, DEC-860" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/W2-92-memory-measure.md

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
