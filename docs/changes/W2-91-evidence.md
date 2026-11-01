# W2-91 evidence: W2-61's 20-question measure after the root files, the governance overlay and schemas/ are embedded, visible half; the vectors per namespace

- **Ticket:** DAEO-a3u2 (W2-91), profile STANDARD. Written by the engineer from the outputs of the measure its lead ran (DEC-996 (A): a ticket's measurement of its own change is the implementer's evidence, at `docs/changes/<id>-evidence.md`; DEC-995).
- **Date:** 2026-11-01.
- **Sources:** DEC-957 (full embeddings: the root files, `governance/**` and `schemas/**`; the hidden half and the generated copies stay out; memory's target of 95 %), DEC-954 Q9c, DEC-833 item 3 (both figures, always together), DEC-860 (retrieval in batches, ranked and stacked), DEC-388 and DEC-694 (the two values of `embedding_policy`), DEC-381 (a namespace that is not embedded never reaches the vectors), DEC-856 and DEC-887 (the overlay's namespace), DEC-820 (d), CAP-10.a and CAP-10's floor of 85 for hit@5; the ticket's KPI lines success 1 to 6 and failure 1 to 4. The figures beside these are `docs/research/W2-86-memory-measure.md` and `docs/research/W2-61-baseline.md`.

This record holds scores only: ids, counts, ranks, digests and pass or fail. It quotes no question's text, no gold answer and no text of a retrieved item. The hidden half of the set was neither read nor run.

## 1. What was measured, and where

- **The two clones,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, left detached:

  | Clone | Commit | What it is |
  |---|---|---|
  | `/home/usain/gov-os-runs/W2-91/head` | `b652fc96d2b5` | the branch head with the path map's change and the ticket's tests; the tree measured as the head |
  | `/home/usain/gov-os-runs/W2-91/base` | `f46b96537d74` | `w2/integrate`'s head when the ticket started; the tree measured as the control, and also the measure's own clone (its code and the visible set, `--sets-root`) |

- **The code is the same at base and head:** `git diff --stat f46b96537d74 b652fc96d2b5 -- src` is empty.
- **What else the head holds** (deviation 2, §7): besides the ticket's commits, the lead's merge of `w2/integrate` at `904bb3a0e7c6` for the ticket's claim. It brought records, the merge queue's tool and its unit test, and no code under `src/`. The path map and `src/` at `904bb3a0e7c6` are the same as at `f46b96537d74` (`git diff --stat` empty for both).
- **The retriever: the pinned gov,** `/home/usain/.local/share/gov-os/pin-5c401220/bin/gov` in both runs.
  - **Version:** `gov 0.1.0 (commit unknown)`, as each run's record names it.
  - **Commit:** `5c40122014da`, named by the pin's folder (`pin-5c401220`), as W2-61's and W2-86's records name it.
- **The measure:** `src/gov/retrieval/measure.py` from the base clone at `f46b96537d74` (last changed at `289b9314a763`, the same code W2-86 ran).
- **The set:** `memory-retrieval`, the visible half only: the 20 questions Q01 to Q20, read from the base clone (`--sets-root`). The hidden half was neither read nor run.
- **The budgets:** the measure's defaults, `batch_size 10`, `bundle_budget 6000`, `stack_budget 24000` (each run's `budget`), as in W2-61's baseline and W2-86's measure.

## 2. The stores' fingerprint

Each clone's stores were built in that clone by the pinned gov, with embeddings (never `--no-embeddings`). Each rebuild ran through `tools/rebuild_slot.sh`, which takes a heavy-job slot and the clone's own lock (DEC-1001 (d)), with `GOV_REBUILD_PYTHON=/home/usain/.local/share/gov-os/pin-5c401220/bin/python`, no `PYTHONPATH` and no `GOV_TICKET`. Times are UTC, on 2026-11-01.

| | base (control) | head |
|---|---|---|
| Disk gate before the rebuild | open: 855 GiB and 64,598,040 inodes free | open: 853 GiB and 64,434,966 inodes free |
| Script start | 16:01:30 | 16:45:25 (it waited for a heavy-job slot until about 17:11; all three slots were busy) |
| End | 17:21:07 | 18:40:14 |
| Exit code | 0 (`ok: true`) | 0 (`ok: true`) |
| Stores (`lexical`, `semantic`, `codeintel`) | each `recreated` | each `recreated` |
| Lexical timing (`timing.lexical_s`) | 278.9 s | 297.7 s |

**The digest each rebuild records** (`result.digest`):

- base (control): `6de3fba99c6fed852b3e99428897af100ee28096e2575ff5ec7c436030ea96a4`
- head: `6061a0dbebd18d2809bfbaf189f0bb6abcd7eb3f303803907690c86dfe9b8dfa`

**The sha256 of each store file after the rebuild:**

| Store file | base (control) | head |
|---|---|---|
| `.gov-runtime/store.db` | `473eba4c3a67683fcd286e477a4c012a2e8a9f9b0e776506464096aac47f1a9b` | `687afd8bbc57794482b3109db3af7a1ddc03e732e6d9503c8de7a9bdbaf02e04` |
| `.gov-runtime/codeintel/home/code.db` | `5e422adca9c8969ef5d3b6c50aec461cee58342191308cedb17ee104bd671764` | `78e750993574dd245478457feea5d51a5b4843dea2f93c963fec1a7e369a7062` |
| `.gov-runtime/codeintel/home/_config.db` | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` | the same (also W2-61's, W2-86's and W2-87's) |

The two digests differ because the record graph differs: the head holds the ticket's commits and the merge of `w2/integrate`. The digest covers the store's record graph (`_digest`, `src/gov/store/loader.py:307`), not the vectors, so the vector set is the figure compared (§6), as in W2-86's §2.

## 3. The runs

Each run measured the visible half with the pinned gov. Times are UTC, on 2026-11-01, as the lead's run log gives them.

| Run | Tree | Start | End | Exit | stderr | Record | `--compare` |
|---|---|---|---|---|---|---|---|
| control | base `f46b96537d74` | 17:21:07 | 17:34:26 | 0 | empty | `records/measure-memory-retrieval-visible-20261101T173426352951Z.json` | — |
| head | head `b652fc96d2b5` | 18:40:53 | 19:35:16 | 0 | empty | `records/measure-memory-retrieval-visible-20261101T193515830840Z.json` | the control's record |

The records are under `/home/usain/gov-os-runs/W2-91/`. A comparison covers five fields per question: hit@5, in the bundle, full evidence, the first gold rank and the stacked digest (the paths and line spans of the stacked context, in order). The head's first measure was stopped before it wrote a record; the head's record above is from a second run on the same store (deviation 3, §7).

## 4. The totals: both figures together

| | hit@5, against CAP-10's floor of 85 and the owner's target of 95 % (DEC-957) | Full evidence, against the owner's target of 99 % | In the bundle |
|---|---|---|---|
| W2-61 baseline (`23079f92a6fa`, pinned gov, pinned stores) | 8 of 20 (40 %), short of 85 by 45 points, of 95 by 55 | 12 of 20 (60 %), short by 39 points | 14 of 20 |
| W2-86 control (`9dc5288161c4`, pinned gov) | 7 of 20 (35 %), short of 85 by 50 points, of 95 by 60 | 11 of 20 (55 %), short by 44 points | 13 of 20 |
| W2-86 head (`338c14fa6475`, pinned gov) | 7 of 20 (35 %), short of 85 by 50 points, of 95 by 60 | 11 of 20 (55 %), short by 44 points | 13 of 20 |
| W2-86 head, tree code (supplementary, `338c14fa6475`) | 11 of 20 (55 %), short of 85 by 30 points, of 95 by 40 | 11 of 20 (55 %), short by 44 points | 15 of 20 |
| W2-91 control (`f46b96537d74`, pinned gov) | 7 of 20 (35 %), short of 85 by 50 points, of 95 by 60 | 11 of 20 (55 %), short by 44 points | 13 of 20 |
| **W2-91 head (`b652fc96d2b5`, pinned gov)** | **7 of 20 (35 %), short of 85 by 50 points, of 95 by 60** | **11 of 20 (55 %), short by 44 points** | **13 of 20** |

**Head against control** (the like-for-like pair, with the same retriever and the same code): hit@5 7 → 7 of 20, full evidence 11 → 11 of 20, in the bundle 13 → 13 of 20. The change moved none of the three figures on this set.

## 5. Per question, visible half

Each cell gives, in order: hit@5, first gold rank, in the bundle, full evidence (pieces found of needed). "First gold rank" is the rank, in the stacked context, of the first item that matches a gold source; "in the bundle" means an item of the first call matches one. W2-61's baseline is its §5; W2-86's columns are its §5 (its control and head are the same in every cell). The last column is the head run's `--compare` against the control.

| Q | W2-61 baseline | W2-86 control and head (pinned) | W2-86 head, tree code (supplementary) | W2-91 control (pinned) | W2-91 head (pinned) | Head against control |
|---|---|---|---|---|---|---|
| Q01 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q02 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q03 | yes, 4, yes, yes (1/1) | no, 7, yes, yes (1/1) | yes, 2, yes, yes (1/1) | no, 7, yes, yes (1/1) | no, 6, yes, yes (1/1) | first gold rank, stacked digest |
| Q04 | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | stacked digest |
| Q05 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 4, yes, yes (1/1) | yes, 4, yes, yes (1/1) | stacked digest |
| Q06 | no, 9, yes, yes (2/2) | no, 8, yes, yes (2/2) | no, 7, yes, yes (2/2) | no, 8, yes, yes (2/2) | no, 8, yes, yes (2/2) | stacked digest |
| Q07 | no, 12, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | stacked digest |
| Q08 | no, 9, yes, yes (1/1) | no, 9, yes, yes (1/1) | no, 11, yes, yes (1/1) | no, 9, yes, yes (1/1) | no, 8, yes, yes (1/1) | first gold rank, stacked digest |
| Q09 | no, 60, no, yes (1/1) | no, 59, no, yes (1/1) | no, 44, no, yes (1/1) | no, 59, no, yes (1/1) | no, 59, no, yes (1/1) | stacked digest |
| Q10 | no, 25, no, no (1/2) | no, 25, no, no (1/2) | no, none, no, no (0/2) | no, 25, no, no (1/2) | no, 25, no, no (1/2) | stacked digest |
| Q11 | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | same |
| Q12 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | stacked digest |
| Q13 | no, 6, yes, no (1/2) | no, 6, yes, no (1/2) | yes, 1, yes, no (1/2) | no, 6, yes, no (1/2) | no, 6, yes, no (1/2) | stacked digest |
| Q14 | no, 16, yes, no (7/9) | no, 16, yes, no (3/9) | no, 17, yes, no (4/9) | no, 16, yes, no (4/9) | no, 15, yes, no (4/9) | first gold rank, stacked digest |
| Q15 | yes, 4, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 4, yes, yes (1/1) | first gold rank, stacked digest |
| Q16 | no, 7, yes, yes (1/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | stacked digest |
| Q17 | no, 21, no, no (1/2) | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | no, 21, no, no (1/2) | no, 21, no, no (1/2) | stacked digest |
| Q18 | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | same |
| Q19 | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | stacked digest |
| Q20 | no, 21, no, no (1/2) | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | no, 21, no, no (1/2) | no, 21, no, no (1/2) | same |

**The in-the-bundle count, per question:** yes for Q01 to Q08 and Q11 to Q15 (13 questions) and no for Q09, Q10 and Q16 to Q20 (7 questions), in the control and in the head alike.

**The stacked digests** (the first 16 hexadecimal digits of each run's `stacked_digest`):

| Q | control | head | | Q | control | head |
|---|---|---|---|---|---|---|
| Q01 | `4ca38be7a0c8468f` | `7051bcbff0ff19b6` | | Q11 | `c8ef3553bbda31c7` | `c8ef3553bbda31c7` |
| Q02 | `e71f57c4fd6cbf14` | `1ecd0aa17d3a8ddb` | | Q12 | `0a9672dea4602b5b` | `04a1ca5e91e28b58` |
| Q03 | `68c06fc9b0b031fa` | `b90d7731379d7f54` | | Q13 | `fadc483f653e1b82` | `07660af5fc229776` |
| Q04 | `deedab3b3835b5d6` | `0e72ebbe70756e8d` | | Q14 | `e4b6430169871a8b` | `4ccc531a4ba82da6` |
| Q05 | `c90f20e1b5580ed8` | `89a018337bad32a0` | | Q15 | `4cab476e49f285e6` | `9e98dc8b6c2cb80c` |
| Q06 | `765762823617e504` | `b9f40db5cf05a5f8` | | Q16 | `d0fc6ff1da9097a0` | `6208aeaa2473ed79` |
| Q07 | `83d13ad05eb89d1e` | `d78981a216ad5092` | | Q17 | `507549f4e9f29497` | `48e79f4c0dad0d8c` |
| Q08 | `800de3a7f479a1b6` | `1c036db60d2fd1e6` | | Q18 | `cd3989c751a72242` | `cd3989c751a72242` |
| Q09 | `190038d3c849190b` | `49cfccd70de2437e` | | Q19 | `78a9908482dfe8e8` | `fe416f68fcfc2c89` |
| Q10 | `a8962443057ef4a1` | `3098530010fcc7bf` | | Q20 | `726b8a89d997f8f9` | `726b8a89d997f8f9` |

**What changed, control to head (pinned):**

- **Unchanged for 20 of 20 questions:** hit@5, in the bundle, full evidence and the pieces found.
- **The first gold rank moved for 4 questions, each by one place:**
  - Q03: 7 → 6, still outside the first five.
  - Q08: 9 → 8.
  - Q14: 16 → 15.
  - Q15: 3 → 4, still inside the first five.
- **The stacked digest differs for 17 questions;** it is the same for Q11, Q18 and Q20. So the stacked context changed for 17 questions, but the count of gold pieces found did not change for any question.
- **What the facts do not show:** which items entered the context. The head's stores also differ from the base's by the records merged from `w2/integrate` (deviation 2), so this record does not attribute the changes to the newly embedded chunks alone.
- **Calls per question:** the same in both runs, Q01 to Q20: 5, 2, 2, 2, 2, 3, 5, 2, 4, 2, 2, 2, 2, 5, 2, 2, 2, 2, 2, 2. These are also W2-86's.

**This control against W2-86's control and head** (the same pinned gov, a later tree and its stores):

- The same totals: 7, 11 and 13 of 20.
- The same cells, with two exceptions:
  - Q05's first gold rank: 2 there, 4 here, still inside the first five.
  - Q14's pieces: 3 of 9 there, 4 of 9 here.

**Against W2-61's baseline:** this control carries the same differences W2-86's §5 found for its own control:

- Q03 leaves the first five.
- Q16 loses its source.
- Q14's pieces fall from 7 of 9; they are at 4 of 9 here.

So hit@5 is 8 → 7, full evidence 12 → 11 and in the bundle 14 → 13 of 20.

## 6. The vectors

From the lead's count over the two clones' stores, each opened read-only, judged by the head's path map. A chunk is a row of `lexical_chunk`; it has a vector when `semantic_vector` holds its id. "Files" are the tracked files of the namespace; "with vectors" counts the files that have at least one chunk with a vector.

| Namespace (head's map) | `embedding_policy` at the head | Files, base / head | Chunks, base / head | Chunks with vectors, base | Chunks with vectors, head | Files with vectors, base / head |
|---|---|---|---|---|---|---|
| `root-files` (`*`) | embedded | 8 / 8 | 26 / 26 | 0 | **26** | 0 / **8** |
| `project-overlay` (`governance/**` as listed) | embedded | 165 / 166 | 2,902 / 2,941 | 0 | **2,941** | 0 / **166** |
| `carried-schemas` (`schemas/**`) | embedded | 5 / 5 | 31 / 31 | 0 | **31** | 0 / **5** |
| `carried-code` (`cli/**`) | not embedded | 0 / 0 | 0 / 0 | 0 | 0 | 0 / 0 |
| `agent-settings` (`.claude/**`, `.rulesync/**`) | not embedded | 87 / 87 | 1,071 / 1,071 | 0 | 0 | 0 / 0 |
| `fixtures` (`fixtures/**`, the hidden half among them) | not embedded | 78 / 78 | 0 / 0 | 0 | 0 | 0 / 0 |
| `kernel-adapter-copies` (`template/.rulesync/**`) | not embedded | 44 / 44 | 529 / 529 | 0 | 0 | 0 / 0 |
| `kernel-vendored` | not embedded | 30 / 30 | 323 / 323 | 0 | 0 | 0 / 0 |
| `ci` (`.github/**`) | not embedded | 1 / 1 | 5 / 5 | 0 | 0 | 0 / 0 |
| `tickets` | embedded | 181 / 182 | 928 / 931 | 928 | 931 | 180 / 181 |
| `docs` | embedded | 868 / 868 | 14,235 / 14,245 | 14,235 | 14,245 | 866 / 866 |
| `kernel-template` | embedded | 93 / 93 | 410 / 410 | 410 | 410 | 93 / 93 |
| `gov-source` (`src/**`) | embedded | 138 / 138 | 2,795 / 2,795 | 2,795 | 2,795 | 132 / 132 |
| `tests` | embedded | 1,202 / 1,207 | 35,531 / 35,741 | 35,531 | 35,741 | 1,162 / 1,167 |
| **The whole store** | | 2,773 / 2,780 paths with chunks | 58,786 / 59,048 | **53,899** | **57,120** | |

- **The newly embedded sets have vectors at the head (KPI 1):**
  - **The root files:** all 8 tracked ones, `.gitignore`, `.gitleaks.toml`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `copier.yml`, `lefthook.yml` and `pyproject.toml` (26 chunks).
  - **`governance/**`:** every tracked file under it, 166 of 166 (2,941 chunks). `git ls-tree -r b652fc96d2b5 -- governance` counts 166 files, all in `project-overlay`.
  - **`schemas/**`:** every tracked file under it, `schemas/records/{checkpoint,decision,lesson,record,research}.schema.json` (31 chunks).
- **What stays out has no vector, in either store (KPI 2):** `fixtures/**`, `.claude/**`, `.rulesync/**`, `template/.rulesync/**` and the `kernel-vendored` parts all hold 0 chunks with vectors. `fixtures/**` has no chunk at all. `cli/**` holds no tracked file at either commit, so it has no chunk and no vector; its namespace says `not embedded`.
- **The vector diff, base to head (KPI 5):** 185 paths gain vectors and none loses any.
  - **179 are the newly embedded sets:** the 8 root files, the 166 files under `governance/` and the 5 under `schemas/`.
  - **4 are the ticket's own new files:** `tests/acceptance/W2-91/README.md`, `tests/acceptance/W2-91/test_w2_91_full_embeddings.py`, `tests/acceptance/W2-91/w2_91_support.py` and `tests/unit/retrieval/test_w2_91_full_embeddings.py`.
  - **2 are new files the merge of `w2/integrate` brought for the claim** (deviation 2): `.tickets/DAEO-fu3n.md` (added at `567ca6c762fd`) and `tests/unit/orchestration/test_merge_queue_speed.py` (added at `904bb3a0e7c6`). They are not the ticket's own, and their namespaces (`tickets`, `tests`) were embedded at the base too, so their verdict is the base's.
  - **No other path** gains or loses a vector.
- **The other chunk counts:** in the namespaces that were embedded at both ends, the counts that moved (`tickets` +3, `docs` +10, `tests` +210) come from those new files and from changed contents of existing files. Every chunk of those namespaces has a vector at both ends.
- **The arithmetic:** 57,120 − 53,899 = 3,221 more chunks with vectors. That is 2,998 in the newly embedded sets (26 + 2,941 + 31) and 223 in the namespaces embedded at both ends (3 + 10 + 210).
- **Every other tracked path's verdict is the same at the head as at the base** (KPI 5). The ticket's builder test `tests/unit/retrieval/test_w2_91_full_embeddings.py::test_nothing_else_moves` checks this for every path tracked at both commits, against the path map at `904bb3a0e7c6`, which is the same as at `f46b96537d74`. The acceptance line success-5 passes (§7).
- **The held-out list file:** the overlay now embeds every tracked file under `governance/**`, and that includes the held-out list file, whose text was already in the lexical index. Only file names are involved; no held-out contents were read for this record.

## 7. The restricted overlay, the acceptance run, and deviations

### The restricted overlay (KPI 3)

- **The overlay's other fields are unchanged.** `project-overlay` keeps `sensitivity: restricted` and `export_policy: denied` at the head, as the head map's figures in the lead's count show, and the same as at the base.
- **The indexer reads `embedding_policy` only.** `_wanted` in `src/gov/retrieval/semantic.py` (lines 207 to 221; the read is at line 215) embeds a file's chunks when every namespace the file matches says `embedded`. Two other places read the field, and neither reads `sensitivity` or `export_policy`:
  - `src/gov/rebuild/command.py:32`, for the warning given when no namespace is embedded;
  - `src/gov/adopt/stages.py:240` to `248`, which checks that the value is one of the two.
- **Nothing in `src/` reads the values of `sensitivity` or `export_policy`.** The two names appear only:
  - as required field names in `src/gov/config/path_map_schema.py:14-15`;
  - as text fields in `template/governance/kernel/schemas/path-map.schema.json:164, 178, 181`;
  - as literal values in a sample namespace that `src/gov/retrieval/retrieve_check.py:141, 144` writes.
- **So embedding the overlay changes no export or sharing rule.**
- **No export path exists today.** No code exports a namespace, so the KPI line's "planted export case" cannot show an export refusal. The lead has returned this to the orchestrator as a package; this record does not decide it.

### The acceptance run

`gov accept DAEO-a3u2`, run with this worktree's `src/` at `a53650525fd8`, gave the outcome `pass`: 19 tests passed, 0 failed, 0 skipped, 0 unmapped.

| KPI line | Outcome | Tests passed |
|---|---|---|
| success-1 | pass | 2 |
| success-2 | pass | 6 |
| success-3 | pass | 4 |
| success-4 | pass | 5 |
| success-5 | pass | 2 |
| failure-1 | pass | 6 |
| failure-2 | pass | 4 |
| failure-3 | pass | 5 |

Success line 6 and failure line 4 concern this record and the measure; no test maps them.

### Deviations and what they mean

1. **The retriever is the pinned gov, `5c40122014da`,** as in W2-61's and W2-86's records. It predates W2-87's authority order.
   - **What it means:** the control and the head carry W2-61's ranking. The pair head against control isolates this ticket's data change, because the retriever and the code are the same. It moved no figure.
2. **The base is `f46b96537d74`, and the head also holds the merge of `w2/integrate` at `904bb3a0e7c6`.** That merge brought records, the merge queue's tool and its unit test, and ticket `DAEO-fu3n`; it brought no change to `src/` or to the path map.
   - **What it means for the vectors:** two of the paths that gain vectors are not the ticket's own (§6). Both are new files in namespaces already embedded.
   - **What it means for the measure:** part of the head's stacked-context changes may come from those records rather than from the newly embedded files. The facts do not separate the two.
3. **The head's first measure was stopped by the lead before it wrote a record,** because its background task's two-hour limit was minutes away. The measure was then run alone on the same store, which was not rebuilt. The start time in §3 is the lead's log entry.
   - **What it means:** the head's record comes from one complete run with exit 0 and empty stderr.
4. **The rebuilds.** The control's first rebuild attempt waited on the old machine-wide lock and was stopped before it started; it never ran. The rebuilds in §2 are the second attempt, in the slot form. The head's rebuild waited about 26 minutes for a heavy-job slot.
   - **What it means:** each reported rebuild ran to its end with exit 0. The waits change no figure.
5. **There was no supplementary tree-code run.** W2-86's tree-code head is shown beside these figures for reference only. It is not like for like with this ticket's control or head.
6. **The head clone is at `b652fc96d2b5`,** before the test designer's README fix (`f57fa0cdf694`, merged as `a53650525fd8`). The fix changes only `tests/acceptance/W2-91/README.md` (one line).
   - **What it means:** the measured tree carries the earlier README. No figure depends on it.

## 8. How to repeat it

Follow W2-61's §8, as W2-86's §8 adapted it, with these changes:

1. **Two clones by exact path,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, left detached:
   - `/home/usain/gov-os-runs/W2-91/head` at `b652fc96d2b5`;
   - `/home/usain/gov-os-runs/W2-91/base` at `f46b96537d74`. The base clone is also the measure's own clone.
2. **The stores,** built by the pinned gov in each clone, with embeddings, after the disk gate. Run the rebuild through `tools/rebuild_slot.sh`, which takes a heavy-job slot and the clone's lock (DEC-1001 (d)), with `GOV_REBUILD_PYTHON=/home/usain/.local/share/gov-os/pin-5c401220/bin/python` and with `PYTHONPATH` and `GOV_TICKET` unset.
   - Record the rebuild's `digest` and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db`.
   - Count the chunks with vectors per namespace of the head's path map in each store, read-only.
3. **The measure:** run the control first, then the head with `--compare` set to the control's record:

   ```
   env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-91/base/src python3 -m gov.retrieval.measure memory-retrieval \
     --root /home/usain/gov-os-runs/W2-91/<base|head> --sets-root /home/usain/gov-os-runs/W2-91/base --part visible \
     --gov /home/usain/.local/share/gov-os/pin-5c401220/bin/gov --out /home/usain/gov-os-runs/W2-91/records --json [--compare <the control's record>]
   ```

   The budgets are the measure's defaults: `--batch-size 10 --bundle-budget 6000 --stack-budget 24000`.
4. **Never `--part hidden`.**
