## The fix round's interface (review round 1's findings F-1 to F-6; the CTO's P-W2-121-7 (a), ticket section "P-W2-121-6 and P-W2-121-7")

Both the test designer and the engineer build to these readings; everything in the first round's interface still holds
except where a line below changes it. A reading you think wrong: follow it, and name it in `unresolved`. Tests check the
behaviour, never the names of the bookkeeping files (those are the engineer's).

- **F-1, an item is written once, ever (S4, S7).** An inbox item (a return `<log>.return.txt`, a start that never ran
  `<log>.never-ran.txt`, an owner item `<log>.owner.txt`), once written, is never written again, as unread or at all, even
  after it is deleted from `inbox/` (an honest operator removes a handled item) or from `inbox/read/` (a tidy-up of the
  read folder). The record that it was written lives in the state folder outside `inbox/` and outlives the item (e.g. an
  `items-written.txt`, one line per item name, appended when the item is written; `never-ran.txt` is read for the
  never-ran items). An item already in `inbox/` or `inbox/read/` also counts as written (a state folder from before this
  record). Deleting an item never raises its escalation again either.
- **F-2, an escalation is recorded only when it was sent (S4).** An item unread past `unread_escalate_s` runs
  `notifier_command` (the item's path its last argument). It counts as raised (never run again for that item) only when
  the notifier exits 0. A notifier that exits non-zero, times out (`command_timeout_s`) or cannot be started leaves the
  escalation due: it is tried again on a later pass, no sooner than `notify_retry_s` seconds (new key; a number >= 0;
  default 600; malformed: exit 2 naming the key) after its last attempt (0: every pass). While an escalation is due after
  a failed attempt, **every** pass's status (`problems` in `status.json`, the `problems:` block of `status.txt`) names
  the item and the last failure, also on passes that do not retry it; the line goes once it is sent or once the item is
  read (moved to `inbox/read/`), and a read item is never retried. A notifier timeout in a pass ends that pass's
  escalations (bounded pass time): the escalations still due in that pass are not run and not recorded as raised, and the
  status names them as not sent. A failed notifier never fails the pass: `ok` stays true and the exit code is the one the
  starts give (0 or 3).
- **F-3, the notifier is required at load (S4, S5).** `notifier_command` is a required key: missing, empty or not an argv
  list is a configuration error at load: exit 2 naming `notifier_command`, nothing started, the status's first line
  `PASS FAILED <time>: ...notifier_command...` (as every other missing key). No pass raises a configuration error after
  it has started a session.
- **F-4, an untracked path is unresolved (S9).** A relative path a return names on `files_changed:` resolves only when
  git knows it in the ticket's worktree: it is in HEAD's tree or in the history (`git log -- <path>` names a commit), or
  it exists and git ignores it (`git check-ignore`). A path that exists only as an untracked, not-ignored file (or only
  staged, in no commit) is named on the item's `unresolved:` line. Absolute paths: unchanged.
- **F-5, the gate case that only the gate refuses (S2, S6).** A gate shut for load or CPU (not memory) with memory room
  ample for the peak refuses every entry with a reason naming the gate (the round-1 reading: "gate shut"), exit 3, no
  start. (Test-only finding; the code already does this.)
- **F-6, a hung git while resolving (S9).** When git times out or fails while resolving a return's commits and paths,
  the item names them as not checked, never as unresolved: a line `unchecked: could not be checked (<the failure>): <the
  ids and paths>` and no `unresolved:` line for them; the pass's status names the failure as before. (Engineer only, with
  a unit test.)
