{
  "ticket": "DAEO-8a3f",
  "ticket_text": "---\nid: DAEO-8a3f\nstatus: in_progress\ndeps: []\nlinks: [DAEO-neam, DAEO-q7lk]\ncreated: 2026-11-11T01:20:17Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-158\ntags: [wave-2, implementation, standard, after-the-lift, check]\nwbs_id: W2-158\ntitle: 'gov check --structural: one cheap, bounded pass over the declared check families and the new links on a head, a notice and never a refusal (EMERGENCY-TOOLS-1 D9; DEC-1052 R1-21, INVESTIGATION-1 T-2)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/check/structural.py\n- src/gov/check/command.py  # the one option, --structural\n- tests/unit/check/test_w2_158*\n- docs/changes/W2-158-evidence.md\nreads:\n- src/gov/check/**\n- src/gov/cli/checks.py\n- src/gov/links/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/check/command.py\nwaits_on:\n- ref: DAEO-q7lk\n  reason: 'the links line of S4 calls `gov links --since <base>` (W2-129); this ticket skips that line while `gov links` is absent'\nkpis:\n  success:\n  - 'S1 `gov check --structural` runs, each in a process of its own, all at once and each within a time bound (default 50 seconds, `--timeout` to change it), the tree''s declared checks of these families: schema, graph, claims, mutation, authority, pathmap, audit and skills; each command is the tree''s own declaration (template/governance/kernel/checks/<id>.yaml, else governance/kernel/checks/<id>.yaml). Verify: a planted tree with a declaration per family: eight processes started, one line per family; a stand-in command that sleeps past the bound is killed at the bound [DEC-1052, INVESTIGATION-1 T-2]'\n  - 'S2 It prints one line per family: `<family>: ok`, `<family>: ok (not applicable: <reason>)`, `<family>: skipped (<reason>)` or `<family>: NOTICE <what it found, its first lines>`, then one last line `structural pass at <head12> ...`; a family that timed out is a NOTICE reading \"not measured\", never ok and never red. Verify: planted checks that pass, find a problem, are not applicable and time out: each reads as stated [DEC-1052, INVESTIGATION-1 T-2]'\n  - 'S3 It exits 0 whatever the checks find, and 2 only when it could not run at all (no such folder, not a git work tree, bad arguments); no commit, close, landing or launch refuses or waits on its result (a landing may call it after the fact and log its lines, as the CTO''s `land.py` does). Verify: a planted failing check gives exit 0 and a NOTICE; a folder that is no work tree gives exit 2; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal [DEC-1052, DEC-1073]'\n  - 'S4 With a `<base>`: the portability family runs only when `<base>..HEAD` touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when `<base>` does not resolve (otherwise it reads \"skipped (no such change)\"), and the tree''s own `gov links --since <base>` runs after the others, as `links: ok (0 new since <base>, M standing)` or `links: NOTICE N new: <the first finding lines>`; it writes only links'' own mark. Without a `<base>` both are left out, named. Verify: planted history with and without a kernel change; a planted tree with and without `src/gov/links/` [DEC-1052, DEC-1073]'\n  - 'S5 It is bounded and cheap: the whole pass on this repository''s main tree ends within the time bound plus 10 seconds, and it reads and writes nothing else (a filesystem-spy test over a planted tree: only the declared checks'' own outputs and links'' mark). Verify: the measured time on this repository, recorded in docs/changes/W2-158-evidence.md [DEC-1052]'\n  failure:\n  - 'A refusal, a non-zero exit or a blocked commit, close, landing or launch because of what it found. Verify: S3''s planted failing check: exit 0 and a NOTICE line; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal'\n  - 'A family that timed out reading ok or red. Verify: S1''s stand-in command that sleeps past the bound and S2''s timed-out planted check: the family''s line reads NOTICE \"not measured\"; a line reading ok, or a red result, is this failure'\n  - 'A check run that is not the tree''s own declaration. Verify: a planted tree whose declaration for one family holds a marker command: the marker runs and no command from a built-in list does; a planted tree with no declaration for a family reads that family as skipped'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1052\n- DEC-1073\n- DEC-1119\n- DEC-1109\n- DAEO-q7lk  # W2-129\n- DAEO-neam  # W2-45\nest_loc: 200\nacceptance_tests:\n  path: tests/acceptance/W2-158/\n  author: 'independent-test-designer (MR-3), from these KPI lines; planted trees with declared checks and planted histories, never this repository''s tickets'\ntrack: C\nlist_rows: []\n---\n# W2-158 gov check --structural\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 row D9; **after the lift**, not before EXAMIN's copy (\u00a71 D9 \"no\").\n\n- **Problem.** The CTO's `structural_pass.py` (`.gov-runtime/scratch/orchestrator/tools/structural_pass.py`, R1-21, DEC-1052) gives a cheap notice-only pass over the check families after every record commit and every landing. Its own docstring says \"later replaced by T-2's `--families`\", but no ticket holds T-2's scoped check: W2-45 (runner semantics) lists no scoped or notice-only run, and `gov check` has only `--list`. An adopted product has the 17 families and no cheap way to run them after a commit.\n- **Approach.** A module that reads the declarations the runner already reads, starts each in its own process with a bound, and prints the notice lines. It reuses the declarations; it adds no check. Alternatives: `gov check --changed <base>` with input globs per check (INVESTIGATION-1 T-2's full design, left to W2-45 or a later ticket); a wrapper script in the template (rejected: scratch tools are the problem this audit names).\n- **Interface.** `gov check --structural [<base>] [--timeout <s>]`; the output lines as S2; exit codes as S3.\n- **Non-goals.** No new check, no scoping by input globs, no gate; W2-45's runner semantics are untouched.\n- **Rabbit holes.** Making a notice a refusal (never, DEC-1052); running the checks in sequence (one process each, all at once, is the measured speed).\n\n[DEC-1052, DEC-1073, DEC-1119 (5)]\n",
  "authority": [
    {
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
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
      "id": "DAEO-q7lk",
      "sha256": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "reason": "declared in sources",
      "tokens": 3919
    },
    {
      "id": "DAEO-neam",
      "sha256": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "authority": "task",
      "lifecycle": "open",
      "constraint": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "reason": "declared in sources",
      "tokens": 812
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
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
      "id": "DAEO-q7lk",
      "sha256": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "reason": "declared in sources",
      "tokens": 3919
    },
    {
      "id": "DAEO-neam",
      "sha256": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "authority": "task",
      "lifecycle": "open",
      "constraint": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "reason": "declared in sources",
      "tokens": 812
    }
  ],
  "supplementary": [
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
      "id": "DAEO-ozyt",
      "path": ".tickets/DAEO-ozyt.md",
      "text": "  - 'S4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument \"abc\"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]'\n  - 'S5 It changes nothing else: it only reads the GPU, the servers'' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]'\n  failure:\n  - 'A process outside the named groups paused or signalled. Verify: S4''s planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure'\n",
      "tokens": 269
    },
    {
      "id": "1bb7395b046294dd36c9248b",
      "path": "governance/project/orchestration/START-NEXT-SESSION.md",
      "text": "  412a4e37 started it, its pid and log are in CHECKPOINT's RESUME HERE. Run: `governance/project/orchestration/nightly/nightly.sh`\n  (day mode, a fresh clone of the head, ~5 h), then the `lifted` suite once, report-only (D4-LIST \u00a72). **No commits on\n  w2/integrate during it.** Then: **triage the reds by group for the owner** (re-run each alone; P1-NIGHTLY-2026-11-02\n  as the old map); fixes by role under RUBRIC-2; a second run.\n- **Done today (11-10 afternoon):** ACT-W2-149-INSTALL-1 `baac0b2c2` (by hand); ACT-DEADMAN-WAKE-1 `905b82a3b`,\n  ACT-CLAUDE-COPIES-3 `a4e703580` (agent); the portability family 204/0; W1-08 merged `34b7815f9`; the ticket template\n  1.0.1 approved (DEC-1121, DEC-1122) and merged; DEC-1119's rubric found then replaced by RUBRIC-2; EMERGENCY-TOOLS-1.\n- **In flight at handover:** ACT-PATHMAP-NS-2 by the owner's operator (fixes `core-pathmap`: the install left\n  `governance/project/indep-briefs/**` without a namespace); ACT-EFFORT-HIGH-2 queued for the agent at 17:33 (the owner's yes just before).\n  Check both landed (`git log`, `~/gov-os-operator/log/operator.jsonl`); landing check after each.\n",
      "tokens": 283
    },
    {
      "id": "DAEO-6lid",
      "path": ".tickets/DAEO-6lid.md",
      "text": "---\nid: DAEO-6lid\nstatus: in_progress\ndeps: []\nlinks: [DAEO-cb2b, DAEO-fd0p]\ncreated: 2026-11-11T01:20:18Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-159\ntags: [wave-2, implementation, standard, after-the-lift, orchestration, hooks]\nwbs_id: W2-159\ntitle: 'The orchestrator''s two Stop checks in the product: a turn does not end with the inbox waiter unarmed, nor idle while unblocked work remains, each a reminder blocking at most once a turn (EMERGENCY-TOOLS-1 A8, A9; DEC-1027 E, DEC-1110 (1))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/session_watch/**\n- src/gov/check/commands.py  # the one line that records `session-watch` (the precedent: W2-20's `resources`)\n- src/gov/cli/main.py  # P-W2-159-1 (a): a hyphenated command maps to its underscore folder (about 4 lines; the CTO, 2026-11-12 08:22)\n- tests/unit/session_watch/**\n- docs/changes/W2-159-evidence.md\nreads:\n- src/gov/dispatch/**\n- src/gov/plan/**\n- governance/project/orchestration/tools/stop_waiter_check.py\n- governance/project/orchestration/tools/stop_idle_check.py\nneeds:\n- src/gov/check/commands.py\nwaits_on:\n- ref: DAEO-cb2b\n",
      "tokens": 294
    }
  ],
  "supplementary_query": "gov check --structural: one cheap, bounded pass over the declared check families and the new links on a head, a notice and never a refusal (EMERGENCY-TOOLS-1 D9; DEC-1052 R1-21, INVESTIGATION-1 T-2)\nS1 `gov check --structural` runs, each in a process of its own, all at once and each within a time bound (default 50 seconds, `--timeout` to change it), the tree's declared checks of these families: schema, graph, claims, mutation, authority, pathmap, audit and skills; each command is the tree's own declaration (template/governance/kernel/checks/<id>.yaml, else governance/kernel/checks/<id>.yaml). Verify: a planted tree with a declaration per family: eight processes started, one line per family; a stand-in command that sleeps past the bound is killed at the bound [DEC-1052, INVESTIGATION-1 T-2]\nS2 It prints one line per family: `<family>: ok`, `<family>: ok (not applicable: <reason>)`, `<family>: skipped (<reason>)` or `<family>: NOTICE <what it found, its first lines>`, then one last line `structural pass at <head12> ...`; a family that timed out is a NOTICE reading \"not measured\", never ok and never red. Verify: planted checks that pass, find a problem, are not applicable and time out: each reads as stated [DEC-1052, INVESTIGATION-1 T-2]\nS3 It exits 0 whatever the checks find, and 2 only when it could not run at all (no such folder, not a git work tree, bad arguments); no commit, close, landing or launch refuses or waits on its result (a landing may call it after the fact and log its lines, as the CTO's `land.py` does). Verify: a planted failing check gives exit 0 and a NOTICE; a folder that is no work tree gives exit 2; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal [DEC-1052, DEC-1073]\nS4 With a `<base>`: the portability family runs only when `<base>..HEAD` touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when `<base>` does not resolve (otherwise it reads \"skipped (no such change)\"), and the tree's own `gov links --since <base>` runs after the others, as `links: ok (0 new since <base>, M standing)` or `links: NOTICE N new: <the first finding lines>`; it writes only links' own mark. Without a `<base>` both are left out, named. Verify: planted history with and without a kernel change; a planted tree with and without `src/gov/links/` [DEC-1052, DEC-1073]\nS5 It is bounded and cheap: the whole pass on this repository's main tree ends within the time bound plus 10 seconds, and it reads and writes nothing else (a filesystem-spy test over a planted tree: only the declared checks' own outputs and links' mark). Verify: the measured time on this repository, recorded in docs/changes/W2-158-evidence.md [DEC-1052]\nA refusal, a non-zero exit or a blocked commit, close, landing or launch because of what it found. Verify: S3's planted failing check: exit 0 and a NOTICE line; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal\nA family that timed out reading ok or red. Verify: S1's stand-in command that sleeps past the bound and S2's timed-out planted check: the family's line reads NOTICE \"not measured\"; a line reading ok, or a red result, is this failure\nA check run that is not the tree's own declaration. Verify: a planted tree whose declaration for one family holds a marker command: the marker runs and no command from a built-in list does; a planted tree with no declaration for a family reads that family as skipped\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "DAEO-fd0p",
      "path": ".tickets/DAEO-fd0p.md"
    },
    {
      "id": "DAEO-ozyt",
      "path": ".tickets/DAEO-ozyt.md"
    },
    {
      "id": "DAEO-ylsh",
      "path": ".tickets/DAEO-ylsh.md"
    },
    {
      "id": "DAEO-6lid",
      "path": ".tickets/DAEO-6lid.md"
    },
    {
      "id": "5ee67db475a7425d3597b0a2",
      "path": "governance/project/orchestration/START-NEXT-SESSION.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "DAEO-fd0p",
          "path": ".tickets/DAEO-fd0p.md"
        },
        {
          "id": "DAEO-o5x1",
          "path": ".tickets/DAEO-o5x1.md"
        },
        {
          "id": "DAEO-ozyt",
          "path": ".tickets/DAEO-ozyt.md"
        },
        {
          "id": "1bb7395b046294dd36c9248b",
          "path": "governance/project/orchestration/START-NEXT-SESSION.md"
        },
        {
          "id": "DAEO-6lid",
          "path": ".tickets/DAEO-6lid.md"
        },
        {
          "id": "DAEO-fd0p",
          "path": ".tickets/DAEO-fd0p.md"
        },
        {
          "id": "DAEO-ozyt",
          "path": ".tickets/DAEO-ozyt.md"
        },
        {
          "id": "DAEO-ylsh",
          "path": ".tickets/DAEO-ylsh.md"
        },
        {
          "id": "DAEO-6lid",
          "path": ".tickets/DAEO-6lid.md"
        },
        {
          "id": "5ee67db475a7425d3597b0a2",
          "path": "governance/project/orchestration/START-NEXT-SESSION.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "5ee67db475a7425d3597b0a2",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-6lid",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-fd0p",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-ozyt",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-ylsh",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-8a3f): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 11858,
  "budget": {
    "limit": 12000,
    "used": 11858
  },
  "left_out": {
    "count": 8,
    "superseded": [
      "DEC-038",
      "DEC-045",
      "DEC-047",
      "DEC-048",
      "DEC-049",
      "DEC-636",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "d577e69de01edeab9ac562813c791cbd78e38bdde622d28bbf7d830f90d3438a"
}
