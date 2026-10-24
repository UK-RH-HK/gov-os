# W2-69 research note: the secrets scan reads what the stores hold

- **Ticket:** DAEO-rmbe (W2-69), profile FULL. Written by a research worker launched as `engineer`.
- **Date:** 2026-10-23. Branch `w2/W2-69`, base commit `c2d539c6`.
- **Tools measured:** gitleaks 8.30.1 (`~/.local/bin/gitleaks`, the one `PATH` finds); SQLite 3.45.1 under Python 3, built with `SECURE_DELETE`, `ENABLE_FTS5` and `ENABLE_DBSTAT_VTAB`.
- **Code under test:** this worktree's `src/` (`gov.__file__` = `/home/usain/gov-os-worktrees/W2-69/src/gov/__init__.py`).
- **Sources:** DEC-897 item 1 (the question), DEC-853, DEC-290, DEC-298, DEC-347, DEC-899; package P-W2-62-G1 §2; rows W2-M404 and W2-M395.

No matched bytes appear anywhere in this note. Every token-shaped string used in a test was built at run time from parts and never printed. The output of every experiment was positions, lengths, rule ids, counts, sizes, times and exit codes only. gitleaks always ran with `--redact`.

## 1. The question

DEC-897 item 1 asks: should the secrets-indexing check scan the indexed text (each SQLite store's rows, as text) instead of the database's raw bytes? That option comes with:

- each store compacted (`VACUUM`) after each rebuild, so no deleted text survives in free pages;
- a boundary-aware raw scan kept only as a backstop.

The other option is boundary-aware raw reads alone. The ticket's KPIs decide:

- **K1:** a real token is found at every offset and in every form the stores hold it.
- **K2:** a word-internal fragment of a longer identifier is never flagged, wherever a read begins.
- **K3:** after a full rebuild, deleted text is in neither a store's rows nor its free pages.
- **K5:** every file scanned today is still scanned, with every rule set. A scan that cannot finish fails closed. DEC-853's clean-result reuse stays, and a finding is never reused.

## 2. The answer, in short

**Scan the rows as text, compact each store after each rebuild, and keep a raw backstop that reads only a store's freed space.** All three parts are needed, and every piece of input is laid out so that each gitleaks read begins at a true boundary.

- **The primary scan** reads every stored value of every table, and `sqlite_master`, as its own chunk.
  - Text is read as stored. Blobs are read as bytes, and again without their zero bytes.
  - Each chunk is cut into pieces of at most 16,000 bytes at whitespace, and the pieces overlap.
  - Each piece is followed by a blank line, so gitleaks' reads can only begin at a piece start (section 4).
- **Compaction:** after each store's build, the rebuild runs FTS5 `optimize` on every FTS5 table, then `VACUUM`. VACUUM alone leaves deleted words in the full-text index's live rows (section 7).
- **The backstop** reads only the freed space of each SQLite file: freelist pages, freeblocks, and the unallocated gap of each b-tree page. It never reads live cells, so it cannot join fields (W2-M395). After compaction the freed space holds no text.
- **Files that are not SQLite stores** are scanned raw, laid out in pieces in the same way.

Boundary-aware raw reads alone fail K3 and leave the byte join (W2-M395) as a chance red. The tests below show it.

## 3. Method

All work was read-only on the worktree's `.gov-runtime/`, except for one copy of the code-graph store in scratch. The record store was measured read-only in place, or as an in-memory image (`serialize`/`deserialize`), never as a file copy.

| Script (scratch, not committed) | What it does |
|---|---|
| `probe_reads.py`, `probe_exact.py` | Find where gitleaks begins each read of standard input. A probe rule per column, `\b` plus that column's unique 4-gram, fires only where a read begins inside a line. |
| `probe_pieces.py` | Test whether blank-line-separated pieces pin gitleaks' read starts, in four delivery modes. Test today's check on a token that straddles a read edge. |
| `cut_test.py`, `cut_each.py` | The package's cut test on the rebuilt code-graph store. |
| `options.py` | Each option on a store, timed. |
| `byte_join.py` | Token-shaped matches in the raw bytes that no single stored value holds. |
| `residue.py` | Freed space, read from the file format: freelist trunk and leaf pages, freeblocks, unallocated gaps. |
| `vacuum.py`, `vacuum_mem.py` | VACUUM and FTS5 `optimize`, timed, with freed space before and after. |
| `deletion.py` | A synthetic token written, deleted and looked for, before and after compaction. |
| `k_tests.py` | K1 and K2 sweeps around piece edges, UTF-16 forms, and the byte join reproduced. |

Rules: the project's `.gitleaks.toml` as the check reads it (`gov.secrets._rules`: two rule sets, DEC-347). Rule set 0 is the project file with gitleaks' defaults (`useDefault`). Rule set 1 is the project's rules alone. gitleaks' default rules were read from the TOML embedded in the binary.

- Rules in all: 226 (222 defaults and the project's 4).
- 71 begin with a word boundary `\b`: the project's 4 (`gov-canary`, `gov-token-digit`, `gov-token-upper`, `gov-token-lower`) and 67 defaults.
- 152 defaults end with an end-of-text alternative (`|$)`). 11 rules end with `\b`. 225 are keyword-gated.

## 4. The mechanism: how gitleaks reads standard input

**Finding:** gitleaks cuts standard input into fragments and matches each fragment on its own. A fragment's start is a text start, so `\b` and `^` match there.

A fragment is built in two steps:

1. one `Read` of up to 100,000 bytes, of whatever the source delivers at once;
2. a peek, byte by byte, until two newlines with only spaces, tabs or `\r` between them, or until 25,000 more bytes.

The peek's byte reads refill a 4,096-byte buffer, so the next `Read` returns only what is left in that buffer. In steady state, a fragment is 3,672 + 25,000 = 28,672 bytes (7 × 4,096).

Fragment starts measured on 2,020,000 bytes of synthetic text with no blank lines:

| Delivery | First fragment | Then | Fragments |
|---|---|---|---|
| stdin from a file | 125,000 (100,000 + 25,000) | every 28,672 | 64 |
| piped from `subprocess.run(input=…)`, as the check does (2 runs) | 90,536 (65,536 pipe buffer + 25,000) | every 28,672 | 65 |
| piped, 1,000-byte writes with pauses | 89,000, then one of 25,480 | every 28,672 | 64 |
| piped, 50,000-byte writes | 88,136 | every 28,672 | 65 |

So the split depends on how the pipe delivers the bytes (timing), not only on the layout. Every rebuild changes the layout, and so where the reads begin.

**The blank-line stop pins the reads.** The input was cut into pieces at arbitrary bytes, and each piece was followed by a blank line. Each fragment start was compared with the piece starts.

| Piece size (bytes) | Delivery modes tried | Fragment starts away from a piece start | Piece starts missed |
|---|---|---|---|
| 20,011 | file, piped, 1,000-byte, 333-byte writes | 0 | 0 |
| 24,000 | the same four | 0 | 0 |
| 24,990, 24,999, 25,001 | file, piped, 1,000-byte writes | 0 | 0 |
| 26,000 | the same three | 16 to 18 | 0 |
| 40,000 | the same three | 45 | 0 |

**Confidence: high.**

- The figures match the read-plus-peek model to the byte: 100,000 and 65,536 for the first read, 25,000 for the peek, 4,096 for the buffer.
- The pinning holds in every delivery mode up to the peek limit and fails just past it.
- The gitleaks source was not read. The model is inferred from these measurements.

## 5. Today's check against K1 and K2

Today the check gives gitleaks one input per file: the raw bytes, then the rows as text, then the bytes without zero bytes.

**K2 fails (the chance red).**

- **The cut test on the lead's fresh code-graph store** (`.gov-runtime/codeintel/home/code.db`, 92,405,760 bytes, copied as one file). Each rule's expression with its leading boundary finds no match in the line. Without the boundary it finds a candidate inside a word.

| Rule | Candidate at byte | Length | Enclosing `[\w-]` run | Offset in the run | Line length | Whole line, sets 0 and 1 | Line cut at the candidate, sets 0 and 1 |
|---|---|---|---|---|---|---|---|
| `gov-token-lower` | 667,648 | 19 | 31 | 12 | 32,594 | exit 0, 0 | exit 3, 3 (`gov-token-lower`) |
| `gov-token-upper` | 11,702,403 | 34 | 45 | 11 | 70,275 | exit 0, 0 | exit 3, 3 (`gov-token-upper`) |
| `vault-service-token` | 3,063,894 | 27 | 14 | 13 | 42,260 | exit 0, 0 | exit 0, 0 (keyword or entropy gate) |

- **Word-internal candidates in this store**, for the 55 of the 71 leading-`\b` rules that Python's `re` compiles (16 use Go-only syntax):

| Rule | Raw bytes | Rows as text | Raw without zeros |
|---|---|---|---|
| `gov-token-lower` | 58 | 6 | 58 |
| `gov-token-upper` | 4 | 2 | 4 |
| `vault-service-token` | 30 | 36 | 30 |
| others | 0 | 0 | 0 |

  Every one of these 100 or so places is a chance red whenever a read happens to begin on it.

- **Synthetic:** a word-internal token-shaped string, placed at 7 offsets around the first fragment edge of today's check, was flagged at exactly 1 of the 7: the offset on the edge.

**K1 also fails (a miss, which is new).**

- A real token at a word boundary (after a space), placed so that it straddles one of today's fragment edges, is **missed** when it begins 1, 3, 5, 8 or 12 bytes before the edge.
- It is found when 21 bytes or more lie before the edge, and found in a control placed away from any edge.
- gitleaks' fragments do not overlap. So a token cut by an edge is lost, unless the part before the edge is a full match.
- Today this hole is open on any input over about 25,000 bytes without blank lines. That includes 144 of the 2,047 non-store files under `.gov-runtime/`.

## 6. The stores a rebuild writes

| File | Writer | SQLite | Journal mode | `-wal`, `-shm`, `-journal` beside it | Size (bytes) | Page size | Pages | Free pages |
|---|---|---|---|---|---|---|---|---|
| `.gov-runtime/store.db` | record store, lexical index, semantic store (`gov.store.load`, `gov.retrieval.lexical`, `gov.retrieval.semantic`) | yes | delete | none | 240,062,464 | 4,096 | 58,609 | 0 |
| `.gov-runtime/codeintel/home/code.db` | the code-graph tool (codebase-memory-mcp, its own SQLite) | yes | delete | none | 92,405,760 | 65,536 | 1,410 | 8 |
| `.gov-runtime/codeintel/home/_config.db` | the code-graph tool | yes | delete | none | 12,288 | 4,096 | 3 | 0 |
| `.gov-runtime/query-vector-cache.db` | searches (`gov.retrieval.semantic`), not the rebuild | yes | delete | none | 20,480 | 4,096 | 5 | 0 |
| 2,047 other files (21,801,978 bytes): code-index file copies, logs, `config.json`, records, snapshots, scratch | various | no | — | — | — | — | — | — |
| 6 placeholder device files | the sandbox | no (not regular files) | — | — | — | — | — | — |

- None of the stores uses WAL, and no `-wal`, `-shm` or `-journal` file was present after the lead's rebuild.
- The record store, the lexical index and the semantic store are one file (`store.db`).
- The record store is rebuilt by `DROP TABLE` and `INSERT`. The lexical and semantic stores are updated in place (`DELETE` and `INSERT`).
- The code-graph store is built anew after its folder is removed. But the tool deletes and rewrites rows while it builds.

Freed space as built (the file-format parse in `residue.py`):

| Store | Freelist pages: bytes / non-zero | Freeblocks: count / bytes / non-zero | Unallocated gaps: bytes / non-zero | Text-like runs (20+ word bytes) in freed space |
|---|---|---|---|---|
| `store.db` | 0 / 0 | 2,176 / 218,379 / 0 | 5,377,995 / 87,971 | 159, on 153 pages |
| `code.db` | 524,252 / 515,822 | 114 / 154,047 / 152,033 | 5,049,411 / 676,055 | 1,616 |
| `_config.db`, `query-vector-cache.db` | 0 / 0 | 1 / 4 / 0 | about 10 to 12 KB / 0 | 0 |

- gov's own writers zero deleted cells, because this machine's SQLite is built with `SECURE_DELETE`. That is a build default, not a setting gov makes. Unallocated gaps still keep 159 text-like runs.
- The code-graph tool's SQLite does not zero freed space. Its free pages and freeblocks keep the old bytes.

## 7. Compaction (K3)

**A synthetic token in a synthetic store** (400 rows of filler), counted in the rows and in the raw bytes:

| Case | `secure_delete` | Written: rows / raw | Deleted: rows / raw | After FTS `optimize`: rows / raw | After `VACUUM`: rows / raw |
|---|---|---|---|---|---|
| delete one row | 0 | 1 / 1 | 0 / **1** | — | 0 / 0 |
| drop the table | 0 | 1 / 1 | 0 / **1** | — | 0 / 0 |
| FTS5 (the lexical tokenizer), delete one document, optimize, then VACUUM | 0 | 3 / 2 | **1** / 2 | 0 / 1 | 0 / 0 |
| FTS5, delete one document, VACUUM only | 0 | 3 / 2 | **1** / 2 | — | **1** / **1** |
| delete one row | 1 | 1 / 1 | 0 / 0 | — | 0 / 0 |
| drop the table | 1 | 1 / 1 | 0 / 0 | — | 0 / 0 |
| FTS5, delete, optimize, then VACUUM | 1 | 3 / 2 | **1** / 1 | 0 / 0 | 0 / 0 |
| FTS5, delete, VACUUM only | 1 | 3 / 2 | **1** / 1 | — | **1** / **1** |

What this shows:

- An FTS5 delete leaves the deleted term in the index's live rows (`<table>_data`) until its segments are merged.
- Neither `secure_delete` nor `VACUUM` removes it. FTS5 `optimize` does.
- So **K3 needs `optimize` on every FTS5 table, then `VACUUM`**: on `lexical_fts` in `store.db`, and on `nodes_fts` in `code.db` (contentless, `content=''`, where `optimize` still applies).

**On the real stores:**

| Store | Step | Time | Size (bytes) | page_count | freelist_count | Freed bytes, non-zero | Text-like runs in freed space |
|---|---|---|---|---|---|---|---|
| `code.db` (file copy, on disk) | as built | — | 92,405,760 | 1,410 | 8 | 1,343,910 | 1,616 |
| | `VACUUM` | 0.45 s | 91,488,256 | 1,396 | 0 | 32 | 0 |
| `code.db` (in memory) | `optimize nodes_fts` | 0.03 s | 96,403,456 | 1,471 | 70 | 434,267 | 1,597 |
| | then `VACUUM` | 0.13 s | 91,422,720 | 1,395 | 0 | 32 | 0 |
| `store.db` (in memory) | as built | — | 240,062,464 | 58,609 | 0 | 87,971 | 159 |
| | `optimize lexical_fts` | 0.06 s | 244,207,616 | 59,621 | 1,063 | 99,066 | 159 |
| | then `VACUUM` | 0.31 s | 238,526,464 | 58,234 | 0 | 4,749 | 0 |

- On disk, `store.db`'s VACUUM will take longer than in memory: it rewrites about 240 MB and syncs it. The code-graph store's 92 MB took 0.45 s on disk.
- No `-wal` or `-shm` file results, since the stores use the rollback journal. The `-journal` file is removed when the VACUUM commits.

## 8. Boundary-aware: what it means, and the tests

**The layout used in every test** (`lab.pieces`, `lab.layout`):

- **One chunk per thing that is one text:**
  - a stored value (for the rows option);
  - a file (for a file that is not a store);
  - a freed region (for the backstop).
  Chunks are never joined to each other, so no match can span two values.
- **Pieces of at most 16,000 bytes.** The peek limit is 25,000, so a piece always ends within one peek.
  - The next piece begins right after the last whitespace byte (tab, newline, vertical tab, form feed, carriage return, space) at least 4,096 bytes before the current piece's end.
  - Failing that, it begins after the last byte that is no word byte.
  - So consecutive pieces overlap by at least 4,096 bytes, and a match up to 4,096 bytes long that begins in a piece is whole in that piece.
- **A blank line after every piece.** Section 4 shows that gitleaks then begins a read only at a piece start, in every delivery mode.
- **Why a piece start is a true boundary.** The byte before a piece start is whitespace in the original. So the start behaves as the original text does for every rule that begins with `\b`, with `^`, or with a class of printable non-word bytes.
- **A leading newline** before the whole input. Without it, gitleaks takes an input that begins with the SQLite header for a binary file and skips it. The first test without it passed falsely, in 0.5 s.

**K1 and K2 sweeps** (`k_tests.py`). Each case is 80 values of 40,000 bytes, with the string at each of the 80 offsets from 40 bytes before a piece edge to 39 after it. Findings were mapped back to their value.

| Filler | String | Exit, sets 0 and 1 | Result |
|---|---|---|---|
| words and spaces | real token after a space (`gov-token-lower`) | 3, 3 | found in 80 of 80 |
| words and spaces | the same string inside a word | 0, 0 | flagged in 0 of 80 |
| dots, no whitespace (non-word cuts) | real token after a dot | 3, 3 | found in 80 of 80 |
| dots, no whitespace | the same string inside a word | 0, 0 | flagged in 0 of 80 |

**UTF-16** (a synthetic store, with `PRAGMA encoding = 'UTF-16le'`, holding a token as text and a token in a UTF-16LE blob):

| How it is read | Exit, sets 0 and 1 | Found |
|---|---|---|
| rows: the text value (SQLite returns it as UTF-8) | 3, 3 | yes |
| rows: the blob as bytes, and without its zero bytes | 3, 3 | yes, in the zero-stripped copy |
| rows: the blob as bytes only | 0, 0 | **no** |
| raw: the file's bytes, and without zero bytes | 3, 3 | yes, in the zero-stripped copy |
| today's check | — | yes |

So the rows scan must give each blob that holds a zero byte twice: as it is, and without its zero bytes. Today's `str(value)` of a blob renders `b'…\x00…'`. That rendering puts a digit or a letter before a token, so a token at a true boundary inside a blob is missed by today's rows part. Today, only the raw part catches it.

**The byte join (W2-M395) reproduced.** A synthetic record has three columns:

- its header ends with the serial type of a 51-byte text, `0x73`;
- its first column is the 16-bit integer `0x6B2D`;
- its second column is a 24-byte identifier, whose serial type `0x3D` is no word byte.

The raw bytes spell a token-shaped string at a word boundary that no stored value holds.

| How it is read | Exit, sets 0 and 1 | Result |
|---|---|---|
| raw bytes, boundary-aware pieces | 3, 3 | **red** (the join is at a true boundary; pieces do not help) |
| rows, value by value | 0, 0 | clean |
| today's check | — | red |

On the lead's fresh code-graph store, no match of the token rules in the raw bytes lacks a stored value that holds it (`byte_join.py`: 0 for each rule, raw and zero-stripped; `sourcegraph-access-token`'s 25 matches are each held by a value). W2-M395's join depended on one row id, which moves with each rebuild.

## 9. The options on the stores, with timings

Each input was given to both rule sets, so 2 gitleaks runs per file in every option. Times are wall-clock on this machine, with 20 processors.

| Store | Option | Input (bytes) | Pieces | Cuts after a non-word byte | Cuts inside a word | Build | Scan | Verdict |
|---|---|---|---|---|---|---|---|---|
| `code.db` | today (`_store_content`, `_holds_secret`) | 206,870,474 | — | — | — | 0.7 s | 21.9 s | clean (on this rebuild) |
| `code.db` | rows, value by value | 75,990,065 | 832,331 | 268 | 0 | 1.3 s | 5.0 s | clean |
| `code.db` | raw and raw without zeros, in pieces | 254,191,062 | 15,886 | 963 | 0 | 0.5 s | 16.7 s | clean |
| `store.db` | today | 769,810,239 | — | — | — | 10.0 s | 70.9 s | clean |
| `store.db` | rows, value by value | 393,165,471 | 544,974 | 0 | 0 | 3.7 s | 22.7 s | clean |
| `store.db` | raw and raw without zeros, in pieces | 620,898,618 | 38,802 | 3 | 0 | 0.7 s | 40.4 s | clean |
| `store.db` | backstop: the freed-space parse | about 5.6 MB of regions | — | — | — | 0.16 s | — | — |
| 2,047 other files | pieces | 21,801,978 | 3,057 | 0 | 0 | — | — | — |

- `code.db` holds 1,626,918 values: 832,498 numbers or nulls and 37,565 blobs with zero bytes. The longest value is 355,810 bytes.
- `store.db` holds 754,522 values: 257,075 numbers or nulls and 47,523 blobs with zero bytes (the semantic vectors). The longest value is 24,575 bytes.
- No UTF-16-like text was found in either store.

## 10. The two options against the KPIs

| KPI | A: rows as text, compaction, freed-space backstop | B: boundary-aware raw reads alone |
|---|---|---|
| K1: a real token found at every offset and in every form | **Passes.** Every value is read as stored, and blobs also without zeros (section 8, UTF-16). Piece overlap finds a token across every cut: 80 of 80 in both sweeps. A token in freed space is read by the backstop. | **Passes** for live values and freed space alike, with the same pieces: 80 of 80. |
| K2: no word-internal fragment flagged | **Passes.** Reads begin only at piece starts, which are true boundaries (0 of 80, and 0 forced cuts in today's stores). No join of fields, since each value is its own chunk. | **Passes K2 as written.** But raw bytes of different fields still join into token-shaped strings at true boundaries. That is the byte join, a chance red of its own (section 8: red). |
| K3: no deleted text after a rebuild | **Passes** with FTS5 `optimize` then `VACUUM` in the rebuild: 0 in rows and 0 in raw bytes, for every case in section 7. The backstop checks it: freed space with text fails closed. | **Fails on its own.** A raw scan sees deleted text but does not remove it. K3 is a property of the stores, so B needs the same compaction. Without `optimize`, the FTS5 index keeps deleted terms in its live rows. |
| K5: every file still scanned, with every rule set | **Passes.** Each SQLite file: values, `sqlite_master` and freed space. Other files: raw, in pieces. Both rule sets. | **Passes:** every file raw, in pieces. |
| K5: fails closed | A store that cannot be opened or parsed is scanned raw in pieces, or the check raises. Never clean undecided. | The same. |
| K5: DEC-853 reuse | The digest stays the sha256 of the file's bytes: the same bytes give the same values and the same freed space. `_FORM` goes to 2, so no clean result of the old form is trusted. A finding is never recorded. | The same, with `_FORM` 2. |
| W2-M395, the byte join | **Settled.** Live cells are never read as one text. | **Not settled:** it stays a chance red. |
| Cost on `store.db` + `code.db` | 27.7 s of scanning (rows) and under 1 s of backstop parse, against 92.8 s today. Plus FTS `optimize` and VACUUM in the rebuild: under 1 s in memory, a few seconds on disk. | 57.1 s of scanning, plus the same compaction if K3 is to pass. |

## 11. The answer

**Option A.** Scan the rows as text, compact each store after each rebuild, and keep a boundary-aware backstop that reads only freed space.

Why, in terms the tests can check:

- **K2 and the byte join** pass only if no read begins inside a word and no match can span two fields. Option A is the only one that does both. Option B's raw bytes join fields (section 8: red on the synthetic join, at a true boundary).
- **K3** needs compaction in either option, and compaction needs FTS5 `optimize` before `VACUUM` (section 7). Once the stores are compacted, a raw scan of live pages adds nothing that the rows do not hold, except joins.
- **K1:** both options find every real token at every offset, with overlapping pieces. Today's check misses one that straddles a read edge (section 5). Option A must read blobs as bytes and without zeros, never as `str(blob)`.
- **Cost:** option A is the cheapest. Its scans are about 3.3 times faster than today's on the two large stores.

**What the primary scan reads**, for each SQLite file under `.gov-runtime/`:

- Every row of every table listed in `sqlite_master` (FTS5 shadow tables included), and the rows of `sqlite_master` itself (schema text, which today is reached only through the raw bytes).
- Each value is its own chunk:
  - text exactly as stored (`text_factory = bytes`, no lossy decoding);
  - a blob as its bytes, and again without its zero bytes when it holds any (UTF-16);
  - numbers and nulls are skipped, since they cannot hold a token.

**What the backstop reads, and how it is kept from the chance red and the byte join:**

- **It reads only freed space,** found from the file format:
  - freelist trunk pages (after their page list) and leaf pages;
  - on each b-tree page, the gap between the cell pointer array and the cell content area, and each freeblock (after its 4-byte header);
  - left for the implementation: the unused tail of each overflow chain's last page.
- **Each region is its own chunk, laid out in pieces like the values.** So no read begins inside a word.
- **It never reads a live cell,** so live fields cannot join.
- **After compaction, freed space holds no text-like run** (section 7: 0 on both large stores). The backstop then finds nothing, by construction.
- **A finding there fails closed.** It means a store was not compacted, or a secret was deleted and is still on disk. Either way the cure is a rebuild, not luck.
- **Inside a dead cell, a join of its old fields is possible.** But only on a store left uncompacted, and it then fails closed. It never moves with a rebuild.

**Files that are not SQLite stores** (the code-index file copies, logs, JSON, records, snapshots, scratch, and any `-wal`, `-shm` or `-journal` file) are scanned raw, in pieces.

**If a SQLite file cannot be opened or parsed,** for example a damaged header, the scan falls back to the raw bytes and the raw bytes without zeros, in pieces. That fallback may be red by a join, but it is never clean by default. The first file that cannot be decided still raises, as today.

## 12. The compaction step in the rebuild

- **Where:** `src/gov/rebuild/command.py`, after each store's build.
  - After `store_load`, `lexical_refresh` and `semantic_refresh`, which all write `.gov-runtime/store.db`: compact once, after the last of them (or after each).
  - After `codeintel_index`: compact `.gov-runtime/codeintel/home/code.db` and `_config.db`.
- **What, in order, on one connection:**
  1. `INSERT INTO <fts>(<fts>) VALUES ('optimize')` for every FTS5 table in the store: `lexical_fts` in `store.db`, `nodes_fts` in `code.db`. Find them from `sqlite_master` (`sql LIKE 'CREATE VIRTUAL TABLE % USING fts5%'`), not from a fixed list.
  2. `VACUUM`.
- **`query-vector-cache.db`** is written by searches, not by the rebuild. It holds hashes and vectors, no text of a query. Compacting it in the rebuild costs nothing (20 KB) and keeps the backstop quiet. Recommended, but outside "each store's build".
- **The record store's digest does not change.** It is taken over rows, not bytes, so two rebuilds from one commit keep one digest.
- **If compaction fails,** for example a busy lock from the code-graph tool's daemon, the rebuild should report that store as not compacted. The backstop then fails closed on any text left in freed space.
- **`PRAGMA secure_delete = ON`** in gov's own writers would make deletes zero their bytes on every build of SQLite, not only on this machine's. But it is outside this ticket's paths, and compaction already covers K3.

## 13. Row W2-M395 (the byte join)

**Settled by the choice.**

- The primary scan reads value by value, so bytes of different fields never meet.
- The backstop reads only freed space, which compaction empties of text.
- The join that W2-M395 recorded (a header byte, two row-id bytes and the next text) cannot arise in either on a compacted store.

This is the outcome W2-M395's own fix text asks for: each stored value, and the freed space of each page, judged separately.

So W2-45 need not build a per-value scan of its own. Whether W2-45's ticket drops the row is for the orchestrator to record.

## 14. Residuals and open questions

- **Read ends, not only read starts.**
  - 152 default rules end with an end-of-text alternative, and 11 end with `\b`. A fragment that ends inside a word can fake a terminator.
  - The test layout cut piece ends at a fixed size. The implementation should end each piece just after a whitespace byte as well, where one lies within the overlap, so that both edges are true boundaries.
  - K2 covers read starts only. A test of read ends is worth adding.
- **Keyword gating** (225 of 226 rules) depends on what shares a fragment. With pieces, a value's context is its own piece and its 4,096-byte overlap, not whatever today's 28,672-byte fragment held. That is deterministic now, but it differs from today: a 40-hex string next to a far-off keyword is judged with less context.
- **Forced cuts inside a word:** none in today's stores, 0 of 1,435,050 pieces. A run of more than about 12,000 word bytes with no other byte would still need one.
  - Recommended: begin such a continuation piece with one neutral word byte, so no false boundary appears at its start, and count it.
  - The alternative is to fail closed, which could block on a large base64 value.
- **The overlap of 4,096 bytes** covers matches up to that length. A PEM private key longer than that, which straddles a cut, needs a larger overlap (8,192 bytes holds an RSA 8192 key).
- **16 of the 71 leading-`\b` rules** use Go-only syntax that Python's `re` does not compile. The word-internal candidate counts in section 5 cover the other 55. The K2 tests should place strings for every one of the 71.
- **The freed-space parser** here skips overflow-page tails and the lock-byte page. The implementation needs both, and a test on a store with overflow chains (the code-graph store's longest value is 355,810 bytes).
- **The code-graph tool's SQLite** does not zero freed space. Compacting it from gov depends on the tool not holding the file. Seen today: no `-wal`, no `-shm`, rollback journal.
- **On-disk VACUUM of `store.db`** was not timed: no file copy was made, to stay within scratch. In memory it took 0.31 s; on disk, expect a few seconds.
- **Today's two-rule-set scans** were run on every input. Option A keeps both, and it keeps 2 gitleaks runs per file. It could join all of a store's chunks into one input per rule set, as tested, because findings map back to chunks by line.

## 15. What the implementation changed and measured

Added by the engineer after the code (2026-10-23, commits on `w2/W2-69` after `ab381f94`).

- **Freed regions are read also without their zero bytes.** Section 11 read freed space only as it is. The acceptance case `freed-space-a-freeblock-of-a-utf16-store` (a token deleted from a UTF-16 store, left in a freeblock) was missed that way. Each freed region now gets both forms, like a value. The word-internal cases on freed rows, UTF-16 stores and blobs stay green.
- **Both edges of a piece are cut at a true boundary.** A piece ends just after a space, else just after a byte that is no word byte (section 14, read ends). Where a window holds neither, the cut is inside a word. The piece then begins or ends with one neutral word byte (`_`), so no read seems to begin or end a word there.
- **Each store is read under a shared lock.** The values and the freed-space parse come from the bytes read while the lock is held, so the digest kept for DEC-853 is of what was judged. A store that is locked, damaged or cannot be parsed is judged by its raw bytes, in pieces, and also without its zero bytes.
- **Virtual tables are not read themselves.** Their rows are in their own tables, which are read. So a store whose FTS5 table needs a module this Python lacks is still read value by value.
- **The overflow tails** of section 14 are read: the unused tail of each overflow chain's last page. A builder test shows the tail is read and the live value before it is not.
- **Time on W1-15's stand-in** (60 files of 4 KiB and a SQLite store of about 9 MB, load average about 40): 4.1 s against 4.5 to 4.9 s for the check before this change.

**After the review's acceptance cases (2026-10-23, a later engineer round).** Four repairs:

- **An FTS5 index is read as its terms.**
  - A leaf page stores each term after the prefix it shares with the term before it, behind one or two varint bytes. Read as raw bytes, the stored tail of an identifier (`…sk_1…` after a shared head) begins after a byte that is no word byte. So a leading-`\b` rule matched it, even after `optimize` and `VACUUM`.
  - Each block of an FTS5 table's `_data` table that is a leaf page is now decoded from its page index into whole terms, without the leading byte that names the index (`0` for the main one). Each term is its own chunk.
  - Any other block (the averages, the structure, doclist-index and tombstone pages), and a leaf that does not parse, is read by its bytes as before.
  - The `_content` and `_idx` tables are read value by value, as before.
- **Long blocks, and blank lines inside them.**
  - The overlap goes from 4,096 to 9,216 bytes, so a private-key block of 8,192 bytes is whole in one piece. Pieces go from 16,000 to 24,000 bytes, still under gitleaks' peek of 25,000 (section 4).
  - A blank line inside a chunk now ended one of gitleaks' reads, so an armoured PGP key (a blank line after its header) was split. Each blank line of a chunk now gets a form feed before its second newline. To the rules, a form feed is a space (`\s`), but gitleaks' search for a blank line stops at it. So the only blank lines left are those between pieces.
- **A raw-bytes verdict on a store is not kept.**
  - The check now waits up to 10 s for a lock held by another process.
  - A SQLite store that still cannot be read is judged by its bytes, but a clean verdict on them is no longer recorded for DEC-853's reuse: the next run reads its values.
  - A clean result held from before is still reused for the same bytes. `_FORM` goes to 3, so no clean result of the earlier form is trusted.
- **The rebuild:**
  - The code-graph tool's stores are found from the resolved project. A relative `--root` made `relative_to` raise, and the rebuild returned no result.
  - A store that cannot be compacted is named on standard error with its reason, as well as in the JSON result.

**Time on a larger stand-in.** A 65 MB store, with an FTS5 index of the lexical tokenizer over three copies of `docs/` and `src/gov/`, plus 300 text files of about 20 MB in all. The two versions of the check were run alternately, at a load average of 19 to 28:

- the check before this round: 20.9 s and 21.2 s;
- after it: 21.0 s and 17.2 s.

Bytes given to gitleaks:

| Input | Before (MB) | After (MB) | Why |
|---|---|---|---|
| The store | 69.7 | 59.6 | Terms in place of whole leaf pages and their doclists |
| The files | 31.2 | 37.4 | The wider overlap |

**The last round (DEC-909, 2026-10-24, the engineer after `ed2de0eb`).** A key block longer than the overlap of 9,216 bytes was missed wherever a piece's cut fell inside it. One repair:

- **Each key block of up to 24 KiB also goes to gitleaks whole, as a piece of its own.**
  - Where a text is longer than one piece, each BEGIN marker (`-----BEGIN`, any case) is followed to the first END marker after it (`-----END`, a label, `-----`). If that span is at most 24,576 bytes, it is added as one more piece: from the first dash of BEGIN to the last dash of END, its blank lines given a form feed as the rest are.
  - The text's own pieces are cut as before. So every read edge they make is unchanged, and the added piece begins and ends with a dash, which is not a word byte. No read begins or ends inside a word there, which covers a BEGIN in mid-line, two blocks back to back and a block with text after its END.
  - A BEGIN with no END inside 24 KiB adds nothing. Nor does an END with no BEGIN, or a text short enough to be one piece already (that piece holds the block whole). A block over 24 KiB is read as before (row W2-L419).
  - The added piece and its separator stay under gitleaks' peek of 25,000 bytes, so it is whole in one read (section 4).
  - The change is in `_pieces`, which the check, the pre-index filter and the judgement of a path name share. Both rule sets still run on every input, and a scan that cannot decide still raises.
  - `_FORM` goes to 4, so no clean result recorded before the change is trusted.
- **Tests.** Every case in `tests/acceptance/W2-69` passes: 352, including this batch's 99. W1-15, W1-16 and the secrets files of W2-50 pass too.
- **Time on a large stand-in.** A 31 MB FTS5 store built with the lexical tokenizer from three copies of the repository's clean `docs/` and `src/gov/` texts, plus 300 text files of 70 KB each. The two versions were run alternately, at a load average of 21 to 27:
  - before: 17.7 s and 16.4 s;
  - after: 17.2 s and 16.1 s.
- **Seen on that stand-in: keyword gating varies with the pipe (section 14).**
  - On one input, `sourcegraph-access-token` flagged twelve 40-hex terms (commit hashes) when the word `sourcegraph` shared a gitleaks read with them.
  - Reads end only at the blank lines between pieces, but which pieces share a read still varies with how the pipe delivers the bytes. Both runs of the earlier check flagged the store; one of the two runs of this check did not. Three probe runs of one fixed input all found the same twelve.
  - That is not a read edge inside a word, and this round does not change it.
