
## W1-17 residuals (lexical index and shared store, 2026-10-04)

Recorded at W1-17's close, from the ticket lead's two summaries. None is a defect of the ticket; each names who
should settle it where that is known.

- **The index-freshness check is red in this repository** until an orchestrator-role session builds the live index
  (DEC-342, DEC-322). It is also not green on an index that holds no chunk (DEC-345), so a project with no
  governance-class file can never be green. W1-26 and W1-27 take both into account.
- **The index reads the working tree; the record graph reads `HEAD`** (DEC-344). The two can describe different
  states of one file. W1-20 settles what a caller sees.
- **A store without graph tables.** If the index is built before any `gov.store.load`, `store.db` exists without the
  graph tables, and `gov.store.digest` and `connect` fail with a raw SQLite error, not `STORE_MISSING`. The fix is in
  `src/gov/store/`: W1-27, which wires `gov rebuild`.
- **`search` can raise.** A default `search` raises when the filter or git fails (no gitleaks binary, for example)
  and does not return the unavailable mapping of DEC-260. W1-20 catches it or this module changes. A machine without
  `gitleaks` on `PATH` skips the whole W1-17 suite.
- **What a query finds.** A query that starts or ends inside a token (`floor_rules` in `partition_floor_rules`) is
  not found, because FTS5 picks candidate chunks by whole tokens. Other letter case, stems, queries across lines,
  ranking, limits and an empty query are unhandled and untested. CAP-11.a's "every occurrence" holds for whole
  tokens only; W1-20 or W1-41 decides whether that is enough.
- **"2.8 s scale"** is held as 10 s on the search after one edited file; G-20 was not read (DEC-341).
- **No version pin in the store.** A change to the chunker or tokenizer needs `.gov-runtime/` deleted and rebuilt;
  nothing detects it. An untracked path map or `.gitleaks.toml` does not trigger re-judging when it changes; a
  committed map change does, and moves unchanged files in and out of the index.
- **Parents are coarse** (DEC-343). Markdown sections are flat, a `#` line inside a code fence counts as a heading,
  and only `.md` and `.markdown` are documents. A Python parent is the outermost function; a method counts as a
  function, a class body and decorator lines belong to the module, and a file that does not parse is module-only.
- **Line numbers** come from `str.splitlines`, so a form feed or a Unicode line separator shifts the reported line.
  Non-UTF-8 and binary files are decoded with replacement and indexed if the filter lets them through; paths with a
  newline and tracked non-regular files are skipped.
- **Removed text stays in SQLite free pages.** This concerns text that passed the filter earlier, a file that later
  gained a secret included. Concurrent refreshes, and a file replaced between the filter's answer and the read, are
  not handled (the W1-15 residual, unchanged).
- **`lexical.py` imports `gov.secrets.CONFIG_REL`**, which is not in `gov.secrets.__all__`; W1-16 keeps or exports
  the name. The `export_policy`, `embedding_policy` and `permitted_roles` residuals that DEC-289 moved here are
  untested.
- **The carried code under `cli/govbridge/` is untouched**, since `cli/tests` still imports it; its query, store,
  freshness, corpus and git-object modules were not ported.
- **Size.** 370 lines against 240 plus 40 to 60 (DEC-343), docstrings and comments included.
- **Workers ran unsandboxed** (interim, DEC-183). The test designer left a throwaway reference implementation in
  its session scratch directory outside the repository.
