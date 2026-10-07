# W1-26 acceptance tests: `gov check` G0-G2

Ticket `DAEO-fygv`, profile FULL (DEC-221). Written before implementation by the Independent Test Designer (MR-3).
136 cases in 15 files.

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

- `test_no_check_family_reason`, `test_check_count_zero_for_uncovered_families`: derived uncovered families from the runner's `check_count` field instead of a fixed list of uncovered families; another ticket registered one (W1-24, `context-reproducibility`).

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

| Covers id | Tests |
|---|---|
| DEC-439 (generic validators for skill files and audit reports) | `test_w1_26_skill_validator.py`, `test_w1_26_audit_validator.py` |
| DEC-441 (minimal form of an audit report) | `test_w1_26_audit_validator.py` |
| DEC-425 (unmeasured, never green) | `test_w1_26_audit_validator.py` (cases 14–17), `test_w1_26_skill_validator.py` (Fix 6) |

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
