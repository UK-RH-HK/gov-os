---
type: probe
id: PR-DAEO-o5x1
task: DAEO-o5x1
reviewer_session: 57de2180-58f9-4a52-8041-8b7e6f345469
implementer_session: 57fb2b5d-d97e-4e6c-9399-68c22586d1f7
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 09fc68645c0c36580f94077e37255ca511c4b3c2
---

# Probe record: W2-152 (DAEO-o5x1), review round 2, the last (DEC-1010)

- **Probed:** head `09fc68645c0c` of `w2/W2-152` (the fix round for round 1's F1, F3, F4, F6 and F5), against
  `w2/integrate`. Round 1 (`16d052d2fda7`) was NOT READY on F1: `governance/project/orchestration/reviews/w2-152-r1.md`.
- **Reviewer:** a fresh independent-auditor session (session above; `gov launch`, OS sandbox, read-only), launched by
  the CTO on 2026-11-09 with the brief `.gov-runtime/scratch/brief/W2-152-review-r2.md`. It wrote nothing in any tree;
  the tripwire showed no change in this worktree (changes only in other trees, by their own sessions).
- **Implementer:** the fix-round engineer (session above); the first build was session `a9809203-73a6`.
- **Commissioned and judged by:** the orchestrator. The reviewer's verdict is READY; the judgement `pass` is the
  reviewer's own, computed from its `verdict` block below (no finding that is in scope, ordinary work yes, and fails
  open or loses work; DEC-1010 item 1). No verdict is written over the reviewer's.
- **After the probe:** the CTO merged `w2/W2-152` (`b0bbd373f8a3`) and the designer's tests branch (`dea78270a`) into
  `w2/integrate`; the branch then took `w2/integrate` back twice (`6dc3db850050`, `e25bdca86bc1`), both merges made by
  git without a conflict. In the ticket's own paths the only change after the probed commit is the designer's
  `32b89d25a578`: one comment line in `tests/acceptance/W2-152/test_w2_152_rev2.py`, so that `gov links` reads no
  planted id as unknown; no test's behaviour changed. The branch's tree at `e25bdca86bc1` is `w2/integrate`'s tree at
  `33b5651eb65d`. No re-probe is due (DEC-895: no merge resolved a conflict in a judged file). The ticket's profile is
  STANDARD. The lead's resume on 2026-11-12 tried a re-probe of the merged head, as the CTO's brief asked; the launcher's
  resource gate refused it twice (memory, DEC-1088 (5)), and the lead stopped there (DEC-1142 (9)).
- **The lead's verification of `e25bdca86bc1` (2026-11-12):** rebuild exit 0; `gov accept W2-152` 67/67 (every KPI
  line pass); the scoped selection (scoped, `core_changed` none, `unplaced` none) 4168 passed, 3 failed in the parallel
  phase, 90 passed in the serial phase. The three reds are not this ticket's: W2-153's two composition cases (red on
  `w2/integrate` until W2-175 merges; the branch's tree is integrate's) and W2-157's load-sensitive backstop case
  (passed alone).
- **Findings left as rows (Wave 3), as the reviewer and the CTO class them:** F7 to F12 (round 1), F13, F14, F15
  (round 2). F2 was decided by the CTO as option (a). None blocks.

## The reviewer's record, verbatim (its session's final message)

**W2-152 round 2: READY.** F1, the only finding that blocked in round 1, is closed. Every line from S1 to S10 and F1 to F3 passes, and nothing open is in scope, ordinary work and fails open or loses work.

**Sandbox check (step 0):**
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-152` failed with `OSError: [Errno 30] Read-only file system`, as it should.
- (b) `git hash-object -w --stdin` worked (blob `1ae28402a109`, the same blob as round 1). `git update-index --refresh` worked (rc 0). `GOV_TICKET=DAEO-o5x1`.

**`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (rc 1).

- **task:** W2-152 (DAEO-o5x1), the independent review, round 2 and the last (DEC-1010). Branch `w2/W2-152` at `09fc68645`, against `w2/integrate`.
- **status:** DONE. Verdict: **READY**.
- **work_completed:**
  - **Read:**
    - EMG-d4b-launched, EMG-common and JUDGEMENT.md.
    - The ticket in full, including "Interface" and "Clarified after the test design".
    - The round 1 record. It is not in this worktree; I read it from commit `260e70bd1`.
    - The fix diff `09fc68645`: `build.py`, the facts schema and the evidence file.
    - `build.py`, `command.py`, `__init__.py` and `util/frontmatter.py` in full.
    - `role-lead.md`, `facts.yaml` and the revision 2 cases (`test_w2_152_rev2.py`).
  - **Ran:**
    - The two test folders, read-only.
    - 61 probes on throwaway fixture repos in my TMPDIR, built from this tree's real templates and facts.
    - A schema validation of `facts.yaml`.
- **files_changed:** none in any tree.
  - `git status --short` is empty.
  - Every bytecode cache predates my session (21:26–21:49); my runs used `-B` and `PYTHONDONTWRITEBYTECODE=1`.
  - The ignored dotfiles (`.bashrc` and the like) are the sandbox's own placeholder device files, dated 2026-11-03.
  - The only write outside my TMPDIR is step 0's git blob, which the brief requires.
- **evidence:**
  - Probe script: `/tmp/gov-launch-independent-auditor-89ctelb7/claude-1000/-home-usain-gov-os-worktrees-W2-152/57de2180-58f9-4a52-8041-8b7e6f345469/scratchpad/probe.py`.
  - Scratch use was 2.1M and 490 inodes. I removed it after the run.
  - One probe miss was my own error: the line I planted after "## Hand-over" was glued onto the heading ("Hand-overUntil"), so the word boundary failed. It shows nothing about the code; the plants in the other three sections were refused.
- **tests:**
  - Command: `pytest tests/acceptance/W2-152 tests/unit/brief -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`, with an empty `HOME`, `PYTHONUSERBASE=/home/usain/.local` and `PYTHONPATH=<tree>/src`.
  - Result: **92 passed** (67 acceptance + 25 unit), which matches the CTO's 67/67 and 25/25.
  - The exclusion left nothing out: nothing was deselected.
  - The S10 guard case inside that run (`gov accept W2-128`) passed.
  - `facts.yaml` passes the schema, and the schema now lists `ready` as required.
  - I did not run `gov accept W2-152` itself; I rely on the CTO's 67/67.
- **discoveries:**
  1. F1 is closed. `build.py:352` now scans T-0's whole text, the whole role template for every role, and `--part`.
  2. A directory named `*.md` (or a ticket file that cannot be opened) in `.tickets/` still crashes a lookup by W2 id with a traceback. The cause is `_w2_of_unreadable` at `build.py:81`, which reads outside any `try`. This is F13, a row.
  3. A ticket that starts with a byte-order mark (BOM) is read as having no front matter. It is refused under the wrong names, `ALLOWED_PATHS_EMPTY` and `KPI_NO_VERIFY kpis`. This is F14, a row.
  4. A ticket with no `created` field is never held to the dependency fields. The evidence file records this as a choice. This is F15, a row.
- **risks:** Once W2-56 closes, every `gov brief lead …` refuses with `UNTIL_CLOSED W2-56` until W2-128's `role-lead.md:27` is edited. That is S5 working as intended; whoever closes W2-56 should know it is coming.
- **lessons:** Revision 2's plant in the lead's common part is what makes F1 testable. My probes confirm the code is general, not fitted to that one spot: plants in front matter, in the end of each worker template, and in three sections outside the run block were all refused.
- **proposed_decisions:** none. F2 was decided by the CTO as option (a); F7–F12 stay rows.
- **unresolved:** none.
- **recommended_next_action:** Treat W2-152 as READY: take it to the merge queue, and take F13, F14 and F15 as Wave 3 rows alongside F7–F12. If they want, the CTO can fold F13 (one `try` at `build.py:81`) into W2-153.

### Round 1's findings re-checked

**F1 is closed.** I tested this tree's real templates with a planted W2-56 ticket (DAEO-wnnz):
- **W2-56 open:** the engineer and all five lead run kinds exit 0, so there is no false refusal.
- **W2-56 closed:**
  - all five lead run kinds (`tests`, `build`, `review`, `resume`, `land`) refuse with `UNTIL_CLOSED W2-56`, by tk id and by W2 id. The line comes from `role-lead.md:27`, which sits in "## Every run", the common part outside the run block;
  - the five worker roles exit 0. Their templates hold no "until" line.
- **Planted "until <closed ticket>" lines:** all refused:
  - at the end of `role-engineer`, `role-reviewer`, `role-product-spec` and `role-research`;
  - in the front matter of `role-test-designer`;
  - in `role-lead`'s "Each worker return", "Return" and step lines;
  - in a role template whose front matter is invalid;
  - in a `--part` file.

**F3 is closed.**
- No `ready` key, `ready: []` and `new_since: null` all give `READY_NEW_SINCE_MISSING ready.new_since`.
- `"soon"`, `"2026-13-45"` and `20261110` all give `READY_NEW_SINCE_NOT_DATE`.
- An unquoted YAML date and a timestamp are accepted.

**F4 is closed.** `kpis` missing, a list, or a string, and `success` empty or missing, all give `KPI_NO_VERIFY kpis`. A `{line, verify: ''}` item gives `KPI_NO_VERIFY S1`.

**F6 is closed.** An unclosed block, a quoting slip in the title (by tk id and by W2 id), and front matter that is a list all give `TICKET_UNREADABLE <ref>: front matter unclosed|not_yaml|not_mapping` alone, with no `ALLOWED_PATHS_EMPTY`.

**F5 is closed** for each case round 1 named:
- A ticket that is not UTF-8 gives `TICKET_UNREADABLE … not UTF-8`, by tk id and by W2 id.
- Another such ticket in `.tickets/` no longer breaks a lookup by W2 id (exit 0).
- facts.yaml with bad YAML or not UTF-8 gives `BRIEF_FACTS_UNREADABLE`.
- `keys.yaml` with bad YAML, a role template that is not UTF-8, and a `--part` or `--repair` file that is not UTF-8 all give `BRIEF_FILE_UNREADABLE`.
- None of these prints a traceback, and a refusal prints 0 bytes on stdout.
- CRLF line endings are read fine.
- A dependency on an unreadable ticket gives `DEPENDS_NOT_CLOSED`.
- The residual cases are F13 and F14 below.

**Nothing else regressed:**
- **S1:** two runs are byte-identical, and a relative `--root` gives the same bytes as an absolute one.
- **S4:** 0 role-template lines appear in each of the five worker briefs.
- **S6:** each lead brief carries only its own block, and line 27 is absent from the brief. So the stdin brief is unchanged; the scan is wider, the output is not.
- **S7:** turning off `guard_refusal_lines` removes exactly its one line.
- **The ready check's split** (`ready_check`, `build.py:154-183`): the fix only adds the `kpis` refusal at `:160-162`. `NON_GOALS_MISSING` and `EST_LOC_OVER` still only warn.

### Verdict per line

| line | verdict | notes |
|---|---|---|
| S1 | pass | No clock and no environment read; `datetime` is used only to parse the date. Byte-identical runs; the golden files pass. |
| S2 | pass | `PLACEHOLDER_LEFT` and `KPI_NO_VERIFY S/F<n>` are named. F2 was decided as (a). F7 is a row. |
| S3 | pass | Warnings and `SIZE` go to stderr and never refuse. F8 is a row. |
| S4 | pass | 0 role-template lines in the worker briefs; a lead brief has only its block. |
| S5 | pass | F1 is closed (probes above). F11 is a row. |
| S6 | pass | One block per kind; `BRIEF_RUN_MISSING` is unchanged. |
| S7 | pass | One line removed, nothing else changed. |
| S8 | pass | F4 and F6 are closed. F9, F13 and F14 are rows. |
| S9 | pass | F3 is closed. F10 and F15 are rows. |
| S10 | pass | The schema requires `ready`; `new_since` has `format: date` and a pattern. The W2-128 guard case passes. |
| F1 | pass | Same as S1. |
| F2 | pass | Advisory items only warn. A missing `kpis` now refuses (F4 closed). |
| F3 | pass | The tree is unchanged after my runs. The extra raw read is of ticket files only. F12 is a row. |

### Findings still open (none blocks)

**F2: `gov brief` refuses every in-flight ticket.** S2, S8; scope: in.
- The CTO decided it as option (a): in-flight tickets get Verify lines before their first `gov brief`.
- Ordinary work: yes, because it hits every real ticket.
- Consequence: other (it fails closed).
- Evidence that would reverse it: the owner overturning the CTO's decision.

**F7, F8, F9, F10, F11, F12:** kept as rows, as the CTO decided. I re-checked each against the code at `09fc68645`; none is changed:
- F7 is at `build.py:215`; F8 at `:267-276`; F9 at `:164`; F10 at `:175`.
- F11: `UNTIL` at `:23` still misses backticked and bold ids.
- F12: `_w2_of_unreadable` adds a raw read, but only of ticket files.
- Each keeps round 1's two lines and its scope.

**F13 (new): a traceback on an unopenable `.tickets/*.md` during a lookup by W2 id.** `build.py:79-81,95`; scope: out (F5's own scope was out).
- `_w2_of_unreadable` calls `path.read_bytes()` outside any `try`. A directory named `X.md`, or a ticket file without read permission, makes `gov brief <role> W2-…` crash with `IsADirectoryError` or `PermissionError`.
- Related: `Tickets.load` (`:63-64`) labels any `OSError` as "not UTF-8".
- Ordinary work: no, because tk writes only plain files that can be read.
- Consequence: other (it fails closed, with a traceback).
- Evidence that would reverse it: such an entry appearing in `.tickets/` in normal flow.

**F14 (new): a ticket that starts with a BOM is refused under the wrong names.** `build.py:62,71-72`, with `frontmatter.py:35`; scope: out.
- The first line is `\ufeff---`, which is not `---`, so the ticket reads as having no front matter. It is refused as `ALLOWED_PATHS_EMPTY` and `KPI_NO_VERIFY kpis`, not `TICKET_UNREADABLE`.
- Ordinary work: no, because tk and this repository's editors write no BOM.
- Consequence: other (it fails closed, under the wrong reason).
- Evidence that would reverse it: a ticket with a BOM appearing in normal flow.

**F15 (new): a ticket with no `created` is never held to the dependency fields.** `build.py:167-168`; scope: in (S9).
- `_day(None)` is None, so the `reads`/`needs`/`waits_on` check is skipped with no warning. This is the same kind of silent switch-off as F3, on the ticket side. The evidence file records it as a choice.
- Ordinary work: no, because tk writes `created` on every ticket.
- Consequence: fails open.
- Evidence that would reverse it: a ticket without `created` reaching `gov brief` in normal flow (for example, written by hand). The fix would be to refuse with something like `CREATED_MISSING`.

**Closed since round 1:** F1, F3, F4, F5 (apart from the F13 and F14 residuals) and F6.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S3", "verdict": "pass", "findings": [{"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S4", "verdict": "pass", "findings": []},
 {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F11", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "S7", "verdict": "pass", "findings": []},
 {"kpi": "S8", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F9", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F13", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F14", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S9", "verdict": "pass", "findings": [{"id": "F10", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F15", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S10", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": [{"id": "F12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
