# Lead brief: fix-select, `gov queue`'s selection: I-1 (a deleted test is not a selected target) and I-2 (a record-only document a branch writes is placed with a notice) (fixes under W2-115b, `DAEO-j9z6`)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (its test command, with node on PATH; the test
designer's reading bounded). Name: `fix-select`; worktree `/home/usain/gov-os-worktrees/E2-fix-select`, branch
`e2/fix-select` from `w2/integrate`. **Do not merge.** Every helper Sonnet; this lead runs medium (DEC-1236 (2)). It must
be green **within about 90 minutes**: I-1 rides release 0.1.5 before its version commit (DEC-1239 (1)); if I-2 would
delay that, finish I-1, commit, and say I-2 is left.

**The findings** (`docs/emergency-2/integration/FINDINGS.md` I-1, I-2; DEC-1239):
- **I-1:** `src/gov/close/select.py` `scoped()` adds every changed path since the last green record that is a test file
  as `TEST_CHANGED` (about `:796-798`), including a test file the change **deleted**; `unresolved()` (`:315-332`) then finds
  it gone and the selection refuses `SELECTION_REFUSED ... FILE_GONE` (`:841`). On 2026-11-22 every `gov queue` landing
  after `e2/models-rubric` deleted `tests/acceptance/W2-201/test_w2_201_s9_substitution.py` refused this way. The fix: a
  path the change deleted (absent from the tree at HEAD) is never selected as a target; it is listed (for example under
  `deleted` in `--select`'s object) and its suite folder still runs if the folder remains. A target the test map names
  (couplings, `every_close`, `record_reading`) that is gone still refuses as today (DEC-912 item 3).
- **I-2:** a document the branch itself writes that no suite, coupling or ticket places refuses
  (`SELECTION_REFUSED ... nothing maps to a suite`, the `UNPLACED` path in `scoped()`). The owner's decision: "a record-only
  document a branch writes is placed as a record with a notice at the landing, never refused." Define record-only by the
  test map's own notion (a path under the record roots the map's `record_only` patterns cover, plus Markdown documents
  outside `src/`, `tests/` and the kit's executable parts; say exactly which rule you choose and why); such a path goes to
  `records` with a notice (`RECORD_PLACED <path>`) in `--select`'s object and the landing's record; code and tests the
  branch writes that nothing places still refuse.

## The flow and green
Test designer first (red on the base: a planted repository whose change deletes a test file; one that writes an unmapped
`docs/x.md`), then the engineer. `gov accept W2-115b` green; `tests/unit/queue`, `tests/unit/close`, `tests/acceptance/W2-115`,
`tests/acceptance/W2-115b`, `tests/acceptance/W2-202`, `tests/acceptance/W2-206`, `tests/unit/optin`. Record each fix in
`.tickets/DAEO-j9z6.md` as a `## Fix:` section. Return: branch and head; I-1 and I-2 each with tests; reds not yours.
