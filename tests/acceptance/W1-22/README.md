# W1-22 acceptance tests: evidence validator and zero-result canaries

Ticket: **DAEO-8nue** (W1-22).  Profile: **FULL**.

## KPI-to-test mapping

| KPI | Kind | Description | Tests | covers |
|-----|------|-------------|-------|--------|
| S1 | success | Validator rejects a bundle without a stopping reason, with an unresolvable citation, a stale hash or a quoted span absent from its source | `TestValidatorAccepts::*`, `TestValidatorRejects::*` | CAP-57.a |
| S2 | success | Each index has canaries run after reindex; a canary miss sets FACET_UNAVAILABLE | `TestDeclarations::*`, `TestCanaryRunner::*`, `TestCanaryMiss::*` | CAP-17.c, CAP-55.a |
| F1 | failure | A bundle with an unresolvable citation passes the validator | `TestF1::test_an_unresolvable_citation_does_not_pass` | CAP-57.a |
| F2 | failure | An empty index answers NOT_FOUND as absence | `TestF2::*` | CAP-55.a |

## covers-to-test mapping

| covers id | Description | Tests |
|-----------|-------------|-------|
| CAP-57.a | Deterministic closure; synthesis citation check | `TestValidatorRejects::*`, `TestF1::*` |
| CAP-17.c | Zero-result canaries after reindex | `TestCanaryRunner::test_lexical_canary_hits_after_reindex`, `TestCanaryRunner::test_semantic_canary_hits_after_reindex` |
| CAP-55.a | Fixed stopping reasons; NOT_FOUND never proof of absence; canaries per index | `TestValidatorAccepts::test_validator_accepts_each_fixed_stopping_reason`, `TestCanaryMiss::*`, `TestF2::*` |

## Test count

| File | Tests |
|------|-------|
| `test_w1_22_validator.py` | 15 |
| `test_w1_22_canaries.py` | 10 |
| `tests/unit/validate/test_canary.py` | 5 |
| **Total** | **30** |

## Expected red reasons

Every test fails before implementation for a clear, stated reason:

| File / class | Red reason |
|--------------|------------|
| `test_w1_22_validator.py` (all classes) | `validator_api` fixture fails: `gov.retrieval.validate.validate does not exist: No module named 'gov.retrieval.validate'` |
| `test_w1_22_canaries.py::TestDeclarations` | `AssertionError: template/governance/kernel/canaries does not exist` |
| `test_w1_22_canaries.py` (all other classes) | `canary_api` fixture fails: `gov.retrieval.canary.run_canaries does not exist: No module named 'gov.retrieval.canary'` |

## Interface (the tests fix it)

### DP-1: the validator

```
Module:   gov.retrieval.validate
Function: validate(root: Path, bundle: dict) -> dict
Returns:  {"valid": bool, "errors": [{"code": str, "message": str, ...}, ...]}
```

The validator checks every evidence item:

1. `stopping_reason` is in the fixed list of six (ADR-0002 §4, DEC-034, DEC-396).
2. Every cited `path` exists under `root`.
3. The `sha256` matches the hash of `lines[start_line - 1 : end_line]` — **the span only**, not the whole file (stricter than W1-21's `check_citation`; DEC-036).
4. The quoted `text` appears in the cited lines.

When multiple defects are present, all are reported (the error list has one entry per defect).

### DP-2: the canary runner

```
Module:   gov.retrieval.canary
Function: run_canaries(root: Path) -> dict
Returns:  {
              "lexical":  {"passed": bool, "status": "AVAILABLE"|"FACET_UNAVAILABLE", "misses": [...]},
              "semantic": {"passed": bool, "status": "AVAILABLE"|"FACET_UNAVAILABLE", "misses": [...]},
          }
```

The runner reads declarations from `template/governance/kernel/canaries/` (one YAML per index: `lexical.yaml`, `semantic.yaml`), queries the project's indexes with `refresh=False`, and reports per-index whether all canary queries found their expected hits.

### DP-3: canary declarations

```
Location: template/governance/kernel/canaries/
Files:    lexical.yaml, semantic.yaml (one per index)
```

Each file declares canary queries whose expected results are content that every adopted project contains.

### DP-4: validator strictness on sha256

The validator checks sha256 against the cited span only (the bytes of lines `start_line` to `end_line`), not the whole file. This is stricter than W1-21's `check_citation` (which accepts either). DEC-036: "every cited source ID exists at the cited hash and every quoted span appears in the source" — the hash is of the cited material.

## What each case needs

- **Validator tests** (`test_w1_22_validator.py`): no machine dependencies. They build a temporary project (git init, files, commit), construct bundles manually, and call `validate(root, bundle)`.
- **Canary declaration test** (`TestDeclarations`): no machine dependencies. Checks files under `template/governance/kernel/canaries/`.
- **Canary runner tests** (all other `test_w1_22_canaries.py`): need `gitleaks` and `sqlite_vec` (marked `@pytest.mark.needs`). They index a temporary project through the Ollama stand-in endpoint, then call `run_canaries(root)`.

## DEC-136 fail-open additions

Four tests added for fail-open findings from the post-green review (DEC-136):

| Test | Red reason |
|------|------------|
| `TestValidatorRejects::test_validator_rejects_path_traversal_outside_root` | The validator does not check that the resolved path stays under root; `Path(root) / "../secret.md"` escapes and the file is accepted |
| `TestValidatorRejects::test_validator_rejects_out_of_range_lines_with_empty_bytes_hash` | Out-of-range lines set span to `b""`; supplying `sha256(b"")` matches and the validator accepts |
| `TestValidatorRejects::test_validator_rejects_missing_line_range` | Missing `start_line`/`end_line` default to whole file; the whole-file hash is accepted |
| `TestCanaryMiss::test_corrupted_store_reports_facet_unavailable` | A corrupted `store.db` causes the searcher to raise; `run_canaries` does not catch it and crashes |

**Not tested through the public interface (DEC-136 finding 5):** missing or malformed canary YAML crashes `run_canaries`. The template path is a module-level constant (`_TEMPLATE`) in `gov.retrieval.canary`, not a parameter of `run_canaries(root)`. This cannot be exercised through the public interface without modifying the template directory. Covered by unit tests in `tests/unit/validate/test_canary.py` (patching `_TEMPLATE` and `_SEARCHERS`).

### Unit tests for empty and malformed canary declarations

| Test | Red reason |
|------|------------|
| `TestEmptyCanaryDeclarations::test_empty_canaries_list_reports_facet_unavailable` | `canaries: []` — the loop never runs, `misses` stays empty, `passed` is True, runner returns `AVAILABLE` |
| `TestEmptyCanaryDeclarations::test_null_canaries_reports_facet_unavailable` | `canaries: null` — `decl.get("canaries", [])` returns `None` (key exists), `for canary in None` raises `TypeError` — the runner crashes |
| `TestEmptyCanaryDeclarations::test_entry_without_query_reports_facet_unavailable` | `canaries: [{}]` — `canary["query"]` raises `KeyError` in the `try` block; the `except` handler also accesses `canary["query"]`, raising a second `KeyError` that propagates uncaught |
| `TestMalformedDeclarations::test_missing_yaml_reports_facet_unavailable` | Already handled (green): `read_text` raises `FileNotFoundError`, caught by the outer `except` |
| `TestMalformedDeclarations::test_non_dict_yaml_reports_facet_unavailable` | Already handled (green): `isinstance(decl, dict)` check raises `ValueError`, caught by the outer `except` |

## Who calls canaries

`run_canaries(root)` is a standalone function in `gov.retrieval.canary`. It is not called by reindex (`lexical.refresh()` in W1-17, `semantic.refresh()` in W1-19) — those live in `src/gov/retrieval/lexical.py` and `src/gov/retrieval/semantic.py`, outside this ticket's paths. DEC-037 says canaries are "run at G1 after reindex and at G4/G5"; `gov doctor` (W1-27, which depends on W1-22) is the G4 implementation and is responsible for calling canaries after reindex and as a health check. Adding a canary call to the reindex itself would be a change to `src/gov/retrieval/lexical.py` or `src/gov/retrieval/semantic.py`; no source requires it.

## "Each index has canaries" — scope analysis

CAP-17.c and DEC-037 say "each derived index (FTS/vector, codebase-memory, RAGFlow if adopted)" has canaries. The current canary runner (`_SEARCHERS`) covers:

- **Lexical** (FTS, W1-17): has `search(root, query, refresh=False)`. Canary declaration exists (`lexical.yaml`).
- **Semantic** (vector, W1-19): has `search(root, query, refresh=False)`. Canary declaration exists (`semantic.yaml`).

Not covered, and not coverable by the current runner API:

- **Code index** (codebase-memory, W1-16): has `definitions()`, `callers()`, `callees()` — queried by symbol name through `gov.closure` (W1-20), not by text query. It has no `search(root, query)` function and no canary declaration. Adding canaries for it would require a different query type (symbol-based, not text-based) and a different runner shape. This is a concern for W1-27 (`gov doctor`) or a later ticket.
- **Closure** (`src/gov/closure/`): computed from the record graph + code index. Not a stored index. Has no store to canary.
- **RAGFlow**: not adopted (DEC-019 path is default until the adoption trigger fires).

**Package recommendation:** the "each index" KPI (CAP-17.c) is satisfied for the text-search indexes (lexical, semantic). Code-index canaries need a different query type and runner shape; this should be tracked as a concern for W1-27 or a subsequent ticket, not a gap in W1-22.

## W1-07 revision

W1-22 does not build a `gov` subcommand. The validator and canary runner are Python functions (`gov.retrieval.validate.validate`, `gov.retrieval.canary.run_canaries`), not CLI commands. No revision of `tests/acceptance/W1-07/w1_07_support.py` is needed.
