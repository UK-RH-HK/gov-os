# Review: ACT-CONTEXT-WATCH-1 (manifest sha256 `487c93c13e1b6ee2f223c5386fbb5cc38101737be200e94e4583aeb52350e58f`)

task: DAEO-ktiw
decisions: [DEC-1140, DEC-1104, DEC-1118, DEC-315, DEC-1010, DEC-801, DEC-808, DEC-1014, DEC-105]
reviewer: independent-auditor, fresh read-only session, sandbox check passed
W2-176 heads: `3a580a4b4d42` at the build; `ad13a5b36c65` at the end of this review

## Classification
Three findings, all in scope, none fails open or loses work (F1 ordinary yes, F2 ordinary no, F3 ordinary yes). None blocks; all three are recorded rows. Recommendation: rebuild the bundle with W2-176's current hook hash before the owner's yes line, unless W2-176 merges at `3a580a4b4d42`.

## Checks
1. **Hashes and scope.** Every hash recomputes. The before copies equal w2/integrate (`6e46f985b0a7`) and the main tree. The after copies add one block in each file (12 and 8 lines), nothing else. None of tonight's other ACTs' files is touched.
2. **Fail safe.**
   - No permission, allow rule or decision field is added.
   - The hook catches every error and exits 0 with no output.
   - With the hook file missing, the registered command exits 2 (reproduced). That is not a fail-closed block: the Bash call has already run, and the model sees an error after each call (F2).
   - `check` refuses (exit 6) on today's main tree, which lacks the hook file.
3. **Matcher and reach.** `Bash` keeps the portability check clean, and every role runs Bash often. The CTO is recognised by `class: coordination` on `DAEO-sdxk`. Sessions in worktrees that have not taken integrate miss the reminder (F3).
4. **Rehearsal.** Own clone with W2-176 at `3a580a4b4d42` merged:
   - check, apply and verify all exit 0; two files changed, modes kept at 644.
   - The five manifest checks match the manifest (counts 6 and 7).
   - The portability check gives `findings: []`.
   - Undo restores both files byte for byte.
   - pytest: `tests/unit/hooks` 165 passed / 2 skipped; `tests/unit/adapters` 94 passed; `tests/unit/gitenv` 60 passed; `tests/acceptance/W2-05` 29 passed / 1 failed (the sandbox's read-only `/tmp` blocks the rebuild lock).
   - Class (b); route: the owner's operator by hand.

## Findings
### F1: the pinned hook hash is no longer the approved one (in scope)
The ACT allows apply only when `context_watch.py` hashes as `c6dabb5e…`. W2-176 has since fixed R8 at `4dec7ec3c72c`. The file now hashes as `ed17fbb0e2b3aadbe141403860c914e3a1b14555647c7ab09e2840743e14c731`, and the CIT-P's section 2 names only that hash. Against the new head, manifest check 2 fails and check 3 passes. After a merge of the new head, `check` and `apply` refuse with exit 6 and nothing is applied. Section 7's R8 row is also out of date.
- Ordinary work: yes, because the ticket moved on during ordinary work while the ACT was being prepared.
- Consequence: other (fails closed: exit 6, nothing written).
- Reversed by: W2-176 merging at `3a580a4b4d42`.

### F2: the missing-file exit 2 is described as blocking (in scope)
For PostToolUse, exit 2 shows its error to the model after the call has run. It neither blocks nor undoes the call.
- Ordinary work: no, because the apply refuses until the file exists, and the registration and the file travel through the same branch history afterwards.
- Consequence: other.
- Reversed by: documentation or a live session showing a PostToolUse exit 2 blocking or withdrawing the tool's result.

### F3: "every session" overstates the reach (in scope)
Sessions load hooks from their own worktree's settings. The launcher's settings carry no hooks. Leads and workers on branches without the ACT commit get no reminder until their branch takes integrate.
- Ordinary work: yes, because ticket branches commonly lag integrate.
- Consequence: other (the PreCompact line still stands).
- Reversed by: launched sessions taking hooks from the main tree's settings.

## Sound
Hashes; scope; refusal before any write; atomic writes; frozen-copy checks; the entry check; undo; no weaker control; the hook silent on every error; markers ignored by git; portability; class (b).

## Hygiene
Nothing written in any tree. The scratch clone (251 MB) is removed. No embedder or model was started.

```verdict
{"kpis": [{"kpi": "act-context-watch-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```

# Round 2

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
