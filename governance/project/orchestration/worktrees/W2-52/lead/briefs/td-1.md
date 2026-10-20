# Brief: independent test designer

You are a fresh independent test designer (MR-3). Ticket: DAEO-siiz (W2-52, "The lite A7 and A10 stage records"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-52` on branch `w2/W2-52`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-siiz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-52` and `w2/W2-52`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. No push, merge or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only, clone into a temporary folder, and are marked `local_only`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch (as `tests/acceptance/W1-41/` does) or from the dev tiers. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
  Your README states how a run exercises this worktree's code, and gives the run line with that `PYTHONPATH`. Where a test starts `gov` in a subprocess, the subprocess must import this worktree's `src/` too (look at how `tests/acceptance/W1-41/w1_41_support.py` and `tests/acceptance/W1-07/` start `gov`, and make sure the import resolves here).
- Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree; `gov adopt` runs only inside the temporary repositories your tests build. Never run `gov rebuild --no-embeddings`, anywhere.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"): stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-siiz.md` (read-only): its KPI lines, its `allowed_paths` and its sources. Its card: `docs/plan/WAVE_2_WBS.md` §2, "W2-52", and §0 (rules for every ticket).
- The sources:
  - Contract v4.2 in `docs/contract/contract.yaml`: CAP-44 (its acceptance and wave note), **CAP-44.f** (the lite A7 and A10 gates: what each checks), **CAP-44.h** (the lite verdict and its conditions, among them "the lite A7 and A10 gates passed"; condition (4) whose lite part is the lite A7 gate, condition (6) whose lite part is the lite A10 gate, condition (9) whose lite part is the derived state rebuilt from git that the lite A10 gate checks), CAP-44.k (what of A7 and A10 stays for Wave 3), and the items they cite: CAP-44.b, CAP-44.c, CAP-44.d, CAP-44.e, CAP-20, CAP-55.
  - `docs/changes/W2-49-CIT-P.md` §3.2 ("The A7 and A10 gates of CAP-44.f, lite": what each lite gate checks and what of each stays for Wave 3) and the row on W2-24 in its impact table: W2-24's fixture adoption runs A0 to A6 and A8 with no A7 or A10 gate, and that is unchanged.
  - The adoption verdict's type, W2-02's (held, not merged into this branch): read it only, with `git show w2/W2-02:template/governance/kernel/schemas/adoption-verdict.schema.json`. It gives a verdict record a list of named conditions, each with `name`, `source` and `state` (`met`, `not met` or `accepted`). You write nothing of W2-02's.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-741 (Contract v4.2; answers F, G, H, I), DEC-722, DEC-090, DEC-006, DEC-738 item 1, DEC-221, DEC-462, DEC-476, DEC-491, DEC-723, DEC-732.
- The public interfaces the ticket must work with: `gov adopt --lite --stage <stage>` and its JSON envelope (`--json`), the evidence records it commits under `governance/adoption/` of the adopted project, the A5 precedent for an Independent Auditor's committed record accepted by a stage (`--verdict <path>`, the `Role: independent-auditor` trailer, a named auditor session different from the sessions that ran the stages), `gov rebuild`, and the adopt skill `template/governance/kernel/skills/adopt/SKILL.md`. Learn their behaviour from `tests/acceptance/W1-41/` (its README and support) and the command's help; you read no private part of an implementation to learn what a test should expect.

## The behaviour to test (the KPI lines and their sources)

- **Success 1.** `gov adopt` runs the lite A7 and A10 gates as Contract v4.2's CAP-44.f (lite) states. Each gate is recorded as its own stage: it writes a stage record with its evidence, in the adoption run's own folder, next to the other stages' records and never over another stage's record. The adopt skill names both steps (A7 and A10). [DEC-741, CAP-44.f]
- **Success 2.** Each lite gate checks what v4.2 says it checks:
  - A7: the A6 migration, against the A3 path map and the A4 plan reviewed at A5, by a fresh Independent Auditor session.
  - A10: the A8 legacy memory extraction and retirement, the derived state rebuilt from git, and the canary of each index (CAP-55), by a fresh Independent Auditor session.
  - Each record names what stays for Wave 3 (CAP-44.k; CIT-P §3.2's "What of A7 stays", "What of A10 stays"). [DEC-741]
- **Success 3.** The adoption verdict (W2-02's type) reads both records as named conditions: the A7 record and the A10 record each give a condition a verdict can carry in W2-02's form (a name, its source item, its state). [DEC-741, CAP-44.h]
- **Failure.** A lite gate that fails writes a failing record, and the verdict cannot be ADOPTED_HEALTHY; a missing record is a named failure, never healthy. (Also in the spirit of the ticket: an unreadable or partial record is never read as healthy, and a gate never passes when what v4.2 says it checks is absent or failing.)
- **What stays unchanged.** Stages A0 to A6 and A8 keep their behaviour; in particular A8 still runs after A6 without an A7 record (the W2-24 row above). Do not rewrite an earlier ticket's tests; if you find the KPIs require it, name the test and return a package.

Where a KPI line leaves the interface open (for example: what an A7 or A10 call takes from the auditor, which stage each stands on, how the verdict's named conditions are exposed through a public interface), choose the reading closest to the sources and to the A5 precedent, and state it in your README as your reading. If you cannot choose without guessing, return a package (question, why now, options, impact, reversibility, cost, recommendation, confidence) and still write and commit the tests for every line that is not in doubt.

The lead knows that, in the tree as it stands, `gov adopt --lite --stage` accepts only A0 to A6 and A8: say in the README that this is one red reason, and that the stage choices are where the run first stops.

## What you write

- Only inside `tests/acceptance/W2-52/`. No throwaway implementation is left in the tree.
- FULL: thorough; every KPI line's success and failure; no combinatorial expansion beyond what a KPI demands. Every covers id (CAP-44.f, CAP-44.h) gets at least one test.
- Behaviour through public interfaces, never internals. Deterministic, no network, no model. Each case builds its own temporary repository (W1-41's support shows how); keep the suite's run time within a few minutes.
- A README that maps each KPI line to its tests and gives the expected red reason of each, the run line (with the `PYTHONPATH` above, `-p no:cacheprovider -rs`), and how a run is shown to exercise this worktree's code.
- Red first: run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/acceptance/W2-52 -q -p no:cacheprovider -rs` to the end (never with `-x`); the tests fail for the reason the README states.
- An ambiguous KPI line or a dispute is never a guess: return it as a package.

## Commit

The git hooks are uninstalled; never use `--no-verify` or `core.hooksPath`. Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-52 (DAEO-siiz): acceptance tests for the lite A7 and A10 stage records" --trailer "Task: DAEO-siiz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-741" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in it: your commit's hash; the test count; the KPI lines and covers ids with their tests; the red reason as you saw it (counts); the `gov.__file__` line; every reading you chose where the KPIs left the interface open; every earlier test you would rewrite, with its reason; any package. Refused twice for the same call: stop and say so.

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
