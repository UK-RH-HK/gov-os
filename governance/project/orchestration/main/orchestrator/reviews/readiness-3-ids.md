# Readiness review before the fresh 80, aspect 3: the register ids (W2-131, W2-133)

Reviewer: independent, read-only (DEC-1097 (3); FRESH-80-READINESS §5 item 3). Date: 2026-11-08. Branch `w2/integrate`
at `e66f2a6965ee`. I opened nothing under `~/gov-os-eval/` and no hidden or spent set.

## What I checked, and how

- **The code** (`src/gov/`, at the integrate head, byte for byte the same as the pin `pin-bcea09060ebc` for
  `decisions/register.py`, `retrieval/authority.py`, `store/loader.py`, `retrieval/lexical.py`, `supplementary.py` and
  `pool.py`; the pin's `retrieve.py` differs only by W2-138's store and commit lines, so the label lines are the same):
  - `retrieve.item()` labels a register item with the entry holding its first line (`entry_of(rel, first)`), or the
    chunk id in the preface or a gap. `entry` and `id` come from the same call, so they always agree (W2-92 S9).
  - `_graph()`'s `record_of` leaves out every record with a span (W2-131 S2), so no register entry stands for the path.
  - `register.leave_out()` → `narrowed()` relabels from the narrowed chunk's own first line and never keeps the
    parent's id, entry, status, `also` or `cut` (W2-133 S1).
  - Expanded parents' pieces (with `left_out`) are labelled one by one, each from its own first line.
- **The integration store**, read-only (`~/gov-os-worktrees/W2-00-store` → `-b`, `store.db` opened with
  `?mode=ro`; fingerprint head `e66f2a6965ee`; the tree is clean):
  - The method: I rebuilt `entry_of` from the store's own records and the folder's register with the code's own
    `authority.register_entries_of`. I labelled every register chunk and parent, then compared each label with an
    independent count: the nearest `### DEC-` heading above the chunk's first line.
  - **2,654 chunks: 2,334 carry their own entry's id, 320 carry their chunk id, 0 carry another id.** The 320 start in
    the preface or in a section heading or section prose (`## 3. Tool decisions`, the Solo Core tables and so on).
    None of them starts on a blank line, and none holds an entry heading.
  - **1,401 parents** (all `section`): 1,093 carry their own entry's id and 308 their chunk id. No parent spans more
    than one entry, so an expansion never runs into a second entry.
  - **No DEC-999 off DEC-999.** No chunk is labelled DEC-999 unless DEC-999's heading is the nearest one above it.
  - **The newest entries, DEC-1085 to DEC-1097:** all 13 are in the store, each found at its own heading line with
    the right span (for example DEC-1097 at 13847 to 13934). DEC-1098 is not in the store or the file.
  - **Other id-bearing records:** every path except the register holds exactly one record, and no id stands on two
    paths. Tickets (207, matching the 207 files in `.tickets/`), CAP- (276), MR- (6), ADR-, CHARTER and CONTRACT are
    each labelled by their file's own id. This rules out the DEC-999 class of mislabel for them.
- **E0's clone store** (`~/gov-os-runs/D4B/w4-e0/repo`, HEAD and store fingerprint `c00d525fd420`, clean tree). This
  is the store the 80 is measured on (FRESH-80-1 items 10 to 13), and I ran the same check on it:
  - 2,626 chunks: 2,306 carry their own entry's id, 320 their chunk id, **0 another id**;
  - DEC-1076 to DEC-1088 are all located at their own headings.
- **Four live searches** (the pinned `gov retrieve --root ~/gov-os-worktrees/W2-00-store`, one at a time):
  1. the DEC-999 mislabel fix;
  2. version 0.476;
  3. "next free id DEC-1093";
  4. the MR on independent test design.
  - **All 54 register items carried their own entry** (`id` = `entry` = the heading above), including DEC-999's real
    chunk, DEC-1089 and DEC-1097. Non-register items carried CAP-51, MR-3, DAEO-r8vq, CHARTER-v5, CONTRACT-v4, or a
    chunk id for files that are not records.
  - Both bundles of searches 1 and 2 answered the question. I made no second search and met no refusals.
- **Tests:**
  - `tests/acceptance/W2-131`, `tests/acceptance/W2-133`, and the W2-131 and W2-133 unit tests (against `src/`): 102
    passed, 2 failed (F3).

## Findings

### F1: the trailing version table sits inside the newest entry, so its rows carry that entry's id
- **What I found:** the register's newest version table has no heading of its own. Its 32 rows (0.450 to 0.481) name
  DEC-1066 to DEC-1097, and the parser (`loader.register_entries`: an entry runs from its heading to the next
  heading) counts them as part of DEC-1097's span (13847 to 13934). In E0's clone the same table sits inside DEC-1088.
- **What a search returns:** search 3 sent all of DEC-1097's lines, the 32 rows included, as one item labelled DEC-1097
  with DEC-1097's status marks. A row recording DEC-1092 is cited under DEC-1097's id.
- **Older version rows are fine:** they sit under the entry they record (for example 0.430 under DEC-1047), so their
  label is right; 318 chunks are mostly version rows. This is the register's layout, and it conforms to W2-131 S1's
  wording (the entry that holds the first line).
- **Why it does not change the verdict:** the row's own text names its decision, and the measure scores by path and
  lines, not by id.
- Ordinary work: yes, because a question about when a recent decision was recorded can return those rows.
- Consequence: other (the label shows the wrong id on version rows; nothing fails open and no work is lost).
- **Where it lands:** a row. It is in scope and reachable, but it does not fail open or make the verdict wrong. A
  possible fix is a heading before each version table, or labelling a table row by the first id the row names.

### F2: the label reads the register from the folder, while the chunk lines come from the store's commit
- **The mechanism:** `register_entries_of` reads `Path(root)/register` as the folder holds it now, but the chunks'
  line numbers come from the store's commit. When the two differ, the labels drift.
- **The simulation** (in scratch, on a copy of the register): the store was left as it is and the copy was edited.
  - With one line added inside DEC-942, 161 chunks after the edit fall back to their chunk id, and none takes a wrong id.
  - **With three lines added, 201 chunks take their neighbour's id** (for example 11629 is labelled DEC-943 instead
    of DEC-944) and 70 fall back to their chunk id.
- **Not reachable in the 80:** the 80 runs on E0's clone with a clean tree, no rebuild and commits held (FRESH-80-1
  items 12 and 13). The integration store is double-buffered and switches its link by an atomic rename.
- **Same class as rows already recorded:** W2-138's review rows F1 (a store built from a dirty tree) and two refreshes
  within one search (the pin lacks W2-138's resolve-once).
- Ordinary work: yes, because the orchestrator can search its own tree while a register edit is not yet committed or
  rebuilt.
- Consequence: other (wrong ids in that window; the item's text and hash also come from the folder, which W2-138's
  line-hash check is there to catch).
- **Where it lands:** a row, to go with W2-138's F1 row. A possible fix is to read the register at the store's
  commit, or to drop the label when the folder's file differs from the commit.

### F3: two of W2-131's acceptance tests have been red on `w2/integrate` since W2-138
- **What fails:** `test_w2_131_unchanged.py`, both S3 tests (`…bundle_is_todays…[a-ticket-batched]` and
  `…continued_pages…`).
- **The cause:** only `continuation` differs, because of W2-138's `s` key (the store's commit). The ids and the
  evidence are unchanged.
- **Why only W2-131's:** W2-138 revised W2-133's acceptance rows and the six unit guards (`9a93f933`, `0a20fdc1`),
  but not W2-131's acceptance tests (`2d97295b`, untouched since). W2-138's merge note reports a scoped regression of
  850 passed, 0 failed, which did not include these two.
- Ordinary work: yes, because `gov accept W2-131` or the regression shows them red.
- Consequence: other (a stale guard; the label behaviour is correct; the 80's code, pin `bcea09060ebc`, predates
  W2-138).
- **Where it lands:** a row. It rides with W2-131's formal close: a test designer adds the `s`-key rewrite with
  `Rewrite-Reason: DEC-1090 (3)`, as W2-133's acceptance rows got.

### Not findings
- **The 320 chunks with chunk ids** follow W2-133 S2 (a first line in the preface or a gap carries its chunk id).
  W2-131 S1's older words, "a parent expansion carries the id of its first entry", are superseded there by W2-133 S2,
  and no parent spans entries in either store, so the difference never shows.
- **ADR-0000** (`template/governance/kernel/templates/decision-record.md`) is a template that declares its own id.
- **The pin prints `store: None`.** It predates W2-138; that is aspect 1's or the lift's.

## Verdict

**READY for the 80 on this aspect.** Every register chunk in both stores carries its own entry's id or its chunk id,
never another id. There are no FIX-BEFORE-THE-80 findings, and 3 rows (F1, F2, F3).

Evidence:
- scratch at the end: 9.0M, 1,059 inodes (scripts and four bundles only; the temp tree is removed);
- searches: 4 of 10, no refusals;
- no commits, rebuilds, GPU work or installs.

```verdict
{"kpis": [
 {"kpi": "A3-1 every register chunk carries its own entry's id (mid-entry, gaps, expansions, narrowed)", "verdict": "pass",
  "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "A3-2 version-table rows and the newest entries DEC-1089 to DEC-1097", "verdict": "pass",
  "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "A3-3 other id-bearing records (tickets, CAP-, MR-) carry their own id", "verdict": "pass", "findings": []},
 {"kpi": "A3-4 W2-131 and W2-133 guards hold on w2/integrate", "verdict": "pass",
  "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
