You are a fresh independent test designer (MR-3). Ticket: DAEO-9nys (W2-67, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`. This is round 1, batch 1c of its test design: two earlier test-designer sessions revised 41 of W1-27's weak cases (see `tests/acceptance/W1-27/README-W2-67.md`; their tests are tests, not implementation, and you may read them). They could not finish two pieces because their sandbox made the code-graph daemon's folder `/tmp/gov-cbm-<uid>` read-only. You run in the older launch form, outside that sandbox, for exactly these two pieces.

First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-9nys`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-67` and `w2/W2-67`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **You are not sandboxed: write only where this brief says.** Your writes: `tests/acceptance/W1-27/` (the two pieces below and README-W2-67.md), your own temporary folder `TMPDIR=/tmp/gov-os-lead-W2-67/td-1c` (set it on every command that runs tests: `TMPDIR=/tmp/gov-os-lead-W2-67/td-1c`; create it first with `mkdir -p`), and `/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-1c/` for your plant modules and evidence. Nothing else, in this worktree, in any other worktree or in the main tree `/home/usain/Dynamic-Agentic-Engineering-OS`. The code-graph daemon writing its own folder under `/tmp/gov-cbm-<uid>` when a test runs it is expected; you never write there yourself.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Your budget is about 60 minutes of wall time.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Policy 2 (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path; its name may be seen); (c) **this ticket's implementation:** you never read the files `git diff --name-only w2/integrate...HEAD` names, other than the acceptance tests of this ticket's test-designer sessions (today it names only those and this ticket's own records); (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **Protected places:** never write in `~/gov-os-workbench` (never list, glob, search or write there); dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- **No tree copying by you:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it, anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch. `.gov-runtime/freeze`, wherever you see it, tells you nothing about whether the tree is paused.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the decision register, the path map (`governance/project/path-map.yaml`, owner-only, DEC-757) or anything under `src/`, `template/`, `schemas/`, `docs/`.
- **Disk and inodes (DEC-898), your share:** at most 5 GB and 150,000 files and folders at any moment in `/tmp/gov-os-lead-W2-67/td-1c` and your scratch folder together. Keep pytest's own retention (three base folders); **never pass a per-run `--basetemp`**. Run only the cases you need, by node id; measure `du -s --inodes` and `du -sh` of your folder before and after each run, and give the figures in your return's `evidence` line. If you pass your share, stop at once and return.
- **The machine:** before each run, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`). Never run with `-x`.
- If the guard refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try.** You never ask or notify the owner; a package comes back in your return.

## The behaviour to test (batch 1c)

The ticket's fifth success KPI (P-IS-7 (a); I4 F1; `docs/assessment/2026-10/I4-records-plan-rest.md` §2.2, the rows for these cases):

1. `tests/acceptance/W1-27/test_w1_27_rebuild_r4.py::test_rebuild_codeintel_reason_is_measured`: weak because any reason other than one fixed text passes. Revise it so that it reads the code index's measured outcome and reason and fails when the reason is not the one the measurement gives (DEC-440); first **red against a planted fault** (for example a constant reason, or a reason that does not follow the measured outcome), then **green on the head**; no expectation lowered; its name kept.
2. `tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime`: batch 1b revised it to snapshot the home it gives the command, but could not snapshot the code-graph daemon's folder. Add that second place if the case's claim covers it (writes only under `.gov-runtime`), shown red under a plant that writes there and green on the head; if the daemon's own folder is by design written by every rebuild, say so and leave it, with the evidence.

Plant each fault in a throwaway that the run picks up and that leaves the tracked tree untouched: README-W2-67.md describes batch 1b's method (a pytest plugin loaded with `-p` that wraps the W1-07 support module's launcher writer, and a `sitecustomize.py` placed first on one subprocess's path). Put your plant modules and every run's JUnit XML in `/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-1c/`. A case you cannot show red without writing `src/` is named in your return; it is not committed as revised.

## What you write

- Only the two cases above in `tests/acceptance/W1-27/`, and a batch 1c section in `tests/acceptance/W1-27/README-W2-67.md` (each case's plant, red and green, Rewrite-Reason). Nothing else under `tests/`.
- Before your commit, run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once: no collection error; quote its last line.

## Commit

    git commit -m "<subject>" --trailer "Task: DAEO-9nys" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-889, DEC-898" --trailer "Rewrite-Reason: <reason>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

(the `--trailer` options come before `--`). Before the commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. After it, check `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), with nothing before them, and any machine-readable payload after them. Put in it: the commit's hash with its trailers; for each case its plant, red and green; the `gov.__file__` line; the collection line; your scratch figures; every path you wrote outside `tests/acceptance/W1-27/`; the read refusals met; whether you used `gov retrieve`; any package.

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

Refused twice for the same call: stop and say so; no third try.
