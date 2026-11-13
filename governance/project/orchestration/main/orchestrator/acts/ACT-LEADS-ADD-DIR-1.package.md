# ACT-LEADS-ADD-DIR-1: ticket leads get their own tests worktree and the runs root by `--add-dir` on their launch line (DEC-1161 (2))

- **For:** the owner (one yes line in the 09:00 digest), then **the CTO** applies it (class (b), `launch_now.sh` is a `watchers`
  control path) after one independent review; then the owner's operator does the two handover steps that follow it (section 5).
- **By:** an ACT-preparation helper of the CTO, 2026-11-13 from about 01:38 UTC. **Nothing live was changed or started:** no commit,
  no stage, no crontab write, no write to the dispatcher's code or state, nothing in the main tree's tracked files, nothing in
  `~/gov-os-worktrees` or `~/gov-os-runs`. Built and rehearsed on a clone of `w2/integrate` and temporary beds under the helper's own
  TMPDIR (section 4). **Not yet independently reviewed** (section 9).
- **Under:** **DEC-1161 (2)** (the owner, 2026-11-13 ~01:45: "an ACT giving ticket leads `--add-dir` for their own `-tests` worktree and
  the runs from `launch_now.sh` (class (b)); then a fresh CTO session ... ; then the owner's operator removes
  `permissions.additionalDirectories` from the main checkout's `.claude/settings.local.json`. Workers stay walled (DEC-313)"); **DEC-313**
  (a worker gets no added directory); **DEC-1157** (no rule holds a lead except the machine's and the governance's protections). The
  manifest's `dec`: "DEC-1161 (2), DEC-313, DEC-1157".
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/leads-add-dir/` (`launch_now.sh` the after, `check_bed.sh`, `checks.json`,
  `rehearse.sh`, `build_manifest.py`, `companion/`). **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-LEADS-ADD-DIR-1/`.

## 0. The short version, the yes line, and who applies it

1. **The change (one file, 12 lines added, nothing removed):** `governance/project/orchestration/tools/dispatch/launch_now.sh`, the
   dispatcher's lead launcher, passes `--add-dir /home/usain/gov-os-worktrees/<W2>-tests --add-dir /home/usain/gov-os-runs` on the lead's
   own `claude` line, before the template flag. When nothing is at `<W2>-tests` it first makes that folder, **empty** (the CLI silently
   drops an `--add-dir` whose folder is missing, and a lead makes its tests worktree only after it starts; `git worktree add` takes an
   empty folder, rehearsed). The folder is made only after the gate check and the registration, so a refused start makes nothing. Nothing
   is made in the runs root. Everything else on the line is byte for byte the same.
2. **Workers are untouched and stay walled:** this file starts only leads (`GOV_ROLE` orchestrator). Workers start through
   `launch_worker.sh` -> `gov launch`, which refuses any `--add-dir` (section 1), and `gov launch` passes no `CLAUDE*` variable of the
   parent to a worker, so nothing the lead was given reaches a worker.
3. **It needs a companion test change first** (two existing W2-153 tests compare the lead line with integrate's, and go red on any added
   argument): `companion-tests.diff`, two files, tolerant of the new line, green on the old launcher and the new one (section 3). Check 3 of
   the manifest refuses the ACT until the companion has landed. **The route of the companion is the CTO's** (section 3: one file is under
   `tests/acceptance/`).
4. **Order at the handover (DEC-1161 (2)):** this ACT first; then the fresh CTO session with its own `--add-dir`; then the removal of
   `additionalDirectories` (section 5).

**The owner's line: `yes ACT-LEADS-ADD-DIR-1 1781a708`** (the first 8 digits of the manifest's sha256, section 8).

**Rebuilt after review round 1 (`review-round-1.md`, manifest `b6923ccc` refused):** F1 fixed (check 1 matches the home part of the `TESTS`/`RUNS` lines by the pattern `/home/[A-Za-z0-9_.-]+/`, no check names `/home/usain` or the live repository; check 5 dropped); F2 fixed (`rehearse.sh` ends with `failures: N`; the new log ends `failures: 0`). The operator's `check_act`, `validate_manifest` and `path_rule` pass on the rebuilt bundle; `act_class.py` gives b. The launcher's after file, `apply.sh` and the companion/follow-up diffs are unchanged. F3 and F4 stay rows for the owner. Needs a round-2 verdict block.

**Who applies it:** class (b): **the CTO**, by hand, after one independent review (verdict block in `review.md`) and the owner's yes, once
the companion has landed:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-LEADS-ADD-DIR-1
bash $G/apply.sh check     # exit 0: "state before (sha256 023623ac6ac8)"
grep -q '_without_add_dirs(ours\["argv"\])' tests/acceptance/W2-153/test_w2_153_dispatch.py && grep -q 'not line.startswith("  --add-dir ")' tests/unit/launch/test_w2_153_template.py && echo companion-in   # must print companion-in
bash $G/apply.sh apply     # exit 0: "state applied (sha256 54345463a67b)"
bash $G/apply.sh verify    # exit 0
git add governance/project/orchestration/tools/dispatch/launch_now.sh
# trailers as ACT-LOAD-BALANCER-A's commit 229037cad (Task: DAEO-sdxk, Implements: ...); its Role there was owner, here the applier's
git commit -m "ACT-LEADS-ADD-DIR-1: the dispatcher's lead line passes --add-dir for the lead's own tests worktree and the runs root (DEC-1161 (2))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1161" --trailer "Role: orchestrator" -- governance/project/orchestration/tools/dispatch/launch_now.sh
```
The next lead the dispatcher starts reads the new file (the apply replaces it by `mv`; a launch already reading it keeps the old one).

## 1. What was found (the questions, with file and line)

**1. How a lead is launched, and whether anything refuses `--add-dir` for a lead.**
- The dispatcher starts a lead with `setsid -f bash .../dispatch/launch_now.sh` (`governance/project/orchestration/tools/dispatch/dispatcher.py:2509-2510`).
- `launch_now.sh` **does not call `gov launch`**: it runs the disk gate (`:12`), the template check (`:15-19`), `gov resources --check`
  (`:23`) and `gov resources --register` (`:29`), then **execs `claude` directly** (`:34-38`, the line this ACT changes). So no launcher
  check of `gov launch` applies to a dispatcher lead, on integrate or on W2-60a.
- `gov launch` on `w2/integrate` (`src/gov/launch/launcher.py`): `_check_cli_args` refuses **any** `--add-dir` (`:317-318`), and it is
  called for **leads too**, not only workers (lead branch `:438-452`, the call at `:440`; workers at `:456`). `_check_repository_settings`
  (`:276-306`, the `additionalDirectories` refusal at `:300-302`) is also called for leads (`:441`) but judges only the tree's own two files.
- W2-60a's launcher (the worktree file, read only; its merge in progress, not touched): `_check_cli_args` still refuses `--add-dir` for
  leads and workers alike (`~/gov-os-worktrees/W2-60a/src/gov/launch/launcher.py:375-376`, called for a lead at `:614`, for a worker at
  `:630`). The difference the lead's note names is in `_check_repository_settings(root, worker)` (`:303-345`): only a worker
  (`worker=True`) also judges the **main checkout's** `.claude/settings.local.json` for a linked worktree (`:316-319`) and the role
  settings (`:340-341`); a lead passes `worker=False` (`:615`) and is judged as before W2-60a.
- **So nothing blocks this ACT:** the dispatcher's path never meets the refusal. **But** a lead started through `gov launch orchestrator`
  (not the dispatcher's path) could not be given `--add-dir`: both launchers refuse it. That would need a product ticket or a widening
  (the owner's); no product code is changed here. No current lead uses that path (the four running leads, below, are dispatcher leads).
- W2-60a's worker check on the real `settings.local.json`, simulated read-only (a temporary root with W2-60a's `settings.json` and a copy
  of the main checkout's local file): **with** `additionalDirectories`: refused ("carries permissions.additionalDirectories: a worker session
  gets no added directory (DEC-313)"); **without** it: passes. The file's other keys (`env`: GOV_DEV_TIERS, GOV_ROLE, GOV_TICKET; `hooks`:
  PermissionRequest, Stop) set no compaction threshold and no agent key, so removing that one key is enough for W2-60a's workers.

**2. Which directories a lead needs (the narrowest set that works).**
- **Its own tests worktree, always `/home/usain/gov-os-worktrees/<W2>-tests`:** `governance/project/facts.yaml:11` (`tests_tree`),
  `.claude/templates/role-lead.md:14`; the lead makes it with `git -C {TREE} worktree add {TESTS_TREE} -b w2/{W2}-tests HEAD`
  (`facts.yaml:80`; `governance/project/briefs/LEAD-w2-common.md:148`) **after it starts**, and removes it before it returns (`facts.yaml:86`).
- **The runs:** a lead has no own folder under `~/gov-os-runs` (`src/gov/launch/launcher.py:449`, DEC-743 7; `src/gov/guard/runs.py:19`);
  a session writes only under `~/gov-os-runs/<its own ticket>/` (`governance/project/prompts/w2-orchestrator.md:74`); an own folder is made
  and **marked** by `gov launch` alone and a folder without the marker is not opened (`launcher.py:475-481`, DEC-751). So the launcher must
  not make `~/gov-os-runs/<W2>` (a worker would then get no own folder), and that folder often does not exist when the lead starts. **The
  runs root is passed**, as today; what a lead may write there stays the guard's.
- **Nothing else:** the lead's temp folder is `/tmp/gov-os-lead-{W2}` (`LEAD-w2-common.md:47`); the integration store
  `~/gov-os-worktrees/W2-00-store` (`facts.yaml:12`) is read only by retrieval; the main checkout and other worktrees are read only.
- **What the leads' own sessions show** (138 lead session transcripts of the last 4 days, tool calls only, nothing printed): file-tool calls
  into the own `-tests` tree: Read 9, Grep 4, **no Edit or Write**; into `~/gov-os-runs`: none; Bash commands naming the own `-tests` tree:
  766, naming `gov-os-runs`: 17. Reads outside every working directory succeed (235 Reads of the main checkout, all ok); writes outside them
  are refused ("Claude requested permissions to write to ..."). So the added directories matter for the lead's Edit/Write and its Bash
  path checks in the tests worktree, not for its reads.
- **The CLI's own behaviour** (Claude Code 2.1.323, the pinned `~/.local/bin/claude`, read from its bundle): an `--add-dir` (or an
  `additionalDirectories` entry) whose folder does not exist is **dropped without a warning** (`pathNotFound` is skipped in the
  permission-context build). Hence the empty `<W2>-tests` folder made before the start.

**The leads running now** (read from `/proc`, about 01:59 UTC): W2-33, W2-88, W2-98, W2-37: all without `--add-dir`, all relying on the local
settings today (section 6, risk 1).

## 2. The change (after minus before)

```
+# DEC-1161 (2) (ACT-LEADS-ADD-DIR-1): the lead gets its own tests worktree and the runs root by --add-dir on its own
+# line, not from the main checkout's .claude/settings.local.json (whose additionalDirectories the owner's operator
+# removes at the handover: W2-60a's launcher refuses a worker launch while it is set, DEC-313). Only this lead line
+# carries them; a worker starts through gov launch, which refuses --add-dir, so workers stay walled.
 W2=$1; ID=$2; BRIEF=$3; LOGF=$4
 ...
 fi   (the registration)
+# DEC-1161 (2): the CLI drops a --add-dir whose folder is missing, without a word, and a lead makes its tests worktree
+# after it starts (git worktree add takes an empty folder), so that folder is made here, empty, when nothing is there.
+# The runs root is passed as it is and nothing is made in it here (DEC-751: an own folder is made and marked by gov
+# launch alone); what a lead may write there stays the guard's (DEC-728, DEC-743).
+TESTS="/home/usain/gov-os-worktrees/$W2-tests"
+RUNS="/home/usain/gov-os-runs"
+[ -e "$TESTS" ] || mkdir "$TESTS" || echo "$(date '+%F %T') LAUNCH_NO_TESTS_DIR: $TESTS could not be made; $W2 starts without it" >&2
 echo "$(date '+%F %T') gate open; $ID registered as pid $$; starting $W2" >&2
 exec /home/usain/.local/bin/claude -p --model claude-opus-5-5 --effort high --output-format json --permission-mode acceptEdits \
   --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" \
   --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"$ID\",\"CLAUDE_CODE_SUBAGENT_MODEL\":\"claude-opus-5-5\"}}" \
+  --add-dir "$TESTS" --add-dir "$RUNS" \
   --append-system-prompt-file "$TEMPLATE" \
   < "$ORCH/briefs/$BRIEF" > "$ORCH/log/$LOGF"
```
A failed `mkdir` does not stop the lead (it starts without the tests folder, as the CLI would drop it anyway) and says
`LAUNCH_NO_TESTS_DIR` in the launch log.

## 3. The companion (before the apply) and the follow-up (after it)

- **Why:** `tests/unit/launch/test_w2_153_template.py::test_the_dispatchers_lead_form_is_otherwise_the_same_command` compares the exec block
  line by line, and `tests/acceptance/W2-153/test_w2_153_dispatch.py::test_f2_the_lead_line_is_integrate_s_but_for_the_one_flag` compares the
  whole argv with integrate's at W2-153's baseline commit. Both go red with the ACT alone (rehearsed, section 4 C).
- **`companion-tests.diff` (45 lines):** the unit test also leaves out a line that starts with `  --add-dir `; the acceptance test strips the
  `--add-dir <value>` pairs before W2-153's comparison (a local `_without_add_dirs`). Green on the old launcher and on the new one, so it can
  land any time before the apply, with nothing red in between.
- **The route is the CTO's:** one of the two files is under `tests/acceptance/` (W2-153's). Two known routes: (i) as ACT-LOAD-BALANCER-A's
  companion did (`792b92923`, "Merge w2/W2-153: the test beds' stand-in gov for ACT-LOAD-BALANCER-A's gate and registration", Task
  DAEO-8s85): a commit on W2-153's branch, merged by the CTO; or (ii) a commit with its own `acceptance_exemptions` entry (DEC-1136 (2)) so
  W1-01 stays green. This helper did not choose and did not commit.
- **`followup-tests.diff` (34 lines, optional, after the apply):** two unit tests of the new line (the two `--add-dir` values and their
  place; the empty folder made; an existing tests worktree left alone). Red on the old launcher by design (rehearsed, F3), so they land only
  after the apply. Until then the ACT's own manifest checks 1 and 2 are the record of the new behaviour.

## 4. The rehearsal

`rehearsal.log` (sha256 `cc3f04710512`): **62 ok, 0 failed**, last line `failures: 0`, run as one `heavy_slot.sh bash rehearse.sh ...` (slot 1, CPUs 0-5,
06:57 to 07:23 UTC, the round-1 rebuild), on its own clone of `w2/integrate` at `829282dbd530` (the main tree's head then), TMPDIR
in the helper's scratchpad. The suites are the three files that read the launcher: `tests/unit/launch/test_w2_153_template.py`,
`tests/acceptance/W2-153/test_w2_153_dispatch.py`, `tests/unit/orchestration/test_dispatcher.py`.

| Section | What | Result |
|---|---|---|
| A | bundle not stale (clone and main-tree launcher = before `023623ac6ac8`); `check` before; `verify` refused (3); `undo` no-op | 6 ok |
| B | suites on the before launcher; manifest checks before (exits 0 1 1 1 0) | **223 passed**, 3 skipped, 10 deselected; checks as expected |
| C | plain apply **without** the companion: checks 0 0 0 **1** 0 (check 3 refuses); suites | **2 failed** (the two W2-153 tests named in section 3), 221 passed; undo byte for byte |
| D | companion applied: old launcher green (**223 passed**); apply: after byte for byte, mode 755, git status only the launcher and the two companion files, no temp file, `check` applied, `verify` 0, apply again no-op | all ok |
| E | every manifest check exactly as written (`bash -c`, clone root) on the applied clone: exits 0 0 0 0 0; suites; check 1 refuses a wrong `RUNS` and a wrong `TESTS` line (E2, E3), launcher back to after (E4) | **223 passed**; 3 ok |
| F | follow-up tests: with the ACT **225 passed**; after `undo` the two new tests **red** (2 failed, 223 passed); re-applied | as designed |
| G | dry run of the lead line, planted `W2-PLANT`, stub `claude` and `gov` in a temporary bed: argv ends `--settings {...} --add-dir <bed>/trees/W2-PLANT-tests --add-dir <bed>/runs --append-system-prompt-file <bed>/trees/W2-PLANT/.claude/templates/role-lead.md`; the tests folder made empty; `git worktree add` into it works; no `LAUNCH_NO_TESTS_DIR` | 4 ok |
| H | `undo` byte for byte; `check` before; a drifted launcher refused by `apply` and `undo` (exit 3, untouched); the main tree's launcher and its tracked `governance/ tests/ src/` status unchanged (read with `--no-optional-locks`) | 7 ok |

Manifest checks: 0 `bash -n`; 1 the line's form (two `--add-dir` only, on the line before the template flag, `TESTS`/`RUNS` as named, the
one `mkdir` after the registration and before `exec`, no name match, no `mkdir -p`, no `rm`); 2 the bed (fresh lead, resumed lead, shut
gate makes nothing and starts nothing); 3 the companion guard; 4 `gov launch` still refuses `--add-dir` (workers stay walled). (Round 1's check 5 on the scratch `launch_worker.sh` was dropped, F1.)

## 5. The handover, in DEC-1161 (2)'s order (the owner's operator, after the CTO's apply)

**Before step 1:** the ACT is applied and verified (section 0); `bash $G/apply.sh verify` exits 0.

**Step 1 (done by the CTO, section 0):** ACT-LEADS-ADD-DIR-1 applied. Every lead the dispatcher starts from then on carries the two
`--add-dir`.

**Step 2: a fresh CTO session, started by the owner's operator, with `--add-dir` and Remote Control** (in a plain terminal):
```
tmux new -d -s cto 'cd /home/usain/Dynamic-Agentic-Engineering-OS && ~/.local/bin/claude --remote-control CTO --add-dir /home/usain/gov-os-worktrees --add-dir /home/usain/gov-os-runs'
tmux ls        # expect "cto: 1 windows ..." beside "cto-sentinel: ..."
```
This is the running sentinel's form (`ps`: `tmux new -d -s cto-sentinel 'cd /home/usain/Dynamic-Agentic-Engineering-OS &&
~/.local/bin/claude --remote-control "CTO sentinel" --model claude-haiku-5-5 --settings "{...GOV_ROLE orchestrator, GOV_TICKET DAEO-sdxk...}"
"$(cat ...)"'`) less its model, settings and prompt: the CTO's `GOV_ROLE`/`GOV_TICKET` come from the main checkout's local settings, whose
`env` stays. If the session name `cto` is taken, pick another (`tmux ls` first). The old CTO session (today in the editor) is ended by the
owner when the new one has taken over; the sentinel needs no added directory and is left as it is.

**Step 3: remove `permissions.additionalDirectories` from the main checkout's `.claude/settings.local.json`** (untracked, git-ignored; a
`settings` path, class (b) by the rules, given to the owner's operator by DEC-1161 (2)), with a backup, in one command:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS && cp -p .claude/settings.local.json .claude/settings.local.json.pre-dec1161 && python3 -I -c 'import json; p=".claude/settings.local.json"; d=json.load(open(p)); d["permissions"].pop("additionalDirectories"); open(p+".new","w").write(json.dumps(d, indent=2)+"\n")' && mv .claude/settings.local.json.new .claude/settings.local.json
python3 -I -c 'import json; d=json.load(open("/home/usain/Dynamic-Agentic-Engineering-OS/.claude/settings.local.json")); print(sorted(d), sorted(d["permissions"]))'   # expect ['env', 'hooks', 'permissions'] ['allow', 'deny']
```
The file round-trips byte for byte through `json.dumps(indent=2)` plus a newline (checked), so only that key changes. With jq instead:
`jq 'del(.permissions.additionalDirectories)' .claude/settings.local.json > .claude/settings.local.json.new && mv .claude/settings.local.json.new .claude/settings.local.json`
(after the same `cp -p` backup; jq may re-format). After step 3, W2-60a's half-done merge can be finished (its launcher's worker check then
passes, simulated in section 1).

**Before step 3, which leads still rely on the local settings** (read only; a lead started before the apply has no `--add-dir`):
```
python3 -I -c 'import os
for p in filter(str.isdigit, os.listdir("/proc")):
    try: a=[x.decode() for x in open(f"/proc/{p}/cmdline","rb").read().split(b"\0") if x]; c=os.readlink(f"/proc/{p}/cwd")
    except OSError: continue
    if a and a[0].endswith("/claude") and "-p" in a and "\"GOV_ROLE\":\"orchestrator\"" in " ".join(a) and c.startswith("/home/usain/gov-os-worktrees/"): print(p, c, "add-dir" if "--add-dir" in a else "NO add-dir")'
```

## 6. Risks

1. **Leads already running at step 3** (four now, none with `--add-dir`) may lose the two directories mid-run if the CLI reloads the
   changed local settings. Their reads are unaffected (reads are open); an Edit/Write in the tests worktree or the runs root, and a Bash
   command the CLI path-checks there, would be refused and count toward their two-refusal stop. Lowest risk: do step 3 when the command above
   prints no "NO add-dir" line, or accept it (a refused lead returns PACKAGES and the dispatcher restarts it with the new line).
2. **An empty `<W2>-tests` folder** is left when a lead's run makes no tests worktree. Harmless to the tools read: the dispatcher skips
   `-tests` names and folders without `.git` (`dispatcher.py:148`, `:1399`), `interim_watch.sh:12` and `hold_lib.py:86` skip `-tests`,
   `lead_ledger.py:374` looks for a log folder inside, and `git worktree add` takes the empty folder (rehearsed, G3). Clean-up: `rmdir`
   (refuses a non-empty folder).
3. **Other lead launch forms are not covered:** `tools/launch_when_gate_opens.sh` (scratch, used by `lead_chain.sh`/`lead_chain2.sh`, the
   pre-dispatcher form) and a lead started by `gov launch orchestrator` (which refuses `--add-dir`, section 1). A lead started either way
   after step 3 has neither directory as a working directory.
4. **The runs root, not the lead's own runs folder:** broader than the narrowest, but it is what leads have today, the own folder often
   does not exist at launch and must not be made by the launcher (DEC-751), and the guard still decides what a lead writes there.
5. **The companion's route** touches a closed ticket's acceptance test (W2-153); if it lands without route (i) or an exemption entry, W1-01
   turns red (DEC-1136 (2)).

## 7. Undo

- **The ACT:** `bash .gov-runtime/scratch/orchestrator/acts/ACT-LEADS-ADD-DIR-1/apply.sh undo` puts the frozen before back, byte for byte,
  only from the after hash (a later change is refused, exit 3, untouched); then commit the revert with the same trailers. Leads started
  meanwhile keep their line; the next lead gets the old one. Empty `-tests` folders it made stay (risk 2).
- **The companion:** reverting it is not needed for the undo (it is green on both launchers).
- **Step 3:** `cp -p /home/usain/Dynamic-Agentic-Engineering-OS/.claude/settings.local.json.pre-dec1161 /home/usain/Dynamic-Agentic-Engineering-OS/.claude/settings.local.json`
  (this brings W2-60a's worker refusal back).
- **Step 2:** end the `cto` tmux session (`tmux kill-session -t cto`) once another CTO session is running.

## 8. Hashes

| File | sha256 |
|---|---|
| `manifest.json` | `1781a70844291708a1ffa7751391f0c8cbb2e29b917afe927ef4db8e40f5c162` (yes line `1781a708`) |
| `before/repo/.../launch_now.sh` (= live `w2/integrate` and the main tree) | `023623ac6ac8b7f3af21db454a6965b8ab321dbe9538c1861390638f9f43859d` |
| `after/repo/.../launch_now.sh` | `54345463a67b34fb32acc0bdb5c055455875118626e2f0924ecbb72d701656a9` |
| `apply.sh` | `5533fda21a8fde66bd291038861e3e4c764ab16b08e4ba68fd2d189e42738613` |
| `list.txt` | `b50b78587128f46bbf6bcdca9ecb38cb958c3ab259abc2124f79be0447a6a610` |
| `rehearsal.log` | `cc3f047105120796a6f4f46a74280373993db4056b0349267cc99dba057e4a66` |
| `companion-tests.diff` | `e6ff98edf9357f7a822bc7587807af208ac419db35751d5b2aed2fa6df5e1d61` |
| `followup-tests.diff` | `36280a9313e6c2a01cd6f0108cd8c8bef07215db33d40c27df86aa53a94da133` |

`apply.sh`'s body (from `set -u` on) is ACT-LOAD-BALANCER-A's, byte for byte; only its header differs.

## 9. Before the yes

1. **One independent review** of the bundle (fresh, read-only session; its fenced verdict block in `review.md`, or the operator's G4 refuses).
2. **The companion's route and landing** (section 3), before the apply.
3. The CTO's choice on risk 1 (the timing of step 3 against the running leads).
4. Rehearsal note: the first rehearsal run (`drafts/leads-add-dir/rehearsal.run1-shared-clone.log`) was stopped and is not the record:
   the clone it used, `$TMPDIR/clone` in the session scratchpad that the CTO's helpers share, was written into by another helper's work
   (ACT-OPERATOR-HOURS-3's after files appeared in it at 01:54:48). The record is the second run, on its own clone
   (`.../scratchpad/leads-add-dir-1/clone`). This helper's own changes in the shared `clone` were taken back out; the other helper's were left.
