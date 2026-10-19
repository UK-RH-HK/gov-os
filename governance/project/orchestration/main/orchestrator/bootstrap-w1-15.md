
## W1-15 residuals (secret rules, pre-index filter and the secrets-indexing check, 2026-10-04)

Recorded at W1-15's close, from the ticket lead's summaries and the reviewer's fourteen findings, seven of which were
fixed. None of the following is a defect of the ticket; each names who should settle it.

- **A project can remove or rewrite a template rule** (DEC-299). The project's `.gitleaks.toml` is the one source of
  rules (DEC-287); its allowlists and disabled rules are ignored by the filter and the check (DEC-290, DEC-298), but a
  rule the project deleted, such as the canary rule, is not put back. A file with no rules at all is refused. A
  project file that extends another file with rules of its own still inherits that file's allowlists.
- **The rules over-block.** The token rule flags ordinary identifiers (`pk_…`, `tok_…`, `rk_…`, `sk-…` of 16 or more
  characters), and the canary rule flags any upper-case identifier with the canary word in the middle. This
  repository loses only the W1-15 ticket file from an index; an adopting product could lose code files. Requiring a
  digit or mixed case in the token body is the suggested repair.
- **Near spellings of the canary are missed** (lower case, other separators, markdown-escaped underscores); they are
  outside DEC-286. The owner still confirms the count of seven canaries against the S0b1 manifest.
- **Path-map patterns match narrowly.** `**/x/**` does not match a top-level `x/`; a trailing slash, a leading `/` or
  `./`, `?` and `[]` match nothing; `paths` given as a string is read character by character with no error. For the
  path-map schema (W1-27 replaces the minimal one, DEC-228).
- **The two W1-08 residuals that named W1-15** (closed lists for the free-text namespace fields; the meaning of
  `permitted_roles`) move to the first ticket that reads export or embedding policy, W1-17 or W1-24 (DEC-289). W1-15
  reads only a namespace's `paths` and `memory_class`.
- **What the check does not see.** Compressed stores and bundles (`.gz`, deflated `.zip`, `.tar.gz`, a gzip BLOB),
  for W1-24 if bundles are compressed; UTF-32 text; a secret in a store file's or folder's name, which is also
  printed in the check's output when the content matches; SQLite WAL side files are scanned as plain bytes only.
- **What the filter cannot see.** A file replaced after the filter answered and before the indexer reads it (for
  W1-16, W1-17 and W1-19; the check is the backstop); a hard link to a product file; a secret split across lines or
  reversed.
- **`.gov-runtime/scratch/` counts as a store for the check**, so the check would be red in this repository on lead
  briefs and worker logs that name the canary. W1-26 settles this before `gov check` runs the check here.
- **gitleaks is trusted by name.** A stand-in `gitleaks` first on `PATH` that exits 0 passes everything; the version
  is not verified. The filter and check cases need gitleaks where they run; putting it on CI is an install for the
  owner, raised with W1-40 (DEC-287).
- **Edges that fail closed or noisily.** A configuration whose only rules come through `[extend] path` is refused as
  "no rules"; one with a TOML date value, or larger than about 128 KB, makes the filter raise; a not-green check on a
  ruleless configuration or an unreadable store exits with a Python traceback; a clean store with an unloadable
  virtual table, or a table name with a double quote, keeps the check red; a FIFO in a governance namespace would
  block the filter (reasoned, not run).
- **The root allowlist.** With the template's rules and no allowlist, gitleaks flags four tracked paths: the W1-15
  ticket file, which names the canary, and three brownfield fixture files. W1-15 allowlisted only the ticket file; the
  fixtures were already allowlisted. The list is the lead's reconstruction, not the first engineer's report.
- **A guard observation.** Twice in the parallel run a worker wrote a file inside its allowed paths through a Python
  script fed by a here-document in Bash, and the guard did not stop it. For W1-46 and W1-47's residual lists.
