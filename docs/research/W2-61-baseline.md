# W2-61 baseline: the standing 20-question memory measure, visible half

- **Ticket:** DAEO-iw1f (W2-61), profile STANDARD. Written by the engineer from the outputs of the baseline its lead ran.
- **Date:** 2026-10-29.
- **Sources:** DEC-941 item 1.2 (the baseline today, on the pinned stores), DEC-833 items 1 to 3 (both figures, always together), DEC-860 (retrieval in batches, ranked and stacked), DEC-828 items 3 and 4 (the split), DEC-877 (a bare `gov` is the pinned gov); the ticket's KPI line 7.

This record holds scores only: ids, counts, ranks, digests and pass or fail. It quotes no question's gold answer and no text of a retrieved item.

## 1. What was measured, and where

- **The tree measured:** a clone at commit `23079f92a6fa` (this ticket's base), `/home/usain/gov-os-runs/W2-61/repo`, made today with `git clone --no-hardlinks` of the main repository and left detached.
- **The retriever: the pinned gov.** `/home/usain/.local/bin/gov`, whose first line is `#!/home/usain/.local/share/gov-os/pin-5c401220/bin/python`.
  - **Version:** `gov --version` says `gov 0.1.0 (commit unknown)`.
  - **Commit:** `5c40122014da`, named by the pin's folder (`~/.local/share/gov-os/pin-5c401220/`; the 12 digits from the repository's history): the second pin, which carries W2-58's refusal (d).
  - **`gov.__file__` of the retrieving process** (each run's `retriever.gov_file`): `/home/usain/.local/share/gov-os/pin-5c401220/lib/python3.12/site-packages/gov/__init__.py`. The executable each run names: `/home/usain/.local/share/gov-os/pin-5c401220/bin/gov`.
- **The measure:** this worktree's `src/gov/retrieval/measure.py` at commit `8d09eb40da8b`, run with `PYTHONPATH` set to this worktree's `src/` (DEC-732). It removes `PYTHONPATH` and `GOV_TICKET` from the process that retrieves, so the retrieval is the pinned gov's own code.
- **The set:** `memory-retrieval`, the visible half only: lens B's 20 questions, `fixtures/evaluation/memory-retrieval/visible/q01.yaml` to `q20.yaml`.
- **The budgets:** `--batch-size 10`, `--bundle-budget 6000`, `--stack-budget 24000`. At radius 0 and 1, one call with batch size 10 gathers 20 items, the same 20-item bundle lens B measured. So "in the first five" and "in the bundle" (an item of the first call) compare with lens B's.

## 2. The stores' fingerprint

The clone's stores were built in the clone by the pinned gov: a bare `gov`, with no `PYTHONPATH` and no `GOV_TICKET` (DEC-877), as `flock /tmp/gov-os-rebuild.lock gov rebuild --json`, after the load and disk gates.

| | Rebuild 1 | Rebuild 2 |
|---|---|---|
| Start and end (UTC) | 20:22:26 to 21:07:20 (44 min 54 s) | 22:03:02 to 22:10:15 (7 min 13 s) |
| Gate at the start: disk; 1-, 5- and 15-minute load | 877 GiB and 64,915,633 inodes free; 10.15, 34.45, 53.93 | 873 GiB and 64,463,467 inodes free; 19.52, 32.33, 46.54 |
| Exit code | 0 | 0 |
| Stores (`lexical`, `semantic`, `codeintel`) | each `recreated` | each `recreated` |
| Lexical timing (`timing.lexical_s`) | 141.8 s | 0.4 s |
| Files compacted | `store.db`, `codeintel/home/_config.db`, `codeintel/home/code.db` | the same three and `query-vector-cache.db` |

**The digest each rebuild records** (`result.digest` in `rebuild-1.json` and `rebuild-2.json`; `result.store.digest` is the same value, with no invalid entries):

- the stores' fingerprint, rebuild 1's digest (`rebuild-1.json`): `5550b460ec6e3956ffa86f88f9217534cc6f12ffd37c39321be2d8cdea106e6c`
- the stores' fingerprint, rebuild 2's digest (`rebuild-2.json`): `5550b460ec6e3956ffa86f88f9217534cc6f12ffd37c39321be2d8cdea106e6c` (the same)

**The sha256 of each store file after each rebuild** (`stores-after-rebuild-1.sha256`, `stores-after-rebuild-2.sha256`):

| Store file | sha256 after rebuild 1 | sha256 after rebuild 2 |
|---|---|---|
| `.gov-runtime/store.db`, sha256 | `a9e2742e9e8f807092d429a68c202d56588b00a83ee1c82cb30310537b8a6024` | `9f33fae69333165554bac7139acfce3d399cdcaf32d3c9f963a741f6fc84c012` |
| `.gov-runtime/codeintel/home/code.db`, sha256 | `1e270a410de4ebe870785f6254f6657bdae5e7a275e0b04b374021c3ddecee14` | `528ee3144a38b58715df34a27547da3690203aa12c6b2380f8fa131903e4741f` |
| `.gov-runtime/codeintel/home/_config.db`, sha256 | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` (the same) |

So the digest the rebuild records is the same after both rebuilds, while the bytes of `store.db` and `code.db` differ. `_config.db` is byte-identical.

## 3. The runs

| Run | What | Start and end (UTC) | Exit | Record (`--out`) |
|---|---|---|---|---|
| 1 | after rebuild 1 | 21:07:43 to 21:26:14 | 0 | `measure-memory-retrieval-visible-20261029T212614400969Z.json` |
| 2 | the repeat: the same index, compared with run 1 | 21:27:25 to 21:55:38 | 0 | `measure-memory-retrieval-visible-20261029T215538826335Z.json` |
| 3 | after rebuild 2, compared with run 1 and run 2 | 22:10:34 to 22:21:52 | 0 | `measure-memory-retrieval-visible-20261029T222152985301Z.json` |

Each run's stderr was empty. A comparison covers five fields per question: hit@5, in the bundle, full evidence, the first gold rank and the stacked digest (the paths and line spans of the stacked context, in order).

## 4. The totals: both figures together

| Run | hit@5 against CAP-10's floor of 85 | Full evidence against the owner's target of 99 % | In the bundle |
|---|---|---|---|
| 1 | 8 of 20 (40.0 %), floor 85: short by 45 points | 12 of 20 (60.0 %), target 99 %: short by 39 points | 14 of 20 |
| 2 | 8 of 20 (40.0 %), floor 85 | 12 of 20 (60.0 %), target 99 % | 14 of 20 |
| 3 | 8 of 20 (40.0 %), floor 85 | 12 of 20 (60.0 %), target 99 % | 14 of 20 |

**Repeatability:** run 2 is the same as run 1 for 20 of 20 questions, and run 3 is the same as run 1 and as run 2 for 20 of 20, in all five compared fields.

## 5. Per question, visible half

"First gold rank" is the rank, in the stacked context, of the first item that matches a gold source. "In the bundle" means an item of the first call matches one. "Full evidence" is the gold entries matched by the stacked context, of those the question needs. The figures are run 1's; the last two columns compare.

| Q | hit@5 | First gold rank | In the bundle | Full evidence (found of needed) | Calls | Repeat (run 2 against run 1) | After the rebuild (run 3) | Lens B's first gold rank (Table 2) |
|---|---|---|---|---|---|---|---|---|
| Q01 | yes | 1 | yes | yes (1 of 1) | 5 | same | same | 1 |
| Q02 | yes | 1 | yes | yes (1 of 1) | 2 | same | same | 1 |
| Q03 | yes | 4 | yes | yes (1 of 1) | 2 | same | same | 5 |
| Q04 | yes | 3 | yes | yes (1 of 1) | 2 | same | same | 3 |
| Q05 | yes | 2 | yes | yes (1 of 1) | 2 | same | same | 1 |
| Q06 | no | 9 | yes | yes (2 of 2) | 2 | same | same | 6 |
| Q07 | no | 12 | yes | yes (1 of 1) | 5 | same | same | 12 |
| Q08 | no | 9 | yes | yes (1 of 1) | 2 | same | same | 6 |
| Q09 | no | 60 | no | yes (1 of 1) | 4 | same | same | 5 |
| Q10 | no | 25 | no | no (1 of 2) | 2 | same | same | none (no caller found) |
| Q11 | yes | 4 | yes | no (1 of 2) | 2 | same | same | 3 |
| Q12 | yes | 2 | yes | yes (1 of 1) | 2 | same | same | 2 |
| Q13 | no | 6 | yes | no (1 of 2) | 2 | same | same | 4 |
| Q14 | no | 16 | yes | no (7 of 9) | 5 | same | same | 9 |
| Q15 | yes | 4 | yes | yes (1 of 1) | 2 | same | same | 1 |
| Q16 | no | 7 | yes | yes (1 of 1) | 2 | same | same | 4 |
| Q17 | no | 21 | no | no (1 of 2) | 2 | same | same | 1 |
| Q18 | no | none | no | no (0 of 2) | 2 | same | same | none (no governing source in the bundle) |
| Q19 | no | none | no | no (0 of 1) | 2 | same | same | none (MR-3 22nd, past the 20 gathered) |
| Q20 | no | 21 | no | no (1 of 2) | 2 | same | same | 3 |

**Causes the outputs or the visible files show** (no other cause is guessed):

- **Q18:** one of its two needed pieces, the PreCompact hook's call (`template/governance/kernel/hooks/precompact.py`), is only under `template/`, which lens B's F6 found is not embedded. Its other piece (DEC-444 or `record.py`) was not found either.
- **Q19:** two of its three alternatives are role files under `template/` (not embedded, lens B's F6). The third, the charter's MR-3, lens B found 22nd on the semantic route, past the 20 gathered.
- **Q17 and Q20:** tests and assessment files take the top ranks. In the lead's direct `gov retrieve` bundles in the clone after run 1, the first five items were:
  - Q17 (`spot-q17.json`): `tests/acceptance/W1-41/test_w1_41_embedding_policy.py`, `docs/DECISION_REGISTER.md` (DEC-941), `tests/unit/rebuild/test_no_embeddings.py`, `tests/unit/semantic/test_semantic.py`, `src/gov/rebuild/command.py`;
  - Q20 (`spot-q20.json`): `tests/acceptance/W1-29/test_session_hooks.py`, `tests/acceptance/W1-49/README.md`, `docs/assessment/2026-10/SYNTHESIS.md`, `docs/assessment/2026-10/E-roles-context.md`, `docs/assessment/2026-10/SYNTHESIS.md`.
- **Q09:** the gold source is not in the first call, but the stacked context of 4 calls holds it (rank 60), so its evidence is full.

## 6. Lens B's figures beside these

| | Lens B, at `fecb870c9fde` | This baseline, at `23079f92a6fa` |
|---|---|---|
| Governing source in the first five (hit@5), against CAP-10's floor of 85 | 13 of 20 (65 %) | 8 of 20 (40.0 %) |
| Full evidence, against the owner's target of 99 % | never measured | 12 of 20 (60.0 %) |
| Governing source in the bundle | 17 of 20 | 14 of 20 |

- **In the first five for lens B, not here:** Q09 (5 to 60), Q13 (4 to 6), Q16 (4 to 7), Q17 (1 to 21), Q20 (3 to 21). None is in the first five here and not for lens B.
- **In the bundle for lens B, not here:** Q09, Q17, Q20. Q10's first caller is found here at rank 25, in the second call; lens B found none.
- **Ranks that moved inside the bundle:** Q03 (5 to 4), Q05 (1 to 2), Q06 (6 to 9), Q08 (6 to 9), Q11 (3 to 4), Q14 (9 to 16), Q15 (1 to 4). The rest have lens B's rank, or none in both (Q18, Q19).

**What differs between the two measurements:**

- **The commit:** lens B measured a clone at `fecb870c9fde`; this baseline a clone at `23079f92a6fa`.
- **The code:** lens B ran the clone's own `src` at `fecb870c9fde` (`PYTHONPATH` set to it). This baseline runs the pinned gov at `5c40122014da` on a tree at `23079f92a6fa`.
- **The index:** it now holds lens B's own report and the later assessment files (`docs/assessment/2026-10/`), which lens B's index did not. Two of them are in Q20's first five above.
- **The gold:** here it is the visible files' sources, read from lens B's Table 2 and stated in each file's comments (alternatives of one entry, or one entry per needed piece). An item from lens B's report or from `fixtures/evaluation/` is never a hit.
- **The scoring:** lens B judged one bundle by hand. The measure scores a stacked context across calls, by path and line overlap.

## 7. Hidden half (W2-61h): scores

*Empty until W2-61h's questions exist.*

The orchestrator, which no set measures, fills this place: it runs the same measure on the hidden half and records the scores only (ids, counts, ranks, pass or fail; never a question or an answer), beside the visible baseline above (W2-61h's ticket, DAEO-h2k3). The engineer of this ticket is measured by the set and writes no hidden score.

| Run | hit@5 against CAP-10's floor of 85 | Full evidence against the owner's target of 99 % | In the bundle |
|---|---|---|---|
| (empty) | | | |

## 8. How to repeat it

The same measure is re-run after each ticket of block B's chain (W2-03, W2-55, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a), beside this baseline (DEC-941; KPI line 7).

1. **The clone:** `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <clone>`, detached at the commit to measure.
2. **The stores,** by the pinned gov, in the clone, after the load and disk gates: `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock gov rebuild --json`. Record its `digest` and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db`.
3. **The measure,** from the clone, with the measure's code under test:

   ```
   env -u GOV_TICKET PYTHONPATH=<worktree>/src python3 -m gov.retrieval.measure memory-retrieval \
     --root <clone> --sets-root <worktree> --part visible --gov /home/usain/.local/bin/gov \
     --out <runs>/records --json [--compare <earlier record>]...
   ```

   The budgets are the measure's defaults: `--batch-size 10 --bundle-budget 6000 --stack-budget 24000`.
4. **Repeatability:** run it twice on the same index (the second with `--compare` the first record), rebuild, and run it again with `--compare` both earlier records.
5. **The hidden half:** the orchestrator only, with `--part hidden`, writing scores only into section 7.
