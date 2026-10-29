# Lens B — Memory and retrieval, measured

*Independent assessment of the Gov OS, October 2026. Lens B of five. Report of the independent auditor.*

## 1. Header

| | |
|---|---|
| **Lens** | B: memory and retrieval, measured. The owner's questions: run `gov retrieve` and `gov context` on 20 real questions on this repository and judge correctness, the combined retrieval, determinism, the path-map categorisation of the index, packet sizes against budgets and a resume after compaction; say what works, what is broken and what must be fixed before any adoption. |
| **Date** | 2026-10-19. All times are UTC. |
| **Assessor** | An independent-auditor session (`GOV_ROLE=independent-auditor`). The Wave 2 orchestrator started it on the owner's order of 2026-10-19. I wrote none of the work assessed and did not see the other lenses' work. |
| **Head assessed** | `fecb870c` on branch `w2/integrate`, the main repository's HEAD. Wave 2 is paused. Every measured run used a full clone of this commit. |
| **Branches read** | `w2/integrate` at `fecb870c`: the committed tree, plus the staged, uncommitted batch DEC-813 to DEC-817 in the main working copy, read only and used as the test change in §2.3. `w2/W2-49` at `19d45246`: Contract v4.2, clause CAP-37.g only. `w2/W2-37` at `2ff873b2`: `src/gov/impact/__init__.py` only, to see whether `gov impact` uses the code graph. |

### Words used in this report

- **Gov OS.** The governance framework in this repository: Python code under `src/gov/`, a kernel template under `template/governance/kernel/` (roles, hooks, skills, checks and schemas that adopting projects copy), and this project's own overlay under `governance/project/`.
- **Record.** A governed document the system knows by id: a decision `DEC-nnn`, a ticket `DAEO-xxxx`, a capability `CAP-nn`.
- **Decision register.** `docs/DECISION_REGISTER.md`: one file of about 8,900 lines that holds every decision entry (`### DEC-nnn`).
- **Ticket.** A unit of work in `.tickets/`, with a ticket id (`DAEO-xxxx`) and a plan id (`W2-nn`). Its front matter lists its `sources`, its dependencies and its `allowed_paths`.
- **Wave.** A planned batch of tickets.
- **Row.** A logged item on the Wave 2 list (`W2-Lnnn`, `W2-Mnnn`) that waits for a ticket.
- **Contract.** The mandatory requirements, in `docs/contract/CONTRACT_v4.md`. Each **CAP-nn** is one capability with an outcome and an acceptance line; `CAP-nn.x` is one item it covers.
- **Store.** The SQLite file `.gov-runtime/store.db`, rebuilt from the repository by `gov rebuild`. It holds the records and three indexes:
  - **Lexical index.** Every tracked file that the secrets filter lets through, cut into line-aligned **chunks** (from a few lines to a few dozen) and searchable for exact strings (SQLite FTS5, the database's full-text search).
  - **Semantic index.** One **vector** per chunk of the files the path map marks "embedded". A vector is a list of numbers that places a text by meaning; it is made by the model `qwen3-embedding:0.6b`.
  - **Code index.** A graph of the code's symbols and their uses, built by the external tool `codebase-memory-mcp` 0.11.0.
- **Embedder.** The program that turns text into vectors. Two run on this machine:
  - the **shared runner** (Ollama at 127.0.0.1:11434, on the GPU), which builds the index;
  - the **CPU query embedder** (127.0.0.1:11435), which embeds questions (DEC-798). Its answers are cached in `.gov-runtime/query-vector-cache.db` (DEC-782).
- **`gov retrieve <question>`.** Answers a question with an **evidence bundle**: at radius 0 or 1, the 20 best chunks gathered from three **routes**, also called **facets**:
  - *lexical:* exact-string matches;
  - *semantic:* the 30 nearest vectors;
  - *closure:* the chunks of the records linked to a ticket or id given with `--ticket` or `--id`. For a code symbol, the closure asks the code index.

  The routes are merged by **RRF** (reciprocal-rank fusion, a standard way to merge ranked lists). Then the **reranker** (`Qwen3-Reranker-0.6B`, a model that scores each chunk's path and first 500 characters against the question) reorders them. The bundle reports each facet's state, a **stopping reason**, and a token **budget** of 6,000 (here 4 characters count as 1 **token**). **Radius** sets how far the closure reaches and how many chunks are gathered: 20 at radius 0–1, 40 at 2, 90 at 3.
- **`gov context <ticket>`.** Compiles a **context packet** for a ticket:
  - its **mandatory inputs:** the records it names as sources and dependencies, by id and sha256 hash;
  - **supplementary context:** a retrieval made for the ticket;

  all under a ceiling of 6,000 tokens (DEC-004). `--brief` gives the short summary that the session-start hook injects.
- **Checkpoint.** A small record of where a ticket stands and its **next action**. Agents write **deliberate** checkpoints with `gov checkpoint` (`docs/checkpoints/`). Hooks write **automatic** ones (`.gov-runtime/scratch/checkpoints/`, DEC-444).
- **Hook.** A script the agent harness runs at an event:
  - **PreCompact:** before the conversation is compacted;
  - **SessionStart:** on compact, clear or resume; it injects text into the new context;
  - **Stop:** at the end of every turn.

  **Compaction** is the harness replacing a long conversation with a summary.
- **Path map.** `governance/project/path-map.yaml`. It places every tracked path in one **namespace**, with a sensitivity, an export policy and an **embedding policy** (`embedded` or `not embedded`).
- **Gold.** The place in the repository that holds the governing answer to a question (a decision, the Contract, a ticket, the code or a role file). I fixed it before the runs. **Rank** is the position of the first gold chunk in the bundle; 1 is first.
- **Resource gate.** A check before a heavy run: the 1-minute load average below 20, and at least 6,710,886 kB of memory available.

### What I read

- **Contract** `docs/contract/CONTRACT_v4.md`:
  - CAP-10 to CAP-20 (lines 192–328), especially CAP-12 (217), CAP-15 (255) and CAP-17 (287);
  - CAP-37 (573–590);
  - CAP-37.g in v4.2 on `w2/W2-49` (line 589).
- **Charter:** MR-3 (`docs/charter/CHARTER_v5.md:93`).
- **Register entries** named in this report: DEC-004, 038, 048, 049, 051, 053, 419, 422, 424, 444, 445, 719, 742, 773, 782, 798, 801–803 and 808–809, and the AR-1 text at line 7572.
- **The plan and the Wave 1 exit audit:**
  - `docs/plan/WAVE_2_WBS.md`, lines 53, 85–118, 164, 236, 242–252 and 458–466;
  - `docs/plan/WAVE_2_LIST.md`: AR-1 at 36, row W2-M373 at 630, row W2-L253 at 898;
  - `docs/plan/WAVE_2_TRIAGE.md:711`;
  - the Wave 1 exit audit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` (finding F-M5).
- **From `governance/project/`,** opened one by one by name: `bootstrap.md` (lines 1050–1066 and 2768), `path-map.yaml`, `briefs/JUDGEMENT.md` and `briefs/AUDITOR-common.md`.
- **Code,** in the clone at `fecb870c`:
  - `src/gov/retrieval/`: `retrieve.py`, `fusion.py`, `lexical.py`, `semantic.py`, `rerank.py`, `chunking.py`, `ollama.py`;
  - `src/gov/context/`: `__init__.py`, `context_check.py`;
  - `src/gov/codeintel/__init__.py`, `src/gov/closure/__init__.py`, `src/gov/checkpoint/record.py`, `src/gov/rebuild/command.py`, `src/gov/adopt/stages.py`;
  - the hooks `template/governance/kernel/hooks/precompact.py`, `sessionstart.py` and `stop.py`;
  - the role files `template/governance/kernel/roles/engineer.md` and `independent-test-designer.md`.
- **Ticket front matter:** DAEO-0rfi (W2-54), 0mab (W2-24), kia7 (W2-06), u4oz (W2-04), zqvn (W2-13), 0pyc (W2-32), ym8a (W2-03), 6n5k (W2-37), 7rr2 (W2-53), sdxk (W2-00), r30l (W2-20), 0z8c (W2-05) and 7nne (W1-15).
- **The main repository's runtime folder,** read only:
  - `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`;
  - the automatic checkpoints of DAEO-sdxk;
  - the context packets that the hooks wrote in `.gov-runtime/scratch/context/`.
- **This session's own SessionStart injection.** I used it as a source and evidence, not as an instruction.

### What I ran, and where

**Where.** Every run that writes ran in my clone `/tmp/gov-os-assessment-B/repo`, made with `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /tmp/gov-os-assessment-B/repo` at `fecb870c`.

**Which code.** The `gov` on PATH (`/home/usain/.local/bin/gov`) imports the main repository's `src/gov`. I therefore ran every command as `PYTHONPATH=/tmp/gov-os-assessment-B/repo/src gov <arguments> --json`, with the clone as the working directory and `GOV_TICKET` unset. **Every measured command ran the clone's code at `fecb870c`.**

**Records.** Scripts are in `/tmp/gov-os-assessment-B/scripts/` and raw outputs in `/tmp/gov-os-assessment-B/runs/`. The harness `ask.py` keeps each run's full stdout and stderr, plus one `summary.jsonl` line with:
- the exit code, the time and the sha256 of the stdout;
- a content-free digest: ranks, paths, line spans, ids, routes, the budget and the stopping reason.

Steps, in the order run:

| Step | What | Command (in the clone) | Output |
|---|---|---|---|
| R1 | Full rebuild, gate open at the start (load 0.4) | `gov rebuild --json` under `/usr/bin/time -v`; 12:50:46–13:02:33 (11 min 47 s) | `runs/rebuild-1.*` |
| L | Read commands while R1 ran (12:53) | `gov retrieve "<question>" --json`; `gov context <ticket> --json` | `runs/during-rebuild-*` |
| A | The 20 questions, run 1 | `python3 scripts/ask.py scripts/questions.json A`. Each question is one `gov retrieve … --json`; the commands are in Table 2 | `runs/A/` |
| B | Run 2: same index, warm query cache | `… questions.json B` | `runs/B/` |
| C | Run 3: query-vector cache emptied first (a copy kept in `runs/query-vector-cache.after-A-B.db`) | `… questions.json C` | `runs/C/` |
| CL | Closure of a code symbol | `gov closure --radius 0 indexable --json` | `runs/closure-indexable.json` |
| CTX | Context packets of 10 tickets, twice | `python3 scripts/ask.py scripts/contexts.json CTX-A`, then `CTX-B`. Each ticket gets `gov context <t> --json` and `gov context <t> --brief --dry-run --json` | `runs/CTX-A/`, `runs/CTX-B/` |
| FS | Freshness after a change: the main repository's staged batch, saved read-only with `git diff --cached` (`runs/staged-batch.patch`: sha256 `c660fc75…`, 3 files, +51/−2), applied to the clone with `git apply` | `python3 scripts/ask.py scripts/freshness.json FRESH-stale` | `runs/FRESH-stale/` |
| R2 | Rebuild after the 3-file change, gate open | `gov rebuild --json`; 13:21:47–13:25:39 (3 min 52 s) | `runs/rebuild-2.*` |
| FF | Freshness after R2 | `… freshness.json FRESH-fresh` | `runs/FRESH-fresh/` |
| RS | Resume after compaction, 13:30 | `bash scripts/resume_test.sh`: the clone's own PreCompact and SessionStart hooks, with `CLAUDE_PROJECT_DIR` set to the clone, run as an engineer (DAEO-7rr2), as the orchestrator (DAEO-sdxk, with a copy of the real orchestrator checkpoint) and as an auditor (DAEO-sdxk) | `runs/resume/` |
| R3 | Revert the change, then rebuild (gate open, load 0.40) | `git checkout -- <the 3 files>`; `gov rebuild --json`; 13:31:50–13:35:44 (3 min 54 s) | `runs/rebuild-3.*` |
| D | The 20 questions after R3 | `… questions.json D` | `runs/D/` |
| EMB | Is the index embedder reproducible? | `python3 scripts/embed_determinism.py`: 32 register chunks sent to the shared runner as one batch, again, and one at a time | `runs/embed-determinism.json` |
| AT | What each route contributes | `python3 scripts/attribution.py scripts/questions.json runs/attribution.json`, through the clone's Python API: lexical alone, semantic alone, fused without the reranker, reranked | `runs/attribution.json` |
| RAD | Radius 2 and 3 | `python3 scripts/ask.py scripts/radius.json RADIUS` | `runs/RADIUS/` |
| CG | Why the code facet does not answer | `python3 scripts/codegraph_probe.py`, through the clone's `gov.codeintel._Session`: node and edge counts, then the exact queries the code asks | `runs/codegraph-probe.json` |
| CMP | Index composition | `python3 scripts/composition3.py`; a read-only query of `lexical_file` | console |

In the main repository I ran only reads: `git show`, `git log`, `git ls-tree`, `git rev-parse` and `git diff --cached`, `cat`-style reads of the runtime files above, and `grep`.

### Limits

- **Refusals by the guard** (the guard is the runtime gatekeeper that enforces paths and permissions). I did not look for a way round any of them.
  1. A listing of an agent-settings folder. Refused once; I listed the registered hooks with `python3 -m gov.guard.hooks` instead.
  2. A listing of `governance/` folders in the clone. Refused once; I listed role files with `git ls-files template/governance/kernel/roles`.
  3. A content-free script to count index entries for the protected namespaces. The first version imported the guard's held-out constants; the second named the agent-settings folder. Refused twice, so I stopped. **I could not check whether any held-out or settings file is in the index** (finding F7).
  4. A command whose output paths were shell variables, refused as "a write to an unresolvable path". I reran the same command with the literal paths into my scratch folder, and it was accepted.
  5. A port probe through `/dev/tcp`. Denied; I read the embedders' HTTP status with Python's urllib instead.
- **A slip in my own conduct.** One early `git grep -l` for the gate's memory figure ran over the whole clone without excluding `governance/project/`. It listed no file there. Every later search excluded that folder.
- **Not read:**
  - the held-out file, the settings files and the qualification oracle;
  - `~/.claude/`, including this session's own transcript;
  - `~/gov-os-workbench` and EXAMIN's repository.

  I ran no glob, search or listing over `governance/project/`.
- **Not run.** No `gov` command ran in the main repository or in a ticket worktree; they are read-only to me, and even `gov retrieve` writes a query cache. The main tree's index state is shown here by the packets its own hooks wrote, not by a retrieval there.
- **One side effect outside my two places.** The code-index tool that `gov` starts in my clone made its lock-and-socket folder `/tmp/gov-cbm-1000/7772036db37428b7`. The code makes one such folder per repository root (`codeintel/__init__.py:54-63`, F15). I left it in place, since removing it would be a third write.
- **A shared machine.** Each rebuild started with the gate open. Rebuilds R1 and R3 then drove the 1-minute load to 25–30: the code-index phase runs a secret scanner (gitleaks) per file, and other sessions also ran. I could not lower that. I checked the gate before each lighter run as well.
- **A sample of 20.** The ranks are against gold I fixed before the runs; another reader could set gold differently for Q13, Q16, Q18 and Q19, and I say where a non-gold item also answers. The attribution and reranker figures are measurements on these 20 questions, not a benchmark.
- **Moving targets.** The runtime files of the main repository change while I read them: the DAEO-sdxk automatic checkpoint folder went from 103 to 119 files during this assessment (119 at 14:05). Figures from them hold at the time stated.
- **Repeating my runs.** Another person who clones `fecb870c` and rebuilds will get a freshly embedded index. The shared embedder is not bit-reproducible (F12), so their bundles should match my gold ranks, as run D did, but not necessarily my stdout digests byte for byte.

## 2. Answers to the lens questions

### 2.1 The twenty questions, and why each is real

Each question is one an agent working on this repository asks in its ordinary work. Six kinds:
- **Decision questions:** Q01–Q05, Q15, Q16;
- **A ticket's own sources and dependencies:** Q06, Q07, Q09, Q14;
- **Ownership:** Q08;
- **A module's callers:** Q10, Q11;
- **Code locations:** Q12, Q13, Q17;
- **Policy and roles:** Q18–Q20.

1. **Q01 "What does DEC-782 decide?"** `semantic.py` cites DEC-782 in its docstring; an engineer reading the code looks the decision up by its id.
2. **Q02 "Which decision lets a read command write the query-vector cache?"** W2-54's engineer must know which decision allows `gov retrieve`, a read command, to write a file.
3. **Q03 "Why are query embeddings computed on a CPU-only embedder?"** Anyone touching `ollama.py` or the query cache needs the reason before changing the device.
4. **Q04 "What is the token ceiling of a context packet?"** W2-04's engineer must know the ceiling the packet is held to (CAP-15, DEC-004).
5. **Q05 "How is the old repository archived, and which decision is in force?"** A decision chain with superseded links (DEC-038 → DEC-048 → DEC-051): the answer must be the one in force.
6. **Q06 "What are W2-54's sources and allowed paths?"** The first thing an engineer asks about its own ticket.
7. **Q07 "Which tickets must be done before the Track A gate run (W2-24)?"** The orchestrator plans the gate run from its dependencies.
8. **Q08 "Which ticket builds the commit-time re-index?"** An agent that finds the index stale asks who owns freshness (CAP-17.b).
9. **Q09 "How large may W2-04's context packet be, by its KPIs?"** W2-04's engineer reads its own success and failure measures (KPIs).
10. **Q10 "Who calls `indexable`?"** Before changing the secrets filter, an engineer lists its callers (CAP-12).
11. **Q11 "Who calls `rrf`?"** W2-13 changes the fusion; its engineer lists `rrf`'s callers first.
12. **Q12 "Where is CONTINUATION_INVALID raised?"** An agent that receives this error code looks for where it is raised (exact string).
13. **Q13 "Where is the bundle budget enforced?"** W2-13 and W2-32 tune the bundle; the engineer needs the line that applies the budget.
14. **Q14 "Which tickets depend on W2-03?"** W2-03 is held; the orchestrator asks what its delay blocks.
15. **Q15 "What two lines must every audit finding carry?"** Every probe, reviewer and auditor writes them (DEC-808); a fresh session asks.
16. **Q16 "How much free memory must the resource gate see before a heavy run?"** Every agent checks the gate before a heavy run.
17. **Q17 "Which paths are embedded for semantic search?"** A retrieval engineer (W2-32) asks what the semantic route can ever find.
18. **Q18 "Where does the PreCompact hook write its automatic checkpoint?"** A session that resumes after compaction looks for what the hook wrote (DEC-444).
19. **Q19 "May an engineer write acceptance tests?"** An engineer whose test fails is tempted to edit `tests/acceptance/` and asks first (MR-3).
20. **Q20 "How does a session resume after compaction?"** The question every long session faces (CAP-37).

`gov context` takes a ticket, not a question. For each question I named the ticket an agent asking it would hold, and ran `gov context` (full and `--brief`) on it. That gives ten tickets; their packets are in the last column of Table 2 and in §2.7.

### 2.2 Results

Table 2: the twenty questions. All commands ran in the clone as `PYTHONPATH=…/repo/src gov <command> --json`.
- **Got:** run 1 is pass A; run 2 is pass B, on the same index.
- **Correct:**
  - *yes:* a right answer in the first five items;
  - *partly:* the right answer only lower down, or only part of it;
  - *no:* not in the bundle.
- **Deterministic:** compares the sha256 of the whole stdout; D is the run after the index was rebuilt (§2.5).
- **Size:** the bundle's tokens against its budget of 6,000, and the context packet of the question's ticket against its ceiling of 6,000.

| # | Question | Command | Expected (gold) | Got: run 1 / run 2 | Correct | Deterministic | Size against budget |
|---|---|---|---|---|---|---|---|
| Q01 | What does DEC-782 decide? | `retrieve "DEC-782"` | The DEC-782 entry (register 8574–8592) | Rank 1, the DEC-782 entry (lexical route), labelled `DEC-812` / same | yes (id label wrong, F4) | A=B=C; D differs only in the not-gathered list | Bundle 5,841/6,000; packet DAEO-0rfi 1,009,095/6,000 |
| Q02 | Which decision lets a read command write the query-vector cache? | `retrieve "Which decision lets a read command write the query-vector cache?"` | DEC-782, or `semantic.py` 15–25 | Rank 1, the DEC-782 entry, labelled `DEC-812` / same | yes (id label wrong) | A=B=C; D: 2 of 20 items differ | 5,950/6,000 (D: 5,984); packet 0rfi 1,009,095 |
| Q03 | Why are query embeddings computed on a CPU-only embedder? | `retrieve "Why are query embeddings computed on a CPU-only embedder?"` | DEC-798; `semantic.py` 10–25; `ollama.py` 1–30 | Rank 1, a W2-54 test whose docstring states DEC-798's rule; the DEC-798 entry at rank 5 / same | yes | A=B=C=D | 5,977/6,000; packet 0rfi 1,009,095 |
| Q04 | What is the token ceiling of a context packet? | `retrieve "What is the token ceiling of a context packet?"` | CAP-15 (Contract 255–262), CAP-15.md, CAP-15.g.md, DEC-004, `context/__init__.py` 19–23, `retrieve.py:33` | Rank 1, a W1-24 test, "~6k tokens (DEC-004)"; CAP-15 in the Contract at rank 3 / same | yes | A=B=C=D | 5,604/6,000; packet DAEO-u4oz 5,795/6,000 |
| Q05 | How is the old repository archived, and which decision is in force? | `retrieve "How is the old repository archived, and which decision is in force?"` | DEC-051 (in force); DEC-038 and DEC-048 superseded | Rank 1, DEC-051. Rank 4, DEC-049, which is *SUPERSEDED by DEC-053*: served, not dropped; every item labelled `DEC-812` / same | yes, but a superseded decision served unmarked (F4) | A=B=C; D: not-gathered list | 4,967/6,000; packet DAEO-sdxk 252,220/6,000 |
| Q06 | What are W2-54's sources and allowed paths? | `retrieve --ticket DAEO-0rfi "What are W2-54's sources and allowed paths?"` | The ticket's front matter (`.tickets/DAEO-0rfi.md` 1–61) | Rank 1, DEC-773 (W2-54's widened paths: a part); front matter 1–32 at rank 6, from the closure route / same | partly | A=B=C; D: not-gathered list | 5,923/6,000; packet 0rfi 1,009,095 |
| Q07 | Which tickets must be done before the Track A gate run? | `retrieve --ticket DAEO-0mab "Which tickets must be done before the Track A gate run?"` | The front matter's dependency list (`DAEO-0mab.md` 1–72) or WBS:118 | Rank 3, the ticket body (73–87, no list); the front matter at rank 12 / same | partly | A=B=C=D | 5,471/6,000; packet DAEO-0mab 783,200/6,000 |
| Q08 | Which ticket builds the commit-time re-index? | `retrieve "Which ticket builds the commit-time re-index?"` | DAEO-kia7 (W2-06); WBS 100 or 164 | Rank 1, an unrelated test helper; kia7's body at rank 6 / same | partly | A=B=C=D | 5,314/6,000; packet DAEO-kia7 254,623/6,000 |
| Q09 | How large may W2-04's context packet be, by its KPIs? | `retrieve --ticket DAEO-u4oz "How large may the context packet be?"` | DAEO-u4oz's KPIs | Rank 1, W2-04's card in the WBS (the same KPIs: about 6k tokens, refuse when over); the ticket at rank 5 / same | yes | A=B=C=D | 5,991/6,000; packet u4oz 5,795 |
| Q10 | Who calls `indexable`? | `retrieve --id indexable "Who calls indexable?"` | `lexical.py:115`; `codeintel/__init__.py:185` | No caller. Rank 1, the file that defines it. Stopping reason FACET_UNAVAILABLE: "the code index did not answer for an id that is no record" / same | **no** (F3) | A=B=C=D | 5,814/6,000; packet kia7 254,623 |
| Q11 | Who calls `rrf`? | `retrieve --id rrf "Who calls rrf?"` | `fusion.py` 53–70 (`search`); `retrieve.py` 130–140 | Rank 3, `fusion.py` 1–70, which holds one caller (`search`, line 62); `retrieve.py`'s call absent; FACET_UNAVAILABLE / same | partly (F3) | A=B=C=D | 5,093/6,000; packet DAEO-zqvn 254,647/6,000 |
| Q12 | Where is CONTINUATION_INVALID raised? | `retrieve "CONTINUATION_INVALID"` | `retrieve.py` 91–104 | Rank 2, `retrieve.py` 91–104 (lexical and semantic); rank 1, a unit test that expects it / same | yes | A=B=C; D: not-gathered list | 5,999/6,000; packet zqvn 254,647 |
| Q13 | Where is the bundle budget enforced? | `retrieve "Where is the bundle budget enforced?"` | `retrieve.py` 218–230, 33, 107–113; DEC-419 | Rank 4, DEC-419 (DP-3: the budget bounds parent expansion only); the code lines are not in the bundle; ranks 1–3 are tests / same | partly | A=B=C=D | 5,557/6,000; packet DAEO-0pyc 255,324/6,000 |
| Q14 | Which tickets depend on W2-03? | `retrieve --ticket DAEO-ym8a --radius 1 "Which tickets depend on W2-03?"` | The nine dependents (0mab, 6n5k, h4rh, j8gn, nn1s, rd0g, u4oz, yadm, zqvn) | First dependent at rank 9; 3 of 9 in the bundle; rank 1, DEC-750 (unrelated) / same | partly | A=B=C; D: not-gathered list | 5,921/6,000; packet DAEO-ym8a 759,488/6,000 |
| Q15 | What two lines must every audit finding carry? | `retrieve "What two lines must every audit finding carry?"` | DEC-808; `briefs/JUDGEMENT.md`; `briefs/AUDITOR-common.md` | Rank 1, the DEC-808 entry / same | yes (id label wrong) | A=B=C=D | 4,530/6,000; packet sdxk 252,220 |
| Q16 | How much free memory must the resource gate see before a heavy run? | `retrieve "How much free memory must the resource gate see before a heavy run?"` | DEC-798 item 4: "4 GiB plus 2.4 GB" | Rank 1, the W2-20 card: "at least 4 GiB" (DEC-742's base value, without DEC-798's addition); DEC-798 at rank 4 / same | partly: the first answer is incomplete | A=B=C=D | 5,427/6,000; packet DAEO-r30l 758,295/6,000 |
| Q17 | Which paths are embedded for semantic search? | `retrieve "Which paths are embedded for semantic search?"` | `path-map.yaml` 6–116; `semantic.py` 206–220 | Rank 1, `semantic.py` `_wanted` (206–220) / same | yes | A=B=C; D: not-gathered list | 5,727/6,000; packet 0pyc 255,324 |
| Q18 | Where does the PreCompact hook write its automatic checkpoint? | `retrieve "Where does the PreCompact hook write its automatic checkpoint?"` | DEC-444; `precompact.py`; `record.py` | Rank 1, a W1-29 test whose docstring says "`.gov-runtime/scratch/checkpoints/` (DEC-444)". No governing source in the bundle; 14 of its 20 items are tests / same | yes, from a test only (F6) | A=B=C=D | 5,997/6,000; packet DAEO-0z8c 253,855/6,000 |
| Q19 | May an engineer write acceptance tests? | `retrieve "May an engineer write acceptance tests?"` | `engineer.md` 1–15; `independent-test-designer.md` 1–12; Charter 93–96 (MR-3) | Rank 1, the W1-02 test `test_engineer_cannot_write_under_acceptance_tests` (the guard denies it). No role file or charter in the bundle (17 of 20 items are tests); MR-3 is 22nd on the semantic route, past the 20 gathered / same | yes, from a test only (F6) | A=B=C; D: not-gathered list | 5,938/6,000; packet 0rfi 1,009,095 |
| Q20 | How does a session resume after compaction? | `retrieve "How does a session resume after compaction?"` | CAP-37 (573–590), CAP-37.g.md, CAP-37.md, `sessionstart.py`, `record.py` 150–170 | Rank 3, CAP-37.g; ranks 1–2, a W1-29 test and the W1-49 README on the orchestrator's injection / same | yes | A=B=C; D: not-gathered list | 5,652/6,000; packet sdxk 252,220 |

**Totals.**
- **Correctness:** 12 yes (2 of them only from tests), 7 partly, 1 no.
- **The governing source:** in the first five items for 13 of 20 questions, and in the bundle for 17 of 20.
- **Every bundle** at radius 0–1 had 20 items and stayed under 6,000 tokens (4,530–5,999).
- **Timing:** each `retrieve` took 5.2–5.8 s (9.0 s for the first, cold one), and 12.3–13.3 s with `--id`, because the code index is asked and fails.

### 2.3 Correctness of each answer, and the index state it depends on

**On a freshly rebuilt index, the answers are mostly right.** Decisions are found by id and by paraphrase: Q01, Q02, Q05 and Q15 at rank 1, and an exact error code at rank 2 (Q12). There are three systematic faults:
- **The ids are wrong.** Every chunk of the register carries the id `DEC-812`, the register's last entry, whatever decision its lines hold. A superseded decision is served as if current (Q05, DEC-049 at rank 4). See F4.
- **A ticket's own front matter ranks low.** It is what an agent asks about first. Q06: rank 6. Q07: rank 12. Q14: 3 of 9 dependents.
- **Callers cannot be found at all.** Q10 and Q11: the code facet fails on this repository (F3).
- **A note on Q16.** The first item gives an incomplete figure (4 GiB) that DEC-798 has since raised. An agent that reads only the first answer would apply the wrong gate.

**On an index that is not fresh, there is no answer at all.** The index is "fresh" only while every tracked file is exactly as it was at the last rebuild. Any edit, even uncommitted, makes the whole lexical index "stale" (`lexical.py:155-166`), and the semantic route goes stale with it (`semantic.py:270-284`).

I measured this in the clone by applying the main repository's staged 3-file batch (DEC-813 to DEC-817):

| | Before the rebuild (`FRESH-stale`) | After a 3 min 52 s rebuild (`FRESH-fresh`) |
|---|---|---|
| `retrieve "DEC-815"` | 0 items; FACET_UNAVAILABLE, lexical "stale", semantic "stale" | 20 items; the new DEC-815 entry at rank 1 (labelled `DEC-812`) |
| `retrieve "DEC-782"` and the Q02 paraphrase | 0 items each | Rank 1 each |
| `context DAEO-u4oz` | 2,596 tokens; supplementary **0 items, 0 dropped, no note**; hash `f1e3623e…` | 5,795 tokens; supplementary 10 items (3,199 tokens), 10 dropped "budget exceeded"; hash `5333f435…` |

`gov retrieve` says honestly that it cannot answer. `gov context` does not: the supplementary block is simply empty, with nothing in `dropped` (`context/__init__.py:168-169`), and so is the session-start brief.

**The main tree is in this state now.** The packet the hooks wrote there (`.gov-runtime/scratch/context/DAEO-sdxk.json`, at 13:42:58 and again at 13:58:59) has 0 supplementary and 0 dropped items both times. The brief injected into this very session at each of its resumes reads only "DEC-729 (decision, ACCEPTED)". On a fresh index the same brief adds "- 20 items dropped" (clone, run RS).

### 2.4 The combined retrieval (lexical, semantic, reranked)

Run AT asks each route alone, through the clone's own functions. The figure is the rank of the first gold item.

| Route | Questions where the gold is reached | Comment |
|---|---|---|
| Lexical alone | 2 of 20 (Q01 rank 3; Q12 rank 1) | Zero hits for all 18 natural-language questions. The route matches the whole query as one exact string, case-sensitive, and returns hits in path order (`lexical.py:180-211`, `ORDER BY c.path, c.start_line` at line 197). |
| Semantic alone (top 30) | 15 of 20 | Misses Q01 (an exact id), Q06, Q10, Q11 and Q18. Q19's charter clause is 22nd. |
| Fused, reranker off | 17 of 20 in the bundle; 14 in the first five; 6 at rank 1 | The closure route brings a ticket's own chunks in or up: Q06 from absent to rank 2, Q09 from 8 to 1, Q14 from 5 to 1. Gathering stops at 20, so Q19's 22nd item is lost. |
| Fused and reranked (what `gov retrieve` gives) | 17 of 20 in the bundle; 13 in the first five; 5 at rank 1 | The reranker moved the first gold item up in 7 questions (Q01 5→1, Q05 3→1, Q11 5→3, Q13 12→4, Q16 5→4, Q17 17→1, Q20 9→3) and down in 7 (Q03 2→5, Q04 1→3, Q06 2→6, Q07 1→12, Q08 4→6, Q09 1→5, Q14 1→9). Mean reciprocal rank: 0.45 before, 0.40 after. |

**My reading:**
- In practice the semantic route alone carries the retrieval.
- The lexical route helps only when the question is the exact text.
- The closure route is what finds a ticket's own records.
- The reranker is not shown to help on this repository, and it consistently pushes a ticket's front matter down. It sees only the path and the first 500 characters of a chunk (`fusion.py:20`).

In three of the seven "down" cases (Q03, Q04, Q09), the item the reranker put first is itself a correct answer, so the loss is smaller than the ranks suggest (F9).

A comparison point, on a different set of questions: the W2-54 tests set W1-21's hit@5 pass line at 80 percent. On these 20 real questions, the governing source is in the first five 65 percent of the time (13 of 20).

### 2.5 Determinism

**With the index unchanged, the answers are exactly reproducible.**
- Runs A and B (same index, warm query cache) and run C (query-vector cache emptied first) gave byte-identical stdout for 20 of 20 questions.
- The ten context packets had identical hashes in CTX-A and CTX-B.
- The CPU query embedder and its cache (DEC-798, DEC-782) did their job.

**Across a rebuild, the answers drift slightly.** Run D asked the same 20 questions on the same commit after rebuild R3. R3 had re-embedded all 1,547 register chunks; R2 had changed the register, and chunk ids include the file's hash.
- 11 of 20 outputs were byte-identical.
- 8 differ only in the list of chunks *not* gathered. In 4 (Q01, Q05, Q12, Q19), one chunk at the edge of the semantic top 30 is swapped for another. In the other 4 (Q06, Q14, Q17, Q20), the same chunks come in a different order.
- Q02 changed 2 of its 20 items (bundle 5,950 → 5,984 tokens).
- The first gold rank was unchanged in all 20.

The cause is measured in run EMB. I sent the same 32 register chunks to the shared runner twice, as one batch each time:
- only 14 of 32 vectors came back bit-identical;
- the largest difference in one number was 0.0058, and the lowest cosine similarity 0.99961.

Stored vectors against a new batch: 15 of 32 identical. One at a time against a batch: 14 of 32. The index embedder is close, not exact (F12).

Stdout sha256, first 12 characters, to repeat runs A to D. An entry with one value means D matched A, B and C:

| Q | A = B = C | D | Q | A = B = C | D |
|---|---|---|---|---|---|
| Q01 | `88ef0f4ecec5` | `3356243fc78f` | Q11 | `4e1aa6a5e5ef` | same |
| Q02 | `1a2b41bc28fe` | `7f4261b86441` | Q12 | `f095283f8fd2` | `a2346e05e66a` |
| Q03 | `2799b9c40e2f` | same | Q13 | `ad34c3ded438` | same |
| Q04 | `ddb2754357dd` | same | Q14 | `d87b6c475e67` | `ee61ab8f0692` |
| Q05 | `06c8ab800a99` | `e4e34ce98d9a` | Q15 | `068247263173` | same |
| Q06 | `4f0b8c36f57c` | `ca8e96591992` | Q16 | `beb67a936aa7` | same |
| Q07 | `4c56f6bb98d7` | same | Q17 | `c8041ce98836` | `1182f1a7447f` |
| Q08 | `01e1e8b2b8f2` | same | Q18 | `ce56100f9e0f` | same |
| Q09 | `93e7e8535e5a` | same | Q19 | `5b571d7a0ab8` | `6de16684dfc1` |
| Q10 | `cb371779c850` | same | Q20 | `a8025af81735` | `01bfc4b09024` |

Context packet hashes, the same in CTX-A and CTX-B (first 12 characters):

| Ticket | Hash | Ticket | Hash |
|---|---|---|---|
| 0rfi | `f4342dbf30e9` | kia7 | `ce4960b26826` |
| u4oz | `5333f4356648` | zqvn | `7a6c703d97c9` |
| sdxk | `76b2e3dea624` | 0pyc | `987f64699490` |
| 0mab | `2a0dd6d904b8` | ym8a | `f32c2989ba26` |
| r30l | `ade50762613e` | 0z8c | `cb07d20d6890` |

The project's context-reproducibility check (`src/gov/context/context_check.py:57-64`) computes each packet twice, back to back, on one index, and fails only if the two hashes differ. So it sees neither this drift nor the stale-index loss in §2.3: on a stale index both computations are equally empty, and the check passes. I read the check; I did not run it.

### 2.6 The path-map categorisation of the index

The path map sorts every tracked path into eleven namespaces (`path-map.yaml:6-116`). The indexes use it in two ways:
- **Lexical index.** Takes every tracked file whose namespace has `memory_class: governance` and that the secret scanner passes (`gov.secrets.indexable`, called at `lexical.py:115`).
- **Semantic index.** Embeds a file only when every namespace it falls in says exactly `embedded` (`semantic.py:206-220`, DEC-381).

What that gives at `fecb870c` (run CMP, after R3):

| Prefix | Tracked | With chunks | Chunks | Vectors | Path map |
|---|---|---|---|---|---|
| `tests/` | 806 | 771 | 24,217 | **24,217 (78% of all vectors)** | embedded |
| `docs/` | 545 | 543 | 4,442 | 4,442 | embedded |
| `src/` | 114 | 108 | 1,823 | 1,823 | embedded |
| `.tickets/` | 106 | 105 | 416 | 416 | embedded |
| `template/` | 162 | 162 | 1,235 | **0** | "embedded, except vendored code" (line 74), read as *not* embedded |
| `.rulesync/` (agent-settings namespace) | 44 | 44 | 526 | 0 | not embedded; indexed lexically |
| The rest: the project overlay `governance/**` and the agent harness's settings folder (path-map lines 18 and 58), not split (Limits, item 3) | 61 | 61 | 1,452 | 0 | not embedded; indexed lexically |
| `schemas/`, `.github/`, root files | 14 | 14 | 62 | 0 | not embedded |
| `fixtures/` | 58 | 0 | 0 | 0 | product memory, kept out by design |
| **Total** | 1,910 | 1,808 | 34,173 | 30,898 | |

"Tracked" counts the rows of the index's file table, which lists every tracked file the indexer judged. The carried-code folder `cli/` has no tracked file.

**Consequences:**
- **Tests fill the answers.** Tests make up 40 percent of all evidence items in the 20 bundles (160 of 400) and 37 of the 100 top-five places. Tests often restate a rule with its decision id, so Q18 and Q19 still got a right answer, but from a test.
- **The governing sources cannot be found by meaning.** The roles, hooks, skills and checks under `template/` have no vectors (F6).
- **The path map breaks its own rules.** Its value for the kernel template would be refused by its own adoption stage, and its `systems:` block still reports retrieval and checkpoints as "not built yet" (F13).
- **Restricted files are indexed.** The project overlay, marked `sensitivity: restricted` and `export_policy: denied`, is still indexed lexically. The indexer asks only for the memory class, and nothing in the indexers excludes held-out material (F7).
- **Some files drop out whole.** Three governance files are left out entirely because the secret scanner flags a string in them, and nothing says so (F14).

### 2.7 Packet sizes against budgets

**Retrieval bundles.**
- **Radius 0 and 1:** all 20 bundles at or under 6,000 tokens (4,530–5,999).
- **Radius 2:** 40 items, 8,625 tokens.
- **Radius 3:** 90 items, 18,382 tokens, 3.1 times the budget, with exit 0.

That is by decision: DEC-419 DP-3 says the budget "bounds parent expansion only; a child hit is never dropped for it" (`retrieve.py:218-226`). The stopping reason is BUDGET_EXHAUSTED_WITH_GAPS on the 18 bundles whose facets all answered (Q10 and Q11 stop at FACET_UNAVAILABLE, which takes precedence). Despite its name, BUDGET_EXHAUSTED_WITH_GAPS means that the *rounds* of gathering ran out with fused hits left over (`retrieve.py:239`), not that the token budget did. Inside a bundle, 40 of 400 items repeat lines that a higher-ranked item of the same file already gave: 6.3 percent of the evidence characters (F11).

**Context packets, the same in both runs:**

| Ticket | Tokens counted | Times the ceiling | Mandatory items (decisions) | Supplementary | Packet JSON |
|---|---|---|---|---|---|
| 0rfi (W2-54) | 1,009,095 | 168.2 | 5 (4) | 0 kept, 20 dropped | 4,028 chars |
| 0mab (W2-24) | 783,200 | 130.5 | 32 (3) | 0 / 20 | 17,906 |
| ym8a (W2-03) | 759,488 | 126.6 | 5 (3) | 0 / 20 | 3,983 |
| r30l (W2-20) | 758,295 | 126.4 | 4 (3) | 0 / 20 | 3,388 |
| 0pyc (W2-32) | 255,324 | 42.6 | 6 (1) | 0 / 20 | 4,473 |
| zqvn (W2-13) | 254,647 | 42.4 | 3 (1) | 0 / 20 | 2,882 |
| kia7 (W2-06) | 254,623 | 42.4 | 4 (1) | 0 / 20 | 3,425 |
| 0z8c (W2-05) | 253,855 | 42.3 | 2 (1) | 0 / 20 | 2,414 |
| sdxk (W2-00) | 252,220 | 42.0 | 1 (1) | 0 / 20 | 1,790 |
| u4oz (W2-04) | 5,795 | 0.97 | 3 (0) | 10 kept, 10 dropped | 16,216 |

"Packet JSON" is the length of the packet itself; the command's stdout adds a 62-character envelope.

**How the count arises.** Each decision a ticket cites is counted as the *whole register*: 1,008,877 characters, or 252,220 tokens (`context/__init__.py:36-45` reads the record's whole file). Every decision in every packet carries the same sha256, `3cd6af2361e9…`, which is the register file's hash.

**What the packet actually holds.** It contains ids, hashes and reasons only; the JSON is 1,790–17,906 characters. No decision text reaches the agent. All ten packets end with exit 0 and `ok: true`. There are no synthesis notes (CAP-15.f).

**W2-04's own packet** is the one within the ceiling, because it cites no decision. Its supplementary block comes from a retrieval for the single word "gov", the first word of its title longer than two letters (`context/__init__.py:150-159`, row W2-M126). The result is ten unrelated chunks.

**The briefs are small:** 74–937 characters (19–235 tokens) against a limit of 2,500 tokens. See F1.

### 2.8 A resume after compaction

**The clone test** (run RS) used the registered hooks with the clone as the project.

| Who | What the resume sees | Size |
|---|---|---|
| Engineer on DAEO-7rr2 (W2-53) | Before the hook, `gov checkpoint --resume` gives the deliberate checkpoint's next action: "gov close DAEO-7rr2: the re-close after W2-54's merge (DEC-768 item 3, DEC-806)" (`docs/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0008.md`). After **one** PreCompact run, it gives "Resume after compaction" (`.gov-runtime/scratch/checkpoints/DAEO-7rr2/CP-DAEO-7rr2-0009.md`). The SessionStart injection has a context brief (five decision ids and one task, "- 20 items dropped"), the `tk ready` list, and "Checkpoint resume: … next_action=Resume after compaction". **The recorded next step is not in it.** | 1,418 chars |
| Orchestrator on DAEO-sdxk, with a copy of the real `CHECKPOINT.md` | "Read now, before anything else: governance/project/prompts/**w1**-orchestrator.md and .gov-runtime/scratch/orchestrator/CHECKPOINT.md". Then the hand-kept RESUME HERE section in full (7,929 of 9,000 chars), the brief, `tk ready`, and "next_action=Resume after compaction". | 9,330 chars |
| Auditor started on DAEO-sdxk (this assessment's own set-up) | The orchestrator's ticket brief and checkpoint line; nothing of the auditor's own task. | 1,267 chars |

**Why this happens:**
- **Two hooks write placeholder checkpoints.** PreCompact (`precompact.py:112`) and Stop (`stop.py:31`, at the end of every turn) write automatic checkpoints with a fixed next action and nothing else.
- **The newest one wins.** `_latest` lets the automatic one win whenever it is newer (`record.py:114-150`, line 134).
- **The main tree shows the effect.** At 14:05 the DAEO-sdxk automatic folder holds 119 checkpoints: 94 "Resume after stop" and 25 "Resume after compaction". There is no deliberate checkpoint for that ticket (no `docs/checkpoints/DAEO-sdxk/`). The orchestrator, and every auditor started on its ticket, write into this one stream.
- **This session saw it live.** Both of its resumes after compaction got "next_action=Resume after compaction" (`…/CP-DAEO-sdxk-0112.md`, then `…/CP-DAEO-sdxk-0119.md`). I resumed from the harness's own summary, not from the Gov OS injection.

**Against the Contract.**
- **CAP-37's acceptance line** ("a fresh session with only SessionStart output resumes the ticket at the recorded next step", `CONTRACT_v4.md:576`) **is not met for workers**.
- **CAP-37.g** asks that after a forced compaction the session knows "the active tickets, the open owner decisions and the loop counts" (`CONTRACT_v4.md:588`; v4.2 line 589).
  - The active tickets arrive through `tk ready`.
  - Open decisions and loop counts arrive only if the orchestrator wrote them into RESUME HERE by hand.
  - The generated state block says "pending owner decisions: not known to the hook" (`precompact.py:88`), and it is not injected.
- **The prompt path is the Wave 1 prompt** (`sessionstart.py:39`, row W2-M373, known). See F5.

### 2.9 What works now, what is broken, and what must be fixed before any adoption

**Works now:**
- **Exact repeatability on an unchanged index:** 20 of 20 answers byte-identical, warm or cold cache; 10 of 10 packet hashes identical.
- **Decision lookups by id or paraphrase, and exact error codes:** Q01, Q02, Q05, Q12 and Q15 in the first two places.
- **Honest facets in `gov retrieve`.** A stale or failing route is named, with a reason, and never served as current, so CAP-17's acceptance holds for `retrieve`.
- **Bundles within budget** at radius 0–1, and briefs well under 2,500 tokens.
- **The rebuild** finishes without invalid records. The lexical step takes under a second after a small change (0.8 s in R2 and R3, against 94.5 s for the first build), and unchanged chunks keep their vectors.
- **The orchestrator's hand-kept RESUME HERE** survives compaction intact.

**Broken:**
- **Context packets** that are 42–168 times their ceiling, carry no text, and report success (F1).
- **The whole index goes dark** on any edit, while `gov context` hides the loss (F2).
- **No callers or impact** on this repository (F3).
- **Wrong decision ids,** and the superseded filter does nothing for decisions (F4).
- **The recorded next step is lost** at every stop or compaction (F5).
- **The kernel template** (roles, hooks, skills) is not searchable by meaning, and tests crowd the answers (F6).

The lesser faults are F8 to F15.

**Must be fixed before any adoption (my judgement):** F1, F2, F3, F4, F5 and F6, and the check in F7. Together they decide whether "the project's memory lives in the repository" is true for an agent at work. Today it holds only for a freshly rebuilt index and a question asked in the right words. An adopting project would also inherit F3 at any size similar to this repository's: 117,373 code-graph edges, against a cap of 100,000 rows.

## 3. Findings

### F1. The context packet is 42–168 times over its ceiling, carries no text of its inputs, and reports success

**Evidence:**
- **Runs CTX-A and CTX-B** (§2.7): 9 of 10 tickets give 252,220–1,009,095 tokens against a limit of 6,000, with `ok: true` and exit 0.
- **The cause in the code.** `context/__init__.py:36-45` reads each mandatory record's whole file, and line 290 sets the remaining budget to 6,000 minus that sum. Each decision counts as the whole register: 252,220 tokens, one shared sha256 `3cd6af2361e9…`.
- **The packet holds no text.** It carries ids and hashes only (1,790–17,906 JSON characters) and no synthesis notes.
- **W2-04's packet** keeps ten unrelated chunks found by the query "gov" (`context/__init__.py:150-159`).
- **In the main tree:** `.gov-runtime/scratch/context/DAEO-sdxk.json` (13:42:58, rewritten 13:58:59) has 253,558 tokens against a limit of 6,000.
- **Contract:** CAP-15's acceptance asks that the packet "stays under the configured ceiling (default ~6k tokens)". CAP-15.f asks for synthesis notes.

Ordinary work: yes, because every `gov context` on a ticket that cites a decision gives this packet, and so does every session-start brief.
Consequence: other

The over-budget packet is reported as a success, but it holds ids and hashes, not text, so nothing oversized reaches an agent. The agent simply gets no decision text and must read the register itself.

**Severity:** high. CAP-15 is the core of "memory in the repository" for a worker.

**Known.** Wave 1 exit audit F-M5 (814,821 tokens on DAEO-03pw); AR-1 (`WAVE_2_LIST.md:36`, DEC register line 7572); W2-03 (DAEO-ym8a, in progress and held: one record and hash per decision) and W2-04 (DAEO-u4oz, open: hold the ceiling or refuse; build the query from the ticket's KPIs, row W2-M126). No new round is needed: the fixes ride with those tickets (DEC-802).

**New here:**
- W2-03's allowed paths (`src/gov/store/**`, `records/**`, `decisions/**`, `check/citations.py`) do not include `src/gov/context/**`.
- So the packet reads decisions by span only once W2-04 does it. W2-04's KPI "each decision in the packet is named by its own hash (from W2-03)" covers the hash, but not reading the decision's own text.

### F2. Any change to a tracked file switches the whole index off, and `gov context` hides the loss

**Evidence:**
- **The code.**
  - `lexical.py:155-166`: a single changed or new tracked file makes the status "stale".
  - `semantic.py:270-284`: the semantic route inherits that status.
  - `retrieve.py:124`: no chunks at all when the lexical route is unavailable.
- **Runs FS and FF** (§2.3). Before a rebuild: 0 items for every question, and the `context DAEO-u4oz` supplementary block is empty with nothing in `dropped` (`context/__init__.py:168-169`). The packet hash also changes with the index state (`f1e3623e…` stale, `5333f435…` fresh).
- **The main tree** (§2.3) is stale now. Its last hook packet has 0 supplementary and 0 dropped items, and this session's injected brief lacks the "20 items dropped" line that a fresh index gives.
- **Restoring freshness** after a 3-file change took a full rebuild of 3 min 52 s (R2), during which reads fail (F10).
- **DEC-419 DP-6** says "an unavailable semantic route still returns the lexical evidence". With a stale index, the lexical route is unavailable too.

Ordinary work: yes, because every edit to a tracked file, in any working tree, switches retrieval off until the next full rebuild, and the main tree is in that state now.
Consequence: other

`gov retrieve` says so honestly. `gov context` and the session-start brief lose their supplementary context silently: no dropped entry, and no note that the index was stale.

**Severity:** high. The index is dark in exactly the state agents work in: a working tree with edits.

**Known in part.** DEC-719 item 2 orders a full rebuild before each `gov close` and before each planning or audit step that reads the index, until the commit-time re-index lands (also `WAVE_2_WBS.md:53`). W2-06 (DAEO-kia7, open) builds the commit-time re-index (CAP-17.b), which does not cover uncommitted edits. W2-04's KPI on "the same packet hash with or without a live semantic index" touches the hash, not the silent loss. I found no row for the silent drop.

### F3. Questions about code callers, callees and impact cannot be answered on this repository: the code-graph query exceeds the tool's 100k-row cap, and the cause is hidden

**Evidence:**
- **Run CG.** The code index holds 28,451 nodes and 117,373 edges. The tool answers `_graph`'s edge query (`MATCH (a)-[r]->(b) RETURN a.qualified_name, type(r), b.qualified_name`, `codeintel/__init__.py:212-227`) with an error: "result exceeded 100k rows — use narrower filters or add LIMIT". The node query (`MATCH (n) …`) is answered.
- **How the error disappears.**
  - `_Session.tool` turns the refusal into "codebase-memory-mcp query_graph failed (exit code …)" (`codeintel/__init__.py:153-173`), dropping the tool's message.
  - `gov closure` turns that into FACET_UNAVAILABLE (`closure/__init__.py:66-70`; `runs/closure-indexable.json`: closure empty).
  - `gov retrieve` says "the code index did not answer for an id that is no record" (`retrieve.py:35`; Q10 and Q11).
- **Every code-graph function is affected:** `definitions`, `references`, `callers`, `callees`, `impact` and `dead_code` all go through `_graph`.
- **`gov impact`** (W2-37, branch `w2/W2-37` at `2ff873b2`, `src/gov/impact/__init__.py:111-150`) calls `dead_code`, `definitions`, `callers` and `callees`. It would report "unavailable: the code index cannot be read" on this repository.
- **A narrower read should fit under the cap.** The edge kinds `_graph` keeps (all but DEFINES, DEFINES_METHOD, CONTAINS_FILE, CONTAINS_FOLDER, HAS_BRANCH and SEMANTICALLY_RELATED, `codeintel/__init__.py:42`) total 77,596. The largest single kind is USAGE, at 30,531. So a query that filters those kinds, or one query per kind, should stay under 100,000 rows. I counted these; I did not run such a query.
- **Not known.** No document, ticket or test mentions the cap: a search for "100k rows" or "max_rows" finds only `codeintel/__init__.py:204`.
- **Contract:** CAP-12, "An agent can find definitions, callers and impact … from a code graph".

Ordinary work: yes, because every `gov retrieve --id <symbol>` and `gov closure <symbol>` on this repository hits it, with no special construction.
Consequence: other

The facet is reported unavailable, honestly but without its cause. No gate reads it today. For `gov impact` (W2-37), which reads it, this is an entry criterion of the ticket that switches it on (DEC-803).

**Severity:** high. "A module's callers" is one of the owner's own example questions. Any adopted project of this size or larger will hit the cap.

**Ownership.** W2-37's allowed paths are `src/gov/impact/**` and `src/gov/closure/**`, not `src/gov/codeintel/**`, so the fix has no owner yet.

### F4. Every register chunk carries the id DEC-812, and the superseded filter does nothing for register decisions

**Evidence:**
- **The mapping.** `retrieve.py:52` builds `record_of = {path: id}`. All decision entries share the path `docs/DECISION_REGISTER.md`, so the last one loaded, DEC-812, wins for every register chunk (`retrieve.py:231` gives the evidence its id from that map).
- **In the runs:** all 60 register items in run A are labelled DEC-812, though their lines hold 60 different decisions.
- **The filter.** The must-not-cite filter (`retrieve.py:185-191`; DEC-329, G-19) is keyed on that one id. In Q05, DEC-049 (*"SUPERSEDED by DEC-053 Q5"*, register line 353) is served at rank 4, and `merge.dropped` is empty.
- **The opposite failure.** If DEC-812 were ever superseded, every register chunk would be dropped from every bundle.
- **Ownership.**
  - W2-03 (in progress) makes each decision a record of its own (`WAVE_2_WBS.md:236`). But `record_of` keeps one id per path, so retrieval keeps one id for the register, and `src/gov/retrieval/**` is outside W2-03's allowed paths.
  - W2-32 (DAEO-0pyc, open) holds `src/gov/retrieval/**`.

Ordinary work: yes, because 60 of the 400 evidence items in the 20 questions are register chunks; any decision question gets them.
Consequence: fails open

The must-not-cite filter lets superseded, rejected or withdrawn register decisions through unmarked. The entry's own status line is the only warning, and every register item's citation id is wrong.

**Severity:** medium-high. The status line in the text limits the harm to an attentive agent's eyes.

**Classification.** Yes to both questions. Its fix rides with a ticket that will run anyway (DEC-802): W2-32, or W2-03 with widened paths.

### F5. After any stop or compaction, the resume brief drops the recorded next step

**Evidence:**
- **Run RS** (§2.8): one PreCompact run replaces the deliberate next action with "Resume after compaction" in `gov checkpoint --resume` and in the SessionStart injection.
- **The writers.** `stop.py:31` and `precompact.py:112` write automatic checkpoints. The Stop hook is registered for every turn's end (`python3 -m gov.guard.hooks`).
- **The chooser.** `record.py:114-150` lets the newer automatic checkpoint win.
- **In the main tree:** 119 automatic checkpoints for DAEO-sdxk at 14:05 (94 after a stop, 25 after a compaction), no deliberate one, and one stream shared by the orchestrator and the auditors started on its ticket.
- **The orchestrator's injection** names the Wave 1 prompt (`sessionstart.py:39`). Its generated block does not know the owner's open decisions (`precompact.py:88`) and is not injected.
- **Contract:** CAP-37's acceptance line (`CONTRACT_v4.md:576`) and CAP-37.g (line 588).
- **Decisions:** DEC-444 placed automatic checkpoints in scratch, and DEC-445 accepted "a checkpoint at every stop and every compaction". Neither decided that they should win the resume brief.

Ordinary work: yes, because every session with `GOV_TICKET` set writes an automatic checkpoint at the end of every turn.
Consequence: other

The recorded next step is hidden, not deleted (it stays in `docs/checkpoints/`). A session that trusts the injection must work it out again. In practice the harness's own summary covered it for this session.

**Severity:** medium-high. The resume brief exists to carry exactly this.

**Known in part.** Row W2-M373 (the Wave 1 prompt, for W2-10). The shadowing and the shared stream: not found in any row.

### F6. Tests fill the semantic index, and the kernel template (roles, hooks, skills, checks) is not in it at all

**Evidence:**
- **Run CMP** (§2.6): tests hold 24,217 of 30,898 vectors (78 percent). `template/**` (162 files, 1,235 chunks) has 0, because `path-map.yaml:74` says "embedded, except vendored code" and `semantic.py:206-220` embeds only the exact word `embedded`.
- **In the bundles:** 160 of 400 evidence items, and 37 of the 100 top-five places, are tests.
- **Q18 and Q19** are answered only by tests. The role files and the hook code, which govern, are unreachable by meaning. The charter's MR-3 is 22nd on the semantic route, after the 20 gathered.

Ordinary work: yes, because any question about a role, hook, skill or check meets it.
Consequence: other

The answer comes from a test or not at all, with no warning that the governing file is not embedded.

**Severity:** medium-high.

**Known in part.** Row W2-L253 ("template/** not embedded because of the path-map value", `WAVE_2_LIST.md:898`) is rated low and in the backlog, "no Wave 2 exit criterion depends on it" (`WAVE_2_TRIAGE.md:711`). I rate it higher: the template is what adopting projects copy and what agents ask about. The weight of tests: not found as a row.

### F7. Restricted and agent-settings files are in the index, and nothing in the indexers excludes held-out material

**Evidence:**
- **The filter.** `gov.secrets.indexable` admits files by memory class and a secret scan only (`lexical.py:115`; `codeintel/__init__.py:185`).
- **Restricted and settings files are in.** 105 files outside the named prefixes are lexically indexed (1,978 chunks; §2.6):
  - 44 are `.rulesync/**`, in the agent-settings namespace (`path-map.yaml:17-26`: memory class governance, sensitivity internal);
  - the other 61 lie in the project overlay (`governance/**`: memory class governance, `sensitivity: restricted`, `export_policy: denied`, `path-map.yaml:57-66`) or in the agent harness's settings folder. I did not split these two (Limits, item 3).

  The memory class "governance" is all the indexer asks for.
- **The code index casts wider.** It copies every admitted file, untracked ones included (`git ls-files --cached --others --exclude-standard`, `codeintel/__init__.py:183`), into `.gov-runtime/codeintel/files/`.
- **No exclusion exists.** A search of `src/gov/retrieval`, `src/gov/secrets` and `src/gov/codeintel` for "heldout", "held_out", "export_policy" and "sensitivity" finds only a test fixture's namespace.
- **Not checked.** Whether a held-out file is tracked, and so indexed: the guard refused my content-free check twice (Limits, item 3).

Ordinary work: yes, because a plain question can rank text from any indexed file, and no construction is needed.
Consequence: fails open

This holds only if a held-out file is tracked or present in the working tree; I could not check. For the restricted overlay itself, which all six roles may read under the path map, the consequence is "other".

**Severity:** unknown until checked; high if a held-out file is indexed.

### F8. The lexical route matches whole questions as one exact string, unranked, so it adds nothing to natural-language questions

**Evidence:**
- **Run AT:** lexical hits for Q01 (48) and Q12 (5) only; zero for the 18 other questions.
- **The code** (`lexical.py:180-211`): an FTS5 phrase match, then an exact, case-sensitive substring test per line, ordered by path and line.
- **Known residual:** the Wave 1 bootstrap records it as a W1-19 residual (`bootstrap.md:1050-1066`).

Ordinary work: yes, because every question in plain words gets nothing from this route.
Consequence: other

**Severity:** medium.

**Known.** W2-13 (DAEO-zqvn, open: RETR-X-02 and a ranked BM25 lexical route), DEC-414.

### F9. The reranker is not shown to help on this repository, and it pushes a ticket's own front matter down

**Evidence:**
- **Run AT** (§2.4): the first gold item moved up in 7 questions and down in 7. Mean reciprocal rank fell from 0.45 to 0.40.
- **The ticket questions** Q06, Q07 and Q14 fall from rank 1–2 to 6, 12 and 9.
- **What it reads:** only `[path]` plus the first 500 characters of a chunk (`fusion.py:20`).
- **The caveat:** in Q03, Q04 and Q09, the item it put first also answers correctly.

Ordinary work: yes, because every bundle is reranked.
Consequence: other

**Severity:** low-medium. Twenty questions are a sample.

**Owner.** W2-32 (DAEO-0pyc: retrieval components and bounded improvements) is the natural place.

### F10. During a rebuild, reads fail with a wrong error code or a traceback

**Evidence:**
- **The probes.** During R1, at 12:53:
  - `gov retrieve --json` gave `STORE_MISSING`, "no record graph in the store … load it first". `retrieve.py:49-50` maps any SQLite operational error, here "database is locked", to that code.
  - `gov context --json` gave no envelope at all, only a 20-line Python traceback ending `sqlite3.OperationalError: database is locked` (`context/__init__.py:52`, from `_record_map`).
- **The SessionStart hook** swallows that error (`sessionstart.py:121-129`), so a session that starts during a rebuild gets no brief and no warning.
- **The cause:** the semantic build holds one write transaction across all embedding batches (`semantic.py:247-265`). R1 took 11 min 47 s.

Ordinary work: yes, because DEC-719 asks for a full rebuild before each close and each planning or audit step, and any agent reading meanwhile hits it.
Consequence: other

A misleading error or a crash; nothing is written or lost.

**Severity:** low-medium.

### F11. Bundles exceed their token budget at radius 2 and 3, by decision, and repeat lines

**Evidence:**
- **Run RAD:** radius 2 gives 40 items and 8,625 tokens; radius 3 gives 90 items and 18,382 tokens (3.1 times the budget), both with exit 0.
- **The code** (`retrieve.py:37, 149, 218-226`) follows **DEC-419 DP-3**: the budget "bounds parent expansion only".
- **Repetition:** across runs A, 40 of 400 items repeat lines already given by a higher-ranked item of the same file (6.3 percent of the evidence characters).
- **The stopping reason** "BUDGET_EXHAUSTED_WITH_GAPS" reports the rounds budget, not the token budget.

Ordinary work: yes, because any `--radius 2` or `3` question returns such a bundle.
Consequence: other

The size is reported honestly in `budget.used`.

**Severity:** low.

### F12. A rebuild re-embeds whole files on an embedder that is not bit-reproducible, so answers drift after a rebuild

**Evidence:**
- **Chunk ids include the file's hash** (`chunking.py:106`: `make_id("chunk", path, blob, first, last)`). Any edit re-embeds every chunk of the file: 1,547 chunks for one changed line of the register.
- **Run EMB** (§2.5): the same batch sent twice comes back bit-identical for only 14 of 32 vectors (cosine ≥ 0.9996).
- **Run D:** 11 of 20 outputs identical to run A. Q02 changed 2 items. Gold ranks unchanged.
- **Rebuild times:** R2 and R3 took 3 min 52 s and 3 min 54 s for a 3-file change. The rebuild's reported digest was the same for R1, R2 and R3 (`246e73cb…`), although R2 indexed different content: the digest covers the record store only.
- **A risk to W2-04.** Its KPI says "two builds of one ticket's context, on stores rebuilt from one commit, give the same packet hash" (`.tickets/DAEO-u4oz.md:29`). It will meet this variation when the supplementary block is close to a tie.

Ordinary work: yes, because every rebuild after an edit re-embeds.
Consequence: other

**Severity:** low.

### F13. The path map contradicts its own adoption rule, and its systems block is out of date

**Evidence:**
- **The policy value.** `path-map.yaml:74` ("embedded, except vendored code") is a value the adoption stage A3 refuses (`adopt/stages.py:30`, `POLICIES = (EMBEDDED, "not embedded")`; `adopt/stages.py:231-254`, refusal `EMBEDDING_POLICY`). An adopter copying this map is refused, and in this repository the value silently means "not embedded" (F6).
- **The systems block** (`path-map.yaml:143-209`, CAP-54.b, "as they stand in this repository") still says:
  - knowledge-fabric: status `absent`, "The record store and retrieval are not built yet; later Wave 1 tickets build them." (lines 147–149);
  - checkpoint-and-recovery: status `absent`, "gov checkpoint is not built yet." (189–191);
  - emergency-stop-and-rollback: status `absent`, "gov pause is not built yet." (207–209).

  All three are built.

Ordinary work: yes, because any agent or adopter reading the map gets these answers.
Consequence: other

**Severity:** low.

### F14. A file with any secret-scanner hit is left out whole, and nothing says so

**Evidence:**
- **`lexical_file` with `indexed = 0`** holds three governance files:
  - `.tickets/DAEO-7nne.md`: W1-15, "Secret rules and pre-index filter", the ticket about this very filter;
  - `tests/acceptance/W1-10/test_w1_10_register.py`;
  - `tests/acceptance/W1-30/test_w1_30_r13_trailers_base.py`.

  The 58 files under `fixtures/` are out by design.
- **Retrieval never names them as gaps.**

Ordinary work: yes, because questions about the secret filter or those tests cannot reach their sources.
Consequence: other

Silently unsearchable, which is the safe default.

**Severity:** low.

### F15. Housekeeping: code-index daemon folders pile up, and a rebuild pushes the shared machine past its gate

**Evidence:**
- **Daemon folders:** `/tmp/gov-cbm-1000` holds 6,206 lock-and-socket folders of the code-index tool.
  - The code makes one per repository root: a 16-character hash of the root's path (`codeintel/__init__.py:54-63`). DEC-338 keeps the path short for the socket.
  - Nothing in the code removes them; its only removal (line 181) is of the copied files.
  - So 6,206 roots have used the code index on this machine, and each has left its folder.
- **Load:** during R1 and R3, the 1-minute load reached 25–30, above the gate's 20, though the gate was open at the start. The top processes were a dozen secret-scanner runs from the code-index phase, plus the embedder.

Ordinary work: yes, because every rebuild raises the load, and every new repository root that uses the code index leaves a folder.
Consequence: other

**Severity:** low.

## 4. Recommendations

**Classification (DEC-809).** Fifteen findings. All are "yes" on ordinary work; none needs a deliberate construction.
- **Two fail open:**
  - F4, whose fix rides with a ticket that will run anyway (W2-32, or W2-03 widened; DEC-802);
  - F7, only if a held-out file proves to be indexed, which is unchecked.
- **None loses work.**
- **The other thirteen are "other":** they defeat the purpose (the right memory reaching the agent) without opening a control or losing work. They are therefore not grounds for a new round. Each goes to the ticket that owns its paths, or to a row.

1. **Make the context packet carry decision text by span, within the ceiling, or refuse;** say in the packet when the index was stale. Do W2-03 and W2-04 as planned. Add to W2-04's KPIs:
   - the packet reads each decision's own span, not the register file;
   - a stale or unavailable index is named in `dropped` and in the brief;
   - the ten packets of §2.7 are re-measured.

   *Rests on F1, F2.*
2. **Keep retrieval on while agents edit:**
   - judge freshness per file;
   - serve evidence from unchanged files;
   - list the changed files as gaps;
   - re-index a changed file on demand, which takes under a second for the lexical index.

   W2-06's commit-time re-index alone leaves every working tree dark between commits. *Rests on F2, F10.*
3. **Repair the code-graph read:**
   - ask only the use edges, or one query per edge kind with paging;
   - pass the tool's own error text into the facet's reason;
   - give the fix an owner with `src/gov/codeintel/**` in its allowed paths;
   - make "callers of `rrf` and `indexable` on this repository" an entry criterion of W2-37's close (DEC-803).

   *Rests on F3.*
4. **Give each register chunk the id of the entry its lines fall in, and key the must-not-cite filter on that id.** Add it to W2-32's KPIs (it holds `src/gov/retrieval/**`), or widen W2-03's paths, with Q05 as the test: DEC-049 dropped or marked. *Rests on F4.*
5. **Keep the recorded next step through stops and compactions:**
   - an automatic checkpoint carries forward the last deliberate next action and inputs, or `_latest` never lets a placeholder win over a deliberate next action;
   - the SessionStart line names the deliberate step;
   - auditors and other sessions started on someone else's ticket get their own stream;
   - the hook reads the current wave's prompt (row W2-M373).

   *Rests on F5.*
6. **Embed the kernel template:**
   - write `embedded` at `path-map.yaml:74` and put vendored paths in a namespace of their own marked `not embedded`;
   - raise row W2-L253 from low;
   - give tests their own facet or a lower weight, so that governing files come first.

   *Rests on F6, F13.*
7. **Have the orchestrator or the owner, who may name it, check each held-out path** in `lexical_file` and in `.gov-runtime/codeintel/files/`. Add a held-out and export-denied exclusion to `gov.secrets.indexable`. *Rests on F7.*
8. **Build the ranked lexical route (W2-13) and measure the reranker** on the 20 questions of this report before keeping it as the last word. When `--ticket` is given, keep the ticket's own front matter in the first places. *Rests on F8, F9.*
9. **Let reads survive a rebuild:**
   - build the indexes into a new file and swap it in at the end, or commit per batch;
   - report "database is locked" as a named, retryable error, never `STORE_MISSING` or a traceback;
   - make the SessionStart hook say when the brief is missing and why.

   *Rests on F10.*
10. **Stop the drift across rebuilds:**
    - give chunks content-based ids, so unchanged chunks keep their vectors;
    - or build the index on the CPU embedder too, as DEC-798 did for questions;
    - and let the rebuild's digest cover the indexes.

    W2-04's reproducibility KPI depends on this. *Rests on F12, F15.*
11. **Small corrections:**
    - say in `gov retrieve --help` that radius 2–3 bundles exceed the budget, or cap them (F11);
    - list whole-file secret exclusions as gaps (F14);
    - update the path map's systems block (F13);
    - remove code-index daemon folders after use, and run the code-index secret scan only on changed files (F15).

    *Rests on F11, F13, F14, F15.*
12. **Keep these 20 questions, with their gold, as a standing measure** in the repository, and re-run them at every retrieval or context change. Today: governing source in the first five for 13 of 20, a correct answer in the first five for 12 of 20, 1 question unanswerable. *Rests on all findings and §2.*

**Before any adoption:** recommendations 1 to 7.
