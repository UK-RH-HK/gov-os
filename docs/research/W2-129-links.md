# W2-129 `gov links`: the engineer's record

The engineer's record for W2-129 (`DAEO-q7lk`, DEC-1073 (5)(b), design `LINK-INTEGRITY.md` §4). It covers:
- each finding code's form;
- the readings chosen where the KPI and §4.4 leave a detail open;
- the first `--all` run's counts by code and role, and the timing;
- S8's parity with W2-92's drift script;
- one row of evidence per KPI line.

The code is `src/gov/links/` (`check.py`, `patch.py`, `command.py`); the unit tests are `tests/unit/links/test_links.py`.

## 1. The run measured

- **Head:** `422aac40581a` (`w2/W2-129`: `w2/integrate` at `e3355def9f99` with the designer's cases and this ticket's
  code).
- **The tree:** the engineer's worktree, read-only. The only file written is `.gov-runtime/links/mark`. The CTO's
  measured run on the main tree is still due (S15).
- **The command:** `PYTHONPATH=src python3 -m gov.cli.main links …`, through `heavy_slot.sh`. No model, network or
  GPU; no store.
- **CPython 3.12.3, PyYAML 6.0.1 with libyaml.** The frontmatter is read with the C loader. With the pure loader,
  `--all` took about 5.0 s.

| Command | Five runs (s) | Median |
|---|---|---|
| `gov links --all` | 3.51, 2.52, 2.53, 2.50, 2.40 | **2.52 s** (bound 10 s) |
| `gov links --since HEAD~1` | 2.38, 2.34, 2.30, 2.29, 2.40 | **2.34 s** (bound 5 s) |

- `--since` costs about the same as `--all`, because every run reads the whole record set (S9).
- About 1.7 s of each run is W2-55's `check_propagation`, used as it stands. Its frontmatter read uses the pure YAML
  loader, and it sits in W2-55's paths.

## 2. The first `--all` run: counts by code and role (the clean-up's baseline)

2,843 findings at `422aac40581a`. 29 of them are free-text findings (all UNMARKED_CHANGE).

| Code | Role | Count |
|---|---|---|
| UNMARKED_CHANGE | orchestrator | 187 |
| UNKNOWN_ID | independent-test-designer | 405 |
| UNKNOWN_ID | orchestrator | 55 |
| UNKNOWN_ID | product-spec | 3 |
| UNKNOWN_ID | owner (a commit whose `Role:` is `owner`) | 1 |
| UNLINKED_ID | orchestrator | 1,891 |
| STATUS_CONFLICT | orchestrator | 110 |
| STATUS_CONFLICT | product-spec | 6 |
| NOT_IN_FORCE_AS_RULE | product-spec | 106 |
| NOT_IN_FORCE_AS_RULE | orchestrator | 35 |
| ENFORCES_SUPERSEDED | independent-test-designer | 44 |

By place:

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
  - It also carries `commit` for a commit's finding, `via` for the other places that stated it, and `whole`, `form`
    and `mark` for UNMARKED_CHANGE.

| Code | Subject | Where the line points | Fix |
|---|---|---|---|
| UNMARKED_CHANGE | `DEC-x <- DEC-y (<form>; whole\|part)` | the register, DEC-x's status line | `add "SUPERSEDED by DEC-y"` (whole) or `add "**Changed by:** DEC-y (part)"` |
| UNKNOWN_ID | `<id or path> in <owner>'s <key>` / `in a kernel line` / `in a test file` / `in <sha12>'s Task:` | the place | correct or remove it; for a commit, name the id it should have named (history is not rewritten) |
| UNLINKED_ID | `<id> in <ticket>'s KPI brackets, not in its sources` / `<id> in <sha12>'s Implements: (<role>), not in <ticket>'s sources` | the ticket's `sources:` line | `add <id> to <ticket>'s sources:` |
| STATUS_CONFLICT | `<id> <status> in the register, spent in ARCHIVE-SUPERSEDED §B` / `… listed in DECISIONS-IN-FORCE` / `<ticket> <status> against its close record <CL> <status>` / `MR-n <status> against contract.yaml <status>` | the list line, the ticket's `status:`, the MR record's `status:` | reconcile the two |
| NOT_IN_FORCE_AS_RULE | `<id> (<STATUS>) in <place>` | the place | decide it, or cite it as proposed (or rejected, …), not as a rule |
| ENFORCES_SUPERSEDED | propagation's own message | the path and line propagation names | cite the decision in force, or record a `**Kept:**` reason |

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
3. **Exit codes:** 0 with no new finding (also when `--all` lists standing ones), 1 with a new finding, 2 when the
   run cannot be made. A run that cannot be made is named on stderr or in the JSON error:
   - `LINKS_NOT_A_WORK_TREE`, `LINKS_NO_HEAD`;
   - `LINKS_NO_RANGE`, `LINKS_BAD_REV`, `LINKS_MARK_UNKNOWN`;
   - `STORE_REGISTER_UNREADABLE`, the loader's own.

   The patches end with 0. The exit code goes through `CHILD_EXIT_CODE`; `cli/main.py` is unchanged.
4. **"New" (S9):**
   - A commit's finding is new when the commit is in the range.
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
5. **Commits:** every commit is judged on every run, so no finding older than the mark is lost (F5). One about a
   commit outside the range is standing.
   - A commit's trailers are read as the loader reads them: its final trailer block, or the whole message before
     2026-10-03 (DEC-182).
   - The role is the commit's `Role:`, or the orchestrator (the ticket's lead) once it is landed. A commit counts as
     landed when it is not on HEAD's first-parent line.
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
   405 now.
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

## 5. S8's parity with `docs/research/W2-92-proto-drift.py`

Both were run `--from-head` at the worktree's head before this ticket's commit.

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

102 passed, 1 failed, 0 skipped (HOME=/home/usain).
- The red is one case of `success-9` (S9, the incremental line).
- The engineer does not read the case (DEC-957, DEC-1056), and `gov accept` reports counts only.
- What was tried, each run through `gov accept`:
  - judging every commit: fixed F5 and two S10 cases;
  - a narrower "new": no change to the S9 case;
  - the refusal printed on stdout too: no change, reverted;
  - `--all` refusing without a mark: seven more reds, reverted.
- The case is unchanged by every reading of "new" tried, so it most likely checks an output detail. The candidates:
  - the `<rev>` after "since" (reading 1);
  - the shape of the standing counts (the first line's parentheses, or JSON `standing` as an integer beside
    `standing_by`);
  - the refusal's stream (stderr).
- The CTO, who can read the case, can say which reading it holds.

## 7. Evidence by KPI line

| KPI line | Evidence |
|---|---|
| S1 one read-only command, writes only its mark | `command.py` (CLASS read, no ACT_PATHS); unit `test_the_mark_holds_heads_sha_alone_and_nothing_else_is_written`; accept success-1 4/4 |
| S2 UNMARKED_CHANGE | `check.unmarked`; units `test_unmarked_change_…`, `test_archive_section_a_…`, `test_a_supersedes_followed_by_plain_text_…`; accept success-2 10/10 |
| S3 UNKNOWN_ID | `check.records`, `register_places`, `contract`, `texts`, `commits`; units `test_the_typed_places_of_tickets`, `test_records_contract_kernel_and_list_rows`, `test_commit_trailers`; accept success-3 22/22 |
| S4 UNLINKED_ID | `check.records`, `commits`; units as S3; accept success-4 5/5 |
| S5 STATUS_CONFLICT | `check.statuses`; unit `test_status_conflicts`; accept success-5 8/8 |
| S6 NOT_IN_FORCE_AS_RULE | `check.records`, `register_places`, `_rule_lines`, `commits`; accept success-6 18/18 |
| S7 ENFORCES_SUPERSEDED | `check.enforces` (W2-55's `check_propagation`, imported); unit `test_enforces_superseded_is_propagations`; accept success-7 2/2 |
| S8 one source of patterns | `register_statements` imported, §5 above; accept success-8 4/4 |
| S9 incremental | `check.touched`, `is_new`; units `test_findings_older_than_the_mark_…`, `test_a_changed_entry_…`, `test_an_entry_a_changed_entry_names_…`, `test_a_status_changed_…`, `test_an_older_commits_finding_…`; accept success-9 **5/6** (§6) |
| S10 output and exit codes | `command.run`, `check.render`; units `test_json_is_the_shared_envelope_…`, `test_cannot_run_exits_2_named`; accept success-10 8/8 |
| S11 the two patches | `patch.py`; units `test_propose_marks_…`, `test_propose_sources_…`; accept success-11 7/7 |
| S12 the role table | `check.ROLE_TABLE`, `role_of`; unit `test_role_table` (14 paths); accept success-12 5/5 |
| S13 never a gate | nothing outside `src/gov/links` imports it; unit `test_never_a_gate_…`; accept success-13 2/2 |
| S14 any repository | `check.not_applicable`; unit `test_a_repository_without_the_kinds_is_not_applicable`; accept success-14 2/2 |
| S15 cheap, measured | §1 (the engineer's run: 2.52 s and 2.34 s); the CTO's measured run on the main tree is still due |
| F1 to F5 | accept failure-1 to failure-5: 1/1, 4/4, 2/2, 5/5, 2/2 |
