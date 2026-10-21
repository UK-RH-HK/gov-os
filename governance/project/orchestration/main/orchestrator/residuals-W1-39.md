
## W1-39: the Copier template and the framework lock (DEC-488, DEC-493, DEC-499; 2026-10-07)

Merged from `w1/W1-39` (67 cases; 218 source lines added against an estimate of 100, about 40 of them the
update procedure's text in the lock header and in `copier.yml`). `gov.lock.compare(root)` answers `MATCH`,
`DRIFT`, `UNLOCKED` (an answers file and no lock), `MISSING` (neither) or `ERROR`; `gov doctor` reports
`MATCH` as passed, `MISSING` as unmeasured and every other answer as failed. `python3 -m gov.lock` writes
`governance/framework.lock` as the one Copier task. Copier was never pointed at this repository.

- `gov check` on the branch before the merge (`log/check-at-W1-39-premerge.json`): no red outside the
  baseline, and the two baseline checks with a recorded count are unchanged (43 and 735).
- **A project can still silence the comparison (DEC-499):** deleting both the lock and the answers file gives
  "unmeasured" and exit code 0; editing the lock's manifest together with a kernel file gives a match. The
  lock is unsigned until Wave 3 (CAP-02.c). Tag and commit are compared with the answers file only, and the
  project can edit both.
- **What the comparison does not look at:** anything inside a `__pycache__/` folder under the kernel
  (DEC-488); anything outside `governance/kernel/` (the generated `.claude/`, the overlay, `.rulesync/`);
  a file's mode (a hook that loses its executable bit is a match); an added empty folder. One listed kernel
  file that was hashed is enough for a match to be possible.
- **A manifest key that is no valid path** raises a traceback (not a false match).
- **The lock task needs the `python3` on PATH to import `gov`:** where `gov` is installed as an isolated
  tool the copy fails at the task. A `gov lock` subcommand is decided with W1-41 (DEC-499).
- **The shipped path map is not valid against the kernel's path-map schema** (namespaces only, no systems):
  a fresh project is at MINIMAL by it; W1-41's adoption settles validity (DEC-499).
- **Declared check commands still name `template/…` paths** that an installed project does not have: for
  W1-41.
- **Adapter generation is a documented step, not run at the copy** (DEC-488); the cases hold only that the
  procedure names rulesync. Which `.rulesync/` paths are the project's own is in no source (ADR-0002 §5).
- **`gov doctor` on a fresh project:** tools, hooks, index, canaries and isolation are unmeasured (W1-40,
  W1-41, the exit run). The Claude Code part reads the machine's real CLI whatever `HOME` says.
- **Not derived:** G-14 and S0a-G-15 (their text is not in the readable tree). "Nothing else is shipped in
  the overlay" is the brief's reading of DEC-493.
- **Loose case:** `test_a_kernel_folder_that_cannot_be_listed_is_not_passed_over` accepts any of several
  reason words. **No case:** an answers file that cannot be read as a map, with no lock.
- **The writer blocks on a FIFO under the kernel;** the comparison reports it as drift without reading it.
- **W1-19's warm-query latency case** failed twice in the lead's runs at a load average near 20 and passed
  alone; W1-19 passed whole in the orchestrator's run (41 passed).
- **Found only after the merge (2026-10-08):** W1-40 added `lefthook.yml` and the CI workflow to the template,
  and the template's path map did not class them, so `gov doctor` failed on a freshly created project: five
  cases red on the integration branch at `855c0e08`, each branch green alone. Fixed on the ticket's branch
  (`36abb70d`: `lefthook.yml` in the `repository` namespace, `.github/**` in a new `ci` namespace) and
  merged again. **A project installed before this fix does not get it by update:** `governance/project/**`
  is never overwritten, so its path map needs the two entries by hand. No check holds "every file the
  template ships is classed by the path map it ships" outside W1-39's own cases.
- **The regression summary's last line was the plan validator's,** not a verdict on the suites; the
  orchestrator reads every suite's line (script corrected).
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** one
  (`test_a_missing_lock_is_not_a_match`, strengthened by DEC-499, with its `Rewrite-Reason:` trailer).
