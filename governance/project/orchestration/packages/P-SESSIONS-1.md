# P-SESSIONS-1: sessions that run without a courier (the owner's four items, 2026-11-15 ~23:40)

The problem, in the owner's words: the way sessions run is stalling the work and making the owner the courier. What
stalls today:
- the adopting sessions (the EXAMIN CTO and the six W2-81 sessions) run interactively in tmux: trust screens,
  permission questions, wakes typed into a pane that can be lost or can hit a question;
- every routine job in another repository passes through the owner's chat to the operator and back;
- commands handed out unrehearsed came back wrong (tonight: the W2-81 run mode, the start line);
- the CTO's own inbox waiter lapsed twice tonight, and returns sat unread for 50 minutes.

## Item 1: adopting sessions run headless, like leads

**What it takes.** `tools/adopter.sh` (built and rehearsed tonight):
- `start` runs `claude -p` in the repository, with the tools set at launch (`--permission-mode acceptEdits
  --allowedTools Bash Read Edit Write Grep Glob Skill 'Read(//<replies folder>/**)'`), in the background, and with only
  `GOV_ROLE=orchestrator` and `GOV_TICKET=<its coordination ticket>` of Gov OS's variables.
- When the session ends its turn (it stops for a reply), the process exits and writes an inbox item. That wakes me; I
  read its reports, write the reply, and run `adopter.sh resume <name>`, which is `claude -p --resume <its session>
  "Read the replies file and continue."`. One run per session at a time.
- `adopt` takes over a session started in tmux: once its pane is idle I end that tmux session (by its exact name) and
  register its session id. The headless resume keeps its whole context; the transcript is the same file.

**Rehearsed (scratch, 23:50-23:57):** a headless start that read a replies file and acted on it; a resume of the same
session id that read the new reply and kept its earlier context; the inbox item on each exit; the second run refused
while the first was live. No trust screen and no permission question appeared.

**What it removes:**
- tmux typing, lost wakes and trust screens;
- the replies-folder question;
- the owner's operator restarting sessions;
- your operator's 5-minute question handler, for these sessions.

**What changes for you:** the sessions no longer show in Remote Control. You read their reports and findings in their
repositories; each run's full output is in `adopters/<name>-<n>.json`.

**What you approve:** the switch, for the EXAMIN CTO and the six W2-81 sessions. It changes how the measured sessions
are started: P-EXAMIN-CTO-1 has your operator start and restart the EXAMIN CTO. Each moves at its next stop for a
reply; nothing is cut mid-turn. **Your line:** `yes P-SESSIONS-1 item 1`.

## Item 2: operator jobs through a queue, on your one-line yes

**What it takes.** A job runner in the operator agent, beside its ACT runner, and on its cron:
- I build a job bundle in `<scratch>/jobs/JOB-<id>/`:
  - `job.sh`: the commands;
  - `manifest.json`: the sha256 of each file, the folders it may write, its class "routine";
  - `REHEARSAL.md`: item 3's result, exit 0;
  - `expected.txt`: taken from that rehearsal.
- I queue `queue/JOB-<id>.req` (`JOB-<id> <manifest sha256>`) and ask for your line `yes JOB-<id> <sha8>`, alone on a
  line in this chat.
- The runner's gates, all failing closed:
  - J1: the bundle frozen and hashed;
  - J2: rehearsed, exit 0;
  - J3: your yes line found in this CTO session's transcript, by the same code as the ACT runner's G6
    (`opcommon.find_owner_line`);
  - J4: the path rule. `job.sh` writes only the folders the manifest names: never the Gov OS repository's control
    paths, `~/.local`, `~/.claude` or the operator's own folder. No sudo, no install, no push, no tag;
  - J5: the holds (act-in-progress, a release hold).
- It then runs `job.sh` in a clean environment (no GOV_*), with a timeout. It writes `jobs/JOB-<id>/RESULT.md` (the
  output, the exit code, the diff against `expected.txt`) and an inbox item, so the result comes back to me directly.

**It does not cover these, which stay with you as now:** the re-pin and the release sitting, anything with sudo, and
ACTs, which keep their review and their (b)-class yes.

**What it removes:** you carrying commands to your operator and output back. A job runs within the runner's poll after
your yes.

**What it needs from you:**
- the runner's bytes. The operator's folder is closed to my writes, so it is installed by you, or by your operator on
  your word, like ACT-OPERATOR-1. I build it with a review and a rehearsal in a clone of the operator folder;
- a 2-minute poll for jobs, instead of the ACT runner's 10, which is a crontab line;
- then your `yes JOB-<id> <sha8>` per job.

**Your line now:** `yes P-SESSIONS-1 item 2` to have me build ACT-OPERATOR-JOBS-1 for your approval. Cost: about 2
hours to build, review and rehearse.

## Item 3: every command rehearsed first, its expected output from the rehearsal

**What it takes.** `tools/rehearse.sh <id> <source repo> <command>` (built and rehearsed tonight). It clones the
target into scratch, runs the command there with no GOV_* variable, and writes `rehearsals/<id>/RESULT.md`: the
command, the exit code, the output, and the clone's status and last commits after it. Every command I hand to anyone
cites its RESULT.md, and the expected lines are copied from it, never written from memory. Item 2's runner refuses a
job without it (J2).

**What it removes:** commands that fail on first use.

**What you approve:** nothing. **Switched tonight:** the tool, and the rule in my standing memory.

## Item 4: the inbox waiter and the helper watch cannot lapse silently

**What it takes:**
- (a) **Tonight, no decision needed:** `tools/waiter_guard.sh`, a background task of my session, now armed. It exits,
  and so wakes me, at the first of:
  - an inbox item unread for more than 10 minutes;
  - no inbox waiter alive for 2 minutes;
  - no helper watch alive for 2 minutes;
  - a 24-hour heartbeat.

  Rehearsed. Its first live run woke me on four items unread since 23:04, among them W2-174's return.
- (b) **The outside check**, for when my session itself is stuck. The sentinel's dead-man watch (`deadman.py`, the
  sentinel's brief) gains one rule: an inbox item unread for more than 10 minutes, or no waiter-guard process alive,
  makes the sentinel send my session a cross-session message. Such a message wakes an idle session, which the inbox
  route cannot do when my waiter is down. If the item is still unread 10 minutes later, it pushes you, as the dead-man
  does today. `deadman.py` and the sentinel's brief are control files, so this is an ACT.

**What it removes:** silent lapses of 50 minutes or more.

**What you approve:** (a) nothing; it runs now. (b) ACT-DEADMAN-INBOX-1, after its review: your `yes ACT-DEADMAN-INBOX-1
<sha8>` when I bring it. **Your line now:** `yes P-SESSIONS-1 item 4b` to have me build it. Cost: about 1.5 hours.

## Order and cost
- Items 3 and 4a are live tonight.
- Item 1 switches each session at its next stop after your yes, starting tonight.
- Items 2 and 4b are built tonight after your yes and come back as an install and an ACT for your approval tomorrow
  morning.
