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
