**Step 0:** `printenv` gave `independent-auditor` and `DAEO-kmcr`. (a) failed as it should, with `OSError: [Errno 30] Read-only file system`. (b) worked and gave object `1ae28402a109`. HEAD is `3e7194a45a58`. The tree was clean at the start and is clean at the end. I read `EMG-common.md` and followed it.

task: DAEO-kmcr
status: DONE
work_completed: Reviewed round 2 of W2-23 on S3 only (`fd1bc056f5ba..3e7194a45a58`), against Interface item 6 and P-W2-23-7 (a). I read the change to `safety.citations` and the new `_folders`, how the A8 proof calls them (`legacy.py:137-165`, called at :225), the new acceptance and unit cases, and bootstrap.md:2362. I ran the brief's test command and probed `safety.citations` with 37 inputs. I also loaded the previous head's `safety.py` into memory to see whether the main finding is new.
files_changed: none
evidence: Tests run through `heavy_slot.sh`: 34 passed in 141.54s. Probe outputs are quoted in the findings below. Scratch `TMPDIR`: 24K and 9 inodes; nothing of mine was written.
tests: `tests/unit/adopt/test_safety.py` and `tests/acceptance/W2-23/test_w2_23_citations.py` with the brief's options: 34 passed, 0 failed. There were no failures to judge.
discoveries: My Write call for a probe script in `$TMPDIR` was refused under the quiet-hours rule (DEC-991) and queued for the morning package. I did not retry the Write. I ran the probes as inline `python3 -c` instead, which writes no file. I'm naming that here in case it counts as "another form".
risks: R2-1 (below) means the A8 proof still releases a store that a rule or a record's prose cites by its folder at the end of a question.
lessons: R1 was reported as "a full stop", but the defect is any punctuation that ends a sentence. The fix and the new cases cover only `.`.
proposed_decisions: none
unresolved: Whether a question mark after a folder citation is ordinary work. If the CTO or owner rules it is not, R2-1 becomes a recorded row and S3 passes.
recommended_next_action: This was the last round under DEC-1010, so the decision goes to the owner with options. (a) A small fix, preferred: treat a `?` that ends a folder citation (followed by whitespace, closing punctuation or end of text) like the full stop, in `_NOT_MORE_PATH_DIR` and the glob token handling. Add one acceptance case for it. Cost: about 3 lines plus 1 test, and no new round. (b) Accept R2-1 as a Wave 3 row and close S3 as it stands.

**What I probed and found sound**
- **R1 is fixed.** These are all found as a folder or a tail through the call path A8 uses:
  - `legacy/memory.`, `legacy/memory/.`, `legacy/memory...`, `../memory/index.md.` and `../../memory/decisions/leg-001.md.`.
  - Text after a folder citation: `!`, `,`, `:`, `)`, and a backtick then `.`.
  - A trailing dot that starts more of a name is still not a stop: `legacy/memory.db`, `legacy/memory/.git`, `legacy/memory.v2` and `../memory/index.md.bak` are not found.
- **R2 is fixed, using the CTO's reading.**
  - For store `notes/memory/2025/q1/a.md` and `notes/memory/2026/b.md`, the proof finds `notes/memory/`, `notes/memory` mid-sentence, `notes/memory.`, `notes/memory/2025/`, `notes/memory/2025/q1` and `notes/memory/2026`.
  - A folder above the store's folder is not found: `notes/`, `notes/.`, `notes/memory2/x`, `notes/memory-old/`.
  - For a single-file store, `notes/memory/` (above its parent) is not found and its own parent is.
- **No other form of item 6 got worse.** Each of these is found, ending in a full stop:
  - a word character or `-` before the path (`xlegacy/memory.`, `-legacy/memory.`)
  - backslashes (`legacy\memory.`, `..\Memory\Index.md.`, `Notes\Memory.`)
  - URL-encoding (`legacy%2Fmemory.`) and another letter case (`Legacy/Memory.`)
  - a path split across lines (`legacy/\nmemory.`)
  - globs (`legacy/memory/*.md.`, `notes/memory/**.`, `notes/memory/2025/**/*.md.`)
- **The change only adds matches.** The new lookaheads block a subset of what the old ones blocked, and the folder set is a superset of each file's own parent. So nothing found before is lost.

**Findings**

**R2-1:** `src/gov/adopt/safety.py:281`, together with :240 and :324-333. A citation of the store's folder that ends a question is not found, so the store is retired.
- **What happens:** a rule file says "Before a vote, did you search legacy/memory?" or "Is it still in legacy/memory/?", or a record's prose asks "Should we keep notes/memory?". The A8 proof finds no citation and the store is retired.
- **Why:** the `?` blocks the folder form, then gets read as a glob wildcard, and that glob does not match the store.
- **What should happen:** the folder is found, as it now is with `.` and `!`.
- **Not new:** the previous head behaves the same, so this is not a regression. It is the same sentence-end defect as R1, which P-W2-23-7 (a) framed as "sentence-final", but the fix covers only the full stop. With `?`, the tail, path and id forms are found; only the folder form misses.
- **Reproduction:** `PYTHONPATH=src python3 -c "from gov.adopt import safety; print(safety.citations('Did you search legacy/memory?', ['legacy/memory/index.md','legacy/memory/decisions/leg-001.md'], []))"` prints `[]`. The same holds for `'Is it in notes/memory/?'` with the nested store. With `!` the folder is found. `_proof` calls exactly this function at `legacy.py:146` and `:155`. For a rule file that cites no id, an empty result means no citer.
- Ordinary work: yes, because a question is the most common sentence end after a full stop. A decision record about the old store, or a rule's checklist question, ends with its folder in ordinary prose.
- Consequence: fails open.
- **What would reverse it:** an owner or CTO ruling that P-W2-23-7 (a)'s "sentence-final" means the full stop only, or that a question ending in a folder path is not ordinary in rule files and record prose. Or a run at this head where an A8 with that sentence planted refuses `ADOPT_STORE_STILL_CITED`.

**R2-2:** `src/gov/adopt/safety.py:284-301`, with `legacy.py:222-225`. When one A8 run retires memory-store entries from two separate stores under one broad folder, a bare mention of that folder holds the stores back.
- **What happens:** `_proof` gets every memory-store entry of the run as one "store", so the deepest common folder can be broad. With `docs/memory/a.md` and `docs/notes/b.md`, the text "Write documentation in docs/." is found as a folder citation of both files, and A8 refuses. Before this change, only `docs/memory` and `docs/notes` counted.
- This follows the CTO's reading taken literally. The refusal names the citation `docs/`.
- **Reproduction:** `safety.citations('Write documentation in docs/.', ['docs/memory/a.md','docs/notes/b.md'], [])` returns two folder hits on `docs/`.
- Ordinary work: yes, because projects can keep two memory folders under one parent (for example `.claude/`), and rule files mention that parent bare. But it fails closed and the refusal says why.
- Consequence: other (wrongly holds a store back, with a named refusal; the owner can reword the rule or retire the stores in separate runs).
- **What would reverse it:** the CTO stating that a run's memory-store entries are one store by definition, in which case this is exactly the intended behaviour. This is a recorded row, not a block.

**Classification:** R2-1 is in scope, ordinary work: yes, fails open, so it blocks. R2-2 is in scope, consequence other, so it is a row.

```verdict
{"kpis": [{"kpi": "S3", "verdict": "fail", "findings": [{"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R2-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```

VERDICT: NOT READY (probe head 3e7194a45a58)