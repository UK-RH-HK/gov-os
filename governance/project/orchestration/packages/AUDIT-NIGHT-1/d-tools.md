# Anti-drift audit (d): every emergency tool the kernel or an adopted repository needs, mapped to a ticket

Written by the product-spec helper (Sonnet, high, class C2) for the CTO (DAEO-sdxk), 2026-11-11 at about 01:20-02:10 UTC, at
`w2/integrate` `797495bdf`. DEC-1125 (3) (iii) d, on DEC-1119 (5) and DECIDED-NOT-DONE row 107. Source: `packages/EMERGENCY-TOOLS-1.md` (71 rows).
**M** means measured (the file or command named); **E** means my judgement.

## 1. The rule and the counts

A row is **mapped** only when a ticket's `kpis.success` holds a line that says what the tool does, in a way a test can check. A ticket that
only names the tool, or only has a title that fits, is not a mapping.

- **Rows in the inventory:** 71 (A 14, B 3, C 9, D 34, E 11).
- **Rows the kernel or an adopted repository needs:** **40** (the inventory's "yes" or "part" in either column: 29 in A-D, all 11 in E).
  Four more (C4, C7, C8, C9) the inventory leaves as an open question; they are mapped too, so nothing changes if the owner wants them.
  The other 27 rows are not needed (listed in §4).
- **Of the 40:** **26 mapped** with a KPI line; **7 mapped without a KPI line** (a line is proposed, §3); **7 missing**, and I filed 5 tickets for them (§2).

## 2. Tickets filed (W2-156 to W2-160; `tk create`, then the fields of DAEO-ar89 and DAEO-l4gf; none committed)

| DAEO id | W2 id | Title (short) | Rows | Before EXAMIN's copy | Parses, plan places it |
|---|---|---|---|---|---|
| DAEO-ylsh | W2-156 | The runaway brake in the product (a ticket past twice its projection holds its next launch; once to the inbox; record-only) | D2 | **yes** (§2 item 4: "no ticket holds the brake") | yes (M: schema ok, `gov plan --open` batch 19) |
| DAEO-ozyt | W2-157 | The GPU backstop in the product (a named GPU job paused on a memory limit, a spill or a partial offload) | D12 | **yes** (GPU safety) | yes (batch 6) |
| DAEO-8a3f | W2-158 | `gov check --structural`: one cheap, bounded, notice-only pass over the check families and new links | D9 | no | yes (batch 11) |
| DAEO-6lid | W2-159 | The orchestrator's two Stop checks (inbox waiter armed; no idle turn with unblocked work) | A8, A9 | no | yes (batch 20) |
| DAEO-fd0p | W2-160 | `gov wait` (bounded wait on an exit file, by pid) and the helper watch | D3, D17 | no | yes (batch 21) |

Each ticket has class `implementation`, role `engineer`, profile STANDARD, `reads:`, `needs:` and `waits_on:` (a ticket created on or after 2026-11-10
must have them, `facts.yaml` `ready.new_since`), S-lines with a `Verify:` and decision brackets, `after-the-lift` in its tags, and the source decisions
in `sources:`. The links check (`gov links`) found no UNLINKED_ID or UNKNOWN_ID in them. I ran it on a scratch clone with the five committed
(`.gov-runtime/scratch/audit-d/clone`), because `gov links` reads what HEAD holds and the main tree holds them untracked. The structural pass on that clone:
all 9 families ok. On the main tree the pass shows schema and claims notices; every one is another helper's draft ticket (DAEO-61vm and others), none is mine.
A first version of my five failed the schema (an unquoted `: ` in `acceptance_tests.author`); fixed before this report (the tickets audit, `c-tickets.md` §4.1, had seen it).

**Why these five and not others.**
- **W2-156 (D2):** nothing in the product refuses a launch for a runaway. DEC-1091 (2) states the brake for *experiments*; the CTO runs it per ticket. The ticket
  `waits_on` DEC-1091 so the owner confirms the wider scope before it is built (M: the register line 13747-13756). It adds no usage alarm (DEC-1089 (3)).
- **W2-157 (D12):** W2-20 has the GPU admission and a trip-wire on *system* memory; it has no line that pauses a running GPU job on a spill or a partial
  offload (M: grep "spill|backstop|pause" in W2-20, W2-121, W2-145: no hit). W2-137 S5 uses "the GPU backstop armed" as a step, so the product relies on a tool it does not hold.
- **W2-158 (D9):** the tool's docstring says "later replaced by T-2's --families", but W2-45 (T-2's home by INVESTIGATION-1 B1-16) holds no scoped or notice-only run, and `gov check` has only `--list` (M).
- **W2-159, W2-160 (A8, A9, D17, D3):** no ticket names them (M: grep over `.tickets`). The dead-man's switch (C3) is left out on purpose: the owner parked it as W3-P16 (DEC-994 item 3; W2-121's moved line).

## 3. Rows mapped without a KPI line: the lines I propose (no ticket edited; another helper audits the tickets tonight)

**P-1. W2-115 (DAEO-emq1), rows A6 and D6 (the landing selection). Held on purpose.** DEC-1100 (4): the product line goes into W2-115 "only once it has proven itself in use"; DECIDED-NOT-DONE row 40 reads "WAITS: proven in use". So there is nothing to fix tonight. When it is proven:
> After a landing on the integration branch that holds a commit outside any ticket and touching the settings, the tool registry or the test map, a scoped selection of that landing runs in a heavy-job slot and its result is logged; a red becomes one inbox item naming the commit; the selection never refuses or undoes the landing. Verify: a planted history with a ticketless commit on each of the three kinds of file: the selection runs; a planted red gives one inbox item and the branch is unchanged [DEC-1100 (2)-(4)]

**P-2. W2-60a (DAEO-cv58) and W2-33 (DAEO-lrre), row D1 (`launch_worker.sh`'s model and effort by class).** DEC-1120 (5) sends RUBRIC-2 "into the product through W2-33's role defaults and W2-60a's launch, before EXAMIN's copy". Neither ticket cites DEC-1119 or DEC-1120 (M: grep over `.tickets`; the tickets audit's §4.2 found the same). W2-60a S3/S4 follow DEC-839 (the role's own default; a model after `--` that is not the role's is refused), which DEC-1120 changes. That is a contradiction with a closed spec, so DEC-105 applies: apply now (one added line, W2-60a gets one more round), defer (a follow-up ticket after W2-60a merges; launches use the role default until then), or re-baseline. I recommend **apply now**, 70 % confidence, because W2-60a is still in progress. Proposed line for W2-60a:
> The model and effort a launch applies come from one table by the role and the ticket's criticality class (C0-C3), read from one file in the kernel; a model or effort given after `--` that differs from the table is refused unless a promotion with its recorded reason (two failed review rounds, or a fail-open finding) is given; the launch record holds the class, the tier and any promotion reason. Verify: planted tickets of each class for each role: the built command line carries the table's model and effort; a differing `--model` is refused; a promotion with a reason is recorded, one without is refused [DEC-1120 (2)-(3), DEC-1119 (2)]

and for W2-33: the role file's machine-readable defaults carry the class column the table needs [DEC-1120 (2)].

**P-3. W2-60b (DAEO-ecac), rows D1 and D2 (the spend log's RUBRIC-2 keys).**
> The session record carries the tier (opus, sonnet, haiku or other, derived from the model's name), the ticket's criticality class and any promotion reason, each null when it is not given. Verify: a planted launch with a promotion: the record holds all three; one without: three nulls [DEC-1120 (3)]

**P-4. W2-115 (DAEO-emq1), row D4 (`lead_verify.sh`).** W2-115's line 3 prints the scoped set; W2-154 S1-S2 hold the serial phase; no line runs a lead's whole verify. The role templates name this script (W2-128 TPL-3 S5).
> `gov close --verify <ticket>` runs the scoped selection, the parallel phase and then the serial phase, each in a heavy-job slot, writes `select.json`, one JUnit file per phase and one summary line, and writes its exit file last; exit 0 green, 1 a red, 2 the selection refused, 3 a run that did not complete. Verify: a planted tree with one red and one serial entry: exit 1, both JUnit files, the summary line; a refused selection: exit 2; a killed run: exit 3 [DEC-1052, DEC-1079, DEC-1050]

**P-5. W2-20 (DAEO-r30l; its paths hold `src/gov/secrets/__init__.py`), row E1 (the secrets switch).** The switch (`ddcec657c`) was built under DAEO-sdxk's own task id, so no ticket holds a line for it; W2-20 only has the scan's pool size.
> The secrets scan is switched by `governance/project/secrets.yaml` (`scan: on|off`; absent means on); off: no content goes to the scanner, the rebuild's report, `gov doctor` and `gov ci` name it, and the secrets-indexing check reads not applicable (YELLOW). Verify: `tests/unit/secrets_check/test_dec1045_switch.py` [DEC-1045]

**P-6. W2-20 or W2-154, row C5 (`nightly.sh`'s held slots).** The nightly's two phases run through the gate's `--held` form (`b7428f793`); the product's slot command (`gov resources --slot`) has no held form (M: `src/gov/resources/slots.py`, `command.py`). Low priority: the nightly is stopped (DEC-1049) and not before EXAMIN.
> A heavy job that needs several slots at once holds them for its whole run, and each phase is confined to the held slots' CPU sets, worker cap and thread budget. Verify: a planted two-phase job holding 2 of 4 slots: both phases inside the 2 slots' sets, the other 2 slots free [DEC-1033 (d), DEC-1038 (4)]

**P-7. W2-116 (DAEO-f58b), row E8 (the store for every worker).** The body (the CTO's note of 2026-11-06) widens S3 to "every worker session"; the KPI line still says "`gov launch independent-test-designer`".
> `gov launch` points every worker session's retrieval at the integration store (the `GOV_STORE` of a launched session); a designer's retrieval never reads a ticket worktree's store. Verify: a launcher unit test per worker role: the session env names the store; a designer's never names a worktree's [DEC-1087 (3), DEC-963]

**P-8 (a dependency, not a KPI line). Row C3, the dead-man's switch.** Mapped to the Wave 3 row **W3-P16** (`docs/plan/WAVE_3_PARKING.md:22`), by the owner's decision (DEC-994 item 3). It has no Wave 2 line, and EMERGENCY-TOOLS-1 §1 C3 says "after the lift". Nothing to file now; the owner may move it.

## 4. The rows, one by one

Key: **M** mapped (ticket, KPI line); **N** mapped without a KPI line (§3); **F** missing, ticket filed; **BE** needed before EXAMIN's copy (the inventory's mark, §1 column 10, kept unless stated).

| Row | Tool | Home ticket and KPI line | Status | BE |
|---|---|---|---|---|
| A1 | cron dispatcher tick | W2-121 line 1 (`gov dispatch tick`, host runs it every minute, outside any session) | M | yes |
| A4 | hook: store refresh after a landing | W2-116 line 4 ("refreshed after every landing"); the hook itself is the operator's ACT (W2-116 body) | M | yes |
| A6 | hook: landing selection | W2-115, no line; held by DEC-1100 (4) (P-1) | N | yes, with W2-115 |
| A8 | Stop hook: waiter check | **W2-159** (DAEO-6lid) S1, S3, S4 | F | no |
| A9 | Stop hook: idle check | **W2-159** S2-S5 | F | no |
| A10 | query wrapper | W2-20, the line "The query-wrapper removal (DEC-1037)" | M | yes |
| A11 | reranker slot module | W2-145 S3 (the service holds every slot) and S5 (a) (the `.pth` guard stays, not changed there); the installed module lagging integrate is an owner ACT, not a ticket (EMERGENCY-TOOLS-1 §4.2) | M | yes |
| B2 | `bash_writes.py` | W2-42a lines 1-10 | M | yes |
| B3 | `role_reads.py` | W2-13 S5 (search filtered by role); W2-141 S1-S3 (the engineer's own acceptance folder); the counterpart rule is in `gov.guard.decide` | M | no |
| C1 | dispatcher and Load Balancer | W2-121 lines 1, 3 (measured peaks), 4 (slots), 9 (embedder health, holder progress), 13 (GPU and layers); `launch_now.sh`: W2-153 S2 | M | yes |
| C2 | `merge_queue.py` | W2-115 lines 11-14 (`gov queue`, land and close in one step, no project names, the store refresh) | M | no |
| C3 | `deadman.py` | none in Wave 2; the Wave 3 row W3-P16 by decision (P-8) | N | no |
| C5 | `nightly.sh`, `rotate.sh` | W2-154 S3 (serial count), W2-115 line 8 (full secrets scan), W2-116 line 2 (refresh after the nightly); the held-slot form has no line (P-6) | N | no |
| D1 | `launch_worker.sh` | W2-56 (the cleaned launch), W2-60a S3-S4 (role default), W2-153 S1 (template); class tiers: no line (P-2, P-3) | N | **yes** |
| D2 | `spend.py`, the brake | brake: **W2-156** (DAEO-ylsh) S1-S6; the cost record: W2-60b line 1; the RUBRIC-2 keys: P-3 | F | **yes** |
| D3 | `wait_for.sh` | **W2-160** (DAEO-fd0p) S1-S2 (W2-128 TPL-3 S5 only names the script) | F | no |
| D4 | `lead_verify.sh` | W2-115 line 3 (prints the scoped set), W2-154 S1-S2 (serial); the whole verify run: P-4 | N | yes, with W2-115 |
| D5 | `select_tests.py` | W2-115 lines 2-3 | M | yes |
| D6 | `landing_select.sh` | as A6 (P-1) | N | yes, with W2-115 |
| D7 | `close_build.py` | W2-115 lines 4-7 and 9 (same verdict on three recorded batches) | M | yes |
| D8 | `land.py` | W2-115 lines 11-12; its inner structural pass: W2-158 S3 | M | no |
| D9 | `structural_pass.py` | **W2-158** (DAEO-8a3f) S1-S5 | F | no |
| D10 | `verdict.py` | **W2-115 line 10** ("READY is computed, not declared", DEC-1010 item 1); the pinned copy in the operator: W2-148 S4. The inventory said "none found": it is held | M | no |
| D11 | `heavy_slot.sh`, `rebuild_slot.sh` | W2-20: the slot line ("Heavy jobs take a slot"), the thread-budget and CPU-set lines; the product command exists: `gov resources --slot` (M: `command.py:8`) | M | yes |
| D12 | `gpu_backstop.sh` | **W2-157** (DAEO-ozyt) S1-S5 | F | **yes** |
| D13 | `rerank_service_slot_hold.py` | W2-145 S3 and S5 (b) | M | yes, then retire |
| D15 | `new_worktree.sh`, `seed_store.py` | W2-122 lines 1, 2, 4 (`gov rebuild --seed`, refused on another model, a product feature) | M | yes (done) |
| D16 | designers' store refresh | W2-116 lines 1-4 | M | yes |
| D17 | `helper_watch.py` | **W2-160** S3-S4 | F | no |
| E1 | secrets switch; scan pools | W2-20 (pools: "sizes its pools to the CPUs the process may use"); the switch itself: no line (P-5) | N | yes, done |
| E2 | selection's record-only rule | W2-66 (closed) line "A declared record-reading set runs on every head"; W2-115 line 2 | M | yes, done |
| E3 | machine-wide vector cache | W2-126 line "a machine-wide cache keyed by the model, its revision and the sha256 of the text" | M | yes, done |
| E4 | no CPU embedding; reranker cache cap | W2-32 S10; W2-112; W2-137 S1-S4 | M | yes, done |
| E5 | no private reranker | W2-145 S1-S3 | M | yes, at the re-pin |
| E6 | the resource gate | W2-20 (the gate, slots, trip-wire, launch enforcement, re-measure) | M | yes, at the re-pin |
| E7 | `gov launch` for every worker; the template | W2-56 (cleaned environment, process group, temp folders); W2-153 S1 | M | yes, at the re-pin |
| E8 | `gov rebuild --integration`; `GOV_STORE` | W2-116 lines 1 and 3; "every worker" is in the body only (P-7) | M (note) | yes, done |
| E9 | `gov plan` | W2-136 S1-S11; W2-147 S1-S4 | M | yes, at the re-pin |
| E10 | the guard: the engineer's search | W2-141 S1-S3 | M | no |
| E11 | search by role; `gov brief`; `gov links`; closures | W2-13 S5; W2-152 S1-S10; W2-129; W2-150 | M | W2-128 and its halves |
| C4 | `indep_launch.py` (open question) | W2-149 S1-S31 | M | no |
| C7 | operator agent core (open question) | W2-148 S1-S5, S17-S22 | M | no |
| C8 | `act_class.py` (open question) | W2-148 S6-S8 | M | no |
| C9 | landing check, wall, pinned verdict (open question) | W2-148 S4, S16, S18, S19 | M | no |

**Not needed (27 rows, the inventory's "no" in both columns):** A2, A3, A5, A7, A12, A13, A14; B1; C6; D14, D18 to D32 (fifteen rows), D33, D34. D22 (`proc.sh`) is not a ticket, but W2-160 needs its "by pid" liveness check; the engineer builds it with `os.kill(pid, 0)`, not by calling the script.

## 5. Marks: needed before EXAMIN's copy

**The inventory's 7 groups** (EMERGENCY-TOOLS-1 §2) and their home, as they stand tonight:

| Group | Home ticket | Status tonight | In W2-27's closure (M) |
|---|---|---|---|
| 1 dispatcher, Load Balancer (C1, A1) | W2-121 | open, not started; the Balancer **is** in its lines 3, 9 and 13 (the inventory said it carries none) | yes |
| 2 scoped close and selection (D5, D7, D4, D6, A6) | W2-115 | open, not started; D4's run and D6/A6 lack lines (P-4, P-1) | yes |
| 3 resource gate (D11, D12, A10, E6) | W2-20; **D12: W2-157** | in progress; D12 had no ticket | W2-20 yes; **W2-157 not yet** |
| 4 launch tiers, template, brake (D1, D2, E7) | W2-56, W2-153, W2-60a, W2-60b; **D2: W2-156** | RUBRIC-2 lines missing (P-2, P-3); D2 had no ticket | W2-56, W2-60a, W2-60b yes; **W2-153 and W2-156 not** |
| 5 guard reads Bash writes (B2) | W2-42a | in progress | **no** |
| 6 GPU safety for the reranker (A11, D13, E5) | W2-145 | in progress | **no** |
| 7 designers' store (D16, A4, E8) | W2-116 | in progress | **no** |

**P1-PLAN P1-14's closure** (§G: W2-27's re-derived closure, 31 tickets). I recomputed W2-27's closure from `.tickets` (`deps:`, `depends_on:`, `waits_on:`; M, a short script in my scratch): W2-20, W2-56, W2-60a, W2-60b, W2-115, W2-121, W2-122, W2-33 and W2-13 are in it. **W2-42a, W2-116, W2-145 and W2-153 are not**, though a decision or the ticket's own text puts each before EXAMIN's copy (DEC-1028 (4); W2-116 "Order: before EXAMIN's copy (W2-27)"; DEC-1119 (2); the inventory §2.6). W2-156 and W2-157 are not in it because they are new. **Recommendation:** add W2-42a, W2-116, W2-145, W2-153, W2-156 and W2-157 to W2-27's `depends_on:` (the CTO's edit; W2-27 is an orchestrator ticket and not mine), then re-run `closure.py` and update P1-PLAN §G's count and estimate (about 31 tickets and 175-225 lead-hours today; add W2-156 about 6-9 h and W2-157 about 5-8 h, **E**: scaled from W2-137 and W2-60b).

## 6. What the inventory said that I found different (M, with the file)

1. §2 item 1: "W2-121 carries no balancer line." **It does:** lines 3 (measured peaks, the forecast), 9 (server health, holder progress) and 13 (GPU state and layers). What is not started is the code (`src/gov/dispatch` does not exist, M).
2. §1 D10: `verdict.py` "needs a ticket (none found)". **W2-115 line 10** holds it (READY computed from a structured verdict, DEC-1010 item 1; "folds W2-117 S7").
3. §1 A4: "the after-landing trigger is not named." **W2-116 line 4 names it** ("refreshed after every landing"). Only the hook's installation is the operator's ACT.
4. §6 asked whether the GPU spill rule and the helper watch have lines. **No** to both; W2-157 and W2-160 hold them. The after-landing trigger: yes (item 3).
5. §1 E1: the secrets switch is "already in product", but no ticket holds a line for it (P-5); W2-20 holds only the pools.

## 7. Risks and what I did not do

- **Scope of W2-156.** DEC-1091 (2) is "for the experiments". Taking it to every ticket of an adopted product widens an owner decision, so the ticket waits on it (`waits_on: DEC-1091`). It never alarms (DEC-1089 (3)). Owner's call in the digest, or the CTO's under DEC-1112 (3) if it reads it as a P2 inside the standing rules.
- **Interface points left open, simplest reading taken** (named in each ticket's Interface): the brake's marker folder (`.gov-runtime/spend/`) and the projection's source (the launch record's); `gov spend`, `gov session-watch`, `gov wait` as command names (the precedent is W2-20's `gov resources`); the open-items source of W2-159's idle check (the dispatcher's ready list by default).
- **Overlap in the plan.** W2-156, W2-159 and W2-160 each add one line to `src/gov/check/commands.py`, a file five other open tickets already hold (the tickets audit §4.6). `gov plan` serialises them (M: batches 19-21). If that is too slow, a registry that does not need an edit per command is a separate ticket.
- **Not done:** no ticket other than my five touched; no KPI line added to an existing ticket; the structural gap of §4.3 (committed tools calling scratch paths) is covered by W2-20 (the `--slot` command exists) and W2-115 (the selection), not by a ticket of its own; the two installed-state gaps (§4.1 `settings.local.json`, §4.2 the reranker module) are owner ACTs and stay in §4 of the inventory.
- **Scratch:** `.gov-runtime/scratch/audit-d/` holds a shared clone (no objects copied) and one links output; the CTO may remove it.
