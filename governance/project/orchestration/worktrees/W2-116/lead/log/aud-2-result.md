**Step 0, sandbox check (launch_worker.sh):** passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-f58b` failed with `OSError: [Errno 30] Read-only file system`, and no file was created.
- (b) `git hash-object -w --stdin` worked (`1ae28402a109…`) and `git update-index --refresh` worked (exit 0).
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- **Tree:** `git -C /home/usain/gov-os-worktrees/W2-116 status --porcelain` is empty at the end, and HEAD is `037cf8a4fff0cada2b64fb8b7751b7c6d5dcd4ed`.

```
---
type: probe
task: DAEO-f58b
decisions: [DEC-1156, DEC-1157, DEC-1090, DEC-801, DEC-808, DEC-1010, DEC-1014]
reviewer_session: fa768cfe-532f-45b1-b455-f60826db00ad (independent-auditor; the session folder named in this sandbox's own TMPDIR task path)
implementer_session: d49a06de-2ce9-46c3-b967-87829495f150 (independent-test-designer, td-4: pass 2c's seven-file revision)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
probed_commit: 037cf8a4fff0cada2b64fb8b7751b7c6d5dcd4ed
scope: narrow independent check of pass 2c (the test designer's seven-file revision, DEC-1156 (7))
---
# Probe record: W2-116 pass 2c (DAEO-f58b), narrow check

## What was probed
- **Identity.** HEAD is 037cf8a4f. Its parents are 9e9428942 (first) and 6666cec2c. The merge brings in only the seven
  test files: `git diff 9e9428942 037cf8a4f` equals `git diff 9e9428942 6666cec2c`, 7 files, +19/-10. So the code
  under test is the same before and after, and only the test files differ.
- **Commits.** Seven commits, one per file. Each carries `Task: DAEO-f58b`, `Role: independent-test-designer` and
  `Rewrite-Reason: DEC-1156 (7), R2-F3's token key / S2's status part (W2-116 pass 2c)`.
- **Code read.**
  - `src/gov/retrieval/retrieve.py` 186-224: `_same_store` checks `s`, then `f` against the resolved folder.
    `_encode_continuation` writes `"s": commit, "f": folder`.
  - `src/gov/status/command.py` 180-209: `integration_store` follows `reranker` in the answer, and `not_read`
    comes from `_unread_in(answer)`.
- **Setup.** Two scratch clones under my TMPDIR (`git clone --shared --no-checkout`, detached): one at 9e9428942
  (before), one at 037cf8a4f (after). No `git worktree add`, nothing written in any repository folder. Every run used
  the brief's pytest command through heavy_slot.sh, with `PYTHONDONTWRITEBYTECODE=1`.
- **Before (9e9428942): 17 failed, 110 passed, 2 deselected.** The 17 red cases:
  - W2-131 acceptance: `test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[a-ticket-batched]`,
    `test_s3_the_continued_pages_are_todays_but_for_the_ids_of_register_items`
  - W2-133 acceptance: `test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[every-chunk-batched-gov-retrieve]`,
    `[every-chunk-batched-retrieve-alone]`, `test_s3_the_continued_pages_are_today_s_but_for_the_register_items_ids_and_status[gov-retrieve]`,
    `[retrieve-alone]`
  - W2-135 acceptance: `test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[almanac-batched]`,
    `[every-file-batched]`, `[almanac-batched-budget-1000]`, `[register-every-chunk-batched-gov-retrieve]`
  - Unit: `test_w2_131_register_ids.py::test_the_bundle_is_the_same_before_and_after_but_for_register_ids` and
    `::test_the_continuation_carries_on_the_same_before_and_after`; `test_w2_133_gap_label.py::test_the_bundle_is_the_same_before_and_after_but_for_a_gap_starter_s_label`
    and `::test_the_continuation_carries_on_the_same_before_and_after`; `test_w2_135_item_cap.py::test_the_bundle_is_the_same_before_and_after_but_for_the_cut_lines_and_key`
    and `::test_the_continuation_carries_on_the_same_before_and_after`
  - Status: `test_status.py::test_a_status_with_a_part_not_read_names_every_such_place`
- **Why they were red.** Each token failure shows only one extra item, `{'f': '<the case's store folder>'}`. The W2-131
  acceptance case names only `['continuation']` as changed. The status failure is `At index 9 diff:
  'integration_store' != 'not_read'`.
- **After (037cf8a4f): 127 passed, 2 deselected.** All 17 are green, and no case that was green before went red.
- **The two deselected cases.** The `rep:` lines for `tests/unit/retrieval/` and `tests/unit/status/` in
  `tests/optin-lifted-breadth.txt` deselect them: they are non-first rows of parametrised functions. They are the same
  on both sides, and none is a revised case (the revised unit cases are not parametrised). The brief's `-m`/`-k`
  filter left nothing out of these seven files: the collection is identical with and without it.
- **Mutation probes.** Each mutant edited `src/` in the after clone, ran the files, then restored the clone with
  `git checkout`; no clone was left dirty.
  - M1, the token gains another key beside `f` (`"g": 1`): **16 red** in the six token files (every case that
    compares tokens). Dropping `f` hides nothing else.
  - M2, the token's offset off by one: **20 red**.
  - M3, R2-F3's folder check inverted, so page 2 on the same folder is refused: **14 red**, including every
    continued-page case in the six files. `f` is still exercised where a token is used, so dropping it from the
    comparison costs no case its sight of `f`.
  - M4, `integration_store` placed before `reranker`: the status case is red (the whole tuple is pinned).
  - M5, `integration_store` read:false but left out of `not_read`: the status case is red.
  - M6, `tickets.ready` dropped from `not_read`: the status case is red.

## Per file
1. **`tests/acceptance/W2-131/test_w2_131_unchanged.py` (8893ad5b0).**
   - Kept its point: **yes**. `FOLDER_KEY = "f"` is added and `_without_store` drops `s` and `f`. The `_place`
     equality, the `FIELDS` comparison, the register-id handling and `_account_for_the_store_key` (which reads the raw
     token's `s`, never stripped) are unchanged. The one-commit-per-question check still reads `s`. M1 and M2 caught.
   - Only `f`: **yes**.
2. **`tests/acceptance/W2-133/test_w2_133_unchanged.py` (d92b61bf5).**
   - Kept its point: **yes**. `_token` drops `s` and `f`; `_comparable` and the gap-label and status assertions are
     untouched. M1 and M2 caught.
   - Only `f`: **yes**.
3. **`tests/acceptance/W2-135/test_w2_135_unchanged.py` (67aa2d12b).**
   - Kept its point: **yes**. `_without_store` drops `s` and `f`, and its docstring now names both. The cut-line and
     cut-key comparison, `_commit_of`, the `<= 1` commit check and the reranker-input case are unchanged. M1, M2 and M3
     caught.
   - Only `f`: **yes**.
4. **`tests/unit/retrieval/test_w2_131_register_ids.py` (3ad7ce713).**
   - Kept its point: **yes**. `_without_s` adds `payload.pop("f", None)`, and the docstring names it. The register-id
     assertions (`was["id"] == "DEC-999"`, `now["id"] == entry or chunk_id`, `register_items >= len(CALLS)`) are
     untouched. M1, M2 and M3 caught.
   - Only `f`: **yes**.
5. **`tests/unit/retrieval/test_w2_133_gap_label.py` (56930ce1a).**
   - Kept its point: **yes**, the same one-line change. M1, M2 and M3 caught.
   - Only `f`: **yes**.
6. **`tests/unit/retrieval/test_w2_135_item_cap.py` (cd2324e06).**
   - Kept its point: **yes**, the same one-line change. `_comparable` drops `evidence` and strips the token as before.
     M1, M2 and M3 caught.
   - Only `f`: **yes**.
7. **`tests/unit/status/test_status.py` (6666cec2c).**
   - Kept its point: **yes**.
     - `PARTS` gains `integration_store` after `reranker`, the code's position, and the whole tuple is still compared
       with `==`.
     - `not_read` with the store present is compared with `==` to the one exact entry the code gives today (the
       project names no integration store).
     - Without the store, the list of places is compared with `==` to `[tickets.ready, tickets.blocked,
       decision_packages, integration_store]`, in that order.
     - No subset, no `in`, no filter. M4, M5 and M6 caught.
   - Only `integration_store`: **yes**.

**Dropping `f` stays inside the before/after comparisons.** In all six token files the stripped form is used only to
compare a token from the code before the ticket's fix with one from today's code; the brief's "two folders" is
"two code versions" in these cases. The old code's token never had `f`, so dropping it on both sides equals ignoring
the new key. Wherever a token is used again (`continuation=...`), the new code still checks `f` (M3). No case that
should see `f` loses it.

## Findings
None that fails the probe.

## Rows
- **R-1, stale inline comments (out of scope for a round, cosmetic).** The comments beside the comparisons in the three
  unit files still say "without its s key", although the helper now drops `f` too:
  - `tests/unit/retrieval/test_w2_131_register_ids.py:188` and `:208`
  - `test_w2_133_gap_label.py:169` and `:190` (approximately)
  - `test_w2_135_item_cap.py`, beside lines 359 and 391 (approximately)

  The helper's docstring is correct. Found by reading.
  - Ordinary work: yes, because a reader could take the comment as the whole story; the helper's docstring corrects it.
  - Consequence: other.
  - What would reverse it: the comments already naming `f`, or the brief excluding comments from the revision
    (it does: "comments and docstrings naming them aside").
- **R-2, no case in this file now pins a fully-read status answer (`not_read == []`).**
  - What changed: in the unit fixture the integration store is never configured, so the first assertion now pins
    `not_read == [the integration_store entry]` instead of `[]`. A grep of `tests/` finds no other case asserting an
    empty `not_read`.
  - Why it is not a failing finding: the order asked for this ("`not_read` stays asserted as the code's behaviour now
    is"), and the exact-list assertion still fails on any other part wrongly read or not read (M5, M6).
  - Why it might matter: a future case that plants an integration store could restore the "all read → empty"
    guarantee.
  - Ordinary work: yes, because a change that made a configured, readable integration store show as not read would
    not be caught by this case. W2-116's own S2 cases cover the configured store.
  - Consequence: other. The answer still says what it did not read; nothing fails open in the code.
  - What would reverse it: a case elsewhere that asserts `not_read == []` for a project with every part readable,
    including a configured integration store.
- **R-3, the status case pins the reason's wording.** `"integration_store: governance/project/rebuild.yaml names no
  integration_store: there is no integration store"` is compared exactly, so any rewording of that message turns this
  W1-32 builder case red. This is tighter than before, not looser, and it is what the order asked for.
  - Ordinary work: yes, because an engineer rewording the message would hit it.
  - Consequence: other. The test is red and the cost is a revision; nothing passes when it should fail.
  - What would reverse it: the owner or CTO preferring exact pinning of the reason (the order's "as the code's
    behaviour now is" reads that way).

## Verdict
**pass.** Each of the seven files changes only `f` (six files) or `integration_store` (one file). The 17 cases red
before are green after, and every case still fails on the plausible wrong change it guards (6 of 6 mutants caught).

Classification: 0 findings; 3 rows (R-1, R-2, R-3), each in-scope-adjacent, ordinary work yes, consequence other; none
blocks.

```verdict
{"kpis": [{"kpi": "R2-F3", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}]}
```
```