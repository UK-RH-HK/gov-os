---
type: probe
task: DAEO-0z8c
reviewer_session: 9de6febd-0c06-466b-b234-bbb059c4e6a0
implementer_session: 4eda27e8-7aae-4c9e-bf5d-0c8834be1e4b
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: f8e85f531cbf7663b2772a4451282f94063299bd
---

# Probe of W2-05 (DAEO-0z8c), the DEC-970 round, at f8e85f531cbf

**Probed:** head f8e85f531cbf on `w2/W2-05`, the round DEC-970 declared (package I (b) and P-W2-05-DRIFT-BASE), from 0cfa8684f720: engineer b173cb5792e2 (the test runs' and the bisect's environment through the run environment helper) and ee4e3bae9333 (sweep row 66, `gov release`, open); test designer f5968e9cffb7 (the drift cases' one-source base pair, merged as 8be7828faa72); the fix of the first review's R4-1, engineer 3a12c208b728 (the bisect step's tests get only the run's environment) and test designer d775baf9c4b9 (the acceptance cases for it, merged as e9a4fdd351fe); the lead's checkpoint records ba807a032603 and f8e85f531cbf. The code under test is this worktree's `src/` (DEC-732): `gov.__file__` is `/home/usain/gov-os-worktrees/W2-05/src/gov/__init__.py`.

**Who:** a fresh, read-only QA engineer (role `independent-auditor`), started through `gov launch`, sandboxed, `--effort max`; its only repository writes were the sandbox check's git object and index refresh. This is the round's second and last review (DEC-413, DEC-916). The first review, at ba807a032603, judged fail on R4-1 (below); its record stays a draft under the lead's scratch.

**Method:** it read the ticket, DEC-970's W2-05 line, the round-3 record, the round's diff and the fix's diff, the unit and acceptance cases, the sweep rows and the README, and ran seven probe scripts in its temporary folder against this worktree's `src/`; no suite was re-run (DEC-959 item 1):
- P1: the run environment helper, with stand-in XDG and `~/.gitconfig` files carrying the three settings and trace2 targets, hooks path, bare, fsmonitor, editor, a stored-login helper, `safe.directory`, signing, alias, url rewrite, template, include, includeIf, proxy, `useConfigOnly`; 22 values of the name; 23 `GIT_*` variables planted in the caller and passed through `_started`;
- P2: the run file's life (end, time-out, SIGINT, SIGTERM) and failing closed (no git, a hanging git, a failing git, no temporary folder);
- P3: three real nights through `python3 -m gov.close.nightly` with a real `git bisect run` on a throwaway project whose red test runs git in a folder of its own with its inherited environment (a clean caller; a caller carrying `GIT_DIR`, `GIT_WORK_TREE`, `GIT_PREFIX`, `GIT_EXEC_PATH` and a trace variable; a project with its own `post-checkout` hook);
- P4: the DRIFT-BASE structure; P5, P5b: the hand-over's edges; P6: a removed run file; P7: a person whose configuration is named by `GIT_CONFIG_GLOBAL`, and the environment's size.

## Findings

Classification (DEC-809): R5-1 no/other; R5-2 no/other; R5-3 no/other; R5-4 no/other. R4-1 is fixed (verified). The first review's R4-2 to R4-5 and N-1 are unchanged by the fix.

**R4-1 (first review, high, fixed): the bisect step's tests got git's own `GIT_DIR`, `GIT_EXEC_PATH` and `GIT_PREFIX`**
- What was done: a throwaway project, `main` checked out nowhere; a red test that runs git in a folder of its own with its inherited environment; the nightly's bisect.
- What happened (at ba807a032603): `git bisect run` exported those variables to the step; the test's git acted on the night clone and through it on the project (`main` moved, a foreign branch, `core.bare = true`, a foreign first bad commit, a bisect that never ended).
- Now (f8e85f531cbf): in three real nights each step's test saw exactly the alone run's environment (only `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`, `GIT_NO_LAZY_FETCH`; the run's `PATH`); the project's refs, HEAD, index, status, configuration, reflogs, worktree list, reachable commits and hooks folder were unchanged; the culprit was named; the night ended red in 17 to 19 s.
- Ordinary work: yes, because a red night on such a test after a green night starts the bisect, and git exports the variables itself.
- Consequence: loses work (fixed).

**R5-1: an environment over 128 KiB stops the night's bisect from starting (row; low)**
- What was done: two 70 KB variables in the run's environment.
- What happened: the whole environment, handed to the step as one variable (149,190 bytes), was over Linux's limit for one string; git could not start ("Argument list too long"); the bisect package named no first bad commit, without saying why.
- What should have happened: the bisect runs, or the record says it could not.
- Ordinary work: no, because an ordinary environment is far below the limit (this session's hand-over: 9,375 bytes).
- Consequence: other (the night stays red with its P1 package).

**R5-2: a bisect whose every step is untestable names the head as the first bad commit (row; low)**
- What was done: the step made unable to read its hand-over (for the probe only).
- What happened: every step answered untestable (125), never good; git ended "We cannot bisect more!"; the older fallback read the bad mark and named the head.
- What should have happened: no first bad commit named when the bisect did not converge.
- Ordinary work: no, because the nightly always gives the `bisect run` call its hand-over, and a real environment's hand-over reads back.
- Consequence: other.

**R5-3: a lone carriage return in one of the person's three settings becomes a line feed (row; cosmetic)**
- What was done: 22 values of the name written by git into `~/.gitconfig` and read through the run's file.
- What happened: 21 exact, none injected a setting or section; a CR not followed by LF came back as LF.
- What should have happened: the value as git reads it.
- Ordinary work: no, because a carriage return inside a name, address or branch name does not occur.
- Consequence: other.

**R5-4: a person whose configuration is named by `GIT_CONFIG_GLOBAL` gets no identity in the run (row; low)**
- What was done: a caller whose `GIT_CONFIG_GLOBAL` names a file with their name, no `~/.gitconfig`.
- What happened: the run's file was empty; a test committing without its own identity is red, as under `/dev/null`.
- What should have happened: the identity the person's git finds.
- Ordinary work: no, because a person's global configuration ordinarily lives in `~/.gitconfig` or the XDG file.
- Consequence: other (fails closed).

Rows of the first review, unchanged: R4-2 (a checkout filter in the person's configuration, as Git LFS installs one, stops the pinned `bisect start`; Ordinary work: yes; Consequence: other), R4-3 (a Latin-1 `user.name` stops the close; no; other), R4-4 (SIGTERM to the close leaves the generated folder; yes; other), R4-5 (no writable temporary folder; no; other), N-1 (an identity only in an included file; yes; other, fails closed).

Notes: N-5, the pinned bisect's checkouts run the project's own `.git/hooks`, not a global hooks folder (Ordinary work: no; Consequence: other). N-6, a test's `git config --global` writes the run's own file, never the person's (Ordinary work: yes; Consequence: other).

## Found sound

- The run's file holds only `user.name`, `user.email` and `init.defaultBranch` (`~/.gitconfig` over the XDG file); every other planted setting inert; neither trace2 target written; a commit in a fresh repository made as the person on the person's default branch; a repository's own `user.name` wins; values survive with no injection (R5-3 apart).
- None of 23 planted caller `GIT_*` variables reached a `_started` run; it saw only the three; everything else kept; nothing left in the project.
- The run file removed at end, on time-out and on SIGINT (SIGTERM: R4-4); a process outliving the run falls back to no identity, no trace, no `~/.gitconfig`.
- Fail closed: no git, a hanging or failing git: the run goes ahead pinned with an empty file; no temporary folder: nothing runs; no handler turns an error into a pass.
- The hand-over reaches only `bisect run` (1 of 66 git calls by name) and no test; `bisect start` and `reset` keep the round's environment; steps and the alone run commit with the same identity.
- W2-M161 holds: the person's trace2 target written only by the night's own clone creation and removal (unpinned by design, rows 54 and 56); no test run, bisect step or bisect command wrote it; `GIT_CONFIG_NOSYSTEM=1` in every run.
- The sweep's rows 36, 51, 52, 55 and 66 describe the code as it is.
- DRIFT-BASE: no expectation lowered, no case removed, ids kept; a green control over the one-source base pair before each plant; each plant changes exactly its own event.

**Judgement: pass.** No finding is "yes" with "fails open" or "loses work"; R5-1 to R5-4 go to the Wave 3 hardening pass (DEC-801).
