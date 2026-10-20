---
type: probe
task: DAEO-kl5e
reviewer_session: 7c5c6aee-9af8-4d17-8fb4-2361c3dc4729
implementer_session: a23ab845-6db1-4846-82c4-811479a78d71
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 8a310cb2d5111ca7c64386b75e9970c2555b189f
---

# Probe record: W2-50, the review of the last round (DEC-758 item 2) (DRAFT, not committed — fail; packages to the owner)

- **What was probed.** This round's change only, at `8a310cb2` on `w2/W2-50`: tests `ef7c1835`, repair `83b0f2f4`
  (engineer session `a23ab845-6db1-4846-82c4-811479a78d71`), CIT-E §9 `d5334c0f`, lead checkpoint `8a310cb2`. A fresh
  read-only reviewer (role `independent-auditor`, session `7c5c6aee-9af8-4d17-8fb4-2361c3dc4729`, 2026-10-17),
  launched in the owner's form with the reading tools only; code under test this worktree's `src/` (DEC-732). Five
  probe scripts with a temporary HOME and a sibling TMPDIR, through the kernel's PreToolUse hook and `gov launch` with
  the stand-in CLI. Forms: `cp`, `install`, `mv` and `ln` into a folder, with or without a trailing slash, `-t`,
  `--target-directory[=]`, `-T`, `-r/-R/-a` with `s`, `s/`, `s/.`, globs, `cd` with relative names, `--`, option
  clusters, options after the operands, destinations through `..` and `/.`; a symbolic link, a hard link, a nested
  link and the marker at `<folder>/<name>`, inside the repository (W2-H056) and in the own folder; `--parents`. F2: a
  clone, a worktree and a `.git`-file project with forged tickets inside the own folder, reached directly and through a
  link. Ordinary copies; the guard's time on trees of 2 000 to 20 000 entries. W2-50: 305 passed; `git status --short`
  empty before and after; real `~/gov-os-runs` ABSENT.
- **What it found.**
  1. **A, high; fails open, loses work, changes acceptance tests.** `cp --parents` into a folder writes
     `<folder>/<source path as written>`, not `<folder>/<name>`. With `..` in the source (no link needed), or through a
     link at a middle level, the guard allowed it. Run for real: an engineer overwrote the project's acceptance test
     (`cp --parents ../../tests/acceptance/W2-90/test_a.py -t <project>/src/app`), and a session overwrote another
     ticket's file under the root (`cp --parents ../W2-91/work.txt ~/gov-os-runs/W2-90/`). Older than this round for
     the repository, but DEC-758 F1 and CIT-E §9 claim every copy into a folder is judged as each file it writes and
     W2-H056 is closed; the own-folder form breaks the KPI's "another ticket's folder" line.
  2. **B, pre-existing since W1-46, outside the round; fails open, changes acceptance tests.** The option parser reads
     a `t` inside an option's value as `-t` (`cp -S.t`, `cp -bS.t`, `install -S.t`, `install -oroot`, `install -m+t`),
     and `cp -- -t F` judges nothing; `cp -S.t` and `cp -- -t` were run for real and each overwrote an acceptance test.
  3. **C, low.** `ln -f` and `ln -sf` into the own folder (with or without a slash) replace the marker; the session can
     then rewrite it through the other name, losing its own folder or handing it to another repository. No write
     outside the session's scope.
- **Found sound.** Every other copy, install and move form into a folder, with a symbolic link, a hard link, a nested
  link or the marker at `<folder>/<name>`, refused with the guard's reason, inside the repository and in the own
  folder. F2: no own folder for a project under the root, in the guard (Write, Edit, `cp`, `touch` refused under the
  root outside the project; in-project writes allowed) and in `gov launch` (write list only the temp folder, nothing
  made under the root, markers unchanged), reached directly or through a link. Speed: at most 1.1 s; more than 10 000
  paths refused; the hook's deadline fails closed. Ordinary copies, installs and moves into the own folder, `cp -t
  src/app X`, `cp -r` into a new folder, a copy over an ordinary file: allowed. Refused as before this round: `cp X
  src/app/` (the folder itself is judged against `src/app/**`); new refusals of difference 18 (a glob with no match,
  more than 10 000 entries) minor.
- **Judgement: fail.** Finding A lets an implementer change acceptance tests and a session write in another ticket's
  folder. By DEC-758 item 2 it goes back to the owner as a package, with no further round; B is a package (a fail-open
  hole outside the round); C is a residual.
