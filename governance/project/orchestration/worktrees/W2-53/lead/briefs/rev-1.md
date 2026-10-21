You are a fresh reviewer (independent-auditor, read-only). Ticket DAEO-7rr2 (W2-53, "The probe gate measures every later merge against git's own merge of its parents"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-53` on branch `w2/W2-53`, at the head `c8d3fb308fd3178206a67ec8a842cdc2ae34089b`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing in the repository.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-7rr2`) and `git rev-parse --show-toplevel --abbrev-ref HEAD HEAD` (expect `/home/usain/gov-os-worktrees/W2-53`, `w2/W2-53` and the head above). If anything differs, stop and say so.
- **DEC-732, the code under test (word for word from the lead's brief):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another (each under 10 minutes); your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- Write no file of the repository and make no commit; no `git checkout`, `git reset`, `git clean`, `git stash`, merge, rebase, push or tag in this worktree. No subagents. Install nothing.
- A probe that needs a repository builds a temporary one from scratch in a folder of your own under `/tmp` (for example with `mktemp -d`), and runs `gov close` there with this worktree's `src/` on `PYTHONPATH`. The acceptance suites' support modules (`tests/acceptance/W2-53/w2_53_support.py`, `tests/acceptance/W2-01/w2_01_support.py`) show how a project is built; you may import them read-only from a script in your `/tmp` folder. Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Never run `gov rebuild --no-embeddings`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it); copy single named files only, never `governance/project/`. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. On an authentication or access error, stop and return.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-7rr2.md`: its KPI lines and its `allowed_paths` (`src/gov/close/**`, `tests/unit/close/**`).
- The sources: DEC-750, DEC-754, DEC-704, DEC-498, DEC-734, DEC-736, DEC-372, DEC-490, DEC-505, DEC-581, DEC-739, DEC-137, DEC-413 in `docs/DECISION_REGISTER.md`; W2-01's probe records `docs/probes/DAEO-g0ip/PR-DAEO-g0ip-round-4.md` and `PR-DAEO-g0ip-split.md` (the cases this ticket takes over).
- The ticket's acceptance tests and README `tests/acceptance/W2-53/` (forms R-1 to R-8), the revised W1-30 case in `49e4aca0`, and the code at the head: `git diff f082bc68 c8d3fb30 -- src tests`.

## DEC-757 (owner, 2026-10-17; in force, staged for the owner's commit, not in this worktree's register; item 2 as it concerns this ticket)

1. **The probe gate measures every later merge against git's own merge of its parents** (DEC-754: W2-01's round-4 findings 1 to 3 and P-5 (c)).
2. **An owner-accepted known-red list, as a ratchet.** The path map key **`accepted_reds`**: entries with **`test`** (the exact test id), **`decision`** (the owner's ACCEPTED decision naming that test id), **`reason`** and **`fixed_by`**. An entry counts only when the commit that added it carries `Role: owner`. A listed red does not refuse a close; any red not on the list does. A listed test that passes refuses the close, naming the entry, until the entry leaves the list. The list never grows without an owner decision. Its core is one public function W2-19 reuses (DEC-736).
3. **A ticket-file edit made from the integration side is not the ticket's own change:** a commit carrying `Role: orchestrator` or `Role: owner`, naming the ticket in `Task:` and changing only its ticket file. A change on the ticket's own side after the probe still refuses.
4. **A named load-sensitive quarantine.** The path map key **`load_sensitive`**: entries with `test`, `decision` and `reason`, under the same owner-commit rule. A listed test that fails in the close counts only if it passes in an isolated re-run (alone, in its own process) inside the same close, and the close reports it by name with both results, never silently. A test not on the list is never re-run. An entry may name a test function, covering its parameters.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard or a gate fail open. Run the code; do not judge by reading alone. A finding you could not reproduce is marked as such. In particular:

- A later merge holding the probed commit that deletes or reverts a probed file, removes or changes an acceptance test, takes another ticket's older whole version, or is an octopus, and still passes; on the integration branch and inward on the ticket's branch; naming the ticket, another ticket or no task.
- A reopened ticket (an earlier round merged back before the final probe); a merge git cannot compute (a conflict on a probed path, and on a path outside them) or cannot read.
- A red that passes the close without an `accepted_reds` entry; with an entry added by a commit not carrying `Role: owner` (in the final trailer block or elsewhere in the message; by an evil merge; by a non-owner editing or re-adding an owner's entry); with a decision that is not an ACCEPTED owner entry naming that exact id; through a near or parameter-variant id; through an entry whose test now passes; a red in a collection error, a setup or teardown error, a crashed or timed-out run, or a run whose results cannot be read, while the lists are present. The list growing without an owner decision. How a `Role:` trailer is trusted.
- An integration-side commit that changes the ticket file and anything else, or a ticket-side change after the probe, passing as integration-side; how the merges carrying such an edit in are judged.
- A load-sensitive test passing without its isolated re-run; a re-run of a test not on the list (a prefix or near name of a listed function included); a re-run that is silent, or whose failure does not refuse.
- **List row W2-L345, to re-check:** an inward merge naming another ticket's task that resolves a probed file to the integration side closes on the ticket branch. Say whether the head now refuses it (a hand resolution, and a clean merge that git itself resolves to the integration side).
- Also classify, as residual or blocker, a non-merge commit after the probe that names another ticket and deletes or reverts a probed file.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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

After the twelve fields, as the payload:
1. Each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work, lets an implementer change acceptance tests, or makes the guard or a gate fail open. Say also what you probed and found sound, and W2-L345's state.
2. **The probe record's full content**, ready to be written as `docs/probes/DAEO-7rr2/PR-DAEO-7rr2.md`: a YAML frontmatter block exactly of this form, then the record's body (what was probed, what was found, the judgement and why):

```
---
type: probe
task: DAEO-7rr2
reviewer_session: <your session id, printed by the lead into this line: write REVIEWER_SESSION>
implementer_session: 08b55925-978d-4263-ac48-f061a9cf6693
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: <pass | fail>
probed_commit: c8d3fb308fd3178206a67ec8a842cdc2ae34089b
---
```

The judgement is `pass` only when no finding could lose work, let an implementer change acceptance tests, or make the guard or a gate fail open in a case the ticket's KPI lines or DEC-757 item 2 hold; findings outside them are residuals and do not fail it.
