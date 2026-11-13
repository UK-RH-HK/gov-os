---
type: probe
task: DAEO-6n5k
kind: narrow independent check of P-7 (a) (DEC-812 item 6) and the _CBM_SUITES line (DEC-1156 (7)), the change since 7bde87727b0f (not a round, DEC-1010)
reviewer_session: ef5bb7a5-2647-49c1-9fdb-55632b229013 (independent-auditor, claude-opus-5-5, high, C2)
implementer_session: ddcfdb7d-05e8-4eea-9c88-918695904777 (eng-6, engineer; td-6 7f50970e-3c34-46a6-a40f-90048638d39e)
implementers: eng-6 ddcfdb7d-05e8-4eea-9c88-918695904777 (engineer; 5915e5c9a); td-6 7f50970e-3c34-46a6-a40f-90048638d39e (independent-test-designer; df75fbd10, merged 9f4878987)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 9f4878987af8622766c4e53846dc665482c91947
date: 2026-11-13
decisions_applied: [DEC-812, DEC-1156, DEC-1010, DEC-801, DEC-808, DEC-809]
---

# Narrow check: P-7 (a), DEC-812 item 6

The reviewer's section and verdict block, as returned (brief: briefs/rev-6.md, carrying governance/project/briefs/JUDGEMENT.md word for word).
Lead's triage: N1 (count case not renamed; tests/optin-lifted-breadth.txt:42 outside the paths) is in scope, ordinary work yes, consequence other: a row, not a round (DEC-1010 item 1). Not decided away: it is returned to the CTO with the rename's cost.

## Narrow check: P-7 (a), DEC-812 item 6

The rule's status: DEC-812 is DONE (owner, DEC-1098 (3)). Nothing in the register supersedes item 6 (searched for `DEC-812 item 6` and `supersed.*DEC-812`).

1. **Sound: the diff.**
   - Command: `git diff 7bde87727b0f 9f4878987 -- src/gov/check/commands.py tests/conftest.py tests/acceptance/W1-07 tests/acceptance/W1-32`
   - `commands.py` gains one line, `RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("impact",)` with a comment. No other command and no other line changed.
   - `conftest.py`: `_CBM_SUITES` gains `"W2-37"` only.
   - `w1_07_support.py` gains a comment and `+ ("impact",)`.
   - The count case's sorted list gains `"impact"`. Its other changes are comments and a docstring paragraph.
   - W1-32's first assert gains `"impact"`.
   - The README adds one revision paragraph.
   - Nothing is weakened. W1-32's other changes in that range (`RECORDED_HERE`, `- set(RECORDED_HERE)`) came from W2-182 (6e3697785, `Task: DAEO-5y8d`, `Rewrite-Reason: DEC-1163 (6)`) through the integrate merge. They are not part of this change.
   - The merge f141d6366 has parents 7bde87727 and 730477098. `git diff --stat 730477098 f141d6366 -- <six files>` is empty, and 6e3697785 is an ancestor of 730477098. So the merge holds these files exactly as w2/integrate held them.
   - `git diff --stat f141d6366 9f4878987` shows only the six files, 23 insertions and 3 deletions.

2. **Sound: trailers and paths.**
   - 5915e5c9a: `Task: DAEO-6n5k`, `Role: engineer`, `Implements: CAP-33.g, DEC-167`. It touches commands.py and conftest.py.
   - df75fbd10: `Task: DAEO-6n5k`, `Role: independent-test-designer`, `Implements: CAP-33.g, DEC-167`, `Rewrite-Reason: DEC-812 item 6, P-7 (a)`. It touches the three W1-07 files and the W1-32 file.
   - 9f4878987, the lead's merge: `Task: DAEO-6n5k`, `Role: orchestrator`.
   - Every `Implements:` id is in the ticket's `sources:` (CAP-33.b, CAP-33.g, DEC-167, DEC-1083).
   - All six files are in the ticket's `allowed_paths` (lines 26 to 31 of DAEO-6n5k.md).

3. **Sound: the tests.** Command:
   ```
   heavy_slot.sh python3 -m pytest tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-32 tests/acceptance/W1-26/test_w1_26_recorded_commands.py tests/unit/check tests/unit/optin/test_optin_lifted.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed --optin=breadth -rfs
   ```
   Output: `454 passed in 181.92s`, exit 0. A collect-only run confirms the three `[impact]` cases and both count cases are selected.

4. **The reason is true; the departure is N1, a row.**
   - `tests/optin-lifted-breadth.txt:42` names `test_w1_07_recorded_commands.py::test_the_recorded_commands_are_four_and_none_is_one_of_the_twelve  # cap`.
   - `tests/unit/optin/test_optin_lifted.py:178` (`test_every_entry_of_the_real_lists_names_a_test_path_or_function_that_exists`) parses each listed file with `ast` and fails with "(no such function)" on a missing name.
   - That list is not in the ticket's `allowed_paths`. Renaming the case alone would turn the opt-in test red, so it would fail closed. Leaving the old name is the only green choice inside this ticket's paths.

5. **Sound: anything else.**
   - Adding `impact` to `GOV_COMMANDS` makes `check()` require `src/gov/impact/command.py`, which exists.
   - It also lets skills name `gov impact`, which the change skill (SKILL.md:48) already does. That is the intended effect of P-7 (a).
   - The three `RECORDED_GOV_COMMANDS` lists (commands.py, W1-07's support, W1-32's first assert) agree on `impact`.

**Finding N1: the count case is not renamed.**
- Setup: DEC-812 item 6 says "its count test renamed".
- Fault: `test_the_recorded_commands_are_four_and_none_is_one_of_the_twelve` keeps its name while it now pins ten commands. The comment in the case and the README paragraph both state why.
- What should happen: rename it in the same change as `tests/optin-lifted-breadth.txt:42`.
- Scope: in, because it is the text of DEC-812 item 6.
- Ordinary work: yes, because any reader of the suite sees a name that says "four" over an assertion of ten.
- Consequence: other. The case still pins the exact ten, so nothing fails open and no work is lost. A rename without the list line would fail closed.
- What would reverse it: an owner or CTO reading that DEC-812 item 6's rename is satisfied or waived, or the rename landing with the list line.

Classification (DEC-809): N1 is in scope, ordinary work yes, consequence other, so it is a row and not a round.

**Judgement: pass.**

```verdict
{"kpis": [{"kpi": "w2-37-p7a-dec812-6", "verdict": "pass", "findings": [{"id": "N1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}], "reviewer": "independent-auditor, fresh read-only session; not the author"}
```