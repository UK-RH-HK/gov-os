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
- **The indexer reads `embedding_policy` only.** The line numbers are those of the code at the D-4b merge `19afc18f3f19` (§9); `w2/integrate`'s changes to `src/` moved them, and the reads are the same. `_wanted` in `src/gov/retrieval/semantic.py` (lines 285 to 299; the read is at line 293) embeds a file's chunks when every namespace the file matches says `embedded`. Two other places read the field, and neither reads `sensitivity` or `export_policy`:
  - `src/gov/rebuild/command.py:36`, for the warning given when no namespace is embedded;
  - `src/gov/adopt/stages.py:240` to `248`, which checks that the value is one of the two.
- **Nothing in `src/` reads the values of `sensitivity` or `export_policy`.** The two names appear only:
  - as required field names in `src/gov/config/path_map_schema.py:14-15`;
  - as text fields in `template/governance/kernel/schemas/path-map.schema.json:164, 178, 181`;
  - as literal values in a sample namespace that `src/gov/retrieval/retrieve_check.py:145, 148` writes.
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

## 9. D-4b: the merge of `w2/integrate`, the rebuild and the verification (2026-11-03)

Under DEC-1055 (2) the ticket lands as built: its embedding scope is not narrowed here. Written by the D-4b engineer (CTO session 33b3628c).

**Verified on:** the merge commit `19afc18f3f19` (`git merge --no-ff w2/integrate` at `23625eb2aebe` into `w2/W2-91` at `55b47e075b3b`). The merge was clean. The ticket's `allowed_paths` follow integrate (`8562ae79`, W2-86's acceptance file no longer listed). The path map differs from integrate's only by this ticket's change (`b652fc96d2b5`). The only commit after it before the runs is `50de449610ed`: §7's code citations moved to the merged code's line numbers, with the same reads.

### The rebuild

- **The command:** `flock /tmp/gov-os-d4b-rebuild.lock bash .gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh ~/gov-os-worktrees/W2-91 --seed`, run with `PYTHONPATH` set to the tree's `src/`.
- **The times:** 15:38:30 to 15:41:32 UTC, 182 s in all (the rebuild's own `total_s` is 125.1, with `semantic_s` 99.9).
- **The result:** exit 0. `lexical`, `semantic` and `codeintel` were each `recreated`. The seed was `none`, because `governance/project/rebuild.yaml` names no `integration_store`. The secrets scan was off by configuration (DEC-1045).
- **The digest:** `f244c6ac6f6b8924041eb77bcc9756468cefbb45025aa2d5c1981225df25dbf7`.
- **The store's sha256:** `.gov-runtime/store.db` is `2fd110a2f5ea60aa586156afde15d047c2ee575f4a301675c180c04687f4a752`.

### The vectors per namespace at the merge, from the rebuilt store

Counted read-only and judged by the merged path map, with the indexer's own matcher.

| Namespace | `embedding_policy` | Tracked files | Chunks | Chunks with vectors | Files with vectors |
|---|---|---|---|---|---|
| `root-files` | embedded | 8 | 26 | **26** | **8** |
| `project-overlay` (`governance/**`) | embedded | 240 | 4,966 | **4,966** | **240** |
| `carried-schemas` (`schemas/**`) | embedded | 5 | 31 | **31** | **5** |
| `carried-code` (`cli/**`) | not embedded | 0 | 0 | 0 | 0 |
| `agent-settings` (`.claude/**`, `.rulesync/**`) | not embedded | 88 | 1,240 | 0 | 0 |
| `fixtures` (`fixtures/**`) | not embedded | 78 | 0 | 0 | 0 |
| `kernel-adapter-copies` (`template/.rulesync/**`) | not embedded | 44 | 529 | 0 | 0 |
| `kernel-vendored` | not embedded | 30 | 323 | 0 | 0 |
| `ci` | not embedded | 1 | 5 | 0 | 0 |
| `tickets` | embedded | 193 | 1,006 | 1,006 | 193 |
| `docs` | embedded | 885 | 14,580 | 14,580 | 883 |
| `kernel-template` | embedded | 93 | 411 | 411 | 93 |
| `gov-source` | embedded | 142 | 3,010 | 3,010 | 136 |
| `tests` | embedded | 1,279 | 38,817 | 38,817 | 1,244 |
| **The whole store** | | | 64,944 | 62,847 | |

- **The three newly embedded sets:** every tracked file in them has vectors (8 of 8, 240 of 240 and 5 of 5). `governance/**` grew from 166 files to 240 with the merge, and every one of them is in `project-overlay` alone.
- **What stays out:** every stay-out set holds 0 chunks with vectors.
- **Each tracked path matches exactly one namespace.**

### The acceptance run: `gov accept W2-91 --json`, through `heavy_slot.sh`

| | success-1 | success-2 | success-3 | success-4 | success-5 | failure-1 | failure-2 | failure-3 | Totals |
|---|---|---|---|---|---|---|---|---|---|
| At the merge, `19afc18f3f19` and `50de449610ed` | **fail** (1 passed, 1 failed) | pass (6) | **fail** (3 passed, 1 failed) | pass (5) | pass (2) | pass (6) | **fail** (3 passed, 1 failed) | pass (5) | 17 passed, 2 failed |
| The branch head before the merge, `55b47e075b3b`, in a clone, the same day | **fail** (1, 1) | pass (6) | **fail** (3, 1) | pass (5) | pass (2) | pass (6) | **fail** (3, 1) | pass (5) | 17 passed, 2 failed |
| The lead's run at `160439f136b4`, 2026-11-02 09:33 | pass (2) | pass (6) | pass (4) | pass (5) | pass (2) | pass (6) | pass (4) | pass (5) | 19 passed, 0 failed |

- **The same two tests fail at the head before the merge,** a tree identical to the lead's passing run apart from one checkpoint file. So the merge did not cause them. Something outside the tree changed between 2026-11-02 09:33 and today.
- **What the engineer ruled out, without reading the tests:**
  - the rebuilt store: the result was the same during the rebuild, after it, and in a clone with no store;
  - `GOV_TICKET` and `GOV_ROLE`: the same unset, set to this ticket, or inherited;
  - the `gov` on `PATH`: the same with pins `5c401220`, `a7182f6c` and `9894b0cf`;
  - the interpreter: the same under `/usr/bin/python3` and under the pins' own Pythons;
  - this record's commits: every commit it cites still resolves;
  - the namespaces: every tracked path under the three sets is embedded, by the indexer's rule.
- **One machine-level change in that window:** ACT-D8's `git reflog expire --expire=now --all` and `git gc --prune=now` on the shared object store, at about 15:35 today. It is not shown to be the cause.
- **The two reds are unresolved here:** the engineer never reads `tests/acceptance/W2-91/`.

### The scoped run: `select_tests.py`'s selection, through `heavy_slot.sh`

- **The selection:** `select_tests.py <tree> W2-91 DAEO-a3u2` gives `scope: scoped`, 98 targets, with `governance/project/path-map.yaml` in the shared core.
- **The command:** `pytest tests -n auto` with its `pytest_options`, `--timeout=900`, `-p no:cacheprovider` and `-o tmp_path_retention_policy=failed`, in `close_build.py`'s form: a parallel phase with the serial-only plugin, then the serial entries.
- **The parallel phase:** 5,873 passed, 9 failed, 8 skipped, in 424.6 s by pytest's count (15:46 to 15:54 UTC). The 9 failures:
  - **2 are this ticket's acceptance tests,** the two above.
  - **2 are W1-19's,** `test_w1_19_embedding_policy::test_only_the_namespace_that_says_embedded_reaches_the_vectors` and `test_w1_19_semantic_index::test_no_text_the_secret_filter_refuses_is_embedded_or_returned`. Each passes when re-run alone in this tree: a red under load, not this change.
  - **5 are not this ticket's.** They fail the same way when re-run alone at `w2/integrate`'s own head `23625eb2aebe`:
    - `W1-06/test_w1_06_install_approvals::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool`: the tool registry's `gov` entry cites DEC-1052, which does not name the tool;
    - `W2-59/test_w2_59_hook_lines::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src[preToolUse[0]]`;
    - `W2-59/test_w2_59_hook_lines_worker_env`'s three `preToolUse[0]` cases: the hook line now runs `.claude/hooks/pretooluse.py`, which the test's planted project lacks.
- **The serial phase:** 33 entries, 75 tests, 75 passed, 0 failed, in 681 s (to 16:05 UTC).
- **The whole scoped run:** 1,140 s, of which the parallel phase is 459 s including its wait for a slot. 5,965 tests: 5,948 passed, 9 failed, 8 skipped. Apart from the two unresolved `gov accept` reds above, none of the failures is this change's.

### Per KPI line

| KPI line | How it is verified | Command | Result | Commit |
|---|---|---|---|---|
| S1: the root files, `governance/**` and `schemas/**` have vectors; the counts recorded | the rebuilt store's count (above); the builder test `test_the_root_files_the_overlay_and_schemas_are_embedded`; `gov accept` success-1 | `rebuild_slot.sh … --seed`; the read-only count; `pytest tests/unit/retrieval/test_w2_91_full_embeddings.py`; `gov accept W2-91 --json` | the store: 26, 4,966 and 31 chunks with vectors, every file in each set; the builder test passes; **`gov accept` fails 1 of 2, also before the merge (unresolved, above)** | `19afc18f3f19` / `50de449610ed` |
| S2: what stays out stays out; `schemas/**` has its own namespace | `gov accept` success-2; the store's count; the builder test `test_what_stays_out_stays_out` | as above | pass (6 of 6); 0 vectors in each stay-out set; passes | `50de449610ed` |
| S3: the overlay stays restricted; the indexer reads `embedding_policy` only | the code reading in §7; the builder test `test_the_overlay_stays_restricted`; `gov accept` success-3 | `grep` over `src/`; as above | `restricted` and `denied` at the head and the base; the builder test passes; **`gov accept` fails 1 of 4, also before the merge (unresolved, above)** | `50de449610ed` |
| S4: the two values only; each tracked path in exactly one namespace; the indexer's code unchanged | `gov accept` success-4; the builder tests `test_only_the_two_values` and `test_every_tracked_path_is_in_one_namespace`; `git diff --stat 23625eb2aebe 19afc18f3f19 -- src` | as above | pass (5 of 5); both pass; the diff is empty | `50de449610ed` |
| S5: nothing else moves | `gov accept` success-5; the builder test `test_nothing_else_moves` | as above | pass (2 of 2); passes | `50de449610ed` |
| S6: W2-61's measure, base and head, both figures together | measure: D-4b measure 1 (the CTO runs the measures); the figures of `b652fc96d2b5` are in §4 and §5 | — | not run here | — |
| F1: no file under `fixtures/`, `.claude/`, `.rulesync/` or `cli/` embedded | `gov accept` failure-1; the store's count | as above | pass (6 of 6); 0 vectors in each | `50de449610ed` |
| F2: the overlay's sensitivity or export policy not changed, the overlay not exported | `gov accept` failure-2; the builder test `test_the_overlay_stays_restricted`; §7 | as above | **fails 1 of 4, also before the merge (unresolved, above)**; the builder test passes | `50de449610ed` |
| F3: no third value; no tracked path in no namespace or in two | `gov accept` failure-3; the builder tests as for S4 | as above | pass (5 of 5); both pass | `50de449610ed` |
| F4: no figure without the other; the hidden half neither read nor run | measure: D-4b measure 1 | — | this record reads no hidden file, and its figures in §4 stand together | — |

The builder test file `tests/unit/retrieval/test_w2_91_full_embeddings.py` gives 6 passed at `50de449610ed`.
