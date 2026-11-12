task: DAEO-kmcr (W2-23), independent auditor, FULL review, one round (DEC-1010)
status: DONE
work_completed: **Step 0 passed.** (a) Writing the sandbox trial file was refused: `OSError: [Errno 30] Read-only file system`. (b) `git hash-object -w --stdin` worked and `git update-index --refresh` returned 0. `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-kmcr`. HEAD is `fd1bc056f5ba` and the tree was clean at the start and at the end. I read EMG-d4b-launched.md, EMG-common.md, JUDGEMENT.md, AUDITOR-common.md, the ticket (its seven Interface items and both Delegated paragraphs) and the whole 25-file delta. I ran the scoped test command. I ran probes only under the sandbox TMPDIR: `safety.citations` on about 40 citation texts, `merge_text` and `merge_settings` on odd inputs, and `merge.generate` on a programme with CRLF line endings and 4-space JSON.
files_changed: none
evidence: The `stages.py` hunks are the import line plus `a0`, `a3`, `_batch` and `a6` only, with no hunk in `run()` or `STAGE` (DEC-954 and P-W2-23-1 (a) are kept). The only change in `merge.py` that touches compaction is `AUTO_COMPACT = {}`, so the tool forces no threshold (DEC-838 is kept). `TMPDIR` holds 107M and 9,923 inodes (the session's own files plus the folders pytest kept for failed tests); my probe folder is removed. `ps` shows no ollama or llama-server process.
tests: 240 passed, 19 failed, 200 deselected (376 s). All 19 failures are `ADOPT_CODE_GRAPH_UNREADABLE`: the code graph cannot run in the sandbox. That accounts for 19 error codes in 19 failures, so none of them points at the code. The failures are three W2-23 cases (S1 move batch, S5 with a move, S7 at A6), three W1-41 migration cases, five path_map cases, one unknown-artefact case and seven verdict cases. The exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"` left out 200 cases, including S6's retrieve/context case. The lead's figures from outside the sandbox (22/22 W2-23, 3 W1-41 migration cases passed) cover the cases that failed here.
discoveries: The A8 citation finder misses three ordinary or near-ordinary forms of the listed citations (R1–R3). The acceptance tests' planted texts happen to avoid these forms: the relative tail is followed by a comma, and the store has a file directly inside `legacy/memory/`.
risks: With R1 or R2 present, A8 can retire a memory store that an active record or rule still cites. The store stays reachable at the archive ref, so the dependency-proof gate passes wrongly but the data is recoverable.
lessons: Citation tests should plant each form at the end of a sentence and in a store that has subfolders, not only in the middle of a line.
proposed_decisions: none (R1 and R2 are fixes inside the allowed paths and fit Interface item 6 as written)
unresolved: Which folder counts as "the store's folder" when the store's files sit in subfolders. I read it as the folder that holds them all (R2). If the CTO reads it as each file's own parent folder, R2 drops to a row.
recommended_next_action: The engineer fixes R1 and R2 in `safety.citations`, and the test designer adds a sentence-final case and a nested-store case to S3. Everything else lands as rows. The fixes ride on the ticket's resume (DEC-802), and a re-check of S3 alone is enough.

Classification: 2 findings are in scope, ordinary work yes and fail open (R1, R2, both S3); 7 are rows (R3–R9).

**R1** — `src/gov/adopt/safety.py:287` and `:291`. A folder citation or a `../` relative tail followed by a full stop is not found.
- What happens: the folder pattern's lookahead `(?![\w./*?\[-])` and the tail pattern's `(?![\w.-])` both reject a following `.`, so a citation at the end of a sentence is missed. With store `legacy/memory/decisions/leg-001.md`:
  - `"The old store is legacy/memory."` gives `[]`.
  - `"…legacy/memory/."` gives `[]`.
  - `"See ../decisions/leg-001.md."` finds the tail form not at all; only the id fallback catches it, and only because this file's name equals its id.
  - The same texts with a comma or a space after them are found.
- What should happen: A8 names that record or rule as a citer.
- Reproduction: `PYTHONPATH=src python3 -c "from gov.adopt.safety import citations; print(citations('The old store is legacy/memory.', ['legacy/memory/decisions/leg-001.md'], []))"`
- Ordinary work: yes, because prose in records and rules routinely ends a sentence with a path or folder.
- Consequence: fails open (the A8 dependency proof passes and the store is retired while it is still cited).
- What would reverse it: a reading of Interface item 6 that excludes citations followed by punctuation, or a test showing that `_proof` catches these citations by another route.

**R2** — `src/gov/adopt/safety.py:289`. A citation of the store's folder is found only when it is a file's immediate parent folder.
- What happens: `folder = parts[:-1]` is computed per file. For a store whose files all lie in subfolders (`.claude/memory/2025/a.md`, `.claude/memory/2026/b.md`), `"The store moved from .claude/memory/ to here"` gives `[]`. I confirmed the same with `legacy/memory/` against `legacy/memory/decisions/leg-001.md`. The acceptance test passes only because its store also has `legacy/memory/index.md`.
- What should happen: a citation of the folder that holds the store is found.
- Ordinary work: yes, because memory stores laid out in dated or topic subfolders are common, and they are cited by their root folder.
- Consequence: fails open.
- What would reverse it: the CTO ruling that "the store's folder" means each file's own parent folder (see unresolved).

**R3** — `src/gov/adopt/safety.py:302`. A glob that starts with a wildcard is skipped.
- What happens: `**/leg-001.md` and `**/memory/*.db` give `[]`. The skip is deliberate: imported rules carry `globs: ["**/*"]` (`legacy.py:38`), which would otherwise cite every store. Brace globs such as `memory/store.{db,json}` are also missed.
- Ordinary work: no, because rules rarely name a store only through a leading-wildcard glob; this is a trade-off made against false citers.
- Consequence: fails open.
- What would reverse it: such globs turning up in real programmes' rule files.

**R4** — `src/gov/adapters/merge.py:97` and `:117`. The merged files change format.
- What happens: `_read` uses universal newlines, so a CRLF `CLAUDE.md` is written back with LF line endings. `json.dumps(indent=2)` reformats a 4-space or one-line `settings.json`. Every line's text, every key, every value and their order are kept.
- Reproduction: a CRLF `CLAUDE.md` `b'own one\r\nown two\r\n'` becomes `b'own one\nown two\n\n<!-- gov:generated begin -->…'`.
- Ordinary work: yes, because Windows-edited files and non-default JSON indentation are common.
- Consequence: other (no text is lost; the S2 tests compare lines, not bytes).
- What would reverse it: S2 being read as requiring the programme's bytes, not its lines.

**R5** — `src/gov/adapters/merge.py:127-129`. On a second generation, any generated file other than the three merged ones that now differs from the project's copy is left as it is and listed in `kept`, never updated.
- Consequence: generated skills and agents go stale after the first run.
- Ordinary work: yes, because `.rulesync/` sources change between runs.
- Consequence: other (outside S2's three files; nothing is lost).

**R6** — `src/gov/adopt/stages.py:295`. The A4 plan still records `rollback_point: refs/gov/adoption/rollback/batch-<n>`, while A6 uses the per-run ref.
- Consequence: the plan names a ref that is never written.
- Ordinary work: yes, because every run's A4 record says it.
- Consequence: other (the A6 record holds the true refs; W1-41 was revised to read them).

**R7** — `src/gov/adopt/legacy.py:98` and `:251`, with restore at `:262`. A8's import checks its targets only against tracked paths.
- What happens: an ignored file standing at an import target (for example an ignored `.rulesync/mcp.json`) is overwritten, and the restore deletes it if the stage fails.
- Ordinary work: no, because it needs an ignored file at exactly a generated import path.
- Consequence: loses work.

**R8** — `src/gov/adopt/stages.py:406`. `_batch`'s restore deletes every planned target that is untracked, including targets of moves not yet made.
- What happens: a file that appears at a planned target after A6's pre-check (a concurrent writer) makes `git mv` refuse, and the restore then deletes that file.
- Ordinary work: no, because it needs a concurrent write to a planned target in the middle of a run.
- Consequence: loses work.

**R9** — `src/gov/adopt/safety.py:213-217`. A kill inside one `git mv` (file renamed, index not yet updated) is refused as `ADOPT_TREE_NOT_CLEAN` rather than resumed.
- Consequence: the user must put it back by hand; the file sits at its target.
- Ordinary work: no, because the window is a single syscall wide.
- Consequence: other (refused, not half-staged silently, nothing lost).

**Probed and found sound:**
- **S1/F1:** `restore` resets, then deletes only the paths its caller wrote and that the reset commit does not track. Untracked directories and nested clones are never iterated, so they cannot raise. `commit` refuses `ADOPT_WOULD_OVERWRITE` rather than write over an untracked or ignored file. A6 refuses any target that already exists (`lexists`).
- **S4:**
  - Run state lives in the git dir.
  - A run killed after a batch's commit is recognised by HEAD^ plus the commit subject.
  - A run killed after the failed record's commit is recognised by its run id.
  - `recover` unstages only when the staged blobs equal the batch's own moves, nothing is unstaged and the only untracked paths are planned ones. Anything else is refused by name and never reset.
  - The failed record carries `status: failed`, `failed_batch` and per-run refs, and the refusal code stays `ADOPT_BATCH_FAILED`.
- **S2:** programme lines come first and in order; the marked block is replaced in place; a lone marker is refused before anything is written; invalid JSON is refused before anything is written; settings merge key by key with the programme first; a second run produces identical files.
- **S5:** `.gitleaks.toml` and the `.gov-runtime/` ignore line are added in A0's record commit; an existing `.gitleaks.toml` is untouched; both files are held through `SET_UP`.
- **S6:** every subprocess call in the delta passes a list, never a shell string.
- **S7:** `ADOPT_TARGET_UNHELD` is raised at A3 before the record is written and at A6 before any batch.
- **S3:** every form planted by the test designer is found; the base64 form is not.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "R7", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}, {"id": "R8", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "R4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "fail", "findings": [{"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "R6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R9", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```

VERDICT: NOT READY (probe head fd1bc056f5ba)