---
type: probe
task: DAEO-kl5e
reviewer_session: 7c3f4e9d-411e-4f7b-a533-708675d0629a
implementer_session: not recorded (the repair engineer's log was cut at the two-hour limit of its launch; the record's engineer was c5d8936f-cc9d-45fc-85f7-e6994592469c)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: fc9e6a2ad67df3e9536e5236e957bc95930c3def
---

# Probe record: W2-50, the review of the last round (DEC-774, DEC-778) (DRAFT, not committed — fail; every finding a row under DEC-779; the owner rules at the close)

- **What was probed.** This round's change only, at `fc9e6a2a` on `w2/W2-50`: tests `2956f9e7` (D) and `397a80de`
  (DEC-778), the ticket's widening `b4172c59`, repair `1c80aa97`, CIT-E §11 `6f9bc03a`, lead checkpoint `fc9e6a2a`
  (CP-DAEO-kl5e-0043). A fresh read-only reviewer (role `independent-auditor`, session
  `7c3f4e9d-411e-4f7b-a533-708675d0629a`, 2026-10-18), launched in the owner's form with the reading tools only; code
  under test this worktree's `src/` (DEC-732).
  - What GNU coreutils 9.4 does to a symbolic link at the destination, run for real in a scratch folder: `cp` with
    `-a`, `-r`, `-R`, `-P`, `-d`, `--no-dereference`, `-u`, `-i`, `-l`, `-s`, `--preserve=…`, `--reflink`,
    `--attributes-only`, with FIFO and socket sources and with the link's target having two names; `mv` with
    trailing slashes and `--strip-trailing-slashes`; `cp -a -t` with hard-linked sources.
  - The guard's decision on each form at a protected name (the fixture's acceptance folder; another ticket's folder)
    and in allowed folders, through the kernel's PreToolUse hook (temporary HOME, the suite's fixtures).
  - The read rule (DEC-778): 50 forms of `mv` and `cp -l` of the stand-in settings file of a temporary project and
    its folder, with every value-taking option, abbreviations, `--`, `-t`, `-T`, and reads through a link, for the
    orchestrator and the engineer; 4 controls.
  - 30 ordinary copies, installs and moves; the preconditions (`mkfifo`, `ln` of a second hard name, `ln -s` at a
    protected name); the hook's time; CIT-E §11 against the code and the tests.
  - W2-50: 613 passed; builder tests `test_protected_one_reader.py` and `test_runs.py`: 161 passed; `git status
    --short` empty before and after; real `~/gov-os-runs` ABSENT.
- **What it found.**
  1. **D1, high (reviewer).** `cp -a`/`-r`/`-R`/`-P`/`-d`/`--no-dereference` of a FIFO or socket source onto a link at
     a protected name is allowed and replaces or removes the link (with `-P`, a regular file appears once the FIFO is
     fed). Reproduced.
  2. **D2, high (reviewer).** `cp --preserve=links`, `-a` or `--preserve=all` onto a link whose target has a second
     hard name is allowed and replaces the link with a regular file. Reproduced.
  3. **D3, medium.** `cp -a -t <protected folder>` with two hard-linked sources whose names there are links is allowed
     and replaces the second link. Reproduced.
  4. **D4, medium.** `mv --strip-trailing-slashes <link>/` (or `<link>//`, `--str`) is allowed and moves the link out
     of a protected folder. Reproduced.
  5. **§11 overclaims:** "any other form … whose write replaces the link" and "a link moved away is judged" do not
     hold for D1 to D4; its "What stays open" does not name them.
  6. **R1, outside this round (present before it).** As the orchestrator, `cp -b`/`mv -b`/`install -b`
     (`-S`, `--backup=numbered`) onto the settings file is allowed and leaves the original under the backup's name,
     which is then readable: the read rule does not count the backup as a second name (it does for `sed -i`,
     DEC-553).
  - Not a finding: a hard link to the settings file made beforehand is not seen, but making one needs `ln`, `link` or
    `cp -l` of the file, all refused as reads.
- **Sorting under DEC-779 (the lead).**
  - D1 to D4: each needs **a symbolic link already at the protected name**. No session can create one through the
    guard (`ln -s` into the acceptance folder or another ticket's folder is refused, as the reviewer tested; `cp`,
    `install` and `mv` onto those names are judged at the protected name). At another ticket's folder only an
    unsandboxed session reaches them; in a sandboxed worker's own worktree they need that precondition. So each is
    **a list row, not a round**. D2's second hard name can be made through the guard, but its link at the protected
    name cannot.
  - §11's overclaim goes with the D1–D4 row.
  - R1: reachable **only by an unsandboxed session** (the orchestrator, the one role that may write the settings
    file; the engineer is refused by the write rule). **A list row.**
- **Found sound.**
  - Every form §11 lists is refused as doubt; the acceptance cases pass.
  - DEC-778: all 50 read forms refused with the read reason, for both roles; controls allowed.
  - No ordinary call refused (30 tried); calls decided in about 0.2 s; the hook's deadline fails closed.
- **Judgement.** **fail** (reviewer): D1 to D4 let a role write at a protected name through forms DEC-774 covers,
  given a pre-existing link there. Under DEC-779 every finding is a row; no further round; the draft stays
  uncommitted and the owner rules on it at the close.
