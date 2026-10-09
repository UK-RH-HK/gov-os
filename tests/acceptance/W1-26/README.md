# W1-26 acceptance tests: `gov check` G0-G2

Ticket `DAEO-fygv`, profile FULL (DEC-221). Written before implementation by the Independent Test Designer (MR-3).
295 cases in 21 files.

```
python3 -m pytest tests/acceptance/W1-26 -q -p no:cacheprovider
```

## How the tests run

- Through public interfaces only: the `gov check` command line (W1-07's console-script stand-in), its API-0002
  envelope and exit code.
- Every project is a temporary git repository (DEC-322): its own `.tickets/`, its own `openspec/` (a copy of
  `template/openspec/`, as an adopted project holds it), its own check declarations and records. No test creates a
  file in this repository. The code under test is this worktree's `src/`.
- Before `gov check` runs, the project is committed.
- Deterministic, no network. External tools (`openspec`, `gitleaks`) are never on PATH unless a test provides a
  stand-in script.

## Red before implementation

Observed 2026-10-06: `1 skipped, 90 errors`.

- The 90 errors stop at the `built` fixture: `gov check is not built yet: it returns NOT_IMPLEMENTED`.
- The 1 skip, in `test_w1_26_command.py::test_gov_check_json_returns_the_api_0002_envelope`: uses the
  `raw_project` fixture (no `built` gate) and skips because `NOT_IMPLEMENTED` is in the output.

## KPI lines and covers ids

| KPI line | Tests | Red reason |
|---|---|---|
| **S1** "Runs schema, id grammar, orphans, path map, adapter drift, openspec validate --strict, decision checker, readiness, ticket DAG acyclicity and field completeness, and the rule that no implementer allowed_paths covers tests/acceptance/**" | `test_w1_26_planted_defects.py` (13), `test_w1_26_openspec.py` (5), `test_w1_26_readiness.py` (4), `test_w1_26_decisions.py` (6) | `NOT_IMPLEMENTED` |
| **S2** "Every policy key maps to a check or is declared informational; each family RED/YELLOW/GREEN" [CAP-39.d] | `test_w1_26_command.py` (4 family-status cases), `test_w1_26_policy.py` (3) | `NOT_IMPLEMENTED` |
| **S3** "Fails a specification with a required open readiness row that has no linked gap ticket" [CAP-30.b] | `test_w1_26_gap_tickets.py` (6) | `NOT_IMPLEMENTED` |
| **S4** "Fails a change to the capability taxonomy or readiness-dimensions.yaml that has no linked CIT-E record" [CAP-30.e] | `test_w1_26_taxonomy.py` (4) | `NOT_IMPLEMENTED` |
| **S5** "Each check declares hard-block or warning; every result records provenance" [CAP-39.d] | `test_w1_26_provenance.py` (4), `test_w1_26_command.py::test_each_check_result_declares_severity` | `NOT_IMPLEMENTED` |
| **S6** "Fails a skill file whose content changed without a version change and a linked decision" [CAP-24.c] | `test_w1_26_skill.py` (4) | `NOT_IMPLEMENTED` |
| **S7** "The check registry names all 17 families; registered checks run; absent reported" [CAP-38.b] | `test_w1_26_registry.py` (13) | `NOT_IMPLEMENTED` |
| **S8** "Fails a record that changes authority class without a decision" [CAP-01.c] | `test_w1_26_authority.py` (5) | `NOT_IMPLEMENTED` |
| **S9** "Flags a commit that cites a decision id missing from the decision register at that commit" (DEC-463) [CAP-38.b] | `test_w1_26_decision_citations.py` (45), `test_w1_26_decision_register_and_base.py` (37) | no declaration `core-decision-citations`; see "A commit citing an unrecorded decision". The 37: the check knows neither entry of the configuration; see "The register file and the base commit" |
| **F-1** "A planted defect of any listed family passes" | `test_w1_26_planted_defects.py` (13) | `NOT_IMPLEMENTED` |
| **F-2** "The scope of a check is a hand-maintained list" [CAP-58.a] | `test_w1_26_derived.py` (6) | `NOT_IMPLEMENTED` |

| Covers id | Tests |
|---|---|
| CAP-39.d (RED/YELLOW/GREEN; hard-block vs warning; provenance) | `test_w1_26_command.py`, `test_w1_26_provenance.py` |
| CAP-30.b (readiness gaps generate linked tickets) | `test_w1_26_gap_tickets.py` |
| CAP-30.e (capability taxonomy extended only through a governed change) | `test_w1_26_taxonomy.py` |
| CAP-38.b (17 families named, registered checks run, absent reported) | `test_w1_26_registry.py` |
| CAP-01.c (authority semantics preserved across stages) | `test_w1_26_authority.py` |
| CAP-24.c (skill changes follow versioned promotion) | `test_w1_26_skill.py` |
| CAP-58.a (checks derived, not enumerated) | `test_w1_26_derived.py` |

## Files

| File | Cases | KPI |
|---|---|---|
| `test_w1_26_command.py` | 10 | S1, S2, S5 |
| `test_w1_26_planted_defects.py` | 13 | F-1, S1 |
| `test_w1_26_registry.py` | 21 | S7 |
| `test_w1_26_provenance.py` | 4 | S5 |
| `test_w1_26_gap_tickets.py` | 6 | S3 |
| `test_w1_26_taxonomy.py` | 4 | S4 |
| `test_w1_26_skill.py` | 4 | S6 |
| `test_w1_26_authority.py` | 5 | S8 |
| `test_w1_26_policy.py` | 3 | S2 |
| `test_w1_26_derived.py` | 6 | F-2 |
| `test_w1_26_openspec.py` | 5 | S1 |
| `test_w1_26_readiness.py` | 4 | S1 |
| `test_w1_26_decisions.py` | 6 | S1 |
| `test_w1_26_skill_validator.py` | 36 | S7 (DEC-439) |
| `test_w1_26_audit_validator.py` | 36 | S7 (DEC-441) |
| `test_w1_26_not_applicable.py` | 21 | S2, S7 (DEC-447) |
| `test_w1_26_decision_citations.py` | 45 | S9 (DEC-463) |
| `test_w1_26_decision_register_and_base.py` | 37 | S9 (DEC-473, DEC-474) |

## The interface the tests fix

| What | Value | From |
|---|---|---|
| Module | `src/gov/cli/commands/check.py` (stub) delegating to `src/gov/check/` | DEC-317, `gov.cli.main` |
| Class | read (CAP-27: `git status --porcelain` empty after the command) | DEC-317 |
| Arguments | `--list` (existing, W1-07); `--json` (standard) | DEC-186 |
| Passes | `ok: true`, exit 0, `result` includes per-family status and per-check results | API-0002 |
| Hard-block RED | `ok: false`, exit 3, `error.details` includes the failing checks | API-0002 code 3 |
| Warning YELLOW | `ok: true` or exit 0 (warnings alone do not block) | CAP-39.d |
| Per-family status | RED, YELLOW, or GREEN | CAP-39.d |
| Per-check provenance | `commit` (HEAD), `check_version`, `inputs_hash` | CAP-39.d |
| Severity | `hard-block` or `warning` per check result | CAP-39.d |
| 17 families | All named; absent families reported by name, never silently missing | CAP-38.b |

## Earlier test revised

`tests/acceptance/W1-07/`: `check` joins `BUILT_LATER` in `w1_07_support.py`. The case
`test_running_checks_stays_not_implemented_with_declarations_present` leaves the list. Reason:
"planned: command implemented" (DEC-190), the same change W1-13 made for `readiness` and W1-25 for
`checkpoint`. W1-07's other cases keep `check` (envelope, read-only, configuration) and stay green
before and after.

## Revised cases

- `test_planted_commands_defect_reserved_command_no_module` (`test_w1_26_planted_defects.py`): the case removes the module file of one reserved command (`adopt`) from its temporary project's own copy of `src/`, then holds what it held before: the command-contract consistency family is not green, and a finding of the case's declared check names that command and no command whose module is present. Until W1-41 the project showed this defect without anything planted, because `adopt` was the one reserved command not built; revised after implementation: W1-41 builds `gov adopt --lite`, so every reserved command has a module ("planned: command implemented"). The code that runs stays this worktree's `src/`, which the case does not touch. One case added beside it for the other side, `test_commands_check_green_when_every_reserved_command_has_a_module`: with nothing removed, the family is green for the same declaration and the check reports no finding. Support: `Project.reserved_command_module_files()` and `Project.remove_reserved_command_module()`, added.
- `test_no_check_family_reason`, `test_check_count_zero_for_uncovered_families`: derived uncovered families from the runner's `check_count` field instead of a fixed list of uncovered families; another ticket registered one (W1-24, `context-reproducibility`).
- `test_lifecycle`, `test_opted_in_family_is_yellow`, `test_not_applicable_never_green_json`, `test_not_applicable_never_green_text`, `test_family_only_red_check_not_green`: each case removes the kernel's `audit-reproducibility` declaration from the temporary project so the family status reflects only the case's own check; revised after implementation: W1-36's kernel declaration of the audit-reproducibility check is now in every project built from the template (DEC-447).

## Generic validators (DEC-439, DEC-441) — follow-up round

Added by the Independent Test Designer (MR-3) for the follow-up round (DEC-439).

### Skill-file validator (`test_w1_26_skill_validator.py`)

The first start created 17 cases (10 test methods + 1 parametrized ×4). The follow-up adds 19 cases for the six fixes:

| Fix | Cases | What |
|---|---|---|
| Fix 1: folder search at every depth | 2 | Deep SKILL.md discovery, broken nested skill |
| Fix 2: SKILL.md without frontmatter is a finding | 1 | SKILL_NO_FRONTMATTER, not silently skipped |
| Fix 3: command refs with args after the name | 4 | Misspelt with args, valid with args, fenced block, bare still works |
| Fix 4: name/description/version not text | 5 | Integer version, integer name, list description, empty name, empty description |
| Fix 5: token count matches gov context formula | 1 | 10001 chars = ceil(10001/4) = 2501 tokens > 2500 |
| Fix 6: unreadable file is unmeasured, not traceback | 2 | Valid folder + missing path, binary file |

Total skill validator: 36 cases.

### Audit-report validator (`test_w1_26_audit_validator.py`)

36 cases testing `python3 -m gov.check.audit_validator` (DEC-441):

| Case | What |
|---|---|
| 1. Valid report passes | Well-formed report, resolvable commit, valid paths |
| 2. Missing frontmatter | No `---` delimiters |
| 3. Missing `commit` | Frontmatter without `commit` |
| 4. Missing `milestone` | Frontmatter without `milestone` |
| 5. Missing `pack_sha256` | Frontmatter without `pack_sha256` |
| 6. Unresolvable commit | Commit hash not in the repository |
| 7. No table rows | Valid frontmatter, empty table |
| 8. Invalid class | Class not in DEC-070's six |
| 9. OK row with `-` evidence | OK row must cite a path |
| 10. Non-OK row with `-` (×5) | MISSING, WEAKENED, CONTRADICTS, UNJUSTIFIED_DROP, SCOPE_CREEP |
| 11. Evidence path not at commit | `git show <commit>:<path>` fails |
| 12. Evidence path at commit (×2) | Single path, comma-separated paths |
| 13. Multiple rows, one bad | One non-existent path fails the report |
| 14. No arguments | Unmeasured (DEC-425) |
| 15. Empty folder | Unmeasured |
| 16. Unreadable file | Nonexistent path, unmeasured |
| 17. Outside git repo | Unmeasured |
| 18. Folder search | Finds .md files with milestone+commit frontmatter |
| 19. Valid folder + missing path | Not green |
| 20. Malformed row (×2) | Two columns (missing evidence), four columns (extra) |
| 21. OK row empty evidence (×4) | Empty cell, empty entry among real, trailing comma, non-OK empty cell |
| 22. Folder broken frontmatter (×2) | Broken YAML not skipped, missing `commit` not skipped |
| 23. commit must be hex id (×2) | HEAD and branch name are findings |
| 24. pack_sha256 format (×2) | Too short and non-hex values are findings |

### KPI and covers for the generic validators

| KPI line | Tests | Red reason |
|---|---|---|
| **S7** "provides the generic validators for skill files and audit reports" [CAP-38.b] | `test_w1_26_skill_validator.py` (36), `test_w1_26_audit_validator.py` (26) | `ModuleNotFoundError` (audit_validator not built yet); skill_validator exits non-zero on the new fix cases |
| **S1** "Runs schema … and the rule that no implementer allowed_paths covers tests/acceptance/**" | Indirectly: the validators are check commands called by the check runner | As above |
| **S2** / **S7** "not applicable until the first audit" [DEC-447] | `test_w1_26_not_applicable.py` (21) | Validator: says unmeasured, exits 1; Runner: ignores the field |

| Covers id | Tests |
|---|---|
| DEC-439 (generic validators for skill files and audit reports) | `test_w1_26_skill_validator.py`, `test_w1_26_audit_validator.py` |
| DEC-441 (minimal form of an audit report) | `test_w1_26_audit_validator.py` |
| DEC-425 (unmeasured, never green) | `test_w1_26_audit_validator.py` (cases 14–17), `test_w1_26_skill_validator.py` (Fix 6) |
| DEC-447 (not applicable until the first audit) | `test_w1_26_not_applicable.py`, `test_w1_26_audit_validator.py` (case 15 revised) |

### "Not applicable until the first audit" (DEC-447) — revision round

Added by the Independent Test Designer (MR-3) for owner decision DEC-447.

#### Not-applicable answer (`test_w1_26_not_applicable.py`)

21 cases testing DEC-447: the audit check is "not applicable until the first audit", a warning, never green.

The validator says `{"not_applicable": true, "reason": "not applicable until the first audit"}` and exits **2** (not 0 and not 1) when a folder holds no report. A declaration opts in with `allows-not-applicable: "true"` (optional; absent means no change).

| Case group | Cases | What | Red reason |
|---|---|---|---|
| Validator: not applicable | 4 | Empty/missing folder → `not_applicable` JSON, exit 2 | Currently says unmeasured, exits 1 |
| Validator: unmeasured unchanged | 3 | No args, missing file, outside git → unmeasured | (passes) |
| Validator: folder with reports | 2 | Valid/broken folder → validated, never not-applicable | (passes) |
| Runner: opted in | 3 | `allows-not-applicable: "true"` + NA answer → YELLOW, reason in JSON | Runner ignores the field |
| Runner: not opted in | 1 | Same answer without field → RED | (passes) |
| Runner: other failures | 5 | Opted in + findings/unmeasured/crash/exit-42/marker-exit-0 | (passes) |
| Lifecycle | 1 | No → YELLOW → valid → GREEN → broken → RED → removed → YELLOW | Phase 1 fails |
| Never green | 2 | JSON and text: family never GREEN on not-applicable | (passes) |

Validator exit codes: 0 clean, 1 findings or unmeasured, **2 not applicable**.

Declaration field: `allows-not-applicable: "true"` (optional; a declaration without it behaves exactly as before).

#### Revised case (owner decision DEC-447)

- `test_w1_26_audit_validator.py::TestEmptyFolder::test_empty_folder_unmeasured` → `test_empty_folder_not_applicable`: a folder with no report files is "not applicable", not "unmeasured".

#### Literal declaration W1-36 should write for audit-reproducibility

```yaml
id: audit-reproducibility
family: audit reproducibility
tier: G2
severity: hard-block
command: python3 -m gov.check.audit_validator audit-reports/
allows-not-applicable: "true"
```

## A commit citing an unrecorded decision (DEC-463) — follow-up round

Added by the Independent Test Designer (MR-3) for owner decision DEC-463, before implementation.
`test_w1_26_decision_citations.py`, 45 cases.

**S9** "Flags a commit that cites a decision id missing from the decision register at that commit: a decision is
recorded before the change it authorises (DEC-463) [CAP-38.b]".

### What is settled, and from what

| Point | Settled | Source |
|---|---|---|
| The decision register in a project | The decision files of the project: every Markdown file whose frontmatter has `type: decision`, or an `id` in the `decision_id` grammar, in any folder. A decision is recorded when such a file carries its id. Read by frontmatter, never by prose. | `tests/acceptance/W1-11/README.md` ("A decision file"), DEC-329, DEC-387 |
| The register as one file of headed entries | **Answered by DEC-473: see "The register file and the base commit".** As written before the answer: package P-1. No source gives a checker that form. It is this repository's present state only (Charter v5 names `docs/DECISION_REGISTER.md`; DEC-274: "decisions are headings in the register, not files"; W1-11's README: the two series "are not both files yet"). No case here uses it. | as named |
| What a citation is | A whole word in the `decision_id` grammar of the kernel's shared definitions (`ADR-` or `DEC-` and three or more digits), in the commit's message: subject, body or trailers. Lower case, fewer digits, another prefix (`CAP-38`, `W1-26`, `L-0900`, `DP-900`, a ticket id) or a longer word around it is no citation. | DEC-227 and `tests/acceptance/W1-08/README.md` (reading 11: one shared `decision_id`), DEC-182 (trailers are part of the message) |
| The changed text | Not read. DEC-463 says "a commit that cites": the commit speaks through its message. An id named by a file is that file's reference (the graph's dangling reference of DEC-274), whoever commits it. | DEC-463, DEC-274 |
| "At that commit" | The register in the tree of the same commit. A commit that adds the decision and cites it is not flagged. A commit citing a decision that a later commit adds stays flagged. A decision present at the citing commit and removed later does not flag that commit; a commit citing it after the removal is flagged. A commit on a merged branch is judged by its own tree, not the merge's. | The KPI line ("missing from the decision register at that commit"), DEC-463 ("recorded before the change it authorises") |
| Which commits are judged | **Answered by DEC-474: see "The register file and the base commit".** As written before the answer: package P-2. DEC-463 says "from now on" and accepts seven late records by name; no source says how `gov check` knows where "now" is, and `gov check` takes no range (`--list`, `--json`; DEC-186). W1-11's README leaves it to this design ("W1-26 may need a range or a baseline"). Every project of these cases records no base and dates every commit it judges after 2026-10-07, so each is judged under options (a), (b) and (d) of P-2; under (c) the cases gain the argument. No case plants history from before the rule. | DEC-463, DEC-186, `tests/acceptance/W1-11/README.md` ("Notes for the lead") |
| The form of the check | A declared check in the kernel's checks (`id`, `family`, `tier`, `severity`, `command`), id `core-decision-citations` (the ticket's path is `template/governance/kernel/checks/core-*`). `gov check` runs it because it is declared. | KPI S7, the ticket's `allowed_paths` |
| Family | "authority/role limits": the rule is about what authorises a change, and this suite already places the decision checker's findings there. | KPI S7 (the 17 families), CAP-01, `test_w1_26_decisions.py` |
| Severity | `warning`: YELLOW, never a hard block. The owner's word is "flags"; every other line of this ticket says "Fails". A commit once made cannot be mended (DEC-182: history is not rewritten), so a hard block would stay red for ever and stop every merge under DEC-466. | DEC-463, DEC-182, DEC-466, CAP-39.d |
| Fail-opens | No repository, a repository without a commit, a git that fails, a history that cannot be read: the unmeasured answer of this suite (`"unmeasured": true`, a reason, exit 1). A decision file of a judged commit that cannot be read: exit 1 and the file is named. None is clean, and none is the not-applicable answer: DEC-447 gives that answer to the audit check alone. | DEC-425, DEC-447, DEC-387, "Validator exit codes" above |

### The interface the cases fix

| What | Value |
|---|---|
| Declaration | exactly one declaration with `id: core-decision-citations` under `template/governance/kernel/checks/`; `family` "authority/role limits" (compared as DEC-436 compares); `severity: warning`; no `allows-not-applicable` |
| Command | the declaration's `command`, run by a shell in the project's root with this worktree's `src/` on `PYTHONPATH`; its name is the engineer's |
| Output | one JSON object on stdout |
| A flagged commit | one entry of `findings`: `{"code": "DECISION_UNRECORDED", "commit": "<the full commit id>", "decision": "<the id>"}`, one for each commit and id (an id written twice in one message is one finding); other keys are free |
| Exit codes | 0 clean; 1 findings or unmeasured; never 2 |
| Through `gov check` | the check's result has `id` `core-decision-citations`; `status` YELLOW with a flagged commit, GREEN on a clean history, never GREEN over a register it cannot read |

A case that expects "not flagged" also holds one flagged commit (it cites `DEC-900`, recorded nowhere) and
asserts the exact set of findings. So it is red until the check exists, and a check that reports nothing does
not pass it.

### Cases

| Group | Cases | What |
|---|---|---|
| The declaration | 3 | family; severity `warning`; no `allows-not-applicable` |
| An unrecorded citation is flagged | 8 | in the subject, the body, a trailer (3); exit 1; an `ADR-` id; two ids are two findings and a repeated id one; the unrecorded id alone beside a recorded one; every citing commit, not the last alone |
| At that commit | 6 | a clean history is clean (exit 0, no finding); record and citation in one commit; recorded by a later commit; removed later; cited after removal; a merged branch's commit by its own tree |
| What the register is | 4 | a typed file in `docs/adr/`, a typed file in another folder, a file with no `type` and an id in the grammar (3); an id named in prose or in another decision's `supersedes` is not recorded |
| What a citation is | 14 | thirteen id-like words that are no decision id; an id in the changed text alone |
| Fail-opens | 6 | no repository; no commit; a stand-in `git` that fails; a missing commit object; a decision file with frontmatter not closed or not YAML (2) |
| Through `gov check` | 4 | YELLOW with a flagged commit; GREEN on a clean history; the family YELLOW; never GREEN over an unreadable register |

Red before implementation, observed 2026-10-07 (`4 failed, 212 passed, 1 skipped, 41 errors`; before this file
`212 passed, 1 skipped`):

- 41 errors at the `declaration` fixture: `0 check declarations with id 'core-decision-citations' under
  template/governance/kernel/checks/ (expected exactly one): the check on commits citing decisions is not declared`.
- 4 failures, the cases through `gov check`: `gov check gives no result for the check 'core-decision-citations'`.

| Covers id | Tests |
|---|---|
| DEC-463 (a decision is recorded before the change it authorises) | `test_w1_26_decision_citations.py` |
| CAP-38.b (a declared check of a named family) | `test_w1_26_decision_citations.py` (the declaration, through `gov check`) |
| DEC-425, DEC-447 (unmeasured, never green; not-applicable for the audit check alone) | `test_w1_26_decision_citations.py` (fail-opens) |

### Open packages

Both are answered: P-1 by DEC-473 (option (a)), P-2 by DEC-474 (option (a)). DEC-475 confirms the severity, the
family and the citation in the message alone. The cases are in the next section. The packages stay here as they
were put.

**P-1 (P1). Does the check know a register that is one file of headed entries?**
The sources define decisions as files (W1-11). This repository records them as headings `### DEC-nnn — title` in
`docs/DECISION_REGISTER.md`, and DEC-466 has `gov check` run here before every merge. A check that knows files
alone flags every commit of this repository that cites a `DEC-` id (DEC-274: every such reference dangles), so here
it measures nothing.
- (a) **Recommended.** Both forms. A decision is recorded at a commit when a decision file of that commit's tree
  carries its id, or when a register file of that tree has a heading that opens with the id. The project names its
  register file (one line of project configuration under `governance/project/`); no path of this repository is
  written into the kernel. With no register file named, files alone.
- (b) Files alone. The check stays yellow in this repository until its decisions are records; DEC-467's baseline
  would carry it.
- (c) Both forms, with `docs/DECISION_REGISTER.md` and `### <id>` fixed in the kernel. Simplest; it puts this
  repository's layout into every adopter's kernel.

Needed with (a) or (c), then written as cases: the heading grammar (level, what may follow the id), and whether an
id in a heading inside a fenced block or a table row counts (recommended: a heading line outside a fence only).

**P-2 (P1). Which commits are judged, and what of the commits made before the rule?**
- (a) **Recommended.** A base commit recorded in the project (under `governance/project/`): the commits reachable
  from `HEAD` and not from the base are judged, merges and the commits they bring included. With no base recorded,
  every commit reachable from `HEAD`. For this repository the base is the commit that records DEC-463
  (`46ec8da3`); the seven late records lie before it. A base that is not a commit of the repository, or not an
  ancestor of `HEAD`, is unmeasured.
- (b) A date in the kernel (2026-10-07). Dates are the committer's to choose, and the kernel would carry this
  repository's date into every adopter.
- (c) A range argument to `gov check`. It changes the command's interface (DEC-186), and a check before a merge
  would judge only what its caller thinks to pass.
- (d) Every commit, and a list of accepted findings by commit and id (as DEC-467 does for red checks). Exact, and a
  hand-maintained list (failure KPI 2).

Cases that wait for the answer: commits before the base are not flagged; a base that cannot be resolved; a shallow
clone whose boundary hides judged commits.

### Not tested

- The headed register (P-1) and history from before the rule (P-2): tested since DEC-473 and DEC-474, see the next
  section.
- A decision's `status`: whether a `PROPOSED` or `SUPERSEDED` decision counts as recorded. The KPI says "missing
  from the decision register"; the cases record with `ACTIVE`.
- A range written in prose ("DEC-460 to DEC-466"): both ends are citations by the grammar; the ids between are not
  read.
- An id with a prefix before it (`X-DEC-900`) or a suffix after a hyphen (`DEC-900-draft`).
- A decision file with the extension `.MD` or `.markdown` (DEC-387's residual), and one moved between two commits.
- Notes (`git notes`) and tag messages: the commit's own message alone.
- Whether an unreadable decision file is reported as a finding or as unmeasured: the cases fix exit 1 and the
  file's name in the output.
- Latency on a long history.

## The register file and the base commit (DEC-473, DEC-474) — follow-up round

Added by the Independent Test Designer (MR-3) for the owner's answers to packages P-1 and P-2, before
implementation. `test_w1_26_decision_register_and_base.py`, 37 cases. The interface (the declared command, its JSON,
the finding `DECISION_UNRECORDED`, the exit codes) is that of the section above.

### The configuration: settled by the designer

No source names a file for "the project's configuration" of a check, and none names the two entries. DEC-473 says
"one line of configuration under `governance/project/`"; DEC-474 says "recorded in the project's configuration".
This is the designer's settlement, not a source's word:

| What | Settled | From |
|---|---|---|
| The file | `governance/project/path-map.yaml` | DEC-185: "There is no new `overlay.yaml`"; a `gov` command loads the `governance/project/` files it knows, `path-map.yaml` first. DEC-224, DEC-230: the project's floor "lives in `path-map.yaml`, under top-level keys". DEC-060: a project's configuration is its path map, its capabilities and its policy strengths, and all three are in that file. This suite's policy cases read `policies` from it (`test_w1_26_policy.py`): it is the one file from which a check of this suite reads project data. The other files of the folder each hold one thing that is not a check's (`roster.yaml`, `tool-registry.yaml`, `research-allowlist.yaml`). |
| The register's entry | top-level key `decision_register`: the path of the register file from the project's root, with `/` | "one line of configuration" (DEC-473); snake case as the file's other keys (`state_class`, `human_gate`) |
| The base's entry | top-level key `decision_citations_base`: a commit id in hexadecimal, full or abbreviated, written as a YAML string (quoted where it could read as a number) | DEC-474 writes this repository's base abbreviated (`46ec8da3`) |
| Both optional | a project without the file, or with a path map that has neither key, is judged as before: decision files alone, the whole history | DEC-473 ("With no register file named"), DEC-474 ("With no base recorded"), DEC-185 ("A missing file is not an error") |
| The schema | not touched by a case. The kernel's path-map schema leaves its top level open, so a path map with the two keys loads today (`gov status` exits 0 on the cases' path map). Whether the schema names the two keys is the engineer's and the lead's. | `template/governance/kernel/schemas/path-map.schema.json` |

Every path map a case writes is valid under the kernel's schema (its twenty-two systems are read from the schema), so
the check may read the file itself or through the configuration loader.

What this repository then writes in its own `governance/project/path-map.yaml` (the lead's, not a case's):

```yaml
decision_register: docs/DECISION_REGISTER.md
decision_citations_base: "46ec8da3"
```

No case names that path as something the check knows. The cases' register is `records/decision-log.md`. A file at
`docs/DECISION_REGISTER.md` appears in three cases, as a file of headed entries that no configuration names: it
records nothing.

### What is settled, and from what

| Point | Settled | Source |
|---|---|---|
| An entry of the register | A line that opens with `### `, then `DEC-` and digits, then a space, a colon or a dash, then the title. Recorded: that id. | DEC-473 |
| The three separators | `### DEC-101 The title`, `### DEC-101: The title`, `### DEC-101 — The title`. The dash case is written as the owner's own headings are (space, em dash, space). | DEC-473; the headings of the register itself |
| No entry | A heading of level 1, 2 or 4. A heading with one space before its marks, or with text before them. `### DEC-101` with nothing after the id. `### DEC-1010 — …` for `DEC-101`. A heading inside a fenced code block; a heading after the fence is closed is an entry again. | DEC-473 ("level-3", "at the start of a line", "followed by … and the title", "inside a fenced code block does not count") |
| Both forms | With a register named, a decision recorded only as a decision file is recorded. | DEC-473 ("either … or") |
| No register named | Decision files alone. A file of headed entries in the project is not read, whatever its path; with a register named, a second such file is not read either. | DEC-473 ("With no register file named, decision files alone count. No path of this repository goes into the kernel.") |
| "At that commit", for the register | The register file as it is in the tree of the citing commit: an entry added by a later commit does not record for the earlier one; an entry and its citation in one commit are not flagged; an entry removed later does not flag the commit that cited it. | The KPI line; the section above ("At that commit") |
| Which configuration | **Reading.** The project's present configuration (the working tree, as the configuration loader reads it), not the configuration of each judged commit. A base can only be recorded after it exists, so the commits between the base and the commit that records it are judged by a configuration they do not hold; the same holds for the register's name. A commit that cited an entry of the file before the configuration named it is not flagged. | DEC-474 (this repository's base is recorded after `46ec8da3`), DEC-185 |
| A named register that cannot be read | The tree of a citing commit does not hold the named register as a readable file (absent there and added later; a directory; bytes that are not text): exit 1 and the register's path in the output. Never clean, although the cited decision is recorded as a decision file. Whether it is a finding or the unmeasured answer is free, as for an unreadable decision file. | DEC-425; the section above ("Fail-opens"); `test_w1_26_skill_validator.py` (a binary file is unreadable) |
| The commits judged | Those reachable from `HEAD` and not from the base: the base itself and the commits before it are not judged, every commit after it is, and a side commit made before the base and merged after it is. | DEC-474; package P-2, option (a), which it accepts |
| No base recorded | The whole history, with a configuration file or without one. | DEC-474 |
| A base that is not a commit of the repository, or not an ancestor of `HEAD` | The unmeasured answer (`"unmeasured": true`, a reason, exit 1). | Package P-2, option (a); DEC-425 |
| No commit after the base | The unmeasured answer. This suite gives it to a repository without a commit: "no commit to judge is not a clean history" (the section above, "Fail-opens"), and a base with nothing after it leaves no commit to judge. A commit cannot hold its own id, so the base is `HEAD` only while the configuration that records it is not committed; the case leaves it uncommitted. | The section above ("Fail-opens"); DEC-425 |

### Cases

| Group | Cases | What | Red reason (observed 2026-10-07) |
|---|---|---|---|
| The heading grammar: an entry | 4 | the three separators (3); a heading after a closed fence | the recorded ids are flagged: the register is not read |
| The heading grammar: no entry | 8 | another level (3); not at the start of a line (2); nothing after the id; a longer id; inside a fence | the control `DEC-200`, recorded by a well-formed heading, is flagged |
| Both forms, and the file the project names | 5 | a decision file beside a named register; no register named (2: no configuration file, a configuration without the entry); only the named file; a register named later | the control or the entry is flagged; the 2 cases with no register named stop at the fixture `register_is_read`: `the check does not read the register file that governance/project/path-map.yaml names under 'decision_register' (DEC-473)` |
| "At that commit" | 3 | an entry added later; an entry and its citation in one commit; an entry removed later | the control or the entry is flagged |
| A named register that cannot be read | 3 | absent at the citing commit; a directory; not text | exit 0 |
| The base | 6 | a commit before the base (2: full id, eight characters); the base itself; every commit after it; a branch merged after it; a register and a base together | the commits at and before the base are flagged |
| No base recorded | 1 | the whole history | stops at the fixture `base_is_honoured`: `the check does not honour the base commit that governance/project/path-map.yaml records under 'decision_citations_base' (DEC-474)` |
| A base that gives nothing to judge | 3 | not a commit of the repository; not an ancestor of `HEAD`; no commit after it | exit 0, no unmeasured answer |
| Through `gov check` | 4 | GREEN on a citation of a register entry; never GREEN with the named register absent; GREEN when only commits before the base are flagged; never GREEN with an unknown base | YELLOW where GREEN is expected; GREEN where it must not be |

A case that expects an id to be flagged because a line is no entry also cites the control (`DEC-200`, recorded by a
well-formed heading of the same register) and asserts the exact set of findings: a check that reads no register
does not pass it. Three cases cannot hold a control (no register is named, or no base is recorded); they depend on
a fixture that shows the entry is known, and are errors until then.

Red before implementation, observed 2026-10-07: `34 failed, 257 passed, 1 skipped, 3 errors`; before this file
`257 passed, 1 skipped`.

| Covers id | Tests |
|---|---|
| DEC-473 (both register forms; the heading grammar; no path of this repository in the kernel) | `test_w1_26_decision_register_and_base.py` (the register groups) |
| DEC-474 (a base commit recorded in the project) | `test_w1_26_decision_register_and_base.py` (the base groups) |
| DEC-425 (unmeasured, never green) | `test_w1_26_decision_register_and_base.py` (a register that cannot be read; a base that gives nothing to judge) |

### Not tested

- Which characters are a dash, and a dash or a colon with no space around it (`### DEC-101—title`,
  `### DEC-101-title`): DEC-473 says "a dash"; the case uses the form of the owner's headings.
- A heading `### ADR-nnnn …`: DEC-473's grammar names `DEC-` alone.
- A fence opened with `~~~`, an indented code block, a fence that is never closed, a heading in a table row or a
  block quote.
- A separator with no title after it (`### DEC-101:`), and a heading with closing `#` marks.
- A named register absent at a judged commit that cites no decision. Every register case holds the register from
  the project's first commit on, so no case depends on it.
- A base written as a branch, a tag or `HEAD~n`, a base that names a tree or a blob, an abbreviation that matches
  two objects, and a `decision_register` or `decision_citations_base` of the wrong type (a list, a number): the
  `CONFIG_INVALID` contract of DEC-189 is the loader's.
- A register path that leaves the project (`../…`, an absolute path) or is a symbolic link.
- A shallow clone whose boundary hides commits after the base.
- The configuration as committed against the configuration in the working tree, apart from the one case with no
  commit after the base.

## Fixture: kernel skills copied (DEC-439)

`_copy_kernel_templates()` in `w1_26_support.py`: revised after implementation: W1-35's
skill-regression check runs the generic validator over the kernel's skills, so a project
built from the template holds them (DEC-439). The copy is generic (every folder under
`template/governance/kernel/skills/`), so future tickets that add skill folders need no
revision of this file.

## Not tested

- Latency under load (DEC-372): a latency case re-run alone when failing under parallel load is not tested;
  the tests run sequentially.
- The cache or early-stop inside the decision checker (W1-11's responsibility).
- What `gov.store.load` does in a partial clone (W1-10's, W1-11 batch 4's).
- Whether `gap_ticket` exists as a ticket vs merely as a string: only the string is checked.
- Running `openspec validate --strict` with the real `openspec` binary.
- Whether gitleaks is installed (the secrets-indexing check, W1-15).
- The seven families not yet registered: their checks are built by other tickets.

## The follow-up after W1-41 on W1-30's ticket (DEC-569): pieces on the checks

Written by a test designer on ticket `DAEO-2lwj` (W1-30, reopened), before the checks are changed. No earlier
case of this suite is changed.

### The probe type in the schema check (DEC-565; `test_w1_26_probe_records.py`, 43 cases)

DEC-565: "The four findings each probe record adds to the schema check are accepted as known growth [...] In
the follow-up after W1-41 the probe type is added to the kernel's record schema, so that the schema check
returns to its recorded baseline."

**The four findings a probe record gives today**, measured on each of this repository's four records (16 in
all) and on a fixture of the same form:

1. `SCHEMA_MISSING_FIELD`, field `id`
2. `SCHEMA_MISSING_FIELD`, field `status`
3. `SCHEMA_MISSING_FIELD`, field `state_class`
4. `SCHEMA_UNKNOWN_TYPE`, type `probe`

The engineer's work is measured by them: after it a well-formed probe record gives none of the four and no
other.

How the cases run: the `command` of the kernel's declaration `core-schema`, in the root of a temporary project
(the suite's `raw_project`, which holds the kernel's schemas where the suite's projects hold them), with this
worktree's code. The findings are the command's JSON; a finding belongs to a record when its `path` is the
file. One case runs the command in this repository's root; it reads only.

**The fields and their shapes (proposed)** are those of the schema, listed in full in W1-08's README, section
"The probe record's schema": the nine required fields (`type`, `task`, `reviewer_session`,
`implementer_session`, `reviewer_wrote_nothing`, `commissioned_by`, `judged_by`, `judgement`, `probed_commit`),
with `id`, `status` and `state_class` not required.

**The findings' codes (proposed).** A missing field keeps the check's code `SCHEMA_MISSING_FIELD`. A field of
a wrong type or value is `SCHEMA_INVALID_FIELD`, a code the check does not have today. Both carry `path` (the
file) and `field`. Only one case holds the codes; the others hold the file and the field.

| Case | Holds | Today |
|---|---|---|
| `test_a_well_formed_probe_record_gives_no_finding` | the nine fields, this repository's form: no finding on the file | red: the four findings |
| `test_each_judgement_word_is_well_formed` (4: `pass`, `passed`, `fail`, `failed`) | no finding; a failed probe is a true record, the gate refuses the close | red, all four: the four findings |
| `test_a_probe_record_that_states_the_shared_fields_is_well_formed_too` | with `id`, `status`, `state_class` (the form of W1-30's fixtures): no finding | red: `SCHEMA_UNKNOWN_TYPE` |
| `test_a_probe_record_is_known_by_its_type_not_by_where_it_lies` | a record under `docs/reviews/`: silent when well-formed, named with `judgement` when not | red: the four findings |
| `test_two_records_of_one_ticket_are_each_judged` | two records in one ticket's folder (DEC-500): the good one silent, the one without `probed_commit` named | red: the good one has the four |
| `test_a_probe_record_without_a_field_the_probe_gate_asks_for_is_a_finding` (8, one per field beside `type`) | a finding with the file and the field, and no finding about anything else | red, all eight: no finding names the field |
| `test_a_field_of_a_wrong_type_or_value_is_a_finding` (21) | the same for one wrong shape or value: `judgement` (outside the words, upper case, a truth value, empty), `probed_commit` (abbreviated, `HEAD`, upper case, 41 characters, a number), `reviewer_wrote_nothing` (a word, a number), each session (empty, a list or a number), `commissioned_by` and `judged_by` (empty, a list or a truth value), `task` (a list, no ticket id) | red, all 21: no finding names the field |
| `test_the_codes_of_a_probe_record_s_findings` | `SCHEMA_MISSING_FIELD` for a missing judgement, `SCHEMA_INVALID_FIELD` for `probed_commit: HEAD`, each once, with `path` | red |
| `test_this_repository_s_probe_records_are_well_formed` | the frontmatter of every file under `docs/probes/*/` here, in a temporary project: no finding | red: four on each |
| `test_no_finding_of_the_check_on_this_repository_names_a_probe_record` | the check on this repository: no finding whose path or message names a file under `docs/probes/`. It does not fix the check's total, so a later record of any type does not break it | red: 16 findings |
| `test_a_record_of_an_unknown_type_is_still_a_finding` | `type: probing`: `SCHEMA_UNKNOWN_TYPE` | green; holds what stays |
| `test_a_record_of_another_type_still_owes_the_shared_fields` | a decision record without `id`, `status`, `state_class`: each named | green; holds what stays |
| `test_a_record_whose_type_is_no_text_is_still_a_finding` | `type` as a list | green; holds what stays |

40 red, 3 green.

### The four recorded commands in the checks (DEC-542; `test_w1_26_recorded_commands.py`, 10 cases)

DEC-542: "`ci`, `launch`, `telemetry` and `lock` are recorded in the command list". The lines and what
"recorded" means for `lock` are in W1-07's README, section "The four commands of DEC-542". Two checks read the
command list, and both hold the twelve only today.

- **`core-commands`** holds for each of the four what it holds for the twelve: where the project holds no
  module for the command, a finding carries the command's name under `command` (the code is the check's own,
  `COMMAND_NO_MODULE`; the cases do not fix it). For `ci`, `launch` and `telemetry` the module is the command's
  module file, as for the twelve. For `lock`, recorded as the module command `python3 -m gov.lock`, it is the
  file that makes that command run. With every module present the check has no finding.
- **The skill validator** (a reading: it is the second reader of the list, and a list that records `ci` while
  a check calls `gov ci` unknown would contradict itself): a skill may name `gov ci`, `gov launch` and
  `gov telemetry`. `gov lock` in a skill stays `SKILL_UNKNOWN_COMMAND`, because `gov` has no such command.

| Case | Holds | Today |
|---|---|---|
| `test_a_recorded_command_without_its_module_is_a_finding_that_names_it` (4: `ci`, `launch`, `telemetry`, `lock`) | the module removed in the temporary project's copy: a finding with `command` the name, the family red, no finding about a command whose module is present | red, all four: the check has no finding |
| `test_with_every_module_present_the_check_has_no_finding` | the twelve and the four each with their module: no finding, the family green | green; it holds that recording `lock` does not make the check report it for the form it has |
| `test_a_skill_may_name_a_recorded_gov_command` (3) | a skill whose code names `gov ci`, `gov launch`, `gov telemetry`: no `SKILL_UNKNOWN_COMMAND`, exit code 0 | red, all three: "unknown gov command" |
| `test_gov_lock_in_a_skill_stays_an_unknown_command` | `gov lock` in a skill is flagged | green; holds that no command is added |
| `test_the_module_command_of_lock_in_a_skill_is_not_flagged` | `python3 -m gov.lock` in a skill | green; holds what stays |

7 red, 3 green. The suite's two earlier cases on this check (`test_w1_26_planted_defects.py`) are unchanged.

### The skill checks in both layouts (DEC-521; `test_w1_26_skill_checks_layouts.py`, 33 cases)

DEC-521 orders for the follow-up "the declared check commands that name `template/` paths". Three declared
checks call the skill validator with paths under `template/governance/kernel/skills/`: `skill-regression-a`
(discovery, planning, test-design, change), `skill-regression-b1` (retrieval, audit, checkpoint, adopt) and
`skill-regression-orchestration` (orchestration). In a project with an installed kernel the skills lie under
`governance/kernel/skills/`; the paths of the commands do not exist there, and each check answers
"unmeasured: path does not exist", whatever the skills hold.

How the cases run: the `command` of the kernel's declaration, started by a shell in the root of a temporary
project, as the runner of `gov check` starts it, with this worktree's code. The project holds only the skills
the case writes (fixtures); no file and no path of this repository is given to the check. The cases of each
check on this repository's own skills stay in W1-35's and W1-36's suites, unchanged.

**What is held (the stricter reading where the decision is silent).**

- Installed layout: measured; green on well-formed skills; a planted defect is a finding that names the
  skill's file under `governance/kernel/skills/`; with one of the check's skills absent the check is never
  green and its answer names the absent skill.
- Template layout: as today.
- Both layouts: both are measured, and a defect in either is a finding whatever the other holds (as the close
  record lists the skills of both, W1-30's settlement 32: no skill a role could load is left out).
- Neither layout, or a skills folder with none of the check's skills: the unmeasured answer
  (`{"unmeasured": true, "reason": ...}`, exit code 1), which `gov check` reports as a finding of a hard-block
  check. Never green without having measured.

| Case (each ×3, one per check) | Holds | Today |
|---|---|---|
| `test_in_an_installed_project_the_check_measures_and_is_green_on_well_formed_skills` | exit code 0, `findings` empty | red, all three: unmeasured, "path does not exist: template/..." |
| `test_in_an_installed_project_a_planted_defect_is_a_finding` | one skill without frontmatter: `SKILL_NO_FRONTMATTER` naming its installed file | red, all three: unmeasured, no finding |
| `test_in_an_installed_project_an_absent_skill_is_never_green` | another skill is there, one of the check's is not: not green, the absent skill named | red for `a` and `b1` (not green, but the answer names the first template path, not the absent skill); green for `orchestration`, whose one skill the template path happens to name |
| `test_with_both_layouts_a_defect_in_either_is_a_finding` (×2: the defect in the installed layout, in the template layout) | the finding names the file of the layout that holds the defect | the installed half red, all three: the check is green, the installed skills are not read; the template half green |
| `test_in_the_template_layout_the_check_is_green_on_well_formed_skills` | as today | green |
| `test_in_the_template_layout_a_planted_defect_is_a_finding` | as today | green |
| `test_in_the_template_layout_an_absent_skill_is_never_green` | as today | green |
| `test_with_both_layouts_well_formed_the_check_is_green` | no doubled finding, exit code 0 | green |
| `test_in_a_project_with_neither_layout_the_check_is_unmeasured_and_never_green` | exit code 1, `unmeasured` with a reason, no finding | green; holds what stays |
| `test_a_skills_folder_without_the_check_s_skills_is_unmeasured` | an installed kernel with a skill of no check only | green; holds what stays |

33 cases: 11 red, 22 green.

Not held, and returned as a package: that `gov check` in an installed project finds the declarations at all.
The declarations are read from `template/governance/kernel/checks/` only, by code outside the paths of this
follow-up; these cases run each declared command directly.

Not held here: where an installed project holds the kernel's schemas. The schema check reads them from the
template layout; the three declared checks that name `template/` paths are piece 15 below, and the schema
check's own place for its schemas is named in no decision.

### Checks in a project with an installed kernel (DEC-579; `test_w1_26_installed_kernel.py`, 31 cases)

Written by a test designer on ticket `DAEO-2lwj`, in the second run of the follow-up, before the code is
changed. It closes the two points the section above left open. No earlier case of this suite is changed.

DEC-579: "`gov check` reads the check declarations, and the schema check reads the schemas, from the installed
kernel as well as from the template layout: today an installed project runs no declared check."

**Measured today**, on temporary projects: with the kernel under `governance/kernel/` only, `gov check --list`
answers `{"checks": []}` and `gov check` runs the three checks that need no declaration and passes, whatever
the installed declarations say, valid or not; the schema check finds no schema there (a ticket record without
`kpis` gives no finding, a well-formed probe record gives `SCHEMA_UNREADABLE`).

How the cases run: `gov check --json` and `gov check --list --json` through the suite's launcher, and the
schema check as it is declared (the `command` of `core-schema`, started in the project's root). Every project
is a temporary git repository built from scratch: a ticket record under `docs/records/`, a probe record where
a case writes one, a small check of the cases' own (a script under the kernel's `bin/` that reads one file of
the project and answers with a finding or with exit code 0), and five kernel files copied by name: the
declarations `core-schema.yaml` and `skill-regression-orchestration.yaml`, the schemas `common`, `ticket` and
`probe`. No project holds a copy of `src/`; no path of this repository is given to a check.

**Settled for a project that holds both layouts** (the stricter reading; this repository holds the template
layout only, so none of it changes its answer or its counts):

- **Alike in both:** one check per declaration, run once; the list, the results, the findings and each
  family's count are those of the template layout alone.
- **A declaration file in one layout only is run.** A check is not dropped because the other layout lacks it:
  dropping would let a check vanish silently.
- **One check id declared differently in the two is refused**, for the run and for the list, before any check
  is started: which of the two the project means is not known, and taking either silently would let one
  layout loosen the other (another command; the not-applicable answer allowed in one copy only). The refusal
  names both files. The comparison held is of the declaration's keys, the optional `allows-not-applicable`
  among them.
- **A declaration that is not valid in the installed layout is refused** even where the template layout holds
  a valid file of the same name.
- **A schema file that differs:** a record is held to the schemas of both layouts, and a finding under either
  is a finding (as the skill checks measure both layouts, section above). With equal schemas no finding is
  doubled.

**Proposed** (names a user sees, each held by a case):

- The refusal of one check id declared differently in the two layouts: the existing code
  `CHECK_DECLARATION_INVALID`, exit code 1, with both files' paths in the error.
- An installed declaration that is not valid: the existing code `CHECK_DECLARATION_INVALID` with
  `details.file` the path `governance/kernel/checks/<file>` and `details.key` and the message as for the same
  file in the template layout.

No new finding code, field or option is proposed.

| Case | Holds | Today |
|---|---|---|
| `test_an_installed_project_lists_its_declarations` | the list is the installed declarations, five fields each, in file-name order | red: the list is empty |
| `test_an_installed_project_is_answered_as_the_same_kernel_in_the_template_layout` | the same kernel files and records in either layout, one record breaking its schema: the same checks, each once, the same statuses, findings and family counts | red: no declared check has a result |
| `test_the_declared_command_of_an_installed_check_is_started_and_its_result_reported` (2: green, a finding) | the small check, whose command names a file of the installed kernel, is started in the project's root: green is reported green; its finding is reported as given, the check and its family red, exit code 3; the result carries provenance | red, both: no result for the check |
| `test_a_kernel_declaration_whose_command_names_template_paths_measures_the_installed_kernel` (2: a well-formed skill, one without frontmatter) | the kernel's `skill-regression-orchestration`, copied as it is: green on the installed skill; `SKILL_NO_FRONTMATTER` naming `governance/kernel/skills/orchestration/SKILL.md` | red, both: no result for the check |
| `test_in_an_installed_project_a_record_that_breaks_its_schema_is_a_finding` (2: a ticket without `kpis`; a probe record with a judgement outside the four words) | the schema check as declared: a finding with the file and the field, and none about anything else | red, both: no finding for the ticket; `SCHEMA_UNREADABLE` for the probe record |
| `test_in_an_installed_project_records_that_keep_their_schemas_give_no_finding` | a complete ticket and a well-formed probe record: no finding | red: `SCHEMA_UNREADABLE` on the probe record |
| `test_gov_check_in_an_installed_project_is_red_on_a_record_that_breaks_its_schema` | end to end: the one finding (file, `kpis`), the family `schema/invariants` red, exit code 3 | red: no result for `core-schema` |
| `test_an_installed_kernel_without_a_record_s_schema_is_never_silent_about_it` | the installed kernel lacks the probe schema: the one finding `SCHEMA_UNREADABLE` on the record | green; holds what stays |
| `test_a_project_with_neither_layout_answers_as_today` | the list is empty; `gov check` passes with exactly the three checks without a declaration (`openspec-validate`, `skill-version`, `readiness`), the 17 families, counts 1 for skill regression and 2 for product traceability and 0 elsewhere, each family without a check yellow with "no registered check"; the schema check gives the one `SCHEMA_UNREADABLE` on a probe record | green; pins today |
| `test_with_both_layouts_alike_every_check_runs_once_as_with_the_template_alone` | list and answer equal those of the template layout alone, with a schema finding and a finding of the small check in them | green; holds what stays |
| `test_this_repository_s_own_list_holds_each_declaration_of_its_template_once` | `gov check --list` on this repository (it reads only): one check per declaration file of its template, in file-name order | green; holds what stays |
| `test_with_both_layouts_a_declaration_in_one_layout_only_is_run` (2: the template alone holds it, the installed alone) | listed once beside the shared ones, run once, green | the template half green; the installed half red: not listed |
| `test_one_check_id_declared_differently_in_the_two_layouts_is_refused` (4: another command, the not-applicable answer allowed; each for the run and the list) | exit code 1, `CHECK_DECLARATION_INVALID`, both files named, no check started | red, all four: the template's declaration is taken silently |
| `test_with_both_layouts_a_record_is_held_to_the_schemas_of_both` (2: the stricter ticket schema in the template, in the installed layout) | the one finding names the field only that schema asks for | the template half green; the installed half red: no finding |
| `test_a_declaration_that_is_not_valid_is_refused_under_the_installed_layout_as_under_the_template` (8: a missing field, a severity outside the two, a list at the top level, no YAML; each for the run and the list) | the same file in a template project and in an installed one: the same code and key, the message equal but for the path, `details.file` the installed path, no check started | red, all eight: `gov check` passes, the list is empty |
| `test_with_both_layouts_a_declaration_that_is_not_valid_in_the_installed_one_is_refused` | refused by the installed file's own path | red: the template's valid file is taken |

31 cases: 25 red, 6 green.

**Not held.** `gov ci` reads the declarations too (to choose what it runs); its answer in an installed project
is not held here. Two declarations of one id that differ only in bytes (a comment, quoting) and not in any
key; a schema file that only one of two layouts holds; two files of one layout that declare one id: none is
fixed. The check that reads `template/governance/kernel/vendor/` for skill versions and the other declared
checks' own readings of kernel paths are not part of this piece.

**Packages:** none. The three choices above are stricter readings and each is reversible by changing its case.
