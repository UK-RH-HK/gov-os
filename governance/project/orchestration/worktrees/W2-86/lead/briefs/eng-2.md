# Brief: engineer, DAEO-jsg1 (W2-86), batch 2 — the measure's record

You are a fresh engineer. Ticket: `DAEO-jsg1` (`W2-86`), profile STANDARD. You work in the worktree `/home/usain/gov-os-worktrees/W2-86` on branch `w2/W2-86` only. In this batch you write one file, `docs/research/W2-86-memory-measure.md`, from your lead's outputs. You change no other file.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-jsg1','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (the twelve fields), naming what happened. Never delete anything outside this worktree.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-jsg1`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-86` and `w2/W2-86`) and `git rev-parse --short=12 HEAD` (expect `338c14fa6475`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another; return only after your commit exists.
- **The code under test (DEC-732), word for word:** **In this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads open, writes closed (DEC-820).** Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it, never type its path); **(c) you never read `tests/acceptance/W2-86/`, by any tool; you may run those tests and see their names, results and failure messages;** **(d) the hidden half of any evaluation set (`fixtures/evaluation/**/hidden/**`), in any tree, never read or run; the measure here was run on the visible half only, and your record says so.** The record quotes no question's text, no gold answer and no text of a retrieved item: scores only (ids, counts, ranks, digests, pass or fail), as W2-61's record does. Never read or name the qualification oracle. Never write in `~/gov-os-workbench`.
- **DEC-849, read refusals:** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Your scratch: `.gov-runtime/scratch/<name>/` is refused in this sandbox; use the sandbox's own temporary folder (`printenv TMPDIR`) by its literal path. A refused form is not retried in another disguise (DEC-409).
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. No copy of the repository. Never touch `tests/**`, `governance/**`, `src/**` or `.gov-runtime/**` outside scratch. Install nothing. Never run `gov rebuild`, `gov close`, `gov adopt` or `gov pause`. Do not run the measure yourself: the figures are your lead's, measured outside the sandbox (inside it, gov embeds on the CPU and its figures prove nothing).
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits everywhere (in the record too), never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token. A sha256 of 64 hex digits is fine in the record, as W2-61's has.
- **Disk budget (DEC-898):** your share is 1 GB and 50,000 files and folders outside the tracked tree; keep the sandbox's own temp folder; measure what you leave there at the end.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return `AUTH_REQUIRED`.

## What you read

- `docs/research/W2-61-baseline.md` and `docs/research/W2-87-memory-measure.md` in this worktree: the form to follow (W2-61's sections 1 to 6 and 8; W2-87's per-question table with several columns), and the figures to set beside yours.
- The ticket file `.tickets/DAEO-jsg1.md`: KPI lines success 1, 4 and 5 and failure 5 (both figures, always together; the hidden half never read or run).
- Your lead's outputs, all in `/home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/` (read-only to you):
  - `measure-outputs.md`: the lead's summary of every figure, path and digest, with the deviations to report. **This is your source;** the files below are there for you to check it.
  - `log/rebuild-base.json`, `log/rebuild-head.json`, `log/rebuild-*.gate`: the two rebuilds;
  - `log/measure-base.json`, `log/measure-head.json`, `log/measure-*.times`, `log/measure-*.record`: the two measures;
  - `log/vectors.json`: the vector counts and the vector and lexical diffs between the two stores;
  - the supplementary run's output, outside this tree: `/home/usain/gov-os-runs/W2-86/logs/tree-measure-wt.json` (it names a commit in full: copy only its 12 first digits).
- `measure-outputs.md` also gives a supplementary head measured with the tree's own code, and the lead's spot retrievals for Q18 and Q19: put both in the record (the supplementary run beside the others in §4 and §5, marked as such; the spot retrievals in the Q18 and Q19 paragraph), with its deviations.

## What you write: `docs/research/W2-86-memory-measure.md`

In W2-61's form (headed sections, tables, scores only), holding:

1. **What was measured, and where:** the three clones (`/home/usain/gov-os-runs/W2-86/head` at the head, `base` at `9dc5288161c4`, `measure` at `w2/integrate`'s head), their commits, the pinned gov's version and its commit, each run's `retriever.gov_file`, the measure's code and set, the budgets, the visible half only.
2. **The stores' fingerprint:** each rebuild's digest, gates, times, exit and store states, and the sha256 of the three store files.
3. **The runs:** times, exits, records, `--compare`.
4. **The totals, both figures together, always:** hit@5 against CAP-10's floor of 85, full evidence against the owner's target of 99 %, and the in-the-bundle count, for: the head, the control, W2-87's figures (11, 11 and 15 of 20 at `cffef92c8534`) and W2-61's baseline (8, 12 and 14 of 20 at `23079f92a6fa`), side by side. Never one figure without the other.
5. **Per question, visible half:** one row per question Q01 to Q20 with W2-61's baseline, W2-87's head, the control and the head side by side (each cell: hit@5, first gold rank, in the bundle, full evidence found of needed), and what changed from the control to the head. **Q18 and Q19 named** in their own paragraph: what the change did for each and why, from the outputs only (their governing sources are under `template/`: the PreCompact hook and the role files).
6. **The vectors:** the chunks with vectors under `template/governance/kernel/roles/`, `hooks/` and `skills/`, and under the vendored set (`vendor/`, `skills/superpowers/<skill>/`, `bin/`) and `template/.rulesync/`, in each store; the paths whose vector set differs between the two stores (must be only newly embedded `template/` files and this ticket's own new files); the files whose lexical content differs (must be only the files the ticket changes or adds). Say that the store digest covers the record graph only (`src/gov/store/loader.py:305`), so the vector set is the figure compared (the ticket's KPI 4).
7. **Deviations and what they mean:** as `measure-outputs.md` lists them, above all: the retriever is the pinned gov, which predates W2-87's authority order, so the control and the head do not carry W2-87's ranking, and W2-87's figures (measured with W2-87's own code) are not like for like; the comparison head against control isolates this ticket's data change, the retriever being the same.
8. **How to repeat it:** W2-61's §8 with this ticket's places.

## Check and commit

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.check.citations` if it accepts no arguments (else skip it and say so), and `git diff --stat 338c14fa6475` showing only your one new file.
- Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`. One commit:

      git commit -m "W2-86 (DAEO-jsg1): the memory measure after the kernel template is embedded, beside the control, W2-87 and W2-61's baseline" --trailer "Task: DAEO-jsg1" --trailer "Implements: DEC-952, DEC-941, DEC-833" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

- Then `git log --oneline -2` and `git status --short`, quoted.

## Return

Your commit's hash (12 digits); the record's sections; whether you used `gov retrieve` and for what; the read refusals you met (DEC-849); any package.

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

Your return gives the twelve fields first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
