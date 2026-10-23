task: Probe W2-69 (DAEO-rmbe, FULL) at head 3fd2b5a1 for behaviour its acceptance tests miss, and return the probe record's content for the lead to write.
status: DONE. The probe is complete. Its verdict is fail: one finding fails open in ordinary work (F1).
work_completed: Step 0 passed: (a) the write outside the worktree failed with "Read-only file system"; (b) `git hash-object -w` and `git update-index --refresh` both exited 0. GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-rmbe, top level /home/usain/gov-os-worktrees/W2-69, branch w2/W2-69, HEAD 3fd2b5a1e664d7c987a2c9a3ffaafd99f4c60a01, all as expected. `gov.__file__` = /home/usain/gov-os-worktrees/W2-69/src/gov/__init__.py. Read refusals: none from the guard; one from the sandbox (`.mcp.json` is a placeholder device). The guard refused three of my Bash commands: an inline heredoc ("cannot be read … gov pause (--off): refused (DEC-409)"); a gpg key generation ("Bash write to '/<guard-unresolvable>' denied"); and a sed after a cd it could not resolve. For the first and third I wrote or edited the script as a file in my temp folder with the Write and Edit tools; I dropped the gpg measurement. The sandbox also refused the code-graph tool's socket. The final cleanup `rm` needed a permission this session did not grant. I did not use gov retrieve: every file I read was named in the brief or found with a grep in a named folder. I read the ticket, DEC-897, DEC-853, DEC-290, rows W2-M395, W2-M404 and W2-L373, the package's outline, the research note, the acceptance README and the change. I ran about 25 probes against this worktree's src: on copies of the four real stores, on synthetic stores, and in temporary projects (one `gov rebuild` in a project of my own). The comparison code was the merge base's (c2d539c6) secrets module, saved as a single file. I also ran the unit and acceptance suites.
files_changed: none in the repository. Scripts and store copies exist only under my $TMPDIR. Step 0's `git hash-object -w` left one loose object, as the brief requires.
evidence: All probe output is positions, counts, lengths and exit codes only. Long key block by length in paragraph text, 246 placements: 3,961 and 4,091 bytes never cut; 4,221 bytes cut at 1%, 4,611 at 4%, 5,261 at 9%, 6,561 at 20%, 7,861 at 31%; every cut placement missed. The 6,561-byte block in paragraph text: new code missed 10 of 41, old code 0 of 41. PGP-shaped block of 6,580 bytes at cut placements: new found 0 of 6, old 6 of 6. End to end: the filter let the document in (old code kept it out), the rebuild indexed it as 293 chunks, and the check passed its file copy. Locked stores: run 1 exit 0 (old code exit 1, "database is locked"), run 2 exit 0 with both stores reused, run 3 exit 1 naming both. Lexical index: one synthetic word next to the identifier turns the store red; the real index holds 51 terms with a key prefix inside them, 3 at the exact layout and 8 within 3 bytes of it. File signatures: with "DICM" at offset 128 or "ustar" at offset 257 the token is not found; the control is found. WAL store: new code exit 0, old code names it. Relative root: ValueError. Compaction blocked by a reader: 32.3 s, "not compacted: database is locked". Cost on copies of the four real stores: 30.0 s new full scan, 5.6 s with reuse, 54.2 s old; peak memory 1.4 GB new against 5.3 GB old; load 15 to 23 on 20 processors. The old code is red on the lead's real store.db: generic-api-key over 59 bytes joining four fields of a lexical_chunk record on page 1895. No commits. Scratch at the end and at peak: 404 MB and 1,320 files and folders, within 4 GB and 100,000. One long probe outran the tool's 2-minute default and was moved to the background by the harness; I waited for its completion and read its output before going on.
tests: tests/unit/secrets_check and tests/unit/rebuild: 37 passed. tests/acceptance/W2-69 at the head, run file by file: 59 passed (K5, K1 forms, K4, K7), 20 passed (K1 read edges), 132 passed (K2), 3 passed (K3). In all, 214 passed, 0 failed, 1 not run: the code-graph daemon case, which cannot start here because the sandbox refuses the tool's socket.
discoveries: The merge base's check turns red on this worktree's rebuilt store.db through a byte join of record fields; the new check is green there, so the change removes a real chance red. Gitleaks 8.30.1 skips a whole input as binary when its first read carries a file signature at offset 128 or 257. The lexical index keeps identifiers whole, and FTS5's suffix encoding is a second source of reads that begin inside a word. VACUUM renumbers the hidden row ids of tables without an INTEGER PRIMARY KEY; no gov code relies on those ids today.
risks: F1's "ordinary work: yes" is my judgement under ADR-0001. Real key sizes were not measured, because the guard refused the gpg run. Timings were taken under load. Whether the code-graph daemon locks its store could not be observed. Copies of the real stores (internal content) remain in my $TMPDIR (stores/, cost/, probe/, p*/) because the removal was not permitted.
lessons: Write probe scripts to files: the guard refuses inline heredocs and a cd it cannot resolve. Gitleaks' fragments vary with layout, so a finding that spans values proves little from one layout: the split key was found 10 of 10 times in one layout and 0 of 15 once shifted. A fix to the piece layout must bump _FORM, or clean results judged under the old overlap stay trusted. Keep this record free of key-block markers, and do not name the 40-hex rule near the head's commit id (F8).
proposed_decisions: Classification for the lead's package (DEC-809): one finding fails open in ordinary work (F1), so a round; three are ordinary but fail closed (F3, F6, F9) and ride along (DEC-802); four are rows for the Wave 3 hardening pass (F2, F4, F7, F8), of which F2's reuse fix is cheap enough to ride along; one is an entry criterion of any ticket that switches a store to WAL or auto_vacuum (F5, DEC-803). Recommendation: resume W2-69 for F1, with F3, F6, F9 and F2's reuse riding along. Confidence: high on the behaviours, all reproduced; medium on F1's ordinary-work call.
unresolved: Whether the code-graph tool's daemon holds code.db locked during gov's own query sessions (sandbox). The actual sizes of real RSA-8192 and PGP keys (measurement refused). The K3 code-graph case was not run here. Whether W2-45 keeps row W2-M395: joins of record bytes are gone, joins of neighbouring values remain possible (F8).
recommended_next_action: Pass F1, F3, F6 and F9 to the test designer for cases, resume the engineer, and record F2, F4, F7 and F8 as Wave 3 rows and F5 as a DEC-803 entry criterion.

---

**Verdict: fail**

**Head probed:** 3fd2b5a1e664d7c987a2c9a3ffaafd99f4c60a01 (w2/W2-69). "The code before" means the merge base c2d539c6.

### Findings, most severe first

**F1 — High. A private-key block longer than 4,096 bytes, inside a text longer than 16,000 bytes, is missed by both the pre-index filter and the check whenever a piece edge falls inside the block.**
- **What was done:** I built key-shaped blocks of 3,961 to 7,861 bytes at run time, in the shape the default private-key rule matches. I placed them at every paragraph start between 120 KB and 180 KB of a 300 KB document. The new code and the old code judged each placement. Then I ran it end to end in a temporary project: the document in a governance namespace, the pre-index filter, `gov rebuild --no-embeddings`, then the check.
- **What happened:**
  - Blocks up to 4,091 bytes are never cut.
  - Longer blocks are cut at 1% (4,221 bytes), 4% (4,611), 9% (5,261), 20% (6,561) and 31% (7,861) of placements.
  - Every cut placement is missed, and only those. In text without blank lines: 10 of 10 and 11 of 11. In paragraph text: 10 of 10. A PGP-shaped block of 6,580 bytes: found at 0 of 6 cut placements.
  - The old code found every paragraph-text placement (0 of 41 missed) and all 6 PGP placements.
  - End to end, the filter let the document in (the old code kept it out), and the rebuild indexed it.
  - The check passed the document's copy under `.gov-runtime/codeintel/files/`, recorded it clean, and reused that result on the next run.
  - store.db holds the block only spread over about six neighbouring 1,200-character chunk values. The check caught it there in the test project's own layout (10 of 10 runs), but in 0 of 15 runs once 6 to 81 other values stood before those chunks, as in a store with many documents.
  - code.db holds no document text.
- **Background:** the research note's §14 names this residual and an 8,192-byte overlap. The implementation kept `_OVERLAP = 4,096` (`src/gov/secrets/__init__.py:55`). No acceptance case has a block longer than the overlap: K1's block is about 260 bytes.
- **What should have happened:** a real token is found across every boundary where the check splits its input (KPI 1), at least as the old code found it.
- Ordinary work: yes, because a key pasted into a governance document is the honest mistake these two gates exist for. Keys over 4 KB are real: an RSA-8192 PEM key is about 6.4 KB, and an armoured PGP secret key of RSA-3072 or 4096 with a subkey is about 5 to 7 KB (general sizes; not measured here). Documents over 16 KB are common, and no construction is needed.
- Consequence: fails open.

**F2 — Medium. A SQLite store that cannot be read at check time is judged by its raw bytes alone. That judgement misses tokens the values hold, and its clean result is recorded and reused once the store is readable again.**
- **Why it is readable or not:** the read uses a busy timeout of 0 (`src/gov/secrets/__init__.py:291`), so any momentary writer's lock sends the store to the raw-bytes fallback (lines 303–305).
- **What was done:** I built two stores whose tokens are held by values but are not whole in the raw bytes:
  - a github-pat shape that straddles the split between a page and its overflow page;
  - a 30-character project-rule token stored as a value on its own, with its serial-type byte (a letter, so a word byte) directly before it.

  Another process held both stores with BEGIN EXCLUSIVE during run 1 and released them for run 2. I removed the clean-result record before run 3.
- **What happened:**
  - Run 1: exit 0, nothing named. The old code raised "database is locked" (exit 1, fails closed).
  - Run 2: exit 0, both stores labelled "clean result reused".
  - Run 3: exit 1, both stores named.
  - A damaged store, and a layout the freed-space reader rejects (F5), take the same path.
- **What should have happened:** a raw-bytes judgement made because the values could not be read leaves no clean result for a later run to reuse in place of reading the values (DEC-853: "a changed store is always scanned in full"). A momentary lock is waited out; the old code waited 5 s.
- Ordinary work: no, because only a rebuild writes store.db and code.db (searches write only the query-vector cache, which holds no text), and the lead runs rebuild and check one after the other. A miss also needs a secret that already passed the filter, placed where the raw bytes split or prefix it. None of the four real stores was locked when I probed. The code-graph daemon's locks could not be observed.
- Consequence: fails open.

**F3 — Medium, the ticket's own purpose. The lexical index's FTS5 data can hold a word-internal piece of an identifier at a true boundary, in a live value, so the check turns red. Which identifiers are affected changes with the index's vocabulary.**
- **What was done:** I built an FTS5 table with the lexical index's own tokenizer (porter, unicode61, underscore kept inside words) and compacted it as the rebuild does. It held an identifier of 19 word characters followed by a gov-token-lower shape. The identifier as a whole is no finding; its inner part alone is one. I then repeated this with a second document holding a word that sorts just before the identifier and shares its whole head. Finally I counted the real index's terms on a copy of store.db.
- **What happened:**
  - The identifier alone: clean.
  - With the neighbouring word: red. Two values hold the inner part without the identifier: the data blob and its zero-free copy.
  - Why: FTS5 stores each term after the first on a leaf page as the suffix after the prefix it shares with the previous term, behind a one-byte length. The stored text therefore begins inside the word.
  - In the real index: 32,138 terms, 51 of them with a project-rule key prefix inside them followed by 16 or more word characters. For 3 of those, the previous term shares exactly the head before that prefix; 8 more are within 3 bytes of it. None has a digit in its body today, which is the only reason the check is green.
  - K2's full-text form uses the default tokenizer, which splits words at underscores, so its tests never build such a term.
- **What should have happened:** an embedded fragment of a longer identifier is never flagged (KPI 2, W2-M404).
- Ordinary work: yes, because terms with this layout are already in the index, names with digits are common in this repository, and which words neighbour each other changes with ordinary commits.
- Consequence: other (fails closed: `gov check` and a close turn red by chance).

**F4 — Low, pre-existing. Gitleaks skips a whole input as binary when its first read carries a file signature at a fixed offset, and the check then judges the input clean.**
- **What was done:** I scanned a text holding a github-pat shape, with "DICM" at input offset 128 or "ustar" at offset 257, and a control without either.
- **What happened:** with a signature, the token is not found under either rule set (exit 0); the control is found. The check's leading newline only protects against signatures at offset 0. None of the four real stores' inputs carries a signature at these offsets, because they begin with fixed schema text.
- **What should have happened:** no input is skipped as binary.
- Ordinary work: no, because it needs a short string at an exact byte offset near the start of a file.
- Consequence: fails open.

**F5 — Low, feature-gated. Two store layouts that no store uses today are read wrongly.**
- **What was done:** I built a WAL store (secure_delete on, automatic checkpoints off) with a token in a row deleted after the switch to WAL, and six synthetic auto_vacuum stores after random writes.
- **What happened:**
  - WAL: the token stays in the main file's pages, which the freed-space reader takes for live cells, and it is not in the log. The new check exits 0; the old code names the store. By reading the code: in WAL mode the reuse key is the main file's digest, while the values come through the log.
  - auto_vacuum: in 2 of 6 stores, a pointer-map page was taken for a b-tree page and the parse refused ("a b-tree page's cells overlap"), so those stores fall back to F2's raw-bytes judgement.
- **What should have happened:** no deleted text in any file under `.gov-runtime/` passes the check.
- Ordinary work: no, because all four stores use the rollback journal with auto_vacuum off. This is an entry criterion for any ticket that switches a store to WAL or auto_vacuum (DEC-803).
- Consequence: fails open (WAL); other (auto_vacuum).

**F6 — Low. `gov rebuild` given a relative root fails in the new compaction step, after the record store, the lexical index and the code index have been built.**
- **What was done:** I ran the rebuild in a temporary project with the root given as `.` and as an absolute path. A stand-in replaced the code-graph tool and wrote a SQLite file in the tool's home, because the real tool cannot start in this sandbox.
- **What happened:** with the absolute path, the rebuild returned and both stores were compacted. With `.`, it raised ValueError (the resolved home "is not in the subpath of '.'"), gave no result, and left the code-graph store uncompacted; through the CLI that is a traceback and exit 1. The CLI passes the root unresolved (`src/gov/cli/main.py:208`), and the step names the home's files relative to it (`src/gov/rebuild/command.py:161`). `gov adopt` resolves its root and is not affected.
- **What should have happened:** a rebuild given any path to the project compacts its stores and returns its result.
- Ordinary work: yes, because `--root` is the CLI's shared option and a relative path is an ordinary way to give it.
- Consequence: other (the rebuild fails after building; nothing is lost).

**F7 — Low. On an uncompacted store, the freed-space backstop reads a freed overflow page as one text that begins inside a word, so the chance red survives in freed space.**
- **What was done:** I built a store with secure_delete off and a long value whose overflow page begins with the gov-token-lower part of an identifier. I deleted the row without compacting, then ran VACUUM.
- **What happened:** with the row live: clean. Deleted and not compacted: red. After VACUUM: clean. On the real compacted stores, the freed regions hold no run of word bytes longer than one byte (store.db: 141 freed texts; code.db: 34).
- **What should have happened:** KPI 2 holds in freed space too.
- Ordinary work: no, because every rebuild now compacts its stores; this needs a failed compaction (F9) or stores built before this change.
- Consequence: other.

**F8 — Low. Values given to gitleaks one after another still interact, so W2-M395 is settled for record bytes but not for values that neighbour each other in the input.**
- **Two mechanisms:** the blank line between values does not stop rules whose patterns cross whitespace, and keyword gating works per gitleaks fragment, which holds several values.
- **What was done:** I scanned pairs of values, neither of which is a finding alone:
  - one ending in a keyword and an assignment, beside one starting with a high-entropy word;
  - a key block's header in one value, its body and end in the next;
  - a value naming a keyword of the default rule whose last alternative is any 40-character hex word, beside a value holding a commit id; and the same pair 130 KB apart.
- **What happened:** every neighbouring pair was a finding (generic-api-key, private-key and that keyword-gated rule); the far pair was not. In today's stores, none of the 1,349,515 neighbouring value pairs forms an assignment junction, and no value opens a key header without closing it. The two values naming that keyword sit 0.87 MB and 1.0 MB of input away from the nearest 40-hex word.
- **What should have happened:** bytes of different values never join into one finding (W2-M395's fix text; the research note's §13).
- Ordinary work: no, because no such junction exists in today's stores, and values do not move with a rebuild unless their content changes.
- Consequence: other.

**F9 — Low. The compaction step reaches beyond "each store's build" and fails silently.**
- **What was done:** a reader held a read transaction on `query-vector-cache.db` during a rebuild in a temporary project.
- **What happened:** the rebuild returned after 32.3 s, with store.db "compacted" and the cache "not compacted: database is locked". It also exits 0 in that case.
  - The step vacuums the query-vector cache, which searches write and the rebuild does not build.
  - A store it cannot compact costs a 30-second wait and appears only in the result's `compaction` entry.
  - It runs once after store.db's three builds, not after each one.
- **What should have happened:** the step stays inside the allowed change, and a store left uncompacted is reported where a close or the lead will see it.
- Ordinary work: yes, because a search running during a rebuild holds the cache.
- Consequence: other (a 30 s wait; the cache holds no text).

### Probed and found sound
- **Scope:** the change stays inside the ticket's allowed paths. Only the test designer's commit (ab381f94) touches the acceptance tests. The edits to the moved unit tests follow the new internals and lower no expectation.
- **Read edges:** no read begins inside a word at the check's own splits (K2: 132 passed; K1 read edges: 20 passed).
- **Real stores read value by value, with no fallback:**
  - store.db: 507,340 texts (372 MB) in 3.0 s, plus 1.4 s to parse freed space;
  - code.db, with 65,536-byte pages: 842,177 texts in 1.9 s.
- **Freed-space coverage:** I ran six synthetic rollback stores with pages of 4,096 and 65,536 bytes, secure_delete off, and random inserts, updates, deletes and drops, including a WITHOUT ROWID table and an FTS5 table. Every marker word lying whole in a store's bytes (133,132 to 172,915 per store) was in a value or freed region the check reads. The two apparent exceptions were raw-byte joins across a freeblock's end into the next live cell, not text the store holds.
- **The ticket's purpose on the real store:** the old code is red on the lead's store.db through a byte join. The generic-api-key match covers 59 bytes: the end of a lexical_chunk path, two one-byte integers and the start of the next text value, running into the next page. The new check is green on the same store.
- **Rule sets and failures:** both rule sets are applied. A finding is never recorded. Gitleaks failures raise (K5).
- **Reuse (DEC-853):** under form 2, all 4 unchanged stores were reused with labels.
- **Cost:** 30.0 s for a full scan against 54.2 s for the old code, 5.6 s when everything is reused, peak memory 1.4 GB against 5.3 GB. The declared limit is 900 s.
- **Compaction safety:**
  - VACUUM renumbers the hidden row ids of tables without an INTEGER PRIMARY KEY (seen on SQLite 3.45.1), but gov joins only on INTEGER PRIMARY KEY columns or its own keys, and the cache's eviction relies only on row-id order, which VACUUM keeps.
  - A sqlite-vec table returns the same ten nearest neighbours and the same vectors after deletes and VACUUM.
  - By reading the code: the rebuild's digest is taken over rows, before compaction.
- **Path-name judgement:** unchanged, since a path is a single piece (with a token: found; plain: clean).
- **UTF-16 and blob forms:** K1 forms, 31 passed.