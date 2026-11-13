# Brief eng-3: engineer for DAEO-fd0p (W2-160), run 3, profile STANDARD, class C2

One change, one line: ROUTE-1 (a), decided by the owner (DEC-1156 (1); the path list itself is DEC-1153 (2)).
`tests/unit/session_watch/test_route.py:19` still asserts W2-159's one-path `ACT_PATHS`; W2-160 added the inbox path
to `src/gov/session_watch/command.py:17`, so the assertion is red. Change that assertion only, to the two-path tuple:

```python
    assert command.act_paths == (".gov-runtime/session-watch/**", ".gov-runtime/dispatch/inbox/**")
```

Nothing else in the file changes, and no other file changes (the ticket allows `test_route.py` for "the ACT_PATHS
assertion only"). Do not touch `src/`, `tests/acceptance/` or any other test.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-160 |
| branch | w2/W2-160 |
| the one path you may change | tests/unit/session_watch/test_route.py (line 19 only) |
| ticket (read its "## Run 3" section) | /home/usain/gov-os-worktrees/W2-160/.tickets/DAEO-fd0p.md |
| the code the assertion describes (read only) | src/gov/session_watch/command.py:17 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## How to work
- Before the edit, run the file and see it red on line 19; after, see it green; then run the folder
  `tests/unit/session_watch` and report its summary line. Every pytest goes through the heavy-slot gate, one line:
  `env TMPDIR=/tmp/w2-160-eng2 HOME=/home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-160/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/session_watch -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (Both folders, /tmp/w2-160-eng2 and the empty home, already exist: never create them; a first engineer was refused a mkdir of them. Run the line exactly as written, without a pipe.)
  A resource gate's refusal is a wait: run it again when it opens; it does not count as a refusal.
- Commit that one path:
  `git commit -m "W2-160 (DAEO-fd0p): test_route asserts session-watch's two ACT_PATHS (ROUTE-1 (a))" --trailer "Task: DAEO-fd0p" --trailer "Role: engineer" --trailer "Implements: DEC-1073, DEC-1112" -- tests/unit/session_watch/test_route.py`
  (`Implements:` only ids from the ticket's `sources:`; DEC-1153 and DEC-1156 go in `discoveries`, not in a trailer.)
  Leave `git status --short` empty.
- One-line commands only; a longer script goes in a file under
  `/home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/eng/`. Literal paths. Never touch
  `.gov-runtime/scratch/lead/`. No install, no network, no `.claude/`, no live session, never a process killed by
  name. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so in your return.

## The ticket's context (from `gov context DAEO-fd0p --role engineer --budget 12000`)

{
  "ticket": "DAEO-fd0p",
  "ticket_text": "---\nid: DAEO-fd0p\nstatus: in_progress\ndeps: []\nlinks: [DAEO-wnnz, DAEO-t8mp, DAEO-6lid]\ncreated: 2026-11-11T01:20:19Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-160\ntags: [wave-2, implementation, standard, after-the-lift, orchestration, launch]\nwbs_id: W2-160\ntitle: 'gov wait and the helper watch in the product: a bounded wait on a job''s exit file by pid, and an inbox item when a helper or a launched worker dies or goes silent (EMERGENCY-TOOLS-1 D3, D17; DEC-1079, DEC-1112 (3), DEC-1073 (4))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/wait/**\n- src/gov/session_watch/helper_watch.py\n- src/gov/check/commands.py  # the one line that records `wait` (the precedent: W2-20's `resources`)\n- tests/unit/wait/**\n- tests/unit/session_watch/test_w2_160*\n- docs/changes/W2-160-evidence.md\n- src/gov/session_watch/command.py  # the helper-watch action and its entry in the act and path list, about 20 lines (DEC-1153 (2))\n- docs/probes/DAEO-fd0p/**  # the probe record (PKG-W2-160-IFACE-1, the CTO)\n- tests/unit/session_watch/test_route.py  # the ACT_PATHS assertion only: the two-path tuple (ROUTE-1 (a), DEC-1156 (1))\n- tests/acceptance/W2-159/test_f4_scope.py  # one test-designer revision: judged only on w2/W2-159 (DEC-1156 (6), as P1-N)\nreads:\n- src/gov/launch/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/check/commands.py\nwaits_on:\n- ref: DAEO-6lid\n  reason: 'W2-159 creates src/gov/session_watch/; the helper watch is one more module there'\nkpis:\n  success:\n  - 'S1 `gov wait <exit-file> [<max-s>]` blocks until the exit file is non-empty or `<max-s>` seconds pass (default and ceiling 570, so a wait ends under a 600-second tool limit; a larger value is capped and says so), then prints the job''s log tail and its exit code; it waits on the file, never on a process name. Verify: a stand-in job writing its exit file after 2 seconds: its code is printed and returned; a never-written file at `<max-s>` 1: exit 124 \"RUNNING\"; a value of 9999 is capped at 570 with a line saying so [DEC-1079, DEC-1052]'\n  - 'S2 When a pid file sits beside the exit file (`<base>.pid`, as `gov launch` writes it), the job''s liveness is asked of its pid alone: a job gone without its exit file ends the wait at once with exit 125 \"GONE\", never waits to the bound; an exit file holding no number, or a usage error, is exit 2. Verify: a stand-in job killed before it writes its exit file: exit 125 within one poll period; a second process of the same name left running does not keep the wait alive [DEC-1073 (4), DEC-1079]'\n  - 'S3 The helper watch (`gov session-watch helper-watch`, one pass or a loop every 5 minutes, ending after a maximum of 24 hours with one \"ended\" line so the caller re-arms it) writes one inbox item, once per condition, when an in-session helper of the registered orchestrator session ends on an API or network error as its last entry, or is not finished and has written nothing for 30 minutes; and when a launched worker (found by its pid file) is gone without its exit file, or its exit file appeared with a non-zero code or an error in its result. The item names the helper or the worker''s log and its last line. Verify: planted helper transcripts and worker pid and exit files, one per condition, and a healthy one: one item each for the first four, none for the healthy one, none again on the next pass [DEC-1112 (3), DEC-1073 (4)]'\n  - 'S4 The helper watch reads names, timestamps and error codes only, never a message''s text; it matches no process by name; it writes only the inbox, its own state file and its own log; only transcripts whose last entry is inside a window (default 24 hours) are looked at. Verify: a filesystem-spy and a text-canary test: a planted message text never appears in an item or the log; a search of the module for a process-name match finds none [DEC-1112 (3), DEC-1073 (4), DEC-495]'\n  failure:\n  - 'A wait that outlives its bound, or that waits for a job whose process is gone. Verify: S1''s never-written exit file at `<max-s>` 1 returns exit 124 within the bound, and S2''s killed stand-in job returns exit 125 within one poll period with a same-name process still running'\n  - 'A process matched by name, or a message''s text copied into an item or a log. Verify: S4''s text-canary test (the planted message text found 0 times in items and log) and its search of the module for a process-name match (none found)'\n  - 'The same condition written to the inbox twice. Verify: S3''s planted conditions run through two passes: the inbox holds one item per condition after the second pass, and none is added by it'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1079\n- DEC-1052\n- DEC-1073\n- DEC-1112\n- DEC-495\n- DEC-1119\n- DEC-1109\nest_loc: 260\nacceptance_tests:\n  path: tests/acceptance/W2-160/\n  author: 'independent-test-designer (MR-3), from these KPI lines; stand-in jobs, planted transcripts and pid files, never a live session'\ntrack: A\nlist_rows: []\n---\n# W2-160 gov wait and the helper watch\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 rows D3 and D17; **after the lift**, not before EXAMIN's copy.\n\n- **Problem.** The role templates name three scripts for the lead's loop: `lead_verify.sh`, `launch_worker.sh` and `wait_for.sh` (W2-128 TPL-3 S5; the facts file's `verify`, `launch` and `wait`). All three are the CTO's scratch tools. `gov launch` (W2-56) replaces the launch; the verify run is W2-115's (see the audit's proposed line); the wait has no product form, and neither has the helper watch, which exists because two helpers died of a network fault on 2026-11-10 and the CTO sat idle for 7 hours (`helper_watch.py`'s own header).\n- **Approach.** `gov wait` is `wait_for.sh` as a command, with the exit codes the script gives; the helper watch is `helper_watch.py` as a module beside W2-159's. Alternative: put the wait in `gov launch` as `--wait` (rejected: a lead also waits on a verify run and a close).\n- **Interface.** `gov wait <exit-file> [<max-s>]` exits with the job's code, 124 running, 125 gone, 2 usage. `gov session-watch helper-watch [--every 300] [--max 86400] [--stale-min 30] [--window-h 24] [--once]`. The inbox is the project's inbox folder.\n- **Non-goals.** No change to `gov launch`'s pid and exit file names; the dead-man's switch (W3-P16) and the Stop checks (W2-159) are not here.\n- **Rabbit holes.** Waiting on a process name (never; DEC-1073 (4)); a wait longer than the tool's own limit.\n\n[DEC-1079, DEC-1112 (3), DEC-1073 (4), DEC-1119 (5)]\n\n## Onto EXAMIN's path (the owner, DEC-1148 (2), item 4 (a1), 2026-11-12)\n\n`gov wait` is the product command an adopted project's facts file names for `wait_for`; every brief's envelope names it (`brief.md:35`), so EXAMIN's copy builds no brief until this lands. Starts after W2-159 lands (the Stop checks it builds on); priority raised for the path.\n\n## P-W2-160-1 decided (the owner, DEC-1153 (2), 2026-11-12) and PKG-W2-160-IFACE-1 (the CTO, delegated P2)\n\n(a): `src/gov/session_watch/command.py` added for the `helper-watch` action (about 20 lines; nothing else in the file changes). The Interface takes the lead's I1 (`gov wait`) and I2 (the helper watch) as written; the lead's package, word for word:\n\ntask: DAEO-fd0p\n# PKG-W2-160-IFACE-1: `gov session-watch helper-watch` needs a path the ticket does not allow, and the helper watch's files are not stated\n\n## Question\nThe ticket's Interface names `gov session-watch helper-watch [...]`. `gov session-watch` is\n`src/gov/session_watch/command.py` (W2-159). Its argparse accepts only `stop-check` (`add_arguments`, the `action`\nchoices), its `run` sends every call to the Stop checks, and its `ACT_PATHS` is `.gov-runtime/session-watch/**` alone.\nA `helper-watch` action needs that file changed, and the file is not in allowed_paths (only `helper_watch.py` is).\nThe ticket also leaves out the product's paths and test hooks for the helper watch (I2 below), and the probe folder\n`docs/probes/DAEO-fd0p/` is not in allowed_paths. Which of these does the CTO choose?\n\n## Options\n(a) **Widen and state (recommended).** Add `src/gov/session_watch/command.py` (the `helper-watch` action beside\n    `stop-check`, the call to `helper_watch.run`, and `.gov-runtime/dispatch/inbox/**` added to `ACT_PATHS`) and\n    `docs/probes/DAEO-fd0p/**` to allowed_paths, and put I1 and I2 below into the ticket's Interface. Cost: about 20\n    lines in a W2-159 file. W2-159 is merged and closed, so no one else is editing it. One ticket edit. The test\n    design starts as soon as the ticket is edited.\n(b) **Keep the paths, change the command.** The helper watch becomes the module command\n    `python3 -m gov.session_watch.helper_watch [...]`, so only `helper_watch.py` is touched. Cost: S3's command text\n    changes. The watch runs outside `gov`'s act class and ACT_PATHS check. `gov --help` does not list it.\n    `check/commands.py` gets a `RECORDED_MODULE_COMMANDS` line, which is not the line the ticket names. I1 and I2 are\n    still needed.\n(c) **Split.** Ship `gov wait` (S1, S2, F1) now and the helper watch (S3, S4) later. This needs a new ticket or a\n    split, so the owner has to decide it (DEC-974). Cost: the wait reaches EXAMIN sooner; the helper watch waits for\n    the owner.\n\n## Recommendation\n(a), confidence high. The ticket's own Interface and S3 name `gov session-watch helper-watch`. W2-20's `resources`\nalready writes its one inbox item under `.gov-runtime/dispatch/inbox/` and declares that path in its ACT_PATHS\n(src/gov/resources/command.py:28, backstop.py:17-18, 126-127), so the helper watch can do the same.\n\n## What it blocks\nThe whole ticket. The test designer needs the helper watch's seams (I2) and cannot write S3 or S4 without them.\n`gov wait` (S1, S2) is on EXAMIN's path (DEC-1148 (2)). Under (a), the S1 and S2 tests can start the moment the\nticket is edited.\n\n## Accept in one line\n\"PKG-W2-160-IFACE-1 (a): allowed_paths add src/gov/session_watch/command.py and docs/probes/DAEO-fd0p/**; the\nInterface takes I1 and I2 as written.\"\n\n## I1 `gov wait <exit-file> [<max-s>]` (src/gov/wait/command.py)\n- `CLASS = \"read\"`, `CHILD_EXIT_CODE = True` (no envelope). It exits with the job's code % 256; 124 RUNNING; 125\n  GONE; 2 for a usage error, a `<max-s>` that is not a number, or an exit file holding no number.\n- `<base>` is the exit file's path less `.exit`. The pid file is `<base>.pid`. Liveness is checked by that pid alone:\n  `os.kill(pid, 0)`, and a `/proc/<pid>/stat` state of `Z` counts as gone. It never matches a process by name and\n  calls no `proc.sh`.\n- Lines, in wait_for.sh's form with the `wait:` prefix: `wait: DONE exit <n> (<file>)`,\n  `wait: RUNNING after <s>s: <file>`, `wait: GONE: the job's process (<pid>) exited without writing <file>`,\n  `wait: <file> holds no exit code: '<text>'`, and on stderr `wait: <max-s> <v> capped at 570`.\n- The tail comes from `GOV_WAIT_LOG`, else the first of `<base>.log`, `<base>.json`, `<base>.txt` that exists. For a\n  JSON log it prints the last result object's `session_id`, `is_error` and `num_turns` and the end of its `result`.\n  Then `<base>.summary`, if present.\n- Test hooks (environment): `GOV_WAIT_EVERY` (poll period in seconds, default 5; fractions allowed) and\n  `GOV_WAIT_LINES` (30).\n- check/commands.py: `wait` is added to `RECORDED_GOV_COMMANDS`.\n\n## I2 `gov session-watch helper-watch [--every 300] [--max 86400] [--stale-min 30] [--window-h 24] [--once] [--root <project>]` (src/gov/session_watch/helper_watch.py)\n- Registered session: `<root>/.gov-runtime/session-watch/session.txt` (W2-159's `state.registered`). With no\n  session file, it looks at no helpers.\n- Helpers: `GOV_SESSION_WATCH_SUBAGENTS`, else\n  `~/.claude/projects/<the root's absolute path, each character not a letter, digit or \"-\" as \"-\">/<session>/subagents/`;\n  the files `agent-<id>.jsonl` and `agent-<id>.meta.json` (`finished`, `description`, `agentType`).\n- Workers: W2-159's configuration `pid_globs` (default `.gov-runtime/**/*.pid`, relative to the root). Each pid file\n  is `<base>.pid`, with `<base>.exit` and `<base>.json` (the log) beside it. Liveness is checked as in I1 (one shared\n  function in gov.wait).\n- Clock: `GOV_SESSION_WATCH_NOW` (epoch seconds, as W2-159). The watch starts at the clock's value. An exit file\n  counts only if its mtime is at or after the start less `--every`.\n- Conditions, once each, recorded in a state file that only grows (DEC-1140 (1)(a)): `api-error` (the last\n  assistant/user/system entry has `isApiErrorMessage` or `apiError`); `stalled` (not `finished`, and no entry for\n  `--stale-min` minutes); `worker gone` (no `.exit`, and the pid is gone); `worker ended with an error` (the exit code\n  is not 0, or the last JSON object has `is_error` or `api_error_status`). A transcript whose last entry is older than\n  `--window-h`, or a pid file whose mtime is older, is skipped.\n- Writes: items in `<root>/.gov-runtime/dispatch/inbox/<UTC yyyymmdd-HHMMSS>-helper-watch[-<n>].txt` (opened with\n  `x`, so no item overwrites another), each naming the helper's id or the worker's log and its last line; the state\n  file `<root>/.gov-runtime/session-watch/helper-watch-state.json`; the log\n  `<root>/.gov-runtime/session-watch/helper-watch.log` (one JSON line per pass: at, conditions, item names).\n- Last line: names, entry types, timestamps, tool names, error codes, and the client's fixed synthetic API-error text\n  only (`model == \"<synthetic>\"`); never a message's own text.\n- Stdout: `HELPER_WATCH item <path>` for each item; when `--max` is reached,\n  `HELPER_WATCH ended after <s> s; <n> item(s) written; re-arm it`. Exit 0. A W2-159 configuration error: exit 1,\n  named.\n\n## Facts for the record (no decision needed)\n- S2 says \"as `gov launch` writes it\", but `gov launch` in this tree writes no `<base>.pid`. The `<base>.pid`,\n  `<base>.exit` and `<base>.json` names are `launch_worker.sh`'s. The tests plant the files, so S2 can still be\n  tested; the ticket's wording is wrong and should be noted.\n\n## Run 3 (DEC-1156 (1), (6), 2026-11-12)\n\n- **ROUTE-1 (a):** `tests/unit/session_watch/test_route.py:19` asserts the two-path tuple `(\".gov-runtime/session-watch/**\", \".gov-runtime/dispatch/inbox/**\")` (DEC-1153 (2)); that assertion only, by an engineer.\n- **W2-159's F4** (`tests/acceptance/W2-159/test_f4_scope.py`): a test designer's revision with its Rewrite-Reason: judged only when HEAD is `refs/heads/w2/W2-159`, skipped elsewhere with its reason (the branch found, or \"detached HEAD\"), the form W2-180 gave W2-170's F5 and P1-N gave W2-171's F5; on a planted `w2/W2-159` branch with a change outside W2-159's paths it still fails.\n- Then a narrow independent check of both changes (DEC-1154), its record as the probe record (the older one to `-round-1.md`), and the land.\n",
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
  "supplementary": [],
  "supplementary_query": "gov wait and the helper watch in the product: a bounded wait on a job's exit file by pid, and an inbox item when a helper or a launched worker dies or goes silent (EMERGENCY-TOOLS-1 D3, D17; DEC-1079, DEC-1112 (3), DEC-1073 (4))\nS1 `gov wait <exit-file> [<max-s>]` blocks until the exit file is non-empty or `<max-s>` seconds pass (default and ceiling 570, so a wait ends under a 600-second tool limit; a larger value is capped and says so), then prints the job's log tail and its exit code; it waits on the file, never on a process name. Verify: a stand-in job writing its exit file after 2 seconds: its code is printed and returned; a never-written file at `<max-s>` 1: exit 124 \"RUNNING\"; a value of 9999 is capped at 570 with a line saying so [DEC-1079, DEC-1052]\nS2 When a pid file sits beside the exit file (`<base>.pid`, as `gov launch` writes it), the job's liveness is asked of its pid alone: a job gone without its exit file ends the wait at once with exit 125 \"GONE\", never waits to the bound; an exit file holding no number, or a usage error, is exit 2. Verify: a stand-in job killed before it writes its exit file: exit 125 within one poll period; a second process of the same name left running does not keep the wait alive [DEC-1073 (4), DEC-1079]\nS3 The helper watch (`gov session-watch helper-watch`, one pass or a loop every 5 minutes, ending after a maximum of 24 hours with one \"ended\" line so the caller re-arms it) writes one inbox item, once per condition, when an in-session helper of the registered orchestrator session ends on an API or network error as its last entry, or is not finished and has written nothing for 30 minutes; and when a launched worker (found by its pid file) is gone without its exit file, or its exit file appeared with a non-zero code or an error in its result. The item names the helper or the worker's log and its last line. Verify: planted helper transcripts and worker pid and exit files, one per condition, and a healthy one: one item each for the first four, none for the healthy one, none again on the next pass [DEC-1112 (3), DEC-1073 (4)]\nS4 The helper watch reads names, timestamps and error codes only, never a message's text; it matches no process by name; it writes only the inbox, its own state file and its own log; only transcripts whose last entry is inside a window (default 24 hours) are looked at. Verify: a filesystem-spy and a text-canary test: a planted message text never appears in an item or the log; a search of the module for a process-name match finds none [DEC-1112 (3), DEC-1073 (4), DEC-495]\nA wait that outlives its bound, or that waits for a job whose process is gone. Verify: S1's never-written exit file at `<max-s>` 1 returns exit 124 within the bound, and S2's killed stand-in job returns exit 125 within one poll period with a same-name process still running\nA process matched by name, or a message's text copied into an item or a log. Verify: S4's text-canary test (the planted message text found 0 times in items and log) and its search of the module for a process-name match (none found)\nThe same condition written to the inbox twice. Verify: S3's planted conditions run through two passes: the inbox holds one item per condition after the second pass, and none is added by it\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 9554,
  "budget": {
    "limit": 12000,
    "used": 9554
  },
  "hash": "cc90009c9d38f74ad2fae0038ae237bf3b1e45619ec0a309a796cc8799c26b56"
}


## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the red line before, the green summary of `tests/unit/session_watch`
after) / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then
`commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true
or false-positive).
