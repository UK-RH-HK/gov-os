{
  "ticket": "DAEO-cb2b",
  "ticket_text": "---\nid: DAEO-cb2b\nstatus: in_progress\ndeps: [DAEO-r30l]\nlinks: [DAEO-zkr9, DAEO-r30l, DAEO-ts4y]\ncreated: 2026-11-01T20:10:00Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-121\ntags: [wave-2, implementation, dispatch, full]\nwbs_id: W2-121\ntitle: 'gov dispatch: one pass a minute keeps the machine full and the work moving without depending on any agent session: the ready list started when there is room for each job''s peak, returns into an inbox, approved landings as one batch, the true status (DEC-1007, DEC-1008)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nwaits_on: []\ndepends_on:\n- DAEO-r30l\nallowed_paths:\n- src/gov/dispatch/**\n- tests/unit/dispatch/**\nkpis:\n  success:\n  - '`gov dispatch tick` does one pass and exits; passes never overlap (a lock); an OFF file stops them; the host runs it every minute (cron or a service) and after a restart, outside any agent session; `gov dispatch status` prints the status Verify: a planted project: two `tick` calls started together run one pass (the second exits at the lock, writing nothing); a planted OFF file makes `tick` exit without starting anything; the host''s cron or service entry runs it every minute and after a restart (read from the installed entry, no agent session in its chain); `gov dispatch status` prints the status. [DEC-1007]'\n  - 'It starts at most one session per pass, staggered, and only an entry of the orchestrator''s ready list (the WBS order is the orchestrator''s, never the dispatcher''s), and only when the ticket''s claim is committed on the integration branch and in its worktree, the worktree clean, the brief complete, the ticket not running and with no unread return, and the gate (W2-20) and disk open; each skipped entry is named with its reason Verify: planted ready lists with several entries: one session starts per pass, staggered; an entry not on the orchestrator''s list is never started; entries with an uncommitted claim, an unclean worktree, an incomplete brief, a running ticket, an unread return, a shut gate or a full disk are each skipped and named with their reason. [DEC-1007, DEC-995, DEC-944 item 2]'\n  - 'Peaks, not the moment: from the history of each kind of job (a lead''s heavy steps, a rebuild, a close''s or the queue''s run, a full check) it keeps each kind''s measured peak (CPU and memory) and starts new work only when the machine has room for the new job''s peak plus the peaks still ahead for the work already running; the figures and their dates are in its status and refreshed from the history at least daily; its memory floor and working size are the gate''s (W2-20 S8 and S9), and memory admission stays W2-20''s S6 Verify: planted job histories for each kind of job: the status prints each kind''s peak (CPU and memory) with its date, refreshed from the history within a day; a start is refused when the room is under the new peak plus the peaks ahead and made when it is over; the memory floor and working size read are the gate''s. [DEC-1008] [re-worded, DEC-1084]'\n  - 'Every finished session''s return becomes one inbox item, once; a start that never ran becomes one inbox item; an item unread past a configured time raises an escalation the host''s notifier pushes to the orchestrator''s owner Verify: a planted finished session: one inbox item, and none more on the next pass; a planted start that never ran: one inbox item; a planted item unread past the configured time: one escalation pushed by the notifier stub to the orchestrator''s owner. [DEC-1007, DEC-998]'\n  - 'A status file every pass: the sessions running counted from the processes (the launcher''s identity marker), the load, memory, the gate, the slots held, the peaks ahead, the queue, the inbox; a pass that fails says so at the top of the status, never a stale file that looks current Verify: after a planted pass the status file holds the running sessions (counted from processes by the launcher''s identity marker), load, memory, gate, slots held, peaks ahead, queue and inbox; after a planted failing pass the top line says the pass failed and the file is not a stale one that looks current. [DEC-1007]'\n  - 'Nothing project-specific in the code; planted tests for every refusal (an uncommitted claim, a shut gate, no room for a peak, a running ticket, an unread return, a malformed list line, a hung command, a crash after a launch); an independent review before it is switched on; this repository''s dispatcher (the CTO''s tool) moves onto it Verify: grep of the dispatcher code for this repository''s branches, paths and ticket ids finds 0 lines; planted tests exist and fail for each named refusal (uncommitted claim, shut gate, no room for a peak, running ticket, unread return, malformed list line, hung command, crash after a launch); the independent review''s record exists before the dispatcher is switched on; this repository''s tool is no longer the one running. [DEC-1007, DEC-982, DEC-1003]'\n  - 'The dispatcher never starts a third review round for a ticket (its review rounds counted from its probe records); such a ticket goes to the inbox as an owner item Verify: a planted ticket with two probe records: its next review launch is not started and the ticket becomes one owner item in the inbox; a planted ticket with one probe record is started. [DEC-1010 item 1, SMART-WORK-3]'\n  - 'No watcher needs re-arming; every wake is an inbox item a pass writes Verify: a planted run across a restart: every wake the caller gets is an inbox item written by a pass, and no watcher process or re-arm step is present or needed. [DEC-1014 item 2, SMART-WORK-4 line 12] (folds W2-118 S5)'\n  - 'Every commit id and path a return names is resolved against git; one that does not resolve is named in the inbox item Verify: planted returns naming a real commit and path and a nonexistent one: the inbox item for the second names the one that does not resolve; the first names none. [DEC-1014 item 2, SMART-WORK-4 line 2] [moved from W2-118 S4, DEC-1083]'\n  - 'The ready list the dispatcher reads may come from gov plan --ready (W2-136), reviewed and committed by the orchestrator; the dispatcher starts only what is on it, and its own order is never its choice Verify: a planted list from `gov plan --ready` committed by the orchestrator: the dispatcher starts only entries on it and in no order of its own; an entry not on it is not started. [DEC-1007 (2), DEC-1088 (1)] [added, DEC-1088]'\n  failure:\n  - 'A session started for an entry not on the ready list, not ready, already running, or without room for its peak; a ticket landed that was not approved, or twice; a return never put in the inbox; a lead count not from the processes Verify: planted passes with an off-list entry, a not-ready one, a running one and one with no room for its peak: no session starts for any; an unapproved ticket and an approved one a second time are not landed; a finished return missing from the inbox, and a lead count taken from anything but processes, are each absent. [DEC-1007, DEC-1008]'\n  lifted:\n  moved:\nprofile: FULL\nsources:\n- DEC-1007\n- DEC-1008\n- DEC-1003\n- DEC-979\n- DEC-998\n- DEC-1009\n- DEC-1010\n- DEC-1014\n- DEC-1015\n- DEC-1018\n- DEC-1030\n- DEC-1031\n- DEC-1083\n- DEC-1084\n- DEC-1088\n- DEC-715\n- DEC-944\n- DEC-952\n- DEC-982\n- DEC-983\n- DEC-989\n- DEC-995\n- DAEO-ts4y\n- DAEO-1ahb\nest_loc: 500\nacceptance_tests:\n  path: tests/acceptance/W2-121/\n  author: independent-test-designer (MR-3)\ntrack: A\nlist_rows:\n- W2-H046\n---\n# W2-121 gov dispatch\n\nThe owner's DEC-1007 (the dispatcher, built first as this repository's CTO tool on 2026-11-01) and DEC-1008 (P1-DISPATCH-1 (a); it lands before EXAMIN's copy and is one of K9's entry criteria: the Gov OS is not adopted on EXAMIN without a dispatcher; its starts are judged by each job's peak, every heavy step in a slot). Its model is `.gov-runtime/scratch/orchestrator/dispatch/` (reviewed PASS on the second round). Its landing step uses `gov queue` where W2-117 has landed it, a configured landing command otherwise (W2-117 is planned after EXAMIN's copy; the owner decides whether it moves before).\n\n## Part a, the core (the CTO's delegated decision, DEC-1112 (3), 2026-11-12: run 1's P-W2-121-1 (a) to P-W2-121-4 (a))\n\nThis ticket is now part a: `gov dispatch tick` and `gov dispatch status` (the former S1, S2, S3, S5, S7, S8, S11, S12,\nS18, S20 and F1's start half). The other lines moved word for word: landing to W2-121b (DAEO-ifgf), health to W2-121c\n(DAEO-5rgj, with `src/gov/resources/slots.py`), watch and launch lead to W2-121d (DAEO-6w5n, with `src/gov/watch/**` and\n`src/gov/launch/**`). Each part is one FULL loop. Whether parts a and b together meet K9's \"a dispatcher\" entry criterion\nfor EXAMIN's copy is the owner's to say (09:30 digest of 11-12).\n\n## Interface (DEC-1052; P-W2-121-2 (a): the reference dispatcher's state folder, its names made generic)\n\n- State folder `.gov-runtime/dispatch/`: `ready.txt` (`<W2> <ticket id> <brief> <log name>` per line; `#` comments; one\n  start per log name), `land.txt` (`<W2>=<12-hex head>`), `started.txt`, `land-done.txt`, `never-ran.txt`, `inbox/` and\n  `inbox/read/` (one text item per event, first lines `log:`, `W2:`, `status:`), `status.json` and `status.txt` (every\n  pass), `peaks.json`, an `OFF` file (no pass runs), `tick.lock`.\n- Configuration: a `dispatch:` section of the project's configuration (`max_leads`, the stagger, the CPU band, the nightly\n  hold window, the landing command, the notifier command); the memory floor and working size from W2-20's `gate.json`.\n- The launcher's identity marker: the lead's `GOV_TICKET` in its `--settings`, as `gov launch` sets it.\n- Exit codes: 0 a pass done or nothing to do; 3 the gate or the forecast refused a start (named in the status); 4 a lock\n  held; 2 a usage or configuration error.\n- S1's installed host entry and S8's switch-over (P-W2-121-4 (a)): checked at the close of the last part through the\n  CTO's ACT after the probe record exists, not inside a build run.\n\n## P-W2-121-5 (the CTO's ruling, delegated P2, 2026-11-12 03:20)\n\nThe six W2-96 reds in `tests/unit/accept/test_w2_96_{run2,review3,review4}.py` (signals and timeouts in `gov accept`'s\nclean-up; red in 13 of 14 recent verifies across eight trees, and in the nightly of 11-12) are shared base reds: each return\nnames them; they do not block this ticket's verify, review or land (the queue traces an unowned red against the head\nwithout the batch). They are not added to `skip_known.json` (that list is for skips). Their fix is its own ticket.\n",
  "authority": [
    {
      "id": "DEC-1007",
      "sha256": "d4795092eed1ef410579953f4e25c70ae27f99dc0b88dd6b09f7efcf467ae927",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d4795092eed1ef410579953f4e25c70ae27f99dc0b88dd6b09f7efcf467ae927",
      "reason": "declared in sources",
      "tokens": 682
    },
    {
      "id": "DEC-1008",
      "sha256": "6fa1b5203cade75aaa661789fd882b1caa5d0d10189a949ad66a8dc142239277",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6fa1b5203cade75aaa661789fd882b1caa5d0d10189a949ad66a8dc142239277",
      "reason": "declared in sources",
      "tokens": 440
    },
    {
      "id": "DEC-1003",
      "sha256": "b86a1741c38517b51144ae824f9612c1898cf3b1ee4bc4b579b6b25be1e8fb90",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b86a1741c38517b51144ae824f9612c1898cf3b1ee4bc4b579b6b25be1e8fb90",
      "reason": "declared in sources",
      "tokens": 376
    },
    {
      "id": "DEC-979",
      "sha256": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "reason": "declared in sources",
      "tokens": 1123
    },
    {
      "id": "DEC-998",
      "sha256": "6fc47e8acc6b0f2cb8c43c0e694336736f999a1dd6bc04ea1dbc57e9104d5c27",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6fc47e8acc6b0f2cb8c43c0e694336736f999a1dd6bc04ea1dbc57e9104d5c27",
      "reason": "declared in sources",
      "tokens": 465
    },
    {
      "id": "DEC-1009",
      "sha256": "1a7e84a4ced96f5e50d6514baf1058eb7f052fda6845181862d725cd1dd072c0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a7e84a4ced96f5e50d6514baf1058eb7f052fda6845181862d725cd1dd072c0",
      "reason": "declared in sources",
      "tokens": 287
    },
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
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
    },
    {
      "id": "DEC-1018",
      "sha256": "d13c152a898c575763519061c2a4798a383ed7209fb7172a8121c230390ba79c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d13c152a898c575763519061c2a4798a383ed7209fb7172a8121c230390ba79c",
      "reason": "declared in sources",
      "tokens": 439
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
      "id": "DEC-1031",
      "sha256": "694b01be9dff6a15501f5e1e71d37da01b7f915c5f793a493967611f170d01a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "694b01be9dff6a15501f5e1e71d37da01b7f915c5f793a493967611f170d01a2",
      "reason": "declared in sources",
      "tokens": 481
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
    {
      "id": "DEC-1088",
      "sha256": "8a0d03808f66bc9d97110a1237cb509bd96b27f36148e4e4828b1f43081f9244",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "8a0d03808f66bc9d97110a1237cb509bd96b27f36148e4e4828b1f43081f9244",
      "reason": "declared in sources",
      "tokens": 736
    },
    {
      "id": "DEC-715",
      "sha256": "edbe5ca0458303bf8623cc83e2a15f9cb5ebc82daab9f8ca18202dd8f3c3ab98",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "edbe5ca0458303bf8623cc83e2a15f9cb5ebc82daab9f8ca18202dd8f3c3ab98",
      "reason": "declared in sources",
      "tokens": 713
    },
    {
      "id": "DEC-944",
      "sha256": "342eeb55535d58b678e38f8a2878ca4b460995c458015c0001bd0cc59fdaaeeb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "342eeb55535d58b678e38f8a2878ca4b460995c458015c0001bd0cc59fdaaeeb",
      "reason": "declared in sources",
      "tokens": 1080
    },
    {
      "id": "DEC-952",
      "sha256": "62db7458ba5174b86200ae76a4bbdda8a7c524960f245deecd2d77c223f86bec",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62db7458ba5174b86200ae76a4bbdda8a7c524960f245deecd2d77c223f86bec",
      "reason": "declared in sources",
      "tokens": 762
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-989",
      "sha256": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "reason": "declared in sources",
      "tokens": 399
    },
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DAEO-ts4y",
      "sha256": "85cf425a4b211b5780de4c8199a7a240868db0a05bdf87f6272fa506a0fc0d65",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85cf425a4b211b5780de4c8199a7a240868db0a05bdf87f6272fa506a0fc0d65",
      "reason": "declared in sources",
      "tokens": 744
    },
    {
      "id": "DAEO-1ahb",
      "sha256": "b6b0ff31e290fb2e1186a075877e203115f5a3840bc2e5d2683999f163f562e4",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b6b0ff31e290fb2e1186a075877e203115f5a3840bc2e5d2683999f163f562e4",
      "reason": "declared in sources",
      "tokens": 1335
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
      "id": "DEC-1007",
      "sha256": "d4795092eed1ef410579953f4e25c70ae27f99dc0b88dd6b09f7efcf467ae927",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d4795092eed1ef410579953f4e25c70ae27f99dc0b88dd6b09f7efcf467ae927",
      "reason": "declared in sources",
      "tokens": 682
    },
    {
      "id": "DEC-1008",
      "sha256": "6fa1b5203cade75aaa661789fd882b1caa5d0d10189a949ad66a8dc142239277",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6fa1b5203cade75aaa661789fd882b1caa5d0d10189a949ad66a8dc142239277",
      "reason": "declared in sources",
      "tokens": 440
    },
    {
      "id": "DEC-1003",
      "sha256": "b86a1741c38517b51144ae824f9612c1898cf3b1ee4bc4b579b6b25be1e8fb90",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b86a1741c38517b51144ae824f9612c1898cf3b1ee4bc4b579b6b25be1e8fb90",
      "reason": "declared in sources",
      "tokens": 376
    },
    {
      "id": "DEC-979",
      "sha256": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a4160c3115e2b73c5c5f4c13b82043cbb549dd7837746d2e0f86a3bd7af3475",
      "reason": "declared in sources",
      "tokens": 1123
    },
    {
      "id": "DEC-998",
      "sha256": "6fc47e8acc6b0f2cb8c43c0e694336736f999a1dd6bc04ea1dbc57e9104d5c27",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6fc47e8acc6b0f2cb8c43c0e694336736f999a1dd6bc04ea1dbc57e9104d5c27",
      "reason": "declared in sources",
      "tokens": 465
    },
    {
      "id": "DEC-1009",
      "sha256": "1a7e84a4ced96f5e50d6514baf1058eb7f052fda6845181862d725cd1dd072c0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a7e84a4ced96f5e50d6514baf1058eb7f052fda6845181862d725cd1dd072c0",
      "reason": "declared in sources",
      "tokens": 287
    },
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
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
    },
    {
      "id": "DEC-1018",
      "sha256": "d13c152a898c575763519061c2a4798a383ed7209fb7172a8121c230390ba79c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d13c152a898c575763519061c2a4798a383ed7209fb7172a8121c230390ba79c",
      "reason": "declared in sources",
      "tokens": 439
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
      "id": "DEC-1031",
      "sha256": "694b01be9dff6a15501f5e1e71d37da01b7f915c5f793a493967611f170d01a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "694b01be9dff6a15501f5e1e71d37da01b7f915c5f793a493967611f170d01a2",
      "reason": "declared in sources",
      "tokens": 481
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
    {
      "id": "DEC-1088",
      "sha256": "8a0d03808f66bc9d97110a1237cb509bd96b27f36148e4e4828b1f43081f9244",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "8a0d03808f66bc9d97110a1237cb509bd96b27f36148e4e4828b1f43081f9244",
      "reason": "declared in sources",
      "tokens": 736
    },
    {
      "id": "DEC-715",
      "sha256": "edbe5ca0458303bf8623cc83e2a15f9cb5ebc82daab9f8ca18202dd8f3c3ab98",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "edbe5ca0458303bf8623cc83e2a15f9cb5ebc82daab9f8ca18202dd8f3c3ab98",
      "reason": "declared in sources",
      "tokens": 713
    },
    {
      "id": "DEC-944",
      "sha256": "342eeb55535d58b678e38f8a2878ca4b460995c458015c0001bd0cc59fdaaeeb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "342eeb55535d58b678e38f8a2878ca4b460995c458015c0001bd0cc59fdaaeeb",
      "reason": "declared in sources",
      "tokens": 1080
    },
    {
      "id": "DEC-952",
      "sha256": "62db7458ba5174b86200ae76a4bbdda8a7c524960f245deecd2d77c223f86bec",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62db7458ba5174b86200ae76a4bbdda8a7c524960f245deecd2d77c223f86bec",
      "reason": "declared in sources",
      "tokens": 762
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-989",
      "sha256": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "reason": "declared in sources",
      "tokens": 399
    },
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DAEO-ts4y",
      "sha256": "85cf425a4b211b5780de4c8199a7a240868db0a05bdf87f6272fa506a0fc0d65",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85cf425a4b211b5780de4c8199a7a240868db0a05bdf87f6272fa506a0fc0d65",
      "reason": "declared in sources",
      "tokens": 744
    },
    {
      "id": "DAEO-1ahb",
      "sha256": "b6b0ff31e290fb2e1186a075877e203115f5a3840bc2e5d2683999f163f562e4",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b6b0ff31e290fb2e1186a075877e203115f5a3840bc2e5d2683999f163f562e4",
      "reason": "declared in sources",
      "tokens": 1335
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
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "#### W2-83a A playbook per stream: the form in the kernel template, its schema in gov check, and the adopt step (STANDARD, product-spec; DEC-944 item 3; EXAMIN minimum)\n- **Ticket file:** `DAEO-dy7j`.\n- **DEC-954:** it builds nothing further until the owner approves the roles spec.\n- **Why:** an adopted product should start with the form for its streams: purpose, standing practices, usual ticket classes, roles and the skills they load.\n- **Starts:** priority 5 (DEC-946), after W2-64 (which holds `src/gov/check/schema.py`).\n- **Allowed paths:** the kernel's `templates/playbook.md` and `schemas/playbook.schema.json`, the schema map's one line in `src/gov/check/schema.py`, the adopt skill and its copies, unit tests, the CIT-P and CIT-E; acceptance tests in `tests/acceptance/W2-83a/`.\n- **KPIs, success:** the form and its schema in the kernel; `gov check` refuses a playbook missing any part; adoption writes the form into a product, which passes `gov check`; nothing project-specific in the kernel.\n- **KPIs, failure:** an incomplete playbook passes; a rule of this repository in the kernel; a kernel file changed without its CIT-P.\n\n",
      "tokens": 286
    },
    {
      "id": "a919c129625c19be83999f6d",
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "text": "## 5. Recommendation\n\n**(a), confidence medium-high.**\n- **Highest confidence:** rows 6, 9, 11 and 12. They have repeated internal evidence and a direct external match, and\n  the fixes are mechanisms already proven here (the dispatcher, the quiet-hours hook).\n- **Medium confidence:** rows 4 and 7. External evidence is strong. Internally the gaming route is mostly closed and\n  only the verdict-level form was met, so the KPI lines are cheap insurance, not a response to an observed defect.\n- **Lowest confidence, medium-low:** the thresholds proposed in rows 2 (5 %), 10 (300 lines), 13 (the band) and 14\n  (10 %). They are starting values to tune.\n\n**In order, if the owner approves:**\n1. The NOW practices, by the CTO today.\n2. The KPI lines, as one SMART-WORK-4 package of exact KPI text, in the form of SMART-WORK-3, applied as each ticket next\n   runs.\n3. The W3 rows into `docs/plan/WAVE_3_PARKING.md`.\n\n",
      "tokens": 228
    },
    {
      "id": "15b4a12cbbc67642cbad76ad",
      "path": "governance/project/orchestration/packages/SMART-WORK-5.md",
      "text": "## 2. The 9 practices and their product tickets\n\n| # | Practice (DEC-1014 item 1) | Product ticket and line | State |\n|---|---|---|---|\n| 1 | Claims only through the dispatcher's readiness check | W2-82 (the Definition of Ready: `gov claim` checks it, `gov launch` refuses) and W2-121 KPI 2 | covered |\n| 2 | The status block generated from files | W2-11, SMART-WORK-4 line 6 | covered |\n| 3 | The remaining watchers into dispatcher passes | W2-121 / W2-118, SMART-WORK-4 line 12 | covered |\n| 4 | The dispatcher watches the sentinel's heartbeat | W2-121, SMART-WORK-4 line 11 | covered; **the sentinel session stays ours** (\u00a73) |\n| 5 | The checkpoint under 300 lines, RESUME HERE first | W2-11, SMART-WORK-4 line 10 | covered |\n| 6 | A tool change carries its before-and-after measurement | none | **stays ours** (\u00a73); its audit is W3-P20 |\n| 7 | A different model or effort for the second review on fail-open FULL tickets; a lead's agreement is not corroboration | W2-60a and W2-11 | **proposed** lines A and B |\n| 8 | The moderator's triage before any round is declared | W2-11 / W2-33 (SMART-WORK-3) and W2-115, SMART-WORK-4 line 5 | covered |\n",
      "tokens": 287
    },
    {
      "id": "a42deaceda362e9fd06f8898",
      "path": "governance/project/orchestration/packages/P1-DISPATCH-1.md",
      "text": "  - `'Every finished session''s return becomes one inbox item, once; an item unread past a configured time raises an escalation the host''s notifier pushes (the orchestrator''s phone) [DEC-1007, DEC-998]'`\n  - `'Every ticket the orchestrator approved to land goes into gov queue (W2-117) as one batch whenever the queue is free, the tree clean and no close running; never one not approved; each outcome becomes an inbox item [DEC-1007, DEC-989]'`\n  - `'A status file every pass: the sessions running counted from the processes, the load, memory, the gate, the slots held, the queue, the inbox; the orchestrator''s status reads it [DEC-1007]'`\n  - `'Nothing project-specific in the code; planted tests for every refusal; an independent review before it is switched on [DEC-1007, DEC-982]'`\n  - and W2-118's S1 amended: `\"...wakes its caller ... ; or, where a dispatcher runs, writes the inbox item it reads (no watcher to re-arm) [DEC-1007]\"`.\n- **(b) KPI changes spread over W2-20, W2-117 and W2-118:** no new ticket, but the starting of sessions belongs to none\n  of them (the gate reads, the queue lands, the watch wakes), so the core would be split across three owners.\n",
      "tokens": 294
    },
    {
      "id": "DAEO-j9z6",
      "path": ".tickets/DAEO-j9z6.md",
      "text": "  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired Verify: grep of the close and queue code for this repository''s branch names, paths and ticket ids finds 0 lines; a planted second repository''s queue runs with the same code; this repository''s queue runs on it and W2-97''s tool is no longer called. [DEC-983, DEC-982] [moved from W2-117 S3, DEC-1083]'\n  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it Verify: a planted landing: the integration store''s refresh (W2-116) is started once afterwards and the queue''s own warm clones are seeded from that store, both visible in the queue''s record. [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3] [moved from W2-117 S4, DEC-1083]'\n",
      "tokens": 220
    },
    {
      "id": "DAEO-zkr9",
      "path": ".tickets/DAEO-zkr9.md",
      "text": "  - '`gov queue` gives W2-97''s queue in the product: the commit tested is the commit landed; one run per batch on the merged result, in a heavy-job slot (W2-20); a run skipped when the merged code is identical to what the lead tested, with its reason; a red batch''s culprit ejected and the rest advanced (W2-115''s attribution) [DEC-959 item 1, DEC-983, DEC-982]'\n  - 'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run, the close citing the queue''s record instead of running its own tests on the same code; no ticket sits merged but not closed [DEC-989, DEC-959 item 1, DEC-983, DEC-982, DEC-1003, SMART-WORK-2]'\n  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired [DEC-983, DEC-982]'\n  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3]'\n",
      "tokens": 285
    },
    {
      "id": "0a3d37b32ea5c6a4b2ba87ea",
      "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md",
      "text": "  a planted mismatch is red [DEC-953 item 2, DEC-954].\n- **r2:** the typed handoff: schema and template; its kinds (\u00a74.2); the twelve fields its required core; a record\n  missing a required field is refused; one live case shows a fresh agent states task, inputs, open questions and\n  next step as the record does [CAP-22.b, AR-6].\n- **r2:** the agents under `.claude/agents/` are generated from the role files, never placed by hand [W2-M084].\n- **r2:** nothing project-specific in a kernel role file (no W2 ids, no EXAMIN, no paths of this repository).\n- **CIT-P first** (the combined one), approved before any kernel file changes; the CIT-E after [CAP-33.a].\n\n**KPIs, failure:** a role file without its defaults block that still reads; a guard-class mismatch that passes;\na handoff record without a required field that validates; a hand-placed agent file; a kernel file changed before the CIT-P's approval.\n\n**Dropped from the card** (to Wave 3, as DEC-832 decided): the test-execution and integration roles, the UX role.\n**DEC-832's four skill packs:** Wave 3, recommended (Q5).\n\n",
      "tokens": 271
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "---\nid: DAEO-9bc0\nstatus: closed\ndeps: [DAEO-k7hz]\nlinks: [DAEO-k7hz]\ncreated: 2026-11-02T00:18:23Z\ntype: task\npriority: 1\nassignee: product-spec\nexternal-ref: W2-11b\ntags: [wave-2, skill, standard]\nwbs_id: W2-11b\ntitle: 'The orchestration skill''s and the reviewer template''s seven lines that W2-11 landed without (SMART-WORK-3, SMART-WORK-4 lines 4, 6, 9, 10, SMART-WORK-5 B and C)'\nclass: skill\nstate_class: AUTHORITATIVE\nrole: product-spec\ndepends_on:\n- DAEO-k7hz\nallowed_paths:\n- template/governance/kernel/templates/brief-*.md\n- template/governance/kernel/skills/orchestration/**\n- template/governance/kernel/skills/qa-review/**\n- .claude/skills/orchestration/**\n- .claude/skills/qa-review/**\n- .rulesync/skills/orchestration/**\n- .rulesync/skills/qa-review/**\n- template/.rulesync/skills/orchestration/**\n- template/.rulesync/skills/qa-review/**\n- docs/changes/W2-11b-CIT-P.md\nkpis:\n  success:\n",
      "tokens": 226
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "- template/.rulesync/skills/orchestration/**\n- template/.rulesync/skills/qa-review/**\n- docs/changes/W2-11b-CIT-P.md\nkpis:\n  success:\n  - 'The reviewer''s brief template requires the structured verdict block per KPI (scope, ordinary work, consequence per finding) and states the two questions word for word; the qa-review skill states the moderator''s triage, the blocking rule and the two-round cap, with one scenario each [DEC-1010 item 1, SMART-WORK-3]'\n  - 'The reviewer states, per finding, what evidence would reverse it [DEC-1014, SMART-WORK-4 line 4]'\n  - 'The orchestration skill: the status block''s counts (leads, queue, inbox, merged, closed, pings) are generated from files; a typed count is a slip [DEC-1014, SMART-WORK-4 line 6]'\n  - 'Each standing rule in the orchestration skill names its mechanism, or says \"prose only\" with the reason [DEC-1014, SMART-WORK-4 line 9]'\n  - 'The orchestration skill: the resume block comes first and the checkpoint stays under a set token budget; over it, the stop hook names it [DEC-1014, SMART-WORK-4 line 10]'\n",
      "tokens": 266
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "# W2-11b The orchestration skill's and the reviewer template's seven lines\n\nThe owner's DEC-1022 item 3 (P-W2-11-LINES (a)): seven approved KPI lines meant for W2-11 (SMART-WORK-3's reviewer\ntemplate and qa-review line; SMART-WORK-4 lines 4, 6, 9 and 10; SMART-WORK-5 B and C) could not ride in W2-11's round,\nwhich landed without them. This ticket carries them, word for word. It starts once W2-11 (`DAEO-k7hz`) closes. If\nW2-11 goes back for another round instead, the seven lines ride along in that round and this ticket is withdrawn.\nSMART-WORK-5 B fixes a product defect: the kernel orchestration skill counts the recommendation's and the proposer's\nagreement as corroboration (`template/governance/kernel/skills/orchestration/SKILL.md`).\n\n**D9-FATES (DEC-1083):** Merged into W2-128 by DEC-1083. S1, F1 and F2 fold into W2-128's TPL-1 S3 and TPL-4 (no new line); S2 moved to W2-128 as the reviewer template's line; S3 to S7 lifted. S1's other half (the qa-review skill's triage, its blocking rule, the two-round cap and the two questions) lives in W2-11 S12 and W2-33's moderator line (S10 in D9-FATES' numbering, its S6 since its lifts and moves).\n",
      "tokens": 289
    },
    {
      "id": "DEC-1022",
      "path": "docs/DECISION_REGISTER.md",
      "text": "- **Decision:** (1) ACT-PUSH-INPUT-1's live test is re-run by day, after 07:30 on 2026-11-02: the CTO pings first, the owner steps away from the laptop and lets the prompt wait a few minutes (at 00:12 the owner approved from the laptop within 25 s, so the phone push was probably skipped as the owner was active). (2) P-W2-90b-1 (b): W2-90b's KPI S4 for W1-46's live sessions and W1-50's freeze launcher is re-baselined under DEC-822 item 3 (a live session judges the pinned guard by design; the non-live cases judge the worktree's code); the line sits in W2-90c (`DAEO-fu3n`, DEC-1016) and is re-worded there; nothing is lowered. (3) W2-11's seven unplaced lines (SMART-WORK-3's reviewer template and qa-review line; SMART-WORK-4 lines 4, 6, 9, 10; SMART-WORK-5 B and C): option (a), W2-11b (`DAEO-9bc0`, product-spec, STANDARD) filed with them word for word, to start once W2-11 closes; if W2-11 goes back for another round instead, the lines ride along in it and W2-11b is withdrawn. (4) SMART-WORK-4 line 3 (reviewer recall per model): option (c), Wave 3 row W3-P21.\n\n| Version | Date | Change |\n|---|---|---|\n",
      "tokens": 279
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-66b | A | **New (DEC-1027 B).** W2-66's record-only case reads `win_toast.ps1` as code; a test revision under the owner's named decision (`DAEO-zuiy`). | test-revision | independent-test-designer | LITE | none | 2 | DEC-1027, DEC-906 |\n| W2-11b | A | **New (DEC-1022 item 3, P-W2-11-LINES (a)).** The seven KPI lines W2-11 landed without (SMART-WORK-3's reviewer template and qa-review line; SMART-WORK-4 lines 4, 6, 9, 10; SMART-WORK-5 B and C), word for word; starts once W2-11 closes; withdrawn if W2-11 takes them in another round (`DAEO-9bc0`). | skill | product-spec | STANDARD | W2-11 | 120 | DEC-1022, DEC-1014, DEC-1010 |\n| ACT 2 | \u2014 | **Milestone (DEC-954 item 6; PLAN-GROWTH-1 gap 4).** The one re-pin, an owner ACT, once memory, the roles and the three layers' foundations have landed; W2-100 and W2-101 start after it | milestone | owner | \u2014 | memory landed (K4), the roles landed (W2-33, W2-60b, W2-11), W2-104 | 0 | DEC-954 item 6 |\n| W2-55 | C | Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see (DEC-791) | implementation | engineer | STANDARD | W2-03 | 150 | DEC-791 (i) |\n",
      "tokens": 287
    },
    {
      "id": "DAEO-dy7j",
      "path": ".tickets/DAEO-dy7j.md",
      "text": "  - 'gov check validates every playbook: core-schema maps the type playbook to its schema, in the record folders it already reads; a planted playbook that lacks any of the five parts, a practice with no id, or a role with no skills is refused, naming the record and the field [DEC-944 item 3, DEC-872 item 2]'\n  - 'Adoption creates the form in a product: the adopt skill gains the step that writes one playbook per stream from the kernel form, its four copies kept in step through the adapter, its version raised; a product built from this template at a temporary path passes gov check with one playbook and is refused with a planted faulty one [DEC-944 item 3, CAP-44.a, CAP-24.a]'\n  - 'CIT-P first: docs/changes/W2-83a-CIT-P.md before any kernel file changes, reviewed independently and approved by the owner before the merge; the CIT-E after [CAP-33.a, CAP-24.c, DEC-944]'\n  - 'Nothing project-specific in the kernel: the form and the adopt step name no keystone, no EXAMIN, no workbench and no path of this repository; gov check is green; the scoped set in the close''s form is green; every red the ticket did not cause is named for the CTO [DEC-968, DEC-983, DEC-982] [DEC-880, DEC-866]'\n",
      "tokens": 299
    },
    {
      "id": "CONTRACT-v4",
      "path": "docs/contract/CONTRACT_v4.md",
      "text": "### CAP-06 \u2014 Repository contract and path map\n\n- **Outcome:** An agent can find where every kind of artefact lives from the committed path map, and nothing material is unclassified.\n- **Acceptance:** `gov doctor` reports zero unclassified tracked paths against `governance/project/path-map.yaml`, and names each path when one is added outside the map.\n- **Wave:** W1\n- **Provider:** W1-08, W1-27, W1-41\n- **Disposition:** KEPT\n- **Sources:** Contract v3 Gate B1, B2; Framework v4.1.2 \u00a78, \u00a79; Adoption Protocol v3.0 \u00a78; OWNER-DECISION-P2-0008 \u00a72 (project-specific floor); DEC-060; DEC-041\n- **Covers:**\n  - `CAP-06.a` [W1] Every material artefact classified by current path, class, authority and intended target \u2014 Contract v3 B1, B2; Framework v4.1.2 \u00a78, \u00a79 \u00b7 delivered by W1-27, W1-08\n  - `CAP-06.b` [W1] Target actions KEEP/MOVE/RENAME/SPLIT/MERGE/EXTRACT/RETIRE/DELETE_FROM_ACTIVE_TREE \u2014 Contract v3 B2 \u00b7 delivered by W1-41\n  - `CAP-06.c` [W1] Unknown material artefacts block destructive migration \u2014 Contract v3 B2 \u00b7 delivered by W1-41\n  - `CAP-06.d` [W1] Imports/references/consumers represented; path-map compliance machine-checkable \u2014 Contract v3 B2 \u00b7 delivered by W1-41, W1-27\n",
      "tokens": 296
    },
    {
      "id": "a2ec75c865af839325a6ce59",
      "path": "docs/contract/contract.yaml",
      "text": "  outcome: An agent can find where every kind of artefact lives from the committed path map, and nothing material is unclassified.\n  acceptance: '`gov doctor` reports zero unclassified tracked paths against `governance/project/path-map.yaml`, and names\n    each path when one is added outside the map.'\n  wave: W1\n  provider:\n  - W1-08\n  - W1-27\n  - W1-41\n  sources:\n  - Contract v3 Gate B1, B2\n  - Framework v4.1.2 \u00a78, \u00a79\n  - Adoption Protocol v3.0 \u00a78\n  - OWNER-DECISION-P2-0008 \u00a72 (project-specific floor)\n  - DEC-060\n  - DEC-041\n  scenarios:\n    dev:\n    - B-01\n    - B-02\n    - B-03\n    - B-04\n    - B-05\n    - B-08\n    - B-09\n    - B-11\n    - AUDIT-B-03\n    - AUDIT-B-07\n    - SEC-B-01\n    - SEC-B-02\n    qual:\n    - MR-B-Q06\n    - SEC-B-Q02\n    - B-Q01\n    - B-Q02\n    - B-Q03\n    - AUDIT-B-Q18\n    - AUDIT-B-Q23\n    - AUDIT-B-Q38\n    - ISO-X-Q01\n    - B-X-Q01\n    dev_unlisted_in_matrix: 2\n  disposition:\n    class: KEPT\n  covers:\n  - id: CAP-06.a\n    item: Every material artefact classified by current path, class, authority and intended target\n    source: Contract v3 B1, B2; Framework v4.1.2 \u00a78, \u00a79\n    wave: W1\n    provider:\n    - W1-27\n    - W1-08\n  - id: CAP-06.b\n",
      "tokens": 295
    },
    {
      "id": "OWNER-DECISION-P2-0008",
      "path": "docs/imported/OWNER-DECISION-P2-0008.md",
      "text": "## 2. P1 RESOLVED \u2014 the floor is project-specific\n\n**Governance OS governs exactly the repository into which it is adopted.** It imposes **no universal filesystem\nlayout** and governs no path outside that repository merely because a global template knows of it.\n\n```\ngov adopt in Repository X \u2192 identify/authenticate X \u2192 inventory X's NATIVE structure\n  \u2192 derive the proposed Project-X floor \u2192 consequential adoption decision where required\n  \u2192 governed owner approval \u2192 authenticated Project-X adoption floor \u2192 govern X by that floor\n```\n\n`src/**`, `backend/**`, `services/**`, `app/**`, `product/**`, `packages/**` are all legitimate. **No universal\n`product/**` assumption may be required for brownfield or native repositories.**\n\nThe floor's authority comes from **the governed adoption transition and the authenticated machine/kernel chain** \u2014 not\nfrom an arbitrary later project edit. After adoption: project-local configuration may add, narrow or strengthen;\nordinary edits **must not silently remove obligations** established by the authenticated floor; changing the\nauthoritative floor itself goes through the governed route; paths outside the repository stay outside the domain absent\n",
      "tokens": 299
    },
    {
      "id": "OWNER-DECISION-P2-0008",
      "path": "docs/imported/OWNER-DECISION-P2-0008.md",
      "text": "## 8. Response to review findings \u2014 automatic, with named stops\n\nAn ordinary implementation defect **within** this architecture: repair \u2192 invalidate affected evidence \u2192 fresh review,\n**automatically, without returning to the owner**.\n\n**STOP and return to the owner** only if evidence shows: `ResolvedExecution` cannot provide the exact-object property\nin this profile; project-specific floor composition cannot satisfy OC-P2-04 or Contract v3; a **new trusted authority**\nmust be invented; Level 1 / R0 / R1 must be reopened; a Level-3 isolation mechanism becomes **mandatory** for Phase 2;\nthe product/security/availability/usability boundary materially changes; or another genuine owner-level architecture\ndecision arises. **No further unbounded enumeration cycle.**\n\n",
      "tokens": 193
    },
    {
      "id": "DAEO-5rgj",
      "path": ".tickets/DAEO-5rgj.md",
      "text": "  - 'The morning report lists every crash or error in the servers'' logs overnight (CUDA errors, runner exits, model loads and their layers, failed and timed-out requests with their counts), beside the nightly''s tests [DEC-1030 item 3, DEC-1031 item 4] [lifted (was S17), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n  - 'The dispatcher alerts when the orchestrator''s session or its sentinel has no heartbeat for a configured time [DEC-1014 item 2, SMART-WORK-4 line 11] (to Wave 3, W3-P16, W-10) [re-scoped, DEC-1083] (was S12)'\nnon_goals:\n- the dispatcher core (W2-121, part a) and the other parts\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]\nacceptance_tests:\n  path: tests/acceptance/W2-121c/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\n---\n",
      "tokens": 262
    },
    {
      "id": "DAEO-5rgj",
      "path": ".tickets/DAEO-5rgj.md",
      "text": "  - 'While ready work waits, busy cores stay within a configured band for at least 80 % of the hours; time below or above the band is reported daily with its cause Verify: planted history of hours with ready work waiting: the daily report gives the share of hours with busy cores inside the configured band (at least 80 % passes, below it is flagged) and lists the time below and above the band with its cause. [DEC-1014 item 2, SMART-WORK-4 line 13]'\n  - 'Each pass reads the GPU state and, for each embedding server, its model''s layers on the GPU (from the server''s own log or API); a crash in a server''s log, or a model loaded with 0 layers on a GPU it is expected to use, writes one inbox item at once and one line for the sentinel, once per incident; the status shows the GPU, its holders and each model''s layers Verify: planted server logs: a crash line, and a model loaded with 0 layers on a GPU it is expected to use, each give one inbox item at once and one sentinel line, once per incident; a healthy log gives none; the status shows the GPU, its holders and each model''s layers. [DEC-1030 items 1 and 4, DEC-1031 item 4]'\n  failure:\n",
      "tokens": 288
    },
    {
      "id": "2808533d411a951d767d749b",
      "path": "governance/project/orchestration/packages/SMART-WORK-5.md",
      "text": "## 3. What stays this repository's own, and why\n\n- **The tool-change measurement (practice 6).**\n  - In an adopted repository the orchestrator has no tools lane of its own. Its tools are the Gov OS's commands.\n  - Those commands change through tickets, which already need measured evidence (DEC-996 A) and CIT-P (CAP-33).\n  - The lane exists here only because the CTO builds tools before the product has them. Each of those tools is retired\n    as its product ticket lands: `land.py` \u2192 W2-117; `heavy_slot.sh` \u2192 W2-20; the dispatcher \u2192 W2-121.\n  - The independent audit of the orchestrator's commits is parked as W3-P20.\n- **The sentinel session (practice 4, the second half).**\n  - The Haiku session in tmux that pushes through the Claude app depends on one owner's devices and channels.\n  - The product gets the part that does not depend on them: the dispatcher's heartbeat alert (W2-121, SMART-WORK-4 line\n    11) through the host's notifier.\n  - The full dead-man's switch as a product feature is already parked as W3-P16, to be decided after the two-day trial\n    (ACT-SENTINEL-1).\n",
      "tokens": 272
    },
    {
      "id": "DAEO-t8mp",
      "path": ".tickets/DAEO-t8mp.md",
      "text": "  - 'Links recorded at the source (DEC-1073 (5)(c)): each role template (T-2 to T-8), the ticket template (T-1) and the record templates (decision-record, lesson, research, checkpoint, failure) carry LINK-INTEGRITY.md \u00a75''s lines for the records that role writes. Verify: a string test per template, and gov links on a planted record filled from each template''s example gives no finding [DEC-1073, DEC-866, DEC-182, DEC-927]'\n  - 'The facts file''s commands hold links (gov links --since {BASE}) with its check form; the lead template''s return quotes its first line [DEC-1073, DEC-927]'\n  - 'The lesson, failure and research schemas allow sources (ids), and research decisions, both optional; every existing record stays valid [DEC-1073]'\n  - 'The kernel part goes through one CIT-P under CAP-33 (evidence R2 and R3, an independent review, the owner''s approval, a versioned promotion), recorded in docs/changes/W2-128-CIT-P.md; the .claude/ copies are installed by the owner''s operator as an ACT [CAP-33, DEC-1050, DEC-1081]'\n  - 'The reviewer states, per finding, what evidence would reverse it [DEC-1014, SMART-WORK-4 line 4] [moved from W2-11b S2, DEC-1083]'\n",
      "tokens": 292
    },
    {
      "id": "53d0c84957753433c4e1bf16",
      "path": "governance/project/orchestration/packages/SMART-WORK-5.md",
      "text": "### Proposed lines\n\n- **A. W2-60a (`DAEO-cv58`), the role, its model and effort loaded at launch.**\n  - \"On a FULL ticket that could fail open, the second review is launched with a different model or effort setting from\n    the first, taken from the role defaults; the launch record shows both, and the same setting twice is refused unless\n    the owner named it [DEC-1014 item 1, RESEARCH-AGENT-FAILURES-1 row 4].\"\n  - SMART-WORK-4 line 3 (reviewer recall per model, on W2-93 / W2-81) then measures whether the difference catches more.\n- **B. W2-11 (`DAEO-k7hz`), the orchestration skill.**\n  - \"Delegation does not count the recommendation and the proposer's agreement as corroboration on a decision that\n    touches verification; that needs an independent reviewer's record [DEC-1014 item 1, row 4].\"\n  - Why: today the kernel skill counts that agreement as corroboration (`template/governance/kernel/skills/orchestration/SKILL.md:38`).\n    That is a product defect, not only a practice.\n- **C. W2-11 (`DAEO-k7hz`), the orchestration skill's daily document.**\n  - \"The daily document gives the week's net ticket growth (filed minus closed, counted from the tickets) and the share\n",
      "tokens": 296
    },
    {
      "id": "DAEO-7r5e",
      "path": ".tickets/DAEO-7r5e.md",
      "text": "  - 'gov check on this repository: 17 of 17 families, no RED, no unexplained YELLOW [W2-H020, W2-L106, W2-L335, W2-M142, W2-L017].'\n  - DEC-709 is retired by a register entry (DEC-719 item 4).\n  - 'Entry criterion (DEC-971 item 3, W2-05''s R3-1): before the hooks go back on, a declared check that reads what is staged sees the staged content under `git commit -a` and `git commit -- <path>` too (git''s own index handed to it under a separate name), with a test; until then the hooks are not reinstalled [DEC-971, DEC-803]'\n  - 'The guard''s false-positive rate on the logged refusals (planted cases plus `guard-refusals.jsonl`) is reported, and is under 10 % before the hooks go back on [DEC-1014 item 2, SMART-WORK-4 line 14]'\n  failure:\n  - Any hook refusal is reported to the owner and never worked round.\nprofile: STANDARD\nsources:\n- MR-3\n- DEC-136\n- DEC-441\n- DEC-709\n- DEC-719\n- DEC-971\nest_loc: 0\nacceptance_tests:\n  judged_by: 'its class (WBS \u00a70 rule 1, W2-07): its named evidence files'\ntrack: A\ncloses:\n- AR-3\n- F-M4\n- F-M13\nlist_rows:\n- W2-H020\n- W2-L017\n- W2-L106\n- W2-L335\n- W2-M013\n- W2-M142\n---\n",
      "tokens": 278
    },
    {
      "id": "DAEO-emq1",
      "path": ".tickets/DAEO-emq1.md",
      "text": "  - 'A scoped close that runs the full suite, or reads or writes an accepted-reds or load-sensitive list. Verify: a scoped close of a planted ticket: the test runner''s call list holds no full-suite run, and the accepted-reds and load-sensitive lists are neither opened nor written (file access or file times show none).'\n  - 'A batch that closes a culprit, or closes the rest when a red is unexplained. Verify: a planted batch with one culprit, and one with a red no candidate explains: the culprit is not closed, and the unexplained batch closes nothing.'\n  - 'The strict close changed in any verdict. Verify: the strict-mode close run on the recorded planted cases from before the change: every verdict and every refusal is the same as the recorded one.'\n  lifted:\n  - 'A round whose in-scope blocking findings are not fewer than the previous round''s is reported as not converging, at once [DEC-1014 item 2, SMART-WORK-4 line 5] [lifted (was S12), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n",
      "tokens": 252
    },
    {
      "id": "DAEO-emq1",
      "path": ".tickets/DAEO-emq1.md",
      "text": "  - 'A round whose in-scope blocking findings are not fewer than the previous round''s is reported as not converging, at once [DEC-1014 item 2, SMART-WORK-4 line 5] [lifted (was S12), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n  - 'A test revision shows case and assertion counts before and after; a deleted case, a new skip or xfail, or a loosened comparison blocks unless the owner named it [DEC-1014 item 2, SMART-WORK-4 line 7] [lifted (was S13), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n  - 'A test that refuses a close has passed 3 runs in a row on the baseline; otherwise it is quarantined and named, never a refusal; a quarantined test is never left on a list; it is fixed at once or escalated, like any red (DEC-968) [DEC-1014 item 2, SMART-WORK-4 line 8] [lifted (was S14), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\n  - 'Each close record carries governance time as a share of the ticket''s time [DEC-1014 item 2, SMART-WORK-4 line 15] [lifted (was S15), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 \u00a75)]'\nprofile: FULL\nsources:\n- DEC-983\n- DEC-982\n- DEC-979\n- DEC-968\n- DEC-966\n- DEC-953\n- DEC-1001\n- DEC-1002\n- DEC-1003\n- DEC-1010\n- DEC-1014\n",
      "tokens": 300
    },
    {
      "id": "25da94c60a6889c098eada60",
      "path": "docs/plan/WAVE_3_PARKING.md",
      "text": "| W3-P20 | An independent auditor samples the orchestrator's operational commits weekly, as the audit role does for tickets (RESEARCH-AGENT-FAILURES-1 row 15) | DEC-1014 | 2026-11-01 |\n| W3-P21 | Reviewer recall per model: the proving ground's planted problems also measure the share of planted defects a review finds, reported per model (SMART-WORK-4 line 3; no home in Wave 2: W2-81 landed without a round, W2-93 has no scorer) | DEC-1022 | 2026-11-02 |\n| W3-P22 | W2-32's R2-F1, the round-2 review's finding on nested parents: parent expansion sends no line of a module twice and names every span it leaves out (DEC-1067); the work is parked at tag `park/W2-32-R2-F1`. Its strict-xfail case (`tests/acceptance/W2-32/test_w2_32_s7_dec1067.py:195`, `test_nested_parents_send_no_line_twice_and_name_every_span_left_out`) stays strict, so it turns red when R2-F1 is fixed; its reason names this row since `b1c101c82` (a test designer, `Rewrite-Reason: DEC-1083 (3)`) | DEC-1083 (3) (D9-FATES) | 2026-11-06 |\n",
      "tokens": 252
    },
    {
      "id": "7ca94abcbb983545cd7274d4",
      "path": "governance/project/orchestration/packages/SMART-WORK-4.md",
      "text": "# SMART-WORK-4 \u2014 RESEARCH-AGENT-FAILURES-1's KPI lines, approved (DEC-1014), each applied when its ticket next runs\n\n1. W2-82: ROLE_SCOPE (already planned, DEC-996).\n2. W2-118: every commit id and path a return names is resolved against git; one that does not resolve is named in the inbox item.\n3. W2-93 / W2-81: the proving ground's planted problems also measure reviewer recall (the share of planted defects a review finds), reported per model.\n4. W2-11: the reviewer states, per finding, what evidence would reverse it.\n5. W2-115: a round whose in-scope blocking findings are not fewer than the previous round's is reported as not converging, at once.\n6. W2-11: the status block's counts (leads, queue, inbox, merged, closed, pings) are generated from files; a typed count is a slip.\n7. W2-115: a test revision shows case and assertion counts before and after; a deleted case, a new skip or xfail, or a loosened comparison blocks unless the owner named it.\n",
      "tokens": 241
    },
    {
      "id": "DAEO-emq1",
      "path": ".tickets/DAEO-emq1.md",
      "text": "  - 'The close''s clean clone is a warm one kept between closes (reset, stores kept), replaced by a fresh one when it cannot be reset Verify: two planted closes in a row: the second reuses the first''s clone (same folder, reset, stores kept); a planted clone that cannot be reset is replaced by a fresh one and the record says so. [DEC-1001 (b), SMART-WORK-2]'\n  - 'READY is computed, not declared: each reviewer''s probe record carries a structured verdict per KPI line (pass or fail, each finding''s scope in or out, ordinary work yes or no, consequence fails open, loses work or other); the close refuses only on a finding that is in scope, reachable in ordinary work and fails open or loses work; a malformed or incomplete verdict refuses (fail closed); a verdict written by the ticket''s lead over a reviewer''s is refused Verify: planted probe records: a complete structured verdict per KPI line with only out-of-scope or non-ordinary findings gives READY; one in-scope, reachable, fails-open finding refuses; a malformed or incomplete verdict refuses; a verdict written by the ticket''s lead over a reviewer''s is refused. [DEC-1010 item 1, SMART-WORK-3] (folds W2-117 S7)'\n",
      "tokens": 296
    },
    {
      "id": "DAEO-6w5n",
      "path": ".tickets/DAEO-6w5n.md",
      "text": "- src/gov/watch/**\n- src/gov/launch/**\n- tests/unit/watch/test_w2_121d*\n- tests/unit/launch/test_w2_121d*\nest_loc: 400\nkpis:\n  success:\n  - '`gov watch` wakes its caller when a lead''s worktree gains a commit whose subject marks a key result (a probe record, a measure, a package, a baseline) and when a lead returns, each once, named [DEC-952 item 3, DEC-983, DEC-982]; where a dispatcher runs, gov watch only reads its inbox and never marks a return seen Verify: a planted lead worktree gains a commit marking a key result (probe record, measure, package, baseline) and a lead returns: `gov watch` wakes its caller once for each, named; with a dispatcher running, `gov watch` only reads the inbox and the return is not marked seen. [DEC-1009, SMART-WORK-3] [moved from W2-118 S1, DEC-1083]'\n  - 'A commit brought into a lead''s branch by a merge from the integration branch never wakes the caller Verify: a planted lead branch merged from the integration branch: `gov watch` does not wake its caller for the merged-in commit. [DEC-1003, SMART-WORK-3] [moved from W2-118 S3, DEC-1083]'\n",
      "tokens": 272
    },
    {
      "id": "304c7922244ef36df1e0a7cd",
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "text": "## 4. Options\n\n- **(a) Practices now, plus KPI lines on existing tickets; no new ticket (recommended).**\n  - **The practices (NOW), all in the CTO's tools lane, about half a day:**\n    - mechanise the second slip;\n    - the status block generated from files;\n    - remaining watchers and chain starts moved into the dispatcher;\n    - the dispatcher watches the sentinel's heartbeat;\n    - checkpoint size and order;\n    - measurement in tool commits;\n    - a different reviewer model on fail-open FULL tickets;\n    - the moderator's triage before a round is declared;\n    - a weekly report of net ticket growth.\n  - **About 14 KPI lines across W2-115, W2-117, W2-121, W2-118, W2-11, W2-08, W2-93/W2-81 and W2-82.** Most extend\n    SMART-WORK-3, which is already proposed. Under DEC-1004, each is applied when its ticket next runs.\n  - **Two Wave 3 rows:** impossible-task canaries; an independent audit sample of the orchestrator's commits. A third,\n    the dead-man's switch as a product feature, is already parked.\n  - **Cost:** about 14 KPI lines and no added ticket count (DEC-974 not triggered).\n  - **Risk:** W2-115 and W2-121 grow a little. W2-115 takes four lines (rows 5, 7, 8, 14).\n",
      "tokens": 298
    },
    {
      "id": "5502c1b5b9156c0dc9414ac8",
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "text": "  - **External:** 25 sources. 17 were fetched or searched today; 8 are cited from known papers and were not re-fetched\n    (each is marked in \u00a77).\n  - **Internal:** the register (DEC-990 to DEC-1009, plus the older rules they build on), the CTO's checkpoint, the\n    slips log, the guard's refusal log, brief gaps, the audit, CAPACITY-1, P1-W2-81-LOOP, P1-DISPATCH-1, the dispatcher\n    README, the prompt's \u00a70, the kernel's roles, skills and hooks, and DEC-1010 as written in the auditor brief and\n    SMART-WORK-3.\n  - The table puts each external failure mode next to its incidents here.\n- **No benchmarking skill exists.** Neither `template/governance/kernel/skills/` nor `.claude/skills/` has one; the\n  discovery skill's method was used instead.\n\n---\n\n",
      "tokens": 190
    }
  ],
  "supplementary_query": "gov dispatch: one pass a minute keeps the machine full and the work moving without depending on any agent session: the ready list started when there is room for each job's peak, returns into an inbox, approved landings as one batch, the true status (DEC-1007, DEC-1008)\n`gov dispatch tick` does one pass and exits; passes never overlap (a lock); an OFF file stops them; the host runs it every minute (cron or a service) and after a restart, outside any agent session; `gov dispatch status` prints the status Verify: a planted project: two `tick` calls started together run one pass (the second exits at the lock, writing nothing); a planted OFF file makes `tick` exit without starting anything; the host's cron or service entry runs it every minute and after a restart (read from the installed entry, no agent session in its chain); `gov dispatch status` prints the status. [DEC-1007]\nIt starts at most one session per pass, staggered, and only an entry of the orchestrator's ready list (the WBS order is the orchestrator's, never the dispatcher's), and only when the ticket's claim is committed on the integration branch and in its worktree, the worktree clean, the brief complete, the ticket not running and with no unread return, and the gate (W2-20) and disk open; each skipped entry is named with its reason Verify: planted ready lists with several entries: one session starts per pass, staggered; an entry not on the orchestrator's list is never started; entries with an uncommitted claim, an unclean worktree, an incomplete brief, a running ticket, an unread return, a shut gate or a full disk are each skipped and named with their reason. [DEC-1007, DEC-995, DEC-944 item 2]\nPeaks, not the moment: from the history of each kind of job (a lead's heavy steps, a rebuild, a close's or the queue's run, a full check) it keeps each kind's measured peak (CPU and memory) and starts new work only when the machine has room for the new job's peak plus the peaks still ahead for the work already running; the figures and their dates are in its status and refreshed from the history at least daily; its memory floor and working size are the gate's (W2-20 S8 and S9), and memory admission stays W2-20's S6 Verify: planted job histories for each kind of job: the status prints each kind's peak (CPU and memory) with its date, refreshed from the history within a day; a start is refused when the room is under the new peak plus the peaks ahead and made when it is over; the memory floor and working size read are the gate's. [DEC-1008] [re-worded, DEC-1084]\nEvery finished session's return becomes one inbox item, once; a start that never ran becomes one inbox item; an item unread past a configured time raises an escalation the host's notifier pushes to the orchestrator's owner Verify: a planted finished session: one inbox item, and none more on the next pass; a planted start that never ran: one inbox item; a planted item unread past the configured time: one escalation pushed by the notifier stub to the orchestrator's owner. [DEC-1007, DEC-998]\nA status file every pass: the sessions running counted from the processes (the launcher's identity marker), the load, memory, the gate, the slots held, the peaks ahead, the queue, the inbox; a pass that fails says so at the top of the status, never a stale file that looks current Verify: after a planted pass the status file holds the running sessions (counted from processes by the launcher's identity marker), load, memory, gate, slots held, peaks ahead, queue and inbox; after a planted failing pass the top line says the pass failed and the file is not a stale one that looks current. [DEC-1007]\nNothing project-specific in the code; planted tests for every refusal (an uncommitted claim, a shut gate, no room for a peak, a running ticket, an unread return, a malformed list line, a hung command, a crash after a launch); an independent review before it is switched on; this repository's dispatcher (the CTO's tool) moves onto it Verify: grep of the dispatcher code for this repository's branches, paths and ticket ids finds 0 lines; planted tests exist and fail for each named refusal (uncommitted claim, shut gate, no room for a peak, running ticket, unread return, malformed list line, hung command, crash after a launch); the independent review's record exists before the dispatcher is switched on; this repository's tool is no longer the one running. [DEC-1007, DEC-982, DEC-1003]\nThe dispatcher never starts a third review round for a ticket (its review rounds counted from its probe records); such a ticket goes to the inbox as an owner item Verify: a planted ticket with two probe records: its next review launch is not started and the ticket becomes one owner item in the inbox; a planted ticket with one probe record is started. [DEC-1010 item 1, SMART-WORK-3]\nNo watcher needs re-arming; every wake is an inbox item a pass writes Verify: a planted run across a restart: every wake the caller gets is an inbox item written by a pass, and no watcher process or re-arm step is present or needed. [DEC-1014 item 2, SMART-WORK-4 line 12] (folds W2-118 S5)\nEvery commit id and path a return names is resolved against git; one that does not resolve is named in the inbox item Verify: planted returns naming a real commit and path and a nonexistent one: the inbox item for the second names the one that does not resolve; the first names none. [DEC-1014 item 2, SMART-WORK-4 line 2] [moved from W2-118 S4, DEC-1083]\nThe ready list the dispatcher reads may come from gov plan --ready (W2-136), reviewed and committed by the orchestrator; the dispatcher starts only what is on it, and its own order is never its choice Verify: a planted list from `gov plan --ready` committed by the orchestrator: the dispatcher starts only entries on it and in no order of its own; an entry not on it is not started. [DEC-1007 (2), DEC-1088 (1)] [added, DEC-1088]\nA session started for an entry not on the ready list, not ready, already running, or without room for its peak; a ticket landed that was not approved, or twice; a return never put in the inbox; a lead count not from the processes Verify: planted passes with an off-list entry, a not-ready one, a running one and one with no room for its peak: no session starts for any; an unapproved ticket and an approved one a second time are not landed; a finished return missing from the inbox, and a lead count taken from anything but processes, are each absent. [DEC-1007, DEC-1008]",
  "further_batch": [
    {
      "id": "DAEO-zkr9",
      "path": ".tickets/DAEO-zkr9.md"
    },
    {
      "id": "DEC-1011",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "f93e91f57dfd8a365a442e80",
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
    },
    {
      "id": "DAEO-lrre",
      "path": ".tickets/DAEO-lrre.md"
    },
    {
      "id": "DAEO-qzrq",
      "path": ".tickets/DAEO-qzrq.md"
    },
    {
      "id": "0be878db3dd9d3d79d74543c",
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
    },
    {
      "id": "3f0eb0255171a42f448100af",
      "path": "governance/project/orchestration/packages/SMART-WORK-3.md"
    },
    {
      "id": "8cefd711bf885fc51a28d088",
      "path": "tests/acceptance/W2-20/README.md"
    },
    {
      "id": "e0dba4f9ae64c3db6a87dd69",
      "path": "tests/acceptance/W2-20/test_w2_20_cpu.py"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "a919c129625c19be83999f6d",
          "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
        },
        {
          "id": "15b4a12cbbc67642cbad76ad",
          "path": "governance/project/orchestration/packages/SMART-WORK-5.md"
        },
        {
          "id": "a42deaceda362e9fd06f8898",
          "path": "governance/project/orchestration/packages/P1-DISPATCH-1.md"
        },
        {
          "id": "DAEO-j9z6",
          "path": ".tickets/DAEO-j9z6.md"
        },
        {
          "id": "DAEO-zkr9",
          "path": ".tickets/DAEO-zkr9.md"
        },
        {
          "id": "0a3d37b32ea5c6a4b2ba87ea",
          "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DEC-1022",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "DAEO-dy7j",
          "path": ".tickets/DAEO-dy7j.md"
        },
        {
          "id": "CONTRACT-v4",
          "path": "docs/contract/CONTRACT_v4.md"
        },
        {
          "id": "a2ec75c865af839325a6ce59",
          "path": "docs/contract/contract.yaml"
        },
        {
          "id": "OWNER-DECISION-P2-0008",
          "path": "docs/imported/OWNER-DECISION-P2-0008.md"
        },
        {
          "id": "OWNER-DECISION-P2-0008",
          "path": "docs/imported/OWNER-DECISION-P2-0008.md"
        },
        {
          "id": "DAEO-5rgj",
          "path": ".tickets/DAEO-5rgj.md"
        },
        {
          "id": "DAEO-5rgj",
          "path": ".tickets/DAEO-5rgj.md"
        },
        {
          "id": "2808533d411a951d767d749b",
          "path": "governance/project/orchestration/packages/SMART-WORK-5.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DAEO-t8mp",
          "path": ".tickets/DAEO-t8mp.md"
        },
        {
          "id": "53d0c84957753433c4e1bf16",
          "path": "governance/project/orchestration/packages/SMART-WORK-5.md"
        },
        {
          "id": "DAEO-7r5e",
          "path": ".tickets/DAEO-7r5e.md"
        },
        {
          "id": "DAEO-emq1",
          "path": ".tickets/DAEO-emq1.md"
        },
        {
          "id": "DAEO-emq1",
          "path": ".tickets/DAEO-emq1.md"
        },
        {
          "id": "25da94c60a6889c098eada60",
          "path": "docs/plan/WAVE_3_PARKING.md"
        },
        {
          "id": "7ca94abcbb983545cd7274d4",
          "path": "governance/project/orchestration/packages/SMART-WORK-4.md"
        },
        {
          "id": "DAEO-emq1",
          "path": ".tickets/DAEO-emq1.md"
        },
        {
          "id": "DAEO-6w5n",
          "path": ".tickets/DAEO-6w5n.md"
        },
        {
          "id": "304c7922244ef36df1e0a7cd",
          "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "5502c1b5b9156c0dc9414ac8",
          "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
        },
        {
          "id": "DAEO-zkr9",
          "path": ".tickets/DAEO-zkr9.md"
        },
        {
          "id": "DEC-1011",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "f93e91f57dfd8a365a442e80",
          "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
        },
        {
          "id": "DAEO-lrre",
          "path": ".tickets/DAEO-lrre.md"
        },
        {
          "id": "DAEO-qzrq",
          "path": ".tickets/DAEO-qzrq.md"
        },
        {
          "id": "0be878db3dd9d3d79d74543c",
          "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md"
        },
        {
          "id": "3f0eb0255171a42f448100af",
          "path": "governance/project/orchestration/packages/SMART-WORK-3.md"
        },
        {
          "id": "8cefd711bf885fc51a28d088",
          "path": "tests/acceptance/W2-20/README.md"
        },
        {
          "id": "e0dba4f9ae64c3db6a87dd69",
          "path": "tests/acceptance/W2-20/test_w2_20_cpu.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "0be878db3dd9d3d79d74543c",
      "reason": "budget exceeded"
    },
    {
      "id": "3f0eb0255171a42f448100af",
      "reason": "budget exceeded"
    },
    {
      "id": "8cefd711bf885fc51a28d088",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-lrre",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-qzrq",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-zkr9",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1011",
      "reason": "budget exceeded"
    },
    {
      "id": "e0dba4f9ae64c3db6a87dd69",
      "reason": "budget exceeded"
    },
    {
      "id": "f93e91f57dfd8a365a442e80",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 29724,
  "budget": {
    "limit": 30000,
    "used": 29724
  },
  "left_out": {
    "count": 5,
    "superseded": [
      "DEC-798",
      "DEC-869",
      "DEC-875",
      "DEC-876",
      "DEC-960"
    ],
    "done": []
  },
  "hash": "aabcc52900304ed135a09d7c1d083d9ac4c19653db0d709ea0346f2bad082c6b"
}
