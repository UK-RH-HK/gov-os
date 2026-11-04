# D-7 + G4 review: what memory embeds and what the keyword index holds (DEC-1052 M-4, DEC-1055 (3), DEC-1066 (3))

Independent reviewer, fresh, read-only for what is reviewed, in the CTO's session (not a sandbox). No `gov retrieve`,
no `gov context`, no embedder, reranker or model started, no rebuild with embeddings. Reviewed: `emg/d7` at
`88134ee45ac3` (worktree `~/gov-os-worktrees/D-7`) against `w2/W2-13` at `5e5d74dde8e6`. That covers:
- the CTO's path map, `9c0807889cb4`;
- the engineer's unit revision, `ef6acd499658`;
- the test designer's acceptance revision, `bf92158a7553`.

`git diff 5e5d74dde8e6 88134ee45ac3` touches 7 files, all under `governance/project/path-map.yaml` and `tests/`. Nothing
under `src/`, `template/` or `.claude/` changes. The verdict's lines are M-4 (D-7's embedding scope) and G4 (DEC-1066 (3)).

Judged by ADR-0001's threat model and DEC-1010 item 1, with JUDGEMENT.md's two questions:
- "Can an honest agent hit this in ordinary work?"
- "Does it fail open or lose work?"

`TMPDIR=/tmp/gov-os-emg-d7-review`. All runs were in two scratch clones made with `git clone --shared` from the D-7
worktree; that writes nothing to the source repository. Scripts are in the TMPDIR and are not committed.

## What was checked

- **Mirroring the indexers.** For each of the 3,187 files tracked at head, a script (`ns_compare.py`) computed the
  verdict under the base's map and under the head's map. It mirrors three rules:
  - one namespace: `check.pathmap`;
  - embedded: `semantic._wanted`, which requires that every matched namespace says `embedded`;
  - keyword-indexed: `secrets._governance`, which requires a namespace whose `memory_class` is governance, and
    `lexical.kept_out`.

  As a cross-check, it recomputed measure 1's vector count from measure 1's store
  (`~/gov-os-runs/D4B/m1/repo/.gov-runtime/store.db`, read-only) under measure 1's map: **63,947, exactly** the
  store's `semantic_vector` count.
- **The path-map check** at head (`python3 -m gov.check.pathmap` in the clone): exit 0, no finding. This confirms the
  CTO's "GREEN".
- **The guard's inputs.**
  - The `role_paths:` block and the `evaluation_sets:` block are byte-for-byte unchanged. The diff's hunks lie only
    in `namespaces:`, from line 45 to line 260.
  - `gov.guard.role_paths` and `gov.guard.reads` read no namespace (grep: no `namespaces` or `embedding` use).
  - `{ticket_tests}` resolves from the `role_paths` block, the ticket and the commits' trailers, not from the `tests`
    namespace.
  - Retrieval's role filter (`retrieve.py:129`, `supplementary.py:135`) applies to every route's hits. A test file
    that the keyword route returns is still withheld from its ticket's engineer.
  - No code names a namespace by its name (grep over `src/`).
- **Runs** (each through `heavy_slot.sh`, `PYTHONPATH=<clone>/src`, `-m "not local_only"`,
  `-k "not real and not green_here and not time_limit"`, `-p no:cacheprovider`):
  - W2-86, W2-91 (acceptance), the W2-91 unit file, W2-13, W1-08, W2-95, W1-27's two path-compliance files and the
    W2-95 unit file: **189 passed**.
  - The scoped set from `select_tests.py <clone> D-7 DAEO-sdxk --base 5e5d74dd` (163 targets): **2,379 passed,
    1 failed, 6 skipped**. The red is
    `tests/acceptance/W1-28/test_w1_28_fixture_copies.py::test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs`.
    It names `W2-13/w2_13_lexical_policy_support.py::pre_s6_src` and `W2-92/test_w2_92_speed.py::base`. Re-run alone
    at the base `5e5d74dde8e6`, it is **red there too**, so D-7 did not cause it. It belongs to W2-13's review and
    W2-92. My real HOME was used, so the CTO's 28 empty-HOME reds do not appear.
- **Planted regressions.** Each plant went into scratch clone 1's path map (or added a tracked file), then the
  guarding tests and the path-map check ran, then the clone was reset. Results:

| plant | path-map check | red |
|---|---|---|
| A `docs/spec/**` dropped from `docs` | RED | W2-86 case 3; W2-91 `nothing_else_moves` (acceptance and unit); W2-91 one-namespace (acceptance and unit); W1-08 one-namespace (6) |
| B `docs/research/**` moved into `doc-records` | green | W2-86 case 3; W2-91 `nothing_else_moves` (acceptance and unit) (3) |
| C `tests` given `lexical_policy: not indexed` | green | **none (67 passed)** |
| D `doc-records` given `lexical_policy: not indexed` | green | **none (67 passed)** |
| E lens B's `lexical_policy` removed | green | W2-13 `test_the_repository_marks_..._not_indexed[lens B's report]` (1) |
| F a new tracked `docs/newfolder/x.md` | RED | W2-86 case 3; W2-91 one-namespace (acceptance and unit); W1-08 (4) |
| G `tests` embedded again | green | W2-86 case 3; W2-91 `nothing_else_moves` (acceptance and unit) (3) |
| H `orchestration-records` embedded | green | W2-91 success 1, W2-91 rebuild, W2-91 unit `nothing_else_moves` (3) |
| I a new tracked `docs/assessment/2026-10/J-new-lens.md` | RED | as F (4) |

- **The test designer's and the engineer's stated counts** were checked against the script:
  - 1,763 files leave the vectors outside `template/`: 1,322 under `tests/`, 18 in `docs/close/`, 363 in
    `docs/checkpoints/`, 59 in `docs/probes/`, and lens B's report;
  - `project-overlay` holds 209 files, `orchestration-records` 40, the overlay's `tools/` 14.

  All of these match.
- **Visible gold.** No visible question's gold source (the 24 questions' `sources[].path`) lies in a folder that moves. The
  hidden half was not read: my role is refused it, and `~/gov-os-eval` was not touched. Its counts are the CTO's
  step 0 (`drafts/d4b/count_gold.py`); see "unresolved" in the return.

## The six questions

1. **Exactly one namespace, now and for a new file.** Now: 0 files in no namespace and 0 in two, by both the check
   and the script, at head and at base. For a new file:
   - **Under `tests/`, `.tickets/`, `src/`, the four named `fixtures/` folders, the 14 named `docs/` folders or
     `docs/*`**: the new file lands in its namespace.
   - **A new `docs/<new>/` folder, a new file in `docs/assessment/2026-10/`, or a new `docs/assessment/<month>/`**:
     the file falls in no namespace. The path-map check catches it: `core-pathmap` is hard-block and tier G1, and
     it runs in `gov check` at the pre-close gate and in CI. So do W1-08, W2-91's two one-namespace cases and W2-86
     case 3 (plants F and I). Until then the file is in **neither** index, because both the secrets filter and
     `_wanted` require a namespace. This fails closed, not open.
   - **A new `fixtures/<new>/` folder**: caught by the same check. Its index state does not change, because product
     memory is never indexed.

   This is acceptable (F1). The path-map language has no negation and a path may match only one namespace, so
   naming the folders is the only way to carve records out of `docs/`. No new `docs/` folder has appeared since
   2026-10-20.
2. **Each move matches M-4 and G4, nothing beyond.**
   - Leaving the vectors: exactly DEC-1055 (3)'s list (`tests/**`, `docs/{close,checkpoints,probes}/**`,
     `governance/project/orchestration/{closes,reviews,sessions,nightly}/**`) plus lens B's report, as DEC-1066 (3)
     decides. That is 1,763 files outside `template/` and 40 overlay records.
   - No other file changes its embedding (the script's moves table holds four rows, all decided). The `docs/`
     folders that M-4's recommended list does not name (`adoption`, `charter`, `imported`, `interfaces`, `lessons`,
     `releases`, `spec`, and `docs/*`) stay embedded as at the base. DEC-1055 (3) lists what goes out, not what
     stays, so that is right.
   - `fixtures/**` was already not embedded.
   - `fixtures/memory-quality/**` "not indexed": no file is tracked there, and any file under `fixtures/` is product
     memory and already out of both indexes. So the line changes nothing in either index, today or later. It is
     within the decision in effect (F3).
3. **Nothing a role's search must find leaves both indexes.** At head, exactly one file leaves the keyword index:
   lens B's report, 88 chunks. The 27 evaluation fixtures move from `indexed = 0` (refused by the filter as product
   memory) to `indexed = 2` (kept out by the path map); they were never in the index. Tests and the close,
   checkpoint, probe and orchestration records keep every keyword chunk: 3,101 files indexed at head, against 3,102
   under the base map (the one is lens B). **No test pins this converse** (plants C and D: F2).
4. **`role_paths` and the guard's reads are unchanged.** See "The guard's inputs" above.
5. **The revised tests keep their guards.**
   - W2-86 case 3 now excepts only D-7's cut, and only in the not-embedded direction. Its cut is written in the
     test, not read from the map, and it refuses a vacuous cut. It is red on plants A, B, F, G and I.
   - The W2-91 unit `test_nothing_else_moves` is an equality against base + W2-91 − D-7 (`_intended`), plus planted
     paths in each D-7 folder. It is red on A, B, G and H.
   - W2-91's acceptance success 1 and its rebuild case are red on H.
   - Every guard on embedding holds. The guard on "kept in keyword search" is the one missing (F2).
6. **The effect on measure 2**, as counts: a `--no-embeddings` rebuild of a scratch clone at `88134ee45ac3`, with the
   store read-only afterwards.

| | under W2-13's map (`5e5d74dde8e6`) | under D-7's map | change |
|---|---:|---:|---:|
| vectors (chunks embedded) | 65,852 | 18,831 | **−47,021 (−71.4 %)** |
| of which `tests/**` | 41,127 | 0 | −41,127 |
| of which `docs/close`, `docs/checkpoints`, `docs/probes` | 3,629 + 1,089 + 774 | 0 | −5,492 |
| of which the overlay's closes, nightly, sessions, reviews | 157 + 91 + 12 + 54 | 0 | −314 |
| of which lens B's report | 88 | 0 | −88 |
| keyword index (chunks) | 68,062 | 67,974 | **−88** (lens B; 1 file) |
| files kept out of the keyword index by the path map | 0 | 28 (27 fixtures, lens B) | +28 (only lens B is a real change) |

For comparison, measure 1's store at `156a5feb677b` held 63,947 vectors, and the package's estimate was 57,600 → 13,500.
W2-15a's record (merged `ff691ec2294a`) adds a raw folder of 115 chunks, which stays embedded and indexed (F5).

## Findings

### F1: a new `docs/` folder or assessment file falls in no namespace until the path map names it (M-4)

Plants F and I. The file is out of both indexes until someone adds one line to the path map. `core-pathmap`
(hard-block), W1-08, W2-91 and W2-86 turn red at the next `gov check`, close or CI run. This follows from the schema
(no negation; exactly one namespace).

Recommendation: none needed for D-7. When D-5 writes the product-spec template, it can name "a new `docs/` folder adds
a line to `namespaces.docs`" as a fact.

Ordinary work: yes, because adding a `docs/` folder or a new assessment lens is plausible (although none has appeared
since 2026-10-20).
Consequence: other (fails closed: the file is in neither index for a while, and a hard-block check names it; nothing
is exposed and nothing is lost, git holds the file).

### F2: no test pins that the keyword index keeps tests and the records (M-4's "they stay in keyword search")

Plants C and D add `lexical_policy: not indexed` to `tests` or `doc-records`. The pair is valid (not indexed with not
embedded), the path-map check stays green, and all 67 guarding cases pass. Those files would then leave both indexes,
which is the opposite of M-4. W2-13's repository case pins only the positive: lens B and the fixtures are marked.

Recommendation: the test designer adds the converse beside W2-13's repository case. The namespaces that say
`not indexed` are exactly `evaluation-sources` and `evaluation-fixtures` (or, in path terms: every tracked file
outside lens B's report and `fixtures/evaluation/**` is not kept out). It rides with the next resume of W2-13 or D-7
(DEC-802); no round.

Ordinary work: yes, because W2-32's G2 round (keyword ranking, "code above tests") is an honest occasion to reach for
`lexical_policy` on `tests`.
Consequence: other (tests and records would no longer be findable by keyword; files stay in git and `Grep`; no gate
opens, and nothing is exposed or lost). Today's map is correct.

### F3: `fixtures/memory-quality/**` "not indexed" names a folder DEC-1066 (3) does not name (G4)

The designer's question: DEC-1066 (3) names `fixtures/evaluation/**`. W2-32 S3's memory-quality events and
"held-out" regression cases (CAP-19.c) will be written "in the project, outside `.gov-runtime/`", in a place S3 leaves
open. S3 requires only "not embedded".
- No file is tracked there today.
- Any `fixtures/` file is `memory_class: product`, which the secrets filter keeps out of the keyword index anyway.
- So the line removes nothing from either index that would otherwise be in it. It only gives the folder a namespace
  (no path-map red when W2-32 writes there) and names its files as kept out.
- The regression case is in the measure's question form, so keeping it out of the keyword index is G4's own reason.

Judged within the decision in effect. Two small inconsistencies, both harmless (nothing is tracked there):
- W2-86's `D7_NOT_EMBEDDED` omits the folder, while the unit file's `D7_OUT_FOLDERS` has it;
- if W2-32 wants its events (not only the cases) findable by keyword, they must live outside `fixtures/`. That is
  W2-32's choice and evidence.

Ordinary work: yes, because W2-32 S3 will write there or nearby.
Consequence: other.

### F4: `lexical_policy: not indexed` on `evaluation-fixtures` is redundant, and `9c0807889cb4`'s message misstates fixtures (G4)

The measure 1 store holds 84 `fixtures/` files at `indexed = 0` with 0 chunks: they were never in the keyword index.
The line's effect is that the rebuild names them as kept out, and it guards against a later `memory_class` change.
The commit message says that `fixtures` are "not embedded (keyword index only)", but fixtures are in neither index.
The record wording should be fixed if the message is quoted in D-7's evidence.

Ordinary work: no, because it is wording; no behaviour depends on it.
Consequence: other.

### F5: a new copy of the visible questions stays in both indexes: W2-15a's raw `topk-visible-misses.txt` (G4's cause, outside D-7's decided scope)

`docs/research/EXP-003/w2-15a/raw/topk-visible-misses.txt` (12 KB, merged with W2-15a's record, `ff691ec2294a`, after
measure 1) holds the opening of 9 of the 19 visible questions with more than 30 characters. That count comes from a
scan that compared counts only (the first 60 characters of each question, verbatim) and printed no text. It is
embedded and indexed under both maps, in the 115 chunks of the raw folder.
- It is the same kind of document as lens B (D4B-GAPS cause 3): never gold, so it can only push gold down.
- Measure 1 did not have it. Measure 2 on this head will, so a drop could be blamed on D-7's scope when this file is
  the cause.
- No other tracked file outside `fixtures/` quotes a question this way, apart from two test files (W2-55, W2-61),
  which are now not embedded.

Moving it out is a decision, not D-7's (see proposed decisions in the return).

Ordinary work: yes, because measure 2 runs on this head.
Consequence: other (it lowers the figure; a never-gold file cannot pass the measure falsely).

### F6: `governance/project/orchestration/nightly/**` holds code (10 of 11 files are `.sh` or `.py`), now not embedded (M-4)

DEC-1055 (3) lists `nightly` among the not-embedded records explicitly, so D-7 is right. M-4's "memory embeds ... the
code" and DEC-934's "the nightly's committed, reviewed scripts" pull the other way. This is a row for D-9's re-wording
of W2-91 S1: 91 chunks.

Ordinary work: yes, because the nightly's scripts are searched when its runs break.
Consequence: other (they stay in the keyword index).

## Verdict

D-7's path map does what M-4, DEC-1055 (3) and DEC-1066 (3) decide, and nothing beyond:
- every tracked path is in exactly one namespace;
- 47,021 chunks leave the vectors, all of them decided;
- 88 chunks (lens B) leave the keyword index;
- `role_paths` and the guard's reads are untouched;
- the revised tests are red on every planted embedding regression.

No finding is in scope, ordinary work, and fails open or loses work. F2 and F3 ride along; F5 goes to the CTO before
measure 2.

```verdict
{"kpis": [
 {"kpi": "M-4", "verdict": "pass", "findings": [
  {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
  {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
  {"id": "F6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}
 ]},
 {"kpi": "G4", "verdict": "pass", "findings": [
  {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
  {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"},
  {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}
 ]}
]}
```
