# ACT-W2-148-S15-1: the ACT review

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session; not the ACT's author (the manifest's author is "cto"; the bundle was built by a CTO helper). Worked under the CTO's review brief and `governance/project/briefs/JUDGEMENT.md`. A Read of the operator's fixed reviewer brief was refused once (quiet hours) and not retried; its sha256 below is the installed file's, from a hash listing and `keep.txt`.
- Manifest sha256: `a3df8ff6c3a49f0f6457eaf64e678b4790468540c707fe040448c45ff13356c5`. Class claimed O; class found **O** (three `operator-own` rows, no script hit, under both tables).
- Reviewed at build head `335c8f3c5dd1`; live HEAD moved to `94132594a02a` during the review; `class-rules.yaml` unchanged (`0f130073bbbd`); the live install is base 1's before (`APPROVED` `1e557c49be58`).

task: ACT-W2-148-S15-1
decisions: DEC-1142, DEC-1104, DEC-1057, DEC-1136, DEC-1131, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-136

## What was probed and found sound
- **The table:** the `settings` row loses only its home match line (its `why` drops PUSH-INPUT-1); a new `home-settings` row follows (home `.claude/settings*.json`, `class: b`, `control: true`); 21 rows to 22; nothing else changes. With the operator's own `act_class.py`, the 35 bundles under `acts/` keep their classes (ACT-EFFORT-HIGH-1/2 change row only, b before and after); home settings files go from the deny-list rule to fixed b; the repository's settings, hooks, CLAUDE.md, the pin, the crontab and the operator's files keep their rows.
- **The bundle:** all 18 hashes match the manifest; install and repository after files identical (`38ac2f2decce`); `APPROVED` changes in its class-rules line only, on both bases; the HOURS-3 base's before equals HOURS-3's after (`APPROVED` `ff3579ff5abd`, `opcommon.py` `c7ec467c5691`).
- **apply.sh on planted folders:** moved file, foreign `APPROVED`, edited install table: exit 3, nothing touched; a queued request: exit 6; a tampered frozen copy: exit 4; both bases: apply, verify and undo exit 0 and the undo restores the before hashes; a second apply does nothing.
- **Tests** (clone at `335c8f3c5`, heavy slot, TMPDIR outside the repository and `~/gov-os-runs`): `tests/unit/operator` + `tests/acceptance/W2-148` + the FR-1 probe: 508 passed, 0 failed; the FR-1 plant (an (a) ACT adding `Read(**)` to the home deny list) is refused at G6 with the new table and applied with the old one; with HOURS-3's four after files added: 655 passed, 0 failed.

## Findings
Classification: 3 findings, 0 blocking.
- **F1** (scope in, ordinary work yes, consequence other): once this ACT is applied, HOURS-3 Part B cannot be undone on its own (its `keep.txt` pins today's class-rules.yaml); undoing it alone needs this ACT undone first, or a rebuild. Reversed by: HOURS-3's `B undo` exiting 0 with this ACT's table installed.
- **F2** (scope in, ordinary work yes, consequence other): every later home-settings change, a deny addition included, is (b): the owner's yes after a review, as DEC-1142 (4) intends; fails closed. Reversed by: the owner choosing S15's option 1.
- **F3** (scope out, ordinary work no, consequence other): the home settings are still not control files in the (a) after-check's snapshot; only an unlisted write by an (a) ACT's script could reach them, which the dry run (S12) must catch. Reversed by: such a write getting past the dry run.

## Recommendation
Take it to the owner with `yes ACT-W2-148-S15-1 a3df8ff6`, applied after HOURS-3 Part B (its `B verify` first). F1 and F2 are the owner's to accept. After the apply, the narrow independent S15 check (package section 10) so W2-148's verdict computes READY. No new round (DEC-802).

```verdict
{"kpis": [{"kpi": "act-w2-148-s15-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}],
 "manifest_sha256": "a3df8ff6c3a49f0f6457eaf64e678b4790468540c707fe040448c45ff13356c5",
 "class": "O",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T05:29:01+00:00",
 "replay_refused": []}
```
