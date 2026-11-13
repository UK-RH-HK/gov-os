# INVESTIGATION-1, part E: a fresh repository, or lift and refactor here?

**By:** a read-only investigator (DEC-1047), 2026-11-02. **Tree read:** the main tree at `w2/integrate` `1e02facd`
(clean). Nothing changed in any tree. Helper scripts and outputs: `/tmp/gov-os-inv-E/` (`imports.py`,
`imports.json`, `closure.py`). Every figure comes from a command named under the table. Estimates are marked
**est.** and say how they were reached.

## Headline
1. **Keep this repository and do the lifting here (recommended; confidence high, about 80 %).** The bureaucracy sits
   in configuration and practice: the switches, the tests in runs, the briefs, the register in context and the
   ceremonies. It does not sit in the repository's shape. DEC-953 and DEC-1045 have already shown that a lift here
   is one configuration line plus a decision.
2. **A fresh repository would not leave the ceremony behind.** The memory stack's import closure takes in **18,063
   of the product's ~26,000 lines (77 modules)**: `store → close.fingerprint → close.select → guard.decide`,
   `retrieve → decisions → guard.containment_merge`, `secrets → guard.runs`, `retrieval.measure → guard.reads`. The
   memory store is itself the governance-record model (tables `records`, `trailers`, `commits`, `register_entries`).
3. **The fresh path costs about 8 to 14 working days (est.); the keep path costs 2 to 4 (est.).** The fresh path
   would also cut 18,360 DEC citations off their register, break W2-61's memory measure (its gold answers are this
   repository's sources), and need a new pin, new paths in 163 tool files and 5 cron lines, new tickets, and the
   owner's new remote and push routine. EXAMIN's copy would move back by about 7 to 12 working days (est.).
4. **Most of what a fresh start would give can be had here by configuration and hygiene** (rows E-3 to E-8):
   - narrow the memory corpus: tests are **60 % of the 55,591 chunks** and `src/` is 4.7 %;
   - split the register into an archive and a short live file;
   - send the lifted features' suites to the nightly or a weekly run;
   - prune the 79 branches and 73 worktrees;
   - move the live five-rule hook's tests into the repository (today they are in untracked scratch).
5. **Untangle the four coupling edges in step 2's refactor whichever way is chosen.** That makes memory a separable
   module of the product, and it is also what a later copy (EXAMIN) needs.

## Table

| id | what | where (paths, tickets, decisions) | cost (machine / tokens / owner; source) | what it protects | DEC-1010 test: in aim? ordinary work? fails open or loses work? | recommendation | what lifting takes (code, tests, tickets, config) | depends on |
|---|---|---|---|---|---|---|---|---|
| E-1 | **The question: a fresh repository, or keep this one and lift here** | whole repository; DEC-1047 (2) last sentence; DEC-1039 (2), (3b); DEC-953; DEC-954 Q1 (EXAMIN's copy by K9's criteria) | **Fresh: about 8 to 14 working days (est.)**, about 3 to 6 owner-hours (est.), EXAMIN's copy about 7 to 12 working days later (est.). **Keep: about 2 to 4 working days (est.)** for the lifts parts A to D recommend, plus E-3 to E-8. Breakdown under the table (§1) | Fresh: a clean slate, a small code and test base, a short register. Keep: history, evidence, the memory measure, pins, the record branch, the tickets' KPIs | The aim's four needs are all in this repository today (memory, spec and KPI agents, role separation, the WBS and tickets). Both paths keep them. Only the fresh path risks losing work: evidence, the measure's baseline, and the in-flight memory branches | **Keep and lift here**, with E-2 to E-8 as the "fresh start inside the repository" | The owner's decision on the combined list. The lifts themselves are parts A to D's rows | parts A1, A2, B1, B2, C, D |
| E-2 | **The memory stack's coupling to close, guard and decisions.** Memory imports the gates' code for small helpers: `store/loader.py:327,379 → close.fingerprint.of_commit → close.select → guard.decide._match_pattern`, `tasks.tickets`; `retrieve/command.py:26 → gov.decisions` (whose `__init__` imports `checker → guard.containment_merge`, `store.loader` trailer rules); `secrets/__init__.py:48 → guard.runs → guard.decide`; `retrieval/measure.py:51 → guard.reads` | `src/gov/store`, `retrieval`, `secrets`, `decisions/__init__.py`, `close/fingerprint.py`, `close/select.py` | The closure is 18,063 lines in 77 modules (`closure.py`), against about 7,600 lines for memory proper (est.: retrieval 2,291, store 457, rebuild 655, codeintel 279, secrets 844, config 292, util 180, cli 384, closure 114, records 73, retrieve 36, decisions.register 201, context 471, plus about 1,290 in-flight lines from W2-112, 122, 123 and 126). Machine and token cost: none directly. It blocks any copy (EXAMIN's or a fresh one), and it makes every memory change select gate tests | Nothing. These are helper reuses (a commit fingerprint, a glob matcher, a ticket-dir constant, the runs root) | Not in itself a guard. It is accidental coupling | **Untangle in DEC-1039 step 2's refactor** (whichever path): move `of_commit`'s path classification, `_match_pattern`, `TICKETS_REL`, `runs.root` and `leave_out` into `gov.util` or `gov.store`, and make `gov.decisions/__init__` lazy | One engineer ticket, est. 0.5 to 1 lead-day (S-profile median 9.2 lead-hours, PLAN-W2-DEC953 §2.0). Unit tests move with the helpers. No acceptance test changes (public calls unchanged) | the four memory branches landed (W2-112, 122, 123, 126) |
| E-3 | **The memory corpus is mostly tests.** `tests/acceptance` 52.9 %, `tests/unit` 7.5 %, `docs/close` 6.5 %, `docs/assessment` 4.8 %, `src` 4.7 %, the register 4.1 % | `.gov-runtime/store.db` `lexical_chunk` (55,591 chunks); corpus = `git ls-files` through `gov.secrets.indexable` by `path-map.yaml` namespaces' `memory_class` | W2-122's measured cold rebuild: **4,709 s** of embedding, 54,425 chunks (`docs/changes/W2-122-evidence.md` on `w2/W2-122`); 1,180 s more waiting for a slot. Tests are about 60 % of that (est., by chunk share). Tokens: a search returns test text where the question was about the spec (not measured) | A search can find test text (useful for "which test covers KPI X") | Searching tests is in the aim. Embedding 32,000 test chunks on every cold build is not required by it. Narrowing loses nothing: lexical search over tests can stay | **Scope:** keep tests in the lexical index and leave them out of the semantic one, or the reverse; the measure (W2-61) decides which. This is the main "smaller memory" gain a fresh repository would bring, had here by configuration | A `path-map.yaml` namespaces change (`memory_class`), one seeded rebuild, W2-61's measure run before and after. If the namespace rule cannot split lexical from semantic, a small KPI line for W2-32 | W2-61 measure; E-2 not needed |
| E-4 | **The register as one 1.66 MB file** (1,043 entries, 12,985 lines; about 415,000 tokens, est. at 4 characters per token) | `docs/DECISION_REGISTER.md`; `DECISIONS-IN-FORCE.md` (16.8 KB) already summarises it (DEC-953 item 7); `path-map.yaml:274 decision_register` | Part A1 item 4 (`gov context`, 1,619,286 tokens) is the acute cost; 2,261 chunks in memory; every recorded decision appends to the file (pings.log 173 lines; 129 packages) | The owner's decisions as git facts (Charter §6, W2-12, W2-55) | Recording is in the aim. Reading the whole file in every packet is not | **Keep the register; split it here:** freeze entries up to the emergency in `docs/archive/` (ids stay resolvable through `register_entries`), keep a short live file and the in-force list. This is the fresh repository's "short register" without breaking 18,360 citations | One product-spec ticket (est. 0.5 to 1 day). It touches tests that read the own register (`W1-10/test_w1_10_register.py:38`, `W2-03/w2_03_support.py:37`, W2-55's backfill), so a test designer revises them (MR-3). The store must read both files (one `path-map` key) | part A1 item 4's fix |
| E-5 | **The live five-rule hook's tests are not in the repository.** `.claude/hooks/pretooluse.py` (274 lines) and `bash_writes.py` (1,431) are tested by `.gov-runtime/scratch/orchestrator/tools/test_guard_fix_3.py` (14 tests, 730 lines, untracked) and `guard4_check.py`. Four W1-02/W1-45 tests name the hook file | `.claude/hooks/`, scratch tools; DEC-953 item 2, DEC-954, ACT-GUARD-FIX-3 (DEC-1023), W2-42a | Small. Machine: seconds. Risk: an untracked file the next cleanup or reboot can lose | The aim's need (3): role separation (the builder never writes acceptance tests; reviewers never fix) | In the aim; reachable in ordinary work (parser misreadings, W2-42a); a lost test means a fail-open goes unseen | **Keep, and move the tests into `tests/unit/hooks/`.** In a fresh repository this would be the first thing lost | One product-spec or engineer task, est. 1 to 2 hours | none |
| E-6 | **The CTO's tools hard-code this repository's path.** 247 mentions in 163 files; 5 cron lines; `dispatcher.py:65`, `merge_queue.py:34` | `governance/project/orchestration/tools/`, `.gov-runtime/scratch/orchestrator/tools/`, prompts, briefs, `crontab -l` | A fresh repository: every one re-pathed and re-verified live (est. 0.5 to 1 day plus a live pass of the dispatcher and the Load Balancer). Keep path: no cost now | Nothing; these are constants | Not a guard | **Keep the paths for now;** derive the root from the file's place when the dispatcher goes into the product (W2-121, W2-117), since EXAMIN needs it then | A KPI line in W2-121 ("no absolute path to the development repository"), est. hours | W2-121 |
| E-7 | **79 branches and 73 worktrees** (`git branch -a`, `git worktree list`), 27 tickets in progress, 71 open | `~/gov-os-worktrees/*`, `w2/*`, `emg/*` | Disk and attention. Each worktree's `.gov-runtime/` is about 300 MB of store (`store.db` 313,782,272 bytes), est. up to about 20 GB if every worktree holds one | Work in flight | Losing in-flight work is what the aim forbids; stale worktrees protect nothing | **Prune after the landing**: delete merged branches and their worktrees (46 of the 75 local branches are already merged into `w2/integrate`: `git branch --merged w2/integrate`). A fresh repository would "solve" this by abandoning them, which is the same as deleting without checking | A CTO sweep with a list for the owner, est. 1 to 2 hours | DEC-1047 (1)'s landings |
| E-8 | **The lifted features' suites run with everything else.** DEC-953 item 1: "the lifted features stay built and tested". For example containment (`guard/containment.py` 1,744 lines), the close (`close/` 4,767 lines), ratchet, history, trailers; their suites W1-30 3,915 s, W2-54 4,216 s, W1-41 2,159 s, W1-26 966 s and so on (`INVENTORY-TESTS-CODE-1.md` §2) | `src/gov/close`, `src/gov/guard/containment*`, `tests/acceptance/W1-30`, `W1-41`, `W2-54`, `W1-26`, and others | The 11-02 nightly took 19,448 s wall (inventory §2). A fresh repository would leave these suites behind. That is the largest single machine saving it promises | Features the product keeps for adopters | Not reachable in this repository's ordinary work while lifted here (DEC-953) | **Move to a weekly run** (or the nightly only), never in tickets' scoped runs, until "whole" (W2-81 and EXAMIN). The same saving as a fresh start, with the code kept | A `serial-only`/marker route plus `select_tests.py`'s exclusion; parts A1 and B1 give the exact list | parts A1 item 3, B1 |
| E-9 | **W2-61's memory measure is tied to this corpus.** Its 20 visible and 20 hidden questions' gold answers are governing sources in this repository (the register, the Contract; `.tickets/DAEO-iw1f.md` KPIs 1 to 4) | `src/gov/retrieval/measure.py`, `fixtures/evaluation/memory-retrieval/` (hidden half not read), DEC-828, DEC-833 | Fresh path: the measure must be re-sourced or rebuilt by an independent session, est. 1 to 2 days, and memory's baseline series (W2-61 to W2-126) breaks | The aim's need (1): it is the only standing proof that memory works | In the aim, ordinary work, and losing it loses work | **Keep.** This is a reason against the fresh path | none | none |
| E-10 | **The record branch and the owner's push** | `record/w2` (159 commits ahead of `w2/integrate`, an orphan branch: DEC-887); the owner pushes both branches (DEC-959 RR-Q2; DEC-953 item 9) | Fresh path: a new remote (`git@github-gov-os:UK-RH-HK/gov-os.git` today, through an ssh host alias), a new record branch, a new push routine; the owner's hours (est. 1 to 2). Keep: none | The orchestration record and the owner's control of what leaves the machine | In the aim (recording the work) | **Keep** | none | none |
| E-11 | **(For the combiner) the ratio of ceremony in the memory fixes themselves.** Lines added against `w2/integrate`, as src / unit / acceptance / records-and-docs: W2-112 400 / 532 / 2,906 / 303; W2-122 294 / 278 / 1,071 / 131; W2-123 370 / 486 / 1,908 / 202; W2-126 223 / 272 / 1,241 / 288 | `git diff --numstat w2/integrate...w2/W2-1xx` | 1,287 product lines carry 7,126 acceptance-test lines (5.5×) and 924 record lines | KPI coverage | Partly: acceptance tests are in the aim (need 3). Their size is a part A/B question | Note only; parts A1, A2, B1 judge it | — | — |

## Evidence

### 1. The two paths, costed

**Common to both:** the memory work DEC-1047 (1) keeps running lands first. W2-112 (20 commits ahead, review round
2 failed on F9, with the owner), W2-122 (17), W2-123 (20) and W2-126 (14) are all **not merged**
(`git merge-base --is-ancestor`). A fresh repository taken before they land would leave out the very
infrastructure the owner kept running. Taken after, it waits for them as the keep path does.

**The fresh path, step by step** (estimates from the measured lead-hours per profile in
`packages/PLAN-W2-DEC953.md` §2.0: L 4.3 h, S 9.2 h, F 13.6 h median, and from the sizes below):

| Step | What | Est. days |
|---|---|---:|
| F1 | Untangle E-2's four edges, then copy memory: about 7,600 product lines | 0.5 to 1 |
| F2 | Port the memory tests: unit (retrieval 126, semantic 11, store 20, rebuild 40, retrieve 4, codeintel 12 cases), and acceptance W1-15 to W1-24, W2-54, W2-87 and W2-108. That is **844 cases, 17,415 code lines, 6,537 s** (inventory §2), bound to `tests/conftest.py`, `template/` and `fixtures/` (78 files). Under MR-3, test designers must re-home the acceptance tests; the engineer cannot | 2 to 3 |
| F3 | The guard's five rules: copy the hook (1,705 lines) and the guard modules it imports (`decide` 1,222, `reads` 1,502, `heldout` 175, `install` 251, `runs` 162, `protected` 519, `util.gitenv` 179), or rewrite them small. A rewrite reopens the parser misreadings that took ACT-GUARD-FIX-2, ACT-GUARD-FIX-3 and W2-42a to close | 1 to 2 |
| F4 | Roles (6 files, 16 KB), skills (196 KB), kernel template, `tk` (1,510 lines of bash, standalone, identical to `~/.local/bin/tk`): copied; the generated `.claude/agents` and `.rulesync` rebuilt | 0.5 |
| F5 | The dispatcher, the Load Balancer, the merge queue and the heavy slots (dispatcher 3,191 + balancer 347 + merge queue 1,296, standard library only, so they copy cleanly), re-pathed (E-6: 247 mentions, 5 cron lines), then a live pass | 0.5 to 1 |
| F6 | A new pin from the new repository (`~/.local/bin/gov → pin-a7182f6c` today; the hook imports `gov.guard.*` from the pin), as an ACT with checks and rollback (DEC-1037's pattern took a window) | 0.5 + an owner ACT |
| F7 | The remaining Wave 2 tickets re-filed: 98 open or in progress, carrying 3,105 DEC citations in `.tickets/`; the plan re-baselined (DEC-105's third option); the owner approves | 1 to 2 |
| F8 | Re-source or rebuild W2-61's measure (E-9) | 1 to 2 |
| F9 | The first cold rebuild of the new corpus: est. 15 to 30 min if the corpus is 20 to 40 % of today's (from the 4,709 s measured), less if W2-126's machine-wide cache (keyed by the text) is on | 0.1 |
| **Total** | | **about 8 to 14** |

**Owner time on the fresh path** (est. 3 to 6 hours): the new GitHub repository and its key or ssh host alias, the
copy list's approval, the rule for carrying citations, the re-pin ACT, the re-baselined plan, and the new push
routine.

**What the fresh path leaves behind:**
- the register: 1,043 entries, cited **18,360 times**. Measured with `git ls-files <tree> | xargs grep -ohE
  "DEC-[0-9]{3,4}" | wc -l`: `src` and `template` 1,694, `tests` 11,975, the Contract 1,586, `.tickets` 3,105;
- the records: 345 checkpoint files, 60 probes, 18 closes, 129 packages; the store holds 1,815 records, 3,591
  commits, 5,316 trailers and 975 register entries;
- `record/w2`;
- about 3,900 commits of history on `w2/integrate`;
- every test of the lifted features.

The old repository stays on origin, so nothing is destroyed. But it is no longer searchable from the new one:
`lexical.py:6` defines the corpus as one root's `git ls-files`. Either the archive goes back in, in which case the
start is not fresh, or memory forgets why every rule exists. The Contract (286 files, 489 KB) is the spec and must
be carried, and its 1,586 citations then dangle.

**The keep path:** the lifts rows A1 to D recommend, by configuration where they are product (DEC-1045 shows the
form: `governance/project/secrets.yaml`, `scan: off`, one commit), plus E-2 to E-8 (est. 2 to 4 days in total,
mostly E-2, E-4 and part A1's context fix). No new pin beyond DEC-1037's planned window 2. No ticket re-filing:
part D's keep, merge and retire list applies in place.

### 2. Coupling, measured
`python3 -I /tmp/gov-os-inv-E/imports.py <repo>` gives the package-to-package import edges. The main ones:

| Package | Imports |
|---|---|
| `close` | `tasks` (21 imports), `cli` (10), `store` (5), `util` (5), `guard` (3), `check` (3), `checkpoint` (3), `config` (3) and 5 more |
| `retrieval` | `store` (5), `cli` (3), `config` (3), `secrets` (2), `util` (2), `guard` (1), `closure` (1), `records` (1) |
| `store` | `close` (2), `config` (1), `retrieval` (1) |
| `decisions` | `store` (6), `cli` (4), `guard` (1), `retrieval` (1) |
| `secrets` | `guard` (1), `config` (1) |
| `guard` | `util` only |

`python3 -I /tmp/gov-os-inv-E/closure.py <repo> gov.retrieval.retrieve … gov.retrieval.ollama` gives the memory
stack's closure: **18,063 lines in 77 modules**. It includes:
- `close.command` (1,466);
- `guard.containment` (1,744);
- `guard.reads` (1,502);
- `guard.decide` (1,222);
- `check.runner` (450);
- `telemetry` (632).

Only the four edges named in E-2 bring these in. The guard depends on nothing but `util`. The dispatcher and merge
queue import only the standard library (`grep` of their imports), so they are the cleanest pieces to move.

### 3. The fresh start's benefits, and where each can be had here
| What a fresh start would give | Measured today | Had here by |
|---|---|---|
| A small, fast memory | 55,591 chunks, 60 % tests; cold embedding 4,709 s | E-3 (namespaces) |
| A short register | 1.66 MB, 1,043 entries | E-4 (archive split), part A1 item 4 |
| No slow suites of lifted gates | nightly 19,448 s wall on 11-02 | E-8, parts A1 and B1 |
| A clean workspace | 79 branches, 73 worktrees | E-7 |
| No ceremony in the way of work | the briefs, the CTO's practices, the trailers, the packages | parts A2, B2 and C. These are practices: they would move to a new repository with the CTO's prompt unless lifted, and a lift works the same here |

### 4. Why the confidence is not higher
- A fresh repository has one benefit the keep path cannot match: **a hard reset of habits**. If the owner judges
  that the lifts will not stick here (each emergency has re-added ceremony: DEC-953, then DEC-1033, DEC-1039 and
  DEC-1047), a new repository forces every carried piece to be justified.
- **The middle way:** treat the new list as that reset in this repository. Every rule the combined list keeps is
  re-recorded in one new in-force file. Everything else is archived (E-4) and switched off by configuration. No
  rule comes back without a DEC-1010 test line.

### 5. Commands used
- `wc -l`, `find` over `src/gov/*`;
- `/tmp/gov-os-inv-E/imports.py` and `closure.py`;
- `git rev-list --count` and `git merge-base --is-ancestor` for the branches;
- `git diff --numstat w2/integrate...w2/W2-1xx`;
- the store, read-only: `sqlite3 'file:.gov-runtime/store.db?mode=ro'` (chunks by path; table counts);
- `git ls-files … | xargs grep -ohE "DEC-[0-9]{3,4}"`;
- `grep -rl /home/usain/Dynamic-Agentic-Engineering-OS` over the tools; `crontab -l`;
- the lead logs `log/*.json`: 439 with `total_cost_usd`, $3,188 in total, median $3.6 and 1.09 h per run. That is
  context for pricing re-done work: about 20 to 40 more lead runs on the fresh path, about $70 to $150 (est.).
