# W1-11 — Decision checker and owner-approval facts: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-be7u` (W1-11), the Contract
items its KPI lines name (CAP-51.a, CAP-01.b, CAP-21.a, CAP-34.d, with the acceptance lines of CAP-51, CAP-21 and
CAP-34 and CAP-21's lite form), ADR-0001 ("Approval facts"), the "Rules for every ticket" of the Wave 1 plan, and
DEC-012, DEC-039, DEC-046, DEC-074, DEC-136, DEC-182, DEC-221, DEC-227, DEC-274 to DEC-278, DEC-308, DEC-312, DEC-322,
DEC-328 to DEC-331 and DEC-360. Batches 1 and 2 were written before implementation; batch 3 was added after it,
from behaviours a review described (DEC-135, DEC-136). Profile FULL. No earlier ticket's test was rewritten.

**82 cases in 66 test functions.** The four decision packages of batch 1 are decided (below). One package of
batch 3 is open (DP-5, "Open package"); it blocks no case that is written and no repair.

## Run

```sh
python3 -m pytest tests/acceptance/W1-11 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. Nothing is installed. About 9 seconds when green.

- **Every call runs in a new Python process**, through a small driver written to a temporary directory, with this
  worktree's `src/` on `PYTHONPATH`.
- **Nothing is written in this worktree.** Every project is a temporary git repository, or a clone of the b-dev tier
  in a temporary directory. The store is built there, never in this repository (DEC-322).
- **Environment, built from scratch:** `PATH`, an empty temporary `HOME`, `TMPDIR`, locale, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX`. The session's `GOV_ROLE` and `GOV_TICKET` are not passed on.
- **Before a check, the project is committed and `gov.store.load` is run**, so the checker may read the record
  graph, git or the working tree: the three agree. One read-only test leaves uncommitted work in the tree on
  purpose and asserts only that nothing is touched. One batch 3 test runs the check without loading the store
  (below, "It needs no loaded store").
- **Fixture commits have fixed dates, authors and trailers.** A commit is dated 2026-10-04 at 12:00 UTC or later;
  two tests make one commit on 2026-09-20, before the trailer rule of DEC-182. The author's and the committer's
  dates are the same, and each falls on the same side of 2026-10-03 in every time zone. No commit is signed.
- **The five b-dev tests are marked `local_only`** and skip when `GOV_DEV_TIERS` (default
  `~/gov-os-workbench/synthetic`) has no `b-dev`. They clone the tier; the tier itself is never checked or written.

## The public interface

No `gov` command belongs to this ticket: no KPI names one, `src/gov/cli/**` is outside its `allowed_paths`, and
W1-26 runs the checker from `gov check`. So no `NOT_IMPLEMENTED` case of the W1-07 registry changes. The tests call
one function, as `gov.store` and `gov.tasks` are called (DEC-275). The engineer builds to exactly this:

**`gov.decisions.check(root)`** (`src/gov/decisions/`)

- `root` is a `pathlib.Path`: a project that is a git repository.
- It returns a list of findings, plain JSON data. **An empty list passes; any finding fails.** The same tree gives
  the same list twice.
- It only reads. It writes no file under `root`, stages nothing, commits nothing and moves no ref.
- It reads frontmatter and git, never a record's body (DEC-329). **It needs no loaded store** (batch 3): the
  store is neither. A commit message may hold any character git stores; none makes the check raise.
- A `root` that is not a git repository raises `gov.cli.errors.GovError` with a non-empty `code` and `details` a
  map. It is never an empty list. The code's name is the engineer's.

**A finding** is a map with four keys:

| Key | Value |
|---|---|
| `code` | One of the codes below. |
| `ids` | A list of strings: the ids of the records the finding is about. |
| `paths` | A list of strings: the files concerned, relative to `root`, with `/`. |
| `message` | A non-empty string for a person. |

A finding may carry more keys. The tests read `ids` and `paths` as sets, and (except for a cycle) ask only that the
ids and paths below are among them.

| Code | Raised when | `ids` hold | `paths` hold |
|---|---|---|---|
| `ACTIVE_SUPERSEDED` | A decision's `status` is `ACTIVE` and another decision's `supersedes` names it, or its own `superseded_by` names a successor. One finding for each such decision. | the ACTIVE decision | its file |
| `DUPLICATE_ID` | Two decision files have the same `id`, in one directory or in two. | the id | both files |
| `OVERLAPPING_ID` | Two decision files in different directories have ids with the same number and different prefixes (`ADR-003`, `DEC-003`). | both ids | both files |
| `SUPERSESSION_CYCLE` | The supersession edges form a cycle; a decision that supersedes itself is one. | exactly the members of the cycle, in one finding | (not asserted) |
| `ACTIVE_UNAPPROVED` | The commit that last set a decision's `status` to `ACTIVE` (added the decision with it, or changed the status to it) carries no owner approval fact (below). One finding for each such decision. | the decision | its file, at its path in `HEAD` |
| `GATE_NOT_AUTHORISING` | A file's frontmatter carries `approval` and a cited id does not authorise it (below). One finding for each citing file and cited id. | the cited id as `approval` writes it, and the citing record's id when it has one (batch 3: a citing file with no `id` gives the cited id alone) | the citing file |
| `TICKET_WAITS_ON_DEAD_GATE` | A ticket that is not closed is named in the `constrains` of a `DECLINED`, `REVOKED` or `STALE` package (DEC-330). | the ticket and the package | the ticket's file |
| `FRONTMATTER_UNREADABLE` (new in batch 3) | A Markdown file of `HEAD` opens with a `---` line and its frontmatter is not closed or is not valid YAML. One finding for each such file, whatever kind of file it is: the checker cannot know what it would have held. | (not asserted; may be empty) | the file |

**A decision file** is a Markdown file whose frontmatter is a decision: `type: decision`, or an `id` that fits the
`decision_id` grammar of `common.schema.json` (DEC-227). The second half is needed for b-dev, whose decision files
have no `type` and are therefore not records of the store (DEC-274). Supersession is read as the store reads it
(DEC-277): `supersedes` on the successor, `superseded_by` on the predecessor, one edge.

**The owner approval fact** (DEC-360, DEC-182) is the `Role: owner` trailer on the commit that sets the decision
`ACTIVE`.

- The trailer is read from the commit's final trailer block. For a commit made before 2026-10-03 a `Role: owner`
  line anywhere in the message counts.
- Only the commit that sets `ACTIVE` counts. A later owner commit approves nothing earlier, whether it edits the
  decision and leaves it `ACTIVE` or changes another file.
- Batch 3. **Only the commit's own `Role` trailer is read.** No other text of its message makes an approval,
  whatever characters it is written with.
- Batch 3. **"Later" is by ancestry, not by date.** An owner commit that descends from the commit that set the
  decision `ACTIVE` approves nothing, whatever its date and whether it reaches `HEAD` directly or through a merge.
  An owner commit on a branch that itself sets the decision `ACTIVE` still approves it after an agent's merge
  commit, which sets nothing. When a merge keeps the agent's file at a path both sides added, the decision in
  `HEAD` is the agent's, and the owner's commit on the other side is not its fact.
- Batch 3. **The decision is its `id`, not its file's path.** A commit that only moves the file sets nothing.
- An edit that leaves an approved decision `ACTIVE` needs no approval. Setting it `ACTIVE` again after another
  status is a new change and needs its own.
- The author's name and email, the record's own frontmatter and body, and any other project file are no fact.

**A gate authorises a citing record** (DEC-331, DEC-328) only when all of this holds; otherwise the check fails
closed with `GATE_NOT_AUTHORISING`:

- the cited id is the id of a record, and that record is a decision package (`type: decision-package`);
- the gate's `status` is `ACCEPTED` (`PROPOSED`, `DECLINED`, `REVOKED` and `STALE` do not authorise);
- the citing record has a `cit`, the gate has a `cit`, and the two are the same string. Two missing `cit` keys are
  not the same string.

A cited id that is no record is still named in `ids`, as written; `paths` holds the citing record's file alone,
because there may be no gate file. A record with no `approval` key is not checked, whatever `cit` it carries.

Batch 3: **the citing file need not be a record.** A Markdown file whose frontmatter carries `approval` is checked
whether or not it has an `id`; DEC-331 exempts only a file with no `approval`. A file that writes `approval` twice
does not pass: the finding is `GATE_NOT_AUTHORISING` for the cited id or `FRONTMATTER_UNREADABLE`, the engineer's
choice, and names the file. A citing file whose frontmatter cannot be read gives `FRONTMATTER_UNREADABLE`.

## KPI lines and their tests

Covers ids: CAP-51.a (21 cases), CAP-01.b and CAP-21.a (23), CAP-34.d (30). The read-only KPI has 6 cases; the
remaining 2 are the interface's own (the same findings twice, and the error case).

| KPI line | Covers | Tests | Decided by |
|---|---|---|---|
| Success 1: flags ACTIVE-while-superseded, duplicate or overlapping ids across directories, and supersession cycles on the b-dev fixtures | CAP-51.a | `test_w1_11_b_dev.py`: the first four tests (HZ-B-06 as planted; HZ-B-03, a cycle and a duplicate id written into the clone). `test_w1_11_hazards.py`: 12 functions, 14 cases, for each class in a register the test plants, and one that a supersession stated only in prose is not read | DEC-329 |
| Success 2: a change that sets a decision ACTIVE without an owner approval fact from git fails | CAP-01.b, CAP-21.a | `test_w1_11_approval.py`: 15 functions, 16 cases. 8 on a change without the trailer (an agent's commit adds or sets ACTIVE; no trailer; the owner's name and email with an agent's role; the file claims its own approval, CAP-01.b; the owner named in the message body after 2026-10-03; PROPOSED passes; every one flagged). 6 on what the owner's commit approves (it passes; the whole register passes; a later agent edit; a later agent re-activation; a later owner commit, 2 cases). 2 on commits made before 2026-10-03. Batch 3, `test_w1_11_approval_history.py`: 6 functions, 7 cases (a message that imitates a log entry, 2; a control character in a message; a later owner commit on a merged branch; the control, an owner commit on a branch that sets ACTIVE; an agent's file kept by a merge; an owner commit that only renames) | DEC-360, DEC-182 |
| Success 3: files stay byte-identical | none | `test_w1_11_read_only.py` (5), `test_the_tier_is_byte_identical_after_the_check` | nothing |
| Success 4: a declined, revoked or stale gate, or a gate answered for another CIT, does not authorise execution | CAP-34.d | `test_w1_11_gates.py`: 6 functions, 13 cases, on a ticket and a change record that cite a gate; 6 functions, 6 cases, on the fail-closed points; 3 functions, 6 cases, on a ticket that waits on a package. Batch 3, `test_w1_11_citing_files.py`: 4 functions, 5 cases (a citing file with no `id`, 2, and its control; unreadable frontmatter; `approval` written twice) | DEC-331 (24 cases), DEC-330 (6) |
| Failure 1: any planted decision hazard is missed | CAP-51.a | `test_every_hazard_planted_together_is_flagged`, `test_every_active_superseded_decision_is_flagged_not_only_the_first`, `test_every_unapproved_active_decision_is_flagged`, the b-dev tests. Batch 3, `test_w1_11_unreadable.py`: 2 functions, 3 cases (a second file of one id that is broken YAML or not closed; the control, a Markdown file with no frontmatter) | DEC-329 |
| Failure 2: the checker rewrites a decision file | none | `test_w1_11_read_only.py`, the b-dev read-only test | nothing |

The interface itself: `test_the_same_tree_gives_the_same_findings_twice`,
`test_a_folder_that_is_no_git_repository_is_an_error_not_a_pass`, and the shape of every finding, which
`w1_11_support.findings` checks on every call.

## Red run

Run on `w1/W1-11` at `e8e3aa36` with batch 2 in the tree, before implementation: **67 failed**, every one with

```
w1_11_support.CheckerMissing: the decision checker does not exist: No module named 'gov.decisions' under src/
```

No collection error and no other reason. The suite was also run against a throwaway reference checker in a copy of
`src/` in the session's temporary directory, outside the repository: 67 passed, the five b-dev tests included. A
reference with the rules weakened (trailers read from the final block alone, the last commit on the file taken as
the one that counts, `cit` compared without asking that it is there, any record type taken as a gate, a missing
gate skipped) failed the new cases that hold those rules. So each test can go green, and no test is red for a
reason of its own.

Expected red reason once the package exists, line by line: success 1 and failure 1, `no <CODE> finding names ids
[...] and paths [...]`; success 2, `no ACTIVE_UNAPPROVED finding names ...` or the findings shown for a decision the
owner approved; success 3 and failure 2, a list such as `docs/adr/ADR-0010.md: rewritten` or `git status changed`;
success 4, `no GATE_NOT_AUTHORISING finding names ...` or `GATE_NOT_AUTHORISING was raised for ...`.

## The decided packages

Batch 1 returned four packages. Each was answered with its option (a); the register holds the text.

| Package | Question | Answer |
|---|---|---|
| DP-1 | What must be flagged on b-dev as planted | **DEC-329**, option (a): the checker reads frontmatter and git, never prose. On the tier as planted it flags the overlapping ids; the other classes are tested on a clone where the test writes the link. Revisited if G-04 requires prose reading. |
| DP-2 | What an owner approval fact from git is | **DEC-360** (owner), option (a): the `Role: owner` trailer on the commit that sets the decision `ACTIVE`. A later owner commit approves nothing earlier. A signature is the stricter form and a residual. |
| DP-3 | How a record cites a gate, and which CIT is compared | **DEC-331**, option (a): `approval`, a list of gate ids, and `cit`, a scalar, on the citing record. The check fails closed. A record with no `approval` is not checked. |
| DP-4 | What a dead package does to waiting tickets | **DEC-330**, option (a): the checker fails a ticket that is not closed and is named in the `constrains` of a `DECLINED`, `REVOKED` or `STALE` package. The READY rule is unchanged. |

## Batch 2 (2026-10-05, before implementation)

12 cases added, 55 to 67. No assertion of batch 1 was changed: DEC-329, DEC-330, DEC-331 and DEC-360 each took the
option the cases already followed, so none of the 55 was made wrong.

| Added | From |
|---|---|
| `test_a_cited_id_that_is_no_record_does_not_authorise` | DEC-331 |
| `test_a_cited_record_that_is_no_decision_package_does_not_authorise` | DEC-331 |
| `test_a_citing_record_without_a_cit_is_not_authorised` | DEC-331 |
| `test_a_gate_without_a_cit_does_not_authorise` | DEC-331 |
| `test_two_missing_cits_are_not_the_same_cit` | DEC-331 ("the same string", with both fail-closed points) |
| `test_a_record_without_approval_is_not_checked` | DEC-331 |
| `test_a_later_owner_commit_that_does_not_set_active_approves_nothing_earlier` (2 cases) | DEC-360 |
| `test_the_owner_name_and_email_on_an_agent_commit_are_no_approval` | DEC-360 (the fact is the trailer) |
| `test_the_owner_role_in_the_message_body_of_a_commit_made_before_the_trailer_rule_approves` | DEC-182, DEC-360 |
| `test_an_agent_commit_made_before_the_trailer_rule_is_no_approval` | DEC-182, DEC-360 |
| `test_a_supersession_stated_only_in_prose_is_not_read` | DEC-329 |

Revised, all before implementation began, none in what a test asserts:

- The docstrings and comments of `test_w1_11_approval.py`, `test_w1_11_gates.py` and `w1_11_support.py` no longer
  say "waits on DP-n" or "recommended option"; they name the decision.
- `w1_11_support.py`: `Project.commit` takes a `date`; `package(..., cit=None)` leaves the key out; the identity
  `AGENT_AS_OWNER` and the date `BEFORE_THE_TRAILER_RULE` are new. No existing fixture changed.

## Batch 3 (2026-10-05, after implementation)

**15 cases added, 67 to 82: "tests added after implementation". No existing case was changed**, in what it
asserts or in its fixture. `w1_11_support.py` gained `Project.switch`, `Project.merge`, `assert_fails_naming` and
the code `FRONTMATTER_UNREADABLE`; nothing in it was altered.

Run on `w1/W1-11` at `fd7b6eb3`, against the checker as built: **12 failed, 70 passed** (the 67 earlier cases and
the 3 controls). No collection error.

| Added | Red, with | From |
|---|---|---|
| `test_a_commit_message_that_imitates_an_owner_log_entry_is_no_approval` (2 cases) | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] ...`, findings `(none)` | DEC-360, CAP-01.b |
| `test_a_control_character_in_a_commit_message_does_not_break_the_check` | `gov.decisions.check failed (exit code 1)`: a `ValueError`, no `GovError` | the interface (a list of findings) |
| `test_a_later_owner_commit_on_a_merged_branch_approves_nothing_earlier` | `no ACTIVE_UNAPPROVED finding names ...` | DEC-360 |
| `test_an_owner_commit_on_a_branch_that_sets_active_approves_after_the_merge` | green: the control | DEC-360 |
| `test_an_agent_decision_kept_by_a_merge_over_the_owner_file_at_the_same_path_fails` | `no ACTIVE_UNAPPROVED finding names ...` | DEC-360, CAP-01.b |
| `test_an_owner_commit_that_only_renames_the_file_approves_nothing_earlier` | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] and paths ['docs/adr/ADR-0010-renamed.md']` | DEC-360 |
| `test_a_citing_file_without_an_id_is_not_authorised_by_a_declined_gate` (2 cases) | `no GATE_NOT_AUTHORISING finding names ids ['DP-0001'] ...` | KPI success 4, DEC-331 |
| `test_a_citing_file_without_an_id_is_authorised_by_an_answered_gate_of_its_cit` | green: the control | DEC-331 |
| `test_a_citing_ticket_whose_frontmatter_cannot_be_read_does_not_pass` | `no FRONTMATTER_UNREADABLE finding names the file .tickets/PROJ-aaaa.md` | KPI success 4, DEC-331 (fails closed) |
| `test_a_second_empty_approval_key_does_not_take_the_first_out_of_the_check` | `no FRONTMATTER_UNREADABLE or GATE_NOT_AUTHORISING finding names the file ...` | DEC-331 |
| `test_a_decision_file_that_cannot_be_read_does_not_pass_in_silence` (2 cases) | `no FRONTMATTER_UNREADABLE finding names the file decisions/ADR-0010.md` | KPI failure 1, DEC-329 |
| `test_a_markdown_file_without_frontmatter_is_not_unreadable` | green: the control | DEC-274 (no frontmatter is no record) |

What the designer settled from the sources, each open to the lead's correction:

- **`FRONTMATTER_UNREADABLE`, for every Markdown file.** Failure line 1 forbids silence. DEC-329 has the checker
  read frontmatter, not scan text, so it cannot know that an unreadable file is a decision file; it reports each.
  On 2026-10-05 no tracked Markdown file of this repository outside `docs/source/` is unreadable in this sense.
- **Identity by `id`** for a renamed decision, and **ancestry** for "later": DEC-360 speaks of the decision and of
  the commit that sets it `ACTIVE`, not of a file path or a date.
- **A citing file with no `id`** gives a finding whose `ids` hold the cited id; the file is in `paths`.

## Open package

**DP-5: what a Markdown file is whose `---` is not its first line.**

- **Question.** A file has a byte-order mark, or blank lines, before the `---` that opens what looks like
  frontmatter; inside it stand `id: ADR-0010` and `status: ACTIVE`. The store reads it as a file with no
  frontmatter (DEC-274), so it is no record. Is it a decision file for the checker, an unreadable file, or prose?
- **Why now.** The review reproduced it: an agent can add such a file with the id of an existing decision and
  `ACTIVE`, and the check passes in silence. No source says what the file is.
- **Options.** (a) The checker reports it as `FRONTMATTER_UNREADABLE`: a Markdown file whose first line that is not
  blank, after an optional byte-order mark, is `---`, and that line is not line 1. (b) The checker reads past the
  mark or the blank lines and treats the file as a decision file. (c) It stays prose and a residual; the store's
  ticket decides whether such a file is a record.
- **Impact.** (a) one more rule and two cases; a file that opens with a blank line and a rule `---` fails the
  check until the blank line goes. (b) the checker and the store disagree about what has frontmatter, so a
  decision the checker approves is still no record of the store. (c) the hazard stays open.
- **Reversibility.** High for each: one rule and its cases.
- **Cost.** (a) about 5 lines and 2 cases. (b) about 5 lines, 2 cases, and a divergence to document. (c) none.
- **Recommendation.** (a). **Confidence:** medium.
- **Dependence.** No repair of the 12 red cases depends on it. Two cases wait on it and are not written.

## Notes for the lead

- **`gov.store.load` (W1-10) splits the commit log on the same ASCII separators** as the checker. A stray unit
  separator in any commit message makes the load raise a `ValueError` (seen in this batch's first run). A message
  that imitates a log entry may also put a commit and trailers into the store that no commit carries; that was
  not tested here. Both are outside this ticket's paths, so
  `test_a_control_character_in_a_commit_message_does_not_break_the_check` runs the check without loading the store.

- **The approval rule is judged on `HEAD`'s decisions over the whole history.** No KPI needs a commit range. A
  legacy register (all of b-dev) is reported unapproved until the owner adopts it. W1-26 may need a range or a
  baseline; that is its test design's.
- **The MADR schema.** `madr.schema.json` (W1-08) validates the frontmatter of a `type: decision` record. No KPI
  line of this ticket says what W1-11 adds to it, and DEC-012 leaves the status list open, so this suite asserts
  nothing about the schema's content; W1-08's suite keeps what it holds. The five gate `status` values (W1-34
  residual) belong in `decision-package.schema.json`, outside this ticket's `madr*` path; `supersedes` and
  `superseded_by` still have no grammar (W1-08 residual); the two committed ADRs lack `state_class`; whether the
  checker reports schema failures is asked by no KPI line and is not tested.
- **G-04** was not read (DEC-329 says when that is revisited).

## Residuals the suite leaves

Decisions:

- **A signature as the stricter approval fact** (DEC-360). Not tested.
- **A commit that carries `Role: owner` and was made by an agent passes this check.** The safeguard is W1-50's
  (DEC-360). No case here pins that it passes.
- **Closing the READY queue to a ticket that waits on a dead package** is for the ticket that next changes
  `gov.tasks` (DEC-330).
- **Whether setting a gate `ACCEPTED` needs an owner approval fact**, the CIT id's grammar, and the schema lines for
  `approval` and `cit` (DEC-331). Not tested.

Approval facts, not fixed by a decision and not tested:

- **Which date decides "made before 2026-10-03".** The store uses the committer date in the commit's own time zone
  (W1-10 residual). Every fixture commit has one date for author and committer, well away from the boundary.
- **A commit with two `Role` trailers** (`Role: engineer` and `Role: owner`), another letter case (`role: Owner`),
  or `Role: owner` in a final block that also holds other trailers.
- **A merge commit that itself sets the status** (its file differs from both parents'), and a merge that keeps
  the owner's file over an agent's at a path both added. Batch 3 tests the merges that set nothing and the merge
  that keeps the agent's file.
- **An agent's commit that renames a decision the owner approved** is reported flagged by the checker as built
  (the review's note; not run here). By the rule above it sets nothing and would pass. The behaviour fails
  closed, so it is recorded here and not tested (DEC-135).
- **A rename that also changes the `id` or the body**, and a decision whose file is deleted and added again.
- **A decision that is `ACTIVE` only in the working tree.** Every checked fixture is committed.

Gates, not tested:

- `approval` that is empty, a scalar, or names one id twice; a `cit` that is empty or not a string; two records with
  the cited id; a package that does not load (W1-09 residual).

Hazards, as in batch 1:

- A file whose `---` is not its first line (a byte-order mark or blank lines before it): open package DP-5.
- Frontmatter that is valid YAML and no map (a list, a scalar), and a key other than `approval` written twice
  (`status`, `id`), are not tested.
- Status values in another case, and a superseder that is itself `PROPOSED`, are not tested.
- Overlapping ids are tested only for identical digit strings (`ADR-003`, `DEC-003`); `ADR-0001` beside `DEC-001`
  is not. This repository's own two series (ADR files, DEC headings in the register) are not both files yet.
- Two overlapping ids inside one directory are not tested: the KPI says "across directories".
