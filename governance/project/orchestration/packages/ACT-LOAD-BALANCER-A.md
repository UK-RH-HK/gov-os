# ACT-LOAD-BALANCER-A: the dispatcher's launcher checks the resource gate and registers each lead (DEC-1133 (3))

- **For:** the owner's operator (class (b): it needs the owner's yes), after the CTO has committed the companion test change
  (section 6) and an independent review says READY.
- **By:** an ACT-preparation helper for the CTO (Sonnet, high; RUBRIC-2), 2026-11-11. Built and rehearsed in a clone and a
  planted home with a stub lead. **Nothing live was changed or started: no real claude session, no real lead, no
  dispatcher, no commit, no stage.** The main tree stayed clean.
- **Sources:** DEC-1133 (3); DEC-1105 (the sample day, then `--remeasure`); DEC-1008 item 5 and DEC-898 (the launcher and
  the disk gate it keeps); DEC-1073 (pids only); `governance/project/orchestration/packages/LOAD-BALANCER-1.md` (section 3,
  ACT A, and the gap named near its line 140); `governance/project/operator/class-rules.yaml`.

## 1. What changes, and why
DEC-1133 (3): "`launch_now.sh` checks the gate before each lead and registers it", so the resource gate and the lead-memory
sampler see every lead the dispatcher starts, and the sample day after it (a working day with leads running) measures real
lead sizes, so `--remeasure` writes the p95, not the maximum. Without it the sample day measures small sessions only
(LOAD-BALANCER-1, near line 140).

**One file, `governance/project/orchestration/tools/dispatch/launch_now.sh`** (the committed launcher; see "Which file" below).
Before the unchanged `exec claude ...` line, after the existing disk gate and template check, it now does three things:

1. `gov resources --check` (the product's start check; its reading goes to the launch log). Exit 0 continues. Exit 3
   (gate shut) or any other result (gov missing, a fault) stops the start: **exit 3, `LAUNCH_GATE_SHUT`, nothing started,
   nothing registered** (fail closed).
2. `gov resources --register "$$" --ticket <id> --session-role orchestrator`: the launcher's own pid. If this fails: **exit 4,
   `LAUNCH_NOT_REGISTERED`, nothing started.**
3. The `exec` is kept as it is (same command, same flags, same line text), so the pid and the process start are the ones just
   registered: **the entry is the lead's own, and it is in place before the lead runs.** No wrapper, no background job,
   no `wait`, so a stop by pid or process group still reaches the lead (DEC-1073).

### What "registers it" means for each reader (item 1 of the brief; found in the code)
| Reader | What it reads for running leads | Needs a change? |
|---|---|---|
| `tools/gate_check.py` (the old gate) | no file: `lead_mem.snapshot()` scans `/proc` for a `claude ... -p` process whose argv holds `"GOV_ROLE":"orchestrator","GOV_TICKET":"<id>"` | No. It already counts any lead the launcher starts (the `exec` keeps the argv). Rehearsed: the sampler lists the stub lead. |
| `tools/lead_mem.py` (the lead-memory sampler, `log/lead-mem.jsonl`) | the same `/proc` scan | No, same. |
| The product's gate, `gov resources` (reading, `--check`, and `gov launch`'s admission) | the registry folder `~/.gov-os/machine/sessions/<pid>.json` (pid, repository, ticket, role, boot, start ticks) | **Yes: this is what the ACT adds.** Today no lead has an entry, so the gate cannot see them. |
| `gov resources --sample` and `--remeasure` (DEC-1105) | the same registry folder, plus the slot holders | **Yes, same.** The sample takes the process-tree memory of each registered session, so it now holds each lead (workers started and registered from a lead's tree are charged once, as their own sessions: `registry.py`). |

An entry whose process has ended is removed by the next reading (rehearsed). A reused pid is never taken for it (the
entry holds the process's boot and start; rehearsed: its start equals the running lead's).

### Which file (a finding the CTO should know)
The task named `.gov-runtime/scratch/orchestrator/dispatch/launch_now.sh`. **That copy is stale** (985 bytes; no role-template
check) and nothing runs it. The crontab line runs `governance/project/orchestration/tools/dispatch/run_tick.sh`, and the
committed `dispatcher.py` starts `CODE / "launch_now.sh"`, its own folder's file (1,370 bytes, W2-153's version, commit
`e57be0ee8365`). The ACT changes the committed file. The scratch copy is left alone (class (O), `cto-scratch`, not an ACT's
business); the CTO may delete or refresh it so nobody patches the wrong one again.

## 2. Class: (b), row `watchers`
`governance/project/operator/class-rules.yaml`, row **`watchers`** (`root: repo`, path
`governance/project/orchestration/tools/dispatch/**`, "the sentinel, the dead-man's switch and the dispatcher"): **class b,
control true.** Checked: the operator's own `act_class.py` run (read only) on this bundle returns class **b**, file row
`watchers`, no other file. It also reports one script hit `session` (class b, the same) on a check line that writes the stub
`claude` into a temporary folder; it is a false hit, it does not change the class. The class-(O) rows (`cto-scratch`, the
pin) are not touched. The scratch `dispatch/` copy would be (O), by hand; that is why the ACT does not name it.
`claimed_class` in the manifest is `b`.

**The owner's yes line:** `yes ACT-LOAD-BALANCER-A 0b40f1bf` (the first 8 digits of the manifest's sha256 below).

## 3. The bundle (`acts/ACT-LOAD-BALANCER-A/`, beside this file)
`manifest.json` sha256: **`0b40f1bfd84b65d043a7e7e2599d0717139461885f8f73462a3f24751b7a8e5f`** (`sha8` 0b40f1bf).

| File | sha256 |
|---|---|
| `before/repo/governance/project/orchestration/tools/dispatch/launch_now.sh` (the file at `b9e878009b8c`) | `03b93044ff986600a4e47185b7fbbb8b594c77579f42cd35dc206e631e5717ec` |
| `after/repo/governance/project/orchestration/tools/dispatch/launch_now.sh` | `023623ac6ac8b7f3af21db454a6965b8ab321dbe9538c1861390638f9f43859d` |
| `apply.sh`, `list.txt`, `rehearsal.log` | in `manifest.json` (`files`) |

`apply.sh check | apply | undo | verify` decides by sha256 alone: **before** (the frozen before) applies; **applied** changes
nothing; **other** (changed since, missing, a link) is refused, exit 3, nothing touched. The plain apply writes only the one
file (a `mktemp` file beside it, the mode kept, then moved); there is no backup option. If the launcher changes before the
apply, `check` says `state other` and nothing is touched: rebuild the after copy from `drafts/act-a/launch_now.sh`'s two
changes and freeze a new bundle.

## 4. The checks (`manifest.json`, each run as `bash -c` from the repository root, all four exit 0)
No check needs pytest: the operator's dry run plants HOME, which hides the user-site pytest, so the pytest runs are in the rehearsal.
0. `bash -n` on the launcher (syntax).
1. Structure: the gate check, then the registration, then the `exec`; the two refusal words; the template flag kept; nothing
   by process name (`pgrep`, `pkill`, `killall`, `pidof`).
2. Behaviour: the launcher copied into a temporary folder with its own absolute paths moved there (read from the script
   itself, so the check names no live path), a stub claude and a stub gov. An open gate: the check is the first gov call,
   the registration is the second and carries the pid the lead then has, the lead starts. A shut gate: exit 3, no lead
   started, no registration.
3. The companion test change has landed (a stand-in gov in the two existing launcher test beds). **This is the sequencing
   guard: until the companion is committed, check 3 is red and the operator refuses the ACT.**
Red on the old launcher: checks 1 and 2 (rehearsal H7). Check 3 is red until the companion lands (rehearsal C).

## 5. Undo
`bash apply.sh undo` from the bundle's folder, run in the repository: the frozen before copy, byte for byte, only while the
file is as this ACT left it (a later change is never overwritten). Rehearsed (C2, C3, H5, H6, H3). No lead already running
is affected either way: the change acts at each start.

## 6. Prerequisite: the companion test change (not an ACT; the CTO commits it first)
The launcher is run by two existing suites with a stub `claude` and no `gov`. With the ACT in, a missing `gov` is a shut
gate (that is the point), so **three existing tests go red**: `tests/unit/launch/test_w2_153_template.py::
test_the_dispatchers_lead_form_passes_the_lead_template`, and in `tests/acceptance/W2-153/test_w2_153_dispatch.py`
`test_s2_the_lead_line_passes_the_flag_with_role_lead_md` and `test_f2_the_lead_line_is_integrate_s_but_for_the_one_flag`
(rehearsal C: 3 failed, 27 passed). The fix adds a stand-in `gov` that exits 0 to each test bed, no assertion changed:
`drafts/act-a/companion-tests.diff` (two files, 6 added lines). With it the 30 tests are green on the old launcher **and** on
the new one (rehearsal D), so it can land before the ACT and nothing is red in between.
Route: both files are under `tests/` (class (O): not an ACT's business). The acceptance file is the independent test
designer's (`tests/acceptance/**`: an engineer never writes it), so the CTO decides the route (a small follow-up under
W2-153's ticket or by the designer). `tests/unit/launch/` is an engineer's.

## 7. The rehearsal (`acts/ACT-LOAD-BALANCER-A/rehearsal.log`, `tools/rehearse.sh`; ends `failures: 0`; 52 `ok` lines)
A `--no-hardlinks` clone of `w2/integrate` at `b9e878009b8c`, a planted HOME, the untracked tools the tests read (`lead_mem.py`,
`disk_gate.sh`, `proc.sh`) copied into the clone's scratch folder, the operator's clean environment, every manifest check run
exactly as written with `bash -c`, the plain apply.

| Step | Result |
|---|---|
| A. the bundle is not stale; check, verify, undo before the apply | before; verify refused (3); undo "nothing to undo" |
| B. existing launcher tests on the old launcher | 30 passed |
| C. apply without the companion | checks 0-2 green, check 3 red, the 3 named tests red, as section 6 says; undone byte for byte |
| D. companion, then the plain apply | old launcher + companion: 30 passed; apply: the frozen after, mode 755 kept, only the one file changed (git status), no temp file left; apply again no change |
| E. the four manifest checks, as written, on the applied clone | all exit 0; the 30 existing tests pass |
| F. `test_launch_now_gate.py` (12 tests, stub gov and the real pinned gov under a planted HOME) | **new launcher: 12 passed; old launcher: 10 failed, 2 passed** (the 2 are "the disk gate and template still come first" and "the lead command is unchanged") |
| G. the dispatcher's own form, `setsid -f bash launch_now.sh ...`, a stub lead held for a moment, real gov | the lead finds its own registry entry at its first line; the entry's pid is the lead's, ticket and role as given; `gov resources` lists it with its memory; `lead_mem.py` lists it; `gov resources --sample` holds it; waited for by pid with `proc.sh wait`; the next reading clears the entry. On the old launcher the same run fails at the first check. |
| H. wider scoped set `tests/unit/launch` + `tests/acceptance/W2-153`; states | 285 passed, 1 skipped; a changed, missing or linked launcher is refused with nothing created; undo byte for byte |
| I. live files only read | the main tree's launcher still `03b93044ff98`; head still `b9e878009b8c` |

The tests that need the real gov use the product's own reading overrides (`GOV_RESOURCES_*`) and a planted HOME; they never
touch `~/.gov-os`. No test starts a real claude: it is a stub file, and nothing matches a process by name.

## 8. Differences from the real run
- The real launcher runs the real `claude`, with the machine's real readings. The gate there is the live `~/.gov-os/machine/gate.json`
  (floor 3 GiB, working size 2.04 GiB until the sample day). The rehearsal's gate is a planted one with overridden readings.
- The operator's dry run runs the four checks in a clone with a planted HOME and the operator's G1-G9; this rehearsal reproduces
  the clone, the environment and the plain apply but does not run the operator's program. The CTO's reviewer does.
- The registry call on a real lead's worktree (a real git worktree) was not tried; the rehearsal's lead tree is a plain
  folder (the registration only records `--root`, the working folder). The first real start shows it in the launch log
  (`log/<W2>-<time>-launch.txt`: "gate open; <id> registered as pid <pid>").

## 9. What to expect after it is in (risks)
- **A shut product gate now stops a lead the dispatcher admitted.** The dispatcher starts the launcher with `setsid -f`, so it
  never sees the exit code; `started.txt` already holds the lead, and about 5 minutes later it raises one "started but never
  ran" inbox item, with the reason in `log/<W2>-<time>-launch.txt` (`LAUNCH_GATE_SHUT`, the gate's reasons). It is not
  retried until the CTO lists it again. The product gate's conditions (memory floor, load, busy cores, disk) are comparable to
  the dispatcher's own (the dispatcher's is the stricter on memory, per LOAD-BALANCER-1 section 2), so a refusal should be rare;
  today's reading is open.
- **Registered leads count in the product gate's memory rule** (`available + live >= floor + working size x (sessions + 1)`):
  a worker launched with `launch_worker.sh` while several leads run is judged with the leads in the count. That is the aim of
  DEC-1133 (3). The working size stays 2.04 GiB until the sample day and `--remeasure` (the p95).
- A registration or gate-check fault (gov missing, a bad registry folder) now stops every lead start. I chose fail closed,
  as the dispatcher's own steps do. The other reading (warn and start) would leave the lead unseen, the gap this ACT closes.
  The CTO or the owner may prefer it: it is one line.
- The launcher is slower by two `gov` calls (about a second each).
- Not changed: the old `gate_check.py`, `lead_mem.py`, the dispatcher, `launch_when_gate_opens.sh` (retired).

## 10. After the ACT: the order (DEC-1133 (3), (2))
1. The error path and the listing rule first, each by ACT, as DEC-1133 (2) says (not this package).
2. Companion tests committed; this ACT applied (owner's yes).
3. The sample day on a working day with leads running (`resources_sample_day_v2.sh`; the leads are registered by this ACT, so
   the CTO's own session is registered by hand once: `gov resources --register <pid> --ticket DAEO-sdxk --session-role orchestrator`).
4. Read `samples_summary.py` first; then `--remeasure` writes the p95 (DEC-1133 (3)). LOAD-BALANCER-1 section 4 point 2 says
   `--remeasure` writes the maximum today: the p95 write is a separate ACT (class (b), `~/.gov-os/machine/**`), not prepared here.
