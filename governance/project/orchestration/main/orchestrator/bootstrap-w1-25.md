
## W1-25 residuals (gov checkpoint, 2026-10-04)

Recorded at W1-25's close, from the ticket lead's summary. None is a defect of the ticket; each names who should
settle it.

- **Nothing calls the command yet.** W1-25 builds `gov checkpoint` (write, `--watch`, `--resume`) and the
  fresh-agent-reconstruction check declaration. The calls at a ticket transition, a compaction and a stop are
  W1-29's, W1-49's successor hooks' and W1-30's (DEC-280).
- **"Only orchestrator-role sessions run `gov checkpoint`" (DEC-320) is not enforced by the command.** It rests on
  the guard's path rules: a worker's write to `docs/checkpoints/<ticket>/` is outside its `allowed_paths`.
- **No acceptance case holds the DEC-321 defaults** (240 minutes, 20 commits); one builder test does. Thresholds are
  not range-checked.
- **Numbering and writing.** Two sessions writing the same ticket's checkpoint at once, or on two branches, can take
  the same number: there is no lock, and the write is not atomic. Files in the folder that do not match
  `CP-<ticket>-<NNNN>.md` are ignored.
- **What the watchdog reads.** "Commits since" counts from the commit that added the checkpoint file, across the
  whole history of HEAD; an uncommitted checkpoint, or one not reachable from HEAD, counts 0. It checks that each
  input has an id, a version and a well-formed sha256 and does not re-hash the files, so input drift is not
  detected. The `ticket-transition` reason compares the ticket's status only (`task_status`, DEC-336). `--watch` on
  a ticket whose file is gone answers `TICKET_UNKNOWN` (exit 1).
- **The family check passes when no ticket has a checkpoint.** W1-26 runs it; whether "no checkpoint at all" should
  fail is W1-26's or W1-29's to settle.
- **Without `--json` the `--resume` brief is indented JSON text**, because `main.py` prints every result that way
  (DEC-317). W1-29's SessionStart hook injects that text.
- **The W1-46 builder test `tests/unit/launch/test_command_modules.py` uses not-yet-built commands as stand-ins**
  (`pause`, `close`). It broke when `checkpoint` was built and will break again when W1-28 builds `pause` or W1-30
  builds `close`: that ticket's lead renames the stand-in, as W1-25's did (`9c8fec02`).
- **Workers ran unsandboxed** (interim, DEC-183).
