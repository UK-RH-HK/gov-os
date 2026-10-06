# W1-23 acceptance tests: hierarchical synthesis notes

Ticket: **DAEO-9i8e** (W1-23).  Profile: **STANDARD**.

## KPI-to-test mapping

| KPI | Kind | Description | Tests | covers |
|-----|------|-------------|-------|--------|
| S1 | success | When evidence exceeds the packet budget, notes are derived under .gov-runtime/, cite source ids and hashes, and disclose unresolved evidence | `TestDerive::*` | CAP-15.f |
| S2 | success | A note is invalidated when any cited source hash changes; notes are rebuildable | `TestInvalidation::*` | CAP-15.f |
| F1 | failure | A note survives a change to a cited source | `TestF1::test_changed_source_invalidates_note` | CAP-15.f |
| F2 | failure | A note cites a span not in its source | `TestF2::test_all_citations_reference_valid_spans` | CAP-15.f |

## covers-to-test mapping

| covers id | Description | Tests |
|-----------|-------------|-------|
| CAP-15.f | Hierarchical synthesis notes: derived, cited, hash-checked, disclose unresolved evidence, rebuildable | `TestDerive::*`, `TestInvalidation::*`, `TestF1::*`, `TestF2::*` |

## Test count

| File | Tests |
|------|-------|
| `test_w1_23_synthesis.py` | 10 |
| **Total** | **10** |

## Expected red reasons

Every test fails before implementation for a clear, stated reason:

| File / class | Red reason |
|--------------|------------|
| `test_w1_23_synthesis.py::TestDerive` | `synthesis_api` fixture fails: `gov.retrieval.synthesis.synthesize does not exist: No module named 'gov.retrieval.synthesis'` |
| `test_w1_23_synthesis.py::TestInvalidation` | `synthesis_api` fixture fails: `gov.retrieval.synthesis.synthesize does not exist: No module named 'gov.retrieval.synthesis'` |
| `test_w1_23_synthesis.py::TestF1` | `synthesis_api` fixture fails: `gov.retrieval.synthesis.synthesize does not exist: No module named 'gov.retrieval.synthesis'` |
| `test_w1_23_synthesis.py::TestF2` | `synthesis_api` fixture fails: `gov.retrieval.synthesis.synthesize does not exist: No module named 'gov.retrieval.synthesis'` |

## Interface (the tests fix it)

### DP-1: the synthesis function

```
Module:   gov.retrieval.synthesis
Function: synthesize(root: Path, evidence: list[dict], budget: int, *, gaps: list[dict] | None = None) -> dict
Returns:  {
              "notes": [
                  {
                      "group": str,
                      "citations": [
                          {
                              "source_id": str,
                              "source_sha256": str,
                              "path": str,
                              "start_line": int,
                              "end_line": int,
                          }
                      ]
                  }
              ],
              "unresolved": [{"id": str, "reason": str}]
          }
```

The function:
1. Takes an evidence list (each item has `id`, `sha256`, `path`, `start_line`, `end_line`, `text`) and a budget in tokens.
2. Groups evidence hierarchically (e.g. by directory path), not as a flat dump.
3. Writes the notes under `root / .gov-runtime/` as derived state.
4. Each citation carries `source_id` and `source_sha256` from the evidence item.
5. Unresolved evidence (from `gaps`) is disclosed in the `unresolved` field.
6. The output is deterministic: same inputs produce the same files and bytes (rebuildable).

### DP-2: the note validator

```
Module:   gov.retrieval.synthesis
Function: validate_notes(root: Path) -> dict
Returns:  {"valid": bool, "errors": [{"source_id": str, "code": str, "message": str}]}
```

The validator reads all synthesis notes under `root / .gov-runtime/`, re-hashes each cited span against the current file on disk, and reports whether all cited source hashes still match. A single mismatched hash makes the result invalid.

## What each case needs

All tests need only `git` and `python3`. No machine dependencies (no gitleaks, no sqlite_vec, no Ollama). Each test builds its own temporary git repository from scratch. Notes are written to the temporary repository's `.gov-runtime/`, never to the live runtime (DEC-322).

## Packages

None.
