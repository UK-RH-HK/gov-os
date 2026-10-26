You are the ticket lead for ticket `DAEO-cy5o` (`W2-57`, "Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `d54546f00b21`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read first:
- the ticket file (`.tickets/DAEO-cy5o.md`): its KPIs, and in its body the test designer's files (MR-3);
- its card in `docs/plan/WAVE_2_WBS.md` §2;
- lens I's synthesis `docs/assessment/2026-10/I-SYNTHESIS.md` (P-IS-6, both tables) and the I4 report's F2;
- DEC-892 item 2, DEC-889 item 5, DEC-899 item 3, DEC-915 and DEC-922.

## Why you start now

- **The first re-pin is done** (DEC-922, 2026-10-26). The owner gave W2-57 the first free slot after it (DEC-915 item 3).
- **The rulesync probe is a live fail-open (I4 F2).** Under load, the portability check's rulesync calls hit their 10-second limit. W1-38's session fixture then reads the timeout as "rulesync is not installed" and skips up to 181 cases, and the close still passes.
- **Until you land,** the orchestrator's interim skip guard stops the close queue on that skip whenever `rulesync --version` answers. rulesync answers on this machine (24.0.0).
- **The serial phase** takes about 31 minutes of every close. Most refused closes since 2026-10-20 came from listed cases or load-caused reds.

## The decisions for this run

- **The probe first (DEC-892 item 2),** with its four effects:
  1. a limit a loaded machine meets, measured under the close's parallel load;
  2. W1-38's fixture fails, never skips, on a timeout (a timeout is not "not installed");
  3. the 9 cases whose "not green" a timeout satisfies assert the reason;
  4. W1-33's research case fails the same way.
- **Then the rest of the KPIs, in one round,** with up to two reviews (DEC-916: this is the only round; its plan is this brief).
- **Tests first,** by a fresh independent test designer. Launch it sandboxed, `--effort xhigh` (a FULL ticket's test designer, DEC-839), and its brief must not set `TMPDIR`.
  - It writes `tests/acceptance/W2-57/`, and revises only the files the ticket body names for it: `serial-only.txt`, W1-30's r11 and r13 files, `W1-38/**`, W1-33's `w1_33_support.py`, `W1-07/**`, `W1-46/**`, `W1-50/**`, `W1-02/**`.
  - Each revision carries a `Rewrite-Reason:`, and no expectation is lowered.
  - **W1-30's `README.md`** is also changed on `w2/W2-67` (built, not merged). Change it only where r11 or r13 is described; a conflict is resolved at merge.
- **Live and real-model files leave the close for the nightly (DEC-889 item 5).** The close's selection must still collect them; they only stop running in the close.
  - Do not edit `governance/project/test-map.yaml`. If the route out needs an entry there, name it exactly in your return, and the orchestrator commits it.
- **W1-09's two race cases** move to the parallel phase only after one green nightly in parallel. Return that as a condition with the entry ready; do not move them in this run.
- **KPI 8, the `load_sensitive` removals,** is the orchestrator's commit (DEC-861; the list only shrinks). Return the exact list of entries your work makes unnecessary, each with its evidence. Never edit the path map.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in the ticket's `allowed_paths`.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **Known:** W1-19's warm-query case is on `load_sensitive`. W2-54's green-here case may time out under load (row W2-L429; re-run it alone).
  - **The probe's own proof:** run W1-38's suite three times in the close's parallel form and show 0 rulesync skips and 0 timeouts each time (the KPI's three closes' worth).
  - Any other red is named with its cause.
- **Reviews:** a fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head. Commit the probe record only when it passes.

## This run's order

1. Tests first (the test designer), then **check red yourself.**
2. The engineer: the probe first, then the doctor probes, the serial list and the gate.
3. Rebuild and verify in full, plus the three W1-38 runs.
4. Review 1. If it fails on a fail-open or lose-work finding an honest agent can hit: one test-design batch, one engineer, a full run, review 2 (the last).
5. **Return** DONE (probe passed), or PACKAGES. Include the `load_sensitive` removals, any test-map entry, and the W1-09 condition, each ready for the orchestrator.

**Estimate:** about 250 lines, about 8 to 10 hours with the full runs and one review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit). Split the engineer's work into batches if needed (the probe; then the rest).

---
