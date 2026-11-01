# W2-86 re-measure: the lead's outputs (source for docs/research/W2-86-memory-measure.md)

Scores only. All times UTC. Commits in 12 digits.

## Places and code

- Clones (each `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS <path>`, detached):
  - `/home/usain/gov-os-runs/W2-86/head` at `338c14fa6475` (the branch head: the path map's namespace block, the tests);
  - `/home/usain/gov-os-runs/W2-86/base` at `9dc5288161c4` (the ticket's base, the control);
  - `/home/usain/gov-os-runs/W2-86/measure` at `bf8ae585b827` (`w2/integrate`'s head when cloned): the measure's code (`src/gov/retrieval/measure.py`, last changed at `289b9314`) and the visible set (last changed at `80c96c44`).
- The code is the same at base and head: `git diff --stat 9dc5288161c4 338c14fa6475 -- src` is empty. Only the path map (and the ticket's new tests) differ.
- The pinned gov: `/home/usain/.local/bin/gov`, first line `#!/home/usain/.local/share/gov-os/pin-5c401220/bin/python`; `gov --version` says `gov 0.1.0 (commit unknown)`; the pin's commit is `5c40122014da` (folder `pin-5c401220`, as W2-61's record names it). Each pinned run's `retriever.gov_file`: `/home/usain/.local/share/gov-os/pin-5c401220/lib/python3.12/site-packages/gov/__init__.py`; executable `/home/usain/.local/share/gov-os/pin-5c401220/bin/gov`.
- The measure command (W2-61 §8 step 3), visible half only: `env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-86/measure/src python3 -m gov.retrieval.measure memory-retrieval --root <clone> --sets-root /home/usain/gov-os-runs/W2-86/measure --part visible --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-86/records --json`, the head with `--compare` the control's record. Budgets: the defaults, `--batch-size 10 --bundle-budget 6000 --stack-budget 24000` (each run's `budget`). The hidden half was neither read nor run.

## The stores (pinned gov, `env -u PYTHONPATH -u GOV_TICKET flock /tmp/gov-os-rebuild.lock gov rebuild --json`, after the load and disk gates; never `--no-embeddings`)

| | base (control) | head |
|---|---|---|
| Gate passed | 22:10:56 on 2026-10-31; 868 GiB and 65,149,800 inodes free; load 4.21, 5.29, 8.53 | 00:03:03 on 2026-11-01; 863 GiB and 64,723,716 inodes free; load 17.92, 33.43, 50.56 |
| Lock held from | about 22:34 (another session's rebuild held it before) | 00:03 |
| End | 23:40:39 | 00:44:46 |
| Exit | 0 (`ok: true`) | 0 (`ok: true`) |
| Stores (`lexical`, `semantic`, `codeintel`) | each `recreated` | each `recreated` |
| `timing.lexical_s` | 311.0 | 370.8 |
| `result.digest` (= `result.store.digest`) | `7f2e1e54ccdf86711ea8bd9bbd1b2918730c09d293350170ca2b07042d255eb9` | `aff71072671894bafe99db13ee6658bccdffd8858561c278f5e3a5efbd1e4bd3` |
| sha256 `.gov-runtime/store.db` | `691a60b0cf8812c6006605f317032e36733c72cc81fd59baa06179c1acd9d012` | `99ad51cb5f774d1d77a4f827560503625454b128890a8eba9462817ffb62d382` |
| sha256 `.gov-runtime/codeintel/home/code.db` | `64b74376194fbebf87550b57361fb7d544fbf9d5412b472dc161e0f99d1373e9` | `b1a06534a5d113d31e2f00d9b457216c5e96cece9d365aa6d67f6928eb89ebad` |
| sha256 `.gov-runtime/codeintel/home/_config.db` | `6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8` | the same (also W2-61's and W2-87's) |

The digests differ because the record graph differs (the head has the ticket's commits); the digest covers the record graph only (`src/gov/store/loader.py:305`), so the vector set is the figure compared.

## The runs

| Run | Tree | Retriever | Start | End | Exit | stderr | Record (`/home/usain/gov-os-runs/W2-86/records/`) | `--compare` |
|---|---|---|---|---|---|---|---|---|
| control | base `9dc5288161c4` | pinned gov | 23:40:51 | 00:01:30 | 0 | empty | `measure-memory-retrieval-visible-20261101T000130633794Z.json` | — |
| head | head `338c14fa6475` | pinned gov | 00:44:54 | 00:58:37 | 0 | empty | `measure-memory-retrieval-visible-20261101T005837664244Z.json` | the control |

Supplementary (deviation 2): `head (tree code)`, the head tree's own code as retriever, on this worktree's own store (built by its own code at `338c14fa6475`, digest `5bbb7249412e3b79d63577f9ac951146caa6d1e5356e3fd0aa0f9319ea5bd8a9`; identical to the head clone's store in its 2,761 lexical files and their blobs and in its 51,114 chunks with vectors, path by path): launcher `gov-wt` (the pinned launcher's body under `#!/usr/bin/env -S PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src /home/usain/.local/share/gov-os/pin-5c401220/bin/python`, in the lead's session scratchpad), `retriever.gov_file` `/home/usain/gov-os-worktrees/W2-86/src/gov/__init__.py`, version `gov 0.1.0 (commit 338c14fa6475)`; 01:38:35 to 02:16:04, exit 0, stderr empty; record `/home/usain/gov-os-runs/W2-86/records-tree/measure-memory-retrieval-visible-20261101T021603839200Z.json`.

## Totals (both figures together; the in-the-bundle count)

| | hit@5 against CAP-10's floor of 85 | full evidence against the owner's target of 99 % | in the bundle |
|---|---|---|---|
| W2-61 baseline (`23079f92a6fa`, pinned gov, pinned stores) | 8 of 20 (40 %) | 12 of 20 (60 %) | 14 of 20 |
| W2-87 head (`cffef92c8534`, W2-87's own code) | 11 of 20 (55 %) | 11 of 20 (55 %) | 15 of 20 |
| control (`9dc5288161c4`, pinned gov) | 7 of 20 (35 %), short by 50 points | 11 of 20 (55 %), short by 44 points | 13 of 20 |
| head (`338c14fa6475`, pinned gov) | 7 of 20 (35 %), short by 50 points | 11 of 20 (55 %), short by 44 points | 13 of 20 |
| head, tree code (supplementary) | 11 of 20 (55 %), short by 30 points | 11 of 20 (55 %), short by 44 points | 15 of 20 |

## Per question (each cell: hit@5, first gold rank, in the bundle, full evidence found/needed)

| Q | control (pinned) | head (pinned) | head, tree code | head vs control (pinned) compare |
|---|---|---|---|---|
| Q01 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | same |
| Q02 | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q03 | no, 7, yes, yes (1/1) | no, 7, yes, yes (1/1) | yes, 2, yes, yes (1/1) | same |
| Q04 | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q05 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q06 | no, 8, yes, yes (2/2) | no, 8, yes, yes (2/2) | no, 7, yes, yes (2/2) | same |
| Q07 | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | no, 6, yes, yes (1/1) | stacked digest |
| Q08 | no, 9, yes, yes (1/1) | no, 9, yes, yes (1/1) | no, 11, yes, yes (1/1) | same |
| Q09 | no, 59, no, yes (1/1) | no, 59, no, yes (1/1) | no, 44, no, yes (1/1) | same |
| Q10 | no, 25, no, no (1/2) | no, 25, no, no (1/2) | no, none, no, no (0/2) | stacked digest |
| Q11 | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | yes, 4, yes, no (1/2) | same |
| Q12 | yes, 2, yes, yes (1/1) | yes, 2, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q13 | no, 6, yes, no (1/2) | no, 6, yes, no (1/2) | yes, 1, yes, no (1/2) | same |
| Q14 | no, 16, yes, no (3/9) | no, 16, yes, no (3/9) | no, 17, yes, no (4/9) | same |
| Q15 | yes, 3, yes, yes (1/1) | yes, 3, yes, yes (1/1) | yes, 1, yes, yes (1/1) | stacked digest |
| Q16 | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | stacked digest |
| Q17 | no, 21, no, no (1/2) | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | stacked digest |
| Q18 | no, none, no, no (0/2) | no, none, no, no (0/2) | no, none, no, no (0/2) | stacked digest |
| Q19 | no, none, no, no (0/1) | no, none, no, no (0/1) | no, none, no, no (0/1) | stacked digest |
| Q20 | no, 21, no, no (1/2) | no, 21, no, no (1/2) | yes, 2, yes, no (1/2) | same |

- Head against control (pinned, the like-for-like pair): the same in hit@5, in the bundle, full evidence, pieces and first gold rank for 20 of 20; the stacked digest differs for 11 (Q02, Q04, Q05, Q07, Q10, Q12, Q15, Q16, Q17, Q18, Q19): new chunks enter the stacked context, none of them a gold piece. Calls per question are the same in all three runs (5, 2, 2, 2, 2, 3, 5, 2, 4, 2, 2, 2, 2, 5, 2, 2, 2, 2, 2, 2).
- Head, tree code against W2-87's head (W2-87's record §5): the same figures (11, 11, 15 of 20) and the same cells but Q09 (first gold rank 44 here, 46 there) and Q14 (4 of 9 pieces here, 6 of 9 there).

## Q18 and Q19 (from the lead's spot retrievals, paths and ranks only; `gov retrieve "<the question>" --json`, the first call's 20 items)

- **Q18** (needs 2 pieces; one alternative is the PreCompact hook, `template/governance/kernel/hooks/precompact.py`): in the head with tree code, `precompact.py` is not among the 20; the bundle holds three register chunks (not the gold entry's lines), a contract chunk, two tickets, W1-29's and W1-49's tests and READMEs on the PreCompact hook (ranks 8, 11 to 16, 18) and assessment reports. The hook's own file now has vectors (6 of 6 hook files, 90 of 90 chunks) but its chunks rank below the tests that name it. Still 0 of 2.
- **Q19** (one of three alternatives suffices: the charter's MR-3 or one of two role files): with the pinned gov at the head, the first 20 are tests, assessment reports and register chunks, with one template file (`template/governance/kernel/skills/test-design/SKILL.md`, rank 16) and no role file; with tree code, template files appear at rank 8 (that skill) and 19 (`template/governance/kernel/templates/brief-lead.md`), the master rule's own file `docs/contract/master-rules/MR-3.md` at 17 (not a gold alternative), and no role file and no charter chunk. Still 0 of 1.
- So the change makes the kernel template reachable (its files now enter the stacked context: the digest moved for both), but for these two questions the governing chunk is outranked by tests, reports and other sources on the same subject; the remaining cause is ranking, not embedding.

## The vectors (each store opened read-only; chunk = a row of `lexical_chunk`, with a vector when `semantic_vector` holds its id)

| Group | files | chunks | chunks with vectors, base | chunks with vectors, head |
|---|---|---|---|---|
| `template/governance/kernel/roles/` | 6 | 19 | 0 | 19 (6 files) |
| `template/governance/kernel/hooks/` | 6 | 90 | 0 | 90 (6 files) |
| `template/governance/kernel/skills/` (all, superpowers included) | 24 | 214 | 0 | 76 (10 files: the 9 kernel `SKILL.md` and `superpowers/vendored.yaml`) |
| `template/governance/kernel/vendor/` | 15 | 139 | 0 | 0 |
| `template/governance/kernel/skills/superpowers/<skill>/` | 14 | 138 | 0 | 0 |
| `template/governance/kernel/bin/` | 1 | 46 | 0 | 0 |
| `template/.rulesync/` | 44 | 529 | 0 | 0 |
| `template/` (all) | 167 | 1,262 | 0 | 410 (93 files) |
| the whole store | 2,632 base, 2,635 head (paths with chunks) | 55,591 base, 55,625 head | 50,672 | 51,114 |

- **Vector diff, base to head:** 96 paths gain vectors, none lose any. 93 are the kernel template's files (schemas 21, checks 20, templates 12, skills 10, hooks 6, roles 6, `openspec/schemas/feature-readiness` 6, canaries 2, and one each: `.copier-answers.yml.jinja`, `.github/workflows/ci.yml.jinja`, `.gitignore`, `.gitleaks.toml`, `kernel/launch/research-allowlist.yaml`, `kernel/settings.json`, `governance/project/path-map.yaml`, `governance/project/test-map.yaml`, `lefthook.yml.jinja`, `openspec/config.yaml`); the other 3 are the ticket's own new files (`tests/acceptance/W2-86/README.md`, `tests/acceptance/W2-86/test_w2_86_kernel_template_embedding.py`, `tests/unit/retrieval/test_w2_86_kernel_template_namespaces.py`). No path outside `template/` other than these 3 changes.
- **Lexical diff, base to head** (`lexical_file` blob by path): 4 files: `governance/project/path-map.yaml` (changed; its namespace is not embedded, so it gains no vector) and the 3 new files. Nothing else.

## Deviations

1. **The retriever is the pinned gov, `5c40122014da`,** as the brief and W2-61's §8 name it. It predates W2-87's authority order (code merged since), so the control and the head carry W2-61's ranking, not W2-87's. That is why the control (7, 11, 13 of 20) is below W2-87's head (11, 11, 15) and also 1 below W2-61's baseline on each figure (the tree and its stores changed since `23079f92a6fa`, as W2-87's §7 found for its own control: Q03 and Q16). The pair head against control isolates this ticket's data change, the retriever and the code being the same.
2. **The supplementary head with tree code** gives the figure the brief expected the control to carry (W2-87's ranking): it equals W2-87's head. Its like-for-like control (the base with tree code, on stores built by tree code) was not run: the pinned gov's stores cannot be read by the tree's code (W2-87's §7 deviation 1), and the base's rebuild by tree code waited more than an hour behind three other sessions' rebuilds on the shared lock under a load of 60 to 88, so the lead stopped it. The head with tree code used this worktree's store instead of the head clone's (the same files and vectors path by path, built by the same code at the same commit), because rebuilding the head clone too would have meant a second wait on the lock.
3. **The order and the lock:** the base rebuild waited about 24 minutes for another session's rebuild; the lead restarted its own queued waiters twice (never a running rebuild) to keep each inside the two-hour limit of a background command. No rebuild was stopped while running.
