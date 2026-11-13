Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-4: engineer for DAEO-ozyt (W2-157), profile STANDARD, class C2: the reopened fix (a hanging unit test)

You are a fresh engineer for ticket DAEO-ozyt (W2-157: the GPU backstop, `gov resources --backstop <pgid>...`). The
code is built, reviewed and merged with w2/integrate (head 13ab2c9fe of w2/W2-157). The owner reopened the ticket for
one fix (DEC-1144 (2), P1-B (a)): read the ticket's last section "Reopened for one fix" first. You make that fix and
nothing else. No KPI line changes; you never read or change `tests/acceptance/` (an independent test designer's; it
runs `gov` as a subprocess with its own timeouts and is not touched by this fix).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157 |
| branch | w2/W2-157 |
| your allowed paths | src/gov/resources/backstop.py, tests/unit/resources/test_w2_157*, docs/changes/W2-157-evidence.md (command.py and config.py are in the ticket's paths but this fix does not need them) |
| the ticket (S4: "when every named group has ended on its own, the watch logs it and ends") | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| the code | src/gov/resources/backstop.py (`_live`, `watch`) |
| the unit tests | tests/unit/resources/test_w2_157_backstop.py (the `Rig` class, the `rig` fixture, about 45 calls of `backstop.watch`) |
| the readings L1-L9 as applied | docs/changes/W2-157-evidence.md |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The fault
`test_w2_157_backstop.py::test_s3_the_limit_comes_before_the_spill_before_the_embedder_before_the_log` hung two
merge-queue runs (1 h 45 min, then 77 min). The test replaces the backstop's sleep, then calls `watch()` on planted
process groups; a call that does not trip polls forever (a busy loop), because a group whose members are all zombies
(the planted child exited but pytest has not reaped it) or paused still passes `os.killpg(g, 0)` in `_live`.

The lead's reading of why that test's fourth call may never trip (check it; do not take it on trust): the replaced
sleep is `lambda s: log.write_text("offloaded 1/2 layers to GPU\n")`, which overwrites the log with the same 28
bytes each time. If any earlier call in the same test slept once (under load: the stand-in `nvidia-smi` or the
stand-in `/api/ps` server answering late, 3 s `PS_TIMEOUT_S`, so the first poll found no reason), the log already
holds those 28 bytes when the fourth call starts, its offset starts at 28, every later write keeps the size at 28, and
`_partial_offload` never sees a new line. Then the planted job (`sleep(120)`) ends after 120 s, stays an unreaped
zombie, its group still answers signal 0, and `watch()` spins for ever.

## The fix (all three; the ticket's last section)
1. **A group whose live members are all zombies counts as ended.** In `backstop.py`, `_live(g)`: after
   `os.killpg(g, 0)` succeeds, read `/proc/<pid>/stat` of the processes whose process group (field 5) is `g`, and
   if every member found is a zombie (state `Z`, or `X` dead) the group has ended. Parse the state and pgrp after the
   last `)` (the command name may hold spaces or parentheses). Nothing by name, no `ps`, no pattern: group ids only.
   A paused member (`T`/`t`) is live. No `/proc` (or no member found though signal 0 succeeded) keeps today's answer
   (live). A process that vanishes while you read it is skipped. Keep `PermissionError` = live and
   `ProcessLookupError`/`OverflowError` = ended as now.
2. **`watch()` takes a bound.** A keyword-only argument (e.g. `max_polls: int | None = None`; or seconds — your
   choice, say which and why in the evidence), whose default (`None`) keeps the command's behaviour exactly
   (`command.py` calls `watch(args.backstop, root)` and is unchanged). When the bound is reached without a trip and
   with a group still live, the watch writes one log line naming it (e.g. `end: the bound of <n> polls reached; no
   trip`) and returns the result untripped. Check what the existing tests assert on the result's keys before you add
   a key; prefer adding none. Every unit test that calls `watch()` passes a bound (a small number fitting that test:
   the polls it needs plus a margin). A bound that cannot hang the run is the point: a test that needs more polls than
   its bound fails with a clear assertion, it never spins.
3. **Each test reaps the groups it plants.** The `rig` fixture already calls `close()` after `yield`; make the reaping
   certain: a `try`/`finally` so a failing test still kills (SIGCONT then SIGKILL to the group) and waits for every
   child it planted, including processes started outside `rig.job()` (e.g. the `other` same-name process in
   `test_s4_only_the_named_group_is_stopped_and_a_same_name_process_runs_on`, the `short_job` children, any `Popen`
   in a test body): register them with the rig, or reap them in the test's own `finally`.
4. **Make that test deterministic too**, inside its own assertions (no assertion weakened, the order limit, spill,
   embedder, log still proven): e.g. reset the log before each call, or have the replaced sleep append a new line
   rather than overwrite the same bytes, so the fourth call trips at its second poll whatever the earlier calls did.
   Look for the same overwrite-with-equal-size pattern in the other tests (`test_s3_a_partial_offload_line_...`,
   `test_s3_an_equal_offload_...`, `test_a_trip_without_a_reading_logs_none`) and fix it where it can bite.

Unit tests first, red on the present code, then the fix: at least (a) a group whose only member is an unreaped zombie
ends the watch untripped with the "every watched group has ended" line; (b) a group with a paused (SIGSTOP) member is
still live; (c) a group with a zombie and a live member is live; (d) `watch(..., max_polls=n)` on readings that never
trip returns untripped after exactly n polls (count the stand-in `nvidia-smi` calls) and logs the bound line;
(e) the default (no bound) still polls past a few polls (stop it with a group that ends, as
`test_s4_a_job_that_ends_first_ends_the_watch_without_a_trip` does).

## Proof (run each; put the outputs' summary lines in `evidence`)
Every pytest goes through the heavy-slot tool, with a TMPDIR outside the repository and outside ~/gov-os-runs:
`mkdir -p /tmp/w2-157-eng4` once, then each run as
`env TMPDIR=/tmp/w2-157-eng4 HOME=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-157/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(pytest-randomly is not installed, so no `-p no:randomly`).
1. The backstop file 20 times in a row, each run under `timeout 120` (a shell loop in a script file under
   /tmp/w2-157-eng4, `timeout 120 env ... bash heavy_slot.sh python3 -m pytest tests/unit/resources/test_w2_157_backstop.py ...`),
   recording each run's exit code and summary line; none may hang (exit 124) or fail.
2. Then `tests/unit/resources` and `tests/acceptance/W2-157` and `tests/acceptance/W2-20` once each (the form above).
Check after every run that no planted process is left: no process of yours from the tests may outlive the run.

## Safety
Your unit tests plant their own process groups only (children started with `start_new_session=True` or `setsid`) and
stand-ins under `tmp_path`; never signal a process you did not start; never run `--backstop` against a real group, the
real GPU or the real HOME's gate.json. A hang you meet is stopped by its pid (`kill <pid>`), never by a name match
(`pkill`, `killall` are refused).

## Rules
- Add to `docs/changes/W2-157-evidence.md` one short section "Reopened fix (DEC-1144 (2))": the cause, the three
  changes as applied (the zombie rule, the bound's name and default, the reaping), the unit tests, and the 20-run
  proof's line.
- Anything longer than one line goes in a script file under /tmp/w2-157-eng4, run with `bash <file>`. Literal paths
  only. No merge, no push, no edit outside your paths. A refused call is reported, never worked around; refused twice
  for the same action, stop and say so. For a new file, `git add <path>` before `git commit -- <paths>`.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: engineer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1073" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the 20 runs' exit codes and summary lines; the pytest summary lines of
tests/unit/resources, tests/acceptance/W2-157 and tests/acceptance/W2-20) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

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
