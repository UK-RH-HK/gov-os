You are a ticket lead for ticket `DAEO-xnbx` (`W1-50`), profile FULL. This is the ticket's closing follow-up: **the freeze mirror outside the repository (owner, DEC-429) and the ticket lead's own role (DEC-434, DEC-435).** **High priority.** You work only in the worktree `/home/usain/gov-os-worktrees/W1-50-mirror` on branch `w1/W1-50-mirror`, which starts at `w1/integrate` (`19d8320a`). Everything else of W1-50 is built, merged and green. **One build round and one review (DEC-415): after the reviewer, only a fail-open hole or a silent change to tests or ticket files is fixed; everything else is a residual; no second review.**

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. A test run of your own is run in the foreground in pieces that each fit one Bash call's longest timeout, or in the background writing to a log and an exit-code file that you wait for in the foreground. Never end a message with "waiting". **Your summary is your last message**: after DONE or PACKAGES, write nothing more.

**If a worker's log or your own call shows an authentication or access error (401, 403, "Failed to authenticate", "access grant"): start nothing more, write your checkpoint, and return at once with the first line `AUTH_REQUIRED` and the state of the branch (DEC-420).**

## The three KPI lines this round builds (read them in `.tickets/DAEO-xnbx.md`)

- `gov pause` writes the freeze to `.gov-runtime/freeze` and to a mirror outside the repository, under `~/.local/state/gov-os/`, keyed by the repository; the guard treats the project as frozen if either exists (DEC-429).
- A flag in the repository that is removed or emptied while the mirror remains is a finding, and the flag is restored with its marker line; lifting in person removes both; a sandboxed worker cannot reach the mirror (DEC-429).
- A ticket lead runs under its own role, which may write only its checkpoint, its scratch and merge-backs judged by the three-way rule; a lead's write to source, tests, tickets or documents is refused (DEC-434, DEC-435).

Read in `docs/DECISION_REGISTER.md`: DEC-402, DEC-407, DEC-409, DEC-421, DEC-427 to DEC-429, DEC-434 to DEC-436, DEC-156 (the orchestrator's write rights), DEC-255, DEC-254, DEC-399, DEC-413, DEC-415, DEC-416, DEC-420; and in `governance/project/bootstrap.md` the section "W1-50 residuals" and the mid-wave audit's MWA-01.

## Safety rules of this round, above everything else

- **Nobody ever runs `gov pause`, in any form, against this repository or against any worktree of it, and nobody creates, empties or removes `.gov-runtime/freeze` here.** Freezing is the owner's action and only the owner lifts.
- **No test, worker or lead ever writes under the real `~/.local/state/gov-os/`.** A mirror entry there for this repository would freeze the project for every session. Every test runs `gov pause` and the guard only on a throwaway project in a temporary directory with a throwaway home (or whatever redirection the design settles, see below). The test designer shows in its README how each test is kept away from the real mirror, and you check it by reading before anything runs: after your whole verification, `ls ~/.local/state/gov-os/ 2>/dev/null` shows no entry made by this round (say what it showed before and after).
- The guard refuses any Bash text containing the lift form of `gov pause`; tests drive lifting through the code's interface with a pseudo-terminal in a subprocess, as W1-50's existing lift tests do.
- The ticket's `allowed_paths` are `src/gov/guard/containment*`, `src/gov/guard/decide*`, `src/gov/pause/**`, `src/gov/launch/**`, the two hooks under `template/governance/kernel/hooks/`, `tests/unit/{containment,guard,pause,launch,install}/**`. A role file, a roster line or a path-map line outside these paths is not written: if the role cannot be built without one, that is a package with the exact line. `.claude/agents/**` and `governance/project/prompts/**` are the owner's.

## Things the test designer settles from the sources and the code, or returns as packages, never as guesses

**The mirror**
- The key: how a repository is identified so that the main tree and every worktree of it share one freeze (or, if the existing flag is per tree and the code depends on that, what the sources say; a package if they do not). A moved or copied repository; two clones of one repository.
- The mirror's content (the same marker line as the flag, DEC-402) and what an empty or unmarked mirror file means (the fail-closed reading: the owner said "frozen if either exists"; an unmarked file in the repository is "no freeze, recorded" by DEC-402; say which holds for the mirror and why, as a package if the two decisions pull apart).
- Fail closed where the mirror cannot be read (no home, unreadable folder): frozen or not, by DEC-429's words; a package if open.
- **How tests redirect the mirror without giving an agent session the same lever.** If the mirror's place follows an environment variable (`HOME`, `XDG_STATE_HOME`), a session that changes it for a child looks at another mirror: say which sessions can do that, what the guard's hook reads, and whether that is inside the residual the owner already accepted ("an opaque write by the orchestrator's own unsandboxed session") or a new fail-open; a new one is a package for the owner with options.
- `gov pause` set by the owner and by the orchestrator writes both; a failure to write one of the two: what the command reports and what state holds.
- Restoring: the containment check around every Bash call (DEC-407) restores the in-repository flag from the mirror with its marker and records a finding; and the same when the flag is found missing at a session's start or at the next tool call of any kind, if the sources ask for it.
- Lifting in person (DEC-409) removes both; a lift that removes one and fails on the other.
- A sandboxed worker (`gov launch`) cannot read-write the mirror: the sandbox profile denies it; the case runs a launched command on a throwaway project where the sandbox is available and says so where it is not.
- Projects frozen before this change (a flag, no mirror): frozen, and whether the mirror is written at the next guard call or only by `gov pause`.

**The lead's role**
- Its name (proposal: `ticket-lead`), added to the known roles in `src/gov/guard/decide.py`; a lead is started by the main orchestrator, unsandboxed, with that role and its ticket in `--settings`, and starts workers with `gov launch`.
- **Stricter only:** whatever the orchestrator's role is refused, the lead is refused; nothing the orchestrator cannot do becomes possible.
- Writes allowed (Write, Edit, and Bash write targets as the guard already reads them): `.gov-runtime/scratch/lead/**` in its own worktree (its checkpoint is `.gov-runtime/scratch/lead/CHECKPOINT.md`, its briefs and logs are under it), and what its own test runs write in temporary directories, as for any role. Refused: `src/**`, `template/**`, `tests/**`, `docs/**`, `.tickets/**`, `governance/**`, and every other tracked path.
- Commits: a lead's only commit is a merge of the integration branch into its ticket branch (a merge-back), judged by the three-way rule (DEC-421 and the acceptance-test rule before it); a non-merge commit with the lead's role that changes any path is a finding; a merge-back made in a command that does not commit (`--no-commit`) is refused for this role (DEC-436 tells why).
- What a lead must still be able to do, each with a case that it is not refused: run `gov launch`, run the test suites and the validator, `git merge` and `git merge --abort`, read everything the orchestrator may read, `git log/diff/show/status`, copy a worker's log inside its scratch.
- `gov launch` started by a lead: the launched worker's identity and sandbox are as today; the lead's role cannot be launched as a worker unless the sources ask for it.
- Setting a freeze: the orchestrator may (DEC-409); whether a lead may is not decided: the stricter reading (no) holds unless a source says otherwise.
- Existing leads and suites: other tickets' leads run as `GOV_ROLE=orchestrator` until the owner changes the start line; nothing in this round changes what the orchestrator's role may do.

**Shared test files:** additions to `tests/acceptance/W1-07/w1_07_support.py` or other shared lists go on lines of their own. W1-22, W1-24 and W1-26 are being built on other branches and add lines there too.

## What you do, in order

1. Write `.gov-runtime/scratch/lead/CHECKPOINT.md`; keep it current.
2. **Test design** (brief A1, a fresh designer through `gov launch independent-test-designer DAEO-xnbx`, FULL, in proportion). Packages come back early; those inside DEC-416 the main orchestrator decides quickly, the rest go to the owner. If the designer returns packages the engineer depends on, **return PACKAGES at once** with the design committed; do not decide them and do not let the engineer guess.
3. **Check red** yourself, to the end of each suite: the new cases red on behaviour or on the absent code, said apart; every earlier suite as it was.
4. **Engineer** (brief A2, fresh, `gov launch engineer DAEO-xnbx`), on decided ground. Proportion rule DEC-135: the estimate for this round is about 150 lines of source; say the figure built.
5. **Verify**, every suite to its end, never `-x`: `tests/acceptance/W1-50`, `W1-01`, `W1-02`, `W1-03`, `W1-04`, `W1-05`, `W1-07`, `W1-28`, `W1-46` (alone, its live sessions fail beside other suites), `W1-47`, `tests/unit`, and `python3 docs/plan/tools/validate_s1.py` (ends `RESULT: ALL PASS`). Then the check of the real mirror folder named above.
6. **One reviewer** (brief A3, fresh, read-only; `gov launch independent-auditor DAEO-xnbx`). Besides its own probes: a state in which the project is frozen by the mirror and a tool call is allowed; a way for a sandboxed worker to reach the mirror; a way for the lead's role to write a tracked file or make a non-merge commit without a finding or a refusal; anything the lead's role may do that the orchestrator's may not; a test that could touch the real mirror. Fixes after it as said at the top; cases for a fix are written by a test designer, red before the fix (DEC-136).
7. **Return** DONE or PACKAGES, your last message: the head, the commits with their roles (`git log --format='%h %s | %(trailers:key=Role,valueonly)' w1/integrate..HEAD`; every commit has one), each suite's count, the reviewer's findings and what was done with each, the residuals for `bootstrap.md`, **the exact start line a lead needs under the new role** (for the owner, who edits the orchestrator prompt), the mirror's path form and key, the steps of the owner's manual check from a plain terminal with the mirror included (it is run at the wave's exit, DEC-428), the learning metrics for this round, and the temporary folders you left.

