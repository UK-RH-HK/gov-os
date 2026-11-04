# Review: W2-32, DEC-1067 order (5), index-time method 1 (contextual headers when embedded), ticket DAEO-0pyc

Reviewer: a fresh independent session, 2026-11-04. Read-only on what is reviewed; this file is the only write.

**Reviewed:** branch `w2/W2-32-index` (worktree `~/gov-os-worktrees/W2-32-index`), its own commits `d6770e5a9a88` (the
method) and `335233db685d` (`CONFIG_INVALID` from the loader), diff `65d28f3bbec4..335233db685d`; the designer's
cases `fdc7b7ac180a` (`tests/acceptance/W2-32/test_w2_32_s7_headers.py`, 14 cases), merged at `ff347bcd1519`. The
merge onto integrate's head `0936077cfe29` (later than `16e0287ae302`): `git merge-tree --write-tree w2/integrate
w2/W2-32-index`, tree `a56391e1ec6a`, extracted into the TMPDIR for the runs.

**KPI line judged:** S7, its note "DEC-1067 order (5), index-time method 1" (each chunk embedded after a deterministic
header of its path and the headings above it; the keyword chunk, the evidence text and the reranker's input
unchanged; within `EMBED_LIMIT_CHARS`; behind `rebuild.yaml` `embed_headers: true|false`, absent false, invalid
`CONFIG_INVALID`; the recipe in the manifest, so switching re-embeds).

## Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work (DEC-1010; at most two rounds; READY computed by `verdict.py` from the block below).

## Runs (TMPDIR `/tmp/gov-os-emg-hdr-review`; pytest through `heavy_slot.sh`, `PYTHONPATH=<tree>/src`, `-m "not local_only" -k "not real and not green_here and not time_limit"`, `-p no:cacheprovider`; no `gov retrieve`, no `gov context`, no model, no rebuild, no measure)

| run | code | result |
|---|---|---|
| the designer's 14 cases + the engineer's `tests/unit/retrieval/test_w2_32_embed_headers.py`, `--optin=lifted,breadth` | `335233db685d` | **65 passed** (14 + 51); without the opt-in 33 passed, 32 deselected |
| `tests/unit/` retrieval, semantic, rebuild, retrieve + `tests/acceptance/` W2-32, W1-19, W2-108, W2-76, W1-08, `-n auto` | the merged tree `a56391e1ec6a` (a plain extract, no `.git`) | 643 passed, 26 failed, 6 skipped, 1 xfailed (R2-F1). 24 of the 26 need a git tree (W2-91's tracked paths, W1-08's committed schemas and templates): **pass** when re-run from integrate's checkout with the merged `src`. Left: W1-19's `test_only_the_namespace_that_says_embedded_reaches_the_vectors` (red in that combined run **on integrate's own `src` too**, 1 passed alone three times on each: the known shared-cache case, not this branch's) and **S7's `test_a_store_embedded_at_the_old_cut_is_stale_and_the_next_rebuild_embeds_the_chunk_whole`: red on the branch and on the merge, 1 passed on integrate `0936077cfe29`** (F1) |
| probe `plan_time.py` / `plan_fix.py`: a synthetic store of 5,000 files, 60,000 chunks | merged `src` | `_Texts._PARENTS`'s plan is `SCAN f VIRTUAL TABLE` (the whole FTS table per file); `over_limit` 124 s, a full pass of `_Texts` 120 s; with `AND c.path = ?` bound, the plan is `SEARCH c USING INDEX lexical_chunk_by_path`, the same rows, 0.06 s for 5,000 files (F2) |
| probe `real_time.py`: the main checkout's `.gov-runtime/store.db`, opened `mode=ro` (55,591 chunks, 2,632 paths) | merged `src` | as written 0.030 s a file, **about 79 s for every path**; bound, **0.07 s for every path** (F2) |
| probe `fence_count.py`: tracked Markdown | integrate's tree | 33 of 1,504 files hold 223 lines inside a fenced block that the chunker reads as headings (F4) |
| `git merge-tree` onto `0936077cfe29` | | `src/` merges without conflict, and the merged tree's change to `semantic.py`, `loader.py` and `chunking.py` against integrate is **line for line the branch's own change** (compared). Two conflicts, both in documents: `docs/changes/W2-32-evidence.md` (the S7 row: integrate's longer row against the branch's row plus its new "DEC-1067 (5) method 1" row: keep integrate's S7 row and add the new row) and `tests/acceptance/W2-32/README.md` (the case count line, the S7/S8 rows of the map, and Rounds 17-18 against round 10: a union, the count recomputed; the designer's file) |

## What the brief asked, judged

- **Off is today's embedder input, byte for byte: yes.** `_Texts.__call__` runs the same join as the removed `_TEXT`
  (`lexical_chunk` to `lexical_fts` by rowid, by `chunk_id`) and returns `("" + text)[:EMBED_CHARS]`, which is
  `text[:EMBED_CHARS]`; `over_limit` off is the unchanged `_over_limit`; the machine cache is keyed by that same text.
  Off writes a new `semantic_pin` row `embed_headers=false`; a store without the row reads as false, so today's
  stores stay fresh and nothing is re-embedded (the unit case and `_build`'s `is not` test agree).
- **The header is deterministic and leaks nothing: yes.** It is built only from the chunk's own file: its path and the
  first line of each of that file's parents' first chunks in `lexical_fts`, the lines already in the keyword index
  (whose chunks are the raw file text). Chunk ids carry the path and the file's blob, so any change to a file (a
  heading included) renews all its chunks and their headers. The header is computed only for chunks in `missing`
  (a subset of `_wanted`) and, in `over_limit`, only for kept ids (`chunk_id in keep and ...` short-circuits): a file
  kept out of the keyword index (W2-13's `kept_out`), out of the vectors (`embedding_policy`) or held out (the
  learning loop's cases) never gets a header, and no header carries another file's text.
- **Role separation (DEC-1065 (2)): unchanged.** The header changes only the vector of a chunk the vectors already
  held; the hits are the same chunk records, and `retrieve` filters them by the caller's `role_paths` after the search
  as before. The evidence text and the reranker's input are read from `lexical_fts`, untouched.
- **The switch is a full re-embed and nothing serves a mixed store: yes.** In `_build`, a recorded recipe other than
  the setting (`is not`, so an unreadable row counts as other) deletes every vector and writes the new recipe in the
  same transaction; a batch that gives up commits only vectors of the new recipe (the old ones already deleted), and
  the store is `stale` until every wanted chunk has one. `_vectors` compares the recorded recipe with the setting on
  every status read, and `_status`'s cache key now stamps `rebuild.yaml` (in `KNOWN_FILES`), so a switch is seen at
  once; `gov retrieve` searches with `refresh=False`, so a stale store is `FACET_UNAVAILABLE` (keywords only), never
  served. A seeded store carries its `semantic_pin` rows, so a recipe other than the tree's is stale there too (F3).
- **`CONFIG_INVALID`: right, and wide.** An invalid `embed_headers` (`yes`, `True`, quoted `"true"`, null, a list)
  fails `load_config`, so every `gov` command in that tree fails before it starts (DEC-185); the guard does not use
  `load_config`. The file's other faults stay the rebuild's own (`_rebuild_settings` holds an unreadable file as none,
  and `embed_headers()` itself still refuses a non-map or bad YAML for the semantic stage).
- **The merge: clean in meaning.** Integrate's S8 (routing, phrasings) and the request bounds work at query time and on
  the reranker's input; this branch changes only the embedder's chunk input, the recipe row and the loader's known
  files (beside integrate's `retrieval.yaml`; the `rebuild.yaml` branch in `_load` returns before `validate`, so
  integrate's `_validate_retrieval` is not reached for it). The query embedder is given no header, as intended. The
  one interaction is F1 (a test helper), plus F3 for worktrees after the switch.

## Findings

**F1. One S7 acceptance case goes red with this branch: `test_w2_32_s7_whole_chunk.py::test_a_store_embedded_at_the_old_cut_is_stale_and_the_next_rebuild_embeds_the_chunk_whole`.**
Red on `335233db685d` and on the merged tree; passes on integrate `0936077cfe29`. The designer's helper
`w2_32_support.set_store_cut` treats every key of `manifest()` other than the models as the cut (the interface: "the
key is not judged"), and sets a `semantic_*` column only if every value it holds is among those keys' values. The
manifest now also carries `embed_headers: False`; the `semantic_pin.value` column holds `{"10000", "false"}` against
`{"10000", "False"}`, so nothing is set and the case's premise fails ("0 > 0"). The product is right (the old-cut
stale and re-embed path is unchanged, and the designer's header case needs `manifest()` to carry the recipe), so the
fix is the designer's: `cut_entries` should leave out `embed_headers` (or pick the `embed_chars` key). Merged as it
stands, `gov accept W2-32`'s S7 line shows this red on integrate.
- Ordinary work: yes, because the CTO's gate run after this merge runs it.
- Consequence: other (a red gate case, which fails closed on the close; no product behaviour is wrong).

**F2. With headers on, every rebuild's semantic stage spends about 79 s on this repository's store working out headers, and a full re-embed about 79 s more.**
`_Texts._PARENTS` binds only `p.path`, and SQLite plans it as a scan of the whole `lexical_fts` table for each file
(`SCAN f VIRTUAL TABLE`). `refresh` always passes `cut`, so `over_limit` computes a header for every kept chunk on
every rebuild, a close's refresh and the store loader's refresh included, even when nothing is to embed (measured
read-only on the main store: 0.030 s a file, 2,632 paths). Binding the chunk's path too (`WHERE p.path = ? AND c.path
= ?`, the same rows) plans through `lexical_chunk_by_path`: 0.07 s for every path. Search is not affected (`_vectors`
computes no header).
- Ordinary work: yes, because once the CTO switches it on every `gov rebuild` and close's refresh runs it.
- Consequence: other (speed; feature-gated, so per DEC-803 an entry criterion of the switch: one line, best in before
  the setting goes on).

**F3. Seeding across the switch: a tree whose `rebuild.yaml` says otherwise than the base's recipe is seeded, then its first rebuild drops every vector and re-embeds the whole store.**
`seed._differences` compares the code, the schema and the embedder, not the recipe; the copied `semantic_pin` row
then makes the tree's vectors `stale` (correct, never mixed), and its next build is a full re-embed (55,591 chunks
here), the semantic facet unavailable until it ends. Every live worktree branched before the switch has no
`rebuild.yaml` (false) and meets this against an integration store built with headers. `seed.py` is outside this
ticket's paths.
- Ordinary work: yes, because a worktree branched before tonight's switch is seeded in ordinary work.
- Consequence: other (GPU time and a keywords-only window; fails closed). Recommend the CTO merges integrate into the
  live worktrees before they rebuild, and a row for the seed (W2-76's) to name or refuse a recipe difference.

**F4. A `#` line inside a fenced code block is a heading for the chunker, so the header trail can be wrong.**
`chunking.parents` already makes such a line a section (pre-existing); `headers` then puts it in the trail, and a
level-1 `# comment` pops the whole trail, so later sections of that file carry the comment as their title until the
next real heading. 33 of 1,504 tracked Markdown files, 223 lines. Deterministic, and only the embedder's input.
- Ordinary work: yes, because such files exist and are embedded.
- Consequence: other (retrieval quality only; a row for the chunker, not this round).

**F5. The header is not bounded on its own.** `(header + text)[:EMBED_CHARS]` keeps the header first; a heading line
near 10,000 characters would leave little or none of the text. No such heading exists in the tracked tree.
- Ordinary work: no, because it needs a heading line thousands of characters long.
- Consequence: other.

## Verdict

S7 (its DEC-1067 order (5) note): **pass.** Off is byte for byte today's input; the header is deterministic and
built from the chunk's own file only; nothing kept out gets one; role separation is unchanged; a switch is a full
re-embed and no mixed store is served; the `src/` merge onto `0936077cfe29` is the branch's change line for line.
No finding is in scope, ordinary work and fails open or loses work. Before the CTO switches it on: F1 (the designer's
helper, or integrate's S7 gate line goes red) and F2 (one bound path in `_PARENTS`), which ride along (DEC-802);
F3 as an operating note for the switch; F4 and F5 rows.

```verdict
{"kpis": [
 {"kpi": "S7", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}
]}
```
