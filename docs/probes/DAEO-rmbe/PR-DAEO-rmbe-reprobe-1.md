---
type: probe
task: DAEO-rmbe
reviewer_session: cd4b8e11-e2aa-495a-add9-458909c90db3
implementer_session: 00af067b-d55b-4467-8332-ca3d002f72d1
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 06df14f32d0678537d238ef83390b3be7bc7540e
---

# Probe record: W2-69 (DAEO-rmbe), judgement-only re-probe after W2-74's merge (DEC-895)

- **What was probed.** Head `06df14f32d0678537d238ef83390b3be7bc7540e` of `w2/W2-69`: the lead's merge of `w2/integrate` (`b99c75ce1700`) into the ticket's branch, made for this re-probe. This was a judgement-only re-probe (DEC-895, DEC-926), not a new review round. Its scope was every file that the earlier probe judged and that changed between that probe's head `e00fd14a26be` and this head. It asked one question: does any change alter what the earlier probe found, or let the check pass something it refused?
- **Why.** The earlier record, `PR-DAEO-rmbe.md`, is the third and last review's record (DEC-909), a pass at `e00fd14a26be`. It went stale when W2-74's merge (`6ee7b4d02843`, DEC-925 item 1) changed two files it had judged. The earlier record stays as it is.
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, session `cd4b8e11-e2aa-495a-add9-458909c90db3`, 2026-10-27, effort max. It was started through `gov launch` under its OS sandbox with the reading tools alone. The ticket lead, an orchestrator-role session (DEC-137), commissioned and judged it. It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree or in any other tree.
- **Step 0.** The write outside the worktree was refused (read-only file system). `git hash-object -w` and `git update-index --refresh` worked. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-69/src/gov/__init__.py`. Read refusals: 0.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only "yes" with "fails open" or "loses work" fails the probe.
- **Verdict: pass.** Classification (DEC-809): F1, the renamed case's failure output, is yes / other. No finding is "yes" with "fails open" or "loses work", and no change in scope lets the check pass anything it refused at `e00fd14a26be`. The lead's judgement agrees. F1 is a row: it fails closed, and W2-71's card already aims at the cause.
- **The earlier record's findings and classification stand.** They are: wrapped key word (no / fails open); double-spaced block (no / fails open); many markers (no / other); vanished file (yes / other). No change in scope touches them. The code under test, the check's declaration and the gitleaks configurations are unchanged since `e00fd14a26be`.

## The judged files that changed

How the list was computed: 24 non-merge commits with the trailer `Task: DAEO-rmbe` up to `e00fd14a26be` touch 41 files, and 170 files changed between `e00fd14a26be` and the head. Three files are in both. The lead and the reviewer computed the list separately and found the same three.

1. **`tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py`** (W2-74's commit `1ebb6f0f96aa`, an independent test designer's, with `Rewrite-Reason: DEC-911`).
   - **What changed:**
     - The code-search vendor's access-token rule's name became a named constant, written in two string parts that Python joins.
     - A one-entry map gives that rule's case the id `code-search-access-token`.
     - The premise test's parametrize decorator gained an `ids=` callable.
   - **Compared from both versions** (Python's `ast` on `git show` copies):
     - the rule tuple holds 68 values in both, element-wise equal, in the same order, with no duplicates; the renamed rule is at index 63 in both;
     - the no-case table (3 entries) and the project rules (4) are equal;
     - the premise test's body and arguments are identical, and both versions have 8 test functions.
   - **At the head:**
     - Collection gives 132 cases. The 68 premise ids equal the rule names, except index 63, and no id holds a keyword of row W2-L423's rule.
     - The file's run gives 132 passed, none skipped. The renamed case still requires gitleaks to report the rule by its full id for the built token, and no finding for the word-internal form, so it cannot pass vacuously.
   - **Effect:** none on the earlier findings, and the check is let pass nothing.
2. **`tests/acceptance/W2-69/README.md`** (same commit).
   - **What changed:** one table row now notes the renamed case, and a new paragraph, "Renamed case", explains it.
   - **Unchanged:** every expectation, count and "red today" statement.
   - **Its claims hold:** the values, their order, the input and the assertions are unchanged, and no other test id holds a keyword.
   - **Effect:** none on the earlier findings.
3. **`docs/plan/WAVE_2_WBS.md`.**
   - **What changed:** 63 lines added and none removed:
     - a round-2 note in W2-07's card;
     - three allowed-path lines in W2-57's card;
     - four new cards, W2-71, W2-72, W2-73 and W2-74.
   - **W2-69's card** is byte-identical.
   - **W2-71** aims at this ticket's code: it would exempt row W2-L423's rule when the 40-hex match names a commit of this repository. It starts only once no ticket in flight holds `src/gov/secrets/`. It is not in this head, and it changes no rule W2-69 relies on.
   - **Effect:** none on the earlier findings.

Blob ids show that only W2-74's commit changed the two test files. No merge altered them.

## Findings

### F1: when the renamed case fails, its report still holds the rule's full name (severity: low)

- **What was done:** the reviewer read the premise test after the rename and followed what a failure of the renamed case would write into the run's report.
- **What happened:**
  - The rename takes the keyword out of the test id, so a passing run's report holds none.
  - The case's parameter value is still the rule's full name, and a failure message prints it. So do pytest's explanation of a failed membership assertion and the suite's other tests over the same tuple.
  - So a failing run's JUnit report under `.gov-runtime/` would hold the keyword again. Beside a full 40-hex hash in the same file, the secrets-indexing check would turn red.
  - This was reasoned from the code, not reproduced: making the case fail needs another gitleaks or a changed test.
- **What should have happened:** a failure report of this suite holds no keyword of row W2-L423's rule either, or the check no longer takes a real commit hash of this repository for that rule's token (W2-71's card).
- Ordinary work: yes, because a gitleaks upgrade that changes the code-search rule makes the premise case fail in an ordinary run.
- Consequence: other (it fails closed: a red check beside a test that is already red; nothing is let through and no work is lost)

## Probed and found sound

1. **The judged-file list:** recomputed from parsed trailers and the head's diff. It holds the same three files, with no renames among them.
2. **Same rule, same input, same assertions:** the renamed case tests the same rule with the same input and the same assertions. Only `ids=` was added.
3. **No case lost, skipped or vacuous:**
   - 132 collected and 132 passed;
   - no conftest selects, skips or deselects by id;
   - the serial-only list does not name this file.
4. **Nothing newly accepted:** no acceptance test of this ticket now accepts a store or file it refused at `e00fd14a26be`. These are all unchanged:
   - the ticket's code (`src/gov/secrets/`, `src/gov/rebuild/command.py`);
   - its unit tests and research note;
   - the tests' inputs and assertions;
   - the check's declaration, `template/.gitleaks.toml` and the template path map.
5. **The runner change does not reach these tests:**
   - W2-59 changed `src/gov/check/runner.py`. A declared `python3` or `gov` command now runs with the judge's own interpreter and `-P`, and the runner no longer adds the project's `src/` to `PYTHONPATH`.
   - This ticket's acceptance tests run the declared command themselves, with this worktree's `src/`.
   - At a real `gov check` without `PYTHONPATH`, the pinned judge's secrets check runs. So this ticket's check counts at a close only once the pin carries it, by design (DEC-822, DEC-835).
6. **The other merged source changes are off the check's and the rebuild's path.** These are the changes in `gov.cli.main`, `gov.close.*`, `gov.guard.containment*`, `gov.hooks.subagentstop` and `gov.retrieval.*`. None is imported by `gov.secrets`, by `gov.rebuild.command` or by the rebuild's lazy imports.
7. **Nothing written:** the reviewer wrote nothing in the worktree. Its run used `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`.
