# q02 writer variant, version 2: notes (W2-94 P1 option (b); a draft, not installed)

## The draft
- File: `.gov-runtime/scratch/orchestrator/drafts/q02-variant-v2/EXAMIN-writer-q02-fix.md`
- sha256: `7aa6d88c3a7769c1abe34ffd54b8ced4f4110fb2208ed1f316d1a7c000b021b6` (18,335 bytes)
- v1, for comparison: `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`
- It was checked with the code of `w2/W2-94-fix` (66dd6e77a), not run in a wall.

## What changed from v1 (P1, P2, and the checker paragraph)
1. **Front matter:** `version: 2`. Nothing else in it changed.
2. **The opening:** "Version 2", plus one sentence. The writer cannot read the fixed brief, so section 6 writes out every part of it that binds the writer.
3. **§1:** the binding list now points to section 6 and adds "section 8's words for your result". Its meaning is unchanged: v1 already bound §3, §4, §5, §7 and §9 word for word.
4. **§2 Input:** names the two files the launch script also stages: `input/sample.json` (always staged, used only in step 3) and `input/selection.json` (its `sample` is empty here, `last_audit` matters for §9). v1 named only q02.yaml and verdict.txt, which was inaccurate about what is staged.
5. **§3 step 3:** "the launch script puts that ordered list in input/sample.json for this case only" now reads "the ordered list is in input/sample.json; use it for this case only". The file is staged on every fix run (`plan_fix`).
6. **§5 Output:**
   - It names the §8 words. P1 (iii): a guessed word is refused 20 "schema".
   - It says "nothing else in out/ when you deliver".
   - It gives the stop form `{"questions": 0, "by_kind": {}, "by_area": {}, "stopped": "<word>"}`, which ends **21** "stopped" (`check_result` checks `stopped` before the schema). P1 (iv): v1's form (`questions: 0`, no word) ends 20 "fix_result".
   - `out/conflicts.md` appears only on a stop (P2: beside a delivered result it refuses 20 "entries").
7. **The last paragraph:** there is no walled checker any more (DEC-1180 (2)). The launch script puts the file in place of the old q02 and keeps the old file in the run's archive; the operator re-runs `check_gold.py`, and 20 of 20 is expected.
8. **New §6, "The fixed brief's rules, word for word":**
   - The fixed brief's §3, §4, §5, §8 and §9 are copied byte-identical. The §7 YAML block is identical apart from the 2-space list indent. I checked this by substring match against `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`.
   - Each section is followed by a bracketed "(For this run …)" note that applies it to one question:
     - §4: on delivery, conflicts.md is written only on a stop.
     - §5: q02 is `code-location`; items 1, 3 and R5 are kept by touching nothing else; a replacement draws from `input/sample.json` and cannot reuse q02's own governing source.
     - §7: the file is `out/q02.yaml`.
     - §8: `questions` is 1, plus `action`.
     - §9: each condition and its stop word:
       - not writable by step 2 or step 3: `form-not-writable`;
       - COPY-HEAD missing: `input-missing`;
       - COPY-HEAD malformed, or `last_audit` not null: `input-malformed`;
       - a conflict: step 3 first, then `decisions-conflict`;
       - a forbidden read: `forbidden-read-needed`.
   - All five words are in `writer-result.schema.json`'s `stopped` enum and in `STOPPED`.

The order, the question, the verdict text, the bounds and §4 "Never" are all unchanged from v1.

## The self-check (the code of w2/W2-94-fix; no hidden content)
I ran `check_result` and `resolve_brief`, imported from the branch's `indep_launch.py`, with the branch's `writer-result.schema.json`, on hand-made results. The script is at `$scratchpad/v2check/check.py`.

| Input | Outcome |
|---|---|
| `resolve_brief` on v2's front matter, fix run | (`claude-sonnet-5-5`, `writer-result.schema.json`, sample 0, no entry): accepted |
| `{"questions":1,"action":"corrected","by_kind":{"location":1},"by_area":{"code":1}}` | accepted, action corrected |
| the same as replaced, with `fact:0`, `contract:0`, `kernel:0` | accepted, action replaced |
| v2's stop form with `stopped: form-not-writable` | refused **21** "stopped" |
| v1-style stop (no word) | refused 20 "fix_result", the P1 (iv) case |
| guessed key `code-location` in by_kind | refused 20 "schema", the P1 (iii) case |

## Scaffold 3 is needed
`--commit` pins the brief's bytes. Stage 10 reads the brief with `blob(repo, commit, brief_path)`, which is `git cat-file blob <commit>:<path>`, and checks its sha256 against `--brief-sha256`. The working tree is not read. So v2 must be committed in the launch clone. The clone is at `52208402587e` on `w2/integrate` and its tree is clean. The CTO runs:

```
cd ~/gov-os-runs/W2-94/examin
git status --short   # expect nothing
cp /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/q02-variant-v2/EXAMIN-writer-q02-fix.md governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md
sha256sum governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md   # expect 7aa6d88c…21b6
git add governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md
git commit -m "Launch scaffold 3 for W2-94's q02 fix (P1 (b)): the writer variant version 2, self-contained (sha256 7aa6d88c); no code

Task: DAEO-g87r
Role: orchestrator
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016M9azgrN7ySZMxKEFWQgjt"
git log -1 --format=%h   # this is the new --commit
```

Run these only after the owner's yes on v2. The same path holds v1 at 5220840, which stays reproducible.

## The new APPROVED line (the owner's operator, in `<sets root>/indep-walls/APPROVED`)
```
7aa6d88c3a7769c1abe34ffd54b8ced4f4110fb2208ed1f316d1a7c000b021b6  brief governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md
```
The operator's four commands change as follows:
- **(1)** installs v2's bytes at the same repo path, with a Role: owner commit.
- **(2)** appends this line. v1's line can stay; `b_lines` matches on the hash and the path together.
- **(3)** uses `--brief-sha256 7aa6d88c…21b6 --commit <scaffold-3 short sha>`.
- **(4)** is unchanged.

## Risks left open
- **Possible objection: the interpretation notes.** The "(For this run …)" notes are new text, though v1's sentence "§9's stop conditions … apply to you" already implied one-question readings. A reviewer could call the §9 word mapping, and the `decisions-conflict` "after step 3" ordering, new meaning. They resolve one ambiguity: in v1, step 3 and §9's conflict stop overlap. I chose step 3 first, then the stop, because that follows v1's own order.
- **§4 and a mistaken open.** The fixed brief writes conflicts.md even if the writer goes on. In this run that would refuse 20 (P2), so a file opened by mistake and left unused is recorded nowhere.
- **§1's "counted in your result".** v1 also says an ignored instruction is "counted in your result", but neither the schema nor the fix check has a key for it. I left the sentence unchanged, as in v1. A writer that adds such a key at the top level passes, because the top-level schema is not closed.
- **The other residuals are unchanged:** P4 (the counts schema refuses `--counts-only` 17), P5 (22 still delivers) and P8 (AUDITS.log; currently absent under ~/gov-os-runs/indep, so clear today).
- **Untested in a wall.** The draft was checked by the code's result logic, not by a live walled run.
