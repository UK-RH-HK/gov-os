# Brief rev-1: independent auditor for DAEO-g29a (W2-113), STANDARD review round 1, class C2

You are the independent auditor (a fresh, read-only session) for ticket DAEO-g29a (W2-113: an adopted product's CTO is
named at adoption — Stage A0 creates the coordination ticket and writes the roster's `coordination_ticket` key; the
install refusal, when the rule cannot run, names `GOV_TICKET` and says how to set the key in true words). Audit the
branch head **6542b7ec525b** of `w2/W2-113` in /home/usain/gov-os-worktrees/W2-113 against the ticket's KPI lines
(success-1, success-2, failure-1, failure-2) and its `## Interface` section (I1, I2, I3 and the readings), which the
owner decided (DEC-1156 (4); I2 (iii) as PKG-3 (b), DEC-1157 (15)). The `moved:` line (role files, W2-33's) and the
`lifted:` line (the quiet-hours hook, DEC-1083) are out of scope.

You change nothing in the repository: no edit, no commit, no merge. Your verdict is your return.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-g29a','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must work.
If (a) wrote the file, stop there and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-g29a`).

## What to read
| what | path |
|---|---|
| the ticket (KPI lines; `## Interface`) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g29a.md (also in the context packet below) |
| the change | `git -C /home/usain/gov-os-worktrees/W2-113 diff 159abfe06..6542b7ec525b -- src tests/unit` (src/gov/adopt/stages.py `_coordination`, `a0`; src/gov/guard/install.py `coordination_ticket` docstring, `cto_install`'s no-key refusal; tests/unit/adopt/test_w2_113_coordination.py) |
| the independent acceptance suite (74 cases, all green at this head by `gov accept`) | tests/acceptance/W2-113/ (README.md maps KPI lines to cases; two cases revised to PKG-3 (b) in 3352f754b87e) |
| the guard that decides (rule 4 calls `cto_install`) | template/governance/kernel/hooks/pretooluse.py; W2-110's suites tests/acceptance/W2-110/, tests/unit/guard/test_w2_110_cto_install.py (line 172 pins "Set the top-level key") |
| A0's machinery | src/gov/adopt/project.py (`Run.finish`, the commit), src/gov/adopt/safety.py (`setup`), src/gov/tasks/tickets.py (`create`, `TK_REL`), governance/kernel/bin/tk in a generated product |
| W2-110's probe record (its F5 is the complaint success-2 answers) | docs/probes/DAEO-3r1j/ |
| the sources (by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-971 (item 4), DEC-957, DEC-982, DEC-974, DEC-1156 (4), DEC-1157 (15), DEC-1052 |

Search with Read, Grep and Glob; search again once in different words if the first does not answer (DEC-1065).

## Known to the lead (judge them; do not re-report them as new)
- The engineer's choices where the Interface is silent: a roster key that names no existing ticket is left as it is
  (A0 completes, creates nothing, its record says so; the guard stays closed); a roster that is not a readable mapping,
  or cannot take the key as one added line, is left as it is likewise; `tk` present but failing makes A0 refuse
  (`ADOPT_COORDINATION_TICKET_FAILED`) and write nothing; a second A0 run creates no second ticket (the key now names
  one). Say whether each is within I1/I2 and safe (fails closed), or contradicts them.
- Older suites red inside the worker sandbox, from the code-graph tool at A3 (`ADOPT_CODE_GRAPH_UNREADABLE`) and at
  `gov rebuild`: W1-41 (16), W2-23 (3), W2-52 (56 errors), W2-05 (1). The lead's verify run (outside the sandbox)
  judges them; you need not.
- `tests/acceptance/W2-23/test_w2_23_space.py:99` pins six kernel hooks and finds a seventh (`context_watch.py`), not
  A0's doing.

## What to probe (at least these; add your own)
1. Each KPI line and failure line against the code, not only the tests; where a test is weaker than its line, probe
   the line directly. failure-2 by every session form you can think of (roles, subagent types, an orchestrator on
   another ticket, by id and by WBS id, no ticket, odd spellings). Scope: `git diff --name-only 4ede6c3fee3d..6542b7ec525b`
   against the ticket's allowed_paths (tests/acceptance/W2-113/ is the test designer's; anything from the merge of
   w2/integrate is not this ticket's).
2. I1 end to end: a product generated from the template (copier, then `rulesync generate`, as W2-110's support does),
   committed, then `gov adopt --lite --stage A0` (this worktree's `src` on PYTHONPATH): the ticket's exact title
   (`<folder> coordination`), `class: coordination`, `state_class`, the roster key, A0's record entries (old keys kept,
   new ones added), everything in A0's one commit, the tree clean, the backup ref; then the hook's decisions.
3. I2: (i) a key by id and by WBS id kept, nothing created; (ii) the roster's other keys, comments, blank lines, order,
   a file with no final newline, an empty file, a comment-only file, odd YAML (flow mapping, anchors, a document
   marker `---`, CRLF line ends, a tab, a duplicate key, the key nested under another key) — does A0 ever write a
   roster the guard reads differently from what A0 recorded?; (iii) `tk` missing: success, no ticket, no key, the
   record says so in words, the guard closed and its refusal naming `GOV_TICKET`.
4. Failure paths of A0: `tk create` failing or printing something unexpected; the ticket file left behind or lost
   (A0 reads it back and deletes it before committing — what if the commit then fails?); A0 run twice; A0 when
   `.tickets/` holds a ticket with the same title; whether anything is written to the tree on a refusal.
5. success-2's words in each case the rule cannot run (no roster, no key, empty/null value, a key naming no ticket,
   unreadable roster): names `GOV_TICKET`, says how to set the key, no claim that a key was set when none was, still
   a refusal, `ESCALATE`'s tail kept, W2-110's line-172 sentence kept. Read the words as a CTO would: are they true
   in each case, and do they tell the CTO what to do?
6. No other behaviour of the guard changed: W2-110's acceptance and unit suites at this head.

Your probes are read-only on the repository and run by Bash in your own TMPDIR (DEC-1144 (7)): use the sandbox's
TMPDIR (outside the repository); plant everything there; scripts longer than one line go there too. Any pytest goes
through the heavy-slot gate:
`TMPDIR=<your tmp> bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in your tmp> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-113/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
A heavy-slot or resource refusal is a wait. Never `gov adopt`, `gov close` or `gov pause` on a real repository or
worktree (on a planted product in your TMPDIR it is the probe). Never open the evaluation sets' root or any hidden or
memory-verdict folder. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never
reach the same effect by another form (DEC-1142 (9)). Clean up your TMPDIR trees before you return.

The ticket's context packet (`gov context DAEO-g29a --role independent-auditor --budget 12000`) follows.

----

