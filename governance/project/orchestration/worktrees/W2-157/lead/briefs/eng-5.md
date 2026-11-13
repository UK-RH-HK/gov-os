# Brief eng-5: engineer for DAEO-ozyt (W2-157), profile STANDARD, class C2: the reopened fix, iteration 2 (load reds)

You are a fresh engineer for ticket DAEO-ozyt (W2-157: the GPU backstop, `gov resources --backstop <pgid>...`). The
owner reopened the ticket for one fix (DEC-1144 (2), P1-B (a)): read the ticket's last section "Reopened for one fix".
A first engineer made that fix (head f5b148151 of w2/W2-157: a group of only zombies has ended, `watch(...,
max_polls=)`, each test reaps what it plants). Its unit file no longer hangs, but under CPU load it is red. You make
the unit file green under load and nothing else. No KPI line changes; you never read or change `tests/acceptance/`.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157 |
| branch | w2/W2-157 |
| your allowed paths | src/gov/resources/backstop.py, tests/unit/resources/test_w2_157*, docs/changes/W2-157-evidence.md |
| the ticket | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| the unit tests | tests/unit/resources/test_w2_157_backstop.py (the `Rig` class and `rig` fixture) |
| the lead's failing output (full) | /home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/lead/red-load-run20.txt |
| the lead's load loop (read it; run your own copy under your $TMPDIR) | /home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/lead/stress20.sh |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The failing output
The lead ran `tests/unit/resources/test_w2_157_backstop.py` 20 times inside a heavy slot of 7 CPUs with 7 busy loops
(`python3 -c "while True: pass"`) beside it: every run exit 1, 2 to 10 failed each, none hung (a light-load loop of 20 was
20 of 20 green). The last run:
```
FAILED test_w2_157_backstop.py::test_s1_below_then_above_the_limit_pauses_at_the_second_reading
  E  AssertionError: assert 'R' == 'T'                                         (line 224)
FAILED test_w2_157_backstop.py::test_s1_the_limit_and_period_are_the_files
  E  assert (True and [7, 0.001, 0....8, 0.016, ...] == [7])  Left contains 3548 more items, first extra item: 0.001  (line 253)
FAILED test_w2_157_backstop.py::test_s3_a_partial_offload_line_written_since_the_start_trips_it
  E  assert (True and 2 == 3)  where 2 = smi_calls()                           (line 404)
FAILED test_w2_157_backstop.py::test_the_bound_ends_a_watch_that_never_trips_after_exactly_that_many_polls[2]
  E  assert (2 == 2 and [5, 0.001, 0....8, 0.016, ...] == [5])  Left contains 7240 more items  (line 1013)
FAILED test_w2_157_backstop.py::test_the_default_has_no_bound_and_polls_on_until_the_group_ends
  E  assert (False is False and 4 == 9)  where 4 = smi_calls()                 (line 1069)
9 failed / 5 failed / 4 failed ... in the other runs (names not kept).
```

## The lead's reading of the cause (check it; do not take it on trust)
`backstop.time` is the global `time` module, so `rig.mp.setattr(backstop.time, "sleep", ...)` (and the rig's own
`monkeypatch.setattr(time, "sleep", lambda s: None)`) replaces `time.sleep` for the whole process. `read_gpu` calls
`subprocess.run(..., timeout=20)`; under load the stand-in `nvidia-smi` has closed its output but not yet exited when
`communicate` returns, so `Popen._wait` (timeout given) polls with `time.sleep(0.001, 0.002, ... 0.05)`. Those calls
land in the test's replacement: `rig.sleeps` gains `0.001, ...`, and a replacement with a side effect (write the log,
kill the job, count polls, end at the ninth) fires inside a GPU reading rather than between polls. The `lambda s: None`
also makes those waits spin. Every test that replaces the sleep is exposed, not only the five above.

## The fix wanted
Only the backstop's own pause between polls is replaced in a test, never `time.sleep` for the process. Either (a) a
module-level seam in `backstop.py` (e.g. `_pause = time.sleep` called as `_pause(every)`, or `watch` reading
`time.sleep` through a name the tests can patch without touching the `time` module), the tests patching that seam; or
(b) tests-only, patching `backstop.time` with a stand-in object (not the module) that has the `sleep` they want. Pick
one, say which and why in the evidence; the command's behaviour is unchanged either way. Remove the rig's global
`time.sleep` replacement; any wait loop a test needs uses the real sleep. Keep every assertion's meaning (no assertion
weakened, no count loosened); the bounds and the reaping from iteration 1 stay. A test of the seam: a replaced backstop
pause is not called by `subprocess` (e.g. a stand-in `nvidia-smi` that closes stdout then sleeps 0.2 s before it
exits: `rig.sleeps` holds only the period).

## Proof (put the summary lines in `evidence`)
Every pytest through the heavy-slot tool, with your sandbox's own `$TMPDIR` (outside the repository and ~/gov-os-runs;
`/tmp/<name>` may be read-only in the sandbox), `PYTHONUSERBASE=/home/usain/.local`, an empty HOME:
`env TMPDIR=<your tmp> HOME=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-157/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(no pytest-randomly installed). A heavy slot or memory gate refusal is a wait: retry when open.
1. Red first: your copy of the lead's load loop (one busy loop per CPU of the slot, `OMP_NUM_THREADS= nproc`, each run
   under `timeout 120`, the busy loops killed by their pids at the end) on the present head shows the reds.
2. After the fix: the same loaded loop, 20 runs, every run exit 0, none 124.
3. Then `tests/unit/resources`, `tests/acceptance/W2-157` and `tests/acceptance/W2-20` once each (the form above).
No planted process may outlive a run.

## Safety
Unit tests plant their own process groups only (`start_new_session=True` or `setsid`) and stand-ins under `tmp_path`;
never signal a process you did not start; never run `--backstop` against a real group, the real GPU or the real HOME's
gate.json. Stop anything stuck by its pid (`kill <pid>`), never by a name (`pkill`, `killall` are refused).

## Rules
- Add to the evidence's section "Reopened fix (DEC-1144 (2))" a short paragraph: the load reds, their cause, the seam
  chosen, and the loaded 20-run line.
- Anything longer than one line goes in a script file under your $TMPDIR, run with `bash <file>`. Literal paths only.
  No merge, no push, no edit outside your paths. A refused call is reported, never worked around; refused twice for
  the same action, stop and say so. For a new file, `git add <path>` before `git commit -- <paths>`.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: engineer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1073" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the red loop's line, the 20 loaded runs' exit codes and summary lines; the
pytest summary lines of tests/unit/resources, tests/acceptance/W2-157 and tests/acceptance/W2-20) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The ticket's context (gov context DAEO-ozyt --role engineer)
{
  "ticket": "DAEO-ozyt",
  "ticket_text": "---\nid: DAEO-ozyt\nstatus: in_progress\ndeps: [DAEO-r30l]\nlinks: [DAEO-r30l, DAEO-5emz]\ncreated: 2026-11-11T01:20:16Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-157\ntags: [wave-2, implementation, standard, after-the-lift, gpu, capacity]\nwbs_id: W2-157\ntitle: 'The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills into shared memory, or an embedder is not wholly on the GPU (EMERGENCY-TOOLS-1 D12; DEC-1067, DEC-1068 (4))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-r30l\nallowed_paths:\n- src/gov/resources/backstop.py\n- src/gov/resources/command.py  # the one option, --backstop\n- src/gov/resources/config.py  # the one new value, gpu_backstop_limit_mib\n- tests/unit/resources/test_w2_157*\n- docs/changes/W2-157-evidence.md\n- docs/probes/DAEO-ozyt/**  # the probe record, so F4 holds at the branch head (run 1's F4 note; the CTO, 2026-11-12 07:20)\nreads:\n- src/gov/resources/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/resources/command.py\n- src/gov/resources/config.py\nwaits_on:\n- ref: DAEO-r30l\n  reason: 'W2-20 owns src/gov/resources/** and its gate configuration; this ticket adds one module and one value after it merges'\nkpis:\n  success:\n  - 'S1 `gov resources --backstop <pgid> [<pgid> ...]` watches the named process groups and, every 5 seconds (a configured value), pauses every live named group with SIGSTOP at once when GPU memory used is above the configured limit (`gpu_backstop_limit_mib` in the gate''s one configuration file, dated and sourced; this machine''s value 15,872 MiB, 15.5 GiB); a missing or malformed limit refuses to start, naming it. Verify: a stand-in `nvidia-smi` printing 15,800 then 15,900 MiB and a stand-in job in its own process group: the job is running at the first reading, stopped at the second, the trip logged with the reading [DEC-1067 (GPU safety), DEC-1068 (4)]'\n  - 'S2 A spill into shared GPU memory trips it too: GPU memory used within 64 MiB of the card''s total. Verify: a stand-in reading of total minus 63 MiB trips it and total minus 65 MiB does not [DEC-1067 (GPU safety), DEC-1068 (4)]'\n  - 'S3 An embedder not wholly on the GPU trips it: a model of an embedding server (the ports from the gate''s configuration) whose `size_vram` is below its `size`, or a line \"offloaded N/M layers to GPU\" with N below M in the server''s log written since the watch started. Verify: a stand-in server answering both forms, each tripping it once, and a line with N equal to M not tripping it [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030]'\n  - 'S4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument \"abc\"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]'\n  - 'S5 It changes nothing else: it only reads the GPU, the servers'' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]'\n  failure:\n  - 'A process outside the named groups paused or signalled. Verify: S4''s planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure'\n  - 'A trip on a reading under every limit, or a spill, an embedder partly on the CPU or a partial offload not tripping it. Verify: S1''s stand-in readings (15,800 MiB no trip), S2''s (total minus 65 MiB no trip, total minus 63 MiB trip) and S3''s stand-in server (N equal to M no trip; `size_vram` below `size` and N below M each trip): each reading gives the stated outcome'\n  - 'A limit taken from anywhere but the gate''s configuration file. Verify: a planted configuration with a limit differing from the built-in value (and an environment variable and a command-line argument holding a third value): the trip happens at the file''s value only; a planted file with the limit missing or malformed refuses to start and names it'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1010\n- DEC-1067\n- DEC-1068\n- DEC-1030\n- DEC-1073\n- DEC-1119\n- DEC-1109\n- DAEO-r30l  # W2-20\nest_loc: 160\nacceptance_tests:\n  path: tests/acceptance/W2-157/\n  author: 'independent-test-designer (MR-3), from these KPI lines; a stand-in nvidia-smi, a stand-in embedding server and planted process groups, never the real GPU or the shared servers'\ntrack: A\nlist_rows: []\n---\n# W2-157 The GPU backstop in the product\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 row D12; **after the lift**, **before EXAMIN's copy** (\u00a71 D12 \"yes, GPU safety\"; the copy shares this machine's GPU).\n\n- **Problem.** The CTO's `gpu_backstop.sh` (`.gov-runtime/scratch/orchestrator/tools/gpu_backstop.sh`, DEC-1067 (GPU safety), DEC-1068 (4)) pauses a GPU job on a memory limit, a spill or a partial offload. It is a scratch tool. W2-20's gate refuses a start that lacks GPU room and stops the largest heavy job below a memory floor; neither watches a GPU job while it runs, and EMERGENCY-TOOLS-1 \u00a73 retires the tool only once the product covers a spill. W2-137 S5 already names \"the GPU backstop armed\" as a step of its measure.\n- **Approach.** One module beside W2-20's gate, started with `--backstop` and the job's process groups. Same triggers and the same pause as the script; the limit moves into the gate's configuration file. Alternative: fold it into W2-20's trip-wire (rejected: W2-20 is merged or in review and its trip-wire is on system memory, not the GPU).\n- **Interface.** `gov resources --backstop <pgid>...`; the limit `gpu_backstop_limit_mib`; the poll period `gpu_backstop_every_s`. The inbox is the project's inbox folder (as W2-156's).\n- **Non-goals.** No kill (a pause only; the owner or the CTO resumes or stops); no GPU scheduling (W2-20 S-lines on GPU shares); no change to the shared servers.\n- **Rabbit holes.** Matching processes by name or `ps | grep` (the groups are named, nothing else); reading Windows' shared-usage counter (WSL cannot; the total-minus-64 MiB sign stands).\n\n[DEC-1067 (GPU safety), DEC-1068 (4), DEC-1119 (5)]\n\n## Run 1's notes (the CTO, delegated P2, 2026-11-12 07:20)\n\nF4: the probe record's folder is in allowed_paths (no test change after the review). The lead's L2 key `gpu_backstop_embedders` and\nthe three backstop keys outside `template()` (W2-20's frozen key set) stand. Rows: FR-11 (a try/finally so the own group's pause\nhappens whatever the item write does), FR-12, FR-13, FR-3 (an owner question: a GPU that cannot be read), FR-4, FR-6 to FR-10.\nAfter the land the owner's operator adds the three gate.json entries (docs/changes/W2-157-evidence.md).\n\n## Reopened for one fix (the owner, DEC-1144 (2), P1-B (a), 2026-11-12)\n\n`tests/unit/resources/test_w2_157_backstop.py::test_s3_the_limit_comes_before_the_spill_before_the_embedder_before_the_log` hung two\nmerge-queue runs (1 h 45 min, then 77 min). The cause: the test replaces the backstop's sleep, then calls `watch()` on planted process\ngroups; a call that does not trip polls forever, because a group whose members are all zombies (unreaped) or paused still passes\n`os.killpg(g, 0)`. The fix, inside S4 as written (\"when every named group has ended on its own, the watch logs it and ends\") and this\nticket's paths: (1) a group whose live members are all zombies counts as ended; (2) `watch()` takes a bound (a maximum number of polls\nor seconds, a keyword argument whose default keeps the command's behaviour), and every test that calls it passes one; (3) each test reaps\nthe process groups it plants. No KPI line changes. One C2 run; it lands through the queue (DEC-989). The owner's temporary skip (P1-B (b))\ncannot take effect without a control-path change (DEC-1144 (2)'s note), so until this lands a hang is stopped by pid.\n",
  "authority": [
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1067",
      "sha256": "6a043602e5c77a59cfe06b8fe0bd6bb8faae30427eea44a284de2470bd4a70d1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6a043602e5c77a59cfe06b8fe0bd6bb8faae30427eea44a284de2470bd4a70d1",
      "reason": "declared in sources",
      "tokens": 1102
    },
    {
      "id": "DEC-1068",
      "sha256": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "reason": "declared in sources",
      "tokens": 983
    },
    {
      "id": "DEC-1030",
      "sha256": "4a2c2d06cc9c56f23bf2a745ecbc44518a26d45a01d758250f1cd842013bd7bd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a2c2d06cc9c56f23bf2a745ecbc44518a26d45a01d758250f1cd842013bd7bd",
      "reason": "declared in sources",
      "tokens": 381
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DAEO-r30l",
      "sha256": "c8ece8799d3d23c7781f98354f9a78d69015f7df93edcdd9f5889ab2bd32421b",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "c8ece8799d3d23c7781f98354f9a78d69015f7df93edcdd9f5889ab2bd32421b",
      "reason": "declared in sources",
      "tokens": 2424
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1067",
      "sha256": "6a043602e5c77a59cfe06b8fe0bd6bb8faae30427eea44a284de2470bd4a70d1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6a043602e5c77a59cfe06b8fe0bd6bb8faae30427eea44a284de2470bd4a70d1",
      "reason": "declared in sources",
      "tokens": 1102
    },
    {
      "id": "DEC-1068",
      "sha256": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "reason": "declared in sources",
      "tokens": 983
    },
    {
      "id": "DEC-1030",
      "sha256": "4a2c2d06cc9c56f23bf2a745ecbc44518a26d45a01d758250f1cd842013bd7bd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a2c2d06cc9c56f23bf2a745ecbc44518a26d45a01d758250f1cd842013bd7bd",
      "reason": "declared in sources",
      "tokens": 381
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DAEO-r30l",
      "sha256": "c8ece8799d3d23c7781f98354f9a78d69015f7df93edcdd9f5889ab2bd32421b",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "c8ece8799d3d23c7781f98354f9a78d69015f7df93edcdd9f5889ab2bd32421b",
      "reason": "declared in sources",
      "tokens": 2424
    }
  ],
  "supplementary": [],
  "supplementary_query": "The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills into shared memory, or an embedder is not wholly on the GPU (EMERGENCY-TOOLS-1 D12; DEC-1067, DEC-1068 (4))\nS1 `gov resources --backstop <pgid> [<pgid> ...]` watches the named process groups and, every 5 seconds (a configured value), pauses every live named group with SIGSTOP at once when GPU memory used is above the configured limit (`gpu_backstop_limit_mib` in the gate's one configuration file, dated and sourced; this machine's value 15,872 MiB, 15.5 GiB); a missing or malformed limit refuses to start, naming it. Verify: a stand-in `nvidia-smi` printing 15,800 then 15,900 MiB and a stand-in job in its own process group: the job is running at the first reading, stopped at the second, the trip logged with the reading [DEC-1067 (GPU safety), DEC-1068 (4)]\nS2 A spill into shared GPU memory trips it too: GPU memory used within 64 MiB of the card's total. Verify: a stand-in reading of total minus 63 MiB trips it and total minus 65 MiB does not [DEC-1067 (GPU safety), DEC-1068 (4)]\nS3 An embedder not wholly on the GPU trips it: a model of an embedding server (the ports from the gate's configuration) whose `size_vram` is below its `size`, or a line \"offloaded N/M layers to GPU\" with N below M in the server's log written since the watch started. Verify: a stand-in server answering both forms, each tripping it once, and a line with N equal to M not tripping it [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030]\nS4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument \"abc\"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]\nS5 It changes nothing else: it only reads the GPU, the servers' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]\nA process outside the named groups paused or signalled. Verify: S4's planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure\nA trip on a reading under every limit, or a spill, an embedder partly on the CPU or a partial offload not tripping it. Verify: S1's stand-in readings (15,800 MiB no trip), S2's (total minus 65 MiB no trip, total minus 63 MiB trip) and S3's stand-in server (N equal to M no trip; `size_vram` below `size` and N below M each trip): each reading gives the stated outcome\nA limit taken from anywhere but the gate's configuration file. Verify: a planted configuration with a limit differing from the built-in value (and an environment variable and a command-line argument holding a third value): the trip happens at the file's value only; a planted file with the limit missing or malformed refuses to start and names it\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 10202,
  "budget": {
    "limit": 12000,
    "used": 10202
  },
  "hash": "48dbea299c6b12067115c1a9cca01afd1c33b4ea477f7d2535c6b865a7c82c7b"
}
