
## W1-40: the hooks and the CI job (DEC-489, DEC-494, DEC-497; 2026-10-07)

Merged from `w1/W1-40` (74 cases; `src/gov/ci` 175 lines against an estimate of 80, the rest the evidence
record, the CI gate and the decided install and "unmeasured" behaviour). `lefthook.yml` runs
`gov ci checks G1 G2` and `gov ci staged-secrets` before a commit and `gov ci push <remote>` before a push;
the push hook runs the declared G3 checks and leaves the evidence record, a JSON git note on the head commit
under `refs/notes/gov-evidence`. `.github/workflows/ci.yml` installs the `gov` package from the checkout and
gitleaks from the registry's archive, verified against the registry's checksum before it is unpacked, then
runs `gov ci job`, gitleaks, the tests and `gov ci record`; every step runs after a failed one. The two root
files are byte-identical copies of their templates. **No hook is installed:** `~/.local/bin/lefthook install`
is the owner's step at the Wave 1 exit, once the baseline is empty. The suite's README lists the residuals
as R-1 to R-21; the ones that matter outside the suite:

- **This repository's CI job is red with "unmeasured"** until the owner approves pytest, openspec and
  rulesync for the hosted runner (DEC-497). Once pytest is there, `python3 -m pytest tests` runs every
  acceptance suite of this repository (over an hour, needing tools the runner lacks).
- **The runner is a simulation.** The real checkout, the runner image, the network, the real download and
  its checksum, `python3 -m pip install .` on the runner's system Python, `gov` on PATH after it, PyYAML for
  the gitleaks step, and whether the host accepts the pushed notes ref are all seen for the first time on
  the owner's first push. A failure there is red, never falsely green.
- **Bypasses by design of git and lefthook:** a commit without lefthook on PATH passes (the generated hook
  exits 0); `--no-verify` and `LEFTHOOK=0` skip the hooks. A bypassed push has no record, so CI is red;
  nothing holds against a bypassed commit until the push.
- **The evidence record can be written by hand** (DEC-489), also one that says "no G3 check declared" for a
  project that declares G3 checks; comparing the note with the checkout's declarations is a cheap Wave 2
  addition. Removing a project's G3 declarations turns the gate into a report (DEC-497). The record is bound
  to the head commit while G3 runs on the working tree.
- **Left as built by DEC-497 (Wave 2 list):** the notes ref with several clones (never forced; fetch and
  merge before writing); `gov ci` declares the class "read" though `push` writes a note; the skill-version
  check reads a missing parent commit as green (`src/gov/check/runner.py`, W1-26's code) and only the last
  commit of a push is compared; tier selection calls the check runner's internals (`gov check` has no tier
  option).
- **What passes as yellow in the job:** a warning-severity or not-applicable check whose tool is absent
  (only the finding codes `OPENSPEC_ABSENT` and `RULESYNC_ABSENT` are known as "tool absent"); openspec with
  nothing to validate; a failing warning-severity check; a family with no check; a missing or malformed
  path map yields no policy result at all.
- **gitleaks in CI** scans only the two commits of the checkout; earlier commits of a multi-commit push are
  not scanned there. The install trusts the registry of the pushed commit, and the unpacked binary's version
  is not compared with the registry's. A product project needs a registry with the `archive` fields or the
  step fails. The second, strict gitleaks scan of the pre-commit hook against the canary fixtures is for the
  exit package (DEC-489).
- **The word "unmeasured"** is held for pytest, openspec and rulesync only; a missing `gov` or gitleaks fails
  with "command not found", and the hooks do not use the word.
- **The adapter comparison has no step of its own** (DEC-497); with a stand-in rulesync the case is green:
  what the real rulesync generates is W1-38's.
- **The guard refuses to create the folder of an allowed file** (`mkdir -p .github/workflows` by the
  engineer); the file was produced by `install -D` and `cp` (accepted, DEC-497). The Write tool refuses
  `lefthook.yml` by its name (DEC-489).
- **Not derived:** S0a-G-11 (not in the readable tree).
- **One W1-16 case** (the one that watches `.gov-runtime` for new files) failed once in the lead's full run
  on files of the lead's own wait calls, and passed alone.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** two, both for DEC-497,
  with their `Rewrite-Reason:` trailer (`54829432`).
