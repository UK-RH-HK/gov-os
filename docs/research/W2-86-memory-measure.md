# W2-86 memory measure: W2-61's 20-question measure after the kernel template is embedded, visible half

- **Ticket:** DAEO-jsg1 (W2-86), profile STANDARD. Written by the engineer from the outputs of the measure its lead ran.
- **Date:** 2026-11-01.
- **Sources:** DEC-952 (memory's quick wins, each re-measured with W2-61's measure), DEC-941 item 1 (the measure re-run after each ticket of the memory chain, beside W2-61's baseline), DEC-833 item 3 (both figures, always together), DEC-860 (retrieval in batches, ranked and stacked), DEC-877 (a bare `gov` is the pinned gov), DEC-957 (memory's target of 95 %), CAP-10 (the floor of 85 for hit@5); the ticket's KPI lines success 1, 4 and 5 and failure 5. The figures beside these are `docs/research/W2-61-baseline.md` and `docs/research/W2-87-memory-measure.md`.

This record holds scores only: ids, counts, ranks, digests and pass or fail. It quotes no question's text, no gold answer and no text of a retrieved item. The hidden half of the set was neither read nor run.

## 1. What was measured, and where

- **The three clones,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, left detached:

  | Clone | Commit | What it is |
  |---|---|---|
  | `/home/usain/gov-os-runs/W2-86/head` | `338c14fa6475` | the branch head: the path map's namespace block and the ticket's tests; the tree measured as the head |
  | `/home/usain/gov-os-runs/W2-86/base` | `9dc5288161c4` | the ticket's base; the tree measured as the control |
  | `/home/usain/gov-os-runs/W2-86/measure` | `bf8ae585b827` | `w2/integrate`'s head when cloned: the measure's code and the visible set only |

- **The code is the same at base and head:** `git diff --stat 9dc5288161c4 338c14fa6475 -- src` is empty. Only the path map (`governance/project/path-map.yaml`) and the ticket's new tests differ.
- **The retriever: the pinned gov.** `/home/usain/.local/bin/gov`, whose first line is `#!/home/usain/.local/share/gov-os/pin-5c401220/bin/python`.
  - **Version:** `gov --version` says `gov 0.1.0 (commit unknown)`.
  - **Commit:** `5c40122014da`, named by the pin's folder (`pin-5c401220`), as W2-61's record names it.
  - **Each pinned run's `retriever.gov_file`:** `/home/usain/.local/share/gov-os/pin-5c401220/lib/python3.12/site-packages/gov/__init__.py`; the executable each names: `/home/usain/.local/share/gov-os/pin-5c401220/bin/gov`.
- **The supplementary run's retriever** (deviation 2, §7): the head tree's own code, through a launcher `gov-wt` (the pinned launcher's body under `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`, in the lead's session scratchpad). Its `retriever.gov_file`: `/home/usain/gov-os-worktrees/W2-86/src/gov/__init__.py`; version `gov 0.1.0 (commit 338c14fa6475)`; root `/home/usain/gov-os-worktrees/W2-86`, commit `338c14fa6475`.
- **The measure:** `src/gov/retrieval/measure.py` from the measure clone (last changed at `289b9314a763`), run with `PYTHONPATH` set to that clone's `src/` and `GOV_TICKET` removed; the retrieving process is the `--gov` given.
- **The set:** `memory-retrieval`, the visible half only: the 20 questions Q01 to Q20, read from the measure clone (`--sets-root`); the visible set last changed at `80c96c44bdcf`. The hidden half was neither read nor run.
- **The budgets:** the measure's defaults, `--batch-size 10`, `--bundle-budget 6000`, `--stack-budget 24000` (each run's `budget`), as in W2-61's baseline and W2-87's measure.

## 2. The stores' fingerprint

Each clone's stores were built in that clone by the pinned gov, with embeddings (never `--no-embeddings`), as `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock gov rebuild --json`, after the load and disk gates. Times UTC.

| | base (control) | head |
|---|---|---|
| Gate passed | 22:10:56 on 2026-10-31 | 00:03:03 on 2026-11-01 |
| Gate at the start: disk; 1-, 5- and 15-minute load | 868 GiB and 65,149,800 inodes free; 4.21, 5.29, 8.53 | 863 GiB and 64,723,716 inodes free; 17.92, 33.43, 50.56 |
| Lock held from | about 22:34 (another session's rebuild held it before; deviation 3) | 00:03 |
| End | 23:40:39 | 00:44:46 |
| Exit code | 0 (`ok: true`) | 0 (`ok: true`) |
| Stores (`lexical`, `semantic`, `codeintel`) | each `recreated` | each `recreated` |
| Lexical timing (`timing.lexical_s`) | 311.0 s | 370.8 s |
| Files compacted | `store.db`, `codeintel/home/_config.db`, `codeintel/home/code.db` | the same three |

**The digest each rebuild records** (`result.digest`; `result.store.digest` is the same value, with no invalid entries):

- base (control): `7f2e1e54ccdf86711ea8bd9bbd1b2918730c09d293350170ca2b07042d255eb9`
- head: `aff71072671894bafe99db13ee6658bccdffd8858561c278f5e3a5efbd1e4bd3`

**The sha256 of each store file after the rebuild:**

| Store file | base (control) | head |
|---|---|---|
| `.gov-runtime/store.db` | `691a60b0cf8812c6006605f317032e36733c72cc81fd59baa06179c1acd9d012` | `99ad51cb5f774d1d77a4f827560503625454b128890a8eba9462817ffb62d382` |
| `.gov-runtime/codeintel/home/code.db` | `64b74376194fbebf87550b57361fb7d544fbf9d5412b472dc161e0f99d1373e9` | `b1a06534a5d113d31e2f00d9b457216c5e96cece9d365aa6d67f6928eb89ebad` |
| `.gov-runtime/codeintel/home/_config.db` | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` | the same (also W2-61's and W2-87's) |

The two digests differ because the record graph differs (the head holds the ticket's commits). The digest covers the record graph only (`src/gov/store/loader.py:305`), not the vectors, so the vector set is the figure compared (§6).

**The supplementary run's store** (deviation 2): this worktree's own store, built by its own code at `338c14fa6475`, digest `5bbb7249412e3b79d63577f9ac951146caa6d1e5356e3fd0aa0f9319ea5bd8a9`. It is identical to the head clone's store in its 2,761 lexical files and their blobs and in its 51,114 chunks with vectors, path by path.

## 3. The runs

Each run measured the visible half. Times UTC; the control's run began on 2026-10-31, the others on 2026-11-01.

| Run | Tree | Retriever (`--gov`) | Start | End | Length | Exit | stderr | Record | `--compare` |
|---|---|---|---|---|---|---|---|---|---|
| control | base `9dc5288161c4` | pinned gov | 23:40:51 | 00:01:30 | 1,239 s | 0 | empty | `records/measure-memory-retrieval-visible-20261101T000130633794Z.json` | — |
| head | head `338c14fa6475` | pinned gov | 00:44:54 | 00:58:37 | 823 s | 0 | empty | `records/measure-memory-retrieval-visible-20261101T005837664244Z.json` | the control's record |
| head, tree code (supplementary) | this worktree at `338c14fa6475` | `gov-wt` (the tree's own code) | 01:38:35 | 02:16:04 | 2,249 s | 0 | empty | `records-tree/measure-memory-retrieval-visible-20261101T021603839200Z.json` | — |

The records are under `/home/usain/gov-os-runs/W2-86/`. A comparison covers five fields per question: hit@5, in the bundle, full evidence, the first gold rank and the stacked digest (the paths and line spans of the stacked context, in order).

## 4. The totals: both figures together

| | hit@5, against CAP-10's floor of 85 and the owner's target of 95 % (DEC-957) | Full evidence, against the owner's target of 99 % | In the bundle |
|---|---|---|---|
| W2-61 baseline (`23079f92a6fa`, pinned gov, pinned stores) | 8 of 20 (40 %), short of 85 by 45 points, of 95 by 55 | 12 of 20 (60 %), short by 39 points | 14 of 20 |
| W2-87 head (`cffef92c8534`, W2-87's own code) | 11 of 20 (55 %), short of 85 by 30 points, of 95 by 40 | 11 of 20 (55 %), short by 44 points | 15 of 20 |
| control (`9dc5288161c4`, pinned gov) | 7 of 20 (35 %), short of 85 by 50 points, of 95 by 60 | 11 of 20 (55 %), short by 44 points | 13 of 20 |
| **head (`338c14fa6475`, pinned gov)** | **7 of 20 (35 %), short of 85 by 50 points, of 95 by 60** | **11 of 20 (55 %), short by 44 points** | **13 of 20** |
| head, tree code (supplementary, `338c14fa6475`) | 11 of 20 (55 %), short of 85 by 30 points, of 95 by 40 | 11 of 20 (55 %), short by 44 points | 15 of 20 |

**Head against control** (the like-for-like pair, the same retriever and code): hit@5 7 → 7 of 20, full evidence 11 → 11 of 20, in the bundle 13 → 13 of 20. The change moved neither figure on this set.

## 5. Per question, visible half

Each cell gives, in order: hit@5, first gold rank, in the bundle, full evidence (pieces found of needed). "First gold rank" is the rank, in the stacked context, of the first item that matches a gold source; "in the bundle" means an item of the first call matches one. W2-61's baseline is its §5; W2-87's head is its §5. The last column is the head run's `--compare` against the control.

| Q | W2-61 baseline | W2-87 head | control (pinned) | head (pinned) | head, tree code (supplementary) | Head against control |
|---|---|---|---|---|---|---|
| Q01 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | same |
| Q02 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q03 | yes, 4, yes, yes (1/1) | yes, 2, yes, yes (1/1) | no, 7, yes, yes (1/1) | no, 7, yes, yes (1/1) | yes, 2, yes, yes (1/1) | same |
| Q04 | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q05 | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q06 | no, 9, yes, yes (2/2) | no, 7, yes, yes (2/2) | no, 8, yes, yes (2/2) | no, 8, yes, yes (2/2) | no, 7, yes, yes (2/2) | same |
| Q07 | no, 12, yes, yes (1/1) | no, 12, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | stacked digest |
| Q08 | no, 9, yes, yes (1/1) | no, 11, yes, yes (1/1) | no, 9, yes, yes (1/1) | no, 9, yes, yes (1/1) | no, 11, yes, yes (1/1) | same |
| Q09 | no, 60, no, yes (1/1) | no, 46, no, yes (1/1) | no, 59, no, yes (1/1) | no, 59, no, yes (1/1) | no, 44, no, yes (1/1) | same |
| Q10 | no, 25, no, no (1/2) | no, none, no, no (0/2) | no, 25, no, no (1/2) | no, 25, no, no (1/2) | no, none, no, no (0/2) | stacked digest |
| Q11 | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | same |
| Q12 | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q13 | no, 6, yes, no (1/2) | yes, 1, yes, no (1/2) | no, 6, yes, no (1/2) | no, 6, yes, no (1/2) | yes, 1, yes, no (1/2) | same |
| Q14 | no, 16, yes, no (7/9) | no, 17, yes, no (6/9) | no, 16, yes, no (3/9) | no, 16, yes, no (3/9) | no, 17, yes, no (4/9) | same |
| Q15 | yes, 4, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q16 | no, 7, yes, yes (1/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | stacked digest |
| Q17 | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | no, 21, no, no (1/2) | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | stacked digest |
| **Q18** | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | stacked digest |
| **Q19** | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | stacked digest |
| Q20 | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | no, 21, no, no (1/2) | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | same |

**What changed, control to head (pinned):** hit@5, in the bundle, full evidence, pieces found and first gold rank are the same for 20 of 20 questions. The stacked digest differs for 11 (Q02, Q04, Q05, Q07, Q10, Q12, Q15, Q16, Q17, Q18, Q19): newly embedded chunks enter the stacked context, none of them a gold piece. Calls per question are the same in all three runs (Q01 to Q20: 5, 2, 2, 2, 2, 3, 5, 2, 4, 2, 2, 2, 2, 5, 2, 2, 2, 2, 2, 2).

**The supplementary head (tree code) against W2-87's head:** the same totals (11, 11 and 15 of 20) and the same cells, but Q09 (first gold rank 44 here, 46 there) and Q14 (4 of 9 pieces here, 6 of 9 there).

**The control against W2-61's baseline** (the same pinned gov, a later tree and its stores): Q03 leaves the first five (4 → 7), Q16 loses its source (7 → none, 1 of 1 → 0 of 1), Q14's pieces fall (7 → 3 of 9), and Q06 (9 → 8), Q07 (12 → 6), Q09 (60 → 59) and Q15 (4 → 3) move inside the stacked context. So hit@5 8 → 7, full evidence 12 → 11 and in the bundle 14 → 13 of 20, as W2-87's §7 found for its own control (Q03 and Q16).

### Q18 and Q19

Both questions' governing sources are under `template/`, which W2-61's §5 named as the cause of their misses: Q18 needs 2 pieces, one of whose alternatives is the PreCompact hook (`template/governance/kernel/hooks/precompact.py`); Q19 needs 1 of three alternatives, the charter's MR-3 or one of two role files under `template/governance/kernel/roles/`. After the change those files have vectors (§6), and the stacked digest moved for both questions, so the kernel template's chunks now enter their stacked context. Neither figure moved: Q18 stays 0 of 2 and Q19 0 of 1, with no gold item ranked, in every run.

The lead's spot retrievals (`gov retrieve "<the question>" --json`, the first call's 20 items; paths and ranks only) show why:

- **Q18** (head, tree code): `precompact.py` is not among the 20. The 20 hold three register chunks (not the gold entry's lines), a contract chunk, two tickets, W1-29's and W1-49's tests and READMEs on the PreCompact hook (ranks 8, 11 to 16 and 18) and assessment reports. The hook's own file has vectors now (6 of 6 hook files, 90 of 90 chunks), but its chunks rank below the tests and READMEs that name it.
- **Q19** (head, pinned gov): the first 20 are tests, assessment reports and register chunks, with one template file (`template/governance/kernel/skills/test-design/SKILL.md`, rank 16) and no role file. With tree code: template files at rank 8 (that skill) and 19 (`template/governance/kernel/templates/brief-lead.md`), the master rule's own file `docs/contract/master-rules/MR-3.md` at 17 (not a gold alternative), and no role file and no charter chunk.

So the change makes the kernel template reachable, but for these two questions the governing chunk is outranked by tests, reports and other sources on the same subject. The remaining cause is ranking, not embedding.

## 6. The vectors

Each store opened read-only. A chunk is a row of `lexical_chunk`; it has a vector when `semantic_vector` holds its id.

| Group | Files | Chunks | Chunks with vectors, base | Chunks with vectors, head |
|---|---|---|---|---|
| `template/governance/kernel/roles/` | 6 | 19 | 0 | 19 (6 files) |
| `template/governance/kernel/hooks/` | 6 | 90 | 0 | 90 (6 files) |
| `template/governance/kernel/skills/` (all, `superpowers/` included) | 24 | 214 | 0 | 76 (10 files: the 9 kernel `SKILL.md` and `superpowers/vendored.yaml`) |
| `template/governance/kernel/vendor/` | 15 | 139 | 0 | 0 |
| `template/governance/kernel/skills/superpowers/<skill>/` | 14 | 138 | 0 | 0 |
| `template/governance/kernel/bin/` | 1 | 46 | 0 | 0 |
| `template/.rulesync/` | 44 | 529 | 0 | 0 |
| `template/` (all) | 167 | 1,262 | 0 | 410 (93 files) |
| The whole store | 2,632 base, 2,635 head (paths with chunks) | 55,591 base, 55,625 head | 50,672 | 51,114 |

- **The vector diff, base to head:** 96 paths gain vectors; none loses any. 93 are the kernel template's files: schemas 21, checks 20, templates 12, skills 10, hooks 6, roles 6, `openspec/schemas/feature-readiness/` 6, canaries 2, and one each of `.copier-answers.yml.jinja`, `.github/workflows/ci.yml.jinja`, `.gitignore`, `.gitleaks.toml`, `governance/kernel/launch/research-allowlist.yaml`, `governance/kernel/settings.json`, `governance/project/path-map.yaml`, `governance/project/test-map.yaml`, `lefthook.yml.jinja` and `openspec/config.yaml` (each under `template/`). The other 3 are the ticket's own new files: `tests/acceptance/W2-86/README.md`, `tests/acceptance/W2-86/test_w2_86_kernel_template_embedding.py` and `tests/unit/retrieval/test_w2_86_kernel_template_namespaces.py`. No path outside `template/` other than these 3 gains or loses a vector.
- **The vendored set has no vector** in either store: `vendor/`, `skills/superpowers/<skill>/`, `bin/` and `template/.rulesync/` hold 0 chunks with vectors, while `superpowers/vendored.yaml`, the kernel's own record, is embedded.
- **The lexical diff, base to head** (`lexical_file` blob by path): 4 files, `governance/project/path-map.yaml` (changed; its namespace is not embedded, so it gains no vector) and the 3 new files. Nothing else.
- **Why the vectors are the figure compared:** the record store's digest (§2) covers the record graph only (`src/gov/store/loader.py:305`), so it moves with the ticket's commits and says nothing about the vectors. The ticket's KPI 4 compares the vector set and the lexical index instead, and both differ only as above.

## 7. Deviations and what they mean

1. **The retriever is the pinned gov, `5c40122014da`,** as the brief and W2-61's §8 name it. It predates W2-87's authority order (code merged since), so the control and the head carry W2-61's ranking, not W2-87's.
   - **What it means:** the control (7, 11 and 13 of 20) is below W2-87's head (11, 11 and 15 of 20), and also 1 below W2-61's baseline on each figure, because the tree and its stores changed since `23079f92a6fa` (Q03 and Q16, §5). W2-87's figures were measured with W2-87's own code and are not like for like with the control or the head. The pair head against control isolates this ticket's data change, the retriever and the code being the same: it moved no figure.
2. **The supplementary head with tree code** gives the figure the brief expected the control to carry (W2-87's ranking): it equals W2-87's head on the totals. Its like-for-like control (the base with tree code, on stores built by tree code) was not run: the pinned gov's stores cannot be read by the tree's code (W2-87's §7 deviation 1), and the base's rebuild by tree code waited more than an hour behind three other sessions' rebuilds on the shared lock, under a load of 60 to 88, so the lead stopped it. The head with tree code used this worktree's store instead of the head clone's (the same files and vectors path by path, built by the same code at the same commit), because rebuilding the head clone too would have meant a second wait on the lock.
   - **What it means:** the supplementary run shows where the head stands with today's ranking, but it has no control of its own, so its difference from the pinned runs is the retriever's, not this ticket's.
3. **The order and the lock:** the base rebuild waited about 24 minutes for another session's rebuild; the lead restarted its own queued waiters twice (never a running rebuild) to keep each inside the two-hour limit of a background command. No rebuild was stopped while running.
   - **What it means:** each reported rebuild ran to its end with exit 0; the waits change no figure.

## 8. How to repeat it

W2-61's §8, with these changes:

1. **Three clones by exact path,** each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached: `/home/usain/gov-os-runs/W2-86/head` at `338c14fa6475`, `/home/usain/gov-os-runs/W2-86/base` at `9dc5288161c4`, and the measure's own clone `/home/usain/gov-os-runs/W2-86/measure` at `bf8ae585b827`.
2. **The stores,** by the pinned gov, in the base clone and in the head clone, with embeddings, after the load and disk gates: `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock gov rebuild --json`. Record its `digest` and the sha256 of `.gov-runtime/store.db`, `.gov-runtime/codeintel/home/code.db` and `.gov-runtime/codeintel/home/_config.db`; count the chunks with vectors per group of §6 in each store, read-only.
3. **The measure,** first the control, then the head with `--compare` the control's record:

   ```
   env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-86/measure/src python3 -m gov.retrieval.measure memory-retrieval \
     --root /home/usain/gov-os-runs/W2-86/<base|head> --sets-root /home/usain/gov-os-runs/W2-86/measure --part visible \
     --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-86/records --json [--compare <the control's record>]
   ```

   The budgets are the measure's defaults: `--batch-size 10 --bundle-budget 6000 --stack-budget 24000`.
4. **The supplementary head,** with a launcher whose first line sets `PYTHONPATH` to the head's `src/` (as `gov-wt` in §1), on a store built by that code, `--out /home/usain/gov-os-runs/W2-86/records-tree`.
5. **Never `--part hidden`.**
