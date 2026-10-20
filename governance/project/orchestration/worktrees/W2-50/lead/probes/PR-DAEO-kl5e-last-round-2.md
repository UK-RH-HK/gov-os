---
type: probe
task: DAEO-kl5e
reviewer_session: 8623e319-8684-4c03-9468-93cbf86ccff1
implementer_session: 3024c21e-7e82-45cf-ae22-d784bac7fcca
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 2d60cdd3b8773ac6803d004afb16b10e85652a92
---

# Probe record: W2-50, the review of one more short round (DEC-764 item 3) (DRAFT, not committed — fail; packages to the owner)

- **What was probed.** This round's change only, at `2d60cdd3` on `w2/W2-50`: tests `41aa00c0`, repair `83756def`
  (engineer session `3024c21e-7e82-45cf-ae22-d784bac7fcca`), CIT-E §10 `3787cc79`, lead checkpoint `2d60cdd3`
  (CP-DAEO-kl5e-0037). A fresh read-only reviewer (role `independent-auditor`, session
  `8623e319-8684-4c03-9468-93cbf86ccff1`, 2026-10-18), launched in the owner's form with the reading tools only; code
  under test this worktree's `src/` (DEC-732). 116 forms through the kernel's PreToolUse hook with the suite's fixture
  (temporary HOME, a sibling TMPDIR, a fixture project built from scratch, own folders made by a launch). The guard's
  option tables against GNU coreutils 9.4 (every short letter, every `--help` long name, value or none). Where `cp`,
  `install` and `mv` land a backup when the destination is a symbolic link, run in a scratch folder. `--parents` in
  every spelling; value-taking options with `t`, `-t`, `--` or a leading `-` in the value; clusters; options after
  operands; `POSIXLY_CORRECT`; every `--` placement; backups; the controls; hook timing. W2-50: 358 passed;
  `tests/unit/guard/test_runs.py`: 78 passed; `git status --short` empty before and after; real `~/gov-os-runs`
  ABSENT.
- **What it found.**
  1. **D, medium; a write outside the role's scope, conditional; no work lost.** With `-b`, `-S`, `--suffix` or
     `--backup`, `cp` onto a symbolic link does not write through it: it renames the link to `<link><suffix>` and
     makes a new regular file at the link's own path, in the link's folder (confirmed by the lead in a scratch folder:
     `test_x.py` a new file, `test_x.py~` the link, the target unchanged). The guard judges the link's target and
     `<target><suffix>` instead, so `cp -b X <link>`, `cp -S.t X <link>`, `cp --backup[=simple] X <link>` and
     `cp -b -t <other ticket's folder> mylink` were allowed where the link sits in another ticket's folder (or the
     acceptance folder) and points into the session's writable area. The session cannot make such a link itself
     (`ln`, `cp -s`, `cp -P`, `cp -a` into those places are refused). The forms were allowed before this round too,
     but this round's backup judgement and §10 claim to cover them.
  2. **Outside this round, the same cause:** `install X <link>`, `mv X <link>` and `cp --remove-destination X <link>`
     onto such a link replace the link itself and are allowed.
  3. **The record.** §10's claims that a backup is judged "beside each file the call replaces" and that W2-H056 is
     closed within its scope do not hold for a link destination, and "What stays open" omits the case.
- **Found sound.** The option tables match coreutils 9.4 exactly; `-Z` takes no value, so `cp -Zt <folder> X` is
  judged as a copy into `<folder>` (the lead's reading agreed). `--parents` is refused as doubt in every spelling
  (`--pa` to `--parents`, `--path`, `--parents=x`) and position (with `-t`, `-a`/`-r`, after an operand, after `--`,
  into the own folder); `mv`/`install --parents` are refused as unknown options; `cp -- --parents D` copies a file of
  that name and is allowed. Values with a `t`, values that are `-t`, `--` or `--target-directory`, clusters
  (`-pvS.t`, `-St`, `-vt`, `-Zt`, `-gt`, `-Dt`), long forms with `=`, as the next word and abbreviated, options after
  operands, `POSIXLY_CORRECT=1` and every `--` placement, for `cp`, `install` and `mv`: judged as the files they
  write, refused where they should be. Backups to ordinary files, `mv -b -T` within the own folder, and every control
  of the brief: allowed. Slowest hook call 225 ms; nothing timed out or failed open. No ordinary call newly refused
  (`cp X src/app/` refused for the folder itself is §9's, with or without `-b`).
- **Judgement: fail.** Finding D lets a role write outside its scope (another ticket's folder, or the acceptance
  folder) under a precondition the session cannot make itself; no work is lost. By DEC-764 item 3 it goes back to the
  owner as a package, with no further round; finding 2 is outside the round; finding 3 corrects the record.
