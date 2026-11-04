# Retired questions of the memory-retrieval set

This folder keeps questions taken out of the set, with their past results. It is not a part of the set: the measure
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

### Q03's past results (every measure record of the visible half found)

The date is the record's own time stamp (UTC). The tree is the measured root and the commit the record names. Each
record had 20 questions and Q03 needed one piece of evidence (`pieces_needed` 1).

| Record | Date (UTC) | Tree (root @ commit) | Retriever | hit@5 | Full evidence | In the bundle | First gold rank |
|---|---|---|---|---|---|---|---|
| `.gov-runtime/scratch/orchestrator/archive/worktree-scratch/W2-61/lead/runs/records/measure-memory-retrieval-visible-20261029T212614400969Z.json` (W2-61 baseline, run 1) | 2026-10-29 21:26 | `~/gov-os-runs/W2-61/repo` @ 23079f92a6fa | pin-5c401220 | yes | yes | yes | 4 |
| `…/W2-61/lead/runs/records/measure-memory-retrieval-visible-20261029T215538826335Z.json` (W2-61 baseline, repeat) | 2026-10-29 21:55 | `~/gov-os-runs/W2-61/repo` @ 23079f92a6fa | pin-5c401220 | yes | yes | yes | 4 |
| `…/W2-61/lead/runs/records/measure-memory-retrieval-visible-20261029T222152985301Z.json` (W2-61 baseline, after the rebuild) | 2026-10-29 22:21 | `~/gov-os-runs/W2-61/repo` @ 23079f92a6fa | pin-5c401220 | yes | yes | yes | 4 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T204744666636Z.json` | 2026-10-30 20:47 | `~/gov-os-runs/W2-87/head` @ 060e03ef57ea | gov-base (df0782fa4c4e) | no | yes | yes | 6 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T210612149889Z.json` | 2026-10-30 21:06 | `~/gov-os-runs/W2-87/head` @ 060e03ef57ea | gov-reg (006ad0bb36ce) | no | yes | yes | 6 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T213841067037Z.json` | 2026-10-30 21:38 | `~/gov-os-runs/W2-87/head` @ cffef92c8534 | gov-base (df0782fa4c4e) | no | yes | yes | 6 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T215256578023Z.json` | 2026-10-30 21:52 | `~/gov-os-runs/W2-87/head` @ cffef92c8534 | gov-reg (006ad0bb36ce) | no | yes | yes | 6 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T221154739899Z.json` | 2026-10-30 22:11 | `~/gov-os-runs/W2-87/head` @ cffef92c8534 | gov-head (cffef92c8534) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-86/records/measure-memory-retrieval-visible-20261101T000130633794Z.json` | 2026-11-01 00:01 | `~/gov-os-runs/W2-86/base` @ 9dc5288161c4 | pin-5c401220 | no | yes | yes | 7 |
| `~/gov-os-runs/W2-86/records/measure-memory-retrieval-visible-20261101T005837664244Z.json` | 2026-11-01 00:58 | `~/gov-os-runs/W2-86/head` @ 338c14fa6475 | pin-5c401220 | no | yes | yes | 7 |
| `~/gov-os-runs/W2-86/records-tree/measure-memory-retrieval-visible-20261101T021603839200Z.json` | 2026-11-01 02:16 | `~/gov-os-worktrees/W2-86` @ 338c14fa6475 | gov-wt (338c14fa6475) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-55/records/measure-memory-retrieval-visible-20261101T042015457494Z.json` | 2026-11-01 04:20 | `~/gov-os-runs/W2-55/head` @ 2281b081cc7d | gov-base (84c1d4277b9c) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-55/records/measure-memory-retrieval-visible-20261101T043140266796Z.json` | 2026-11-01 04:31 | `~/gov-os-runs/W2-55/head` @ 2281b081cc7d | gov-head (2281b081cc7d) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T140024036524Z.json` | 2026-11-01 14:00 | `~/gov-os-runs/W2-92/base` @ 7ca16b19df3f | gov-base (7ca16b19df3f) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-13/records/base/measure-memory-retrieval-visible-20261101T141401010245Z.json` | 2026-11-01 14:14 | `~/gov-os-runs/W2-13/base` @ c38a5b49bc86 | gov-base (c38a5b49bc86) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-13/records/head/measure-memory-retrieval-visible-20261101T151713552810Z.json` | 2026-11-01 15:17 | `~/gov-os-runs/W2-13/head` @ bd329ce3b402 | gov-head (bd329ce3b402) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-13/records/head-a/measure-memory-retrieval-visible-20261101T152010872537Z.json` | 2026-11-01 15:20 | `~/gov-os-runs/W2-13/head` @ bd329ce3b402 | gov-head-a (bd329ce3b402) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T161333491429Z.json` | 2026-11-01 16:13 | `~/gov-os-runs/W2-92/head` @ fb0c8c430171 | gov-head (fb0c8c430171) | yes | yes | yes | 2 |
| `~/gov-os-runs/W2-91/records/measure-memory-retrieval-visible-20261101T173426352951Z.json` | 2026-11-01 17:34 | `~/gov-os-runs/W2-91/base` @ f46b96537d74 | pin-5c401220 | no | yes | yes | 7 |
| `~/gov-os-runs/W2-91/records/measure-memory-retrieval-visible-20261101T193515830840Z.json` | 2026-11-01 19:35 | `~/gov-os-runs/W2-91/head` @ b652fc96d2b5 | pin-5c401220 | no | yes | yes | 6 |
| `~/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T205024907715Z.json` | 2026-11-01 20:50 | `~/gov-os-runs/W2-92/head` @ d72c96fc029c | gov-head (d72c96fc029c) | yes | yes | yes | 2 |

In all 21 records the old Q03 was in the bundle and had its full evidence; hit@5 held in 13 and missed in 8 (its first
gold source at rank 6 or 7: the four runs of the pinned gov by W2-86 and W2-91, and W2-87's four runs other than
its head's). The
retriever column gives the executable the record names (the pinned gov `~/.local/share/gov-os/pin-5c401220`, else a
lead's wrapper with the commit its version line gives).

## q09-lens-b.yaml: lens B's Q09 label, retired 2026-11-03

- **What it was:** lens B's Q09 (Table 2 of `docs/assessment/2026-10/B-memory-retrieval.md`), "How large may the
  context packet be?", written into the visible half by W2-61 at commit 23079f92a6fa (commit 8d09eb40, 2026-10-29).
  Its one source was W2-04's ticket KPI lines (`.tickets/DAEO-u4oz.md`, `kpis:`, lines 24-36). The file here is that
  file, byte for byte.
- **Why its label was retired:** the owner's decision of 2026-11-03, DEC-1066 (4) (in the chat; recorded in the
  register by the orchestrator). The label named only the ticket's KPI lines, while the rule's governing source, the
  Contract's envelope (its token budget: "Context packet ≤ ~6k tokens"), was not a gold source, so a search that
  answered from the Contract was scored as missing. The question and the gold answer were not wrong and are kept; only
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

### Q09's past results (the 21 records of q03's table, and D-4b measure 1's three)

The columns are q03's. Each record named Q09 with one piece of evidence needed (`pieces_needed` 1); the first 21 had
20 questions, measure 1's three had 48 (`--part all`; only Q09's own row was read here).

| Record | Date (UTC) | Tree (root @ commit) | Retriever | hit@5 | Full evidence | In the bundle | First gold rank |
|---|---|---|---|---|---|---|---|
| `.gov-runtime/scratch/orchestrator/archive/worktree-scratch/W2-61/lead/runs/records/measure-memory-retrieval-visible-20261029T212614400969Z.json` (W2-61 baseline, run 1) | 2026-10-29 21:26 | `~/gov-os-runs/W2-61/repo` @ 23079f92a6fa | pin-5c401220 | no | yes | no | 60 |
| `…/W2-61/lead/runs/records/measure-memory-retrieval-visible-20261029T215538826335Z.json` (W2-61 baseline, repeat) | 2026-10-29 21:55 | `~/gov-os-runs/W2-61/repo` @ 23079f92a6fa | pin-5c401220 | no | yes | no | 60 |
| `…/W2-61/lead/runs/records/measure-memory-retrieval-visible-20261029T222152985301Z.json` (W2-61 baseline, after the rebuild) | 2026-10-29 22:21 | `~/gov-os-runs/W2-61/repo` @ 23079f92a6fa | pin-5c401220 | no | yes | no | 60 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T204744666636Z.json` | 2026-10-30 20:47 | `~/gov-os-runs/W2-87/head` @ 060e03ef57ea | gov-base (df0782fa4c4e) | no | yes | no | 60 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T210612149889Z.json` | 2026-10-30 21:06 | `~/gov-os-runs/W2-87/head` @ 060e03ef57ea | gov-reg (006ad0bb36ce) | no | yes | no | 60 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T213841067037Z.json` | 2026-10-30 21:38 | `~/gov-os-runs/W2-87/head` @ cffef92c8534 | gov-base (df0782fa4c4e) | no | yes | no | 60 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T215256578023Z.json` | 2026-10-30 21:52 | `~/gov-os-runs/W2-87/head` @ cffef92c8534 | gov-reg (006ad0bb36ce) | no | yes | no | 60 |
| `~/gov-os-runs/W2-87/records/measure-memory-retrieval-visible-20261030T221154739899Z.json` | 2026-10-30 22:11 | `~/gov-os-runs/W2-87/head` @ cffef92c8534 | gov-head (cffef92c8534) | no | yes | no | 46 |
| `~/gov-os-runs/W2-86/records/measure-memory-retrieval-visible-20261101T000130633794Z.json` | 2026-11-01 00:01 | `~/gov-os-runs/W2-86/base` @ 9dc5288161c4 | pin-5c401220 | no | yes | no | 59 |
| `~/gov-os-runs/W2-86/records/measure-memory-retrieval-visible-20261101T005837664244Z.json` | 2026-11-01 00:58 | `~/gov-os-runs/W2-86/head` @ 338c14fa6475 | pin-5c401220 | no | yes | no | 59 |
| `~/gov-os-runs/W2-86/records-tree/measure-memory-retrieval-visible-20261101T021603839200Z.json` | 2026-11-01 02:16 | `~/gov-os-worktrees/W2-86` @ 338c14fa6475 | gov-wt (338c14fa6475) | no | yes | no | 44 |
| `~/gov-os-runs/W2-55/records/measure-memory-retrieval-visible-20261101T042015457494Z.json` | 2026-11-01 04:20 | `~/gov-os-runs/W2-55/head` @ 2281b081cc7d | gov-base (84c1d4277b9c) | no | yes | no | 44 |
| `~/gov-os-runs/W2-55/records/measure-memory-retrieval-visible-20261101T043140266796Z.json` | 2026-11-01 04:31 | `~/gov-os-runs/W2-55/head` @ 2281b081cc7d | gov-head (2281b081cc7d) | no | yes | no | 44 |
| `~/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T140024036524Z.json` | 2026-11-01 14:00 | `~/gov-os-runs/W2-92/base` @ 7ca16b19df3f | gov-base (7ca16b19df3f) | no | yes | no | 44 |
| `~/gov-os-runs/W2-13/records/base/measure-memory-retrieval-visible-20261101T141401010245Z.json` | 2026-11-01 14:14 | `~/gov-os-runs/W2-13/base` @ c38a5b49bc86 | gov-base (c38a5b49bc86) | no | yes | no | 44 |
| `~/gov-os-runs/W2-13/records/head/measure-memory-retrieval-visible-20261101T151713552810Z.json` | 2026-11-01 15:17 | `~/gov-os-runs/W2-13/head` @ bd329ce3b402 | gov-head (bd329ce3b402) | no | yes | no | 44 |
| `~/gov-os-runs/W2-13/records/head-a/measure-memory-retrieval-visible-20261101T152010872537Z.json` | 2026-11-01 15:20 | `~/gov-os-runs/W2-13/head` @ bd329ce3b402 | gov-head-a (bd329ce3b402) | no | yes | no | 63 |
| `~/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T161333491429Z.json` | 2026-11-01 16:13 | `~/gov-os-runs/W2-92/head` @ fb0c8c430171 | gov-head (fb0c8c430171) | no | no | no | none |
| `~/gov-os-runs/W2-91/records/measure-memory-retrieval-visible-20261101T173426352951Z.json` | 2026-11-01 17:34 | `~/gov-os-runs/W2-91/base` @ f46b96537d74 | pin-5c401220 | no | yes | no | 59 |
| `~/gov-os-runs/W2-91/records/measure-memory-retrieval-visible-20261101T193515830840Z.json` | 2026-11-01 19:35 | `~/gov-os-runs/W2-91/head` @ b652fc96d2b5 | pin-5c401220 | no | yes | no | 59 |
| `~/gov-os-runs/W2-92/records/measure-memory-retrieval-visible-20261101T205024907715Z.json` | 2026-11-01 20:50 | `~/gov-os-runs/W2-92/head` @ d72c96fc029c | gov-head (d72c96fc029c) | no | yes | no | 44 |
| `~/gov-os-runs/D4B/m1/records/measure-memory-retrieval-all-20261103T204508001842Z.json` (D-4b measure 1) | 2026-11-03 20:45 | `~/gov-os-runs/D4B/m1/repo` @ 156a5feb677b | `~/gov-os-runs/D4B/m1/gov` (156a5feb677b) | no | yes | no | 65 |
| `~/gov-os-runs/D4B/m1/records/measure-memory-retrieval-all-20261103T210330372974Z.json` (D-4b measure 1) | 2026-11-03 21:03 | `~/gov-os-runs/D4B/m1/repo` @ 156a5feb677b | `~/gov-os-runs/D4B/m1/gov` (156a5feb677b) | no | yes | no | 65 |
| `~/gov-os-runs/D4B/m1/records/measure-memory-retrieval-all-20261103T212211388209Z.json` (D-4b measure 1) | 2026-11-03 21:22 | `~/gov-os-runs/D4B/m1/repo` @ 156a5feb677b | `~/gov-os-runs/D4B/m1/gov` (156a5feb677b) | no | yes | no | 65 |

In all 24 records the old Q09 missed hit@5 and was never in the bundle; its one source was found in 23, at rank 44 to
65 (full evidence: matched by the stacked context across its batches, at any rank), and in none in W2-92's head run
of 2026-11-01 16:13. The retriever column follows q03's; measure 1's executable is the record's own, with the commit its version line
gives.

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
  state it. A search that answered from the Contract was therefore scored as missing, as Q09's was (DEC-1066 (4)).
  The Charter's span also stopped one line short of the line that puts the acceptance-test paths outside the
  implementer's allowed paths.
- **Its replacement:** `visible/q19.yaml`, still `id: Q19`, with the same question and gold answer, written at commit
  03df21248e36. It has one entry of six alternatives, any one of which counts. Lens B's three are kept, the Charter's
  span now running to line 97. Added: MR-3 in `docs/contract/contract.yaml` (`- id: MR-3`, lines 136-142), in
  `docs/contract/CONTRACT_v4.md` (its table row, line 57) and in `docs/contract/master-rules/MR-3.md`
  (`# MR-3: ...`, lines 11-16). Figures for Q19 before 2026-11-04 are the old label's: the new one counts more
  sources, so they are not comparable.
- **Past results:** not read, as for Q16.
