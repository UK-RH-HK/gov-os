# Review: ADR-0002's refresh (DEC-1093 (3), DEC-1097 (8)), the one independent review

- **Reviewed:** `.gov-runtime/scratch/orchestrator/drafts/adr-0002/ADR-0002-architecture-and-stack.md` (422 lines) and
  `CHANGES.md` (72 changes, 13 open points), against the original `docs/adr/ADR-0002-architecture-and-stack.md`.
- **Reviewer:** independent auditor, read-only, 2026-11-08, at `w2/integrate` head `3552f0f59bb7`.
- **Basis checked:** the register to DEC-1097 (v0.481): DEC-1029 to DEC-1097 read in full, plus DEC-261, DEC-397,
  DEC-419, DEC-530, DEC-700, DEC-798, DEC-963, DEC-966, DEC-979, DEC-1015. Live state on window 4's pin: 
  `governance/project/retrieval.yaml`, `rebuild.yaml`, `tool-registry.yaml` (every sha in §2 compared), the pinned code
  read with `git grep bcea09060ebc` (`retrieve.py` role filter and status items, `rerank.py` caps 16 / 24,000,
  `ollama.py` W2-32 S10), `docs/research/W2-88-memory-practice.md` §1, §7, §8, and the LIFT-1 records E0, E2, E4,
  G1-PROFILE, PAT-1, `D9-FATES.md`, plus `packages/DECIDED-NOT-DONE.md`.
- **Sample:** 55 of the 72 changes checked against their sources (all of 3-5, 7-13, 15, 16, 20-34, 36, 37, 39, 41, 42,
  44-52, 54, 56, 57, 59-61, 63, 64, 66-70, 72), including every change to the reranker, embedders, GPU rules, store,
  pool, bundle, search practice and guard.
- **Retrieval:** `gov retrieve` was not used: it calls the shared GPU servers and this brief forbids GPU use. Reads were
  by Read and `grep` on named files. Where a first search did not answer (W2-127's fate; a ticket line for the query
  wrapper's removal), a second search in other words was made (DEC-1092 (1)). Guard refusals: 0.

**What holds.** Most of the draft is accurate and well cited. Every pin and sha in §2 matches the registry. The pool
(60 / 40 / 2 / uncut / drop nested), the routing, `embed_headers`, the integration store and `GOV_STORE`, the 6,000-token
bundle and the 4,000-character cut, the request cap (16 texts, 24,000 characters; 64 at the lift), the role filter
(`role_filter` in the bundle), the status and "changed by" on register items, and "gov starts no embedder"
(`EMBEDDER_UNAVAILABLE`) are all live in `bcea09060ebc`. The K9 bar, the fresh 80's configuration, the release re-measure,
M3 and M1 not adopted, and the glossary marked open (DEC-1097 (6)) are stated as decided. Speed and VRAM figures match
E0, PAT-1 and G1.

## Must-fix findings (in scope; ordinary work yes; fails open)

The refresh exists so that "no stale record is read as current" (DEC-1093 (3), basis question 2). Each finding below
makes the ADR, which carries `state_class: AUTHORITATIVE`, state a protection as stronger or more current than it is.
An agent or an adopting team that relies on that statement lets through what the protection is meant to stop.

### F1: ACT-GUARD-SETS-1 reads as done (overstated). Draft lines 241-243; DEC-1084, DEC-1097 (2)
- The draft says: "ACT-GUARD-SETS-1, decided, rebuilt and applied before the fresh 80's single use". Read plainly, that
  says the ACT has been rebuilt and applied.
- In fact it is decided but not applied. DECIDED-NOT-DONE row 1 says "IN PROGRESS: rebuild started 11-08", and §2
  item 1 says "Not applied; patch stale".
- CHANGES.md #57 says the draft marks it "**not yet applied**", but the draft does not say that.
- The line also narrows the decision. It says "the measured roles", but DEC-1084 (1) decided six refused roles plus
  `transcripts/**`, and DEC-1097 (2) adds the 80's reader-run folder.
- **Fix:** "Decided (DEC-1082 (3), DEC-1084): the guard refuses the hidden sets, wherever they lie, to six measured
  roles and `transcripts/**`. **Not yet applied:** it is being rebuilt with the 80's reader folder, and is applied
  before the fresh 80's single use (DEC-1097 (2))."
- Ordinary work: yes, because any agent asking memory whether the 80 is protected gets this line as the answer.
- Consequence: fails open.

### F2: The sections not re-audited are not marked in the ADR (missing marker). L3 (line 74), §6 (lines 245-331), §7 (lines 333-352); DEC-953, DEC-954, DEC-1061 (3a), DEC-1087 (13)
- CHANGES.md §9 (1) admits that L3, §6 and §7 still describe Wave 1's enforcement. The draft's body never says so.
- Worse, the draft adds Wave 2 lines inside exactly those sections: role separation in L3, `GOV_STORE` and the sandbox
  bullet in §6, DEC-1010 in §7. That makes them read as re-audited and current.
- What they state as current, without qualification:
  - the "PreToolUse default-deny guard". On this repository it is five rules (DEC-953, DEC-954), and the full guard's
    cases are opt-in (DEC-1061 (3a));
  - lefthook G1-G3 and the install rule as gates. Both are lifted here as gates;
  - "Wave 1 has five roles, and a sixth". There are now six roles, the ticket lead, and the three layers back in
    Wave 2 (DEC-1087 (13));
  - the nightly. It is stopped (DEC-1049).
- **Fix:** put a one-line marker at the head of L3, §6 and §7: "Not re-audited in the 2026-11-08 refresh: this states
  the product's enforcement as of Wave 1. On this repository DEC-953 / DEC-954 lifted it as gates; see
  DECISIONS-IN-FORCE." Whether to say more is then CHANGES §9 (1)'s question for the owner. The marker itself is not
  optional.
- Ordinary work: yes, because agents retrieve ADR-0002 when they ask what the guard enforces.
- Consequence: fails open.

### F3: The guard's own-acceptance search gap and W2-141 are missing (missing, overstated). L3, line 74; DEC-1093 (2)
- L3 says flatly that "an engineer is refused its own ticket's acceptance tests wherever they sit".
- DEC-1093 (2) records that this fails open on a wide Grep, Glob or recursive Bash search. W2-141 closes the gap, and is
  applied with the guard's ACT at the lift's re-pin. Until then, every engineer brief carries the exclusion line.
- The CHANGES.md header lists W2-141 among the items the draft marks "at the lift's re-pin", but W2-141 appears nowhere
  in the draft.
- **Fix:** add after the G-14 clause: "A wide search that reaches the ticket's acceptance folder is refused only from
  W2-141, at the lift's re-pin (DEC-1093 (2)). Until then, the engineer's brief carries the exclusion."
- Ordinary work: yes, because a repository-wide grep is the most ordinary search an engineer makes.
- Consequence: fails open.

### F5: "No private reranker beside the service" is stated as the product's behaviour (overstated). Lines 129-131; DEC-1046 (1), DEC-1048 (5), DEC-1097 (8)
- §2 says "while the service runs, no private reranker joins it on the GPU". In the product it does not hold:
  - W2-112's KPI still allows one private reranker beside the service (DEC-1036 (2); DECIDED-NOT-DONE row 49);
  - on this machine, only the CTO's interim `rerank_service_slot_hold.py` enforces it;
  - the product ticket is not filed yet (DECIDED-NOT-DONE item 9).
- The CHANGES.md header says this item is marked "at the lift's re-pin". In §2 it is not marked. The Bad list (lines
  388-390) states the truth, but §2 contradicts it.
- In an adopted repository without the interim tool, the service plus a private reranker can "reach or pass the budget"
  (DEC-1043 (2)): the CUDA-crash path of 2026-11-02.
- **Fix:** "On this machine the interim slot-hold tool keeps any private reranker off the GPU while the service runs
  (DEC-1043 (2), DEC-1048 (5)). In the product, the rule arrives with the new ticket, built before the lift
  (DEC-1046 (1), DEC-1097 (8))."
- Ordinary work: yes, because EXAMIN's copy runs the product without the CTO's tools.
- Consequence: fails open.

## Other findings (rows: fix while editing, none blocks)

### F4: E4 is said to have judged rerankers it never ran end to end (overstated). Lines 57-60, 379-380; DEC-1097 (5), DEC-1077 (b), DEC-1079
- "each measured on the 138 … then end to end (E4)" and "none made agents answer better end to end" are both too broad.
- E4 ran only M3 and M1 end to end. gte and zerank alone appear there for hit@5 only. The 4B, the cascade and mxbai never
  reached a reader (E4-RESULT).
- **Fix:** "M1 and M3 were run end to end (E4) and answered no better. The others were judged on hit@5 and MRR only."
- Ordinary work: yes, because a future reranker decision would read this line.
- Consequence: other (the evidence is overstated; no protection fails).

### F6: Open point 5 is stale. CHANGES §9 (5); DEC-966, DEC-1087 (3)
- DEC-966 now carries "Changed by: DEC-1087 (3)" (`3552f0f59bb7`). Drop the point.
- DEC-963's status still names only DEC-966. That is a `gov links` notice, not an ADR matter.
- Ordinary work: no, because it is a record note.
- Consequence: other.

### F7: Open point 6 is misframed; DEC-261 is contradicted, not ended. Line 135; DEC-261, DEC-1065 (1)
- DEC-261 decided "`gov` starts `ollama serve` on demand and never stops it". The draft cites DEC-261 for a sentence
  whose first half ("only an explicit restart … starts `ollama serve`") reverses that start.
- The pin does start none (W2-32 S10, `ollama.py:48`), and DEC-261 carries no "Changed by" mark (DEC-866).
- The owner's real question is whether to mark DEC-261 changed by DEC-1065 (1) / W2-32 S10. "Never stopped" already
  matches DEC-261.
- Ordinary work: yes, because the register and the ADR disagree.
- Consequence: other.

### F8: The CTO's interim tools are presented as the product (overstated; no open point names it). §3 lines 143, 155-157, 381-382; DEC-1030 (4), DEC-1037 (4), DEC-1057 (4)
- Three statements are about this repository's operation, not the product:
  - "limits are derived from the machine detected";
  - "the dispatcher watches each model's layers";
  - "they restart by class … without an ACT".
- In the product these are KPI lines for W2-20 / W2-121. W2-20 is to be rebuilt before the lift (DEC-1097 (8)), and none
  of it is on the pin.
- **Fix:** mark them "on this repository, by the CTO's tools; in the product through W2-20 / W2-121". Add this to §9 as
  a point.
- Ordinary work: yes, because an adopter reads §3 as what ships.
- Consequence: other.

### F9: "Wrong claims unchanged" is wrong. Line 365; DEC-1092 (1)
- E2-RESULT: wrong claims were 2 at one search and 3 at two searches. Say "wrong claims 2 → 3".
- W2-88 §8 repeats the error.
- Ordinary work: no.
- Consequence: other.

### F10: The reranker's GB figures predate the memory release. Line 148; DEC-1043 (2), DEC-1068
- "about 4.8 GB, up to 6.4 GB" are the readings of 2026-11-02. Since window 4 the service releases its memory after each
  request (E0's total peak was 8,404 MiB).
- Label the figures with their date, or drop them for the window 4 measures.
- Ordinary work: no.
- Consequence: other.

### F11: The G1 burst time is misattributed. Line 383
- "about 14 s for the burst, G1": G1's own bursts took 14.5-17.4 s. The 13.4-13.9 s figure is PAT-1's.
- Ordinary work: no.
- Consequence: other.

### F12: Stale "recorded at …" placeholders in §2. Lines 96-102
- The registry now holds shas for gitleaks, ccusage, superpowers, bubblewrap and socat. §2 still shows "—" or
  "recorded at install / vendoring / when W1-06 creates the registry".
- Ordinary work: no.
- Consequence: other.

### F13: Launch enforcement is missing (missing). L4 line 75, §6 launcher bullet; DEC-1088 (5)
- `gov launch` is to refuse:
  - a lead outside the approved batch, or one whose waits are unmet;
  - any session while the gate is shut or the machine's limits would be passed.
- This lands with W2-136 / W2-20 at the lift. L4 names `plan` but not the refusal. Add it, marked "at the lift".
- Ordinary work: yes.
- Consequence: other (not live yet; nothing relies on it today).

### F14: The status line overclaims. Line 16
- "Every change … cites its decision": changes #19, #38, #55 and others cite none, as CHANGES.md itself says. Say
  "every decided change".
- Ordinary work: no.
- Consequence: other.

### F15: The store's counts are undated. Line 141
- 69,464 / 19,113 / 1,126 are W2-88 §1's D-4b figures, not a count of window 4's store. Date them.
- Ordinary work: no.
- Consequence: other.

### F16: "Every session searches one current store" is too broad. Line 362; DEC-1064 (2)
- Sandboxed sessions run no `gov retrieve` until W2-127. Qualify the line, or point to the Bad bullet.
- Ordinary work: no.
- Consequence: other.

### F17: Open point 12 understates the gap. CHANGES §9 (12); DEC-1037 "recorded with it"
- DEC-1037 says the wrapper's removal "stays tracked (the W2-20 / W2-121 KPI line, then its own small ACT)". No ticket
  carries that line (searched in `.tickets/` twice).
- That makes it a decided-but-not-done item for DECIDED-NOT-DONE, as well as an ADR point.
- Ordinary work: no.
- Consequence: other.

## CHANGES §9: are the 13 open points the right ones?
Mostly yes. Points 2, 3, 4, 7, 8, 9, 10, 11 and 13 are real and well put. Point 11 (accept now and re-read at the lift,
or accept after the lift) is the most important for the owner, because six draft items change at the lift.

- **Drop point 5.** It is already done (F6).
- **Reframe point 6** as "mark DEC-261 changed by DEC-1065 (1) / W2-32 S10" (F7).
- **Point 1 needs a fix in the draft, not only a question.** The inline "not re-audited" marker goes in whatever the
  owner answers (F2). What the owner decides is only whether the ADR also states this repository's lifted regime.
- **Point 12:** add that DEC-1037's tracking line is missing from every ticket (F17).
- **Add:**
  - the product-against-CTO-tools line in §3 and Consequences (F8);
  - W2-141 and the guard's wide-search gap, if the drafter would rather ask than state it (F3).

## Verdict
**NOT READY** to bring to the owner. One editing pass fixes it, with no re-research. The four must-fix changes:
- F1: say ACT-GUARD-SETS-1 is decided and not yet applied (six roles, `transcripts/**`, the reader folder);
- F2: put inline "not re-audited" markers at L3, §6 and §7;
- F3: add W2-141 and the wide-search gap to L3's G-14 clause;
- F5: mark "no private reranker beside the service" as the interim tool now and the product at the new ticket.

F4 and F6 to F17 ride along in the same pass (DEC-802). After the pass, a delta check of these lines alone is enough
(DEC-1010, round 2 at most).

```verdict
{"kpis": [
  {"kpi": "ADR-0002-refresh: statements match the register and window 4's pin", "verdict": "fail", "findings": [
    {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
    {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
    {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F9", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F10", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F11", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F12", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F14", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F15", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F16", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "ADR-0002-refresh: nothing decided is missing", "verdict": "fail", "findings": [
    {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
    {"id": "F13", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "ADR-0002-refresh: no proposal presented as decided (glossary open, ACT-GUARD-SETS-1 not applied, M3 not adopted)", "verdict": "fail", "findings": [
    {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
  {"kpi": "ADR-0002-refresh: sections not re-audited are marked", "verdict": "fail", "findings": [
    {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
  {"kpi": "ADR-0002-refresh: CHANGES §9's open points are the right ones", "verdict": "pass", "findings": [
    {"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F17", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}
]}
```

## Round 2 (the last, DEC-1010): the delta check

- **Checked:** every line that CHANGES.md §8b rows 73-88 name, each read in context in the revised draft (441 lines),
  and the revised §9 (15 points).
- **Sources:** the five new shas compared with `tool-registry.yaml`. W2-145 searched in the register, DECIDED-NOT-DONE,
  `.tickets/` and every branch. Guard refusals: 0. No GPU, no `gov retrieve`.

### Round 1's findings
| Finding | Fixed? | Where, and what it now says |
|---|---|---|
| F1 | yes | Lines 250-253: "Decided (DEC-1082 (3), DEC-1084 (1)) … six measured roles and `transcripts/**`. **Not yet applied:** … being rebuilt … with the fresh 80's reader-run folder … applied before the 80's single use (DEC-1097 (2))". |
| F2 | yes | Italic markers at the head of L3 (line 75), §6 (lines 257-259) and §7 (line 350). Each names the lifts (DEC-953 / DEC-954), the five rules, the stopped nightly, six roles, the ticket lead and the three layers, and points to DECISIONS-IN-FORCE. |
| F3 | yes | Line 75: the wide-search gap is refused only from W2-141 at the lift; until then the exclusion line is in every engineer brief (DEC-1093 (2)). |
| F5 | yes | Lines 131-135: "decided … but is not yet in the product". The interim watcher is the only enforcement; W2-112's KPI still allows one private reranker; W2-145 is not yet built. The Bad list (lines 407-409) agrees. |
| F4 | yes | Lines 60-61 and 396-398: only M1 and M3 ran end to end; the others were judged on hit@5 and MRR. |
| F6 | yes | §9 (5) now says it is done and not an ADR matter. |
| F7 | yes | Lines 136-140: "starts none" cites W2-32 S10 / DEC-1065 (1) and says it changes DEC-261's start, which is not yet marked. "Never stops" stays DEC-261's. §9 (6) is reframed. |
| F8 | yes | Lines 149-150, 163-166 and 399-401 are marked "on this repository, by the CTO's tools; in the product W2-20 / W2-121, not on the pin". DEC-1031 (4) is cited correctly (SMART-WORK-6's W2-20 / W2-121 lines). §9 (14) is added. |
| F9 | yes | Line 382: "wrong claims 2 → 3". §9 (10) names the same error in W2-88 §8. |
| F10 | yes | Line 155: the figures are dated 2026-11-02, before the memory release. |
| F11 | yes | Lines 402-403: G1 14.5-17.4 s; PAT-1 13.4-13.9 s. |
| F12 | yes | Lines 97, 98, 101 and 103: all five shas match the registry (gitleaks `88f91962…`, Superpowers `f2a95244…`, ccusage `b8d59c19…`, bubblewrap `2461f1be…`, socat `46e85428…`). |
| F13 | yes | L4 (line 76) and the launcher bullet (lines 303-304) give the launch refusals at the lift (DEC-1088 (5)). L4 carries the full list; §6 a short form that points the same way. |
| F14 | yes | Lines 16-17: "Every decided change … (descriptive updates cite their source)". |
| F15 | yes | Lines 146-148: the counts are dated to D-4b, "not a count of window 4's store". |
| F16 | yes | Line 379: "Every unsandboxed session". |
| F17 | yes | §9 (12) is widened. Line 410 states the missing ticket line plainly. |

### New in round 2

**R2-1: W2-145 is named as though filed.** Lines 134 and 409; DEC-1097 (8)
- The ticket exists only as a scratch draft (`drafts/w2-145/W2-145.md`, `id: DAEO-xxxx` placeholder) and in
  START-NEXT-SESSION. It is not in `.tickets/`, the register or DECIDED-NOT-DONE (row 9 still says "ticket to file").
- §9 (15) discloses this to the owner, so nothing is hidden.
- **Suggested wording when it is next touched:** "W2-145 (drafted, to be filed)".
- Ordinary work: no, because the line already says "not yet built", and no agent acts on the ticket id alone.
- Consequence: other.

Nothing else new is wrong. The substitutions keep their cited decisions accurate, and §9's 15 points are the right set
for the owner. Point 11 (accept now and re-read at the lift, or accept after the lift) is still the main question.

### Verdict, round 2
**READY** to bring to the owner. No finding is in scope, reachable in ordinary work, and fails open or loses work.
R2-1 is a row: fix it when the draft is next touched, or when W2-145 is filed.

```verdict
{"kpis": [
  {"kpi": "ADR-0002-refresh: statements match the register and window 4's pin", "verdict": "pass", "findings": [
    {"id": "R2-1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "ADR-0002-refresh: nothing decided is missing", "verdict": "pass", "findings": []},
  {"kpi": "ADR-0002-refresh: no proposal presented as decided (glossary open, ACT-GUARD-SETS-1 not applied, M3 not adopted)", "verdict": "pass", "findings": []},
  {"kpi": "ADR-0002-refresh: sections not re-audited are marked", "verdict": "pass", "findings": []},
  {"kpi": "ADR-0002-refresh: CHANGES §9's open points are the right ones", "verdict": "pass", "findings": []}
]}
```
