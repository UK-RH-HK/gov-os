# Review r1: ACT-DISPATCH-1 and ACT-IDLE-GUARD-2 (independent auditor, DAEO-8s85, 2026-11-12)

Decisions: DEC-1140, DEC-1118, DEC-1052, DEC-1110, DEC-1104, DEC-1010, DEC-801, DEC-808.
Classification: F1 blocks (in scope, ordinary work, fails open); F2-F5 are rows.

## ACT-DISPATCH-1 (manifest a20754dd1e9f…): pass
- **Hashes:** every hash matches; `before/` is `w2/integrate` 0206c0f7c691; `launch_now.sh` is untouched.
- **Red then green in my clone:** new test files on the old code 13 failed, 208 passed; the whole folder 490 passed, 6 skipped, 95 deselected; old test files on the new code 203 passed.
- **Manifest checks:** all five pass as written, with counts 4, 5 and 4.
- **Dry tick in planted folders:** the cap refuses the sixth line ("lead cap: 5 of 5 running"); idle items 1, 1, 1, 1, 2 (the second is the 7-hour reminder); the forecast admits at 8.0 of 18. The old dispatcher starts a sixth lead, gives 1, 1, 1, 2, 3 items, and refuses at 22.7 of 18.
- **C3:** memory admission unchanged (RAM and GPU terms, 3 GiB floor, oom_watch raising it, fail-closed). The real-CPU admission and the cap still bind. The discount needs at least 5 minutes in one phase. A burst stays inside its slot's CPU set, so over-booking is at worst a slowdown.
- **Class:** (O) with its tests, (b) for code only. The route is right.
- **Rows:**
  - F2: the 6-hour reminder departs from the letter of DEC-1140 (1)(a); the owner should confirm it.
  - F3: section 8 says `mem_guard.py` stops starts; it does not.
  - F4: out of scope; the RAM term prices running jobs at their current phase only.
  - F5: the `floor` name is reused in `balancer.forecast`.

## ACT-IDLE-GUARD-2 (manifest 531d98c006de…): fail
- **Hashes:** every hash matches.
- **Red then green:** the new test file on the old hook 9 failed, 44 passed; with the new code it passes within the whole-folder run.
- **Manifest checks:** all three pass as written.
- **F1 and F3:** done as the review asked. 8 s at the worst against `timeout: 10`, and the hook never fails the session.
- **F1 (blocks):**
  - What happens: `git for-each-ref --merged w2/integrate` also lists a just-claimed ticket's fresh branch, which has no commits of its own. The plan arm then logs that ticket as "merged, to close (not launchable)" and stops naming it. W2-115 is in this state today; the old hook named it.
  - Ordinary work: yes. Consequence: fails open.
  - Fix: leave out only branches whose tip is off integrate's first-parent line, or name merged tickets instead of leaving them out. Add a test for a branch with no commits of its own.
  - What would reverse it: evidence that ticket branches always have a commit of their own before they appear in the plan's first batch.
- **Next:** rebuild with the fix and a new manifest and yes line. Review r2 is the last round.

## The reviewer's verdict block (as returned; READY computed by verdict.py per KPI: act-dispatch-1 READY, act-idle-guard-2 not READY on F1)

```verdict
{"kpis": [{"kpi": "act-dispatch-1", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "act-idle-guard-2", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
