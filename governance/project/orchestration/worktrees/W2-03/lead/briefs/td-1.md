# Brief: independent test designer — DAEO-ym8a (W2-03), STANDARD

You are a fresh independent test designer (MR-3). Ticket: DAEO-ym8a (W2-03, "Decisions as records, each with its own hash"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-03` on branch `w2/W2-03`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ym8a`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-03` and `w2/W2-03`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src` set **per command** (never in a session's `--settings` env). Your suite must exercise this worktree's code: every process a test starts gets `PYTHONPATH` pointing at this worktree's `src/`, found from the test files' own place, and one test shows that `gov.__file__` in a started process lies under it. Your README says how.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests (if any) use `GOV_DEV_TIERS` by name only and clone into a temporary folder. This ticket should need none.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository) anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`.
- The decision register `docs/DECISION_REGISTER.md` is the real one and read-only: your tests never write it; they build their own small registers in a temporary repository.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return at once.

## What you read

- The ticket file `.tickets/DAEO-ym8a.md` (read-only): its KPI lines, its `allowed_paths` and its sources (DEC-729, DEC-752).
- The ticket card in `docs/plan/WAVE_2_WBS.md` §2 (W2-03), and §0 (rules for every ticket).
- The list rows its KPI lines name, in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`: W2-L221, W2-M267, W2-M145, W2-M106, W2-L069. Their origin is described in `governance/project/bootstrap.md` (name it by that path; read the residual lines about the decision-citations check and the decision checker's exact comparisons and empty ids).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-012, DEC-274, DEC-276, DEC-277, DEC-463, DEC-473, DEC-479, DEC-485, DEC-521, DEC-579, DEC-718 (AR-1), DEC-746 (item 5), DEC-221, DEC-462, DEC-732. Contract items in `docs/contract/contract.yaml` that the card's AR-1 rests on, as you need them.
- **DEC-752 (owner, 2026-10-17; not yet in this worktree's register):** this branch carries W2-02's held branch (record types, the decision entry's schema and the `wbs_id` grammar). W2-02's files are not yours and not the implementer's. DEC-746 item 5 leaves loading real register entries against the decision entry's schema to this ticket.
- The schemas this ticket's KPI line 4 reads: the kernel's `template/governance/kernel/schemas/common.schema.json` (`decision_id`) and `template/governance/kernel/schemas/register-entry.schema.json` (the decision entry, added by W2-02; its description says W2-03 gives the span its form).
- The public interfaces the ticket must work with, and nothing private: the store (`gov.store`: `load`, `connect`, `digest`) as `gov rebuild` builds it, the record queries (`gov.records`: `records`, `edges`, `dangling`, …), the decision checker (`gov.decisions.check`), and the decision-citations check as `gov check` runs it (the command in `template/governance/kernel/checks/core-decision-citations.yaml`, with its JSON output and exit code). Earlier acceptance suites that exercise these (for example under `tests/acceptance/W1-10/`, `tests/acceptance/W1-11/`, `tests/acceptance/W1-26/` and `tests/acceptance/W2-02/`) show how a temporary repository with a path map and a register is built; read them for the form. You read no private part of an implementation to learn what a test should expect.

## The behaviour to test

In the words of the KPI lines and their sources:

1. **Each entry is a record with its own hash [AR-1, F-M5].** The store loads each `### DEC-nnn` entry of the register file the project's path map names as a record of its own, with its own sha256 over its own span (the entry's own text in the register, from its heading to the next). Two decisions never share a hash.
2. **A decision id resolves to its entry, not to the register [AR-1].** What the store answers for a decision id is that entry (its span and its hash), not the register file as a whole; and the decision-citations check resolves a cited decision id to its entry in the same way.
3. **What is not a decision record [W2-L221, W2-M267, W2-M145].** A register heading alone (no status line under it) is not a decision record, for the store and for the citations check. Any Markdown file that merely carries a decision id in its frontmatter is not a decision record: it does not satisfy a citation and is not loaded as that decision. (The rows' expected outcomes: "a register entry needs a heading and a status line to count"; "only a schema-valid decision record satisfies a citation"; "only decision files in the declared folders and live register entries count".)
4. **Grammar, case included [W2-M106, W2-L069].** Decision status and id comparisons follow the schema's grammar, case included: an id outside the `decision_id` grammar (case or digits) is no decision id; a non-canonical status (for example a lower-case one) is reported as a finding, not passed silently; a decision with an empty id is reported as a finding, never followed as `None` or `""`.
5. **Failure line.** An edited entry changes only its own hash: every other entry's hash stays the same. A duplicate DEC id is refused, and the refusal names both locations.

Where a KPI line leaves the expected public form open (for example, under which name the store gives a record's hash and span, what "refused" means for a duplicate, or which folders are "declared" for decision files), choose the reading the sources support, state it in the README as a reading taken, and keep the test to behaviour; if the sources do not support one reading, return a package instead of guessing.

## What you write

- Only inside `tests/acceptance/W2-03/`. No earlier ticket's tests are revised unless a KPI line names them; if you find that this ticket's KPIs require revising an earlier ticket's acceptance test, name it and return it as a package; do not edit it. No throwaway implementation is left in the tree.
- In proportion to the profile (DEC-221): STANDARD — every KPI line's success and failure, plus the key edge cases. No combinatorial expansion beyond what a KPI demands. Every covers id (AR-1, F-M5, and the five rows above) gets at least one test.
- Behaviour through public interfaces, never internals. Deterministic, no network. Every repository a test needs is a temporary one, built from scratch under pytest's `tmp_path`.
- A README that maps each KPI line to its tests and gives the expected red reason of each, says how the suite runs and how it exercises this worktree's code (DEC-732), and lists every reading taken.
- Red first: run the tests to the end, never with `-x`:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -m pytest tests/acceptance/W2-03 -q -p no:cacheprovider -rs`
  They fail for the reason the README states. Run also `PYTHONPATH=/home/usain/gov-os-worktrees/W2-03/src python3 -c "import gov; print(gov.__file__)"` and quote it.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-03 (DAEO-ym8a): acceptance tests, decisions as records" --trailer "Task: DAEO-ym8a" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2` and `git status --short`, and quote them.

## Return

Your final message is the only thing read. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in them: your commit's hash; the test count; the KPI lines and covers ids with their tests; the red reason as you saw it (counts: failed, passed, skipped); the `gov.__file__` line; every reading taken; every earlier test you would need revised; any package. Refused twice for the same call: stop and say so.

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
