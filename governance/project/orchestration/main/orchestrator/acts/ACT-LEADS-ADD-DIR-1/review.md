# ACT-LEADS-ADD-DIR-1: the ACT review, round 2

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session. I am not the ACT's author, and I did not write round 1. This is a short round 2 under DEC-802. It covers only round 1's blockers F1 and F2 and whatever the rebuild touched.
- **The reviewer brief.** My Read of the operator's fixed reviewer brief was refused once (quiet hours, DEC-991). I did not retry it and did not read it another way. I hashed it only: sha256 `e86703304144…`, the same value round 1 records. I used round 1's record form and its reading of brief checks 1 and 3.
- **One probe refused.** The planted run of check 1 under /tmp/claude-1000/ was refused once (quiet hours). I did not retry it or run it another way. Instead I read check 1 against the after and before files, and I cite the rehearsal's own runs of check 1 (below).
- I ran these operator functions as tools, read-only, on the bundle: `validate_manifest`, `check_act`, `path_rule`, `live_path_refs` (from `operator_run.py`) and `act_class.py`. Nothing was written in any tree.
- Manifest sha256: `1781a70844291708a1ffa7751391f0c8cbb2e29b917afe927ef4db8e40f5c162`. Class claimed b. Class found **b**.
- Reviewed at live HEAD `829282dbd530`. The rehearsal ran on a clone at that same commit. The live launcher is still the frozen before (`023623ac6ac8`), and the main tree is clean.
- **This record must be copied byte for byte** to `acts/ACT-LEADS-ADD-DIR-1/review.md` for the operator's G4. The guard refuses my writes under `acts/`.

task: ACT-LEADS-ADD-DIR-1
decisions: DEC-1161, DEC-313, DEC-1157, DEC-953, DEC-991, DEC-801, DEC-802, DEC-808, DEC-1010, DEC-1014, DEC-136

## What was probed and found sound
- **F1 is resolved.**
  - `path_rule` passes on the bundle (returns None).
  - `live_path_refs` returns None for apply.sh and for each of the five checks.
  - Check 1 now matches the home part of the `TESTS=` and `RUNS=` lines with the pattern `/home/<name>/`, anchored to the whole line. Everything else in check 1 is as before:
    - exactly two `--add-dir` in the code, both on the exec line;
    - the literal pair placed just before the template flag;
    - the order register, then the one `mkdir "$TESTS"`, then exec;
    - `GOV_ROLE` orchestrator on the exec line;
    - no pgrep, pkill, `mkdir -p` or rm.
  - The after file's lines 41 and 42 match the pattern. The before file has no `--add-dir`, so check 1 fails on it.
  - The rehearsal shows check 1 at exit 1 on the before launcher (sections B and D) and exit 0 on the after launcher (sections C and E). It also shows exit 1 on a planted wrong RUNS line (E2) and a planted wrong TESTS line (E3), and the launcher back to the frozen after (E4).
  - The rehearsal ran the manifest's checks exactly as written: `drafts/leads-add-dir/checks.json` equals the manifest's five check commands (compared).
  - The only thing the pattern gives up is the user name in the home path.
- **Dropping check 5 loses nothing that the bundle's file needs.**
  - Check 5 read the CTO's scratch `launch_worker.sh`. That file is not in `touched`, so the apply cannot change it. It is also untracked, so a clone of the repository cannot check it.
  - It still carries no `--add-dir` (read now: 0 occurrences).
  - The guarantee that workers stay walled is still checked: check 4 asserts that `gov launch` refuses `--add-dir`, and the package's section 1 states it.
- **F2 is resolved.**
  - The rehearsal log's last non-blank line is `failures: 0`. It matches G3's rule `^failures:\s*(\d+)$` with 0.
  - The log's line before that reads `=== 62 ok, 0 failed`. The log contains no FAIL line.
  - The count agrees with the changes: round 1 had 63. Check 5's four runs are gone (−4) and E2, E3 and E4 were added (+3), which gives 62.
  - The rehearsal's `sha256` equals the log's entry in `files` and the file's real hash.
  - The last line comes from `rehearse.sh` itself (`echo "failures: $fail"`), so the script cannot print 0 when a step failed.
- **Every manifest hash matches the bundle.** That covers all 7 entries in `files`, the `touched` before and after hashes, and `list.txt`. `validate_manifest` and `check_act` pass.
- **Nothing else changed since round 1.**
  - The after launcher (`54345463a67b…`), apply.sh (`5533fda21a8f…`), the companion diff (`e6ff98edf935…`) and the follow-up diff (`36280a9313e6…`) have the hashes in the package's table. They are byte-identical to the drafts that round 1 compared.
  - Their modification times (01:48 to 01:58) are earlier than round 1's review (06:53).
  - Round 1's record does not list these hashes in full. My evidence that they are unchanged is these modification times, the match with the drafts, and the package's table.
  - Only manifest.json and rehearsal.log are new (07:23), and review-round-1.md was added (see F5).
- **The class.** `act_class.py` gives **b**: row `watchers` (`dispatch/**`). The one script hit is `session` (b), from check 2's stub `$T/bin/claude`. This is unchanged from round 1.

## Findings
Classification: 1 new finding (F5): in scope, ordinary work yes, consequence other (fails closed). F1 and F2 are closed. F3 and F4 stay rows as round 1 recorded them. No finding fails open or loses work.

- **F5. The bundle holds round 1's record under a name the manifest does not list, so the operator's G1 refuses the bundle as it stands.**
  - `acts/ACT-LEADS-ADD-DIR-1/review-round-1.md` was added at 06:55, during the rebuild. G1 walks the bundle and exempts only `manifest.json` and `review.md`. Any other file not listed in `files` gets "the bundle holds a file the manifest does not list".
  - I ran G1's walk on the bundle, read-only, and it flags this one file. No other file is unlisted, and no listed file is missing.
  - Earlier ACTs keep a superseded round's record in a sibling folder, for example `ACT-EXAMIN-SETS-1.r1-97d45565/review.md`. The same text already exists at `reviews/act-leads-add-dir-1.md` (compared: identical).
  - Fix, before queueing:
    1. Move `review-round-1.md` out of the bundle, for example to `acts/ACT-LEADS-ADD-DIR-1.r1-b6923ccc/review.md`.
    2. Copy this record to `acts/ACT-LEADS-ADD-DIR-1/review.md`.
  - The fix changes no hashed file, so the manifest stays `1781a708` and so does the yes line. It needs no rebuild and no new round (DEC-802).
  - Ordinary work: yes, because keeping the earlier round's record beside the bundle is a natural step for a builder.
  - Consequence: other (fails closed: G1 refuses and nothing is touched).
  - Reversed by: `acts/ACT-LEADS-ADD-DIR-1/` holding no file outside `files` other than `manifest.json` and `review.md` when the CTO queues it, or G1 shown to accept the bundle as it stands.
- **F3 and F4** are unchanged from round 1 and stay rows for the owner. The rebuild touched neither the companion nor the launch paths.

## Recommendation
The rebuilt manifest `1781a708` passes. F1 and F2 are resolved. The launcher change, apply.sh, the companion and the follow-up are unchanged from round 1's sound reading. Before queueing, do F5's move and copy. Then give the owner `yes ACT-LEADS-ADD-DIR-1 1781a708`. Round 1's sequencing stands:
- land the companion by route (i) before the apply;
- do step 3 only when the /proc check prints no "NO add-dir" line.

```verdict
{"kpis": [{"kpi": "act-leads-add-dir-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}],
 "manifest_sha256": "1781a70844291708a1ffa7751391f0c8cbb2e29b917afe927ef4db8e40f5c162",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author, not round 1's reviewer",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T07:27:06+00:00",
 "replay_refused": ["planted run of check 1 under /tmp/claude-1000/ (quiet hours, DEC-991; not retried)"]}
```

F1 and F2 are listed as closed (resolved in manifest 1781a708).
