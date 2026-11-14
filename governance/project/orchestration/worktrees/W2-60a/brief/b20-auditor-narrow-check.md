You are a fresh independent auditor, read-only. Ticket: DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL. Worktree `/home/usain/gov-os-worktrees/W2-60a`, branch `w2/W2-60a`, **head to probe: 97f208456bdb**. This is a **narrow independent check**, not a review round: the ticket's review rounds are spent (DEC-1010; review 3 passed at 0e11b5db743d, record `docs/probes/DAEO-cv58/PR-DAEO-cv58.md`). You judge only the changes listed below against the ticket's KPI lines and the decisions named, and say pass or fail with findings.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a`, `w2/W2-60a`) and `git rev-parse --short=12 HEAD` (expect `97f208456bdb`; if the head moved, probe 97f208456bdb by `git show`/`git diff` and say so). If anything else differs, stop and say so.

## Rules

- Read-only: write nothing in the repository (your scratch is your session's `$TMPDIR` only). No commit, merge, checkout, stash or reset. The lead writes the probe record from your return.
- Reads are open (DEC-820) except secrets, the held-out qualification material's contents and the hidden half of an evaluation set. A guard refusal is an answer: report it; refused twice for the same call: stop that line; never another form.
- You may run `gov launch` from this worktree's `src` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main launch …`) against fixture projects you build in `$TMPDIR` with a stand-in CLI (the acceptance suite's `tests/acceptance/W2-60a/w2_60a_support.py` has one; import it read-only with bytecode off), and read any file. No real session (no network). A pytest run is allowed only for a single file or case you need, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, TMPDIR your `$TMPDIR`, `HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. Time budget about 75 minutes.

## What to check (the only scope)

The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-cv58.md` (its KPI lines S1 to S10 and F1 to F3, its Interface section and its "Delegated" lines). W2-60a's own changes since review 3 (`git log e1a3e2214266..97f208456bdb`), in four items:

1. **S2's version reader** (7c789919b): a skill's (and command copy's) version is its top-level `version`, else `metadata.version` when `metadata` is a mapping; neither is `no version`, and a named one still refuses. Today's generated copies (`.claude/skills/*/SKILL.md`, `metadata: version:`) must not be refused (F3).
2. **P-7 (a), a vendored skill's version from its manifest** (8a21a9c1a; the CTO's decision in the ticket): a copy with no version whose name is a key of `token_sizes` in `template/governance/kernel/skills/superpowers/vendored.yaml` (adopted: `governance/kernel/skills/…`) takes the manifest's `version`, and its record entry gets `version_source` (the manifest's path); the hash stays the loaded copy's; unlisted, no manifest or a malformed manifest stays `no version` and a named one refuses. Probe: can it fail open (a skill recorded with a version it does not have, an unversioned named skill that launches where it should refuse, a manifest read through a link or from outside the root)? Does `read_role` on this tree now pass for engineer?
3. **S10 (the plan line, called S12 in the briefs) and P-6 (a)** (2ef612682, 4ebf55fb4): `gov launch --plan <role> <ticket>` prints one line `model <id>, effort <e>` from the role file's `- **Launch default:**` line and exits 0, starting nothing (no session, no CLI run, no launch record, no temp folder left, no gate taken); a role file without the line or with a malformed one refuses `LAUNCH_REFUSED` naming the file, exit 1. Nothing reads `Launch by criticality` (W2-184's). Without `--plan`, a launch is as before.
4. **The restored DEC-839 lines S3, S4 and S8, and the merge of w2/integrate** (the owner's DEC-1167 (2): S3, S4 and S8 back to their DEC-839 forms; RUBRIC-2's lines moved to W2-184): confirm no RUBRIC-2 code (criticality tiers, trial, promotion, `Launch by criticality`) is read or recorded by the launcher, and that the merge's resolution of `src/gov/launch/launcher.py` (`git diff 5b7941b66^1 5b7941b66 -- src/gov/launch/launcher.py` and `git diff 5b7941b66^2 5b7941b66 -- src/gov/launch/launcher.py`, then the later commits) keeps the reviewed behaviour: the role's model and effort on the line and recorded with `model_source`; a model after `--` not the role's refused naming both; `CLAUDE_CODE_SUBAGENT_MODEL` in the settings' env equal to the model, recorded; no compaction threshold; S7's arguments refused; one record per launch keyed by `--session-id`, written before the start, unwritable folder refused; and the one appended file `<TMPDIR>/role-<role>.md` = role file's bytes, a blank line, the template's bytes, placed last after the caller's arguments (P-4 (A)). Look especially for a refusal that integrate's code path lets through on W2-60a's side (W2-136's lead launch, W2-20's gate, W2-56's environment), i.e. a worker launch that starts without the role text, record or checks.

Not in scope: anything reviewed in rounds 1 to 3 and unchanged since; the integrate-side suites whose fixtures predate W2-60a (being fixed separately); S10's old second-review line (moved to W2-184).

## Return

First, a fenced block exactly in this form:
```
verdict: pass | fail
probed_commit: <40-hex>
reviewer_session: <your session id if you know it, else "unknown">
wrote_nothing: true | false
```
Then the twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line; in `evidence` each item 1-4 with what you ran or read and what you saw; each finding with its severity (blocking or not), file:line, a reproduction, and which KPI or decision it breaks. Guard refusals met (count).
