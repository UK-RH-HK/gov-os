# Round 1

**Outcome: pass.** I found nothing that should stop the ACT. All six checks pass and the class is **(b)**. My three findings are all out of scope and none blocks.

**Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-STANDBY-1/`. It contains `manifest.json`, `apply.sh`, `list.txt`, `rehearsal.log` and the `before/` and `after/` copies of `governance/project/orchestration/tools/deadman.py`. Package: `governance/project/orchestration/packages/ACT-DEADMAN-STANDBY-1.md`.

- **Manifest sha256, recomputed:** `824cfc1613cf6d0f2c3f48b09407ff8931dd1896022049a9a37184dad48a7c8d`. It matches the package and the yes line.
- **Brief sha256, recomputed from `~/gov-os-operator/install/reviewer-brief.md`:** `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`. It matches `install/APPROVED` line 10.
- **Bundle file hashes:** all five files hash as the manifest states. The live `deadman.py` is still the before copy (`5d770bfb…`).

## What I did
- **My own rehearsal:** I re-ran the bundle in a throwaway `--no-hardlinks` clone under `/tmp`, at `c9742b08910a`, the same commit the rehearsal log names. I used a copy of the bundle, a planted empty HOME and `env -i`. The results:
  - `check` 0, `verify` 3, `apply` 0, `verify` 0.
  - The file mode stays 644. `git status` shows only ` M …/deadman.py`.
  - All six manifest checks gave the exit codes and counts the manifest states (1, 1, 1, 1; exit 0 with HEARTBEAT standby; exit 10 with the ALERT ending "its stand-by note had expired (…)").
  - `undo` 0, and the file is back to `5d770bfb…` byte for byte. `check` gives 0 again.
- **Nothing outside the clone changed:** the live `deadman.py` and `crontab -l` hashes were the same before and after. Nothing was written to the planted HOME. The throwaway folder has been removed.
- **The diff:** it changes only one rule. Before, the dead-man was muted whenever the note file existed. Now it is muted only if the note is under the age limit, read from a leading UTC time or else the file's mtime. Every case muted after the change was also muted before, so the change only tightens the control.
- **Edge-case probes** of `standby_state`, run with TZ=America/New_York:
  - A fresh note, the `T…Z` form and up to 5 minutes of clock skew all mute.
  - A stale leading time expires even when the mtime is fresh.
  - A future year with a fresh mtime falls back to the mtime. A future year with a future mtime expires ("ahead of the clock").
  - An invalid date or a time without seconds falls back to the mtime.
  - Exactly 2 hours old expires. `--standby-max-s 0` and negative values expire.
  - A missing file returns `None`.
  - Nothing I tried mutes for good.
- **Tests on the applied file:**
  - The proposed `test_cto_safety_nets.py` (`09c11e4bc3e9`): 15 passed.
  - The committed tests that touch deadman, the dispatcher, the stop hooks and the operator (W2-148 units, W2-66): 375 passed, 3 skipped, 1 failed. That failure is pre-existing (F2).
  - The wake's draft tests, which the author did not run: 10 of 11 passed (F1).

## Findings
- **F1 (out of scope; ordinary work: no; consequence: other).** One draft wake test, `test_no_wake_with_dry_or_in_a_standby` in `drafts/deadman-wake/test_deadman_wake.py`, fails on the applied file. It passes 11/11 on the before.
  - Cause: the test writes an untimed note, so its mtime is the real time, then runs with `--now 2026-11-10 04:00`. The new rule correctly reads that note as dated ahead of the clock and expires it.
  - This is a fault in the test, not the ACT. That file is not committed. Before it is committed, it should write a timed note, or set the note's mtime to the simulated clock.
- **F2 (out of scope; ordinary work: no; consequence: other).** `tests/unit/operator/test_w2_148_round2.py::test_the_default_notice_goes_through_the_three_channels` fails with the before and the after file alike. It is unrelated to this ACT.
- **F3 (out of scope; ordinary work: yes; consequence: other).** The stand-by habit, as recorded today, doesn't say to write a leading UTC time. Two effects until the prompt line in package §6 lands:
  - A note with no time is aged by its mtime. That still expires correctly.
  - A note whose old leading time is kept, for example when a line is appended, expires even though the CTO renewed it. That fails toward the alert, as the package intends, but it can cause a push the CTO didn't expect.

## KPI notes
1. **Touched list and path rule: pass.** One file is touched, with its before and after hashes listed. `apply.sh` works only from `$PWD` and its own folder. The checks use relative paths, `mktemp` and `$T` alone. Nothing names the live repository or the real HOME, and nothing `cd`s to either. HOME and crontab were unchanged.
2. **Undo: pass.** It restores the file byte for byte, in the rehearsal log and in my re-run.
3. **Rehearsal: pass.** The log matches what `rehearse.sh` prints, from a clone at the live HEAD, and ends `failures: 0`. My re-run reproduces it.
4. **Checks: pass.** All six reproduce exactly from the repository root.
5. **Class: (b).** The `watchers` row covers `deadman.py` (b, a control path). The change tightens the dead-man, but it alters a watcher of the CTO, so it stays (b) as the ACT claims.
6. **Guard replay: not applicable.** There is no path-map or deny-list change.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass",
           "findings": [{"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "other"},
                        {"id": "F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
          {"kpi": "4", "verdict": "pass", "findings": []},
          {"kpi": "5", "verdict": "pass",
           "findings": [{"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "824cfc1613cf6d0f2c3f48b09407ff8931dd1896022049a9a37184dad48a7c8d",
 "class": "b",
 "reviewer": "act-reviewer-round1 (session 63e8ed6c-76cf-44b4-95fe-9612cc0248e0)",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-10T21:01:00+00:00",
 "replay_refused": []}
```