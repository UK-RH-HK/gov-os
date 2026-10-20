# Brief: independent test designer — DAEO-ym8a (W2-03), STANDARD, two earlier cases rewritten (DEC-755)

You are a fresh independent test designer (MR-3). Ticket: DAEO-ym8a (W2-03, "Decisions as records, each with its own hash"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-03` on branch `w2/W2-03`. This ticket's implementation is built and committed. Two of W1-26's acceptance cases contradict this ticket's KPI lines. The orchestrator has decided both (DEC-755, below), and you make those two rewrites and nothing else.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ym8a`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-03` and `w2/W2-03`), and `git log --oneline -1` (expect `039740a1`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -c "import gov; print(gov.__file__)"` and quote the line.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. **Commit your rewrite before you run any long suite.** A correction after it is a new commit. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. This work needs none.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository) anywhere. A test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild` (with or without `--no-embeddings`), `gov close`, `gov adopt` or `gov pause`.
- The decision register `docs/DECISION_REGISTER.md` is the real one and read-only.
- **If the guard refuses you either path below, do not work around it and do not ask anyone else to write it: return a package (DEC-755 item 2).** Refused twice for the same call: stop and say so; no third try (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return at once.

## The decision you apply: DEC-755 (orchestrator, delegated, 2026-10-17; staged for the owner's commit, not in this worktree's register — apply it as written here)

1. **P-1 (a), stricter only.** In `tests/acceptance/W1-26/test_w1_26_decision_register_and_base.py`, the case `test_a_heading_after_a_closed_fence_records_its_id` writes a register heading after a closed fence with no status line under it. Under this ticket's KPI line 3 and list row W2-L221 ("a register entry needs a heading and a status line to count"), a heading alone is no entry. Add `- **Status:** ACCEPTED` under that fixture heading, so the case again tests what it was written for: the fence ends where it is closed, and the entry after it counts. The case keeps its purpose and its expectation.
2. **P-2 (a), stricter only.** In `tests/acceptance/W1-26/test_w1_26_decision_citations.py`, the form `no-type-id-in-grammar` of `test_a_decision_file_records_its_id` writes a file whose frontmatter has an `id` in the `decision_id` grammar but no `type: decision`, and expects it to satisfy the citation. Under list rows W2-M267 ("only a schema-valid decision record satisfies a citation") and W2-M145, it does not. Turn that form into a case where the commit citing the id is **flagged**, not counted. Choose the smallest clean form: for example, move it out of the parametrisation into its own case, named for what it now shows, and keep the other two forms as they are. Its docstring says what it shows. The case's assertions use the same helpers the file already uses.

Nothing else in W1-26 or in any other suite changes. You add no new behaviour and no new case beyond the P-2 one.

## What you read

- The two files above, in full, and their suite's README `tests/acceptance/W1-26/README.md` (if it maps the cases, update its line for the two cases to say what they now show, citing DEC-755).
- This ticket's KPI lines in `.tickets/DAEO-ym8a.md` (read-only) and its acceptance README `tests/acceptance/W2-03/README.md`.
- The rows W2-L221, W2-M267 and W2-M145 in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`.
- No private part of any implementation, to learn what a test should expect.

## Check

Run, in the foreground, each to its end (never `-x`):

- `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -m pytest tests/acceptance/W1-26 -q -p no:cacheprovider -rs`

Both rewritten cases are expected to pass against this branch's code (they describe it as built), and every other W1-26 case to stay as it was. If a rewritten case fails, report its output in full; do not change the code and do not weaken the case.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your W1-26 paths, in one commit, with the trailers in the final block (DEC-182, DEC-476, DEC-491):

    git commit -m "W2-03 (DAEO-ym8a): two W1-26 cases follow the entry and citation rules (DEC-755)" --trailer "Task: DAEO-ym8a" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Rewrite-Reason: W2-03 KPI line 3 and W2-L221 (a heading needs a status line to count); W2-M267 and W2-M145 (an id-only file does not satisfy a citation); DEC-755 items 1 and 2" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2`, `git show --stat HEAD` and `git status --short`, and quote them.

## Return

Your final message is the only thing read. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in them: your commit's hash and trailers; the diff of the two cases (short); W1-26's counts (passed, failed, skipped) and the output of any failure; the `gov.__file__` line; any refusal or package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Refused twice for the same call: stop and say so.

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
