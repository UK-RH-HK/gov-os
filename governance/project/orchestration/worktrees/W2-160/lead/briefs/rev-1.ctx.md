{
  "ticket": "DAEO-fd0p",
  "ticket_text": "---\nid: DAEO-fd0p\nstatus: in_progress\ndeps: []\nlinks: [DAEO-wnnz, DAEO-t8mp, DAEO-6lid]\ncreated: 2026-11-11T01:20:19Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-160\ntags: [wave-2, implementation, standard, after-the-lift, orchestration, launch]\nwbs_id: W2-160\ntitle: 'gov wait and the helper watch in the product: a bounded wait on a job''s exit file by pid, and an inbox item when a helper or a launched worker dies or goes silent (EMERGENCY-TOOLS-1 D3, D17; DEC-1079, DEC-1112 (3), DEC-1073 (4))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/wait/**\n- src/gov/session_watch/helper_watch.py\n- src/gov/check/commands.py  # the one line that records `wait` (the precedent: W2-20's `resources`)\n- tests/unit/wait/**\n- tests/unit/session_watch/test_w2_160*\n- docs/changes/W2-160-evidence.md\n- src/gov/session_watch/command.py  # the helper-watch action and its entry in the act and path list, about 20 lines (DEC-1153 (2))\n- docs/probes/DAEO-fd0p/**  # the probe record (PKG-W2-160-IFACE-1, the CTO)\nreads:\n- src/gov/launch/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/check/commands.py\nwaits_on:\n- ref: DAEO-6lid\n  reason: 'W2-159 creates src/gov/session_watch/; the helper watch is one more module there'\nkpis:\n  success:\n  - 'S1 `gov wait <exit-file> [<max-s>]` blocks until the exit file is non-empty or `<max-s>` seconds pass (default and ceiling 570, so a wait ends under a 600-second tool limit; a larger value is capped and says so), then prints the job''s log tail and its exit code; it waits on the file, never on a process name. Verify: a stand-in job writing its exit file after 2 seconds: its code is printed and returned; a never-written file at `<max-s>` 1: exit 124 \"RUNNING\"; a value of 9999 is capped at 570 with a line saying so [DEC-1079, DEC-1052]'\n  - 'S2 When a pid file sits beside the exit file (`<base>.pid`, as `gov launch` writes it), the job''s liveness is asked of its pid alone: a job gone without its exit file ends the wait at once with exit 125 \"GONE\", never waits to the bound; an exit file holding no number, or a usage error, is exit 2. Verify: a stand-in job killed before it writes its exit file: exit 125 within one poll period; a second process of the same name left running does not keep the wait alive [DEC-1073 (4), DEC-1079]'\n  - 'S3 The helper watch (`gov session-watch helper-watch`, one pass or a loop every 5 minutes, ending after a maximum of 24 hours with one \"ended\" line so the caller re-arms it) writes one inbox item, once per condition, when an in-session helper of the registered orchestrator session ends on an API or network error as its last entry, or is not finished and has written nothing for 30 minutes; and when a launched worker (found by its pid file) is gone without its exit file, or its exit file appeared with a non-zero code or an error in its result. The item names the helper or the worker''s log and its last line. Verify: planted helper transcripts and worker pid and exit files, one per condition, and a healthy one: one item each for the first four, none for the healthy one, none again on the next pass [DEC-1112 (3), DEC-1073 (4)]'\n  - 'S4 The helper watch reads names, timestamps and error codes only, never a message''s text; it matches no process by name; it writes only the inbox, its own state file and its own log; only transcripts whose last entry is inside a window (default 24 hours) are looked at. Verify: a filesystem-spy and a text-canary test: a planted message text never appears in an item or the log; a search of the module for a process-name match finds none [DEC-1112 (3), DEC-1073 (4), DEC-495]'\n  failure:\n  - 'A wait that outlives its bound, or that waits for a job whose process is gone. Verify: S1''s never-written exit file at `<max-s>` 1 returns exit 124 within the bound, and S2''s killed stand-in job returns exit 125 within one poll period with a same-name process still running'\n  - 'A process matched by name, or a message''s text copied into an item or a log. Verify: S4''s text-canary test (the planted message text found 0 times in items and log) and its search of the module for a process-name match (none found)'\n  - 'The same condition written to the inbox twice. Verify: S3''s planted conditions run through two passes: the inbox holds one item per condition after the second pass, and none is added by it'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1079\n- DEC-1052\n- DEC-1073\n- DEC-1112\n- DEC-495\n- DEC-1119\n- DEC-1109\nest_loc: 260\nacceptance_tests:\n  path: tests/acceptance/W2-160/\n  author: 'independent-test-designer (MR-3), from these KPI lines; stand-in jobs, planted transcripts and pid files, never a live session'\ntrack: A\nlist_rows: []\n---\n# W2-160 gov wait and the helper watch\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 rows D3 and D17; **after the lift**, not before EXAMIN's copy.\n\n- **Problem.** The role templates name three scripts for the lead's loop: `lead_verify.sh`, `launch_worker.sh` and `wait_for.sh` (W2-128 TPL-3 S5; the facts file's `verify`, `launch` and `wait`). All three are the CTO's scratch tools. `gov launch` (W2-56) replaces the launch; the verify run is W2-115's (see the audit's proposed line); the wait has no product form, and neither has the helper watch, which exists because two helpers died of a network fault on 2026-11-10 and the CTO sat idle for 7 hours (`helper_watch.py`'s own header).\n- **Approach.** `gov wait` is `wait_for.sh` as a command, with the exit codes the script gives; the helper watch is `helper_watch.py` as a module beside W2-159's. Alternative: put the wait in `gov launch` as `--wait` (rejected: a lead also waits on a verify run and a close).\n- **Interface.** `gov wait <exit-file> [<max-s>]` exits with the job's code, 124 running, 125 gone, 2 usage. `gov session-watch helper-watch [--every 300] [--max 86400] [--stale-min 30] [--window-h 24] [--once]`. The inbox is the project's inbox folder.\n- **Non-goals.** No change to `gov launch`'s pid and exit file names; the dead-man's switch (W3-P16) and the Stop checks (W2-159) are not here.\n- **Rabbit holes.** Waiting on a process name (never; DEC-1073 (4)); a wait longer than the tool's own limit.\n\n[DEC-1079, DEC-1112 (3), DEC-1073 (4), DEC-1119 (5)]\n\n## Onto EXAMIN's path (the owner, DEC-1148 (2), item 4 (a1), 2026-11-12)\n\n`gov wait` is the product command an adopted project's facts file names for `wait_for`; every brief's envelope names it (`brief.md:35`), so EXAMIN's copy builds no brief until this lands. Starts after W2-159 lands (the Stop checks it builds on); priority raised for the path.\n\n## P-W2-160-1 decided (the owner, DEC-1153 (2), 2026-11-12) and PKG-W2-160-IFACE-1 (the CTO, delegated P2)\n\n(a): `src/gov/session_watch/command.py` added for the `helper-watch` action (about 20 lines; nothing else in the file changes). The Interface takes the lead's I1 (`gov wait`) and I2 (the helper watch) as written; the lead's package, word for word:\n\ntask: DAEO-fd0p\n# PKG-W2-160-IFACE-1: `gov session-watch helper-watch` needs a path the ticket does not allow, and the helper watch's files are not stated\n\n## Question\nThe ticket's Interface names `gov session-watch helper-watch [...]`. `gov session-watch` is\n`src/gov/session_watch/command.py` (W2-159). Its argparse accepts only `stop-check` (`add_arguments`, the `action`\nchoices), its `run` sends every call to the Stop checks, and its `ACT_PATHS` is `.gov-runtime/session-watch/**` alone.\nA `helper-watch` action needs that file changed, and the file is not in allowed_paths (only `helper_watch.py` is).\nThe ticket also leaves out the product's paths and test hooks for the helper watch (I2 below), and the probe folder\n`docs/probes/DAEO-fd0p/` is not in allowed_paths. Which of these does the CTO choose?\n\n## Options\n(a) **Widen and state (recommended).** Add `src/gov/session_watch/command.py` (the `helper-watch` action beside\n    `stop-check`, the call to `helper_watch.run`, and `.gov-runtime/dispatch/inbox/**` added to `ACT_PATHS`) and\n    `docs/probes/DAEO-fd0p/**` to allowed_paths, and put I1 and I2 below into the ticket's Interface. Cost: about 20\n    lines in a W2-159 file. W2-159 is merged and closed, so no one else is editing it. One ticket edit. The test\n    design starts as soon as the ticket is edited.\n(b) **Keep the paths, change the command.** The helper watch becomes the module command\n    `python3 -m gov.session_watch.helper_watch [...]`, so only `helper_watch.py` is touched. Cost: S3's command text\n    changes. The watch runs outside `gov`'s act class and ACT_PATHS check. `gov --help` does not list it.\n    `check/commands.py` gets a `RECORDED_MODULE_COMMANDS` line, which is not the line the ticket names. I1 and I2 are\n    still needed.\n(c) **Split.** Ship `gov wait` (S1, S2, F1) now and the helper watch (S3, S4) later. This needs a new ticket or a\n    split, so the owner has to decide it (DEC-974). Cost: the wait reaches EXAMIN sooner; the helper watch waits for\n    the owner.\n\n## Recommendation\n(a), confidence high. The ticket's own Interface and S3 name `gov session-watch helper-watch`. W2-20's `resources`\nalready writes its one inbox item under `.gov-runtime/dispatch/inbox/` and declares that path in its ACT_PATHS\n(src/gov/resources/command.py:28, backstop.py:17-18, 126-127), so the helper watch can do the same.\n\n## What it blocks\nThe whole ticket. The test designer needs the helper watch's seams (I2) and cannot write S3 or S4 without them.\n`gov wait` (S1, S2) is on EXAMIN's path (DEC-1148 (2)). Under (a), the S1 and S2 tests can start the moment the\nticket is edited.\n\n## Accept in one line\n\"PKG-W2-160-IFACE-1 (a): allowed_paths add src/gov/session_watch/command.py and docs/probes/DAEO-fd0p/**; the\nInterface takes I1 and I2 as written.\"\n\n## I1 `gov wait <exit-file> [<max-s>]` (src/gov/wait/command.py)\n- `CLASS = \"read\"`, `CHILD_EXIT_CODE = True` (no envelope). It exits with the job's code % 256; 124 RUNNING; 125\n  GONE; 2 for a usage error, a `<max-s>` that is not a number, or an exit file holding no number.\n- `<base>` is the exit file's path less `.exit`. The pid file is `<base>.pid`. Liveness is checked by that pid alone:\n  `os.kill(pid, 0)`, and a `/proc/<pid>/stat` state of `Z` counts as gone. It never matches a process by name and\n  calls no `proc.sh`.\n- Lines, in wait_for.sh's form with the `wait:` prefix: `wait: DONE exit <n> (<file>)`,\n  `wait: RUNNING after <s>s: <file>`, `wait: GONE: the job's process (<pid>) exited without writing <file>`,\n  `wait: <file> holds no exit code: '<text>'`, and on stderr `wait: <max-s> <v> capped at 570`.\n- The tail comes from `GOV_WAIT_LOG`, else the first of `<base>.log`, `<base>.json`, `<base>.txt` that exists. For a\n  JSON log it prints the last result object's `session_id`, `is_error` and `num_turns` and the end of its `result`.\n  Then `<base>.summary`, if present.\n- Test hooks (environment): `GOV_WAIT_EVERY` (poll period in seconds, default 5; fractions allowed) and\n  `GOV_WAIT_LINES` (30).\n- check/commands.py: `wait` is added to `RECORDED_GOV_COMMANDS`.\n\n## I2 `gov session-watch helper-watch [--every 300] [--max 86400] [--stale-min 30] [--window-h 24] [--once] [--root <project>]` (src/gov/session_watch/helper_watch.py)\n- Registered session: `<root>/.gov-runtime/session-watch/session.txt` (W2-159's `state.registered`). With no\n  session file, it looks at no helpers.\n- Helpers: `GOV_SESSION_WATCH_SUBAGENTS`, else\n  `~/.claude/projects/<the root's absolute path, each character not a letter, digit or \"-\" as \"-\">/<session>/subagents/`;\n  the files `agent-<id>.jsonl` and `agent-<id>.meta.json` (`finished`, `description`, `agentType`).\n- Workers: W2-159's configuration `pid_globs` (default `.gov-runtime/**/*.pid`, relative to the root). Each pid file\n  is `<base>.pid`, with `<base>.exit` and `<base>.json` (the log) beside it. Liveness is checked as in I1 (one shared\n  function in gov.wait).\n- Clock: `GOV_SESSION_WATCH_NOW` (epoch seconds, as W2-159). The watch starts at the clock's value. An exit file\n  counts only if its mtime is at or after the start less `--every`.\n- Conditions, once each, recorded in a state file that only grows (DEC-1140 (1)(a)): `api-error` (the last\n  assistant/user/system entry has `isApiErrorMessage` or `apiError`); `stalled` (not `finished`, and no entry for\n  `--stale-min` minutes); `worker gone` (no `.exit`, and the pid is gone); `worker ended with an error` (the exit code\n  is not 0, or the last JSON object has `is_error` or `api_error_status`). A transcript whose last entry is older than\n  `--window-h`, or a pid file whose mtime is older, is skipped.\n- Writes: items in `<root>/.gov-runtime/dispatch/inbox/<UTC yyyymmdd-HHMMSS>-helper-watch[-<n>].txt` (opened with\n  `x`, so no item overwrites another), each naming the helper's id or the worker's log and its last line; the state\n  file `<root>/.gov-runtime/session-watch/helper-watch-state.json`; the log\n  `<root>/.gov-runtime/session-watch/helper-watch.log` (one JSON line per pass: at, conditions, item names).\n- Last line: names, entry types, timestamps, tool names, error codes, and the client's fixed synthetic API-error text\n  only (`model == \"<synthetic>\"`); never a message's own text.\n- Stdout: `HELPER_WATCH item <path>` for each item; when `--max` is reached,\n  `HELPER_WATCH ended after <s> s; <n> item(s) written; re-arm it`. Exit 0. A W2-159 configuration error: exit 1,\n  named.\n\n## Facts for the record (no decision needed)\n- S2 says \"as `gov launch` writes it\", but `gov launch` in this tree writes no `<base>.pid`. The `<base>.pid`,\n  `<base>.exit` and `<base>.json` names are `launch_worker.sh`'s. The tests plant the files, so S2 can still be\n  tested; the ticket's wording is wrong and should be noted.\n",
  "authority": [
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
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
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-495",
      "sha256": "3e1bccf9ebb0f60bad28f0e1d29bd3016f9277bf876feac09554d05d4afa3da4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e1bccf9ebb0f60bad28f0e1d29bd3016f9277bf876feac09554d05d4afa3da4",
      "reason": "declared in sources",
      "tokens": 333
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
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
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
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-495",
      "sha256": "3e1bccf9ebb0f60bad28f0e1d29bd3016f9277bf876feac09554d05d4afa3da4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e1bccf9ebb0f60bad28f0e1d29bd3016f9277bf876feac09554d05d4afa3da4",
      "reason": "declared in sources",
      "tokens": 333
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
    }
  ],
  "supplementary": [
    {
      "id": "8f80e5aaf7d40426f7f8bf4a",
      "path": "docs/changes/W2-160-evidence.md",
      "text": "## KPI map\n\n| KPI | code | tests |\n|---|---|---|\n| S1 bounded wait, 570 cap, tail, codes | `wait/command.py` `run`, `_tail` | acceptance `test_s1_wait.py`; unit `tests/unit/wait/test_command.py` |\n| S2 liveness by pid alone, 125 GONE, 2 usage | `wait/liveness.py`, `wait/command.py` | acceptance `test_s2_gone.py`; unit `test_liveness.py` (zombie, pid-file forms) |\n| S3 one item per condition, once | `helper_watch.py` `_helpers`, `_workers`, `_pass`, `_item` | acceptance `test_s3_helper_watch.py`; unit `test_w2_160_helper_watch.py` (name collision `-<n>`, window and stale edges, empty exit file, second pass, configuration error) |\n| S4 names only; no process-name match; writes only inbox, state, log | `helper_watch.py` `_name`, `_describe`; no temporary or lock file | acceptance `test_s4_reads_and_writes.py`; unit text-canary case |\n| F1 wait never outlives its bound / waits for a gone process | sleep cut to the time left; gone pid seen at the next poll | S1 and S2 cases above |\n| F2 no process matched by name, no message text copied | same as S4 | S4 |\n| F3 the same condition never written twice | state file keys only grow | S3 second-pass cases |\n",
      "tokens": 292
    },
    {
      "id": "175983cf65ec25c22b74c677",
      "path": "tests/acceptance/W2-107/test_w2_107_engine_change.py",
      "text": "\"\"\"W2-107: any change to gitleaks or its rules forgets every remembered verdict; a scan that cannot decide still raises.\n\nKPI success 3 (a fingerprint that differs from the cache's clears it before the first read) and success 4's last clause\n(a scan that cannot decide still raises as today); failure 2 (a changed gitleaks or rule set answered from the old\nresults). The engine is changed as the design says a test changes it: another stand-in, with other bytes, first on PATH,\nor the stand-in's own bytes rewritten in place between two processes.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport pytest\n\nimport w2_107_support as support\nfrom gov import secrets\n\npytestmark = support.needs_tools\n\nFILES = {\n    \"docs/alpha.md\": \"W2-107: the alpha page, ordinary text.\\n\",\n    \"docs/beta.md\": \"W2-107: the beta page, ordinary text.\\n\",\n}\nNAME = \"docs/an-ordinary-name.md\"\nADDED_RULE = (\"\\n[[rules]]\\n\"\n              'id = \"w2-107-added\"\\n'\n              'description = \"W2-107: a rule added by the case; it matches nothing the case writes\"\\n'\n              \"regex = '''w2-107-never-written-[0-9]{12}'''\\n\")\n\n\n",
      "tokens": 277
    },
    {
      "id": "DAEO-8a3f",
      "path": ".tickets/DAEO-8a3f.md",
      "text": "  - 'S4 With a `<base>`: the portability family runs only when `<base>..HEAD` touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when `<base>` does not resolve (otherwise it reads \"skipped (no such change)\"), and the tree''s own `gov links --since <base>` runs after the others, as `links: ok (0 new since <base>, M standing)` or `links: NOTICE N new: <the first finding lines>`; it writes only links'' own mark. Without a `<base>` both are left out, named. Verify: planted history with and without a kernel change; a planted tree with and without `src/gov/links/` [DEC-1052, DEC-1073]'\n  - 'S5 It is bounded and cheap: the whole pass on this repository''s main tree ends within the time bound plus 10 seconds, and it reads and writes nothing else (a filesystem-spy test over a planted tree: only the declared checks'' own outputs and links'' mark). Verify: the measured time on this repository, recorded in docs/changes/W2-158-evidence.md [DEC-1052]'\n  failure:\n",
      "tokens": 248
    },
    {
      "id": "DAEO-o5x1",
      "path": ".tickets/DAEO-o5x1.md",
      "text": "  - 'S10 facts.yaml gains ready.new_since (an ISO date, the day this ticket lands) and the schema declares it; W2-128''s acceptance cases still pass. Verify: the schema test and gov accept W2-128 [DEC-1050]'\n  failure:\n  - 'Two runs of gov brief on the same inputs differ (TPL-3 F1).'\n  - 'The ready check refuses a ticket for an advisory item, or lets a ticket missing a required field through as READY (TPL-5 F1, as DEC-1083 amends it).'\n  - 'gov brief writes any file, or reads anything beyond the ticket file, facts.yaml, the kernel templates and the --part/--repair files (a filesystem-spy test).'\nprofile: STANDARD\nsources:\n- DEC-1050\n- DEC-1083\n- DEC-1088\n- DEC-1112\n- DEC-1109\nest_loc: 380\nacceptance_tests:\n  path: tests/acceptance/W2-152/\n  author: independent-test-designer (MR-3), from these KPI lines and W2-128's interface\ntrack: A\nlist_rows: []\n---\n",
      "tokens": 216
    },
    {
      "id": "DAEO-ozyt",
      "path": ".tickets/DAEO-ozyt.md",
      "text": "  - 'S4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument \"abc\"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]'\n  - 'S5 It changes nothing else: it only reads the GPU, the servers'' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]'\n  failure:\n  - 'A process outside the named groups paused or signalled. Verify: S4''s planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure'\n",
      "tokens": 269
    },
    {
      "id": "5f5783d075d168b63d67925c",
      "path": "tests/acceptance/W2-160/README.md",
      "text": "  (600 s old no and 100 s old yes at 300; 600 s old yes at 1000). The window: a transcript whose last entry is 25 h old is skipped and\n  23 h is looked at with `--window-h 24`; 25 h is looked at with 48; a pid file's mtime likewise.\n- Safety: the canary is found 0 times in an item, the state file, the log, standard output or standard error, over two passes; a snapshot\n  of the root, HOME, the temporary folder and the session folder (path, size, mtime) before and after each pass shows only files under\n  `.gov-runtime/dispatch/inbox/`, `helper-watch-state.json` and `helper-watch.log` new or changed (so no lock file); the code of\n  `src/gov/session_watch/helper_watch.py` and of every `.py` under `src/gov/wait/` holds no process-name match (below).\n- The source search reads the CODE: string constants (docstrings left out), names, attributes and imports of the parsed file; whole tokens\n  `pgrep pkill killall pidof psutil proc.sh /cmdline /comm`, the string `\"ps\"` and `ps -`. A comment or a docstring that names one (to say it is\n  not used) is no hit.\n\n",
      "tokens": 266
    },
    {
      "id": "DEC-1135",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1135 \u2014 A process-name match used only to detect, which can only refuse and never stops anything, is outside DEC-1073 (4)\n- **Status:** ACCEPTED (owner, 2026-11-11, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-11)`); standing \u00b7 **Under:** DEC-1073 (4), DEC-1133 (5), DEC-1132 (4) \u00b7 **Source:** the owner's message (chat, 2026-11-11 ~17:45 UTC), confirming the reading ACT-NIGHTLY-RESTART-1's round-1 review raised (F6; `governance/project/orchestration/reviews/ACT-NIGHTLY-RESTART-1-review-r1.md`, package \u00a72.4)\n- **Decision:**\n  - (1) **DEC-1073 (4)'s rule (every wait and every stop by pid or process group, never a name match) governs waits and\n    stops.** A process-name match used only to detect (to decide that the machine is busy), which can only refuse an\n    action (a night of the nightly) and never waits on, signals or stops a process, is outside it, as for `rg` in\n    DEC-1133 (5) D1. `nightly/quiet_check.py`'s detection matches and the wrapper's watchdog count are read so.\n",
      "tokens": 274
    },
    {
      "id": "DEC-1153",
      "path": "docs/DECISION_REGISTER.md",
      "text": "| 0.515 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1127 WITHDRAWN (never in force); DEC-1132 (closes by DEC-953, option D; ADOPT-VERIFY-1 (d) and W2-174; the rg tripwire; the nightly's restart ACT; set-up A's bar to define). Next free id: DEC-1133. |\n| 0.516 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1133 (set-up A's bar; the error path and listing rule first; ACT A; the sample day and the p95; FX6; MEMORY-PROTECTION-1 D1-D3; the floor 3 GiB). Next free id: DEC-1134. |\n| 0.517 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1134 (the two warm-latency reds to accepted_reds until W2-155; linger; the handover). Next free id: DEC-1135. |\n| 0.518 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1135 (a detection-only process-name match that can only refuse is outside DEC-1073 (4); DEC-1073 (4) read with it). Next free id: DEC-1136. |\n| 0.519 | 2026-11-11 | Owner (recorded by the orchestrator, DEC-861): DEC-1136 (the W1-01 exemption first, the two path-map ACTs rebuilt after; every ACT changing tests/acceptance/ carries its own exemption entry in its apply). Next free id: DEC-1137. |\n",
      "tokens": 294
    },
    {
      "id": "OWNER-DECISION-P2-0008",
      "path": "docs/imported/OWNER-DECISION-P2-0008.md",
      "text": "## 9. Anti-stall rule \u2014 active for the remainder of Phase 2\n\nThe 420-minute coordinator-handshake stall and the ~10-hour self-matching `pgrep -f` wait-loop are now binding lessons.\nNo unbounded wait loops. Every wait carries a **maximum elapsed time or iteration count, an observable condition, and a\ndeterministic timeout action**. Prefer tracked PID/process-group state over process-name regex; where pattern matching\nis unavoidable, **prove the waiter cannot match itself**. No worker may remain indefinitely `BLOCKED_ON_COORDINATOR`.\nStates distinguish at least `RUNNING_COMPUTE`, `RUNNING_TOOL`, `BLOCKED_RESOURCE`, `BLOCKED_ON_COORDINATOR`,\n`BLOCKED_ON_OWNER`, `STALLED`, `COMPLETE`, with `last_progress_at` freshness. **Rising elapsed time with unchanged\nstatus is a stall signature.** Reconcile the task registry against live process state, output freshness and worker\nreports. **Never tell the owner work is \"still running\" from a stale observation** \u2014 obtain current evidence first. A\nsleeping waiter is not productive work.\n\n",
      "tokens": 259
    },
    {
      "id": "L-0075",
      "path": "docs/lessons/L-0075.md",
      "text": "---\nid: L-0075\ntype: lesson\nstatus: ACTIVE\nstate_class: HISTORICAL\nlifecycle: approved\nscope: framework\nseverity: high\nconstrains: [DAEO-wqd6]\n---\n\nDuring Phase 2, two unbounded wait incidents occurred. A coordinator-handshake stall ran for 420 minutes, and a self-matching `pgrep -f` wait-loop ran for approximately 10 hours \u2014 the process's pattern matched its own command line, so the wait condition could never become false.\n\nThese incidents demonstrated that any wait loop without explicit bounds can stall an entire pipeline indefinitely, and that process-name pattern matching can produce self-matches that make the loop logically unfalsifiable.\n\nThe lesson learned was that every wait must carry a maximum elapsed time or iteration count, an observable condition that can actually transition, and a deterministic timeout action. Process-group or tracked-PID state is preferred over process-name regex; where pattern matching is unavoidable, the waiter must be proven unable to match itself.\n\n**Source:** OWNER-DECISION-P2-0008 (OD-P2-08) \u00a79, \"Anti-stall rule \u2014 active for the remainder of Phase 2.\"\n",
      "tokens": 277
    }
  ],
  "supplementary_query": "gov wait and the helper watch in the product: a bounded wait on a job's exit file by pid, and an inbox item when a helper or a launched worker dies or goes silent (EMERGENCY-TOOLS-1 D3, D17; DEC-1079, DEC-1112 (3), DEC-1073 (4))\nS1 `gov wait <exit-file> [<max-s>]` blocks until the exit file is non-empty or `<max-s>` seconds pass (default and ceiling 570, so a wait ends under a 600-second tool limit; a larger value is capped and says so), then prints the job's log tail and its exit code; it waits on the file, never on a process name. Verify: a stand-in job writing its exit file after 2 seconds: its code is printed and returned; a never-written file at `<max-s>` 1: exit 124 \"RUNNING\"; a value of 9999 is capped at 570 with a line saying so [DEC-1079, DEC-1052]\nS2 When a pid file sits beside the exit file (`<base>.pid`, as `gov launch` writes it), the job's liveness is asked of its pid alone: a job gone without its exit file ends the wait at once with exit 125 \"GONE\", never waits to the bound; an exit file holding no number, or a usage error, is exit 2. Verify: a stand-in job killed before it writes its exit file: exit 125 within one poll period; a second process of the same name left running does not keep the wait alive [DEC-1073 (4), DEC-1079]\nS3 The helper watch (`gov session-watch helper-watch`, one pass or a loop every 5 minutes, ending after a maximum of 24 hours with one \"ended\" line so the caller re-arms it) writes one inbox item, once per condition, when an in-session helper of the registered orchestrator session ends on an API or network error as its last entry, or is not finished and has written nothing for 30 minutes; and when a launched worker (found by its pid file) is gone without its exit file, or its exit file appeared with a non-zero code or an error in its result. The item names the helper or the worker's log and its last line. Verify: planted helper transcripts and worker pid and exit files, one per condition, and a healthy one: one item each for the first four, none for the healthy one, none again on the next pass [DEC-1112 (3), DEC-1073 (4)]\nS4 The helper watch reads names, timestamps and error codes only, never a message's text; it matches no process by name; it writes only the inbox, its own state file and its own log; only transcripts whose last entry is inside a window (default 24 hours) are looked at. Verify: a filesystem-spy and a text-canary test: a planted message text never appears in an item or the log; a search of the module for a process-name match finds none [DEC-1112 (3), DEC-1073 (4), DEC-495]\nA wait that outlives its bound, or that waits for a job whose process is gone. Verify: S1's never-written exit file at `<max-s>` 1 returns exit 124 within the bound, and S2's killed stand-in job returns exit 125 within one poll period with a same-name process still running\nA process matched by name, or a message's text copied into an item or a log. Verify: S4's text-canary test (the planted message text found 0 times in items and log) and its search of the module for a process-name match (none found)\nThe same condition written to the inbox twice. Verify: S3's planted conditions run through two passes: the inbox holds one item per condition after the second pass, and none is added by it\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "718072378207657f68257b4e",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
    },
    {
      "id": "40e6ffadc08ff84d86173a25",
      "path": "tests/acceptance/W2-160/test_s4_reads_and_writes.py"
    },
    {
      "id": "a8be8f0139f79a951d51b282",
      "path": "tests/acceptance/W2-160/test_s4_reads_and_writes.py"
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
      "id": "DAEO-8a3f",
      "path": ".tickets/DAEO-8a3f.md"
    },
    {
      "id": "DAEO-ozyt",
      "path": ".tickets/DAEO-ozyt.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "8f80e5aaf7d40426f7f8bf4a",
          "path": "docs/changes/W2-160-evidence.md"
        },
        {
          "id": "175983cf65ec25c22b74c677",
          "path": "tests/acceptance/W2-107/test_w2_107_engine_change.py"
        },
        {
          "id": "DAEO-8a3f",
          "path": ".tickets/DAEO-8a3f.md"
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
          "id": "5f5783d075d168b63d67925c",
          "path": "tests/acceptance/W2-160/README.md"
        },
        {
          "id": "DEC-1135",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1153",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "OWNER-DECISION-P2-0008",
          "path": "docs/imported/OWNER-DECISION-P2-0008.md"
        },
        {
          "id": "L-0075",
          "path": "docs/lessons/L-0075.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "718072378207657f68257b4e",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "40e6ffadc08ff84d86173a25",
          "path": "tests/acceptance/W2-160/test_s4_reads_and_writes.py"
        },
        {
          "id": "a8be8f0139f79a951d51b282",
          "path": "tests/acceptance/W2-160/test_s4_reads_and_writes.py"
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
          "id": "DAEO-8a3f",
          "path": ".tickets/DAEO-8a3f.md"
        },
        {
          "id": "DAEO-ozyt",
          "path": ".tickets/DAEO-ozyt.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "40e6ffadc08ff84d86173a25",
      "reason": "budget exceeded"
    },
    {
      "id": "718072378207657f68257b4e",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-6lid",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-6lid",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-8a3f",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-8a3f",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-ozyt",
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
      "id": "a8be8f0139f79a951d51b282",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 11970,
  "budget": {
    "limit": 12000,
    "used": 11970
  },
  "left_out": {
    "count": 6,
    "superseded": [
      "DEC-048",
      "DEC-798",
      "DEC-869",
      "DEC-875",
      "DEC-876",
      "DEC-960"
    ],
    "done": []
  },
  "hash": "7d8688c9d6801b0043ff6d84c3bcb7b17a50b1905defce61afae88079d104cce"
}
