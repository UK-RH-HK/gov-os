You are a fresh reviewer. Ticket DAEO-siiz (W2-52, "The lite A7 and A10 stage records"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-52` on branch `w2/W2-52`, at the head `643aeeef6ffb6fca20ab41533ecae8ade90b9548`, and its acceptance tests pass. You probe that head, on the ticket's whole change (`git diff 29bef106 643aeeef6ffb6fca20ab41533ecae8ade90b9548`; `29bef106` is the merge of `w2/W2-49` this ticket stands on), for behaviour the tests miss. You write nothing.

## The threat model (DEC-801, DEC-808)

Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round. Only a finding an honest agent can hit in ordinary work, and that fails open or loses work, justifies a round.

Ask of every finding these two questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?" Every finding in your probe record carries these two lines, under it:

- `Ordinary work: yes|no, because …`
- `Consequence: fails open|loses work|other`

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-siiz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-52` and `w2/W2-52`), and `git log --oneline -1` (expect `643aeeef6ffb6fca20ab41533ecae8ade90b9548`). If anything differs, stop and say so.
- You start outside the sandbox (the lead's choice: your probes run the adoption stages, whose A3 needs the code graph's folder `/tmp/gov-cbm-<uid>`, read-only inside the sandbox until W2-56). A tripwire compares every tree before and after your session: change nothing anywhere, this worktree, the main tree and every other worktree included.
- In this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -c "import gov; print(gov.__file__)"` and quote the line in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed at the tool's limit: keep each run short (one test file, or one probe, at a time; the W2-52 suite takes about seven minutes, so run single files of it, not the whole suite at once).
- You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash` in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- The workbench (DEC-723): never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A probe that needs a repository builds a temporary one from scratch in a temporary folder made with `mktemp -d` outside every repository (never under a `.gov-runtime/` folder, DEC-673). The acceptance suite's own support module `tests/acceptance/W2-52/w2_52_support.py` builds such repositories; you may import it from a probe script you keep in your temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write no file of the repository and make no commit. No subagents. Install nothing. No push, merge, rebase or tag. Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree: `gov adopt` runs only in your temporary repositories.
- Your temporary folders: name each in your return.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Refused twice for the same call: stop and say so; no third try (AR-6).

## What you read

- The ticket file `.tickets/DAEO-siiz.md`: its KPI lines and its `allowed_paths`, as the W2-52 card in `docs/plan/WAVE_2_WBS.md` section 2 narrows them (`src/gov/adopt/stages.py`: its A7 and A10 entries only, its one import line used by them counted among them; the adopt skill: its A7 and A10 steps only; `src/gov/adopt/command.py`: the `STAGES` entries `"A7"` and `"A10"` and the docstring's stage list beside them, only; `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md`: byte copies of `template/governance/kernel/skills/adopt/SKILL.md`).
- The sources: Contract v4.2's CAP-44.f, CAP-44.h and CAP-44.k (`docs/contract/capabilities/CAP-44.f.md`, `CAP-44.h.md`, `CAP-44.k.md`, and their rows in the contract file under `docs/contract/`), as W2-49 changed them; this ticket does not change them.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-741, DEC-722, DEC-738, DEC-490. And these owner decisions, staged and not yet in the register, as written here:
  - DEC-795: a missing A7 or A10 record is a condition `not met`, through the skill, as built; a machine reader goes to W2-28.
  - DEC-796: a gate is never run again over its own failing record; that record is removed by a commit of its own first. Revisited at W2-27.
  - DEC-803: a risk that exists only when a feature is switched on (the git hooks, before W2-08, for example) is named as an entry criterion of the ticket that switches that feature on, not a finding of this ticket.
- The ticket's acceptance tests (`tests/acceptance/W2-52/`, with its README) and the code at the head: `src/gov/adopt/lite_gates.py`, the changes to `src/gov/adopt/stages.py` and `src/gov/adopt/command.py`, the adopt skill, and `tests/unit/adopt/test_lite_gates.py`.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open.

In this ticket, in particular: a lite gate that passes when what Contract v4.2 says it checks is absent or failing; a missing, unreadable or partial stage record read as healthy; an adoption verdict that could be ADOPTED_HEALTHY with a failing or missing A7 or A10 record; a stage record written outside the adoption run's folder or over another stage's record; a lite record that does not name what stays for Wave 3; any change outside this ticket's allowed paths, `src/gov/adopt/stages.py` beyond its A7 and A10 entries, `src/gov/adopt/command.py` beyond its two entries and docstring list, and the adopt skill beyond its A7 and A10 steps included.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work or fails open, with the two lines `Ordinary work: …` and `Consequence: …` under it. Say also what you probed and found sound. You repair nothing (MR-4).

After the twelve fields, give the probe record's body as a payload: a short Markdown text with "What was probed", "What it found" (each finding with its two lines) and "Judgement" (`pass` if no finding is one an honest agent can hit in ordinary work that fails open or loses work; otherwise `fail`), and your own session id (from `printenv CLAUDE_SESSION_ID` if set, otherwise say you do not know it).

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Refused twice for the same call: stop and say so.
