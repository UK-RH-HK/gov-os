---
judgement: fail
probed_commit: ba807a032603
reviewer_wrote_nothing: true
---
# DRAFT (failing review, not committed): W2-05 round DEC-970 (package I (b), P-W2-05-DRIFT-BASE), review 1 of 2

Reviewer: rev4 (independent-auditor, gov launch, sandboxed, effort max), session 15c16bc9. Full return: `log/rev4-pkgI.json`.
Probed: `0cfa8684f720..ba807a032603` (engineer `b173cb5792e2`, `ee4e3bae9333`; test designer `f5968e9cffb7` merged as `8be7828faa72`; checkpoint `ba807a032603`).
Method: P1 to P6 probes in the sandbox's temporary folder, no suite re-run (the person's configuration against `_started` with a positive control; values and injection; the file's life and failing closed; `_alone` and `_bisect` for real in throwaway projects; the drift construction; the repository's identity wins).

## Findings

**R4-1 (high): the bisect step's tests get git's own `GIT_DIR`, `GIT_EXEC_PATH`, `GIT_PREFIX`**
`git bisect run` exports them to the step; a red test that runs git in a folder of its own with the inherited environment acts on the night clone and, through it, on the project: `main` moved onto a foreign merge, a foreign branch appeared, once the person's commit fell off `main`; `_bisect` named a commit outside the project's history. Batch 2's form does the same.
- Ordinary work: yes, because a red night on such a test after a green night starts `_bisect`; git exports the variables itself.
- Consequence: loses work

**R4-2 (low): with a checkout filter in the person's configuration (Git LFS), the pinned `bisect start` refuses**
- Ordinary work: yes, because `git lfs install` puts its filter in `~/.gitconfig`.
- Consequence: other

**R4-3 (low): a Latin-1 `user.name` stops every close with UnicodeDecodeError; a raw CR comes back as LF**
- Ordinary work: no, because current terminals and editors write UTF-8.
- Consequence: other (fails closed)

**R4-4 (low): SIGTERM to the close leaves the generated folder (name and email) in the temporary folder**
- Ordinary work: yes, because sessions and tool time limits send SIGTERM.
- Consequence: other

**R4-5 (info): with no writable temporary folder, the generated folder sits in the project for the run**
- Ordinary work: no, because it needs every temporary folder unwritable.
- Consequence: other

**N-1: an identity kept only in an included file does not reach the run (by design)**
- Ordinary work: yes, because dotfile setups use includes.
- Consequence: other (fails closed)

Found sound: the generated file's keys, precedence and values (16 of 18 tricky values byte for byte, no injection); only the three variables reach a `_started` run; trace, hooks path, fsmonitor, aliases, credential helper, safe.directory, signing inert; the file removed on end, time-out and interrupt; fails closed without a temporary folder or git; W2-M161 holds; `_bisect`'s start, run and reset get runner_env; DRIFT-BASE lowers nothing and each drift case turns on its plant.
