# Lead brief: reds-memory (retrieval, the memory-use log, the close's store, the scan cache)

Read `/home/usain/Dynamic-Agentic-Engineering-OS/docs/emergency-2/briefs/REDS-COMMON.md` first and follow it.
Branch `e2/reds-memory` from `w2/integrate`, worktree `/home/usain/gov-os-worktrees/E2-reds-memory`. Task trailer:
`Task: emergency-2`, `Class: Q`. Never rebuild the shared store or run a memory measure (the machine rule); tests build
their own small stores.

**Your reds**
1. **W2-54 against W2-197's memory-use log (4 cases):** `test_w2_54_query_cache`
   `test_gov_retrieve_and_gov_context_write_at_most_one_derived_file_under` (2 files: `memory-use.jsonl`,
   `query-vector-cache.db`) and `test_in_a_project_without_an_index_a_read_creates_nothing` (`.gov-runtime/` made);
   `test_w2_54_cpu_embedder` (2 cases): a read that got no query vector changed `memory-use.jsonl`. The CTO's decision:
   - the memory-use log is a log, not a derived file: W2-54's "at most one derived file" count leaves
     `.gov-runtime/memory-use.jsonl` out (T, Rewrite-Reason: W2-197, EMERGENCY-2 §5.6);
   - a read that fails (no query vector) or runs in a project without an index writes nothing, no log line and no
     folder (C, a fix in W2-197's record). Run `gov accept W2-197` after it; if a W2-197 KPI line requires the
     opposite, stop on this red and return it.
2. **W2-61h `test_f3_each_new_visible_gold_source_holds_its_answer`: "q22.yaml: 2 source entries, the designer's reading
   has 3".** q22 was re-anchored last night (find the commit). If the re-anchoring was deliberate and q22 still holds
   its answer, (T) the designer's reading follows; otherwise (R) the gold file.
3. **`tests/unit/retrieval/test_w2_131_register_ids.py`, `test_w2_133_gap_label.py`, `test_w2_135_item_cap.py` (6
   cases): `ImportError: cannot import name 'role_paths' from 'gov.guard'`.** The guard left the product (DAEO-gr7t,
   b18c3ddec). Find what the tests used `role_paths` for and where that now lives, or give the tests what they need
   themselves. (C, unit tests only.)
4. **`tests/unit/close/test_repo.py::test_a_store_that_cannot_be_asked_is_an_error_and_names_the_rebuild[not a
   database]`: `sqlite3.DatabaseError: file is not a database` escapes** where the case expects an error that names the
   rebuild. (C): the close's store check catches it.
5. **W2-107 (26 errors, 1 failure, every file of `tests/acceptance/W2-107/`):** each case's premise fails: "a clean text
   is scanned and let through ... and 0 >= 1" (no gitleaks call recorded); `gitleaks` is at `~/.local/bin/gitleaks`.
   Find why the scanner makes no call: a path retired with the guard (DAEO-gr7t) or gitleaks being off (DEC-1045;
   EMERGENCY-2 §2.11: no gitleaks while private, one full scan before going public), or a bug. If the scan cache's
   path is retired, (T) retire the W2-107 cases and say which change retired it. If it is still the path of §2.11's
   one full scan, (C) fix it. If you cannot tell, stop and return it as one line with options.
