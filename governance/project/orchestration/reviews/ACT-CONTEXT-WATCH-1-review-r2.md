# ACT-CONTEXT-WATCH-1: independent review, round 2 of 2 (DEC-1010)

- **task:** ACT-CONTEXT-WATCH-1 (GOV_TICKET DAEO-ktiw)
- **Reviewer:** independent auditor, fresh read-only session, Opus 5.5, 2026-11-12
- **Bundle:** `acts/ACT-CONTEXT-WATCH-1/`, manifest sha256 `5bdfa0981808513db3d9fceeb30f13ba11ea72ea28528ef40664bfe9a931da5a`; round 1's bundle `acts/ACT-CONTEXT-WATCH-1.r1-c6dabb5e/`
- **Hook bytes:** `213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242` (W2-176 at `3b6c5cb79d39`); round 1's `c6dabb5e…` (`3a580a4b4d42`)
- **decisions:** DEC-1141 (2)(3), DEC-1140 (1)(b), DEC-1118 (A) (replaced), DEC-315, DEC-1104 (2), DEC-1010, DEC-801, DEC-808, DEC-1073, DEC-1014

**Classification:** 2 findings, both in scope, ordinary work yes, consequence other. Neither blocks; no round is proposed.

## Verdict
act-context-watch-1: **pass**.

## Checks
1. **Diff between the rounds:** only `apply.sh` (the `HOOK_SHA` line), `manifest.json` (`dec`, check 2's hash, check 3's body and count 7→8, the `apply.sh` and `rehearsal.log` hashes) and `rehearsal.log` differ. `before/`, `after/` and `list.txt` are byte-identical. `before/` equals the live files and `w2/integrate` (`12119eb31a35`) today.
2. **Hashes:** the section 3 table, `list.txt` and every entry in the manifest's `files` and `rehearsal` were recomputed; all match. The manifest itself hashes `5bdfa098…`.
3. **Check 3:** in a `--no-hardlinks` clone of `w2/integrate` with `w2/W2-176` merged in the clone only, it prints 8 and exits 0. With `3a580a4b4d42` merged instead, it fails at the 180,000 case. `apply.sh check` exits 0 on the former and 6 on the latter. Check 2 is green on the merge; check 1 is red before the apply. Check 3's body equals `tools/check_hook.py`. Nothing round 1 checked is unchecked now except the removed cap. A model outside the table and the orchestrator text branch are unchecked in both rounds; W2-176's unit cases cover them.
4. **Fail safe and class:** apart from the hash, `apply.sh` is identical to round 1. The entry gate still refuses with exit 6 and writes nothing. The after copy has matcher `Bash` and timeout 10. No commit touches `class-rules.yaml`, `portability.py` or the template's hooks source since round 1. Class (b).

## Findings
### F1: the package text still describes the withdrawn cap and round 1's checks
- **Behaviour:** the header ("Under: DEC-1118 (A) … 200,000 tokens"), section 1 ("every lead and worker: at most 200,000"; option (a) "30,000 tokens of a 200,000 window") and section 8 ("a lead or worker is reminded against 200,000 (DEC-1118 (A))") describe the cap DEC-1141 withdrew. Section 6 keeps round 1's counts (D 166, F "6 and 7", G "200,000 window", H 65/166 against the log's 196, 8, 1,000,000, 95/196). Section 7 says every check is as round 1, but checks 2 and 3 changed. Superseded rule in use: DEC-1118 (A), replaced by DEC-1141 (3).
- Ordinary work: yes, because the owner reads sections 1 and 8 to decide on the yes line.
- Consequence: other.
- Scope: in.
- **Reversed by:** a regenerated package whose header and sections 1, 6, 7 and 8 match the log and DEC-1141, or an owner ruling that the yes binds to the bytes alone.
- **Fix:** text only in `ACT-CONTEXT-WATCH-1.md`; no new bytes and no rebuild (the manifest does not hash the package).

### F2: round 1's review record is missing at its cited path
- **Behaviour:** `governance/project/orchestration/reviews/ACT-CONTEXT-WATCH-1-review.md` is not on disk and not in any git ref. Section 7's round 1 READY can't be traced, and the operator's G4 on a morning run would find no record.
- Ordinary work: yes, because a reader or the operator follows section 7's path.
- Consequence: other. Tonight's by-hand route runs no G4, and this record can be filed there.
- Scope: in.
- **Reversed by:** the record found at a path or ref not reached by `git log --all -- <path>` and a grep of `orchestration/`.

## Not done
- A one-file runner script in my own TMPDIR was refused by the quiet-hours rule and queued for the 09:00 morning package; not retried.
- The guard refused `bash -c "$(cat …)"` twice; I stopped using that form. The manifest's check strings ran with `bash <file>` from the clone's root: the same bytes and, for a single here-document, the same behaviour.
- No live `.claude/` touched, no Claude session started, no pytest run. The clones were removed (scratch 462M at peak, 20K after).

```verdict
{"kpis": [{"kpi": "act-context-watch-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
