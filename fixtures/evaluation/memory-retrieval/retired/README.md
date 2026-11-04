# Retired questions of the memory-retrieval set

This folder keeps questions and labels taken out of the set, with their history and the reasons. The measure
results of retired labels are kept outside this folder (DEC-1068: blind checkers read this folder for the form). It is not a part of the set: the measure
reads only `<set>/visible/*.yaml` and the hidden part, never this folder, and `fixtures/` is a namespace the indexer
does not read, so nothing here is scored or retrieved.

## q03-lens-b.yaml: lens B's Q03, retired 2026-11-03

- **What it was:** lens B's Q03 (Table 2 of `docs/assessment/2026-10/B-memory-retrieval.md`), "Why are query
  embeddings computed on a CPU-only embedder?", written into the visible half by W2-61 at commit 23079f92a6fa
  (commit 8d09eb40, 2026-10-29). Its gold answer and its sources (DEC-798's entry, `semantic.py` lines 12-17,
  `ollama.py` lines 8-11) state DEC-798's CPU-only rule. The file here is that file, byte for byte.
- **Why it was retired:** the owner's decision of 2026-11-03 (in the chat; recorded in the register by the CTO).
  On 2026-11-02 DEC-1033 replaced DEC-798's CPU-only rule (commit 75f18d1118c7 changed `src/gov/retrieval/semantic.py`
  and `ollama.py`: a question's vector is used from any device and the query daemon starts with the GPU visible).
  A question that rewards a replaced decision works against memory's own design (W2-55, W2-87: superseded entries
  left out, authority ranking) and against the basis. Measure 1 had not run yet and becomes D-4b's baseline, so the
  rewrite costs one question's history only.
- **Its replacement:** `visible/q03.yaml`, still `id: Q03`, category `decision`, asks where query embeddings are
  computed now, on which device, and why, with DEC-1033's entry and today's `semantic.py` and `ollama.py` as its
  sources (written at commit acfea6d9d4ef). Figures for Q03 before 2026-11-03 are the old question's, and are not
  comparable with the new one's.

## q09-lens-b.yaml: lens B's Q09 label, retired 2026-11-03

- **What it was:** lens B's Q09 (Table 2 of `docs/assessment/2026-10/B-memory-retrieval.md`), "How large may the
  context packet be?", written into the visible half by W2-61 at commit 23079f92a6fa (commit 8d09eb40, 2026-10-29).
  Its one source was W2-04's ticket KPI lines (`.tickets/DAEO-u4oz.md`, `kpis:`, lines 24-36). The file here is that
  file, byte for byte.
- **Why its label was retired:** the owner's decision of 2026-11-03, DEC-1066 (4) (in the chat; recorded in the
  register by the orchestrator). The label named only the ticket's KPI lines, while the rule's governing source, the
  Contract's envelope (its token budget: "Context packet ≤ ~6k tokens"), was not a gold source, so a search that
  answered from the Contract would count as a miss. The question and the gold answer were not wrong and are kept; only
  the sources changed. The new label was set blind by a session independent of the retrieval work (the independent
  test designer): its sources decided from the question, the gold answer and the repository, before any past result
  below was read, and never from a retrieval run.
- **Its replacement:** `visible/q09.yaml`, still `id: Q09`, the same question and gold answer, with one entry of six
  alternatives, any one of which counts (written at commit 68ce354a74c7): the Contract's token budget in
  `docs/contract/contract.yaml` (`  token_budget:`, lines 52-60) and in `docs/contract/CONTRACT_v4.md` (the
  `- **Token budget**` line, line 44); CAP-15's acceptance in `contract.yaml` (`- id: CAP-15`, lines 962-969), in
  `CONTRACT_v4.md` (`### CAP-15 — Context packet compilation`, lines 256-273) and in
  `docs/contract/capabilities/CAP-15.md` (`# CAP-15: Context packet compilation`, lines 11-19); and the ticket's KPI
  lines, kept. Figures for Q09 before 2026-11-03 are the old label's: the new one counts more sources, so they are
  not comparable.

## q16-pre-dec1067.yaml: lens B's Q16 label, retired 2026-11-04

- **What it was:** lens B's Q16 (Table 2 of `docs/assessment/2026-10/B-memory-retrieval.md`), "How much free memory
  must the resource gate see before a heavy run?", written into the visible half by W2-61 at commit 23079f92a6fa
  (commit 8d09eb40, 2026-10-29). Its gold answer, MemAvailable of at least 4 GiB plus 2.4 GB while the CPU embedder
  is not loaded, and its one source (DEC-798 item 4, `docs/DECISION_REGISTER.md` line 8737) state DEC-798's rule. The
  file here is that file, byte for byte.
- **Why it was retired:** the owner's DEC-1067 (c) (2026-11-04, in the chat; recorded in the register by the
  orchestrator): a blind label check by a session independent of the retrieval work (the independent test
  designer). The label was wrong. DEC-798 is SUPERSEDED by DEC-1033, and DEC-942 item 2 had already replaced its
  fixed gate figures with the measured gate. The rule in force is DEC-961 item 1, with DEC-947 item 5's floor, so the
  label rewarded a superseded decision (as q03's did). The question was not answerable as asked either: today a
  "heavy run" (a test run or a rebuild) takes a heavy-job slot (DEC-979 D1, DEC-1038 (4)), while the memory rule
  DEC-798 item 4 set figures for is the launch gate's.
- **Its replacement:** `visible/q16.yaml`, still `id: Q16`, category `decision`, written at commit 03df21248e36. It
  asks how much free memory the resource gate must see before it launches a new lead. Its sources are two pieces.
  The first, the rule, is one entry with two alternatives: DEC-961 item 1 (`docs/DECISION_REGISTER.md` line 12039)
  and W2-20's KPI line (`.tickets/DAEO-r30l.md` line 36). The second, the floor of 3 GiB, is DEC-947 item 5 (line
  11726). Figures for Q16 before 2026-11-04 are the old question's and are not comparable with the new one's.
- **Past results:** not read. The check was blind (DEC-1067 (c)): this session read no measure record and no
  retrieval result, so no table is given here. One may be added from the records by a session that is not judging
  the label.

## q19-pre-dec1067.yaml: lens B's Q19 label, retired 2026-11-04

- **What it was:** lens B's Q19 (Table 2), "May an engineer write acceptance tests?", written into the visible half
  by W2-61 at commit 23079f92a6fa (commit 8d09eb40, 2026-10-29). It had one entry of three alternatives: the
  Charter's MR-3 (`docs/charter/CHARTER_v5.md`, lines 93-96) and the allowed paths of `engineer.md` and
  `independent-test-designer.md` (lines 8-10 each). The file here is that file, byte for byte.
- **Why its label was retired:** the owner's DEC-1067 (c), the same blind check. The question and the gold answer
  hold today and are kept: MR-3, the guard's rule kept by DEC-953 item 2, and G-14 (DEC-1056, DEC-1059). The label
  left out the Contract, which carries MR-3's acceptance (the guard refuses an implementer's write to
  `tests/acceptance/**`, as it does to every role but the Independent Test Designer) as fully as the role files
  state it. A search that answered from the Contract would therefore count as a miss, as under Q09's old label (DEC-1066 (4)).
  The Charter's span also stopped one line short of the line that puts the acceptance-test paths outside the
  implementer's allowed paths.
- **Its replacement:** `visible/q19.yaml`, still `id: Q19`, with the same question and gold answer, written at commit
  03df21248e36. It has one entry of six alternatives, any one of which counts. Lens B's three are kept, the Charter's
  span now running to line 97. Added: MR-3 in `docs/contract/contract.yaml` (`- id: MR-3`, lines 136-142), in
  `docs/contract/CONTRACT_v4.md` (its table row, line 57) and in `docs/contract/master-rules/MR-3.md`
  (`# MR-3: ...`, lines 11-16). Figures for Q19 before 2026-11-04 are the old label's: the new one counts more
  sources, so they are not comparable.
- **Past results:** not read, as for Q16.

## q03-pre-dec1067.yaml: q03's DEC-1033 label, retired 2026-11-04

- **What it was:** the owner's rewritten Q03 of 2026-11-03, "Where are query embeddings computed now, on which
  device, and why?", written at commit acfea6d9d4ef (commit 68252f5c). Its gold answer said that a question's vector
  is used from whichever device computed it, CPU or GPU (DEC-1033 (2) (b), "accepted from any device"). It had one
  entry of three alternatives: DEC-1033's entry (`docs/DECISION_REGISTER.md`, lines 12838-12845), `semantic.py`
  lines 12-18 and `ollama.py` lines 8-12. The file here is that file, byte for byte.
- **Why its label was retired:** the DEC-1067 (c) form (a blind label check by a session independent of the
  retrieval work, the independent test designer), on the CTO's order after W2-32's review (F-9), once W2-32 merged
  into `w2/integrate` at b32e8504. The label was wrong. DEC-1065 (1) (the owner, 2026-11-03: no CPU fallback for
  embeddings, anywhere), carried out by W2-32 S10, makes the GPU the only device. A vector computed on the CPU is
  now refused (`EMBEDDER_ON_CPU`) and never cached or stored. `gov` never starts an embedder for a search: an
  unreachable embedder makes the semantic part unavailable, and the search answers by keywords. So the answer's "CPU
  or GPU" no longer held, and DEC-1033's entry, which states "any device", was no longer gold. `ollama.py`'s cited
  lines had also changed (the measure's pre-check found entry 1.3 unresolved). The question still holds and is kept.
- **Its replacement:** `visible/q03.yaml`, still `id: Q03`, with the same question and category, written at commit
  b32e8504b8d3. It has one entry of four alternatives, any one of which counts, the governing source first:
  DEC-1065's entry (`docs/DECISION_REGISTER.md`, lines 13145-13148), W2-32's S10 KPI line (`.tickets/DAEO-0pyc.md`,
  line 39), `semantic.py`'s docstring lines on the question's vector (lines 12-18) and `ollama.py`'s on no CPU
  fallback and the two daemons (lines 3-17). Figures for Q03 before 2026-11-04 are the old label's and are not
  comparable with the new one's.
- **Past results:** not read, as for Q16.

## The labels retired 2026-11-04 under DEC-1069 (`<id>-pre-dec1069.yaml`)

These come from the owner's DEC-1069 (1) to (3) (2026-11-04, in the chat; recorded in the register by the
orchestrator), which apply the fixes of the visible half's audit (`docs/research/memory-measure-audit/VISIBLE.md` §4
and §5). The independent test designer, a session independent of the retrieval work, checked each one blind against
the repository at cc9c94d42a54 and read no result. Each file here is the label as it stood at cc9c94d42a54, byte for
byte. Its replacement is `visible/<id>.yaml`, whose header comment gives the detail. Figures for a re-labelled
question before 2026-11-04 are the old label's.

- **q02-pre-dec1069.yaml** (lens B's Q02, W2-61's 8d09eb40): its gold answer named the cache file
  `.gov-runtime/query-vectors.db`. At cc9c94d42a54 the file is `.gov-runtime/query-vector-cache.db`
  (`QUERY_VECTORS_REL`). Only the file name was re-worded.
- **q03-pre-dec1069.yaml** (q03's DEC-1065 label, a9ef6f82): it had one entry of four alternatives, and no single
  one held all three asked facts (DEC-1065's entry names no host; W2-32's S10 line gives neither where nor why). It
  is split into two entries, as DEC-1069 (3) confirms: where (`ollama.py` 3-17 or `semantic.py` 12-18), and the
  device and why (DEC-1065's entry or `semantic.py` 12-18). S10's line is left out. The question and the gold
  answer are kept.
- **q04-pre-dec1069.yaml** (lens B's Q04, 8d09eb40): it cited DEC-004 (PROPOSED, not the governing source),
  `CAP-15.g.md` (it states only the ~2.5k summary) and `retrieve.py`'s `BUNDLE_BUDGET` (the retrieval bundle's
  budget, another limit), and was categorised `decision`. It is re-labelled to the Contract: CAP-15 in
  `contract.yaml` added, the Contract's envelope (`token_budget`, and its line in `CONTRACT_v4.md`) added, the three
  dropped, and category `contract`. The question is kept, beside Q09 (DEC-1069 (2), option (a)).
- **q07-pre-dec1069.yaml** (lens B's Q07, 8d09eb40): its gold answer gave 27 tickets, DAEO-g0ip to DAEO-7rr2, but
  DAEO-0mab's `depends_on` holds 23, DAEO-g0ip to DAEO-2bdu: d7d41d6e (DEC-954) took nine out and put five in. Its
  ticket span (17-44) also ran into `allowed_paths`. The gold answer is now the 23, and the span is 17-40.
  Volatile (DEC-1069 (6)).
- **q09-pre-dec1069.yaml** (Q09's DEC-1066 (4) label, f1a01dfe): categorised `ticket`, while the Contract governs
  the answer. Its category is now `contract`; nothing else changed.
- **q10-pre-dec1069.yaml** (lens B's Q10, re-anchored at ba08ca77): its gold answer gave lines 115 and 185, while
  the calls are at 270 and 188. The line numbers are dropped.
- **q11-pre-dec1069.yaml** (lens B's Q11, re-anchored at 320b98f3): its gold answer gave lines 62 and 135 (the calls
  are at 80 and 283) and left out the code route that `retrieve` fuses when the question names a symbol (W2-92). The
  line numbers are dropped and the code route is named.
- **q12-pre-dec1069.yaml** (lens B's Q12, re-anchored at bc1219c1): its gold answer gave three cases, but W2-32's S7
  added two more for the same token (a malformed list of expanded parents or of spans sent alone, through
  `_expanded_of` and `_alone_of`). They are added. The source is kept.
- **q13-pre-dec1069.yaml** (lens B's Q13, 8d09eb40): entry 1's span ended before the deciding check (`if used +
  cost <= limit:`), and entry 2's `retrieve` alternative ended before the line that takes the limit. They are
  re-anchored to 411-431 and 214-221, the headings kept.
- **q14-pre-dec1069.yaml** (lens B's Q14, 8d09eb40): its gold answer gave nine dependents, while 13 tickets list
  DAEO-ym8a in `depends_on` (DAEO-2bdu, DAEO-arrl, DAEO-n0wb and DAEO-s9qc added). The four had no entry, and "depend
  on" was ambiguous (DAEO-2d6f names W2-03 only in tk's `deps`). It now has 13 entries, and the gold answer states
  `depends_on` and names DAEO-2d6f as outside it. Volatile (DEC-1069 (6)).
- **q17-pre-dec1069.yaml** (lens B's Q17, 8d09eb40): the path map's `namespaces:` span (6-135) covered half the
  block, which runs 6-288. It is re-anchored to 6-288.
- **q23-pre-dec1069.yaml** (W2-61h's q23): its gold answer gave line 26, while `MAP_REL` is at line 27 (its value
  unchanged). The line number is dropped.
