{
  "ticket": "DAEO-ozyt",
  "ticket_text": "---\nid: DAEO-ozyt\nstatus: in_progress\ndeps: [DAEO-r30l]\nlinks: [DAEO-r30l, DAEO-5emz]\ncreated: 2026-11-11T01:20:16Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-157\ntags: [wave-2, implementation, standard, after-the-lift, gpu, capacity]\nwbs_id: W2-157\ntitle: 'The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills into shared memory, or an embedder is not wholly on the GPU (EMERGENCY-TOOLS-1 D12; DEC-1067, DEC-1068 (4))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-r30l\nallowed_paths:\n- src/gov/resources/backstop.py\n- src/gov/resources/command.py  # the one option, --backstop\n- src/gov/resources/config.py  # the one new value, gpu_backstop_limit_mib\n- tests/unit/resources/test_w2_157*\n- docs/changes/W2-157-evidence.md\nreads:\n- src/gov/resources/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/resources/command.py\n- src/gov/resources/config.py\nwaits_on:\n- ref: DAEO-r30l\n  reason: 'W2-20 owns src/gov/resources/** and its gate configuration; this ticket adds one module and one value after it merges'\nkpis:\n  success:\n  - 'S1 `gov resources --backstop <pgid> [<pgid> ...]` watches the named process groups and, every 5 seconds (a configured value), pauses every live named group with SIGSTOP at once when GPU memory used is above the configured limit (`gpu_backstop_limit_mib` in the gate''s one configuration file, dated and sourced; this machine''s value 15,872 MiB, 15.5 GiB); a missing or malformed limit refuses to start, naming it. Verify: a stand-in `nvidia-smi` printing 15,800 then 15,900 MiB and a stand-in job in its own process group: the job is running at the first reading, stopped at the second, the trip logged with the reading [DEC-1067 (GPU safety), DEC-1068 (4)]'\n  - 'S2 A spill into shared GPU memory trips it too: GPU memory used within 64 MiB of the card''s total. Verify: a stand-in reading of total minus 63 MiB trips it and total minus 65 MiB does not [DEC-1067 (GPU safety), DEC-1068 (4)]'\n  - 'S3 An embedder not wholly on the GPU trips it: a model of an embedding server (the ports from the gate''s configuration) whose `size_vram` is below its `size`, or a line \"offloaded N/M layers to GPU\" with N below M in the server''s log written since the watch started. Verify: a stand-in server answering both forms, each tripping it once, and a line with N equal to M not tripping it [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030]'\n  - 'S4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument \"abc\"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]'\n  - 'S5 It changes nothing else: it only reads the GPU, the servers'' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]'\n  failure:\n  - 'A process outside the named groups paused or signalled. Verify: S4''s planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure'\n  - 'A trip on a reading under every limit, or a spill, an embedder partly on the CPU or a partial offload not tripping it. Verify: S1''s stand-in readings (15,800 MiB no trip), S2''s (total minus 65 MiB no trip, total minus 63 MiB trip) and S3''s stand-in server (N equal to M no trip; `size_vram` below `size` and N below M each trip): each reading gives the stated outcome'\n  - 'A limit taken from anywhere but the gate''s configuration file. Verify: a planted configuration with a limit differing from the built-in value (and an environment variable and a command-line argument holding a third value): the trip happens at the file''s value only; a planted file with the limit missing or malformed refuses to start and names it'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1067\n- DEC-1068\n- DEC-1030\n- DEC-1073\n- DEC-1119\n- DEC-1109\n- DAEO-r30l  # W2-20\nest_loc: 160\nacceptance_tests:\n  path: tests/acceptance/W2-157/\n  author: 'independent-test-designer (MR-3), from these KPI lines; a stand-in nvidia-smi, a stand-in embedding server and planted process groups, never the real GPU or the shared servers'\ntrack: A\nlist_rows: []\n---\n# W2-157 The GPU backstop in the product\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 row D12; **after the lift**, **before EXAMIN's copy** (\u00a71 D12 \"yes, GPU safety\"; the copy shares this machine's GPU).\n\n- **Problem.** The CTO's `gpu_backstop.sh` (`.gov-runtime/scratch/orchestrator/tools/gpu_backstop.sh`, DEC-1067 (GPU safety), DEC-1068 (4)) pauses a GPU job on a memory limit, a spill or a partial offload. It is a scratch tool. W2-20's gate refuses a start that lacks GPU room and stops the largest heavy job below a memory floor; neither watches a GPU job while it runs, and EMERGENCY-TOOLS-1 \u00a73 retires the tool only once the product covers a spill. W2-137 S5 already names \"the GPU backstop armed\" as a step of its measure.\n- **Approach.** One module beside W2-20's gate, started with `--backstop` and the job's process groups. Same triggers and the same pause as the script; the limit moves into the gate's configuration file. Alternative: fold it into W2-20's trip-wire (rejected: W2-20 is merged or in review and its trip-wire is on system memory, not the GPU).\n- **Interface.** `gov resources --backstop <pgid>...`; the limit `gpu_backstop_limit_mib`; the poll period `gpu_backstop_every_s`. The inbox is the project's inbox folder (as W2-156's).\n- **Non-goals.** No kill (a pause only; the owner or the CTO resumes or stops); no GPU scheduling (W2-20 S-lines on GPU shares); no change to the shared servers.\n- **Rabbit holes.** Matching processes by name or `ps | grep` (the groups are named, nothing else); reading Windows' shared-usage counter (WSL cannot; the total-minus-64 MiB sign stands).\n\n[DEC-1067 (GPU safety), DEC-1068 (4), DEC-1119 (5)]\n",
  "authority": [
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
  "supplementary": [
    {
      "id": "DAEO-8a3f",
      "path": ".tickets/DAEO-8a3f.md",
      "text": "  - 'S4 With a `<base>`: the portability family runs only when `<base>..HEAD` touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when `<base>` does not resolve (otherwise it reads \"skipped (no such change)\"), and the tree''s own `gov links --since <base>` runs after the others, as `links: ok (0 new since <base>, M standing)` or `links: NOTICE N new: <the first finding lines>`; it writes only links'' own mark. Without a `<base>` both are left out, named. Verify: planted history with and without a kernel change; a planted tree with and without `src/gov/links/` [DEC-1052, DEC-1073]'\n  - 'S5 It is bounded and cheap: the whole pass on this repository''s main tree ends within the time bound plus 10 seconds, and it reads and writes nothing else (a filesystem-spy test over a planted tree: only the declared checks'' own outputs and links'' mark). Verify: the measured time on this repository, recorded in docs/changes/W2-158-evidence.md [DEC-1052]'\n  failure:\n",
      "tokens": 248
    },
    {
      "id": "DAEO-fd0p",
      "path": ".tickets/DAEO-fd0p.md",
      "text": "  - 'S4 The helper watch reads names, timestamps and error codes only, never a message''s text; it matches no process by name; it writes only the inbox, its own state file and its own log; only transcripts whose last entry is inside a window (default 24 hours) are looked at. Verify: a filesystem-spy and a text-canary test: a planted message text never appears in an item or the log; a search of the module for a process-name match finds none [DEC-1112 (3), DEC-1073 (4), DEC-495]'\n  failure:\n  - 'A wait that outlives its bound, or that waits for a job whose process is gone. Verify: S1''s never-written exit file at `<max-s>` 1 returns exit 124 within the bound, and S2''s killed stand-in job returns exit 125 within one poll period with a same-name process still running'\n  - 'A process matched by name, or a message''s text copied into an item or a log. Verify: S4''s text-canary test (the planted message text found 0 times in items and log) and its search of the module for a process-name match (none found)'\n",
      "tokens": 254
    },
    {
      "id": "DAEO-o5x1",
      "path": ".tickets/DAEO-o5x1.md",
      "text": "  - 'S9 Dependency fields (DEC-1088 (3)): a ticket created on or after facts.yaml ready.new_since without reads:, needs: or waits_on: is refused by name (READS_MISSING, NEEDS_MISSING, WAITS_ON_MISSING; an empty list is a declared none); each waits_on id or record path must exist (WAITS_ON_UNKNOWN <ref>); a ticket created before the date is not refused for them. Verify: the ready check on planted tickets either side of the date [DEC-1088, DEC-1052]'\n  - 'S10 facts.yaml gains ready.new_since (an ISO date, the day this ticket lands) and the schema declares it; W2-128''s acceptance cases still pass. Verify: the schema test and gov accept W2-128 [DEC-1050]'\n  failure:\n  - 'Two runs of gov brief on the same inputs differ (TPL-3 F1).'\n  - 'The ready check refuses a ticket for an advisory item, or lets a ticket missing a required field through as READY (TPL-5 F1, as DEC-1083 amends it).'\n  - 'gov brief writes any file, or reads anything beyond the ticket file, facts.yaml, the kernel templates and the --part/--repair files (a filesystem-spy test).'\nprofile: STANDARD\nsources:\n- DEC-1050\n- DEC-1052\n- DEC-1083\n- DEC-1088\n- DEC-1112\n- DEC-1109\nest_loc: 380\nacceptance_tests:\n",
      "tokens": 295
    },
    {
      "id": "00c917af3a35b90204c0dd51",
      "path": "docs/probes/DAEO-0z8c/PR-DAEO-0z8c-r7.md",
      "text": "- Reversed by: a run in which, with an inherited index and a logging git first on `PATH`, that git logs nothing.\n\n**F5 (S1): pinning can open the retrieve filter where the repository has another owner.**\n- What was done: `role_paths` now reads no global config, so a person's `safe.directory` in `~/.gitconfig` no longer applies.\n- What happened: for a tree owned by another user, git would refuse with \"dubious ownership\". `changed` and `engineer_side` would then return None, and `gov retrieve` would hand the test designer the engineer's files, where the old environment let git answer. This is reasoned from git's rule that `safe.directory` is read only from the system, global and command-line config. I did not reproduce it: no second owner is possible in the sandbox.\n- Ordinary work: no, because on this machine one uid owns every tree (the last probe's finding).\n- Consequence: fails open.\n- Scope: in.\n- Reversed by: git answering in such a tree under `GIT_CONFIG_GLOBAL=/dev/null`, or the filter refusing on None.\n\n**F6 (S2, S3, F1): `gov accept` reports three passing lines as fail.**\n",
      "tokens": 275
    },
    {
      "id": "c365105fe6bba6c953b5cb09",
      "path": "tests/acceptance/W2-20/README.md",
      "text": "## Round 2's changes (2026-11-09)\n\n| Change | Point | Cases | Commit |\n|---|---|---|---|\n| new file: S21's cases | the F2 line (DEC-1088 (5)(b)) | 9 cases in `test_w2_20_plan_source.py` | `cc88ceeea` |\n| support: every planted file carries a dated `rebuild_peak_bytes` | P-5 (a) | none changed in what it asserts | `a8575eda6` |\n| new case: the rebuild peak from rebuild slot holders, no verification lock | P-5 (a) | `test_w2_20_remeasure.py::test_s7_s9_...` | `3418453fc` |\n| new cases: `--init-config` writes the template, never overwrites | P-3 (a) | 2 in `test_w2_20_config.py` | `cc2f14f42` |\n| new cases: a full set of slots never refuses a launch; an unreadable `heavy_slots` does; docstring notes P-1 (a) and P-2 | P-1 (a), P-2 (a)+(c) | 6 in `test_w2_20_launch.py` | `1562a461e` |\n| none: the override already a launch option logged to `launch.log` and stderr | P-1 (a) | round 1's four override and command-line cases, unchanged | \u2014 |\n| none: the measured case already uses time-bound programs | P-4 | S16's case, unchanged | \u2014 |\n| none: no `nvidia-smi` without a declared need; once with one | P-6 | round 1's S10/S13 cases, unchanged | \u2014 |\n\n",
      "tokens": 289
    },
    {
      "id": "DAEO-6lid",
      "path": ".tickets/DAEO-6lid.md",
      "text": "---\nid: DAEO-6lid\nstatus: open\ndeps: []\nlinks: [DAEO-cb2b, DAEO-fd0p]\ncreated: 2026-11-11T01:20:18Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-159\ntags: [wave-2, implementation, standard, after-the-lift, orchestration, hooks]\nwbs_id: W2-159\ntitle: 'The orchestrator''s two Stop checks in the product: a turn does not end with the inbox waiter unarmed, nor idle while unblocked work remains, each a reminder blocking at most once a turn (EMERGENCY-TOOLS-1 A8, A9; DEC-1027 E, DEC-1110 (1))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/session_watch/**\n- src/gov/check/commands.py  # the one line that records `session-watch` (the precedent: W2-20's `resources`)\n- tests/unit/session_watch/**\n- docs/changes/W2-159-evidence.md\nreads:\n- src/gov/dispatch/**\n- src/gov/plan/**\n- governance/project/orchestration/tools/stop_waiter_check.py\n- governance/project/orchestration/tools/stop_idle_check.py\nneeds:\n- src/gov/check/commands.py\nwaits_on:\n- ref: DAEO-cb2b\n  reason: 'S2''s open items and S1''s waiter name come from the dispatcher''s inbox and ready list (W2-121); until it lands the check reads a configured file'\nkpis:\n",
      "tokens": 300
    },
    {
      "id": "7a821fa6f5ee5bbd8178f975",
      "path": "governance/project/bootstrap.md",
      "text": "**What a session writes now** (for the orchestration skill): a search from the project root always names a folder below it or a glob for the files meant (`path: src`, `glob: '*.py'`, `grep -rn <word> src tests`, `rg <word> src`, `find src \u2026` or `find . -name \u2026`, `ls -R src`); a type filter alone is not enough (`rg -t py <word>` is refused; `-g '*.py'` is the way). Inline JSON or scripts with many brace groups go into a file; no digit word stands directly before a redirect in a search.\n\n**The harness's hook time limit** was not measured and this repository's configured limit is not known; by DEC-110 and DEC-179 a hook that passes its limit lets the call through. The rule's own decision stays under 0.4 s for every input the probe found slow.\n\n**Residuals** (the suite's README carries them as 31 to 51):\n\n- What a command-line guard cannot see: a search whose command, keyword, prefix or path is made at run time (a variable, a substitution, `eval`, an alias or a function); a brace word made past the bound by a variable or `eval`, and a sequence such as `{1..1000}`.\n",
      "tokens": 270
    },
    {
      "id": "DAEO-6lid",
      "path": ".tickets/DAEO-6lid.md",
      "text": "# W2-159 The orchestrator's two Stop checks\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 rows A8 and A9; **after the lift**, not before EXAMIN's copy.\n\n- **Problem.** This repository's CTO has two Stop-hook reminders (`governance/project/orchestration/tools/stop_waiter_check.py`, `stop_idle_check.py`; registered in the untracked `.claude/settings.local.json`, EMERGENCY-TOOLS-1 \u00a74.1). They keep a turn from ending while the inbox waiter is unarmed (DEC-1027) and while unblocked work remains with nothing running (DEC-1110 (1)). An adopted product's orchestrator has neither. The idle check also reads this repository's DECIDED-NOT-DONE tables, so it cannot be copied as it is.\n- **Approach.** One module, two checks, one state and log; the open items and the waiter come from the project's configuration, defaulting to W2-121's dispatcher. Alternative: copy the two scripts into the kernel template (rejected: the idle check names this repository's file; a kernel change needs its CIT-P).\n",
      "tokens": 267
    },
    {
      "id": "DAEO-8a3f",
      "path": ".tickets/DAEO-8a3f.md",
      "text": "---\nid: DAEO-8a3f\nstatus: open\ndeps: []\nlinks: [DAEO-neam, DAEO-q7lk]\ncreated: 2026-11-11T01:20:17Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-158\ntags: [wave-2, implementation, standard, after-the-lift, check]\nwbs_id: W2-158\ntitle: 'gov check --structural: one cheap, bounded pass over the declared check families and the new links on a head, a notice and never a refusal (EMERGENCY-TOOLS-1 D9; DEC-1052 R1-21, INVESTIGATION-1 T-2)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/check/structural.py\n- src/gov/check/command.py  # the one option, --structural\n- tests/unit/check/test_w2_158*\n- docs/changes/W2-158-evidence.md\nreads:\n- src/gov/check/**\n- src/gov/cli/checks.py\n- src/gov/links/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/check/command.py\nwaits_on:\n- ref: DAEO-q7lk\n  reason: 'the links line of S4 calls `gov links --since <base>` (W2-129); this ticket skips that line while `gov links` is absent'\nkpis:\n  success:\n",
      "tokens": 261
    },
    {
      "id": "DAEO-fd0p",
      "path": ".tickets/DAEO-fd0p.md",
      "text": "---\nid: DAEO-fd0p\nstatus: open\ndeps: []\nlinks: [DAEO-wnnz, DAEO-t8mp, DAEO-6lid]\ncreated: 2026-11-11T01:20:19Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-160\ntags: [wave-2, implementation, standard, after-the-lift, orchestration, launch]\nwbs_id: W2-160\ntitle: 'gov wait and the helper watch in the product: a bounded wait on a job''s exit file by pid, and an inbox item when a helper or a launched worker dies or goes silent (EMERGENCY-TOOLS-1 D3, D17; DEC-1079, DEC-1112 (3), DEC-1073 (4))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/wait/**\n- src/gov/session_watch/helper_watch.py\n- src/gov/check/commands.py  # the one line that records `wait` (the precedent: W2-20's `resources`)\n- tests/unit/wait/**\n- tests/unit/session_watch/test_w2_160*\n- docs/changes/W2-160-evidence.md\nreads:\n- src/gov/launch/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/check/commands.py\nwaits_on:\n- ref: DAEO-6lid\n  reason: 'W2-159 creates src/gov/session_watch/; the helper watch is one more module there'\nkpis:\n  success:\n",
      "tokens": 280
    },
    {
      "id": "DAEO-ylsh",
      "path": ".tickets/DAEO-ylsh.md",
      "text": "---\nid: DAEO-ylsh\nstatus: open\ndeps: [DAEO-ecac, DAEO-r30l]\nlinks: [DAEO-ecac, DAEO-cv58]\ncreated: 2026-11-11T01:20:16Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-156\ntags: [wave-2, implementation, standard, after-the-lift, launch, spend]\nwbs_id: W2-156\ntitle: 'The runaway brake in the product: a ticket whose measured cost passes twice its projection holds its next launch and goes to the inbox once; usage stays record-only (EMERGENCY-TOOLS-1 D2; DEC-1091 (2), DEC-1119 (5))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-ecac\n- DAEO-r30l\nallowed_paths:\n- src/gov/spend/**\n- src/gov/launch/launcher.py  # the one call that refuses a braked ticket's launch, after the gate's call\n- src/gov/check/commands.py  # the one line that records `spend` (the precedent: W2-20's `resources`)\n- tests/unit/spend/**\n- tests/unit/launch/test_w2_156*\n- docs/changes/W2-156-evidence.md\nreads:\n- src/gov/launch/**\n- src/gov/telemetry/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n",
      "tokens": 262
    }
  ],
  "supplementary_query": "The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills into shared memory, or an embedder is not wholly on the GPU (EMERGENCY-TOOLS-1 D12; DEC-1067, DEC-1068 (4))\nS1 `gov resources --backstop <pgid> [<pgid> ...]` watches the named process groups and, every 5 seconds (a configured value), pauses every live named group with SIGSTOP at once when GPU memory used is above the configured limit (`gpu_backstop_limit_mib` in the gate's one configuration file, dated and sourced; this machine's value 15,872 MiB, 15.5 GiB); a missing or malformed limit refuses to start, naming it. Verify: a stand-in `nvidia-smi` printing 15,800 then 15,900 MiB and a stand-in job in its own process group: the job is running at the first reading, stopped at the second, the trip logged with the reading [DEC-1067 (GPU safety), DEC-1068 (4)]\nS2 A spill into shared GPU memory trips it too: GPU memory used within 64 MiB of the card's total. Verify: a stand-in reading of total minus 63 MiB trips it and total minus 65 MiB does not [DEC-1067 (GPU safety), DEC-1068 (4)]\nS3 An embedder not wholly on the GPU trips it: a model of an embedding server (the ports from the gate's configuration) whose `size_vram` is below its `size`, or a line \"offloaded N/M layers to GPU\" with N below M in the server's log written since the watch started. Verify: a stand-in server answering both forms, each tripping it once, and a line with N equal to M not tripping it [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030]\nS4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument \"abc\"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]\nS5 It changes nothing else: it only reads the GPU, the servers' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]\nA process outside the named groups paused or signalled. Verify: S4's planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure\nA trip on a reading under every limit, or a spill, an embedder partly on the CPU or a partial offload not tripping it. Verify: S1's stand-in readings (15,800 MiB no trip), S2's (total minus 65 MiB no trip, total minus 63 MiB trip) and S3's stand-in server (N equal to M no trip; `size_vram` below `size` and N below M each trip): each reading gives the stated outcome\nA limit taken from anywhere but the gate's configuration file. Verify: a planted configuration with a limit differing from the built-in value (and an environment variable and a command-line argument holding a third value): the trip happens at the file's value only; a planted file with the limit missing or malformed refuses to start and names it\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "bc04786225ba699aa31758fe",
      "path": "tests/acceptance/W1-13/README.md"
    },
    {
      "id": "DAEO-8a3f",
      "path": ".tickets/DAEO-8a3f.md"
    },
    {
      "id": "DAEO-fd0p",
      "path": ".tickets/DAEO-fd0p.md"
    },
    {
      "id": "DAEO-ylsh",
      "path": ".tickets/DAEO-ylsh.md"
    },
    {
      "id": "DEC-1125",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "DEC-889",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "2c1907f16bac7cb30b163599",
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md"
    },
    {
      "id": "5548467509b04b3d6b0eaab7",
      "path": "docs/assessment/2026-10/D-tool-staging.md"
    },
    {
      "id": "a44efd97cce794b1dd96bbc1",
      "path": "docs/assessment/2026-10/H-test-strategy.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "DAEO-8a3f",
          "path": ".tickets/DAEO-8a3f.md"
        },
        {
          "id": "DAEO-fd0p",
          "path": ".tickets/DAEO-fd0p.md"
        },
        {
          "id": "DAEO-o5x1",
          "path": ".tickets/DAEO-o5x1.md"
        },
        {
          "id": "00c917af3a35b90204c0dd51",
          "path": "docs/probes/DAEO-0z8c/PR-DAEO-0z8c-r7.md"
        },
        {
          "id": "c365105fe6bba6c953b5cb09",
          "path": "tests/acceptance/W2-20/README.md"
        },
        {
          "id": "DAEO-6lid",
          "path": ".tickets/DAEO-6lid.md"
        },
        {
          "id": "7a821fa6f5ee5bbd8178f975",
          "path": "governance/project/bootstrap.md"
        },
        {
          "id": "DAEO-6lid",
          "path": ".tickets/DAEO-6lid.md"
        },
        {
          "id": "DAEO-8a3f",
          "path": ".tickets/DAEO-8a3f.md"
        },
        {
          "id": "DAEO-fd0p",
          "path": ".tickets/DAEO-fd0p.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DAEO-ylsh",
          "path": ".tickets/DAEO-ylsh.md"
        },
        {
          "id": "bc04786225ba699aa31758fe",
          "path": "tests/acceptance/W1-13/README.md"
        },
        {
          "id": "DAEO-8a3f",
          "path": ".tickets/DAEO-8a3f.md"
        },
        {
          "id": "DAEO-fd0p",
          "path": ".tickets/DAEO-fd0p.md"
        },
        {
          "id": "DAEO-ylsh",
          "path": ".tickets/DAEO-ylsh.md"
        },
        {
          "id": "DEC-1125",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-889",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "2c1907f16bac7cb30b163599",
          "path": "docs/assessment/2026-10/A-purpose-roadmap.md"
        },
        {
          "id": "5548467509b04b3d6b0eaab7",
          "path": "docs/assessment/2026-10/D-tool-staging.md"
        },
        {
          "id": "a44efd97cce794b1dd96bbc1",
          "path": "docs/assessment/2026-10/H-test-strategy.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "2c1907f16bac7cb30b163599",
      "reason": "budget exceeded"
    },
    {
      "id": "5548467509b04b3d6b0eaab7",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-8a3f",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-fd0p",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-ylsh",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1125",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-889",
      "reason": "budget exceeded"
    },
    {
      "id": "a44efd97cce794b1dd96bbc1",
      "reason": "budget exceeded"
    },
    {
      "id": "bc04786225ba699aa31758fe",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-ozyt): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 11783,
  "budget": {
    "limit": 12000,
    "used": 11783
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-048",
      "DEC-798",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "00d3c40b4a15e50c474defa27ff699474ef8a9022a487f363ca01a95200588d9"
}
