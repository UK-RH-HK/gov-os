{
  "ticket": "DAEO-ifgf",
  "ticket_text": "---\nid: DAEO-ifgf\nstatus: in_progress\ndeps: [DAEO-cb2b]\nlinks: [DAEO-cb2b]\ncreated: 2026-11-12T01:50:00Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-121b\ntags: [wave-2, dispatch, full]\nwbs_id: W2-121b\ntitle: \"gov dispatch, part b: landing: the landing hand-off, no wait on a non-conflicting close, the nightly never kept from starting\"\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: [DAEO-cb2b]\nwaits_on: []\nreads:\n- src/gov/dispatch/**\n- src/gov/resources/**\n- governance/project/orchestration/tools/dispatch/**  # the CTO's dispatcher, a reference only\n- .tickets/DAEO-cb2b.md  # part a's Interface\nneeds: []\nallowed_paths:\n- src/gov/dispatch/**\n- tests/unit/dispatch/test_w2_121b*\n- src/gov/resources/slots.py  # with the slot line from W2-121c (DEC-1144 (5)), only as that line needs\n- docs/probes/DAEO-ifgf/**  # the probe record (P-W2-121b-1, the CTO, 2026-11-12)\nest_loc: 500\nkpis:\n  success:\n  - 'Every ticket the orchestrator approved to land goes to the project''s landing command (W2-115 (which took W2-117), where it exists; a configured command otherwise) as one batch whenever it is free, the tree clean and on the integration branch, and no close running; never one not approved, never twice (the approvals claimed before the launch); each outcome becomes an inbox item Verify: planted approvals: an approved ticket goes to the landing command as one batch when the tree is clean, on the integration branch and no close runs; an unapproved ticket never goes; an approved one never goes twice (the approval is claimed before the launch); each outcome is an inbox item. [DEC-1007, DEC-989] [re-worded, DEC-1084]'\n  - 'A landing never waits for a close it does not conflict with: a running close blocks a landing only when a ticket it closes is among the landing''s, or while it is committing its records; otherwise the landing goes ahead, and two record commits never collide (retried) Verify: planted closes: a running close with a ticket in the landing''s set blocks the landing, as does one committing its records; a running close with no shared ticket does not block it; two record commits at the same time both land (one retried). [DEC-1014 item 5]'\n  - 'The project''s nightly is never kept from starting by a landing: from a configured time before its start until it has started (its running marker), or a configured latest time, the dispatcher claims no landing; one already running is finalised; the status names the hold Verify: a planted configured hold time before the nightly: from then until its running marker (or the latest time) no landing is claimed, a landing already running is finalised, and the status names the hold. [DEC-1018 item 1]'\n  - 'Every heavy step takes a heavy-job slot (W2-20: test runs, rebuilds, full checks, retrieval measures), so peaks stay capped whenever they come; a heavy step found running outside a slot is named in the status as a finding Verify: a planted heavy step (test run, rebuild, full check, retrieval measure) is shown holding a slot; a planted one running with no slot is named in the status as a finding. [DEC-1008, DEC-979 D1]'\n  failure: []\nnon_goals:\n- the dispatcher core (W2-121, part a) and the other parts\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]\nacceptance_tests:\n  path: tests/acceptance/W2-121b/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\n---\n# W2-121b gov dispatch, part b\n\nSplit from W2-121 (DAEO-cb2b) by the CTO's delegated decision on its run 1's P-W2-121-1 (a) and P-W2-121-3 (a), 2026-11-12: these KPI lines moved word for word; it builds on part a's Interface (in W2-121's ticket) and runs after it. The reference is the CTO's dispatcher (`governance/project/orchestration/tools/dispatch/`), never a target.\n\n## Waits on the owner's K9 decision (DEC-1142 (8), 2026-11-12)\n\nKept for now; whether parts a (closed) and b meet K9's \"a dispatcher\" for EXAMIN's copy is the owner's decision. Not started before it.\n\n## K9 decided (the owner, DEC-1144 (5), P1-E option 1, 2026-11-12)\n\nK9's \"a dispatcher\" (DEC-1008 (2)) is parts a and b. This part gains, word for word, W2-121c's first KPI line (\"Every heavy step takes a heavy-job slot ...\", DEC-1008 (3)), now its last success line, and `src/gov/resources/slots.py` in its paths as that line needs: a widening by the owner's decision (DEC-974). Startable now, on EXAMIN's path; W2-121c (less that line) and W2-121d stay parked.\n\n## Interface (DEC-1052; P-W2-121b-1 (a), the CTO's delegated decision, DEC-1112 (3), 2026-11-12)\n\nAll generic: nothing names this repository; every new key in `governance/project/dispatch.yaml`'s `dispatch:`. Builds on part a's Interface (DAEO-cb2b).\n\n1. **The claim and the batch (S1).** A pass may claim only when: no landing of its own is unfinished, the root (the\n   tree `gov dispatch` runs in) has no tracked change and is on `integration_branch`, no conflicting close (2), no\n   nightly hold (3). It claims by an atomic rename `land.txt` -> `land-claimed-<land id>.txt` (`<land id>` =\n   `land-<UTC stamp>`) *before* the launch; lines whose `<W2>=<head>` is already in `land-done.txt` are dropped from\n   the batch (never twice). The batch: `landing_command` with the token `{approvals}` replaced by one argument per line\n   `<W2>=<head>` (appended at the end when the token is absent), run detached in the root, output\n   `logs/<land id>`, exit code `logs/<land id>.exit`. A later pass finalises it: one line per approval\n   `<W2>=<head> <time> <exit code> <land id>` into `land-done.txt`, one inbox item `<land id>.land.txt`\n   (`log: <land id>`, `W2: <ids space-separated>`, `status: landed` | `failed (exit N)`, `kind: land`), and the\n   claimed file removed. A line not of the form `<W2>=<12-hex>` is never sent and is named in the status.\n2. **Closes (S2).** A running close is a process matching `job_markers[\"close\"]`; the tickets it closes are those of\n   its arguments equal to a W2 id or ticket id in the landing's set. It blocks a landing only when one of them is in\n   the set, or while it commits its records: the root's `.git/index.lock` exists, or the root's tracked changes all\n   lie under `close_record_paths` (a list of path prefixes, default `[]`). Any other close does not block.\n   \"Two record commits never collide\": part b provides `gov.dispatch.landing.commit_records(root, paths, message,\n   trailers, attempts=3, wait_s=2)`, a commit that retries while another holds `index.lock`; two at once both land\n   (one retried). Wiring `gov close` and W2-115 to it is theirs, not in these paths.\n3. **The nightly hold (S3).** `nightly_hold` gains an optional `marker` (a path, relative to the root or absolute): from\n   `from` (local time) no landing is claimed until `marker`'s mtime is later than today's `from`, or until `until`\n   (the latest time; a window with `from` > `until` crosses midnight). Without `marker` the hold lasts until `until`.\n   A landing already claimed is finalised as usual, never stopped; starts and the inbox are not held. Status\n   (`status.json` key `land_hold` and a `status.txt` line): `land: held for the nightly until it starts (from HH:MM,\n   at the latest HH:MM)`. Exit 0.\n4. **Heavy steps (S4).** The heavy steps are the `job_markers` kinds `test`, `rebuild`, `check` and `measure`. Full\n   checks and retrieval measures take the existing `test` slot (`gov resources --slot test -- ...`): no new slot kind,\n   so `src/gov/resources/command.py` (outside the paths) is untouched; `slots.py` gains at most a read helper (the\n   runner pids of the slots held, from `holders()`). A heavy step is in a slot when it or an ancestor is a slot's\n   runner; the status lists each heavy step with its slot (`heavy_steps: [{kind, pid, slot}]`), and one with no slot\n   is a `findings:` entry `heavy step outside a slot: <kind> pid <pid>` (a finding shown, never a failed pass).\n\nExit codes: a landing held (busy, unclean tree, wrong branch, conflicting close, nightly) is exit 0, its reason in\nthe status as `land: <reason>`.\n",
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
      "id": "DAEO-cb2b",
      "sha256": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "reason": "declared in sources",
      "tokens": 1633
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
      "id": "DAEO-cb2b",
      "sha256": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "reason": "declared in sources",
      "tokens": 1633
    }
  ],
  "supplementary": [],
  "supplementary_query": "gov dispatch, part b: landing: the landing hand-off, no wait on a non-conflicting close, the nightly never kept from starting\nEvery ticket the orchestrator approved to land goes to the project's landing command (W2-115 (which took W2-117), where it exists; a configured command otherwise) as one batch whenever it is free, the tree clean and on the integration branch, and no close running; never one not approved, never twice (the approvals claimed before the launch); each outcome becomes an inbox item Verify: planted approvals: an approved ticket goes to the landing command as one batch when the tree is clean, on the integration branch and no close runs; an unapproved ticket never goes; an approved one never goes twice (the approval is claimed before the launch); each outcome is an inbox item. [DEC-1007, DEC-989] [re-worded, DEC-1084]\nA landing never waits for a close it does not conflict with: a running close blocks a landing only when a ticket it closes is among the landing's, or while it is committing its records; otherwise the landing goes ahead, and two record commits never collide (retried) Verify: planted closes: a running close with a ticket in the landing's set blocks the landing, as does one committing its records; a running close with no shared ticket does not block it; two record commits at the same time both land (one retried). [DEC-1014 item 5]\nThe project's nightly is never kept from starting by a landing: from a configured time before its start until it has started (its running marker), or a configured latest time, the dispatcher claims no landing; one already running is finalised; the status names the hold Verify: a planted configured hold time before the nightly: from then until its running marker (or the latest time) no landing is claimed, a landing already running is finalised, and the status names the hold. [DEC-1018 item 1]\nEvery heavy step takes a heavy-job slot (W2-20: test runs, rebuilds, full checks, retrieval measures), so peaks stay capped whenever they come; a heavy step found running outside a slot is named in the status as a finding Verify: a planted heavy step (test run, rebuild, full check, retrieval measure) is shown holding a slot; a planted one running with no slot is named in the status as a finding. [DEC-1008, DEC-979 D1]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 19988,
  "budget": {
    "limit": 25000,
    "used": 19988
  },
  "hash": "4082c471175763eb2a3c3631ee44e5a94bf4676aabe30f1de2c63542955ff5b5"
}
