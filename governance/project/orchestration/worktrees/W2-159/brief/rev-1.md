Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief rev-1: reviewer (independent-auditor, read-only) for DAEO-6lid (W2-159), profile STANDARD, class C2, round 1 of at most 2

You are the reviewer (QA): you read everything, you change nothing. You probe the head 2a67c4a63da0 of
/home/usain/gov-os-worktrees/W2-159 (branch w2/W2-159) for behaviour the acceptance tests miss, against the ticket's
KPI lines S1-S5 and F1-F4 (non-goals: none in the KPI table; the ticket's text parks the dead-man's switch and the
helper watch elsewhere).

## Where things are
| what | path |
|---|---|
| the tree (read only; write nothing) | /home/usain/gov-os-worktrees/W2-159 |
| the ticket (KPI lines; the `## Interface` section at its end is the contract, accepted by the CTO as P-W2-159-2 (a)) | /home/usain/gov-os-worktrees/W2-159/.tickets/DAEO-6lid.md |
| the code | src/gov/session_watch/ (command, checks, config, items, running, state, status, transcript); src/gov/cli/main.py (`_known`, `_module_name`: the hyphenated route, P-W2-159-1 (a)); src/gov/check/commands.py (`RECORDED_GOV_COMMANDS`, the existence check) |
| the acceptance tests (independent test designer, 84 cases) | tests/acceptance/W2-159/ (README.md maps each case to a KPI line) |
| the unit tests (engineer) | tests/unit/session_watch/ |
| the reference this ticket ports (this repository's own Stop hooks; not a target) | governance/project/orchestration/tools/stop_waiter_check.py, stop_idle_check.py |
| the dispatcher it reads (W2-121) | src/gov/dispatch/ (run.py's status data, state.py), src/gov/plan/ (`--ready`), .tickets/DAEO-cb2b.md `## Interface` |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1027, DEC-1028, DEC-1110, DEC-1109, DEC-936, DEC-1088, DEC-1119, DEC-994 |
| the branch's base (for F4: `git diff --name-only e84e6c9cf..2a67c4a63da0`; the acceptance case test_f4_scope.py checks the same) | e84e6c9cf |

## The lead's results (do not re-run them)
- The lead's scoped verification (`lead_verify.sh`) at 680bdce1f526 (the code head; 2a67c4a63da0 adds only one
  acceptance case): 4853 tests, 10 failed, every one the W2-96 signal family (gov accept's signal handling), red the
  same on w2/integrate (shared base reds, W2-177 fixes them); serial phase 1 test, green. Being re-run at 2a67c4a63da0.
- `gov accept W2-159` at 680bdce1f526: 84 passed, 0 failed; every line pass except failure-4, which had no case. The
  test designer then added F4's case (test_f4_scope.py, 9254a220dfbc, merged at 2a67c4a63da0: 85 cases, 85 green
  in the designer's run); the lead's gov accept at 2a67c4a63da0 is being re-run.
- The engineer's fix round: tests/unit/check's `test_the_recorded_commands_are_held_and_lock_by_its_module_command`
  went red when `session-watch` was recorded; the existence check now accepts the module in the underscore folder or a
  folder of the command's own name (680bdce1f526).

## Steps
1. `printenv GOV_ROLE GOV_TICKET` and `git -C /home/usain/gov-os-worktrees/W2-159 rev-parse HEAD` (expect it to start
   2a67c4a63da0).
2. Read the ticket, the tests, the code and the lead's results; re-run nothing the lead ran; run code only to
   reproduce a finding, in a temporary folder outside the repository (planted roots, the Stop hook's JSON on standard
   input, `GOV_SESSION_WATCH_PS` / `GOV_SESSION_WATCH_NOW` / `GOV_SESSION_WATCH_GOV` in place of the live machine).
   Never register a hook in any `.claude/`, never run against a live session.
3. Look first for: a check that traps a session (blocks with no way out, blocks twice in a turn, blocks when
   `stop_hook_active` is set); a check that fails open silently (an error with no `systemMessage` and no log line, or
   a legitimate-wait answer given when the condition does not hold, e.g. a stale status file read as fresh, a stale or
   dead pid counted as running, a stand-by note letting S2 end idle); a block or reason carried into the next turn;
   a file name, folder or ticket id of this repository in src/gov/session_watch (F3); a change outside the ticket's
   allowed_paths (F4; tests/acceptance/W2-159/ is the test designer's path).
4. Any pytest you run to reproduce goes through the heavy-slot gate, one line, with a TMPDIR outside the repository
   and outside ~/gov-os-runs (the sandbox's own `$TMPDIR` where `/tmp` is read-only):
   `mkdir -p /tmp/w2-159-rev && env TMPDIR=/tmp/w2-159-rev HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <one file or case> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
5. Write nothing in any tree: `git -C /home/usain/gov-os-worktrees/W2-159 status --porcelain` is empty when you
   finish. Search with Read, Grep and Glob (no `gov retrieve` in the sandbox); search once more in other words if the
   first does not answer (DEC-1065).
6. Give your record `task: DAEO-6lid` and `decisions:` (the ids its findings rest on); name both ids where a
   superseded or PROPOSED rule is in use (DEC-1073). State, per finding, what evidence would reverse it (DEC-1014).
   Under `.gov-runtime/` and in your return, write commit hashes as 12 digits (DEC-911).


## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## Judgement
- Judge against ADR-0001's threat model: honest agent mistakes, plausible accidents and drift in ordinary work, not a deliberate adversary with the owner's privileges [DEC-801].
- Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?" [DEC-801].
- Give every finding two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` [DEC-808].
- Mark a finding that needs a deliberate construction (a link planted at a protected name, git variables set by hand, replace refs, an interpreter used to evade the guard) ordinary work no: a Wave 3 row, never a round [DEC-801].
- Block only on a finding in scope (the KPI lines, not the non-goals), reachable in ordinary work, that fails open or loses work; every other finding lands as a recorded row [DEC-1010].
- Hold at most two review rounds; then the owner once, with options [DEC-1010].
- Start no round of its own for accepted fixes when the ticket resumes anyway [DEC-802].
- Treat a risk that exists only when a feature is on as an entry criterion of the ticket that turns it on [DEC-803].
- State the classification of the findings on one line, before the recommendation, in a package that proposes a round [DEC-809].
- Leave READY to code: it is computed from your verdict block, and no lead writes a verdict over yours [DEC-1010].


## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing): task / status (DONE or PACKAGES) /
work_completed / files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive). Then the probe record body: what you probed and found sound, each finding described as behaviour
(what was done, what happened, what should have; never as code), each with its two lines (`Ordinary work: yes|no,
because …` and `Consequence: fails open|loses work|other`), its scope (in|out) and what would reverse it, the
classification of the findings on one line, and this fenced block, one entry per KPI line (S1, S2, S3, S4, S5, F1, F2,
F3, F4):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Name findings FR-1, FR-2, ... (the KPI table already uses F1-F4).

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
