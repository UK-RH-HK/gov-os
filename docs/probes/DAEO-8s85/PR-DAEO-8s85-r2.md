---
type: probe
task: DAEO-8s85
reviewer_session: ccc6955a-cbdc-41ee-9ab1-6919011d6c9d
implementer_session: 99c8b156-1fb8-4ee1-a595-abcf36d2cf5d (fe721a7ec); 65fa91e4-b126-4f32-a790-529b92eb10b7 (ef8041c5c)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ef8041c5c8ace6cc1a9207692ba72ec7c961a8e1
---

# Probe of DAEO-8s85 (W2-153), reopened line S-ADOPTED (DEC-1192 (2)): narrow independent check (DEC-1154), judgement pass

The check covers only the change made for the reopened line S-ADOPTED: in an adopted repository `gov adapters
generate` writes `.claude/templates/<stem>.md` from the kit's templates, and `gov doctor` names a missing or differing
copy. S1 to S6, F1 and F2 were reviewed and landed earlier. This is a narrow record, not a full re-review.

- **Head probed:** `ef8041c5c8ac` on `w2/W2-153`. The diff since the reopen (`02bb50535`) is the engineers' two
  commits. `fe721a7ec` (session `99c8b156-1fb8-4ee1-a595-abcf36d2cf5d`) changed `src/gov/adapters/merge.py`,
  `command.py`, `portability.py` and `src/gov/doctor/command.py`, and added `tests/unit/adapters/test_w2_153_adopted.py`
  and `tests/unit/doctor/test_w2_153_templates.py`. `ef8041c5c` (session `65fa91e4-b126-4f32-a790-529b92eb10b7`) made
  doctor's `templates` part report with status `report` instead of `drift`.
- **Why the second commit:** the lead's first verification at `fe721a7ec` was red on three W1-39 cases. A project
  freshly made by `copier copy` has no copies until generate runs, and `gov doctor` must stay healthy there.
- **Reviewer:** a fresh independent-auditor, session `ccc6955a-cbdc-41ee-9ab1-6919011d6c9d`, model claude-opus-5-5,
  effort high, class C2, `--owner-named DEC-1154`. It was launched read-only (`--allowedTools Bash Read Grep Glob`)
  with its scratch in the sandbox's own `$TMPDIR` under `/tmp/`, and carried JUDGEMENT.md word for word.
  `git status --short` was empty when it ended, and the tripwire shows no change in the W2-153 tree.
- **The lead's verification at `ef8041c5c`:**
  - `lead_verify`: 7223 tests, 1 failed, 24 skipped; serial 1 passed.
  - The one red, `tests/unit/orchestration/test_w2_149_indep_launch.py::test_f1_a_timed_out_session_without_traces_is_checked_0`
    (`assert (14 == 21)`, a timed-out stub session), passed when re-run alone: 1 passed in 2.48 s. It is outside
    this diff, and it was green in the first full run at `fe721a7ec`.
  - The three W1-39 cases, `tests/unit/doctor` and `tests/unit/adapters`: 184 passed. At `fe721a7ec`,
    `tests/unit/adapters`, `tests/unit/doctor` and `tests/unit/launch`: 843 passed.
- **The lead's triage (DEC-1010 item 1):** no finding is in scope, ordinary work and fails open or loses work, so READY
  holds.
  - N1 (a symlinked copy is written through) needs a deliberate construction. It goes to the CTO as a Wave 3
    hardening row.
  - N2 (a hand-edited copy is replaced) is the line's own required behaviour. It is recorded.
  - N3 (generate needs all eight `TEMPLATE_COPIES`, stricter than the seven mapped stems) fails closed, and every
    shipped kit holds all eight. It is recorded.
  - N4 (an `unmeasured` part can lower the adoption level where a kernel has no `templates/`) applies to no shipped
    layout. It is recorded.

## The reviewer's return (verbatim)

pass — 4 findings, all recorded rows and none blocking (DEC-809): N1 needs a deliberate construction (ordinary work no); N2 is behaviour the KPI line itself requires (scope out); N3 and N4 are ordinary work no, consequence other.

**Step 0, sandbox check (launch_worker.sh / EMG-d4b-launched.md):**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-153` failed with `OSError: [Errno 30] Read-only file system`, as it should.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (exit 0, `1ae28402a1…`). `git update-index --refresh` worked (exit 0).
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1).
- **Head:** `git rev-parse HEAD` = `ef8041c5c8ace6cc1a9207692ba72ec7c961a8e1`.

**What I probed and found sound** (on a real adopted repository, made with `copier copy --trust --defaults --skip-tasks --vcs-ref=HEAD` from this worktree into `$TMPDIR`, then `git init`; the real `rulesync` and `python3 -m gov.cli.main adapters generate`, PYTHONPATH set to the worktree's `src`):

- **(1) Generate writes the copies.**
  - Before running generate I planted three programme files: a differing `.claude/templates/role-engineer.md`, the programme's own `.claude/templates/my-own.md`, and a `CLAUDE.md` with its own line.
  - Generate exited 0. Its output had `templates: {written: [the other 7], replaced: [.claude/templates/role-engineer.md]}`, so the differing copy was replaced and named.
  - All eight copies are byte-equal to `governance/kernel/templates/`.
  - `launcher.template_args(root, role)` passes for all seven roles in `ROLE_TEMPLATES`.
  - `my-own.md` was left untouched, and `CLAUDE.md` kept its own line (it was merged).
  - The unit test (the command from the brief) gave 7 passed, 0 failed. Its other cases also hold: a second run writes nothing; a kit that lacks a template is refused before anything is written (`merge.generate` works out the template step before its write loop).
- **(2) Gov OS's own repository is unchanged.**
  - `merge._is_source_tree(<this worktree>)` is True and `merge._template_copies(<this worktree>)` is None. So generate writes no `.claude/templates/` file there and returns exactly `{merged, written, kept}`: the `templates` key is added only when there is a template step.
  - `_is_source_tree(<adopted repo>)` is False.
- **(3) Doctor's new part.**
  - On a fresh copier project (no copies) the part is `status: report` and names all eight as missing. On the repo after generate it is `pass`. After a hand edit to `role-lead.md` it is `report`, with `differing: [.claude/templates/role-lead.md]` and a reason that names `gov adapters generate`. On Gov OS's own worktree it is `pass`.
  - `report` is not in doctor's `("fail", "drift")` test, so the part never makes doctor unhealthy. My planted repos were unhealthy only because `framework_lock` failed: I skipped copier's `gov release --lock-from` task, so there was no lock. That has nothing to do with this change.
  - The adoption level was MINIMAL both with the new part and with the part stubbed to pass.
  - I stubbed only `canaries` and `index_freshness` (to `unmeasured`), so no embedder ran.
- **(4) No write outside `.claude/templates/`.** The step writes only `.claude/templates/<one of the eight>.md`, and only when the copy is missing or differs. It refuses a copy path that exists but is not a file. The template copies are not gitignored in a kit project (`check-ignore` exit 1), so a committed copy that gets replaced can be recovered from git.

**Findings**

- **N1: a copy that is a symlink is written through.** `_template_copies` refuses a path that exists but is not a file. A symlink to a file passes `is_file()`, though, so `write_bytes` writes the kit's bytes into the link's target, which can be outside `.claude/templates/`. The same goes for a `.claude/templates` folder that is itself a link. I found this by reading `merge.py` (the `os.path.lexists(...) and not is_file()` check, then `write_bytes`). KPI line: S-ADOPTED.
  - Ordinary work: no, because it needs a link planted at a generated copy's name, a deliberate construction under DEC-801 (and if the link points at the kit file itself, the bytes are equal and nothing is written).
  - Consequence: loses work.
  - Scope: out. A Wave 3 hardening row.
- **N2: a hand-edited copy is replaced without a backup.** In an adopted repo, generate overwrites a differing `.claude/templates/<role>.md` and names it under `templates.replaced`. I saw this in the planted run (`role-engineer.md`). KPI line: S-ADOPTED.
  - Ordinary work: yes, because a programme might hand-edit a generated copy; but the line itself requires it ("a copy that differs is replaced only by generate and named in its output"), the copies are generated files (DEC-315), doctor names the difference first, and a committed copy can be recovered from git.
  - Consequence: loses work (an uncommitted hand edit to a generated copy).
  - Scope: out. It is the owner-specified behaviour, not a defect against the line; changing it would be an owner decision. A recorded row.
- **N3: generate is stricter than the line.** It requires all eight `TEMPLATE_COPIES`; the line asks only for "every template gov launch maps" (seven stems, without `brief` and `role-cto`). When any one of the eight is missing from the kit, the whole command is refused with `ADAPTERS_TEMPLATE_MISSING`, including the CLAUDE.md, AGENTS.md and settings merges. I found this by reading `_template_copies` and the unit test `test_a_kit_missing_one_template_refuses_and_nothing_is_written`. Every shipped kit holds all eight: I checked `git ls-tree v0.1.0` and HEAD. KPI line: S-ADOPTED.
  - Ordinary work: no, because no shipped kit lacks one; it would take a programme deleting a kernel template by hand.
  - Consequence: other (it fails closed with nothing written; it neither fails open nor loses work).
  - Scope: in. A recorded row.
- **N4: the new part can be `unmeasured` and lower the adoption level.** `_check_adoption_level` lowers ADOPTED_HEALTHY to INTERMEDIATE when any part is `unmeasured`. The new part is `unmeasured` only where the kernel has no `templates/` folder. That never happens for a copier kit (v0.1.0 and HEAD both ship it) or for Gov OS's own repo (it uses `template/governance/kernel/templates/`). The one exception would be a repo with no kernel folder at all, and such a repo's other parts are unmeasured anyway. I checked by reading `doctor/command.py`, and on the fresh copier project the level was MINIMAL with and without the part. KPI line: S-ADOPTED.
  - Ordinary work: no, because no shipped layout has a kernel without `templates/`.
  - Consequence: other (a reported level, not health; it neither fails open nor loses work).
  - Scope: in. A recorded row.

**What would reverse these:**
- N1: a supported flow that makes `.claude/templates/*` symlinks to files outside the kit.
- N2: an owner decision that hand edits to `.claude/templates/` are the programme's own work.
- N3: a shipped kit that lacks one of the eight.
- N4: a shipped or adopted layout whose kernel has no `templates/` folder and that is otherwise ADOPTED_HEALTHY.

**Guard refusals: 2, neither repeated.**
1. In one Bash line I ran `cd "$TMPDIR/adopted" && … mkdir -p .claude/templates`. The guard resolved the relative `mkdir` against the worktree and refused it. The real target was in `$TMPDIR`; I named it by absolute path in `$TMPDIR` and nothing touched the worktree.
2. `git -C "$A" archive HEAD`, with the revision given through a variable, was refused as an unresolvable revision. I did not repeat it; I made the second fresh repo with a second `copier copy` instead.

```verdict
{"kpis": [{"kpi": "S-ADOPTED", "verdict": "pass", "findings": [{"id": "N1", "scope": "out", "ordinary_work": "no", "consequence": "loses work"}, {"id": "N2", "scope": "out", "ordinary_work": "yes", "consequence": "loses work"}, {"id": "N3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "N4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```

task: W2-153 (DAEO-8s85): independent check of S-ADOPTED (DEC-1154, DEC-1192 (2)); decisions: DEC-1192, DEC-315, DEC-801, DEC-808, DEC-1010
status: done, pass
work_completed: sandbox check; read the diff `02bb50535..ef8041c5c`, `launcher.ROLE_TEMPLATES`, `template_args`, `portability._template_findings`, `_kernel` and `fabric.MARKERS`, and doctor's `run` and `_check_adoption_level`; ran the new adapters unit test; ran the real `gov adapters generate` (real rulesync) on a copier-made adopted repo with programme files planted; ran doctor's `run` on a fresh and on a generated adopted repo, and doctor's part on Gov OS's own worktree; checked the source-tree rule against this worktree without writing to it
files_changed: none
evidence: the copier-made repo in `$TMPDIR` (removed afterwards); generate's output had `templates.written` = 7 and `templates.replaced` = [role-engineer.md]; all eight copies byte-equal to the kit; `template_args` passes for all 7 roles; `my-own.md` and CLAUDE.md's own line kept; on this worktree `_is_source_tree` is True and `_template_copies` is None; doctor's part is `report` (8 missing) on the fresh repo and `pass` after generate, `report`/differing after a hand edit, and `pass` on Gov OS's own worktree; adoption level MINIMAL with and without the part; the v0.1.0 kit holds all eight templates
tests: tests/unit/adapters/test_w2_153_adopted.py: 7 passed, 0 failed (run through heavy_slot.sh with `-m "not local_only" -k "not real and not green_here and not time_limit"`; that filter left out none of the 7 tests); I did not run the full verification (it is the lead's)
discoveries: in my planted repos doctor was unhealthy only through `framework_lock`, because `--skip-tasks` skipped `gov release --lock-from`; that is not related to this change
risks: N1 (writing through a symlink, a Wave 3 row); N2 (replacing a hand-edited copy is the line's own behaviour)
lessons: the guard resolves a relative write in a `cd …&&` line against the worktree; use absolute `$TMPDIR` paths for scratch work
proposed_decisions: none
unresolved: none
recommended_next_action: land S-ADOPTED once the lead's full verification is green; file N1 as a Wave 3 hardening row; N2 to N4 recorded as rows only
git status --short: (empty)
