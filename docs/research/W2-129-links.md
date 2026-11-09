# W2-129 `gov links`: the engineer's record

The engineer's record for W2-129 (`DAEO-q7lk`, DEC-1073 (5)(b), DEC-1088 (6), design `LINK-INTEGRITY.md` §4). It
covers:
- each finding code's form;
- the readings chosen where the KPI and §4.4 leave a detail open;
- the `--all` run's counts by code and role, and the timing;
- S8's parity with W2-92's drift script;
- one row of evidence per KPI line.

The code is `src/gov/links/` (`check.py`, `patch.py`, `command.py`); the unit tests are `tests/unit/links/test_links.py`.

The KPI success lines are numbered S1 to S16 in the ticket's order: S9 is the role table, S10 the incremental line,
S11 the output, S12 the patches, S13 never a gate, S14 any repository, S15 the timing and S16 the ticket changes. The
first pass of this record numbered them wrongly from S9 on; §7 is corrected.

## 1. The run measured (second pass)

- **Head:** `90ddd18a01ce` (`w2/W2-129`: `w2/integrate` at `a1d3e81a9`, the designer's S16 cases and this ticket's
  code). It is one commit behind integrate's head `416b59da1779`.
- **The tree: the engineer's worktree, not the main tree.** The launch sandbox keeps the main tree read-only, so the
  tool cannot write its mark there. A scratch folder whose `.git` names the main repository was refused as a
  sensitive write; the refusal was taken. The CTO's measured run on the main tree is §1a (S15).
- **The mark:** the sandbox also keeps this worktree's `.gov-runtime/` read-only. Each run named
  `LINKS_MARK_UNWRITTEN` on stderr and printed its findings (§4 reading 2). With no mark, `--all` judged the whole
  history.
- **The command:** `PYTHONPATH=src python3 -m gov.cli.main links …`, through `heavy_slot.sh`, timed from outside the
  process by `perf_counter`. No model, network or GPU; no store.
- **CPython 3.12.3, PyYAML 6.0.1 with libyaml.** The frontmatter is read with the C loader.

| Command | Five runs (s) | Median |
|---|---|---|
| `gov links --all` | 2.82, 2.81, 2.80, 2.74, 2.77 | **2.80 s** (bound 10 s) |
| `gov links --since HEAD~1` | 2.79, 2.80, 2.83, 2.83, 2.89 | **2.83 s** (bound 5 s) |

- The first pass measured 2.52 s and 2.34 s at `422aac40581a`. S16 adds about 0.3 s: one `git log --raw` over the
  ticket folder (685 commits touch it) and one `cat-file --batch` of the blobs before and after.
- `--since` costs about the same as `--all`, because every run reads the whole record set and every commit (S10).
- About 1.7 s of each run is W2-55's `check_propagation`, used as it stands.

## 1a. The CTO's measured run on the main tree (S15)

Measured by the CTO on the main tree at `416b59da1779` (`w2/integrate`), median of five runs each:

| Command | Median |
|---|---|
| `gov links --all` | **3.14 s** (bound 10 s) |
| `gov links --since HEAD~1` | **2.94 s** (bound 5 s) |

The first `--all` gave **3,037 standing findings**. These are the clean-up's baseline:

| Code | Role | Count |
|---|---|---|
| UNMARKED_CHANGE | orchestrator | 188 |
| UNKNOWN_ID | independent-test-designer | 381 |
| UNKNOWN_ID | orchestrator | 56 |
| UNKNOWN_ID | owner | 1 |
| UNKNOWN_ID | product-spec | 3 |
| UNLINKED_ID | orchestrator | 1,897 |
| STATUS_CONFLICT | orchestrator | 110 |
| STATUS_CONFLICT | product-spec | 6 |
| NOT_IN_FORCE_AS_RULE | orchestrator | 35 |
| NOT_IN_FORCE_AS_RULE | product-spec | 106 |
| ENFORCES_SUPERSEDED | independent-test-designer | 44 |
| CLOSED_TICKET_EDITED | orchestrator | 117 |
| TICKET_CHANGE_UNMARKED | orchestrator | 93 |

- The main tree has 27 fewer UNKNOWN_ID findings for the test designer than this worktree (381 against 408). 25 of
  the worktree's are in `tests/acceptance/W2-129/` (counted by path from `--json`), which `w2/integrate` does not hold
  yet; the other 2 are not traced.
- This baseline is from the code before review round 2. Round 2 (§8) takes out the one UNMARKED_CHANGE whose changer
  is PROPOSED (DEC-056 <- DEC-017), and adds no TICKET_CHANGE_UNMARKED on this history.

## 2. The `--all` run: counts by code and role

3,065 findings at `90ddd18a01ce`. 29 of them are free-text findings (all UNMARKED_CHANGE).

| Code | Role | Count | First pass (`422aac40581a`) |
|---|---|---|---|
| UNMARKED_CHANGE | orchestrator | 188 | 187 |
| UNKNOWN_ID | independent-test-designer | 408 | 405 |
| UNKNOWN_ID | orchestrator | 55 | 55 |
| UNKNOWN_ID | product-spec | 3 | 3 |
| UNKNOWN_ID | owner (a commit whose `Role:` is `owner`) | 1 | 1 |
| UNLINKED_ID | orchestrator | 1,899 | 1,891 |
| STATUS_CONFLICT | orchestrator | 110 | 110 |
| STATUS_CONFLICT | product-spec | 6 | 6 |
| NOT_IN_FORCE_AS_RULE | product-spec | 106 | 106 |
| NOT_IN_FORCE_AS_RULE | orchestrator | 35 | 35 |
| ENFORCES_SUPERSEDED | independent-test-designer | 44 | 44 |
| CLOSED_TICKET_EDITED | orchestrator | 117 | (new) |
| TICKET_CHANGE_UNMARKED | orchestrator | 93 | (new) |

- No commit's finding has a landed lead on this repository. The commits with an unknown `Task:` or `Implements:` are
  on the first-parent line, or their `Role:` is orchestrator.
- The 210 S16 findings touch 72 tickets in 60 commits.
  - CLOSED_TICKET_EDITED, by the fields the edit changed: `depends_on` 52, `status` 14 (a reopening), `body` 11,
    `sources` 11, `state_class` 10, `deps` 7, `status, allowed_paths` 6, `links` 2, three others.
  - TICKET_CHANGE_UNMARKED, by field: `kpis` 51, `allowed_paths` 29, `depends_on` 13.

The first pass's counts by place (at `422aac40581a`) stand for the six older codes:

| Code | Place | Count |
|---|---|---|
| UNKNOWN_ID | a test file (`DEC-n`, `W1-3-n`) | 405 |
| UNKNOWN_ID | `acceptance_tests.path` (in-progress and closed tickets) | 43 |
| UNKNOWN_ID | a commit's `Task:` | 13 |
| UNKNOWN_ID | a ticket's `sources`; a record's `task`; a kernel line | 1 each |
| UNLINKED_ID | a worker commit's `Implements:` (616 DEC, 538 CAP) | 1,154 |
| UNLINKED_ID | KPI brackets (310 W, 219 CAP, 205 DEC, 3 MR) | 737 |
| STATUS_CONFLICT | current in the register, spent in ARCHIVE §B | 110 |
| STATUS_CONFLICT | MR-1 to MR-6 PROPOSED against `contract.yaml` ACCEPTED (expected: the CTO's point (10)) | 6 |
| NOT_IN_FORCE_AS_RULE | `CONTRACT_v4.md` lines | 99 |
| NOT_IN_FORCE_AS_RULE | a register entry's `**Under:**` | 28 |
| NOT_IN_FORCE_AS_RULE | a kernel line | 7 |
| NOT_IN_FORCE_AS_RULE | a commit's `Implements:` | 3 |
| NOT_IN_FORCE_AS_RULE | KPI brackets (2), sources (1), a brief or prompt line (1) | 4 |

What the counts say:
- DECISIONS-IN-FORCE agrees with the register: no conflict.
- No `contract.yaml` provider or source names an unknown id.
- UNLINKED_ID is large because the KPI asks for every id in `sources:`. That includes W ids and CAP ids, and the
  `Implements:` of every worker commit in history. `--propose-sources` prints the patch for all of them.

## 3. Each finding's form

One line per finding:

```
<CODE> <subject>[ (text)] | <path>:<line> | <role> | <fix>
```

- The four fields are separated by ` | `. A `|` inside a field is written `/`.
- `(text)` ends the first field when a free-text pattern found the finding. That covers the register's free text,
  its change log, and ARCHIVE-SUPERSEDED §A.
- `--json` gives the same findings in gov's envelope: `{ok, command: "links", result, session}`.
  - Each finding carries `code`, `ids`, `path`, `line`, `role`, `fix`, `subject`, `text` and `new`.
  - It also carries:
    - `commit` for a commit's finding, and `lead` (`orchestrator`) when that commit has landed;
    - `via` for the other places that stated it;
    - `whole`, `form` and `mark` for UNMARKED_CHANGE;
    - `field` for the two S16 codes.

| Code | Subject | Where the line points | Fix |
|---|---|---|---|
| UNMARKED_CHANGE | `DEC-x <- DEC-y (<form>; whole\|part)` | the register, DEC-x's status line | `add "SUPERSEDED by DEC-y"` (whole) or `add "**Changed by:** DEC-y (part)"` |
| UNKNOWN_ID | `<id or path> in <owner>'s <key>` / `in a kernel line` / `in a test file` / `in <sha12>'s Task:` | the place | correct or remove it; for a commit, name the id it should have named (history is not rewritten) |
| UNLINKED_ID | `<id> in <ticket>'s KPI brackets, not in its sources` / `<id> in <sha12>'s Implements: (<role>), not in <ticket>'s sources` | the ticket's `sources:` line | `add <id> to <ticket>'s sources:` |
| STATUS_CONFLICT | `<id> <status> in the register, spent in ARCHIVE-SUPERSEDED §B` / `… listed in DECISIONS-IN-FORCE` / `<ticket> <status> against its close record <CL> <status>` / `MR-n <status> against contract.yaml <status>` | the list line, the ticket's `status:`, the MR record's `status:` | reconcile the two |
| NOT_IN_FORCE_AS_RULE | `<id> (<STATUS>) in <place>` | the place | decide it, or cite it as proposed (or rejected, …), not as a rule |
| ENFORCES_SUPERSEDED | propagation's own message | the path and line propagation names | cite the decision in force, or record a `**Kept:**` reason |
| CLOSED_TICKET_EDITED | `<ticket> <sha12> <fields changed>: closed before the commit` (`body` when no frontmatter field changed; `the file (deleted)`) | the ticket's file, the commit's first changed line | revert the edit, or carry the change in a new ticket |
| TICKET_CHANGE_UNMARKED | `<ticket> <sha12> <field>: changed with no DEC-n in the lines, Implements: or Decided-by:` | the ticket's file, the field's key line at HEAD | name the decision behind the change (a DEC-n in a commit's `Implements:` or `Decided-by:`), or revert it |

Both S16 codes are orchestrator's. One TICKET_CHANGE_UNMARKED is listed per field changed.

The first line:

```
gov links: N new since <rev>, M standing (<CODE> <role> <n>, …; records R, register E entries, commits C[; not applicable: …])
```

## 4. The readings chosen

Where neither the KPI nor §4.4 states a detail, the tool takes the simplest form below. Each is pinned by a unit test.

1. **`<rev>` in the first line:**
   - the `--since` argument as given;
   - otherwise the mark as stored (HEAD's full sha);
   - `root` for `--all` with no mark and no `--since`, which judges the whole history, so every finding is new.
   - The KPI says "with neither it refuses". That holds for a bare run, which exits 2 naming `--since`.
   - `--all` with neither runs, because the acceptance cases run it that way.
2. **The mark** holds HEAD's 40-character sha and nothing else, with no newline. Every run that can run writes it.
   The two `--propose-*` options write nothing and need no range.
   - **A mark it cannot write** (a read-only tree, as in the launch sandbox) is named on stderr,
     `LINKS_MARK_UNWRITTEN`. The findings and the exit code are unchanged, and the next run judges from the previous
     mark, a wider range. A notice does not fail on its one side effect. Unit:
     `test_a_mark_it_cannot_write_is_named_and_the_findings_stand`.
3. **Exit codes:** 0 with no new finding (also when `--all` lists standing ones), 1 with a new finding, 2 when the
   run cannot be made. A run that cannot be made is named on stderr or in the JSON error:
   - `LINKS_NOT_A_WORK_TREE`, `LINKS_NO_HEAD`;
   - `LINKS_NO_RANGE`, `LINKS_BAD_REV`, `LINKS_MARK_UNKNOWN`;
   - `STORE_REGISTER_UNREADABLE`, the loader's own.

   The patches end with 0. The exit code goes through `CHILD_EXIT_CODE`; `cli/main.py` is unchanged.
4. **"New" (S10):**
   - A commit's finding is new when the commit is in the range. That includes the two S16 codes: a ticket change
     is listed only when its commit is in the range, and is counted as standing otherwise.
   - A record file (one with a frontmatter id) changed in the range makes every finding in it new.
   - Any other file is judged by line: a finding is new when the range added or changed its line. This covers a hand
     list, a kernel text, a brief, the path map, `contract.yaml` and the test files.
   - The register is judged by entry: a finding there is new when one of its ids is an entry whose own text changed,
     the changer's new entry among them.
   - A STATUS_CONFLICT, NOT_IN_FORCE_AS_RULE or ENFORCES_SUPERSEDED finding is also new when its decision's status
     word changed. A finding stated elsewhere (`via`) is new when that place changed: an ARCHIVE §A line, a close
     record, `contract.yaml`'s status line.
   - "An entry a changed entry names" is met through the changer: its new statement's finding sits on the named
     entry's status line and is new because the changer changed.
   - The named entry's older findings stay standing.
5. **Commits and their role (S9):** every commit is judged on every run, so no finding older than the mark is lost
   (F5). One about a commit outside the range is standing.
   - A commit's trailers are read as the loader reads them: its final trailer block, or the whole message before
     2026-10-03 (DEC-182).
   - **The role field names the commit's `Role:` trailer** (for example `independent-test-designer`). A commit with
     no `Role:` names `orchestrator`. The fix text no longer carries the role.
   - **Once landed**, the finding also names the ticket's lead: `lead: orchestrator` in `--json`. A commit counts as
     landed when it is not on HEAD's first-parent line. The counts by role use the role field.
   - **Where this departs from the brief:** the brief asked for the text line's role field to read
     `independent-test-designer; once landed: orchestrator`. That form passes S9's commit case but fails one other
     acceptance case, mapped to S9 and F3, so `gov accept` gave 134/1. With the bare `Role:` in the role field and
     the lead in `--json`, `gov accept` gives 135/0. The engineer does not read the cases; the probe runs are in §6.
     To print the lead in the text line, `render` in `check.py` is the one line to change, once the case allows it.
   - Worker commits are those whose `Role:` is one of the five worker roles; landing commits never give an
     UNLINKED_ID.
6. **Ids:** the store's grammars (common.schema.json):
   - `(DEC|ADR)-n{3,}`, `CAP-nn[.x]`, `MR-n`, `W<n>-nn[x]`, list rows `W<n>-<L>n`, `L-nnnn`;
   - ticket ids by the prefixes the project's own tickets use.

   A typed value names an id by its first token, the loader's rule ("DEC-954 Q9c" names DEC-954). A value whose first
   token is in no grammar is free text, not a finding (`contract.yaml`'s "MADR + check-jsonschema").

   An id resolves when one of these holds it:
   - a register entry;
   - a frontmatter `id`, or a `wbs_id` / `external-ref` alias;
   - an id in `contract.yaml` (capability, item, master rule, the Contract's own);
   - a row's first cell or a card heading in `docs/plan/**.md` (the list file).

   `Task: decision-record` is not a finding (DEC-861).
7. **Test files:** only the census's two patterns, `DEC-n` and `W[1-3]-n` (`D4B-link-census.py` §5). The other
   grammars in tests are planted stand-ins far more often than citations: reading them all gave 983 findings, against
   405 at the first pass.
8. **Kernel lines:** every line of `template/governance/kernel/{roles,skills,templates}/**`, the vendored superpowers
   skills excepted.
   - UNKNOWN_ID reads the ids inside `(…)` or `[…]`, which is how those texts bracket a citation ("(DEC-066, MR-5)").
   - NOT_IN_FORCE_AS_RULE reads every decision id on the line.
   - Briefs, prompts and `CONTRACT_v*.md` are read by line; the path map's comments only.
9. **ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE** are looked for in `governance/project/orchestration/` (the CTO's
   point (5)).
   - §A is the text from its `## A` heading to the next `## ` heading. Each `- DEC-x…: … <verb> by DEC-y` line is read
     with the loader's `_BY` pattern, as the drift script reads it.
   - §B is read the same way, a line counting as spent when it holds "Spent" or "spent". The drift script reads from
     `## B.` to the file's end, which takes in §C's "DEC-038 to DEC-063 … Spent". This tool keeps to §B.
   - An id is "listed in force" when it sits in the lead of a top-level bullet (before its first `:`) in any section
     but "Lifted".
10. **"Current" for §B:** a status not in PROPOSED, REJECTED, WITHDRAWN, SUPERSEDED or DONE, and not superseded or
    done by `gov.decisions.register.read`. A PROPOSED decision is never current.
11. **UNMARKED_CHANGE "names no such changer":** the target's status line (its first line) does not hold the
    changer's id. That is the line `--propose-marks` writes and the line `gov.decisions.register` reads `Changed by:`
    from. A hint elsewhere in the entry does not count, as LINK-INTEGRITY §3 item 2 has it ("the changers their status
    line misses").
    - **Whole:** the statement is a supersession and `register_statements` says it names ids alone. This is the
      loader's SUPERSEDES rule.
    - An `**Amends:**` naming ids alone is a part with no part named.
    - **The part:** the text after the target id in the stating entry ("(item 2)", "Q5", "§3").
12. **Whole or part, the CTO's point (3):** `register_statements` decides, and it reads `**Supersedes:** DEC-x`
    followed by plain body text as a part. Its label value runs on to the next label and is not ids alone. The
    loader's own SUPERSEDES edge reads the status line alone and calls it whole. The tool follows
    `register_statements`; the unit case
    `test_a_supersedes_followed_by_plain_text_is_a_part_as_register_statements_reads_it` pins it.
13. **STATUS_CONFLICT, ticket against close record:** a close record whose status is not SUPERSEDED, WITHDRAWN,
    REJECTED, REVOKED or REFUSED says the ticket is closed. A conflict is a disagreement with the ticket's
    `status: closed`.
14. **STATUS_CONFLICT for a master rule:** a record whose id is a `contract.yaml` master rule, with a status other
    than `contract.yaml`'s own top-level `status`.
15. **The patches:**
    - `--propose-marks` appends ` · SUPERSEDED by DEC-y` or ` · **Changed by:** DEC-y (part)` to the status line,
      with one entry's changers on one line.
    - `--propose-sources` adds the ids to `sources:`: a block list, a flow list, a scalar made a list, or a new key.
    - Both are unified diffs with 3 lines of context against HEAD's text. The unit tests apply them with `git apply`
      and see the findings clear.
16. **Ticket changes (S16, DEC-1088 (6)):**
    - **The commits read:** every non-merge commit that changes a file under `.tickets/`
      (`git log --full-history --raw`, so a side branch's commits are not simplified away). A merge's changes are its
      parents' commits'. A commit that adds a ticket is not a change of one.
    - **Closed** is the ticket's `status` in the commit's parent. Any change to that file is CLOSED_TICKET_EDITED: an
      edit, a reopening, a deletion. A decision id in the lines or the trailers does not excuse it.
    - **Open** is `open` or `in_progress` in the parent. A field changed is a field whose parsed frontmatter value
      differs between the parent and the commit, among `title`, `kpis`, `allowed_paths`, `reads`, `needs`,
      `waits_on`, `depends_on` and `acceptance_tests`. Any other field (`status`, `assignee`, `links`, `sources`, …)
      and the body are not findings.
    - **The commit that closes the ticket** (open in the parent, closed in the commit) is not a finding, whatever
      else it changes.
    - **Marked:** a `DEC-n` in a line the commit removed or added in that ticket's file (the lines that are not in
      both versions), or in the commit's `Implements:` or `Decided-by:` trailers, read as the loader reads trailers.
    - **The line:** for TICKET_CHANGE_UNMARKED, the field's key line in HEAD's copy of the ticket (the commit's copy
      if the ticket is gone); for CLOSED_TICKET_EDITED, the first line the commit changed.
    - The short sha is the first 12 digits, as in the other commit subjects.

## 5. S8's parity with `docs/research/W2-92-proto-drift.py`

Both were run `--from-head` at the worktree's head before this ticket's first commit (first pass).

| | Count |
|---|---|
| The drift script's drifting list (current, spent left out) | 194 |
| Decisions UNMARKED_CHANGE names (187 pairs) | 151 |
| In both | 128 |
| Drifting, not named: **every changer already on its status line** (checked one by one; none missing) | 66 |
| Named, not drifting: PROPOSED 11, SUPERSEDED 1, DONE 1, spent (ACCEPTED, on the reconciliation list) 10 | 23 |

- Every drifting decision is named, or already marks all its changers on its status line.
- Every decision named but not drifting is outside the drift script's "current" (DEC-1073 (2)). Three of them are
  whole supersessions only (the CTO's point (4)).
- The statements are the loader's `register_statements`, imported. §A is read with the loader's `_BY` and
  `_verb_class`. There is no second pattern set.

## 6. `gov accept W2-129`

**135 passed, 0 failed, 0 skipped** (HOME=/home/usain), at the second pass's code. S16's 32 cases pass.

The S9 role, probed through `gov accept` (counts only; the engineer does not read the cases, DEC-957, DEC-1056):

| The role field of a landed commit's finding | `gov accept` |
|---|---|
| `orchestrator` (the first pass) | 134/1: S9 5/6, F3 2/2 |
| `independent-test-designer; once landed: orchestrator` in the text and in JSON `role` | 134/1: S9 5/6, F3 1/2 |
| the same in the text; JSON `role` the bare `Role:` with `lead` | 134/1: S9 5/6, F3 1/2 |
| the bare `Role:` in the text and JSON; JSON `lead: orchestrator` (kept) | **135/0** |

- The suffix form fixes S9's commit case but fails another case, mapped to S9 and F3. That case reads the text
  line's role field and accepts one role name there.
- The CTO can read both cases and decide whether the lead belongs in the text line. If it does, the case and
  `render` change together.

## 7. Evidence by KPI line

| KPI line | Evidence |
|---|---|
| S1 one read-only command, writes only its mark | `command.py` (CLASS read, no ACT_PATHS); units `test_the_mark_holds_heads_sha_alone_and_nothing_else_is_written`, `test_a_mark_it_cannot_write_is_named_and_the_findings_stand`; accept success-1 4/4 |
| S2 UNMARKED_CHANGE | `check.unmarked` (a PROPOSED, REJECTED or WITHDRAWN changer skipped, §8); units `test_unmarked_change_…`, `test_archive_section_a_…`, `test_a_supersedes_followed_by_plain_text_…`, `test_a_proposed_rejected_or_withdrawn_entry_is_no_changer` (and its ACCEPTED control); accept success-2 10/10 |
| S3 UNKNOWN_ID | `check.records`, `register_places`, `contract`, `texts`, `commits`; units `test_the_typed_places_of_tickets`, `test_records_contract_kernel_and_list_rows`, `test_commit_trailers`; accept success-3 22/22 |
| S4 UNLINKED_ID | `check.records`, `commits`; units as S3; accept success-4 5/5 |
| S5 STATUS_CONFLICT | `check.statuses`; unit `test_status_conflicts`; accept success-5 8/8 |
| S6 NOT_IN_FORCE_AS_RULE | `check.records`, `register_places`, `_rule_lines`, `commits`; accept success-6 18/18 |
| S7 ENFORCES_SUPERSEDED | `check.enforces` (W2-55's `check_propagation`, imported); unit `test_enforces_superseded_is_propagations`; accept success-7 2/2 |
| S8 one source of patterns | `register_statements` imported, §5 above; accept success-8 4/4 |
| S9 the role table, a commit's role | `check.ROLE_TABLE`, `role_of`, `commit_role_field`; units `test_role_table` (14 paths), `test_a_commits_finding_names_its_role_then_the_lead_once_landed`; accept success-9 6/6 (§4 reading 5, §6) |
| S10 incremental | `check.touched`, `is_new`; units `test_findings_older_than_the_mark_…`, `test_a_changed_entry_…`, `test_an_entry_a_changed_entry_names_…`, `test_a_status_changed_…`, `test_an_older_commits_finding_…`; accept success-10 8/8 |
| S11 output and exit codes | `command.run`, `check.render`; units `test_json_is_the_shared_envelope_…`, `test_cannot_run_exits_2_named`; accept success-11 7/7 |
| S12 the two patches | `patch.py`; units `test_propose_marks_…`, `test_propose_sources_…`; accept success-12 5/5 |
| S13 never a gate | nothing outside `src/gov/links` imports it; unit `test_never_a_gate_…`; accept success-13 2/2 |
| S14 any repository | `check.not_applicable`; unit `test_a_repository_without_the_kinds_is_not_applicable`; accept success-14 2/2 |
| S15 cheap, measured | §1a: the CTO's main-tree run at `416b59da1779`, `--all` 3.14 s and `--since HEAD~1` 2.94 s (median of five), 3,037 standing findings by code and role; §1 the engineer's worktree run (2.80 s and 2.83 s) |
| S16 ticket changes | `check.ticket_changes`; units `test_a_closed_tickets_file_edited_…`, `test_reopening_a_closed_ticket_…`, `test_an_open_tickets_scope_changed_unmarked_…` (4 fields), `test_marked_or_unwatched_ticket_changes_…` (7 forms; the closing commit's status change alone), `test_the_closing_commit_is_judged_as_any_other` (open, in_progress), `test_a_closing_commit_marked_by_a_decision_is_not_a_finding` (Implements:, Decided-by:), `test_a_decision_in_a_removed_line_…`, `test_a_ticket_change_is_listed_only_when_its_commit_is_in_the_range`; accept success-16 (§8) |
| S17 planted ids in test fixtures | `check.planted_spans`, `_Repo.planted`, `_planted_cite`; units `test_s17_*` (5); accept success-17 8/8, failure-7 7/7 (§9) |
| S18 a settlement is a change | `check.CHANGE_CLASSES` (`settle` added), `SETTLES_FORM`, `unmarked`; unit `test_s18_a_settles_label_is_a_change_as_an_amendment` (4 cases); accept success-18 6/6 (§10) |
| F1 to F5 | accept failure-1 to failure-5: 1/1, 4/4, 2/2, 5/5, 2/2 |

## 8. Review round 2 (`.gov-runtime/scratch/orchestrator/reviews/w2-129.md`, F1 to F3)

- **F2 (S16, blocked):** `ticket_changes` no longer skips the commit that closes a ticket. Its eight watched fields
  are judged as in any other commit against an open or in-progress ticket. An unmarked change is
  TICKET_CHANGE_UNMARKED, one per field. The status change itself, `assignee` and `links` still give nothing.
- **F1 (S2, failure-4):** `unmarked` skips a statement whose changer's status is PROPOSED, REJECTED or WITHDRAWN
  (`NOT_A_CHANGER`), wherever the statement stands: entry label, free text, change log or ARCHIVE §A. With no
  finding there is no mark, so `--propose-marks` prints none. A SUPERSEDED changer still counts, because its change
  took effect before it was itself superseded.
- **F3 (S15):** §1a holds the CTO's main-tree timing and baseline.
- **On this worktree** (`--all`, the round-2 code, head `5b8e73055223`): 3,065 findings.
  - UNMARKED_CHANGE is 187 (188 before). The one dropped is DEC-056 <- DEC-017, whose changer DEC-017 is PROPOSED.
  - TICKET_CHANGE_UNMARKED is 93 (unchanged). No closing commit in this history changes a watched field unmarked,
    as the review's probe found (0 of 152).
- **Units:** `tests/unit/links` 61 passed (55 before; 6 new cases).
- **`gov accept W2-129`** (HOME=/home/usain), on the round-2 code before the designer's F2 cases are merged:
  **135 passed, 0 failed, 0 skipped**; success-16 included, so the status-only close still gives nothing.

## 9. S17 (D-6 part 2, DEC-1109 (2)): planted ids in test fixtures

- **The change** (`check.py`, `src/gov/links/**` only; W2-55's `gov.decisions.propagation` is unchanged):
  - `planted_spans(text)` gives, per line, the character columns of a Python file that stand inside a string
    literal that is not a docstring: plain, triple-quoted, raw, bytes or f-string, assigned or not. The strings come
    from `tokenize`; on 3.12 an f-string is one span from `FSTRING_START` to its `FSTRING_END`, its `{...}` parts
    within. Docstrings come from `ast`: the first statement's string of a module, class or function (ast's byte
    columns turned into characters). A file that does not parse gives `None` and is judged as before. So does a file
    with a lone carriage return, where ast's line numbers and `str.split("\n")`'s differ.
  - `_Repo.planted(path, line, column)` parses each `tests/**/*.py` file at most once per run, and only when a
    finding asks.
  - UNKNOWN_ID (`texts`): a test-file id inside a planted span gives no line.
  - ENFORCES_SUPERSEDED (`enforces`, `_planted_cite`): a propagation finding on a line of a `tests/**/*.py` file
    that parses is dropped when it only *cites* its old id ("cites DEC-x") and every place of that id on the line is
    inside a planted span. Comments, docstrings and code keep it. Non-Python files and files that do not parse keep
    it too.
- **A reading:** a propagation hit on a recorded value (`holds '…'`) is about a value, not an id, so S17 does not
  filter it. It is carried as before. The register holds no `**Values:**` line today, so this changes no count.
- **On this worktree** (`gov links --all --json`, five runs each; HOME a scratch folder):

  | | before (`7940fad46619`) | after (`99d54ecee95a`) |
  |---|---|---|
  | all findings | 2,041 | 1,513 |
  | UNKNOWN_ID, independent-test-designer | 560 | 60 |
  | ENFORCES_SUPERSEDED, independent-test-designer | 73 | 45 |
  | every other code and role | unchanged | unchanged (117 CLOSED_TICKET_EDITED, 20 NOT_IN_FORCE_AS_RULE, 6 STATUS_CONFLICT, 93 TICKET_CHANGE_UNMARKED, 55 + 1 + 3 other UNKNOWN_ID, 1,104 UNLINKED_ID, 9 UNMARKED_CHANGE) |
  | `--all`, median of five | 3.15 s (3.03 to 3.33) | 3.84 s (3.77 to 4.03) |

  - No finding was added. No finding outside `tests/` changed.
  - The 560 UNKNOWN_IDs before are 3 more than the brief's 557. The extra 3 come from the designer's S17 cases,
    merged at `7940fad46619`.
  - Of the 60 UNKNOWN_IDs left, 58 are in comments and docstrings, judged as before; the other 2 are in the
    designer's W2-129 folder, which the engineer does not read. Examples: W1-90 in `W1-02`'s docstrings,
    W2-911 in a table in `W2-20`'s module docstring, DEC-9999 and DEC-000 in docstrings. These are F's (row 23).
  - **ENFORCES_SUPERSEDED, 28 dropped:**
    - 27 cite DEC-002 or DEC-013 inside planted registers and records: `W1-10` 10, `test_store.py` 5,
      `test_w2_92_record_files.py` 5, `test_w2_32_index_methods.py` 3, `test_w2_87_register.py` 3,
      `W2-03`'s grammar 1.
    - The sitting counted 29 such places. The other 2 (`test_w1_10_register.py:292` and `:415`) are in function
      docstrings, so the KPI keeps them: "ids in comments and docstrings … are judged as today".
    - The 28th is DEC-798 at `tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py:87`. That line is a `#`
      comment inside `_READER = r'''…'''`, a program embedded as a raw string. To Python it is a string literal, not
      a comment, so S17 counts it as planted.
  - **ENFORCES_SUPERSEDED, 45 kept:** DEC-798 39 and DEC-876 4 (43 of the "44 README citations"; the 44th is the
    embedded-program line above), plus the 2 DEC-002 docstrings. 23 are in `README.md` files. 22 are in `.py`
    comments, docstrings and code.
  - Timing: 0.7 s more, from parsing the test files that hold an unresolved id or a carried finding. That is well
    under S15's 10 s. The CTO's main-tree measure stays the S15 record.
- **`python3 -m gov.decisions.propagation`** is unchanged (no diff under `src/gov/decisions/`). `check_propagation`
  on this worktree still gives all 73 test-file lines. The unit case checks the same on a planted repository.
- **Units:** `tests/unit/links` 66 passed (61 before; 5 new `test_s17_*` cases): literals of each form against
  comments and docstrings; a file that does not parse; ENFORCES_SUPERSEDED carried for a docstring, a comment, code,
  README, JSON, text and a file that does not parse, and dropped for a planted register, plain and f-strings and a
  later string; a line outside `tests/` unchanged; `planted_spans` per line.
- **`gov accept W2-129`** (`99d54ecee95a`, HOME a scratch folder): **150 passed, 0 failed, 0 skipped**; success-17
  8/8 and failure-7 7/7 (both red before).

## 10. S18 (D-6 part 2 item F2, round 2; DEC-866 (1), DEC-1109 (2)): a settlement is a change

- **Why:** W2-55 S9 removed `tags.py`'s relation check. That check caught a `**Settles:**`, which DEC-866 (1) counts
  as a change; UNMARKED_CHANGE counted supersede and amend only, so S9 would have lost it.
- **The change** (`check.py` only):
  - `CHANGE_CLASSES` gains `settle`, the class the loader's `register_statements` gives `**Settles:** DEC-x`. There is
    still one pattern set (S8).
  - **Only the label counts** (`SETTLES_FORM`, `**Settles:**`). The loader also gives `settle` to a free "settled by"
    and to a `**Changed by:** settled by`. On this register:
    - the free form adds one pair, DEC-763 <- DEC-762. It comes from DEC-763's body, "P-4 is settled by DEC-762
      item 3", which settles a package item, not the entry;
    - the `**Changed by:**` form stands on the settled entry's own status line, so it never gives a finding.

    The brief asks that only `**Settles:**` pairs be added, so the free form is left out.
  - A settlement is never whole. Its finding is a part, `DEC-x <- DEC-y (**Settles:**; part)`, with `ids` (changed,
    changer) as for an amendment. Its mark is `**Changed by:** DEC-y (the part)`, so `--propose-marks` writes it.
  - A PROPOSED, REJECTED or WITHDRAWN settler gives nothing (`NOT_A_CHANGER`), as for the other forms.
- **On this worktree** (`gov links --all --json`, HOME a scratch folder; before `b4b4b18cb`, after this commit):

  | Code | Role | Before | After |
  |---|---|---|---|
  | UNMARKED_CHANGE | orchestrator | 8 | **9** |
  | UNLINKED_ID | orchestrator | 1,106 | 1,106 |
  | CLOSED_TICKET_EDITED | orchestrator | 117 | 117 |
  | TICKET_CHANGE_UNMARKED | orchestrator | 93 | 93 |
  | UNKNOWN_ID | orchestrator / owner / product-spec | 54 / 1 / 1 | 54 / 1 / 1 |
  | NOT_IN_FORCE_AS_RULE | orchestrator | 20 | 20 |
  | ENFORCES_SUPERSEDED | independent-test-designer | 4 | 4 |
  | **All** | | **1,404** | **1,405** |

  - **The one added:** `DEC-026 <- DEC-086 (**Settles:**; part)`. DEC-086's `**Settles:**` names DEC-004 and
    DEC-026, and DEC-026's status line names neither DEC-086 nor any changer.
  - **The register's 4 `**Settles:**` labels** give 5 statements: DEC-086 settles DEC-004 and DEC-026, DEC-377
    settles DEC-361, DEC-381 settles DEC-289 and DEC-833 settles DEC-828. The other 4 targets already carry
    `**Changed by:** settled by DEC-y` on their status lines, so they give nothing.
  - The other 8 UNMARKED_CHANGE pairs are unchanged, and so is every other code.
- **Units:** `tests/unit/links` 70 passed (66 before; 4 new parametrised cases). The ACCEPTED case is red with the old
  `CHANGE_CLASSES`.
- **`gov accept W2-129`** (HOME a scratch folder with `.local` linked in): **156 passed, 0 failed, 0 skipped**;
  success-18 6/6.
