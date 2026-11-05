# D4B link census: every link the repository states, against the graph's edges (DEC-1072 (1))

- **By:** the research role (one session, Claude Opus 5.5), for the CTO, under DEC-1072 (1), DEC-1071 (1) (the graph)
  and D4B-STRUCTURE G1.
- **Date:** 2026-11-04.
- **Measured at:** the m6 clone `~/gov-os-runs/D4B/m6/repo`, commit `24f06026`. Its store `.gov-runtime/store.db` was
  built by a rebuild at that head (fingerprints row `24f06026…`, kind `rebuild`).
- **Method:** read-only. No model, no GPU, no `gov retrieve`, no network.
  - **The graph as the product sees it:** `gov.records.records/edges` and `gov.closure.closure`.
  - **Its rules:** read in `src/gov/store/loader.py` and `src/gov/retrieval/retrieve.py` (`_graph`), and in
    `authority.py` (`register_entries_of`, `Order`).
  - **The stated links:** the clone's files, its `git log` and the store's `lexical_chunk` table, parsed by one script,
    `docs/research/D4B-link-census.py`. It is run as
    `PYTHONPATH=<clone>/src python3 census.py <clone> <out.json>` and takes about a minute.
  - **Columns:** *pairs* counts distinct source→target pairs. A pair is *resolvable* when its target is a store record
    (a W1-/W2- id counts through its ticket's `wbs_id`). A pair is *in the graph* when an edge of any type joins the
    two, either way: the closure follows edges both ways.
  - **Approximation:** every pattern is a regular expression. Where a count is approximate, the table says so.

## 0. What the graph holds and how it is built
- **Records:** 2,034. That is 1,072 decisions (1,065 register entries and 7 decision files), 364 checkpoints,
  276 capabilities, 194 tickets and the rest.
- **Edges:** 757: DEPENDS_ON 743, CONSTRAINS 9, SUPERSEDES 3, IMPLEMENTS 2.
- **What the edges connect:** ticket→ticket 440, capability→capability 214, capability→Contract 62, plan 17, spec 9,
  lesson→ticket 6, decision 9.
- **Decisions with any edge at all: 7 of 1,072.** Tickets with any edge: 179 of 194.
- **How an edge is made (the loader):**
  - A front-matter key whose name is one of the eight edge types, in lower case, becomes an edge.
  - So does `superseded_by`.
  - In the register, a `**Supersedes:**` on the entry's first line, holding ids alone, becomes an edge. That gives the
    3 SUPERSEDES edges: DEC-048→DEC-038, DEC-051→DEC-048 and DEC-961→DEC-960.
  - No other key and no text becomes an edge.
- **What retrieval treats as not current (`_graph`, `authority`):** status SUPERSEDED (8 entries), a SUPERSEDES target
  (3), or status DEPRECATED, REJECTED or WITHDRAWN.
- **A register chunk is never dropped** (`in_register`). A not-current entry only loses its authority lift.
- **The bundle carries no currency flag**, so the agent sees only the chunk's own text.
- **Trailers:** the store keeps `Task:` and `Implements:` in a `trailers` table. They are not edges, and the closure
  does not read them.
- **What the closure reaches from a ticket (radius 1):**
  - From W2-21 (`DAEO-1ahb`, `sources:` DEC-902, DEC-715, DEC-434, DEC-743): 8 tickets and 0 decisions.
  - From DEC-715, DEC-183 or DEC-140: only the decision itself.

## 1. The census

*Followable today:* **graph** means the closure or record route reaches the target from the source. **Keyword only**
means the source's text is in the lexical index and names the target's id, so a keyword search on that id can surface
it. **No** means the text is not indexed and is not an edge (git history).

| Kind | Where stated (form) | Instances | Distinct pairs | Resolvable | In the graph | Followable today |
|---|---|---:|---:|---:|---:|---|
| **Decision → decision** | | | | | | |
| supersedes (Supersedes, Replaces, Withdraws, Reverses; "superseded/replaced/withdrawn/reversed/ended by") | register: `**Changed by:** superseded by` 16, `replaced by` 14, `**Replaces:**` 8, `**Supersedes:**` 6, `**Withdraws:**` 4, free text 15 | 71 statements | 55 | 55 | **3** | graph only for the 3; else keyword only |
| amends (Amends, Changes, Corrects, Narrows, Restores, `Lifted by`, `Changed by` without "superseded", "(amended here)", "amended/changed/corrected by") | register: `**Changes:**` 172, `**Changed by:**` 130, `**Amends:**` 64, `**Lifted by:**` 15, `**Corrects:**` 9, free text 31 | 442 statements | 340 | 340 | **0** | keyword only |
| refines / extends / settles / ratifies / confirms / implements | register labels (`**Refines:**` 59, `**Extends:**` 24, `**Ratifies:**` 19, `**Settles:**`, `**Confirms:**`, `**Implements:**` 8 each) | 138 | 133 | 133 | 0 | keyword only |
| under (the governing decisions) | register `**Under:** DEC-n, …` (796 entries) | 2,458 | 2,458 | 2,458 | 0 | keyword only |
| under/implements a capability, MR, ADR or ticket | register `**Under:**` / `**Implements:**` values | 294 | 294 | 293 | 0 | keyword only |
| cites (any DEC id in an entry's span but its own) | register text, everywhere | 7,287 | 4,987 | 4,986 | 6 | keyword only |
| change-log rows "(…; supersedes/amends DEC-n)" | register text outside entries | 4 | 4 | 4 | 2 | keyword only |
| own status line marks the entry changed | `**Status:** SUPERSEDED …`, "amended by", `Changed by:` on line 1 | 151 entries | n/a | n/a | 8 by status word | status word only |
| X superseded/changed by Y (curated) | `orchestration/ARCHIVE-SUPERSEDED.md` §A | 83 | 82 | 82 | 0 | keyword only |
| decision spent (a state) | ARCHIVE-SUPERSEDED.md §B "Spent" | 111 ids | n/a | 111 | 0 | keyword only |
| **Ticket →** | | | | | | |
| decision, `sources:` | `.tickets/*.md` front matter | 807 | 807 | 807 | **0** | keyword only |
| capability / MR / ADR, `sources:` | front matter | 304 | 304 | 264 | 0 | keyword only |
| `closes:` (DEC, CAP, AR, list rows) | front matter | 129 | 129 | 37 | 0 | keyword only |
| decision named in a KPI (`[DEC-n]`) | front matter `kpis` | 1,311 | 764 | 764 | 0 | keyword only |
| decision named in the body | ticket body | 910 | 698 | 698 | 0 | keyword only |
| *any DEC id in the ticket file (union of the three rows above)* | | | **1,378** | | **0** | keyword only |
| ticket, `depends_on:` | front matter | 440 | 440 | 440 | **440** | **graph** |
| ticket, `deps:` (tk's copy) | front matter | 436 | 436 | 436 | 430 | graph (through depends_on) |
| ticket, `links:` | front matter | 28 | 28 | 28 | 10 | keyword only (18) |
| ticket, `parent:` | front matter | 6 | 6 | 6 | 0 | keyword only |
| ticket named by W-id in KPIs or body | ticket text | 1,844 | 725 | 720 | 157 | mostly keyword only |
| list rows, `list_rows:` (W2-H001 …) | front matter | 566 | 566 | 0 (rows, no records) | 0 | keyword only |
| **Commits** | | | | | | |
| `Task:` → ticket | git log trailers (3,561 commits, 193 values) | 3,561 | 3,561 | 3,053 (496 are `decision-record`) | 0 | **no** (store table; `git log`) |
| `Implements:` → decision / capability / ticket | git log trailers (2,647 commits, 511 values) | 4,246 | 4,246 | 4,187 | 0 | **no** |
| ticket ⇄ decision through one commit's `Task:` + `Implements:` | derived | 4,246 | 1,176 (740 to DEC on real tickets; 341 of them not stated in the ticket file) | 1,151 | 0 | **no** |
| `Role:`, `Decided-by:` | git log trailers | 3,502 / 180 commits | 11 / 21 values | n/a (no records) | 0 | no |
| commit message names a decision | git log subject and body | 3,611 | 3,490 | 3,488 | 0 | no (messages not indexed) |
| **Contract and capabilities** | | | | | | |
| capability → provider ticket | `contract.yaml` `capabilities[].provider` (57 more are tools) | 159 | 159 | 159 | 0 | keyword only |
| capability item → provider ticket | `contract.yaml` `covers[].provider` | 203 | 203 | 203 | 0 | keyword only |
| capability (item) → decision | `contract.yaml` `sources` / `covers[].source` | 331 | 331 | 331 | 0 | keyword only |
| master rule → provider ticket / decision | `contract.yaml` `master_rules[]` | 32 / 18 | 32 / 18 | all | 0 | keyword only |
| capability item → capability → Contract | capability pages' `depends_on:` | 276 | 276 | 276 | **276** | **graph** |
| Contract text cites a decision | `CONTRACT_v4.md` | 506 | 108 | 108 | 0 | keyword only |
| **KPI → tests** | | | | | | |
| ticket → its acceptance tests | `acceptance_tests.path` | 173 | 173 | 104 (path exists) | 0 | keyword only (the path string) |
| test folder → ticket | `tests/acceptance/<W-id>/` (95 folders) | 95 | 95 | 95 | 0 | no edge; keyword on the path |
| test file names a decision / a ticket | `tests/**/*.py` | 7,615 / 4,131 | 3,847 / 2,087 | 3,801 / 1,904 | 0 | keyword only (tests indexed today) |
| test map: path → suite; comments → decision | `test-map.yaml` `couplings`; `# DEC-n` | 81 / 20 | 81 / 11 | 81 / 11 | 0 | keyword only |
| **Roles and skills** | | | | | | |
| role → skill | kernel role files | **0** | 0 | n/a | 0 | n/a: never stated |
| skill → role (by name) | kernel `SKILL.md` | 13 | 13 | 13 | 0 | keyword only |
| role / skill cites DEC, CAP, MR | role files / skills | 107 / 271 | 87 / 95 | all | 0 | keyword only |
| **Lessons and failures** | | | | | | |
| lesson constrains ticket | `docs/lessons/*.md` `constrains:` | 6 | 6 | 6 | **6** | **graph** |
| lesson → the decision it came from | lesson body `**Source:** DEC-n` | 6 | 4 | 4 | 0 | keyword only |
| failure record → its source | (no failure record exists beyond the template) | 0 | 0 | n/a | 0 | n/a |
| **Plan and path map** | | | | | | |
| plan → decisions | `docs/plan/*.md` front matter `decisions:` | 168 | 168 | 168 | 0 | keyword only |
| plan card → ticket; card → decision | `#### W2-n` cards; DEC-n under a card | 94 / 510 | 93 / 380 | 92 / 380 | 0 | keyword only |
| path map entry → decision | `path-map.yaml` comments | 69 | 33 | 33 | 0 | keyword only |
| **Other record front matter that the loader ignores** | | | | | | |
| checkpoint → ticket | `task:` | 364 | 364 | 363 | 0 | keyword only |
| close record → ticket / decisions | `task:`, `decisions_applied:`, `requirements_implemented:` | 226 | 226 | 221 | 0 | keyword only |
| spec / ADR → decisions | `decisions:` | 129 | 129 | 129 | 0 | keyword only |
| change records → decisions | `decisions_carried/recorded/read:` | 138 | 138 | 138 | 0 | keyword only |
| **Other text** | | | | | | |
| review package → ticket; → decision | `orchestration/packages/**` (approx.: any W-id in name or first 2,000 chars) | 629 / 3,209 | 629 / 1,400 | 626 / 1,400 | 0 | keyword only |
| in-force list → decision | `orchestration/DECISIONS-IN-FORCE.md` | 78 | 56 | 56 | 0 | keyword only |
| any other indexed file → decision | 598 files (checkpoints, research, briefs, src …) | 22,641 | 7,426 | 7,413 | 0 | keyword only |

**Totals:**
- The overlapping rows are left out: "cites" contains the register's typed rows, `deps:` repeats `depends_on:`, the
  commit-derived row repeats the trailers, and Role, Decided-by and "spent" are no pairs.
- Over the remaining 65 rows: **63,569 stated instances**, **37,815 distinct pairs**, of which **895 are in the graph
  (2.4 %)**.
- The 895 are almost all ticket `depends_on` (440), the capability tree (276), ticket W-ids already joined by
  depends_on (157), `links:` (10) and lessons (6).
- **Decision-to-anything pairs in the graph: 6** of about 9,000.

**Reconciliation with D4B-STRUCTURE G1:**
- G1's "9,111 citations" is every DEC mention in the register file, own ids included. The census counts 8,831 inside
  entries and **7,287** once each entry's own id is excluded.
- G1's "103 supersessions or amendments" is a different pattern set. Here the labelled and free-text supersede and amend
  statements number 513 (55 + 340 distinct pairs). Most of them are the `Changes:` and `Changed by:` labels, which G1's
  66 lines did not count.

**Approximations:**
- The labelled forms (`**Label:** ids`) are exact as patterns. The class of a `Changed by:` value is read from its verb
  ("superseded by" counts as superseding; no verb counts as amending).
- The free-text forms (46 of 513 statements) take their subject from the nearest id in the clause. Hand checks on 18
  statements found 1 wrong (DEC-1053, a branch "withdrawn by DEC-880") and 1 ambiguous (DEC-072, "Q4 is superseded by
  DEC-064").
- Ranges ("DEC-030…DEC-037", "DEC-285 to DEC-290") count only their two ends, so amendments are slightly undercounted.
- A `Changes:` value sometimes names a context id beside the changed one, so it slightly overcounts.

## 2. Drift: decisions an agent would retrieve as current although the register says they changed
**Current** is the brief's sense: status ACCEPTED, not in `not_current` (no SUPERSEDED status, no SUPERSEDES edge,
no must-not-cite status). **Stated** means an entry's labelled or free-text statement, the entry's own status line, or
ARCHIVE-SUPERSEDED §A.

| | Decisions stated | of them current | whole (ids alone) | no hint in its own entry | its register chunks / chunks with no hint |
|---|---:|---:|---:|---:|---:|
| superseded (whole or in part) | 57 | **43** | 1 (DEC-140) | **8** | 114 / **68** |
| amended (not superseded) | 205 | **196** (172 amended only) | 27 | **87** | 682 / **516** |
| **either** | | **215** | | **87** | 722 / **536** |

- **Already not current (correctly): 9.** DEC-038, DEC-048, DEC-049, DEC-636, DEC-798, DEC-869, DEC-875 and DEC-876
  by status (8); DEC-960 by edge (DEC-038 and DEC-048 also by edge).
- **Stated changed but PROPOSED, so not ACCEPTED, yet not dropped either: 13 more.** DEC-002, -005, -007, -024, -034,
  -037, -040, -043, -044, -045, -047, -056, -062 (for example, DEC-002/043/045/047 "superseded by DEC-058/064").
  Retrieval treats PROPOSED as current, so these count beside the 215 if PROPOSED counts as current.
- **Spent but current: 110 of 111.** These are the decisions ARCHIVE-SUPERSEDED §B calls "spent". It is a third drift
  kind, a state rather than a link, and the file says the register stays the authority.
- **Whole supersessions are rare: 1 of 43** (DEC-140, "withdrawn by DEC-842", status still ACCEPTED). In the other
  42 the statement names a part: an item, a cap, a rule ("its 300k context limit … superseded by DEC-838"). So a
  SUPERSEDES edge that drops its target as not current would be wrong for 42 of 43. They need an edge that brings
  the changing entry into view, with the target staying current.
- **"No hint":**
  - The changed entry's own span names none of the entries that change it, so the statement lives only in the other
    entry (or the archive). That is **8 superseded** and **87 amended** decisions.
  - At chunk level it is worse. Where an entry does carry a hint, it is usually its status line (34 of the 43 have
    one there), and that sits in the first chunk only.
  - So **536 of the 722 register chunks** of the 215 drifted entries carry no hint. An agent handed any of those
    chunks sees a current decision.
- **Superseded in part, current, no hint in its own entry (all 8):**
  - DEC-365 and DEC-407: their ancestry rule was replaced by DEC-409. Their own entries never mention DEC-409.
  - DEC-508 and DEC-723 (DEC-820 `Replaces:`).
  - DEC-605 (DEC-822 `Replaces:`).
  - DEC-709 ("replaces DEC-709 for good", DEC-719).
  - DEC-761 (item 1's line, DEC-772).
  - DEC-1066 ((2)'s wording, DEC-1067).
- **Twelve more superseded in part, current:**
  - DEC-183 (DEC-371).
  - DEC-208, DEC-237, DEC-248, DEC-451 and DEC-665 (DEC-838).
  - DEC-448 (DEC-477).
  - DEC-737, DEC-776 and DEC-786 (DEC-847).
  - DEC-843 and DEC-852 (DEC-880).
- **Amended, current, no hint in its own entry (examples):**
  - DEC-030 (DEC-080) and DEC-070 (DEC-096).
  - DEC-083 (DEC-163) and DEC-107 (DEC-117).
  - DEC-153 and DEC-157 (DEC-209).
  - DEC-176 (DEC-365, DEC-402) and DEC-235 (DEC-363).
  - DEC-250 (DEC-420) and DEC-290 (DEC-1045).
- **Most-changed current entries:** DEC-899 (7 changers), DEC-880 and DEC-884 (6 each), and DEC-492, DEC-936,
  DEC-938 and DEC-941 (5 each).

## 3. What an agent can and cannot follow
- **Through the graph, today:**
  - ticket→ticket `depends_on` (and `deps` through it);
  - the capability tree;
  - lesson→ticket;
  - 3 supersessions;
  - the rest of DEPENDS_ON (plans, specs).
- **Keyword only:** every decision link (supersede, amend, under, cite), and every ticket→decision link. The same
  holds for capability→provider and capability→decision, plan→decisions, checkpoint/close/change→ticket or decision,
  and every test, skill and role citation. An agent reaches these only by searching the id, and then:
  - it finds the chunks that name the id, not the relation;
  - a search on a changed decision's id surfaces its changers among every other mention of it (a median decision is
    cited by several entries, 4,987 pairs in all), with nothing to say which is the change.
- **Not at all:** commit trailers and commit messages. They are not indexed and not edges; the store's `trailers`
  table is read by `gov close`/`status`, not by retrieval. Role→skill is never stated.

## 4. The kinds to build, ranked (instances × how often an agent needs them)
"Need" is judged from who starts from what:
- every launched worker session and `gov retrieve --ticket` closes over its ticket;
- every cited decision falls under the retrieval skill's rule that no superseded record is cited as current (CAP-51);
- the auditor and the test designer start from a ticket's KPIs and the Contract.

1. **Ticket → its decisions.**
   - Pairs: 1,378 stated in ticket files; 807 in `sources:` alone, the most structured. Commits'
     `Task:`+`Implements:` add 341 more, for 1,719 in all.
   - In the graph: 0. 188 of 193 tickets name at least one decision (median 6).
   - Need: highest. A ticket's closure today reaches tickets only (W2-21: 0 of its 4 sources).
   - Build: first `sources:` as edges; then the KPI- and body-named ids; then the commit-derived pairs. These need no
     commit nodes, only ticket→decision edges derived at rebuild.
2. **Decision supersedes/amends decision**, including the incoming `Changed by:` and `Lifted by:` forms and the
   archive's §A.
   - Pairs: 395 distinct (55 + 340). In the graph: 3.
   - Drift: 215 current decisions, 87 of them with no hint in their own entry, and 536 chunks with no hint.
   - Build two types:
     - SUPERSEDES only where the statement names ids alone. Here that is DEC-140, plus the status-SUPERSEDED cases
       already read.
     - AMENDS (or "changed by") for the rest, the 42 partial supersessions included.
   - Then the closure's one-hop step from G1. A drop rule on partial statements would hide 42 decisions that are
     still in force in part.
3. **Decision under decision** (`**Under:**`).
   - Pairs: 2,458, every one labelled and resolvable. In the graph: 0.
   - Need: high for "what governs this". It is K6, the hop kind in 2 hidden misses (G1).
   - Build as DEPENDS_ON-like edges.
   - The remaining free citations (4,987 pairs, a superset) should wait. They are 2.4× the under pairs, and following
     every one at one hop would crowd the closure; measure the typed kinds first.
4. **Other records' front-matter id keys the loader ignores.**
   - The keys: checkpoint `task` 364, close `task/decisions_applied/requirements_implemented` 226, plan `decisions`
     168, spec and ADR `decisions` 129, change records 138.
   - About 1,025 pairs, 0 in the graph. One loader rule covers them all (cheap).
   - Need: medium. What a ticket did, and what a plan rests on.
   - Note: DEC-1052 M-4 keeps close and checkpoint records out of the embeddings; their edges are a separate matter.
5. **Capability ↔ provider ticket and capability → decision.**
   - Pairs: 394 provider pairs (capability 159, item 203, MR 32), 349 decision pairs, and the tickets' `sources`
     (304) and `closes` (CAP) back. In the graph: 0.
   - These live in `contract.yaml` (not a record file), so the capability pages, which are generated, would have to
     carry them in front matter.
   - Need: medium (the auditor, Contract coverage).
6. **Ticket `links` (18 not in the graph) and `parent` (6).** Small and cheap; build alongside 4.
7. **KPI → tests.** 173 `acceptance_tests.path` (104 exist) and 95 test folders. Tests are not records and are
   leaving memory (DEC-1052 M-4). Not an edge kind now; the path string serves keyword search.

**Not supported by the evidence:**
- role → skill: 0 statements;
- lesson → source: 4 pairs;
- failure → source: no failure records.

**Already well served:**
- ticket `depends_on` (440/440);
- the capability tree (276/276);
- lesson `constrains` (6/6).

**Residuals:**
- **Spent decisions:** 110 current. This is a state stated only in an orchestration file, not the register. It is
  outside an edge build and goes to the owner if it is to count against currency.
- **Commit nodes:** none are proposed. Only the derived ticket→decision pairs are.
- **Edge types:** how many and which, for "amends" and "under", is the prototype's call.
