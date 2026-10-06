# W1-11 — Decision checker and owner-approval facts: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-be7u` (W1-11), the Contract
items its KPI lines name (CAP-51.a, CAP-01.b, CAP-21.a, CAP-34.d, with the acceptance lines of CAP-51, CAP-21 and
CAP-34 and CAP-21's lite form), ADR-0001 ("Approval facts"), the "Rules for every ticket" of the Wave 1 plan, and
DEC-012, DEC-039, DEC-046, DEC-074, DEC-136, DEC-182, DEC-221, DEC-227, DEC-274 to DEC-278, DEC-308, DEC-312, DEC-322,
DEC-328 to DEC-331 and DEC-360. Batches 1 and 2 were written before implementation; batches 3, 4 and 5 were added
after it, from behaviours a review described (DEC-135, DEC-136) and, in batch 5, from DEC-387 and DEC-398 (with
DEC-403, DEC-410, DEC-413 and DEC-415). Profile FULL. No earlier ticket's test was rewritten.

**132 cases in 97 test functions.** The four decision packages of batch 1 are decided, and so are DP-5 (DEC-387),
DP-6 (DEC-398) and DP-7 (DEC-387). One package is open ("Open package"): DP-8 of batch 5, on how the checker learns
what a merge's dropped parent changed. It blocks no case; the engineer's repair of the merge rule depends on it.

## Run

```sh
python3 -m pytest tests/acceptance/W1-11 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. Nothing is installed. About 20 seconds.

- **Every call runs in a new Python process**, through a small driver written to a temporary directory, with this
  worktree's `src/` on `PYTHONPATH`.
- **Nothing is written in this worktree.** Every project is a temporary git repository, or a clone of the b-dev tier
  in a temporary directory. The store is built there, never in this repository (DEC-322).
- **Environment, built from scratch:** `PATH`, an empty temporary `HOME`, `TMPDIR`, locale, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX`. The session's `GOV_ROLE` and `GOV_TICKET` are not passed on. Batch 4: three cases add
  `GIT_DIR` on purpose (`check_only(root, environment=...)`).
- **Before a check, the project is committed and `gov.store.load` is run**, so the checker may read the record
  graph, git or the working tree: the three agree. One read-only test leaves uncommitted work in the tree on
  purpose and asserts only that nothing is touched. One batch 3 test runs the check without loading the store
  (below, "It needs no loaded store"). The seven batch 4 cases of `test_w1_11_object_store.py` and
  `test_w1_11_git_environment.py` do the same: what `gov.store.load` does in a partial clone, with an object
  missing or under `GIT_DIR` is not this ticket's, and a load could fetch the very objects a case needs absent.
  Batch 5: so do the two cases of `test_w1_11_no_id_and_replace_refs.py` and the case of a merge with 25 parents.
- **Batch 4: a partial clone's remote is a local repository** in the same temporary directory, reached by a
  `file://` address. That is not the network.
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
- It only reads. It writes no file under `root`, stages nothing, commits nothing and moves no ref. Batch 4:
  **`.git/` is under `root`.** No file there is added, removed or rewritten, and **nothing is fetched**: in a
  clone made with a blob filter the check does not ask the remote for the versions it lacks.
- Batch 4. **It checks `root`, whatever repository the environment names.** With `GIT_DIR` naming another
  repository the result is the findings of `root` or a `GovError`, never the other repository's.
- Batch 4. **A history it cannot read does not pass.** When a version of an `ACTIVE` decision's file in an
  earlier commit is absent from the object store, the check gives `ACTIVE_UNAPPROVED` for the decision or raises
  `GovError`. Which of the two is the engineer's.
- It reads frontmatter and git, never a record's body (DEC-329). **It needs no loaded store** (batch 3): the
  store is neither. A commit message may hold any character git stores; none makes the check raise.
- A `root` that is not a git repository raises `gov.cli.errors.GovError` with a non-empty `code` and `details` a
  map. It is never an empty list. The code's name is the engineer's. Batch 4: this holds with `GIT_DIR` set.

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
| `FRONTMATTER_UNREADABLE` (new in batch 3) | A Markdown file of `HEAD` opens with a `---` line and its frontmatter is not closed or is not valid YAML. Batch 5 (DEC-387): or its head looks like frontmatter and the store does not read it as frontmatter (below). One finding for each such file, whatever kind of file it is: the checker cannot know what it would have held. | (not asserted; may be empty) | the file |

**A decision file** is a Markdown file whose frontmatter is a decision: `type: decision`, or an `id` that fits the
`decision_id` grammar of `common.schema.json` (DEC-227). The second half is needed for b-dev, whose decision files
have no `type` and are therefore not records of the store (DEC-274). Supersession is read as the store reads it
(DEC-277): `supersedes` on the successor, `superseded_by` on the predecessor, one edge.

Batch 5 (DEC-387). **A file with `type: decision` and no `id` is a decision that fails**: the check gives a finding
that names the file. Its code is the engineer's. The case is an `ACTIVE` one an agent added; whether the same file
fails when it is `PROPOSED`, or added by the owner, is not asserted.

Batch 5 (DEC-387). **A head that looks like frontmatter and is not read as frontmatter is unreadable.** The store
reads frontmatter only from a file whose first line is exactly `---`, in UTF-8, with LF or CRLF line ends. Five
heads are tested, each on a file that would be a second `ACTIVE` decision of an existing id: a byte-order mark
before `---`; a blank line before `---`; a first line `--- # c`; CR-only line ends; UTF-16. Each gives
`FRONTMATTER_UNREADABLE` for the file. Not reported (the control): a decision file with CRLF line ends, and prose
whose first line that is not blank is a heading or a rule of five dashes, with or without a byte-order mark. A
consequence DEC-387 accepts: prose that opens with a blank line and then a rule `---` is reported until the blank
line goes.

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
- Batch 4. **A commit with two parents can be that new change.** The owner's commit set the decision `ACTIVE`
  and a commit that descends from it gave it another status: the demotion is the later word. A commit that holds
  the decision `ACTIVE` and has that demotion, or a descendant of it that keeps the other status, as a parent
  sets the decision `ACTIVE` again, whether its file is its first parent's, its second parent's or written new,
  and whether or not its other parent is an ancestor of the first. Its own `Role` trailer is the fact: an agent's
  fails, the owner's passes. A merge that brings in a commit which itself set the decision `ACTIVE` after the
  demotion still sets nothing. Batch 5 restates this bullet as the merge rule below; every case of batch 4
  follows from it.
- Batch 4. **An earlier version that cannot be read is not "the file did not exist then".** It makes no later
  commit the one that set `ACTIVE`.
- Batch 5 (DEC-387). **A replace ref changes nothing.** The fact is the trailer of the commit the history names,
  not of a commit a ref under `refs/replace/` puts in its place.
- The author's name and email, the record's own frontmatter and body, and any other project file are no fact.

**The merge rule** (batch 5; DEC-398, the owner's answer to the lead's package DP-6 on how the approval rule reads
merges, with DEC-403 and DEC-410 for the helper). The approval rule judges a merge against the merge base.

- **A decision's state in a commit** is whether the commit holds a decision file with that `id`, and its `status`,
  wherever the file lies.
- **A commit with several parents that holds the decision `ACTIVE` sets nothing only when** a parent holds it
  `ACTIVE`, **and** no other parent changed its id, its status or its presence since the merge base, **and** the
  commits that set it `ACTIVE` in every parent that holds it `ACTIVE` carry the owner's fact. Otherwise the merge
  commit is itself the change that sets it `ACTIVE`, and its own `Role` trailer is the fact: an agent's fails, the
  owner's passes.
- **A moved file.** The decision is its `id`. A parent that only moved the file changed neither its id, its status
  nor its presence. Where one side moves the file and the other demotes or removes it at the old path, the side
  that demoted or removed is the one that changed the decision; a merge that holds the moved file `ACTIVE` is the
  change. The finding names the id and the file's path in `HEAD`. A branch that only moved an approved decision,
  merged into a line that left it alone, passes.
- **It fails closed.** Where the parents have several merge bases (two lines that crossed) or none (unrelated
  histories), nothing counts as brought by a parent: a decision the merge commit holds `ACTIVE` in a file that
  differs from any parent's, or that a parent does not hold, is set by the merge commit. A merge that holds the
  very file of the decision that every parent holds sets nothing, whatever the merge bases.
- **A merge it cannot read does not pass.** A merge commit with more than 24 distinct parents on the way to an
  `ACTIVE` decision that an agent's commit set gives `ACTIVE_UNAPPROVED` or a `GovError`, never an empty list.

**What the checker relies on, and the engineer must use and not build again:**
`gov.guard.containment_merge.read_merge(root, commit)`, the one helper that reads a merge, shared with containment
(DEC-398, DEC-403, DEC-410). It is built on W1-50's branch and is not in this tree yet (early test design,
DEC-415). No case imports it, names its result or asserts anything of it: every case asserts the result of
`gov.decisions.check` on a history a temporary repository holds. As the brief for this batch describes it, it gives
two sorted, disjoint lists of paths for a merge commit, `own` and `brought`, without rename detection; with several
merge bases or none, every path that differs from any parent is in `own`; it raises `MergeReadError` for a merge
with more than 24 distinct parents, a commit it cannot read, or an argument that is no commit id. If its interface
changes before W1-50 is merged, the cases here need no revision unless the rule above changes.

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

Covers ids: CAP-51.a (28 cases), CAP-01.b and CAP-21.a (60), CAP-34.d (30). The read-only KPI has 9 cases; the
remaining 5 are the interface's own (the same findings twice, the error case, and three on `GIT_DIR`).

| KPI line | Covers | Tests | Decided by |
|---|---|---|---|
| Success 1: flags ACTIVE-while-superseded, duplicate or overlapping ids across directories, and supersession cycles on the b-dev fixtures | CAP-51.a | `test_w1_11_b_dev.py`: the first four tests (HZ-B-06 as planted; HZ-B-03, a cycle and a duplicate id written into the clone). `test_w1_11_hazards.py`: 12 functions, 14 cases, for each class in a register the test plants, and one that a supersession stated only in prose is not read | DEC-329 |
| Success 2: a change that sets a decision ACTIVE without an owner approval fact from git fails | CAP-01.b, CAP-21.a | `test_w1_11_approval.py`: 15 functions, 16 cases. 8 on a change without the trailer (an agent's commit adds or sets ACTIVE; no trailer; the owner's name and email with an agent's role; the file claims its own approval, CAP-01.b; the owner named in the message body after 2026-10-03; PROPOSED passes; every one flagged). 6 on what the owner's commit approves (it passes; the whole register passes; a later agent edit; a later agent re-activation; a later owner commit, 2 cases). 2 on commits made before 2026-10-03. Batch 3, `test_w1_11_approval_history.py`: 6 functions, 7 cases (a message that imitates a log entry, 2; a control character in a message; a later owner commit on a merged branch; the control, an owner commit on a branch that sets ACTIVE; an agent's file kept by a merge; an owner commit that only renames). Batch 4, `test_w1_11_approval_merges.py`: 3 functions, 6 cases (an agent's commit with two parents that sets ACTIVE again a decision the owner demoted, 4; the controls: the owner's such merge, and an agent's merge that brings in the owner's later commit). `test_w1_11_object_store.py`: `test_a_missing_object_does_not_make_a_later_owner_commit_the_approval`. Batch 5, `test_w1_11_approval_merge_base.py`: 14 functions, 19 cases (a concurrent demotion or removal, 2, and the owner's such merge; the owner's file kept over an agent's; the three reviewed histories, 5, with the pair that shows what hid the first, 2; the owner's merges, 2; everyday merges, 6). `test_w1_11_approval_fail_closed.py`: 4 functions, 10 cases (several merge bases or none: an agent's merge, 4, the owner's, 4; two crossed lines that hold the same file; a merge with 25 parents). `test_w1_11_no_id_and_replace_refs.py`: `test_a_replace_ref_that_gives_an_agent_commit_the_owner_role_is_no_approval` | DEC-360, DEC-182, DEC-398, DEC-387 |
| Success 3: files stay byte-identical | none | `test_w1_11_read_only.py` (5), `test_the_tier_is_byte_identical_after_the_check`. Batch 4, `test_w1_11_object_store.py`: 3 cases on `.git/` (the control in a whole repository; a partial clone whose remote can be asked; one whose remote is out of reach). The two partial clone cases also hold success 2: the result is no pass | nothing |
| Success 4: a declined, revoked or stale gate, or a gate answered for another CIT, does not authorise execution | CAP-34.d | `test_w1_11_gates.py`: 6 functions, 13 cases, on a ticket and a change record that cite a gate; 6 functions, 6 cases, on the fail-closed points; 3 functions, 6 cases, on a ticket that waits on a package. Batch 3, `test_w1_11_citing_files.py`: 4 functions, 5 cases (a citing file with no `id`, 2, and its control; unreadable frontmatter; `approval` written twice) | DEC-331 (24 cases), DEC-330 (6) |
| Failure 1: any planted decision hazard is missed | CAP-51.a | `test_every_hazard_planted_together_is_flagged`, `test_every_active_superseded_decision_is_flagged_not_only_the_first`, `test_every_unapproved_active_decision_is_flagged`, the b-dev tests. Batch 3, `test_w1_11_unreadable.py`: 2 functions, 3 cases (a second file of one id that is broken YAML or not closed; the control, a Markdown file with no frontmatter). Batch 5: the same function with five more heads (5 cases), `test_an_ordinary_file_is_not_unreadable`, and `test_an_active_decision_without_an_id_set_by_an_agent_fails` | DEC-329, DEC-387 |
| Failure 2: the checker rewrites a decision file | none | `test_w1_11_read_only.py`, the b-dev read-only test, the three batch 4 cases on `.git/` | nothing |

The interface itself: `test_the_same_tree_gives_the_same_findings_twice`,
`test_a_folder_that_is_no_git_repository_is_an_error_not_a_pass`, and the shape of every finding, which
`w1_11_support.findings` checks on every call. Batch 4, `test_w1_11_git_environment.py`: 3 functions, 3 cases
(`GIT_DIR` names a clean repository; `root` holds an agent's ACTIVE decision, is no repository, or is a folder
inside a repository).

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

## Batch 4 (2026-10-05, after implementation)

**13 cases added, 82 to 95: "tests added after implementation". No existing case was changed**, in what it
asserts or in its fixture. `w1_11_support.py` gained `Project.merge_with`, `Project.commit_by_hand`, `parents_of`,
`partial_clone`, `absent_objects`, `remove_object`, `everything_under`, `differences` and `outcome`.
`Api.check_only` and `Api._batch` take one more argument with a default (variables added to the checker's
environment); a call without it runs as before.

Run on `w1/W1-11` at `3f4aff31`, against the checker as built: **9 failed, 86 passed** (the 82 earlier cases and
the 4 green cases below). No collection error.

| Added | Red, with | From |
|---|---|---|
| `test_an_agent_merge_that_sets_active_again_a_decision_the_owner_demoted_fails` (4 cases: the branch keeps its own tree and main moves forward; the main line takes the branch's file; a commit by hand names the owner's old commit as a parent; the merge writes the file new) | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] and paths ['docs/adr/ADR-0010.md']`, findings `(none)` | DEC-360, KPI success 2 |
| `test_an_owner_merge_that_sets_active_again_a_demoted_decision_passes` | green: the control | DEC-360 |
| `test_an_agent_merge_that_brings_in_the_owner_commit_that_set_active_again_passes` | green: the control | DEC-360 |
| `test_a_check_leaves_every_file_under_git_as_it_was` | green: the control | KPI success 3 |
| `test_a_check_of_a_partial_clone_fetches_nothing_and_writes_nothing` | `assert ['.git/objects/pack/pack-….idx: added', ...] == []` (8 files added, new packs under `.git/objects/pack/`) | KPI success 3, failure 2 |
| `test_a_check_of_a_partial_clone_whose_remote_is_out_of_reach_does_not_pass` | green today: the check raises `GovError` and writes nothing. It pins that a repair of the case above does not turn into a pass | KPI success 3, DEC-360 |
| `test_a_missing_object_does_not_make_a_later_owner_commit_the_approval` | `no ACTIVE_UNAPPROVED finding names ...`, findings `(none)` | DEC-360 |
| `test_git_dir_naming_another_repository_does_not_hide_the_findings_of_the_root` | `no ACTIVE_UNAPPROVED finding names ...`, findings `(none)` | the interface |
| `test_git_dir_does_not_make_a_folder_that_is_no_repository_pass` | `a folder that is no git repository gave findings: (none)` | the interface |
| `test_git_dir_does_not_make_a_subfolder_of_a_repository_pass` | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] and paths []`, findings `(none)` | the interface |

What the designer settled from the sources, each open to the lead's correction:

- **A commit with two parents can set `ACTIVE` again.** DEC-360 names "the commit that sets the decision
  `ACTIVE`" and batch 3 read "later" as ancestry. Where the demotion descends from the owner's commit, a merge
  that holds `ACTIVE` over it undoes the later word: the merge is the change. The batch 3 control
  (`test_an_owner_commit_on_a_branch_that_sets_active_approves_after_the_merge`) stays as it is: there the main
  line's `PROPOSED` is the earlier word and the branch's owner commit the later.
- **The owner's merge that sets `ACTIVE` again passes.** A merge commit is a commit, and it carries the trailer.
- **`.git/` is under `root`** for "files stay byte-identical" and "it only reads". A fetch is a write there and a
  use of the remote, so the check does not fetch. The three cases compare every file under the root by its bytes,
  read from the file system; no git command runs between the two listings except the check's own.
- **A history that cannot be read gives a finding or a `GovError`**, the engineer's choice. A partial clone that
  may not fetch is such a history, so the partial clone cases accept either and forbid a pass. Whether a partial
  clone can ever pass (an owner's decision whose earlier versions are absent) is not asserted.
- **Can it go green.** With git 2.43 as installed here, `GIT_NO_LAZY_FETCH=1` makes `git cat-file` fail on an
  absent blob without fetching, and `git cat-file --batch-all-objects --batch-check` lists the objects held
  without fetching; both left `.git/` as it was in a probe outside the repository. The engineer's means are their
  own.
- **A `root` that is a folder inside a repository** is not said by the interface to be an error or to be checked
  as its repository; the checker as built raises `GovError`. The `GIT_DIR` case accepts either and forbids a pass.

## Batch 5 (2026-10-06, after implementation)

**37 cases added, 95 to 132: "tests added after implementation". No existing case was changed in what it asserts
or in its fixture: no case of batches 1 to 4 contradicts DEC-398 or DEC-387.** Two texts were revised, with the
reason "owner decision: DEC-398" and "DEC-387": the docstring of `test_w1_11_approval_merges.py` no longer calls
DP-6 open, and the docstring of `test_w1_11_unreadable.py` no longer says the first-line forms wait on a package.
`test_a_decision_file_that_cannot_be_read_does_not_pass_in_silence` gained five parameters (DEC-387); its two
earlier cases are as they were. `w1_11_support.py` gained `Project.remove`, `move`, `orphan`, `bare_commits`,
`copy_of_commit`, `criss_cross`, `merge_bases` and `assert_some_finding_names`; `Project.merge_with` takes three
more arguments with defaults (`drop`, `unrelated`, `under`) and `Project.write` also takes bytes; a call without
them runs as before. No interface change: `gov.decisions.check(root)` and the eight codes stand.

Run on `w1/W1-11` at `c3072357`, against the checker as built, the shared helper absent: **13 failed, 119 passed**
(the 95 earlier cases and the 24 green cases below). No collection error; no case imports the helper.

| Added | Red, with | From |
|---|---|---|
| `test_an_agent_merge_that_keeps_active_fails_although_the_demoted_line_merged_an_old_branch` (2 cases: demoted to `PROPOSED`; the file removed) | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] and paths ['docs/adr/ADR-0010.md']`, findings `(none)` | DEC-398, DEC-360, KPI success 2 |
| `test_the_same_merge_fails_without_the_old_branch` (2 cases) | green: flagged as built. The pair shows the merge of an old branch is what hid the case above | DEC-360 |
| `test_an_agent_merge_that_keeps_a_moved_active_file_over_a_demotion_at_the_old_path_fails` (2 cases: demoted; removed, a merge git makes with no conflict) | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] and paths ['decisions/ADR-0010.md']`, findings `(none)` | DEC-398, DEC-360, DEC-387 (the decision is its id) |
| `test_a_second_merge_that_keeps_the_owner_file_does_not_hide_an_agent_reactivation` | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] and paths ['docs/adr/ADR-0010.md']`, findings `(none)` | DEC-398, DEC-360 |
| `test_an_agent_merge_that_cannot_be_judged_against_one_merge_base_fails` (4 cases) | 1 red, `two crossed lines, the owner approved on one`: `no ACTIVE_UNAPPROVED finding names ...`, findings `(none)`. 3 green: flagged as built (two crossed lines with the owner's approval on both; an unrelated history without the decision; an unrelated history imported with it). They pin "fails closed" | DEC-398, DEC-403 |
| `test_an_active_decision_without_an_id_set_by_an_agent_fails` | `no finding names the file docs/adr/ADR-0011.md`, findings `(none)` | DEC-387, KPI failure 1 |
| `test_a_replace_ref_that_gives_an_agent_commit_the_owner_role_is_no_approval` | `no ACTIVE_UNAPPROVED finding names ids ['ADR-0010'] and paths ['docs/adr/ADR-0010.md']`, findings `(none)` | DEC-387, DEC-360 |
| `test_a_decision_file_that_cannot_be_read_does_not_pass_in_silence` (5 new cases: a byte-order mark, a blank line, a comment on the first line, CR-only line ends, UTF-16) | `no FRONTMATTER_UNREADABLE finding names the file decisions/ADR-0010.md`, findings `(none)` | DEC-387, KPI failure 1 |
| `test_an_ordinary_file_is_not_unreadable` | green: the control | DEC-387 |
| `test_an_agent_merge_that_keeps_active_over_a_concurrent_owner_demotion_fails` (2 cases: demoted; removed) | green: flagged as built (it fails two sides that disagree). They pin package DP-6 of batch 4 as decided | DEC-398 |
| `test_an_owner_merge_that_keeps_active_over_a_concurrent_demotion_passes` | green: the control | DEC-398, DEC-360 |
| `test_an_agent_merge_that_keeps_the_owner_file_over_an_agent_file_at_the_same_path_fails` | green: flagged as built. It pins the residual batch 3 left | DEC-398 |
| `test_an_owner_merge_that_keeps_active_over_the_demoted_line_passes`, `test_an_owner_merge_that_keeps_the_moved_file_over_the_demotion_passes` | green: the controls | DEC-360 |
| `test_an_owner_merge_that_cannot_be_judged_against_one_merge_base_passes` (4 cases) | green: the controls | DEC-398, DEC-360 |
| `test_an_agent_merge_of_two_crossed_lines_that_both_hold_the_approved_file_passes` | green: the control | DEC-398 |
| `test_an_agent_merge_with_too_many_parents_that_sets_active_again_does_not_pass` | green: flagged as built, which reads the merge itself. It pins that a checker which reads merges through a helper that refuses this one does not turn the refusal into a pass | DEC-398, DEC-410 |
| `test_an_agent_merge_of_a_branch_that_only_moved_an_approved_decision_passes`, `test_an_agent_integration_merge_of_a_branch_where_the_owner_added_a_decision_passes`, `test_an_agent_merge_that_brings_nothing_about_decisions_passes`, `test_an_old_branch_merged_late_into_a_line_where_the_owner_approved_passes` (2 cases), `test_the_main_line_merged_back_into_a_ticket_branch_and_the_branch_merged_passes` | green: the controls, everyday merges | DEC-398, DEC-394 ("an ordinary integration merge and an ordinary merge-back stay silent") |

Expected red reason, by line: success 2, `no ACTIVE_UNAPPROVED finding names ...` (7 cases); failure 1,
`no FRONTMATTER_UNREADABLE finding names the file ...` (5) and `no finding names the file ...` (1). **Can it go
green:** no reference checker was run this batch, because the helper is not in this tree and is not to be stood
in for. Each red case's fixture is asserted in the test (the merge is `HEAD`, has the parents and the merge bases
the case says, and holds the file the case says), and each expected result was derived from the rule above by
hand; "What the rule gives, case by case" shows the derivation.

What the designer settled from the sources, each open to the lead's correction:

- **Which package DEC-398 answers.** DEC-398 says "package DP-6 option (b)". That is the lead's package on how the
  approval rule reads merges, not the designer's text of batch 4, whose option (b) said the opposite of what is
  decided. The designer did not see the lead's package; the rule here is DEC-398's own words ("judges a merge
  against the merge base ... fails closed") as the brief for this batch states them in full. If the lead's option
  (b) says something else about a concurrent demotion, the two cases of
  `test_an_agent_merge_that_keeps_active_over_a_concurrent_owner_demotion_fails` are the ones to look at.
- **A concurrent demotion.** One side sets `ACTIVE`, the other demotes or removes, neither later; an agent's merge
  keeps `ACTIVE`: `ACTIVE_UNAPPROVED`. The demoting side changed the status since the merge base, so the merge is
  the change. The owner's such merge passes.
- **The owner's file kept over an agent's** at a path both added, by an agent's merge: `ACTIVE_UNAPPROVED`. Both
  sides changed the decision's presence since the merge base, and one `ACTIVE` parent was set by an agent.
- **A moved file** is the same decision (DEC-387: followed by its `id`). See "The merge rule".
- **The three false alarms are findings.** DEC-398 says the rule fails closed with several merge bases; DEC-403
  and DEC-410 (DP-23) say that with several merge bases or none every path that differs from any parent is the
  merge commit's own, "also where it keeps what its first parent holds"; no decision excepts decision files. So:
  (1) an unrelated history that never held the decision, merged by an agent into a line where the owner approved
  it, is a finding for every `ACTIVE` decision of that line; (2) an unrelated history that holds an
  owner-approved decision, imported by an agent below a folder, is a finding for each such decision; (3) two
  crossed lines on each of which the owner set the decision `ACTIVE`, with two texts, merged by an agent, is a
  finding. A fourth, the plainest: (4) two crossed lines, the owner approves on one, an agent's ordinary merge
  brings it to the other. In each the owner's merge passes. All four are accepted false alarms of "fails closed";
  (1) and (4) are the ones everyday work can meet.
- **Where "fails closed" stops.** Two crossed lines that hold the same file of the decision: the merge has nothing
  to be trusted for and passes. Without this every merge of two crossed lines would fail every decision.
- **The helper refusing** is reachable through a history: a merge commit with 25 distinct parents. One case.

**What the rule gives, case by case** (M is the merge in `HEAD`; "base" is the merge base of its parents):

| Case | Base holds | The parent M keeps | The other parent | So |
|---|---|---|---|---|
| the demoted line merged an old branch | `ACTIVE` (the owner's approving commit) | `work`: `ACTIVE`, unchanged | the main line: `PROPOSED` or no file, changed | M is the change; an agent's fails |
| a moved file over a demotion | `ACTIVE` at the old path | `move`: `ACTIVE`, same id, moved only | the main line: `PROPOSED` or no file, changed | M is the change |
| a second merge keeps the owner's file | `ACTIVE`, the owner's file (the side branch's earlier tip) | `side`: `ACTIVE`, unchanged | the main line: `ACTIVE`, set by an agent's commit and an agent's merge | an `ACTIVE` parent's setting commits lack the fact; fails |
| a concurrent demotion | `ACTIVE` | the branch: `ACTIVE`, set again by the owner | the main line: changed | M is the change |
| the owner's file over an agent's | no file | the owner's branch: added | the main line: added by an agent | M is the change, and an `ACTIVE` parent lacks the fact |
| an old branch merged late; a merge back; an integration merge | the state before the approval | the approved line | unchanged since the base | M sets nothing; the owner's commit is the fact |
| two crossed lines; unrelated histories | several, or none | any | differs, or does not hold the file | M is the change |

## The decided packages of batches 3 and 4

| Package | Question | Answer |
|---|---|---|
| DP-5 (batch 3) | What a Markdown file is whose `---` is not its first line | **DEC-387**, option (a): `FRONTMATTER_UNREADABLE`, with a first line such as `--- # c`, CR-only line ends and UTF-16. A decision with `type: decision` and no `id` fails. |
| DP-6 (batch 4, and the lead's package on reading merges) | A decision one side of a merge sets `ACTIVE` and the other demotes; how the rule reads a merge | **DEC-398** (owner): the merge base rule, one helper shared with containment, fail closed with several merge bases. |
| DP-7 (the lead's) | Tampering in the root's own `.git` | **DEC-387**, option (a): git runs with replace refs off; a loose object overwritten in place is a residual. |

The texts of DP-6 and DP-5 as batches 4 and 3 returned them follow, for the record. They are closed.

## Open package

**DP-8 (batch 5): how the checker learns whether the parent a merge drops changed the decision since the merge
base.**

- **Question.** The rule needs, for a merge that holds a decision `ACTIVE`, each parent's state of the decision
  against the merge base. The helper, as described to the designer, answers in paths: `own` and `brought`. Where
  the merge keeps one parent's file whole and that parent changed it since the base, the path is `brought`,
  whether the other parent left it alone (an ordinary integration merge: passes) or changed it too (a concurrent
  demotion; the owner's file over an agent's; a moved file over a demotion at the old path: fails). The two lists
  are the same in both. The outside rule that makes "a path more than one parent changed" the merge's own
  (DEC-410, DP-24) holds under `tests/acceptance/**` only. So the helper's lists cannot carry the rule for these
  merges; the checker needs the decision's state at the merge base from somewhere.
- **Why now.** The engineer builds the rule next, and "the checker reads a merge only through the helper"
  (DEC-398) leaves no stated way to get it. Five cases turn on it: the two concurrent cases and the owner's file
  over an agent's (green as built, and they must stay so), and the two moved-file cases (red).
- **Options.** (a) The checker asks git for the merge base itself, only for a parent pair for which the helper
  listed a path as `brought` (the helper has then found exactly one base), and reads the decision's state in that
  commit by its `id`. The helper stays the only judge of `own` against `brought` and of "fails closed". (b) The
  helper gains what it already computes: the merge base it used for each parent, or a third list of the paths
  that more than one parent changed against the base. W1-50's interface changes before it is merged (DEC-415
  foresees this; "owner decision: early test design" for W1-50's suite). (c) The checker keeps an ancestry rule
  of its own for these merges, as built. It is a second way of reading merges, and it is the rule the three
  reviewed histories defeat.
- **Impact.** (a) one more git call per merge that brings a decision; two places name a merge base, and they can
  only disagree where the helper would have failed closed, which (a) excludes by asking only after `brought`.
  (b) one reading of merges in the strict sense; a change to a helper that had seven review rounds, and W1-50's
  suite gains cases. (c) the fail-open holes stay.
- **Reversibility.** (a) and (b) high: the cases here assert results only and stay as they are under either.
- **Cost.** (a) about 10 lines in the checker. (b) about 10 lines in the helper, its cases, and the same use in
  the checker. (c) none.
- **Recommendation.** (a), unless W1-50 is still open for a change at no cost, then (b). **Confidence:**
  medium-low: the designer has not seen the helper, only its description.
- **Dependence.** No case waits on it. The engineer's work depends on it: it decides where the state at the merge
  base comes from. It touches containment's helper under (b), so it is not the orchestrator's to delegate lightly
  (DEC-416 excludes containment).

## Closed packages, as returned

**DP-6 (batch 4): a decision one side of a merge sets `ACTIVE` and the other side demotes, neither later.**
Decided by DEC-398; in the terms of the options below the result is (a).

- **Question.** Two lines of history part from a commit where the decision is `ACTIVE` (or `PROPOSED`). On one,
  the owner's commit sets or keeps it `ACTIVE` with a change of its own (sets it `ACTIVE` again after a demotion
  there, or edits the body). On the other, a commit demotes it or deletes its file. Neither commit descends from
  the other. An agent's merge keeps the `ACTIVE` side. Is the merge the commit that sets `ACTIVE` (it fails), or
  is the owner's commit on the kept side still the fact (it passes)? The same question for the residual batch 3
  left: a merge that keeps the owner's file over an agent's at a path both added.
- **Why now.** The review's four merges are all the simple form (the demotion descends from the approval) and
  the sources decide them. A repair has to pick a rule for a merge, and whatever it picks answers this case too,
  without a decision behind it.
- **Options.** (a) Fail closed: a merge that holds a decision `ACTIVE` where a parent holds it with another
  status, or without its file, sets it `ACTIVE` unless that parent's state is one the kept side's setting commit
  descends from; the merge then needs `Role: owner`. (b) The owner's commit on the kept side stays the fact; the
  agent's merge sets nothing unless the demotion descends from that commit. (c) Leave it a residual: the suite
  asserts nothing, the engineer's rule stands and is recorded.
- **Impact.** (a) an agent cannot resolve a disagreement about a decision's status in favour of `ACTIVE`; the
  owner makes that merge. An integration merge by an agent fails the check when two branches disagree on a
  status, which is rare and is a real disagreement. (b) an agent chooses between two owner statements, or between
  the owner's `ACTIVE` and another agent's demotion. (c) the behaviour is whatever the repair yields.
- **Reversibility.** High for each: one rule and two or three cases.
- **Cost.** (a) or (b): about 10 lines in the walk and 2 to 3 cases. (c) none.
- **Recommendation.** (a): CAP-01.b and DEC-360 want the owner's fact on the change that makes a decision
  `ACTIVE`, and choosing `ACTIVE` over a concurrent demotion is such a change. **Confidence:** medium.
- **Dependence.** No repair of the 9 red cases depends on it: every rule that flags the four merges and keeps
  the three merge controls green passes the suite under (a), (b) and (c). Two or three cases wait on it and are
  not written.

**DP-5 (batch 3): what a Markdown file is whose `---` is not its first line.** Decided by DEC-387, option (a).

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
- **A merge commit that itself sets the status** (its file differs from both parents'), other than over a
  demotion that descends from the owner's approval (batch 4 tests that one). Batch 3 tests the merges that set
  nothing and the merge that keeps the agent's file; batch 5 the concurrent forms and the owner's file kept over
  an agent's (DEC-398).
- **An agent's merge over a demotion that an agent made**, and a merge with three to 24 parents. Batch 5 tests a
  removal by the owner, and one merge with 25 parents.
- Batch 5, merges, each failing closed or passing between owner commits, so none is a fail-open hole (DEC-413):
  - **The owner set the decision `ACTIVE` on both sides of a merge with one merge base** and an agent's merge
    keeps one text, or both sides hold the same text. By the rule's words the other parent changed the status
    since the base and the merge is the change; every setting commit is the owner's. Not asserted, and not run
    against the checker as built.
  - **The owner's merge where an `ACTIVE` parent was set by an agent** (the owner's file kept over an agent's;
    the second merge of the third reviewed history, made by the owner). Whether the owner's merge is then the
    fact is not asserted.
  - **A merge with more than 24 parents that touches no decision**, in a register the owner approved: a finding,
    a `GovError` or a pass is not asserted. Only "no pass where an agent set `ACTIVE`" is.
  - **Two crossed lines or an unrelated history deep in the history**, not at `HEAD`: the same rule holds at
    every merge the walk meets; only merges at `HEAD` are tested. **Nobody has run the rule over this
    repository's own history.** W1-50 replayed 174 real merges for containment (DEC-401); the same replay for
    the approval rule is the engineer's or the reviewer's.
  - **A moved file whose `id`, `status` or text also changes in the move**, a file moved on both sides, and a
    decision that one side moves while the other edits its text and keeps it `ACTIVE`.
- **An agent's commit that renames a decision the owner approved**, in a straight line, was reported flagged by
  the checker as built (a review's note; not run here). By the rule it sets nothing and passes. Batch 5 tests the
  move on a branch that an agent merges, which passes as built.
- **A rename that also changes the `id` or the body**, and a decision whose file is deleted and added again.
- **A decision that is `ACTIVE` only in the working tree.** Every checked fixture is committed.

The repository and the environment (batch 4), not tested:

- **A missing commit or tree object.** The checker as built raises `GovError` for each (a probe outside the
  repository, 2026-10-05). It fails closed, so it is recorded and not tested (DEC-135). Batch 4 tests the missing
  version of the file, which passed.
- **A shallow clone**, whose earlier commits are absent by design, and a partial clone made with another filter
  (`tree:0`). Whether a partial clone of an owner-approved register can pass without fetching is not asserted.
- **Other git variables.** With `GIT_OBJECT_DIRECTORY` or `GIT_COMMON_DIR` naming a clean repository the checker
  as built raises `GovError`; with `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_CEILING_DIRECTORIES` or `GIT_NAMESPACE`
  it returned the finding of `root` (the same probe). `GIT_ALTERNATE_OBJECT_DIRECTORIES`, and an object directory
  that holds the root's commits with other files, were not tried. Only `GIT_DIR` is tested.
- **`GIT_DIR` naming a repository with findings while `root` is clean**: the other repository's findings would be
  reported for `root`. It fails closed and is not tested.
- **A `root` that is a folder inside a repository, with no variable set**: `GovError` as built; no source says.
- **Files written outside `root`** (the temporary directory, `HOME`) are not compared.

Gates, not tested:

- `approval` that is empty, a scalar, or names one id twice; a `cit` that is empty or not a string; two records with
  the cited id; a package that does not load (W1-09 residual).

Hazards, as in batch 1:

- Batch 5 (DEC-387), residuals by decision, no case: an id outside the `decision_id` grammar in a file with no
  `type`; the extensions `.MD` and `.markdown`; a loose object overwritten in place in the root's own `.git`
  (left to W1-50 and the worker sandbox).
- Other heads that look like frontmatter (a first line of spaces before `---`, `---` followed by spaces alone,
  UTF-16 without a byte-order mark, UTF-32) are not tested: DEC-387 names five.
- Frontmatter that is valid YAML and no map (a list, a scalar), and a key other than `approval` written twice
  (`status`, `id`), are not tested.
- Status values in another case, and a superseder that is itself `PROPOSED`, are not tested.
- Overlapping ids are tested only for identical digit strings (`ADR-003`, `DEC-003`); `ADR-0001` beside `DEC-001`
  is not. This repository's own two series (ADR files, DEC headings in the register) are not both files yet.
- Two overlapping ids inside one directory are not tested: the KPI says "across directories".
