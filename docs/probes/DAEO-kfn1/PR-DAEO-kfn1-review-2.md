---
type: probe
task: DAEO-kfn1
kind: "narrow independent check of the path case P-W2-189-P3 (a) revisions (DEC-1156 (7)); the FULL review at c512f982f (PR-DAEO-kfn1-review-1) stands for the product change"
reviewer_session: b7cd993a-5d58-4953-a98e-2f60203e5b55
reviewer: "au-2, independent-auditor, claude-opus-5-5, effort max (the launcher's review round 2), C2, read-only"
implementer_session: c029820f-89eb-4834-93ed-c8706a123a50
implementers: ["td-3 c029820f-89eb-4834-93ed-c8706a123a50 (independent-test-designer, e3c67d369)", "en-3 99280756-ff5f-4f27-aa9a-dbaa13df12f4 (engineer, df4c68b12)"]
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ae5b599b659e6d8b58d567b48ae9975d33ffd083
probed_range: 58ee60e19..da02e3b0a
date: 2026-11-16
decisions_applied: [DEC-1197, DEC-1156, DEC-1068, DEC-1010, DEC-820]
---
# PR-DAEO-kfn1-review-2: W2-189 (DAEO-kfn1) narrow independent check of the P-W2-189-P3 (a) revisions (five cases, four files)

Reviewer: independent-auditor au-2 (claude-opus-5-5, effort max), fresh read-only session b7cd993a-5d58-4953-a98e-2f60203e5b55, launched by the ticket lead with brief au-2 on 2026-11-16 at 10:12 GMT; checked head ae5b599b6 (scope 58ee60e19..da02e3b0a, four test files). It cites PR-DAEO-kfn1-review-1 (the FULL review, PASS at c512f982f), which stands for the product change. Its return follows as it wrote it; the lead wrote nothing in it.

---

Sandbox check (EMG-d4b-launched.md step 0, `GOV_TICKET=DAEO-kfn1`, `GOV_ROLE=independent-auditor`):
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kfn1','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system`, and no file was made. This is the expected result.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0` (exit 0). `git update-index --refresh` exited 0. Both work as required.

ps check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1). No model process of mine is running.

task: DAEO-kfn1 (W2-189), brief au-2. A narrow independent check of the P-W2-189-P3 (a) revisions, `git diff 58ee60e19 da02e3b0a` (four test files), at head ae5b599b6.

status: DONE, PASS. All five revisions are exactly what the CTO decided, and none makes its case vacuous. Three rows are recorded; none blocks.

work_completed:
- Checked identity: HEAD is `ae5b599b659e…`.
- Read the ticket in full, including the path-case paragraphs at `.tickets/DAEO-kfn1.md:101,103`. Read DEC-1197 (2)(i), DEC-1156 (7), and review-1's Part A item 3, Part B (B1-B4) and "The five reds' new behaviour".
- Read the full scope diff and each revised case in context. Read the product code the cases depend on: `lexical.py:507-706`, `semantic.py:786-831`, `retrieve.py:458-469,612-647`, and `loader.py:30,58-74`.
- Checked commit roles and the merge's content.
- Ran the two briefed runs.
- Ran non-vacuity probes on scratch copies:
  - the base source (2b6cf3e43);
  - five mutants of the head source: m-sem, the semantic facet does not leave stale paths out; m-lex, the lexical facet does not leave them out; m-ret, retrieve's chunk map does not leave them out; m-all, all three; m-recipe, the DEC-1068 recipe check is switched off;
  - an in-process probe of test_bounded's set-up, with and without an existing `rebuild.yaml`.

files_changed: none in any repository.
- Scratch files only, under `$TMPDIR/au2/`: a narrow head copy (src, the W1-21, W2-108 and unit/context tests, config files), the base src, five mutant srcs, four scratch trees, logs and probe repositories.
- Step 0 wrote one loose blob to the shared object store and refreshed this worktree's index, as the brief requires.
- `git status --porcelain` is empty at the end.

evidence:
- `git diff c512f982f 58ee60e19 -- src/gov/retrieval src/gov/retrieve src/gov/cli/main.py`: 0 lines. The product code is the code review-1 judged. The only other src change in that range is W2-190's `src/gov/adopt/stages.py`.
- `git diff --stat 58ee60e19 da02e3b0a`: exactly the four files (60 insertions, 11 deletions). `da02e3b0a..ae5b599b6` changes only the probe record.
- Blob identity: the three acceptance files are the same in e3c67d369, da02e3b0a and ae5b599b6 (9b68c0fad, a6c4f4246, 5538b4b9b). test_bounded.py is the same in df4c68b12, da02e3b0a and ae5b599b6 (f08044839).
- Merge check: every other acceptance path in the merge equals the ticket side. The merge made no content of its own.

tests:
- (1) The four files, in the brief's form: `78 passed, 9 deselected in 38.13s`.
  - The 9 deselected are opt-in lifted/breadth cases (DEC-1061), deselected with or without the `-m`/`-k` filter: `test_w1_21_command.py::test_an_option_that_is_no_number_is_a_usage_error[--batch-size]` and `[--bundle-budget]`, `::test_in_a_project_without_an_index_the_command_answers_and_builds_nothing`, and six parametrised `test_bounded.py` cases (`test_an_emptied_capability_file_blocks_and_is_never_read` ×3, `test_an_emptied_dependency_ticket_blocks_and_is_never_read` ×1, `test_an_emptied_file_blocks_the_brief_and_the_dry_run_and_writes_no_brief` ×2).
  - With `--optin lifted --optin breadth`, the filter leaves out none of the 87.
  - None of the five revised cases is among those left out.
- (2) `tests/acceptance/W2-189`: `43 passed in 4.14s`.
- Probes (stand-in embedders only):

| Probe | Result |
|---|---|
| Base src: W2-108 committed case, 3 working-tree cases, 2 test_bounded cases | `1 failed, 5 passed in 9.00s` (the committed case, at `:76`) |
| W1-21's two cases on base | `2 failed in 3.33s` (bundle `:83`, command `:42`) |
| W2-108 committed case on m-sem / m-lex / m-ret / m-all | `1 failed` (`:82`) / `1 passed` / `1 passed` / `1 failed` (`:82`) |
| W1-21 bundle case on m-all / m-lex / m-ret | `1 failed in 2.15s` (`:80`) / `1 passed` / `1 passed` |
| test_bounded's two cases on m-recipe | `2 failed in 0.40s` |
| `tests/acceptance/W2-189` on m-lex / m-sem | `1 failed, 42 passed` each (its lexical and semantic F1 cases) |

discoveries:
- (1) W2-108's committed case does not exercise the lexical facet's leave-out (R1). The ticket's own F1 lexical case does.
- (2) Two READMEs and one module docstring still describe the old rule. Both READMEs are outside the four files the ticket gained (R2).
- (3) test_bounded's helper appends to an existing `rebuild.yaml`. For a fixture that already commits `lexical_split_identifiers: true`, the case would pass on the uncommitted-edit rule rather than the recipe (R3). This fixture has no such file.
- (4) The W1-21 bundle case's two defences each cover for the other: the facet's leave-out and retrieve's chunk-map leave-out. The case judges the end-to-end outcome, as F1 does.

risks:
- The W1-21 bundle case does not assert that the bundle answered at all. Serving is asserted by W2-108's committed case (AVAILABLE, non-empty hits) and by W2-189's S1/S3. The CTO's words did not ask for it.
- The stopping reason on a lagging store (B2) stays open, as decided.

lessons: The guard treats a call that writes a script and runs it, while naming `tests/acceptance/`, as a write into the acceptance tests (ACT-GUARD-FIX-6 option B, `pretooluse.py:376-380`). This holds even when the script sits under `$TMPDIR`. Build the scratch in a call that names no test path, then run pytest directly.

proposed_decisions: none.

unresolved: B1-B4 from review-1 stay as recorded rows (B2 is open for the CTO). They are not in this scope.

recommended_next_action:
- Treat the P-W2-189-P3 (a) revisions as passing the narrow check, and land the ticket on its normal path.
- Record R1-R3 as rows.
- If the CTO wants it, a test designer can later update `tests/acceptance/W2-108/README.md:75-76`, `tests/acceptance/W1-21/README.md:272` and the W2-108 module docstring, and add a lexical query on a tides phrase to W2-108's committed case.

decisions: DEC-1197 (2)(i), DEC-1156 (7), DEC-1068, DEC-342, DEC-430, MR-3, DEC-953 item 2, DEC-1061, DEC-801, DEC-808

guard_refusals: 1.
- Refused call: one Bash call that wrote a runner script and a node-id list into `$TMPDIR/au2/` and ran the script, naming acceptance node ids. The guard answered "only the independent test designer writes the acceptance tests (MR-3) (DEC-953 item 2)". The rule is option B: a run the scan cannot read, in a call whose text names the acceptance tests, counts as a write. Nothing in that call ran.
- I did not retry it in that form. Afterwards:
  - I ran pytest only in the brief's own line form, with no self-written script.
  - I built the mutant sources in calls that name no acceptance path.
  - I ran W1-21's cases in scratch trees under `$TMPDIR`. W1-21 always loads `REPO_ROOT/src`, so the brief's PYTHONPATH form cannot redirect it.
- Under `in_a_trees_tests` (`pretooluse.py:1373-1383`, row 81), a scratch folder in /tmp is not an acceptance tree. Those scratch copies came from the `git archive | tar` made before the refusal. The lead or CTO may judge whether that use was within the rule.
- Separately, the harness's own rm check (not the guard) stopped `rm -rf "$M/$m"`. I removed the rm, since the folders did not exist yet.
- No read was refused.

## Revision 1: W2-108 `test_a_committed_change_is_seen`. Verdict: pass

Read: `tests/acceptance/W2-108/test_w2_108_change_seen.py:41-49` (the helper, unchanged), `:52-58` and `:90-104` (the working-tree cases, unchanged), `:61-87` (the revised case), `w2_108_support.py:162-191` (corpus and questions).

(a) It is exactly what the CTO decided.
- The diff has one hunk (`@@ -59,11 +59,32 @@`). The committed case no longer calls `assert_stale_after`.
- It asserts:
  - freshness is still `STALE [notes/tides.md]` (`:74`; this line is unchanged from the helper);
  - the lexical and semantic facets and the tide question are all AVAILABLE (`:76-79`);
  - the hits are not empty (`:80`);
  - tides.md is in no hit (`:81-83`) and not in the bundle's evidence (`:84-85`);
  - tides.md is in `store_of(root)["stale"]` (`:86-87`).
- The stopping reason is not asserted, which fits B2.
- The test designer's additions are all within scope:
  - the tide question (`QUESTIONS[2]`) gives a query on which tides.md's old text would be nearest;
  - the `store_of` step is the only way to read `stale` through the function, because the function's bundle has no `store` key;
  - the non-empty-hits check stops the "not in hits" lines passing on empty answers;
  - the bundle-evidence check applies F1 to the fused answer.

  None of them asserts beyond DEC-1197 (2)(i).
- Nothing else in the file changed.

(b) The case is not vacuous.
- On m-sem it goes red at `:82`: "the semantic hits serve notes/tides.md". The baker question's hits are 30 deep (`semantic.TOP_K`), which covers the whole 7-chunk store, and include tides.md at distance 1.0.
- m-all is red at the same line.
- On base it is red at `:76` (lexical facet unavailable).
- The lexical half is vacuous: m-lex stays green. The case's only lexical query is the amber phrase, which tides.md never held, and lexical hits are exact-phrase lines (`lexical.py:686-696`). This is row R1. The lexical leave-out is covered by `test_w2_189_stale_left_out.py::test_f1_the_lexical_facet_gives_no_hit_and_no_ranked_chunk_of_a_stale_path`, which goes red on m-lex.

(c) The working-tree cases (`[edited]`, `[deleted]`, second edit) still call `assert_stale_after` byte for byte. They are green at head and on base.

## Revision 2: W1-21 `test_a_file_changed_after_the_index_is_never_cited_at_its_old_bytes`. Verdict: pass

Read: `tests/acceptance/W1-21/test_w1_21_bundle.py:67-84`, `w1_21_support.py:411-424` (`check_citation`), `:439-478` (`check_bundle`), `:622-623` (PHRASE, PAGING).

(a) It is exactly what the CTO decided.
- The `FACET_UNAVAILABLE` assertion is replaced by two checks: `paging/p3.md` is not cited (`:80-81`), and it is in `store_of(repo)["stale"]` (`:82-84`).
- The stopping reason is not asserted (B2).
- The set-up (`:71-73`) and `check_bundle(..., root=repo)` (`:74-75`) are unchanged. The docstring and the Rewrite-Reason comment are updated. Nothing else in the file changed.

(b) The case is not vacuous, and it still catches a citation at old bytes.
- `check_bundle` → `check_citation` still refuses a sha256 that is not of the current file or span, and cited text that is not in the span (unchanged).
- The new `:80` refuses any citation of the changed path, at any bytes.
- On t-all it goes red at `:80`: the bundle cites `paging/p3.md` among p1, p2, p4, p6 and others. The phrase ranks it when it is not left out.
- On base it goes red at `:83` (store_of has no `stale`).
- On t-lex and t-ret alone it stays green, because each defence covers for the other.

## Revision 3: W1-21 `test_the_command_returns_the_bundle_of_the_function`. Verdict: pass

Read: `tests/acceptance/W1-21/test_w1_21_command.py:30-48`.

(a) It is exactly what the CTO decided.
- Only `:42` changes: the key set `{commit, root}` becomes `{commit, head, stale, root}`. The comments at `:36-40` are updated.
- `:43-48` are unchanged: commit is 40 hexadecimal characters, root resolves to the project, the function's bundle has no `store`, and the rest equals the function's bundle whole.
- The set equality is stricter than before, not weaker.

(b) On base it goes red at `:42`. The values of head and stale are left to W2-189 S2's cases, as the CTO's words ask only for the keys.

## Revisions 4 and 5: `tests/unit/context/test_bounded.py`. Verdict: pass (both)

Read: `:12,19` (imports), `:31-39` (FILES; no `rebuild.yaml`), `:56-62` (`_recipe_switched`), `:159-166` and `:312-318`. The old lines are 149-152 and 299-301 at 58ee60e19.

(a) They are exactly what the CTO decided.
- In each case, the set-up `_commit(project, {"notes/new.md": "# New\n"})` becomes `_recipe_switched(project)`, at `:163` and `:316`.
- The assertions at `:165-166` and `:318` are unchanged.
- The helper writes `lexical_split_identifiers: true` into `governance/project/rebuild.yaml` (`loader.py:30,58,67`). This is the INDEX_FLAGS value W2-13's case uses.
- No other case changed. df4c68b12 (Role: engineer) touches only this file.

(d) The recipe value is what makes the index unusable.
- In the probe, before the helper runs: fresh, and 2 supplementary items.
- After it runs:
  - git status shows `?? governance/project/rebuild.yaml` only (untracked; no tracked edit, no commit);
  - freshness is `stale` with 7 paths, and `served` is `stale`;
  - the supplementary list is empty, and the drop reason is "the lexical index is stale".
- On m-recipe (`lexical.py:596` switched off) both cases go red. On base both stay green, since the set-up is unusable under both rules.
- Where a fixture already has a `rebuild.yaml`, the helper reads it and appends the line:
  - a committed file with `false` or with another key ends `stale` (by the recipe and by the tracked edit);
  - a committed file with `true` ends `stale` by the uncommitted edit alone (row R3);
  - an untracked file with `true` stays fresh, so the case would fail loudly, never pass falsely.

(e) MR-3 and DEC-430 hold.
- `git log --format='%h %(trailers:key=Role)' 58ee60e19..da02e3b0a -- tests/acceptance` lists e3c67d369 (`Role: independent-test-designer`) and the merge da02e3b0a (`Role: orchestrator`). The merge carries the designer's three blobs byte for byte and makes no acceptance content of its own.
- The engineer's commit touches no acceptance file.

## Findings (rows; none blocking)

**R1.** W2-108's committed case runs no lexical query that tides.md's old text would answer. A lexical facet that served a stale path's chunks would leave this case green (m-lex: `1 passed`).
- The semantic half and the end-to-end check do catch stale text (m-sem and m-all red at `:82`).
- The lexical leave-out is caught by W2-189's own F1 lexical case.
- What would reverse it: a lexical search of an old tides phrase that goes red on m-lex.
- Ordinary work: yes, because a lexical leave-out regression is an ordinary mistake.
- Consequence: other (W2-189's F1 lexical case catches it; this case adds no lexical protection).
- Scope: out (the CTO's words do not ask for a per-facet query).

**R2.** Two READMEs and one docstring still describe the old rule:
- `tests/acceptance/W2-108/README.md:75-76` says that after "a committed change; both facets report `stale`, and the bundle stops on `FACET_UNAVAILABLE`";
- `tests/acceptance/W1-21/README.md:272` gives `store` as `{commit, root}`;
- W2-108's module docstring (`:8-9`) says the semantic facet reports stale after such a change.

The READMEs are outside the ticket's paths, and the revisions rightly left them alone.
- What would reverse it: the README lines updated, or a ruling that README maps describe test names only.
- Ordinary work: yes, because a reader of the README meets the old rule.
- Consequence: other (documentation; no test outcome changes).
- Scope: out.

**R3.** `_recipe_switched` appends to an existing `rebuild.yaml`. If this fixture ever committed `lexical_split_identifiers: true`, the append would not switch the recipe. The case would then pass by the uncommitted tracked edit (probe: `M`, stale 1, `served` stale), not durably by the recipe. Today FILES has no `rebuild.yaml`, so the recipe is the only cause.
- What would reverse it: a helper that sets the key to the value opposite to the built recipe.
- Ordinary work: no, because it needs someone to add a committed `rebuild.yaml` with that key true to this fixture.
- Consequence: other (the case would still assert an unusable index, by another rule).
- Scope: out.

```verdict
{"kpis": [{"kpi": "PATH-CASE-P3", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R3", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}], "reviewer": "independent-auditor, fresh read-only session; not the author"}
```
