
## W1-32: `gov status` and the launcher's two residuals (DEC-392, DEC-449, DEC-526; 2026-10-08)

Merged from `w1/W1-32` at `ff85c968` (81 cases; 266 source lines added against an estimate of 80: about
190 in `src/gov/status/command.py`, about 75 in the launcher). `gov status --json` always answers
`ok: true` with exit 0 (W1-07 holds it to exit 0 without a store) and gives `tickets` (ready, blocked with
reasons, claimed with holder), `decision_packages`, `readiness`, `governance_share`, `pause`, `doctor` and
`not_read`; whatever could not be read is `{read: false, reason}` and is listed under `not_read`. The
launcher ends its session on SIGINT, SIGTERM and SIGHUP (asked first, killed on a second signal or 5 s
later), removes the session's folder and ends with 130; a failed removal keeps the session's exit code.
Merged as built under DEC-526 while package P-19 is with the owner; the ticket is not closed.

Not covered or not built, by name:

- **The natural-language half of CAP-28.a.** No skill, role file or instruction line routes a status
  question to `gov status --json`; the file would lie in `.claude/**`, `CLAUDE.md`, `AGENTS.md` or the
  kernel skills, outside the ticket's paths. No case covers it (P-19 point 2).
- **Governance share in status** is "not measured" for every claimed ticket: nothing records a ticket's
  sessions (DEC-491), so the counter is asked with no session named.
- **Gates:** only open decision packages and specifications with an open required readiness row are
  shown. Audit tickets (DEC-088), the check gates and `gate` records are not.
- **`src/gov/status/command.py`:**
  - a ticket constrained by a package whose record could not load is still listed `ready` (the READY
    rule in `src/gov/tasks/queue.py`, outside the paths, fails open here);
  - an absent `.tickets/` or `openspec/changes/` reads as an empty list;
  - the store is trusted when it holds `HEAD`'s commit and its tables answer: rows removed, or a store of
    a later commit, read as clean; the store is probed once and read again, so a break in between gives
    an unmarked empty `ready`;
  - records come from `HEAD` only: an uncommitted package is not shown and nothing says so;
  - any Markdown record at `HEAD` that the load cannot take appears under `decision_packages` as not
    read, not only likely packages;
  - status imports two private functions (the loader's `_read_records`, the guard's `_mirror_frozen`); a
    missing mirror folder reads as not frozen, the guard's own reading;
  - doctor's part states are passed on as the status word only, without reasons;
  - the exit code is 0 even when parts were not read;
  - it is as slow as doctor (10.9 s under load).
- **`src/gov/cli/commands/status.py`** is dead code, outside the ticket's paths.
- **`src/gov/launch/launcher.py`:**
  - only the session process is signalled, not its process group: a command the session started can
    outlive it;
  - SIGQUIT, SIGUSR1 or SIGKILL to the launcher leaves the session running and the folder in place;
  - a signal ignored on entry (`nohup`) stays ignored;
  - a launcher signal in the instant after the session ended on its own gives 130 instead of its code; a
    session killed by a signal passes on a negative code;
  - an error other than `OSError` from the removal, or an error restoring the handlers, would replace
    the exit code;
  - the handlers need the main thread: `launch()` from another thread raises before anything starts.
- **`src/gov/cli/main.py`** (outside the paths): a refusal printed to an unwritable stderr ends with a
  traceback's code; no session exists on that path.
- **The command list:** `gov --help` shows `ci`, `launch` and `telemetry` beyond the twelve reserved
  names; the suite pins the three as found and goes red when another command is added (P-19 point 3).
- **Checkpoints:** four real records under `docs/checkpoints/DAEO-8goq/`; the command numbered the first
  one 0002 and there is no 0001.
- **Sandbox:** placeholder dotfiles and `docs/source` show as untracked inside a worker's sandbox; the
  designer could not read S0a-G-01 there. The hook's containment notice attributed the designer's files to
  the lead's waiting call (DEC-253 to DEC-255).
- **Latency under load (DEC-372):** in the lead's full runs one W1-05 p95 case and one W1-19 p95 case
  failed while two suite streams ran side by side; each passed alone.
- **KPI disputes:** six (four from the test designer, two from the lead's reading of the diff), all in
  package P-19. **Acceptance tests rewritten after implementation began:** none; eleven cases were added
  after the lead's diff reading (nine red first, two guards).
