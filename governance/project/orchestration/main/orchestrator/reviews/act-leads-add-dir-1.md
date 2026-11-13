# ACT-LEADS-ADD-DIR-1: the ACT review

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session. I am not the ACT's author: the manifest's author is "cto" and a CTO helper built the bundle. I worked under the operator's fixed reviewer brief, read through a shell (sha256 `e86703304144…`, the hash `APPROVED` lists), and under `governance/project/briefs/JUDGEMENT.md`.
- A Read of the operator's `act_class.py` was refused once (quiet hours). I did not retry it and did not read the file another way. I ran the operator's own `act_class.py`, `validate_manifest`, `live_path_refs` and `path_rule` from the install as tools.
- The guard refused this record's write at `acts/ACT-LEADS-ADD-DIR-1/review.md` (DEC-953 item 2: a reviewer writes only under `reviews/`), so it is written here. **The CTO copies it, byte for byte, to `acts/ACT-LEADS-ADD-DIR-1/review.md`** for the operator's G4.
- Manifest sha256: `b6923ccc5e793fadd60372984f2c291d526481945211b2d9b25ed4863873715f`. Class claimed b. Class found **b**.
- Reviewed at live HEAD `94132594a02a`. The bundle was built at `23c6bb45456f`. The live launcher is still the frozen before (`023623ac6ac8`).

task: ACT-LEADS-ADD-DIR-1
decisions: DEC-1161, DEC-313, DEC-1157, DEC-1104, DEC-1156, DEC-751, DEC-953, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-136

## What was probed and found sound
- **The touched list and the hashes.** The manifest's 7 file hashes all match the bundle. `list.txt` agrees with `touched`. The drafts' `launch_now.sh` is byte-identical to `after/`. The drafts' companion diff is identical to the bundle's. The change is what the package's section 2 says: 12 lines added, nothing removed, and every other argument on the exec line is unchanged.
- **apply.sh, run in a planted copy under /tmp/claude-1000/ with HOME planted:**
  - check before exited 0; verify before exited 3.
  - apply wrote the after copy byte for byte and kept mode 755. It left no temp file and wrote nothing else.
  - A second apply did nothing (exit 0). verify then exited 0.
  - undo restored the before copy byte for byte. A second undo did nothing.
  - A launcher changed since the freeze: apply, undo and check each exited 3, file untouched.
  - A moved (missing) launcher: exit 3.
  - A tampered frozen after copy: apply exited 4, untouched. A tampered frozen before copy: undo exited 4, untouched.
  - A link at the launcher's path: exit 3.
  - The planted HOME stayed empty.
  - apply.sh reaches the bundle through its own folder, acts only on `$PWD/<path>`, names no live path and has no `cd` to the repository or HOME. The operator's `live_path_refs` returns None for apply.sh.
- **The companion and the follow-up**, run in a clean detached worktree of `w2/integrate` at `94132594a`. Each pytest ran through heavy_slot.sh with `-p no:cacheprovider -q`, `PYTHONPATH` set to the worktree's src, and TMPDIR under /tmp/claude-1000. The worktree was removed afterwards.

  | Launcher | Test change | Result |
  |---|---|---|
  | old | none | 30 passed |
  | new | none | 2 failed: exactly the two W2-153 tests the package names |
  | new | companion | 223 passed, 3 skipped (all three files) |
  | old | companion | 30 passed |
  | old | companion + follow-up | 2 failed: the two new tests |
  | new | companion + follow-up | 225 passed, 3 skipped |

  On the applied worktree, all six manifest checks exited 0, as listed. This agrees with the rehearsal's sections B to F.
- **The class.** The operator's `act_class.py` on the bundle gives **b**: row `watchers` (`dispatch/**`, control). The one script hit is `session` (b), from check 2's stub `$T/bin/claude`. There is no sudo, push, tag, rm or install. The class rows and the hits agree.
- **Workers stay walled (DEC-313).** `gov launch` still refuses `--add-dir` (check 4). `launch_worker.sh` carries none. The new line is only on the dispatcher's lead exec, which has `GOV_ROLE` orchestrator.
- **The runs root.** Nothing is made in the runs root (check 2), so DEC-751's marked own folder stays gov launch's. The empty `<W2>-tests` folder is made only after the gate and the registration, and a shut gate makes nothing. The scratch scanners I read (dispatcher, interim_watch, tripwire, rebuild_counts, store_survey) skip or tolerate an empty non-git folder.
- **Step 3's commands.**
  - The main checkout's `settings.local.json` round-trips byte for byte through `json.dumps(indent=2)` plus a newline (checked). Mode 644 equals the umask's result, so only `additionalDirectories` changes.
  - It now holds `['/home/usain/gov-os-runs', '/home/usain/gov-os-worktrees']`. With the ACT and step 3, a dispatcher lead goes from all worktrees to its own `-tests` tree, so the set is narrower.
  - The package's /proc check, run read-only now, lists one lead: W2-88, pid 2770203, "NO add-dir". A broad scan finds no other lead process.

## Findings
Classification: 4 findings. None is blocking under JUDGEMENT (none fails open or loses work). F1 and F2 fail reviewer-brief checks 1 and 3, and under the brief a failed check refuses an ACT. F1 and F2 are in scope, ordinary work, consequence other. F3 is in scope, not ordinary work, other. F4 is out of scope, ordinary work, other.

- **F1. Two manifest checks name live paths, so the operator refuses the bundle at G1** (reviewer-brief check 1).
  - Check 1 looks for the launcher's two new lines by their literal text, which includes the real HOME (`/home/usain/gov-os-worktrees/…`, `/home/usain/gov-os-runs`).
  - Check 5 greps the CTO's scratch `launch_worker.sh` by the live repository's absolute path.
  - The operator's own `path_rule` refuses: "G1: the path rule: a check breaks it, it names the real HOME's path (/home/usain)". `live_path_refs` flags check 1 for the real HOME and check 5 for the live repository.
  - Both checks are read-only, so no live file would change. But in the operator's clone check 5 reads the live file instead of the clone. In a clone the file does not exist (it is untracked scratch), so a relative form would fail there.
  - Fix: match the home part of the two lines with a pattern (any `/home/<name>/` prefix), and drop check 5 (its point is already in the package's section 1 and in check 4). Then rebuild the manifest. This gives a new yes line.
  - Ordinary work: yes, because the launcher itself hard-codes the home path and an honest builder checks for it literally.
  - Consequence: other (fails closed: G1 refuses and nothing is touched).
  - Reversed by: the operator's `path_rule` returning None for this manifest, or an owner decision that this (b) ACT goes only by the CTO's hand apply, where G1 never runs.
- **F2. The rehearsal log does not end with `failures: 0`** (reviewer-brief check 3).
  - Its last line is `rehearsal exit 0`, after `=== 63 ok, 0 failed`.
  - The brief requires the log to end with `failures: 0`. G3 reads that from the last non-blank line and otherwise refuses (operator_run.py G3, as quoted in ACT-PERMISSIONS-3's review).
  - Every other bundle under `acts/` ends with `failures: 0`.
  - The rehearsal itself is real. It is this apply.sh run in its own clone at `23c6bb454`, and my reproduction above agrees with it.
  - Ordinary work: yes, because the helper's script prints its own summary format.
  - Consequence: other (fails closed at G3).
  - Reversed by: a rebuilt log whose last line is `failures: 0`, or G3 shown to accept this log.
- **F3. The companion edits a closed ticket's acceptance test (W2-153), routed by the CTO rather than written by the independent test designer.**
  - It only relaxes the comparison to ignore the new `--add-dir` pairs. It is green on both launchers (verified).
  - The route is DEC-1156 (7)'s (decided-behaviour test revisions, CTO-routed). It has a precedent in ACT-LOAD-BALANCER-A's companion `792b92923` (a commit on W2-153's branch, merged).
  - If it lands outside that route without an exemption entry, W1-01 turns red (package risk 5).
  - Ordinary work: no, because the route is a deliberate, decided one.
  - Consequence: other.
  - Reversed by: a rule barring CTO-routed revisions of a closed ticket's acceptance tests.
- **F4. Leads started by any other path lose both directories after step 3** (package risk 3).
  - Both launchers (`gov launch orchestrator`, on integrate and on W2-60a) refuse `--add-dir`. The old `launch_when_gate_opens.sh` form carries none.
  - The package's /proc check would also miss a `gov launch` lead. Its `--settings` is written by `json.dumps` with a space after the colon, so the literal `"GOV_ROLE":"orchestrator"` does not match. Such a lead would be listed neither "add-dir" nor "NO add-dir".
  - No such lead runs now (broad scan). Fixing the launchers needs a product ticket (the owner's).
  - Ordinary work: yes, if the CTO starts a lead by gov launch.
  - Consequence: other (its writes to the -tests tree and the runs root are refused, and it stops and returns. Its files stay).
  - Reversed by: a lead path other than the dispatcher in use at the handover. For the check alone: a planted gov-launch lead that the check lists.

Note on risk 1 (not a finding): it assumes the CLI applies the main checkout's `settings.local.json` to a session whose cwd is a linked worktree. W2-88's worktree has no local settings file of its own, and the package's transcript count shows no lead Edit or Write into `-tests` or the runs. I did not verify the premise. If it is false, step 3 cannot affect running leads. If it is true, the /proc check before step 3 is the right control: do step 3 when it prints no "NO add-dir" line (W2-88 is the only one now).

## Recommendation
Do not take `b6923ccc` to the owner. The change, apply.sh, the class, the companion and the follow-up are sound. Rebuild with three changes:
1. check 1 matches the two lines by a pattern for the home part;
2. check 5 is dropped;
3. the rehearsal log ends with `failures: 0`.

Then send it for a short round 2 (a second verdict block), and give the owner `yes ACT-LEADS-ADD-DIR-1 <new 8>`. Land the companion by route (i) before the apply. Do step 3 only when the package's /proc check prints no "NO add-dir" line. F3 and F4 are rows for the owner to accept.

```verdict
{"kpis": [{"kpi": "1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "fail", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "4", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "b6923ccc5e793fadd60372984f2c291d526481945211b2d9b25ed4863873715f",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T06:53:10+00:00",
 "replay_refused": []}
```
