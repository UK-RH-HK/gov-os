
## W1-10 residuals (store and record graph, 2026-10-04)

Recorded at W1-10's close, from the ticket lead's summary. None is a defect; each is for a later ticket.

- **Who writes `.gov-runtime/store.db` in a live session** is open with the owner (W1-10 DP-3). The guard keeps
  `.gov-runtime/` outside `scratch/` closed to worker roles, and W1-17, W1-20 and W1-24 read the store in worker
  sessions. Every W1-10 test builds the store in a temporary repository.
- **What loads as a record today (DEC-274).** The charter, the contract and the plan have `id` and `status` but no
  `type`, so the load reports them invalid. The seven kernel templates load as records with placeholder ids.
  Decisions are headings in the register, not files, so every `DEC-…` reference is dangling. Two files with one id
  both load.
- **Dangling edges in this repository (DEC-277).** A ticket's `depends_on` holds WBS ids while its `id` is the tk id.
  Trailer values such as `decision-record`, `owner-prompt` and `CAP-58.a` name no record. Unresolved trailers appear
  in `dangling()` with type `IMPLEMENTS` or `TASK`; `TASK` is outside the eight edge types.
- **The four edge keys DEC-012 does not name** (`evidence_for`, `tests`, `generates`, `validates`) are to be checked
  against the archived Framework §11.2 by a product-spec worker before any real record uses them (DEC-277).
- **Records are read from `HEAD`**, not the working tree: an uncommitted edit to a record is not in the graph.
  Untested.
- **The DEC-182 boundary** uses the committer date in the commit's own time zone; no test fixes which date decides.
- **The digest (DEC-276)** covers records (path, id, type, status), edges, commits, trailers and each commit's
  changed paths. It does not cover other frontmatter keys or the record body, and no `content_hash` is stored.
- **Merge commits** list no changed paths, so they never match `commits(root, path=…)`. Renames are untested.
- **Two new error codes**, `STORE_MISSING` and `STORE_GIT_FAILED`, are untested.
- **Not tested:** the `owner` and free `links` filters of CAP-08.a; no KPI line names them.
- **A load replaces only its own five tables**, in one transaction, so tables a later ticket adds to the same file
  survive.
