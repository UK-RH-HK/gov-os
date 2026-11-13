Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-3: engineer for DAEO-6lid (W2-159), review round 1's fix, profile STANDARD, class C2

`gov session-watch stop-check waiter|idle` is built and green (tests/acceptance/W2-159 85 passed). The reviewer found
two behaviours it does not hold (below). Fix them inside your paths, test first, change nothing else. An independent
test designer writes acceptance cases for the same behaviours in parallel; you never read them.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-159 |
| branch | w2/W2-159 (head 2a67c4a63da0) |
| allowed paths | src/gov/session_watch/**, tests/unit/session_watch/** (nothing else is needed for this fix) |
| the ticket (KPI lines; the `## Interface` section is the contract) | /home/usain/gov-os-worktrees/W2-159/.tickets/DAEO-6lid.md |
| where the behaviours live (the reviewer's reading) | src/gov/session_watch/running.py (pid files), state.py and checks.py (the once-a-turn record) |
| the reference's rule for B1 (read only; never copy its project-specific names) | governance/project/orchestration/tools/stop_idle_check.py, `START_SLACK_S` and the "reused pid" lines (~237-240) |

## The two behaviours to hold (review round 1 of DAEO-6lid, findings FR-1 and FR-2, described as behaviour; DEC-136)

**B1 (S2; FR-1, blocking: in scope, ordinary work, fails open): a reused pid is not running work.**
- Done: a project holds a leftover pid file (under the pid globs, no `<name>.exit` beside it) written two days ago
  (its mtime); the number in it now belongs to an unrelated live process that started 10 minutes ago. One unblocked
  item is listed; nothing else runs.
- Happened: the idle check let the turn end, saying something of the orchestrator's is running (that pid).
- Should happen: a block naming the item. S2 counts "a pid file whose process is alive": the process the file named
  is gone; a process that started after the file was written is not it. The lead's reading [lead]: a pid file's
  process counts only when it started no later than 15 minutes (900 s, a slack for clock steps) after the file's
  mtime; one that started later is not counted and not named as running (as a dead pid is not). A process that
  started before the file was written, or within the 15 minutes after, still counts (the existing cases stay green).
  The project-specific exceptions of the reference (named launcher scripts) are not ported: the code names nothing of
  this repository (S5, F3).

**B2 (S3; FR-2, rides along: in scope, ordinary work, consequence other; DEC-802): the two checks keep each other's
once-a-turn record.**
- Done: both checks are installed; Claude Code runs a Stop event's hooks side by side. On one Stop the waiter is
  unarmed and an item is unblocked, so both block. The idle check reads the shared state file at its start and writes
  it after `gov plan` returns; the waiter check wrote its record in between.
- Happened: the idle check's write dropped the waiter's record; a later stop in the same turn, without
  `stop_hook_active`, got a second waiter block.
- Should happen: S3's "never twice for the same turn" holds whatever the order: after both checks end, the state file
  holds both checks' records for the turn, and a third waiter call in the same turn (no `stop_hook_active`) says
  nothing. (The Interface keeps one `state.json` shared by both checks, keyed by check.)

## What to do
- B1: a unit case first (red), then the fix; the existing cases stay green. Keep the 900 s slack a named constant.
- B2: a unit case first (red: the two records interleaved, deterministic, no sleeps), then the fix (e.g. re-read the
  state file and merge this check's record just before writing, under a short file lock or an atomic replace; or any
  inner choice that keeps one shared `state.json` keyed by check, as the Interface says). An error in that step is
  still S4's: the turn ends, named in `systemMessage` and the log.
- No name, path, folder or ticket id of this repository in src/gov/session_watch (S5, F3), comments included.
- Then run tests/unit/session_watch, then tests/acceptance/W2-159 (read and run it; never edit it), each green.

## Rules
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside ~/gov-os-runs
  (the sandbox's own `$TMPDIR`: `/tmp` is read-only there), `PYTHONUSERBASE=/home/usain/.local`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`, one folder per run, as one line, run in the background
  with its output to a file (the gate may queue for a while: all slots can be taken), e.g.:
  `env HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/session_watch -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- One commit (or one per behaviour), your paths only (`git add` a new file first):
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: engineer" --trailer "Implements: DEC-1110, DEC-1109" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/session_watch tests/unit/session_watch`
  The lead may merge acceptance tests into your branch between your commits: commit before a long pause, and
  `git status --short` empty when you return.
- One-line commands only; a longer script goes in a file under the sandbox's `$TMPDIR`. Use literal paths. Never touch
  `.gov-runtime/scratch/lead/` or `tests/acceptance/`. No install, no network, no `.claude/`, never a live session or
  a hook registered anywhere. Search with Read, Grep and Glob; search once more in other words if the first does not
  answer (DEC-1065).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (each behaviour: file:line) / files_changed / evidence (each run's pytest summary line) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The ticket's context packet (gov context at 08:40 UTC; the ticket text is unchanged since; today's call answers CONTEXT_OVER_CEILING)
{
  "ticket": "DAEO-6lid",
  "ticket_text": "---\nid: DAEO-6lid\nstatus: in_progress\ndeps: []\nlinks: [DAEO-cb2b, DAEO-fd0p]\ncreated: 2026-11-11T01:20:18Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-159\ntags: [wave-2, implementation, standard, after-the-lift, orchestration, hooks]\nwbs_id: W2-159\ntitle: 'The orchestrator''s two Stop checks in the product: a turn does not end with the inbox waiter unarmed, nor idle while unblocked work remains, each a reminder blocking at most once a turn (EMERGENCY-TOOLS-1 A8, A9; DEC-1027 E, DEC-1110 (1))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/session_watch/**\n- src/gov/check/commands.py  # the one line that records `session-watch` (the precedent: W2-20's `resources`)\n- src/gov/cli/main.py  # P-W2-159-1 (a): a hyphenated command maps to its underscore folder (about 4 lines; the CTO, 2026-11-12 08:22)\n- tests/unit/session_watch/**\n- docs/changes/W2-159-evidence.md\nreads:\n- src/gov/dispatch/**\n- src/gov/plan/**\n- governance/project/orchestration/tools/stop_waiter_check.py\n- governance/project/orchestration/tools/stop_idle_check.py\nneeds:\n- src/gov/check/commands.py\nwaits_on:\n- ref: DAEO-cb2b\n  reason: 'S2''s open items and S1''s waiter name come from the dispatcher''s inbox and ready list (W2-121); until it lands the check reads a configured file'\nkpis:\n  success:\n  - 'S1 `gov session-watch stop-check waiter`, run as a Stop hook, answers \"block\" with a reason that names the inbox waiter and its command when all hold: the session is the orchestrator''s registered session (the id its start wrote to the project''s session file), no stand-by note younger than its limit (default 2 hours) is present, and no process of any configured waiter command is running; in every other case, and on any error, it says nothing. Verify: planted process lists and session files: waiter absent gives a block naming it; waiter present, a younger stand-by note, another session''s id, and a file that cannot be read each say nothing [DEC-1027, DEC-1028]'\n  - 'S2 `gov session-watch stop-check idle`, run as a Stop hook, answers \"block\" naming each unblocked item when nothing of the orchestrator''s is running while its list of open items shows unblocked ones, and lets a turn end when a legitimate wait holds, naming which: the resource gate shut or the machine full (the dispatcher''s status, at most 5 minutes old), every remaining item waiting on the owner, or a running job. \"Running\" is a live background agent, a live background task or a live launched worker or run (a pid file whose process is alive, started under 3 hours ago, with no exit file); one past 3 hours is named as stale and not counted. Verify: planted status files, pid files and open-items lists: one case per legitimate wait, one with a stale pid, one with unblocked items and nothing running (a block naming them) [DEC-1110 (1), DEC-1109 (3), DEC-936]'\n  - 'S3 Both checks block at most once per turn: never when `stop_hook_active` is set, never twice for the same turn (kept in a state file); a line `IDLE-REASON: <why>` in the orchestrator''s messages of the turn lets the idle check end it, and the line is recorded in the check''s log; neither a block nor a reason carries into the next turn. Verify: a planted turn: first call blocks, second with `stop_hook_active` says nothing, a third in the same turn says nothing, a new turn blocks again; a turn with the IDLE-REASON line ends and is logged [DEC-1110 (1), DEC-1027]'\n  - 'S4 A check never traps a session and never fails open silently: on any error the turn ends and the error is named to the owner (`systemMessage`) and in the check''s log; a stand-by note does not let a turn end idle in S2 (unblocked work moves while the owner decides). Verify: a planted unreadable state file: the turn ends, the error named and logged; a stand-by note beside unblocked items: still a block [DEC-1110 (1), DEC-1109 (3)]'\n  - 'S5 Where the open items come from is the project''s configuration, never a file name in the code: the default is the dispatcher''s ready list (W2-121, `gov plan --ready`); a project may name a file and a reader. Verify: a planted project with each source: the same block text naming the items; a search of src/gov/session_watch for this repository''s file names finds none [DEC-1110 (1), DEC-1088]'\n  failure:\n  - 'A turn blocked twice in a row, or blocked for a legitimate wait. Verify: S3''s planted turn (a second and a third call in the same turn say nothing) and S2''s planted files for each legitimate wait (gate shut, owner-only items, a running job): each says nothing blocking and names the wait'\n  - 'A check that fails with no message, or that traps a session it cannot read. Verify: S4''s planted unreadable state file: the turn ends, the error is named in `systemMessage` and in the check''s log; a silent end or a block there is this failure'\n  - 'A file name, folder or ticket of this repository named in the code. Verify: S5''s search of src/gov/session_watch for this repository''s file, folder and ticket names finds none'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1027\n- DEC-1028\n- DEC-1110\n- DEC-1109\n- DEC-936\n- DEC-1088\n- DEC-1119\n- DEC-994\n- DAEO-cb2b  # W2-121\nest_loc: 330\nacceptance_tests:\n  path: tests/acceptance/W2-159/\n  author: 'independent-test-designer (MR-3), from these KPI lines; planted process lists, pid files, status files and transcripts, never a live session'\ntrack: A\nlist_rows: []\n---\n# W2-159 The orchestrator's two Stop checks\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 rows A8 and A9; **after the lift**, not before EXAMIN's copy.\n\n- **Problem.** This repository's CTO has two Stop-hook reminders (`governance/project/orchestration/tools/stop_waiter_check.py`, `stop_idle_check.py`; registered in the untracked `.claude/settings.local.json`, EMERGENCY-TOOLS-1 \u00a74.1). They keep a turn from ending while the inbox waiter is unarmed (DEC-1027) and while unblocked work remains with nothing running (DEC-1110 (1)). An adopted product's orchestrator has neither. The idle check also reads this repository's DECIDED-NOT-DONE tables, so it cannot be copied as it is.\n- **Approach.** One module, two checks, one state and log; the open items and the waiter come from the project's configuration, defaulting to W2-121's dispatcher. Alternative: copy the two scripts into the kernel template (rejected: the idle check names this repository's file; a kernel change needs its CIT-P).\n- **Interface.** `gov session-watch stop-check waiter|idle`, reading the Stop hook's JSON on standard input and answering in the hook's form; the session file, the stand-by note and the state and log files are the project's runtime folder's. Installing the hook into a project's settings is an owner's ACT (class (b)), not this ticket.\n- **Non-goals.** The dead-man's switch is not here: it is parked as W3-P16 by decision (DEC-994 item 3, W2-121's moved line). The helper watch and the bounded wait are W2-160.\n- **Rabbit holes.** Reading a transcript's text (entry types and times only); a block that cannot be lifted (S3's once-a-turn bound is the guard against it).\n\n[DEC-1027, DEC-1110 (1), DEC-1109 (3), DEC-1119 (5)]\n\n## Interface (DEC-1052; P-W2-159-2 (a): the lead's proposal accepted as a whole, the CTO, 2026-11-12 08:22)\n\nThe ticket's Interface names the command, stdin and the hook's answer form, but not where the configuration lives, the\nruntime files' names, the waiter's default or the open-items reader. Proposed, to be accepted as a whole or amended:\n\n1. Command: `gov session-watch stop-check waiter|idle [--root <dir>]` (route: P-W2-159-1). The module declares\n   `CHILD_EXIT_CODE = True`, prints at most one JSON object on stdout in the Stop hook's form\n   (`{\"decision\":\"block\",\"reason\":...}` or `{\"systemMessage\":...}`) and returns 0, always, so no envelope is printed.\n   A configuration error (`load_config` raising before `run`) is out of its reach: named as a residual.\n2. Configuration: `governance/project/session-watch.yaml`, the mapping under `session_watch:` (the dispatcher's\n   precedent, `dispatch.yaml` / `dispatch:`). Keys, all optional:\n   - `waiter_commands`: list of strings, each matched as a substring of a process's command line. Unset or empty:\n     the waiter check says nothing (nothing to arm); S1's planted project sets it.\n   - `waiter_arm`: the command the block's reason names to arm it; default the first of `waiter_commands`.\n   - `standby_max_age_h`: default 2.\n   - `pid_globs`: globs relative to the root; default `.gov-runtime/**/*.pid`.\n   - `items`: `{source: dispatcher}` (default) or `{source: file, path: <relative>, reader: <name>}`. The dispatcher\n     source runs `gov plan --root <root> --ready <tmp>` and takes batch 1 as unblocked, less the tickets the\n     dispatcher's status shows running. Readers: `lines` (built in: one item per non-`#` line, `<id> <state words>`;\n     state `WAIT owner...` is owner-waiting, `WAIT ...` other wait, `DONE|CLOSED` closed, anything else unblocked)\n     and `module.path:function` (returns a list of `{id, title, state}`, state one of open, owner, job, closed).\n3. Runtime folder `.gov-runtime/session-watch/`: `session.txt` (the registered orchestrator session id; this ticket\n   reads it, never writes it: writing it is the session-start hook's install, an owner's ACT), `standby.txt` (the\n   stand-by note; its age is its mtime), `state.json` (the once-a-turn state, shared by both checks, keyed by check),\n   `stop-check.log` (one tab-separated line per decision, with the IDLE-REASON line when one ended the turn).\n4. Dispatcher status: `.gov-runtime/dispatch/status.json` (W2-121's schema), used when at most 5 minutes old by\n   mtime: gate shut = `gate.open` false or `gate.disk.open` false; machine full = `outcome` \"refused\" (exit code 3);\n   running = `running`, `running_jobs`, `pending_starts` non-empty.\n5. Running (S2): the session's background agents and tasks as the reference reads them (Claude Code's own paths,\n   derived from `transcript_path` and `session_id`, overridable for tests by env), and pid files under `pid_globs`\n   (alive, started under 3 h ago, no `<name>.exit`); past 3 h named as stale and not counted.\n6. Test overrides (env, the reference's precedent): `GOV_SESSION_WATCH_PS` (a JSON list of {pid, cmdline, start,\n   state, fds} in place of /proc), `GOV_SESSION_WATCH_NOW` (epoch seconds), `GOV_SESSION_WATCH_GOV` (the `gov`\n   program run for the plan).\n\n**P-W2-159-1 (a):** `src/gov/cli/main.py` in allowed_paths: `_known` and `_module_name` map a hyphenated command to its underscore folder, and `check/commands.py`'s existence check the same; one unit test. W2-160's `helper-watch` uses the same mapping. W2-138 (DAEO-rmhj) also lists `src/gov/cli/main.py`: a trivial merge if both run.\n",
  "authority": [
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-1028",
      "sha256": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "reason": "declared in sources",
      "tokens": 692
    },
    {
      "id": "DEC-1110",
      "sha256": "9b9b5bc5c2a75400d67a1aeac3f3cd966720c73b1b4881d260431aa98fbbfc27",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9b9b5bc5c2a75400d67a1aeac3f3cd966720c73b1b4881d260431aa98fbbfc27",
      "reason": "declared in sources",
      "tokens": 486
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
      "id": "DEC-936",
      "sha256": "9fda8ce7f0a7cf83c8d73147512a939f7845a141f4eca4f06eeee9e0eeb0cfeb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9fda8ce7f0a7cf83c8d73147512a939f7845a141f4eca4f06eeee9e0eeb0cfeb",
      "reason": "declared in sources",
      "tokens": 2662
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
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DAEO-cb2b",
      "sha256": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "reason": "declared in sources",
      "tokens": 2856
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-1028",
      "sha256": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "reason": "declared in sources",
      "tokens": 692
    },
    {
      "id": "DEC-1110",
      "sha256": "9b9b5bc5c2a75400d67a1aeac3f3cd966720c73b1b4881d260431aa98fbbfc27",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9b9b5bc5c2a75400d67a1aeac3f3cd966720c73b1b4881d260431aa98fbbfc27",
      "reason": "declared in sources",
      "tokens": 486
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
      "id": "DEC-936",
      "sha256": "9fda8ce7f0a7cf83c8d73147512a939f7845a141f4eca4f06eeee9e0eeb0cfeb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "9fda8ce7f0a7cf83c8d73147512a939f7845a141f4eca4f06eeee9e0eeb0cfeb",
      "reason": "declared in sources",
      "tokens": 2662
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
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-994",
      "sha256": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "cbbb35460c24cc4be24bf2a9eaf5c761f679e89b0b6b8768fadd14081933b5a2",
      "reason": "declared in sources",
      "tokens": 637
    },
    {
      "id": "DAEO-cb2b",
      "sha256": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e1dfaf86a8864daec401cc151f95264ea009f6e7c5653075abcccb7cdd59bbdc",
      "reason": "declared in sources",
      "tokens": 2856
    }
  ],
  "supplementary": [],
  "supplementary_query": "The orchestrator's two Stop checks in the product: a turn does not end with the inbox waiter unarmed, nor idle while unblocked work remains, each a reminder blocking at most once a turn (EMERGENCY-TOOLS-1 A8, A9; DEC-1027 E, DEC-1110 (1))\nS1 `gov session-watch stop-check waiter`, run as a Stop hook, answers \"block\" with a reason that names the inbox waiter and its command when all hold: the session is the orchestrator's registered session (the id its start wrote to the project's session file), no stand-by note younger than its limit (default 2 hours) is present, and no process of any configured waiter command is running; in every other case, and on any error, it says nothing. Verify: planted process lists and session files: waiter absent gives a block naming it; waiter present, a younger stand-by note, another session's id, and a file that cannot be read each say nothing [DEC-1027, DEC-1028]\nS2 `gov session-watch stop-check idle`, run as a Stop hook, answers \"block\" naming each unblocked item when nothing of the orchestrator's is running while its list of open items shows unblocked ones, and lets a turn end when a legitimate wait holds, naming which: the resource gate shut or the machine full (the dispatcher's status, at most 5 minutes old), every remaining item waiting on the owner, or a running job. \"Running\" is a live background agent, a live background task or a live launched worker or run (a pid file whose process is alive, started under 3 hours ago, with no exit file); one past 3 hours is named as stale and not counted. Verify: planted status files, pid files and open-items lists: one case per legitimate wait, one with a stale pid, one with unblocked items and nothing running (a block naming them) [DEC-1110 (1), DEC-1109 (3), DEC-936]\nS3 Both checks block at most once per turn: never when `stop_hook_active` is set, never twice for the same turn (kept in a state file); a line `IDLE-REASON: <why>` in the orchestrator's messages of the turn lets the idle check end it, and the line is recorded in the check's log; neither a block nor a reason carries into the next turn. Verify: a planted turn: first call blocks, second with `stop_hook_active` says nothing, a third in the same turn says nothing, a new turn blocks again; a turn with the IDLE-REASON line ends and is logged [DEC-1110 (1), DEC-1027]\nS4 A check never traps a session and never fails open silently: on any error the turn ends and the error is named to the owner (`systemMessage`) and in the check's log; a stand-by note does not let a turn end idle in S2 (unblocked work moves while the owner decides). Verify: a planted unreadable state file: the turn ends, the error named and logged; a stand-by note beside unblocked items: still a block [DEC-1110 (1), DEC-1109 (3)]\nS5 Where the open items come from is the project's configuration, never a file name in the code: the default is the dispatcher's ready list (W2-121, `gov plan --ready`); a project may name a file and a reader. Verify: a planted project with each source: the same block text naming the items; a search of src/gov/session_watch for this repository's file names finds none [DEC-1110 (1), DEC-1088]\nA turn blocked twice in a row, or blocked for a legitimate wait. Verify: S3's planted turn (a second and a third call in the same turn say nothing) and S2's planted files for each legitimate wait (gate shut, owner-only items, a running job): each says nothing blocking and names the wait\nA check that fails with no message, or that traps a session it cannot read. Verify: S4's planted unreadable state file: the turn ends, the error is named in `systemMessage` and in the check's log; a silent end or a block there is this failure\nA file name, folder or ticket of this repository named in the code. Verify: S5's search of src/gov/session_watch for this repository's file, folder and ticket names finds none\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 12573,
  "budget": {
    "limit": 16000,
    "used": 12573
  },
  "hash": "d92fd0e07d974819e2f83d953811d01312f3216223a1036464f649ddf523f0a5"
}
