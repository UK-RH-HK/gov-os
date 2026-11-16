# P-JOBS-USER-1: the job runner needs an OS boundary between the agents and what they must not reach

## 1. Why
Ten review rounds of the job runner (DEC-1191 (2), drafts/operator-jobs/) closed every hole found inside the runner,
and round 10's fresh review (2026-11-16) found three more, two demonstrated on planted copies. All three come from one
root, which the reviewer named and I share: **the CTO's sessions and the runner are the same Unix user (usain).** That
user can rename a key or a held-out file anywhere it can write, and append a byte to it, without ever reading it:
- B1: a routine job climbs (`cd ..`) to the host's `/` and reads a key moved into `/var/tmp`;
- B2: a rename plus a one-byte append changes the file's hash, so the content index misses it; your yes would see
  only a harmless file name in the view list;
- B3: a key moved through an R2 job's output folder mid-run reaches the CTO;
- and the refusal message is an oracle that confirms a guessed small held-out file.
Each can be patched in the runner, and each patch has so far opened the next hole. The guard hook in the CTO's session
does not stop these: it judges the commands it can resolve and lets through writes it cannot. The runner is paused
(no install today); your interactive Terminal Operator stays the route.

## 2. Options
| | (A) Separate Unix users | (B) The CTO's and leads' sessions in an OS sandbox (SANDBOX-1's form) | (C) No runner |
|---|---|---|---|
| What | `govop` owns the operator folder and the held-out set (0700) and runs the runner from its crontab; the CTO's sessions run as `govcto`, whose group may only drop requests into the queue; you keep `~/.ssh` | the CTO, leads and adopting sessions start under bwrap, as `gov launch` already starts workers (SANDBOX-1, DEC-1128 (4)): `~/.ssh`, credential files, the sets root and its workbench are not mounted at all; the operator folder is read-only but its `queue/` is writable; the runner stays usain's | your interactive Terminal Operator stays the courier for every job you approve (today's state) |
| Closes B1-B3 and the oracle | yes, by file ownership (the builder's SEPARATE-USER-NOTE.md) | yes for keys and held-out: what is not mounted cannot be moved; the runner's index becomes a second check | nothing to close |
| Your steps | root, once: `useradd` x2, `chown`/`chmod` of the operator folder and the sets root, `crontab -u govop`; a Claude login for `govcto`; the repository, worktrees and stores readable/writable by `govcto` (group) | none as root; one start-line change for the sessions you start (I give it, rehearsed), and a re-start of the CTO session in it | none |
| My work | the runner rebuilt around the uid boundary; every tool that writes the operator folder or reads the sets root re-checked; sessions moved | a session wrapper (bwrap allowlist: the repository, worktrees, gov-os-runs, ~/.local read-only, the operator queue; masks for the rest), built, reviewed on copies, rehearsed; the guard's rules stay; the runner keeps its current design with the content index as a backstop | none |
| Cost | about a day of mine plus your root steps and a re-login; every path and permission touched; hard to undo | about half a day of mine plus one review; undone by starting a session without the wrapper | you stay the courier: the stall P-SESSIONS-1 set out to remove |
| Risk | broad: ownership errors stall leads; two logins to keep | a tool the CTO needs may sit outside the allowlist (found by the rehearsal; added by name); sessions you start by hand must use the line | none new |

## 3. Recommendation
**(B).** It puts the agents behind the same wall the workers already have, needs no root step and no new user, and is
undone by one start line. (A) is the stronger wall and could follow later if (B)'s allowlist proves hard to keep; it is
also the shape the Wave 3 row for the agent-to-agent layer (DEC-1195) would want per product. Confidence: medium; the
open question is how much of the CTO's tooling reaches outside the allowlist, which the rehearsal answers.

Until you decide, the runner stays paused and uninstalled; the act-O kind (P-ACT-O (a)), F11 and OPROOT wait with it.

## 4. Your line
`P-JOBS-USER-1 (A)`, `(B)` or `(C)`.
