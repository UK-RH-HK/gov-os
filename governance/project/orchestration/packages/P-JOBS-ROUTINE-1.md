# P-JOBS-ROUTINE-1: the standing rule for routine operator jobs (the owner's principle, 2026-11-16 ~01:10)

The principle, in the owner's words: routine jobs run without a yes each time; the owner's yes covers only jobs that
change something. Anything outside the routine classes still needs `yes JOB-<id> <sha8>`.

## 1. The routine classes, each with its limits
The runner never trusts a job's claim of a class. It checks the class from the manifest and the bytes, and a job that
fails the check is not refused: it waits for a yes like any other job.

**R1. Status checks (read-only).**
- **Examples:** `git status`/`log`/`diff --stat`, `gov status`/`doctor`/`check`, `tk ls`/`show`, `ps`, `df`, `free`,
  `ls`, and reading non-secret files.
- **Limits:**
  - in the bwrap sandbox with no writable bind at all, only a private throwaway /tmp;
  - no network;
  - no secret path and no held-out path, read or named (the runner's existing refusal);
  - `may_write` empty;
  - no `git commit`/`push`/`tag`, no `gov adopt`, no `gov close`, no `tk` change command (create, start, close, edit);
  - output capped at 200 lines;
  - timeout 300 s;
  - at most 12 runs an hour in all.

**R2. Read-only runs that write only their own output.**
- **Examples:** a measure, a test run of a copy, a summary whose results go to a file.
- **Limits:** R1's limits, except one writable folder that the runner makes fresh for the job,
  `~/gov-os-runs/routine/JOB-<id>/`, never inside a repository, a `.git` folder, `~/.local`, `~/.claude` or the
  operator's folder. Also:
  - the output folder is capped at 1 GB (checked after the run; over it, the result says so);
  - timeout 2 h;
  - at most 6 runs an hour.

**R3. Standing scripts: restarts, re-arms and resumes the sandbox cannot hold.**
- **Examples:** restart the sentinel session after a login drop, re-arm the sentinel's check, restart a crashed
  watcher.
- **The rule:** each standing script is approved by you once, by its bytes: `yes JOB-STANDING-<name> <sha8>`. After
  that, an instance runs without a yes when its `job.sh` is byte-identical to the approved script and its parameters
  match the script's declared patterns (for example, a session name `^w281-[a-z-]+$`).
- **Limits:** each script states its own runs-an-hour limit (default 2). A changed byte is a new script and needs your
  yes again.
- **Scope:** this is the only routine class that runs outside the sandbox, because a restart needs tmux and the CLI.
  So each script is shown to you in full when you approve it.
- **Not included:** resuming the headless adopting sessions. I do that myself with `adopter.sh`, and it is no operator
  job.

## 2. What always needs your yes
Any job that:
- writes to a repository or commits;
- touches `~/.local` (the re-pin);
- uses the network;
- reads the sets root (summary-only hidden-set jobs, DEC-1193);
- is an (O) ACT;
- fails a routine class's check;
- or is a standing script's first run, or any change to it.

## 3. How you see what ran
- **The routine log:** every routine run is a line in `~/gov-os-operator/log/routine-YYYY-MM-DD.md`, with the time,
  the job id, the class, the command's first line, the exit code and the number of output lines. Its full result is in
  the job's `RESULT.md`.
- **Your digest:** my status blocks and the morning digest give the count of routine runs since the last report, by
  class, and name any that failed or hit a limit.
- **Your off switch:** removing one file, `~/gov-os-operator/install/routine-allowed` (the install writes it on your
  yes), turns every routine class off at once. From then on every job waits for a yes.

## 4. What it takes
- The runner's builder adds the class checks (R1/R2 from the manifest and the sandbox binds; R3 by hash against an
  approved-scripts list `install/standing/`), the rate limits, the routine log, the marker file, and tests for each
  class, each limit and each fall-back to "needs a yes".
- The review now running on the frozen runner covers the base. A fresh review then covers this addition's delta before
  the install, so the first install carries it.
- **Cost:** about 1.5 hours to build and review.

## 5. Recommendation
**(a)** all three classes as written, confidence medium-high. R1 and R2 are held by the sandbox. R3 is held by your
one-time approval of each script's bytes.

**Your line:** `P-JOBS-ROUTINE-1 (a)`. Or name the classes you want, for example `(a) R1 R2 only`. Or adjust a limit.
