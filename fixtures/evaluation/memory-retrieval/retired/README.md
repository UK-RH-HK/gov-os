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
