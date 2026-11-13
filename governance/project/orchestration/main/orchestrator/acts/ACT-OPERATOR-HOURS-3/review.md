# ACT-OPERATOR-HOURS-3: the ACT review

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session; not the ACT's author (the manifest's author is "cto"; the bundle was built by a CTO helper). Worked under the CTO's review brief and `governance/project/briefs/JUDGEMENT.md`. A Read of the operator's fixed reviewer brief was refused once (quiet hours) and not retried; an earlier `grep` of that file gave the verdict fields it asks for.
- Manifest sha256: `716da9dc5c4dd4c64b5d03f92a9696a35b3f119d2ff1f20e004565005b665ccc`. Class claimed O (Part A b, Part B O); class found **O** (Part A b: `crontab` row, control; Part B O: `operator-own`, the catch-all `unknown`, path-map ratchet).
- Reviewed at live HEAD `23c6bb45456f`. The four paths and the path map are unchanged since the build (`805bd918`), the live install is the before (`123e17e55811`, `1e557c49be58`) and the live crontab is the before (`88cf08b165a1`).

task: ACT-OPERATOR-HOURS-3
decisions: DEC-1157, DEC-1141, DEC-1104, DEC-1136, DEC-1159, DEC-1057, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-430, DEC-491, DEC-136

## What was probed and found sound
- **Part A.** The live crontab equals `before/`. The after differs in line 7 only: the window, the state-file read and the comment. The launcher command and the log redirect are byte-identical. The table is installed by standard input (case 19 shows the file-argument form refusing a long path). The six manifest checks are consistent with the after table.
- **Part B code.** Only G9's two time holds go: the constants, the two settings, the reader and the window branch. The unreadable clock, the explicit `nightly_window`, NIGHTLY-RUNNING, CLOSE-RUNNING, the CTO's `act-in-progress.txt` and the operator's freeze are unchanged. The install copy equals the repository's after file. `APPROVED` changes in the `opcommon.py` line only, to c7ec467c…. No other code reads the removed names.
- **Tests.** In a clone at 23c6bb454 with the four after files, `tests/unit/operator` plus `tests/acceptance/W2-148` gave 654 passed, 0 failed (heavy slot, TMPDIR outside the repository and `~/gov-os-runs`). The rehearsal shows the revised unit file red on the old code (145 failed) and the old unit file red on the new code (38 failed). W1-01 in the rehearsal: green, then red with one failure naming only the first commit, then green.
- **apply.sh.** Each part refuses on a moved file (exit 3) or a tampered frozen copy (exit 4). Part B also refuses while busy (exit 6) and holds the launcher's own `flock` on `launch.lock`. Writes go temp file then rename, `APPROVED` last, followed by the install's own check. `B exempt` run in a clone at today's head: exactly 2 lines added, and `exempt-verify` exited 0 before and after the second commit. All 18 manifest file hashes match.
- **Order.** Each part alone is safe. A alone: G9 still holds, the result is "held", the request stays queued and no notice is sent. B alone: cron still skips 02:10 to 07:59.

## Findings
Classification: 6 findings, 0 blocking. F1, F2 and F6 are in scope, ordinary work, consequence other. F3 is in scope, not ordinary work, other. F4 and F5 are out of scope, ordinary work, other.

- **F1. The package was stale against the bundle** (the yes line printed 53adcbf2; the manifest is 716da9dc; the log has 127 cases, 0 failures, with parts 6 and W1-01 run). Ordinary work: yes. Consequence: other. Reversed by: a package revision printing 716da9dc. (The CTO corrected the package's yes line to 716da9dc on 2026-11-13 ~02:30.)
- **F2. The nightly start gap is wider than stated.** `nightly.sh` writes NIGHTLY-RUNNING only after its own wait loop; a launcher session can pass G9 during that wait, and G9 is not read again before the commit. The nightly runs in its own clone, and landings already run beside it (DEC-1159 (1)). Closing it is a further (O) change (a start marker or margin in G9). Ordinary work: yes. Consequence: other. Reversed by: an ACT kind shown to corrupt a nightly run it overlaps.
- **F3. The tests were revised by the builder, not an independent test designer**; the printed commit has `Role: owner` and no `Rewrite-Reason:` trailer (the ACT-OPERATOR-HOURS-2 precedent, its F4). Adding `Rewrite-Reason: DEC-1157 (2)` is harmless. Ordinary work: no. Consequence: other. Reversed by: a rule barring owner-committed acceptance edits.
- **F4. Notices at night.** P1 pushes and the "applied" notice can now fire from 02:10 to 07:59; `notify` has no hour rule. Ordinary work: yes. Consequence: other. Reversed by: an hour rule found on the push channel.
- **F5. The operator now applies beside the leads and lands all night.** Coordination is the CTO's `log/act-in-progress.txt` during every land, plus the operator's freeze. Ordinary work: yes. Consequence: other. Reversed by: a land path that commits without that file and is shown to interleave with an operator commit.
- **F6. Applying Part A first at night can block Part B** (a queued request held by the old G9 makes `B check` exit 6 until 08:00); the package's suggested order (B first) avoids this. Ordinary work: yes. Consequence: other. Reversed by: `B check` shown to ignore a held request.

## Recommendation
Take it to the owner with the 716da9dc yes line. F2, F4 and F5 are the owner's risks to accept. No new round (DEC-802).

```verdict
{"kpis": [{"kpi": "act-operator-hours-3", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}],
 "manifest_sha256": "716da9dc5c4dd4c64b5d03f92a9696a35b3f119d2ff1f20e004565005b665ccc",
 "class": "O",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T02:08:37+00:00",
 "replay_refused": []}
```
