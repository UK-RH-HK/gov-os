---
type: probe
task: DAEO-zlog
ticket: W2-188
round: 'narrow check (DEC-1156 (7)), not a review round'
reviewer_role: independent-auditor
reviewer_session: ab68d9eb-ea28-460e-b9fb-426c2b6afb19
implementer_session: "independent-test-designer td-2 89e126ad-a0a4-4e13-8278-b5c7199cf15e (f71c82430, merged 1074c9d04); product-spec ps-5 b6276fec-04df-4439-9a08-fd83fdee2903 (c1c8685b8)"
reviewer_wrote_nothing: true
probed_commit: c1c8685b8079f6011b82e3023e59ff91fdbf5c84
judgement: pass
decisions: [DEC-1157, DEC-1156, DEC-136, DEC-105, CAP-33, DEC-801, DEC-802, DEC-808]
commissioned_by: orchestrator
judged_by: orchestrator
---

# W2-188 (DAEO-zlog): narrow independent check of the S5 re-baseline change

Scope: only the change after review round 1 (`07d7361e7` to `c1c8685b8`). The ticket's S5 and I6 impact clause was
re-baselined by the CTO within purpose (DEC-1157 (12): widenings and KPI edits within a ticket's own purpose are the
CTO's, listed for the owner's reading; P-W2-188-S5 (a), commits 063a35585 and 18a279055, merged as ccc5b3225, the old
text kept beside the new per DEC-105). Two commits followed: the revised S5 impact case (f71c82430, test designer td-2,
merged as 1074c9d04) and the re-worded "W2-11's cases" row of the CIT-P record (c1c8685b8, product-spec ps-5). The
check runs under DEC-1156 (7): a test revision that only records a decided behaviour is the CTO's, under a narrow
independent check.

## 1. The case

- **It checks the clause's three statements, and nothing else.** `test_s5_the_impact_table_says_w2_11_does_not_cover_adopt_adapter_portability_differs_until_the_copies_act_and_w2_88a_unchanged`
  reads the record's table rows, lower-cased with markup dropped, and asks for three things:
  - (1) A row names W2-11 with `adopt`, `body` and `version`, says they are not covered, and says the cases stay as
    they are.
  - (2) A row names `adapter-portability`, `GENERATED_DIFFERS` and `.claude/skills/adopt/SKILL.md`, with `until`,
    `till` or `before` and the word `ACT`.
  - (3) A row names `W2-88a` with `unchanged`.

  These are the clause's three statements (ticket S5 line 44, I6 line 148). The case asks for no line number, no count
  and no case name the clause does not give. The old `W2_11_CASE` constant, which named a case that does not exist,
  is removed. The case checks behaviour as the record describes it, not code (DEC-136).
- **It is not a vacuous pass.** I imported the module in `$TMPDIR` and fed the case altered copies of the record.
  - Current record: passes.
  - Red on each of these: the record at 07d7361e7 (the old W2-11 row); the W2-11 row dropped; the W2-11 row saying the
    cases "cover adopt and go red"; the "Generated copies" row dropped; that row without "until … ACT"; the W2-88a row
    dropped; the W2-88a row saying "revised"; the table turned into prose.
- **No other case touched.** f71c82430 touches only `tests/acceptance/W2-188/README.md` and `test_w2_188_citp.py`.
  In `test_w2_188_citp.py` only the module docstring's IMPACT reading and this one case changed.
  - The W2-61h test files that differ between 07d7361e7 and c1c8685b8 came in with the w2/integrate merge
    (ccc5b3225), not from any commit of this ticket.
  - The folder still holds 54 `def test_` cases. No test names the old case or `W2_11_CASE`.
- **The README map row is true.** The `success-5` row names the renamed case by its full node id, which matches the
  function name. The readings paragraph describes the three statements as the case checks them. The note "count stays
  54, no other case changed" is true.

## 2. The record (`docs/changes/W2-188-CIT-P.md`)

- **Only one line changed.** `git diff 07d7361e7 c1c8685b8` is 1 line out, 1 line in: the "W2-11's cases" row. The
  following are byte-unchanged: front matter, both sha256 values, counts, old and new text, the "Generated copies" and
  "W2-88a's cases" rows, `verdict: PASS` (line 175, still the last verdict) and `owner_approval: 'pending'` (line 13).
- **The W2-11 row is true.**
  - The body case `test_every_copy_carries_the_kernel_skills_body` is parametrized over `test-design`, `orchestration`,
    `audit` and `qa-review` only (`tests/acceptance/W2-11/test_w2_11_skills.py:124`). So there is no `[adopt]` case.
  - The version case `test_the_skill_carries_one_version_in_all_four_places` excludes `adopt` (`:139`,
    `if n != "adopt"`).
  - In `test_w2_11_round2.py`, the only case that excludes `adopt` (`:214`) also excludes it. Its "twin" label is not
    accurate: see N1.
  - "Caught by no W2-11 case (the adapter-portability check reports it)" is true.
  - The past result "276 passed, 1 skipped on `599fa2a22`" was not re-run here.
- **The "Generated copies" row is true at the probed commit.**
  `PYTHONPATH=src python3 -m gov.adapters.portability` exits 1 with exactly one finding: `GENERATED_DIFFERS`,
  ".claude/skills/adopt/SKILL.md", "is not what rulesync generates from its sources". It reports `compared`:
  `rulesync_version` true, 78 kernel files, 93 generated files. These are the row's figures.
- **The W2-88a row is unchanged and true.** It is byte-unchanged. Step 6's text and the three copies are unchanged
  since round 1, so round 1's checks still hold.

## 3. Unchanged bytes

- The kernel copy, `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md` all have sha256
  `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`.
- `git diff --quiet 07d7361e7 c1c8685b8` over the three copies and `docs/research/W2-88-memory-practice.md` shows no
  change.
- `git log 07d7361e7..c1c8685b8 -- .claude/` is empty.

## 4. Trailers

Each commit's trailers stand together as one final paragraph.

- **f71c82430:** `Task: DAEO-zlog`, `Role: independent-test-designer`, `Implements: DEC-1157, DEC-1179, DEC-105,
  CAP-33`, `Rewrite-Reason: DEC-1157 (12), P-W2-188-S5 (a)`, `Co-Authored-By`.
- **c1c8685b8:** `Task: DAEO-zlog`, `Role: product-spec`, `Implements: DEC-1157, DEC-1179, DEC-105, CAP-33`,
  `Co-Authored-By`.
- **Implements:** every id is in the ticket's `sources:` (line 55).
- **Merge 1074c9d04:** `Role: orchestrator`, `Implements: DEC-1157, DEC-105, CAP-33`, all in `sources:`.

## 5. The case against the record

`tests/acceptance/W2-188/test_w2_188_citp.py`, one run through the heavy slot: 6 passed, 1 failed. The failure is
`test_s5_the_owner_approval_line_names_the_after_sha256` (`'pending'`), red by design until the owner's yes. This is
the expected result.

## Findings

### N1. The record's W2-11 row calls the version case's "round-2 twin" the wrong case

The row says "the version case and its round-2 twin (`test_w2_11_round2.py`) exclude `adopt` too". The case in
`test_w2_11_round2.py` that excludes `adopt` (`:214`, `test_every_write_step_lies_in_the_skills_output_class`) checks
a skill's output class, not its version. Round 2 has no per-skill version case. The claim the row rests on, that the
case excludes `adopt` so the bump does not touch it, is true. Only the label is wrong. The phrase was already in the
text round 1 passed, and this change kept it. The row should name the round-2 case as the output-class case.

- Ordinary work: yes, because a reader taking the record as written would look for a version case in round 2 that is
  not there.
- Consequence: other. Nothing fails open and no work is lost; the exclusion claimed is real.
- Scope: in (S5's record). It does not block (DEC-1010). It is a recorded row; the fix can ride along in any later
  edit of the record (DEC-802).
- Reversed by: a per-skill version case in `test_w2_11_round2.py` that excludes `adopt`.

## What I probed and found sound

- The revised case discriminates on each of the three statements and on the table form.
- The test designer touched only the one case, its docstring reading and the README.
- The re-worded row and the "Generated copies" claim hold at the probed commit.
- The skill, its copies, the practice record and `.claude/` are unchanged.
- The trailers are complete and cite only ids in the ticket's sources.
- The red case is the designed one.

Reversal evidence for the pass:
- A table-row wording that meets the clause but that the case marks red, or one that breaks the clause but passes.
- `adapter-portability` reporting more or other findings at c1c8685b8.
- A diff to the skill's copies or to `.claude/` after 07d7361e7.

```verdict
{"kpis": [{"kpi": "S5", "verdict": "pass", "findings": [{"id": "N1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```

verdict: PASS
