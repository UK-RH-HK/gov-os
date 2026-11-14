You are a fresh engineer. Ticket: DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL, class C3. Worktree `/home/usain/gov-os-worktrees/W2-60a`, branch `w2/W2-60a`. Two batches, in this order. The acceptance tests are the independent test designer's; you never change them.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a`, `w2/W2-60a`). If anything differs, stop and say so.

## Standing rules

- Foreground only; your session ends with your last message.
- Your paths (the ticket's): `src/gov/launch/launcher.py`, `src/gov/launch/role.py`, `src/gov/launch/record.py`, `tests/unit/launch/test_role*`, `tests/unit/launch/test_launch_record*`, `docs/changes/W2-60a-CIT-E.md`. Touch `launcher.py` at its argument checks and call sites only; put new logic in `role.py`. W2-05 holds the git-environment lines of `src/gov/**/*.py`: leave them alone. Never edit `tests/acceptance/**`.
- If the guard refuses a write, that refusal is the answer: stop and report it (refused twice for the same call: stop; never another form).
- Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with your session's own `$TMPDIR` as TMPDIR, `HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`. A resource gate's refusal is a wait, not a refusal.
- Write with the Write and Edit tools and absolute paths. No `git merge`, `checkout`, `reset`, `stash`, `clean`, rebase or push. Commit after each batch, your files only: `git commit -m "<subject>" --trailer "Task: DAEO-cv58" --trailer "Role: engineer" --trailer "Implements: DEC-826, DEC-839, DEC-832" -- <your paths>`. Commit hashes in 12 digits. Time budget about 60 minutes.

## Batch 1: S2's defect, a skill's version under `metadata:`

KPI S2: the launch record lists each loadable skill with its name, version and sha256 taken from the copy the session loads; a named skill that is missing (or carries no version) refuses the launch. F3: a refusal the launcher makes today must still refuse, and today's real copies must not be refused.

The kernel's generated skill copies now carry their version only as `metadata:\n  version: 1.4.0` in the front matter (see `/home/usain/gov-os-worktrees/W2-60a/.claude/skills/test-design/SKILL.md`). `role.py` reads only the top-level `version` (`_skills`, about line 118; the named-skill check at about line 212), so every launch of a role naming such a skill is refused "carries no version". Fix: a skill's version is its top-level `version`, else `metadata.version` when `metadata` is a mapping; neither is `no version` (and a named one still refuses). Apply the same rule wherever a skill or command copy's version is read (about line 153), if the record's form for it is the same. Add unit cases in `tests/unit/launch/test_role*` (top-level only; metadata only; both, the top-level wins; `metadata` not a mapping; neither). The test designer's acceptance case for this is in `tests/acceptance/W2-60a/test_w2_60a_skills.py`; run that file and `tests/unit/launch/`.

## Batch 2: S12, `gov launch --plan`

KPI (the ticket's line "Routed from W2-33 (its S2, DEC-1156 (3))"): the launcher's plan for a planted ticket prints the model and effort of the role file's `- **Launch default:**` line; a role file without the line fails the plan, naming the file.

Interface (the ticket, narrowed by the owner's DEC-1167 (2)): `gov launch --plan <role> <ticket>` prints exactly one line, `model <id>, effort <e>`, read from the role file's `- **Launch default:**` line (reuse `read_role`'s reading of that line; the same role-file location, the same refusals), and exits 0. It starts nothing: no session, no CLI run, no launch record, no temp folder left behind, no gate taken. A role file without the line, or with a malformed one, refuses with `LAUNCH_REFUSED` naming the role file's path, exit 2, as a launch does. Read **no** `Launch by criticality` line (that is W2-184's). About 40 lines. Every refusal the launcher makes today keeps refusing. Add a line for `--plan` to `docs/changes/W2-60a-CIT-E.md` where it lists the launcher's behaviour.

The acceptance file for it, `tests/acceptance/W2-60a/test_w2_60a_plan.py`, is being written in parallel; the lead merges it into your branch between your batches or after. If it is in the tree when you reach batch 2, run it; if not, test with unit cases of your own in `tests/unit/launch/test_role*` and say so.

## Reds that are not yours

Before your work, 11 cases in `tests/acceptance/W2-60a` are red for reasons a test designer is revising, not the code: 10 argv-tail checks (`test_w2_60a_launch_record.py:264` x3, `test_w2_60a_model_and_effort.py:51` x2 and `:64` x2, `test_w2_60a_refused_arguments.py:87`, `:117`, `:124`) that predate the appended file being placed last, and `test_w2_60a_refused_arguments.py:189` `[orchestrator]` (integrate's lead launch now refuses it with "no lead for ticket"). Leave them and their behaviour as they are: the appended file stays last; the orchestrator refusal stays integrate's. Name them in your return only if their failure changes.

## Verify, then return

Run `tests/unit/launch` and `tests/acceptance/W2-60a` (each its own run, the form above). Return the twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line: the sandbox check, the counts per folder, every red named (file:line, assertion, and whether it is yours), the guard refusals met (count), and your commits' hashes and trailers.
