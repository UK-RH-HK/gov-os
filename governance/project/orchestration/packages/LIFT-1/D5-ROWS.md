# D5-ROWS: lines D-5's templates must carry, collected as they arise (CTO, 2026-11-03; DEC-1052 templates)

Each line is one a template needs because work today showed its absence; product-spec writes the templates (D-5) and
the CTO approves them. Basis: question 4 (a line only where it changes what is done).

| # | template | the line | why (today's evidence) |
|---|---|---|---|
| 1 | test designer | a case revised for a ticket carries **that ticket's `Task:`** trailer | G-14's link source (i) ties a revised case to the ticket named in `Task:`; W2-126's revisions of W2-54 carried W2-54's (ACT-G14 review R2-F11) |
| 2 | engineer | a whole-branch diff after TESTS-READY uses `git diff --stat` or `-- . ':!tests/acceptance'` | a pathless diff shows the acceptance tests and the guard does not judge it (ACT-G14 review F3) |
| 3 | lead / CTO | **a worker's brief is built with `gov context <ticket> --role <the worker's role>`** | the role filter (W2-13 S5) can only filter for the reader it is told about (W2-13 review S5-F1b) |
| 4 | lead / CTO | pairs (a test designer and an engineer) run under **their ticket's own id**, never a coordination ticket's | the guard does not separate a pair under W2-00 (DEC-1063, G14b-F1); W2-32's pair runs by `gov launch` under DAEO-0pyc |
| 5 | every launched worker | **no merge inside the sandbox**: the CTO (or lead) merges into the worker's branch outside it; restores and conflict resolutions in `tests/acceptance/` by a test designer | the sandbox keeps `.claude/`, `.tickets/`, `tests/acceptance/` read-only, so merges fail part-way; three workers recorded merges with git's low-level commands (2026-11-03) |
| 6 | every launched worker | every whole-folder pytest run adds `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`; no `gov retrieve` in the sandbox | real-model cases reached the shared servers or a private reranker twice on 2026-11-03 (DEC-1012; DEC-1064, DEC-1065 (1)) |
| 7 | test designer | the README map names every case by its **full node id** (`test_<file>.py::test_<name>`) | `gov accept` fails a line whose map names a test it cannot collect (W2-32's round 1) |
| 8 | lead / CTO | `gov accept` for a ticket whose suites need the code index runs **outside the sandbox** until W2-56 | the sandbox keeps `/tmp/gov-cbm-<uid>` read-only (W2-92's S6 round) |
| 9 | lead / CTO | the ticket's **interface** (where config lives, error names, function signatures) is stated in the ticket before the pair starts | W2-32's tests had to assume it (P-W2-32-1); W2-13 needed a rewrite for the same reason (DEC-1000) |
