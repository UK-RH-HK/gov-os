---
type: probe
task: DAEO-q8cl
reviewer_session: e04c7fb9-50e3-4b4a-a605-1d8c0ca8e43c
implementer_session: "independent-test-designer sessions a4392401-9f78-40f4-85ad-4356962dc905 (commit 35b6ac6bacae9aad1c5277e0cb5ac2b9f8973cd0) and 4709ba2f-1fe8-478a-94f8-83d7434eb53f (commit 6a0b84a81a5905d11bd105ba2c1459be3610cbb9)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 36d4539dbe433c4b27e94d7cb357ec8b79a5363f
decisions_applied: [DEC-1156, DEC-1164, DEC-1073, DEC-1010]
---

# Probe record: W2-130 (DAEO-q8cl), the pin run's narrow independent check (a decided-behaviour test revision)

A fresh independent-auditor session (`e04c7fb9-50e3-4b4a-a605-1d8c0ca8e43c`) ran on `claude-opus-5-5` at high effort, class C2, read-only, with
JUDGEMENT.md word for word in its brief. It probed head `36d4539dbe43` of `w2/W2-130` (the lead's merge of
`w2/W2-130-tests`) and wrote nothing (its tripwire clean; sandbox trial file absent). What it probed: the reopen under
DEC-1164 (18) and DEC-1156 (7) for two decided-behaviour test revisions, made by two independent test designers:
`35b6ac6ba` (W2-130 S8's two cases run `gov links` at the record's pinned tree through `clone_at`, not HEAD; W2-175
S7's sha256 case reads each template at W2-175's landing `61cae50dc` through git) and `6a0b84a81` (the case names the
README maps name kept, the unmapped landing-ancestor case folded into the parametrised one). No record was edited.

Its verdict is **PASS**: five items pass, four findings, none blocking (none in scope with ordinary work yes and
fails open or loses work).

## The lead's judgement of the findings

- **F1** (the cases pin `counts-after.measured_at`, 6b62de94e, where the CTO's decided text names `counts-after.head`,
  57cbacfbf). The lead's measurement: at 57cbacfbf `gov links` gives UNLINKED_ID 1417 and UNKNOWN_ID 57 against the
  record's 1420 and 56, and `left.D-9` differs on five paths, so that pin stays red with the record unedited; at
  6b62de94e every count equals the record, which says it counted that tree, and the ticket's S8 Verify reads "at the
  record's last commit" (a2671a340, parent 6b62de94e). Ordinary work: yes, because the next reader of the reopen
  paragraph expects `counts-after.head`. Consequence: other. Brought to the CTO for confirmation in the lead's return.
- **F2** (`_measured_at` takes any descendant of `counts-after.head` that is an ancestor of HEAD). Ordinary work: no,
  because the record is a closed ticket's path and its counts must still equal `gov links` at the commit it names.
  Consequence: other. A row.
- **F3** (`w2_175_support.py`'s module docstring does not mention `LANDING`; the constant's comment and the test
  module's docstring do). Ordinary work: no. Consequence: other. A row; rides along in any later resume (DEC-802).
- **F4** (out of scope: the S8 cases run the current `src/gov/links` on the pinned tree; a planned D-6 change to
  `gov links` reading DEC-1123 (2)'s forms as linked would move the counts at 6b62de94e and turn S8 red again).
  Ordinary work: yes. Consequence: other (a false red, fails closed). Brought to the CTO in the lead's return: pin the
  tool too, or make that ticket's entry criteria include re-baselining W2-130 S8.

Out of scope and not judged here: `test_w2_130_sources.py::test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form`
is red at this head and at its base `f4511c723` (three UNLINKED_ID left by the CTO's `ce8ae4353` on `w2/integrate`);
the lead brings it to the CTO as a package.

## The auditor's return, word for word

Step 0 (sandbox check, from launch_worker.sh): passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-q8cl` failed with `OSError: [Errno 30] Read-only file system`, and no file exists there.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (it gave `1ae28402a109…`), and `git update-index --refresh` exited 0.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing (exit 1), both at the start and before this return.
- `git status --porcelain` in the tree is empty. I committed nothing. All my scratch work is under `$TMPDIR/aud`.

Independent auditor, 2026-11-14T08:39:49+00:00, at 36d4539dbe433c4b27e94d7cb357ec8b79a5363f, W2-130 pin run narrow check.

The commit hashes below are as I used them in my commands; I give short prefixes only where I checked the full hash.

## Item 1: only the three test files changed — PASS
- **Files changed:** `git diff --stat f4511c72339e 36d4539db` lists only `tests/acceptance/W2-130/test_w2_130_record.py` (+31/−8), `tests/acceptance/W2-175/test_w2_175_record.py` (+8/−7) and `tests/acceptance/W2-175/w2_175_support.py` (+16). No record, README, ticket, source file or other test changed.
- **Trailers:** I ran `git interpret-trailers --parse` on 35b6ac6ba and 6a0b84a81. Each ends in a single trailer paragraph with `Task: DAEO-q8cl`, `Role: independent-test-designer`, `Implements: DEC-1073, DEC-1010`, `Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run)` and `Co-Authored-By`.
- **The merge:** 36d4539db has parents f4511c72339e and 6a0b84a81. It carries `Role: orchestrator` and adds nothing of its own to the diff.

## Item 2: W2-130 S8 runs `gov links` at a pinned commit — PASS (one deviation from the decided text, F1)
**What the cases do now.** Both mapped cases now get their findings from `s.links_json(clone_at(_measured_at(record)), home)` (`test_w2_130_record.py:90-100`, `:112-124`). They no longer use `head_findings`.
- `_measured_at` (`:74-87`) fails if the record has no `measured_at`. It also requires a full hash that is `counts-after.head` or a descendant of it, and an ancestor of HEAD.
- `unlinked_by_status` reads each ticket's status from the pinned tree (`_counts(…, tree)`).

**Other cases are untouched.** The diff changes no other function, and `test_w2_130_sources.py` and the other files are unchanged. That includes the HEAD-wide "no UNMARKED_CHANGE but the 8 pairs" case.

**My own measurement.** I ran `gov links --all --json` on `git clone -s` clones under `$TMPDIR`, with HOME empty and PYTHONPATH set to the tree's `src`. `git diff 8f8d707f0bd0 HEAD -- src/gov/links src/gov/cli` is empty. I counted with my own script, which does not use the tests' `_counts`.

| commit | by_code | by_code_role | unlinked_by_status | left D-5 / D-6 / D-9 |
|---|---|---|---|---|
| 57cbacfbf (`counts-after.head`) | UNLINKED_ID 1417 (record 1420), UNKNOWN_ID 57 (record 56) | UNKNOWN_ID orchestrator 48 (record 47) | closed 1352 (record 1355) | 0 / 0 / **5 paths differ** (DAEO-drhj, -g87r, -zmo4, -uw5h, -6icv) |
| 6b62de94e (`measured_at`) | equal | equal | equal | equal |
| a2671a340 (the record's last commit) | equal | equal | equal | equal |

**The lead's choice is sound.**
- The CTO's decision is about pinning a commit that does not move, and `measured_at` does that.
- The ticket's S8 Verify (`.tickets/DAEO-q8cl.md:37`) asks for "a re-run of gov links --all at the record's last commit". That commit is a2671a340: its parent is 6b62de94e, it changes only the record, and its counts equal the record's. 57cbacfbf predates the record: the record was first added in fcf5f5038.
- The record's own `command` says it counted 6b62de94e.
- A pin at `counts-after.head` would stay red while the record is left unedited.
- However, the ticket's reopen paragraph (`:93`) still names `counts-after.head` (F1).

## Item 3: W2-175 S7 reads each template at 61cae50dc through git — PASS
- **What the case does.** It asserts `t.landing_is_ancestor_of_head()` and then hashes `t.landing_bytes(stem)`, which is `git show LANDING:template/governance/kernel/templates/<stem>.md` (`w2_175_support.py:117-124`). It never reads the working tree.
- **The landing commit.** 61cae50dc5b4 is "Merge w2/W2-175 (DAEO-wahn) …" (parents 7350f6b03, 4c0c73472) and is an ancestor of HEAD.
- **Hashes.** For all seven templates, my own `sha256sum` of the file at 61cae50dc:
  - equals the file at the W2-175 branch head 4c0c73472;
  - appears exactly once in `docs/changes/W2-175-CIT-P.md`;
  - differs from the working tree only for role-cto and role-lead. That difference comes from b88a76172, the only change to the templates since 61cae50dc.
- **Tests.** All seven parametrised ids pass. The two changed files give 26 passed.
- **One stale docstring:** the support module's opening text still names only "the tree" and "a named base commit" (F3).

## Item 4: no case lost its point — PASS
I used a scratch `git clone -s` of the head under `$TMPDIR/aud/mut`, edited the records there only, and restored them between runs.

| what I planted | result |
|---|---|
| `counts-after.by_code.UNLINKED_ID` 1420 → 1421 | counts case FAILED: "by_code differs from gov links at measured_at {'UNLINKED_ID': 1421} != {'UNLINKED_ID': 1420}" |
| `left.D-9` `.tickets/DAEO-drhj.md` orchestrator 3 → 2 | left case FAILED: "left.D-9 differs from the findings at measured_at" (2 vs 3) |
| W2-175 role-lead row, landing sha256 4e8e46b0… replaced by `c731503e000…` | `[role-lead]` FAILED, naming 4e8e46b0… at 61cae50dc5b4 and the row; the other 6 passed |
| `measured_at` = 429dc5715 (unrelated, not a descendant of `counts-after.head`) | both FAILED: "not counts-after.head or a descendant of it" |
| `measured_at` = 3bf1c96b4 (a descendant of 57cbacfbf that is not on HEAD's history) | both FAILED: "not an ancestor of HEAD" |
| `measured_at` = 57cbacfbf (on the branch but not the tree the record counted) | both FAILED on the counts and on D-9 |
| `measured_at` = a2671a340 (the record's last commit, same counts) | both pass, which is correct |

An unrelated `measured_at` is caught in every case I tried. Only a commit whose counts match the record exactly gets through (F2).

## Item 5: the README maps still collect — PASS
- I compared each map's `test_w2_1xx_record.py::…` ids with `--collect-only` at the head.
- W2-130: 8 mapped, 8 collected, no difference either way.
- W2-175: 18 mapped, 18 collected, no difference either way.
- The names are the same as at the base, so the runner's matching is unchanged.

## Item 6 (out of scope, confirmed only)
- I ran `test_w2_130_sources.py::test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form` on a clone at f4511c72339e. It is red there with the same three ids: `('DAEO-6f0s','W2-60a'), ('DAEO-6w5n','W2-H046'), ('DAEO-sq3a','W2-56')`.
- It is also red at the head, and the file is identical at both commits, so this revision did not cause it.
- The two whole folders at the head (W2-130 and W2-175) give 131 passed and 1 failed, the failure being this case.
- **Left out by the exclusion:** I ran with `-m "not local_only" -k "not real and not green_here and not time_limit"`. Its effect in these folders was not checked: a run of exactly the folders' 132 cases implies nothing was deselected, but I did not confirm that.

## Findings
**F1 (item 2, in scope).** The cases pin `counts-after.measured_at` (6b62de94e). The CTO's decided text, in the ticket's "Reopened 2026-11-14" paragraph and in DIAG §3-4 (e), names `counts-after.head`. The deviation is justified (see item 2), but the ticket text and the tests now disagree on which commit is pinned. The CTO should confirm it and record the confirmation.
- Ordinary work: yes, because the next reader of the ticket's reopen paragraph will expect `counts-after.head` and find a different pin in the tests.
- Consequence: other (a mismatch between the record of the decision and the tests; nothing fails open and no work is lost).
- Evidence that would reverse it: a CTO or owner note that already accepts `measured_at`.

**F2 (item 4, in scope).** `_measured_at` accepts any commit that descends from `counts-after.head` and is an ancestor of HEAD. It does not require the record's last commit or its parent, and it takes the commit from the record under test. The counts must still equal `gov links` at whichever commit is named, so only a record whose counts are correct for the commit it names gets through.
- Ordinary work: no, because the record is a closed ticket's path. Changing it needs a reopen, and a refresh where the commit and the counts agree is still a true record.
- Consequence: other.
- Evidence that would reverse it: a pin that gets through with counts that do not match its own tree.

**F3 (item 3, in scope).** The opening docstring of `w2_175_support.py` (lines 1-8) still says it reads files "as the tree holds them … or as git holds them at a named base commit". It does not mention the new landing commit, `LANDING`. The constant's own comment and the test module's docstring are accurate.
- Ordinary work: no, because it is a stale description only; no behaviour depends on it.
- Consequence: other.

**F4 (item 2, out of scope: the decision pinned the tree, not the tool).** The S8 cases run the *current* `src/gov/links` against the pinned tree. The record says it counted with "the tool of 6b62de94e3fd". The record's own D-6 lists a planned `gov links` change: reading a `list_rows` backlog row, and a WBS id whose ticket id is in `sources:`, as linked (DEC-1123 (2)). When that lands, the UNLINKED_ID counts at 6b62de94e will move, and S8 will turn red again even though nothing is wrong. That is the same class of problem this reopen fixed.
- Ordinary work: yes, because an engineer doing the D-6 follow-up in `src/gov/links` will hit it.
- Consequence: other (a false red, which fails closed rather than open).
- Recommendation for the CTO: either pin the tool as well (run it from `measured_at`'s `src`), or make that ticket's entry criteria include re-baselining W2-130 S8.
- Evidence that would reverse it: a `gov links` change that leaves the counts at 6b62de94e unchanged.

**Classification:** 4 findings. None is "yes" to both questions, so none fails the check or justifies a round. F1 and F4 are reachable in ordinary work but their consequence is "other". F2 and F3 are not reachable in ordinary work.

```verdict
{"head": "36d4539dbe433c4b27e94d7cb357ec8b79a5363f", "date": "2026-11-14T08:39:49+00:00", "kpis": [{"kpi": "1 confined", "verdict": "pass", "findings": []}, {"kpi": "2 decided behaviour W2-130", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "3 decided behaviour W2-175", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "4 no case lost its point", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "5 maps still hold", "verdict": "pass", "findings": []}]}
```
