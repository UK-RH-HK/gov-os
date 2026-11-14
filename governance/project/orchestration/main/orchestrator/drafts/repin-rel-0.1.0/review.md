# Review: ACT-REPIN-REL-0.1.0, the re-pin from release 0.1.0 (draft bundle, before "released")

Reviewed: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/repin-rel-0.1.0/`. Its BUNDLE.sha256 has sha256 75ab992b…9029f, and all 7 files show OK. The repository head is f2f28ed4e and the tree is clean. Reference: window 5 (`pin/REPIN-COMMANDS-W5.sh`, `reviews/ACT-REPIN-W5-review.md`).

Classification: 0 blocking. 7 rows (F1 to F7). None both fails open or loses work and is reachable in ordinary work.

## Findings

**F1 (row): R-5's "stricter" bar accepts any new refusal of a case that should be allowed, not just the two forms the notes name. So a new false refusal of ordinary work would pass part B.**
- For FIX-4, the check compares two counts (rel_checks.sh:245-246): the number of FAILED lines, and the number of `E AssertionError: …: want allow, got deny` lines. It does not compare names.
- FIX-4's assertion message has that same form in both `test_planted` (test_guard_fix_4.py:180) and `test_rules_1_and_5_judge_what_resolves` (test_guard_fix_4.py:288).
- The second test's "want allow" cases are ordinary work. Examples: "rule 5: a reviewer's record" (`echo x > docs/probes/W2-64-review.md`, :239) and "rule 1: the test designer writes the tests" (:225).
- So if the pin at C refused a reviewer's own record, the check would still print ok and pass.
- FIX-3 (rel_checks.sh:288-291) accepts any case that fails only under the new pin, as long as it says "want allow, got deny".
- A lost refusal does still fail both checks, so the bar holds against failing open.
- Fix: list the accepted names, as `g14` does with `G14_RED` (rel_checks.sh:254-264). Today that is FIX-4's two names, plus FIX-3's one new-only and one old-only name.
- Ordinary work: yes, because a guard regression at C would hit an honest session's ordinary write.
- Consequence: other. It fails closed: sessions are refused after the switch until the one-line rollback.
- What would reverse this: if every "want allow" case in both suites were a documented gap and none were ordinary-work allows. test_guard_fix_4.py:225-279 shows otherwise.

**F2 (row): the logs give only the count of FIX-3 cases that differ between the pins, not their names. The names exist only in `/tmp`, which a reboot clears.**
- r5 log:85 says "1 now refused, 1 let-throughs now refused" and names neither case.
- I found the names in `/tmp/gov-os-rel-repin/run/x/checks/fix3-newonly.txt` and `fix3-oldonly.txt`:
  - "fix3 python heredoc reading .env (gap as today)": the new pin refuses a secret read.
  - "fix3 unterminated heredoc naming acceptance judged as before": the old pin let it through and the new pin refuses it.
- These are the same two forms that NOTES.md:77-83 names, so R-5's claim holds today. But the only evidence for it is in scratch space.
- Fix: print the names in the ok line, as FIX-4's line does (rel_checks.sh:247).
- Ordinary work: yes, because a reboot before the post-fill review is ordinary.
- Consequence: other (the evidence is lost).
- What would reverse this: a kept log or record that names the two FIX-3 cases.

**F3 (row): NOTES says the 9 CTO tools are window 5's, "used unchanged". `tools/heavy_slot.sh` is not window 5's reviewed copy.**
- NOTES.md:16 makes the claim.
- `sha256sum -c pin/REPIN-W5.sha256` gives `tools/heavy_slot.sh: FAILED`. The file is dated 11-12 23:46 and has a `.pre-dec1157` copy beside it.
- r5 ran with the current bytes, and `fill_release.sh` will hash whatever is there at fill time (fill_release.sh:45-47). So the gap is between the claim and the reviewed set, not in what was rehearsed.
- Part B also runs files that are not in the 13-file list, as in window 5:
  - `drafts/act-guard-fix-4/test_guard_fix_4.py`
  - `drafts/g14/test_g14.py`
  - `tools/heavy_slots.conf`
  - the staged W2-141 hook files
- Ordinary work: yes, because the CTO edits its tools in ordinary work.
- Consequence: other.
- What would reverse this: a review record that covers heavy_slot.sh's DEC-1157 bytes and is named in NOTES.

**F4 (row): the neg-check log is not "the files as in this bundle", as NOTES §3 says.**
- neg-check ran from 15:17:54 to about 15:24:41. rel_checks.sh was last changed at 15:30:36.
- The change is in section 7. neg-check stops earlier, at section 6b's staged-import check (log:80-85), so the outcome still holds for the bundle's bytes.
- Ordinary work: yes.
- Consequence: other (wording).
- What would reverse this: a neg-check log dated after 15:30:36.

**F5 (row): R-2's trailer form is sound, but the reason NOTES gives for it does not match the code.**
- NOTES.md:72-74 says `Task: decision-record` fits because the commit "changes a governance record (the tool registry)".
- Gate (h)'s list of governance records does not include `governance/project/tool-registry.yaml` (src/gov/close/gates.py:27-30, 144-165). So gate (h) does not measure this commit.
- What actually carries the commit is `Role: owner`, which the landing check passes (P-RELEASE-1 §4 cites landing_check.py:10-13), and window 5's identical commit 8f00bb908.
- Ordinary work: yes, because a reader may rely on the stated reason.
- Consequence: other.
- What would reverse this: a gate that does count the tool registry among governance records.

**F6 (row): `fill_release.sh` fills whatever template and helpers are on disk. It does not first check them against the reviewed BUNDLE.sha256.**
- fill_release.sh:39-47 fills and hashes without checking BUNDLE.sha256.
- The template-equality check in rehearse_rel.sh:97 compares against the current template, not the reviewed one.
- So if someone edits a file after this review and before "released", the edit goes into the operator's hash list. README:51-53's phrase "stops the line if any file changed since the review" would then be true only against the post-fill review (README:4).
- Fix: make `sha256sum -c BUNDLE.sha256` the first line of `fill_release.sh`.
- Ordinary work: yes, because an honest edit in between is plausible.
- Consequence: other. The post-fill review is the backstop.
- What would reverse this: a post-fill review that diffs the filled script against this reviewed template, with the four value lines masked.

**F7 (row): two of window 5's rows are still present, and there is one new evidence-wipe.**
- Window 5 F5: there is no INT/TERM trap. If the operator presses Ctrl-C during part S, the refresh started with `setsid` keeps running and can flip the store link after the script has died, with nothing to put it back (template:206-207).
- Window 5 F6: `g14` ignores ERROR results (rel_checks.sh:259-260).
- New: `rm -rf "$X"` at template:59 runs before part 0. It wipes the previous run's `/tmp/repin-rel-0.1.0` diagnostics, and `tee` without `-a` overwrites `~/repin-rel-0.1.0.log`. Window 5 used `mkdir -p` here.
- Ordinary work: yes, because a Ctrl-C, or a rerun after a STOP at the CTO's word, is ordinary.
- Consequence: other. No work is lost and nothing fails open: the gov link is untouched, and the store half is at the same head.
- What would reverse this: a trap and an append-mode log in the script.

## What I probed and found sound

1. **Every stop is safe.**
   - Before line 59, the only checks are the slot guard and the commit check, and both exit cleanly (template:35-36).
   - Part 0 (115-130) and part R (133-169) write nothing outside `$X`.
   - The negative runs confirm it:
     - neg-src and neg-uncommitted stop in part 0.
     - neg-tag, neg-manifest and neg-sha stop in part R, with nothing built.
     - The live fixed paths are UNCHANGED in every negative log.
   - Part S records PREV only if the link moved (219), before its own stops (221-223).
   - Part B's failure calls `stop`, then `restore_store`. neg-check log:84-85 shows "the store link is back on W2-00-store-b".
   - A subshell running `stop` because of `set -E` only repeats the STOP message. It always fails closed.
2. **Part R binds the four values to the tag and the record.**
   - C: the tag must be annotated, its commit must have exactly one parent, and that parent must be C in full. The manifest's `commit` must also be C in full.
   - RECORD: equals manifest.json's sha256, after `manifest.sha256 --strict` holds.
   - SHA: equals the manifest's `wheel.sha256`. Both builds in part A must also equal SHA (180), and SHA is checked again after the switch (273-274).
   - EPOCH: equals C's `%ct`.
   - Between C and the tag, only the two record files may change.
   - `verify` passes on the tag's `template/`, and the tag is in the branch's history.
   - `fill_release.sh` reads the same facts from the tag and refuses otherwise. The only thing typed in is the argument C, and it is cross-checked twice.
3. **The live paths written are exactly the act's.**
   - `~/.local/share/gov-os/{pin-C,wheels/C}`
   - the store link and its spare half
   - `~/.local/bin/gov`
   - `tool-registry.yaml` and its commit
   - Everything else goes to `/tmp/repin-rel-0.1.0`, the scratch `restarts.jsonl` (only on a restart), or scratch HOMEs and clones.
   - The hooks are only read.
   - The new parts (R, the §5 lines, P-2) add only reads.
   - No `Co-Authored-By`, `Decided-by` or `Role:` line is written anywhere but the owner's own commit.
4. **The trailers parse.** I rebuilt the commit message (template:290-295) and piped it through `git interpret-trailers --trailer …`, then `--parse`, on git 2.43.0. It printed exactly `Task: decision-record`, `Implements: DEC-1178`, `Role: owner`. The body paragraph has no colon, so the trailers form a separate final paragraph. r5 log:150 shows the same three lines from the scratch commit.
5. **The builder's three points.**
   - R-1 is sound. DEC-1178 is ACCEPTED (owner, 2026-11-14), and no later decision changes it. Its own text names `gov` and 0.1.0, and item (3)(a) approves "the re-pin from the release as its §6". So it passes W1-06's checks: one decision id, in the register, accepted by the owner, and naming the tool (test_w1_06_approvals.py:28-50; test_w1_06_install_approvals.py:158-176). It also matches DEC-197 ("the registry's `approved_by` cites" the install's own entry) better than DEC-1037. `rel_registry.py` still refuses unless the entry it replaces is window 5's DEC-1037 entry (:62-63).
   - R-2 is sound. It is the same form as window 5's 8f00bb908; see F5 for the stated reason.
   - R-5 is sound against failing open: a lost refusal fails both checks. The bar is too wide against new false refusals; see F1.
6. **The logs support the claims.**
   - 7 of 7 modes report OK.
   - r5 shows exit 0 in 1,008 s (log:114, 151).
   - Every figure in NOTES §3's r5 row matches log lines 40-113.
   - The live fixed paths are identical before and after (log:130).
   - The store link, the halves and `w2/integrate` moved with three CTO landings during the run. The live store log's own hook lines show this (log:131-146). `git diff bf04ed69c893 f2f28ed4ef40 -- src pyproject.toml …` is empty, which explains why the quiet-point input check passed.
   - The r3 STOP and the direct FIX-3 log are the failures that R-5 then addressed, as NOTES says.
7. **The hash list passes.** `sha256sum -c BUNDLE.sha256` shows all 7 files OK, and BUNDLE.sha256's own sha256 is the value in the brief.

Also sound:
- No module name in the operator's working directory (`.gov-runtime/scratch/orchestrator`) shadows `gov` or the standard library for the `-E -c` calls.
- Only one hook exists in the main tree, `reference-transaction`, so no commit-msg hook stands in the way of the owner's commit.

```verdict
verdict: PASS
blocking: 0
reviewed_sha256: 75ab992beaf9044cf45188df3d25d7ee073aa5e982188fab1327e8e53369029f
```
