# D. Standing practices: where each lives today, and where it must live for an adopted product to inherit it

Research agent D's findings (read-only, 2026-10-29, `w2/integrate` at `2f2fb03e`), written down by the orchestrator. This is the draft for STATE-OF-GOV-OS part 6 (DEC-936 item 3.3).

**Legend:**
- **Where it lives today:**
  - **P** = the prompt `governance/project/prompts/w2-orchestrator.md` (v3.37, §n);
  - **B** = the project briefs (LB = `LEAD-w2-common.md`, AC = `AUDITOR-common.md`, JG = `JUDGEMENT.md`), which belong to this repository, not the kernel;
  - **T** = the tools in `.gov-runtime/scratch/orchestrator/tools/` (untracked);
  - **O** = the committed scripts in `governance/project/orchestration/` (project files);
  - **K** = the kernel, `template/governance/kernel/`;
  - **J** = the judge, `src/gov/`.
- **Inh.** (inherited by an adopted product): NO = only in P, B, T or O; PART = partly in K or J; YES = in K or J.

DEC-939, rows W2-M408 and W2-L451, and tickets W2-76 and W2-77 are drafts.

**Counts:** 80 practices.
- YES: 17 (C1–C5, C9, C10, C19, C20, D9, E5, F7, G5, G6, G7, H6, H7).
- PART: 24.
- NO: 39, living only in the orchestrator's tooling, the prompt or the briefs.
- About 25 have no ticket that carries them.

**Five practices to move first** (the agent's proposal, confidence medium-high):
1. the nightly into the judge (W2-77, then a ticket for row W2-M407);
2. the scratch budgets, the sweep and the verification lock into `gov launch` and the resource gate (KPIs on W2-20 and W2-21);
3. the stale-probe check at merge time and `Implements:` resolution into judge commands;
4. the judgement rules, DEC-916 and red-first into the kernel through a wider W2-11;
5. the placeholder scan, and commits only after green checks, into a commit-time tier (W2-06, W2-08, W2-12).

**Notable facts the agent verified:**
- W2-07's gates are in pin-5c401220 (`src/gov/close/command.py` lines 192–221).
- `gov close`'s gate (e) checks only that trailers are present; `Implements:` ids resolve only through `gov.close.traceability`.
- The kernel's `test-design/SKILL.md` does not mention red-first.
- `probe.schema.json` has no `ordinary_work` or `consequence` fields.
- The orchestration skill is still at v1.0.0.
- `gov.close.nightly` exists but is not run, and its repo-wide prune is row W2-M406.

## A. The nightly

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| A1 | A full uncached regression every night in the close's form on a fresh clone, JUnit; each red re-run alone (fails alone: bisect, P1; passes alone: flaky candidate) | DEC-852 item 3; DEC-880; DEC-889 items 4, 12; DEC-933 item 2.7 | P §15; O `nightly.sh`, `nightly_alone.py`; J `close/nightly.py` exists, not run (DEC-915 item 4) | J `gov.close.nightly` | W2-77 (draft), then row W2-M407 | PART |
| A2 | Window 02:00 to 05:00, measured length: parallel sum ÷ lowest effective parallelism of the last 3 runs + serial + setup, × 1.10; latest start = 05:00 − estimate; estimate against actual in the digest; lock-wait apart (draft) | DEC-933 items 2.1, 2.2; DEC-934; DEC-939 item 6 (draft) | O `nightly_estimate.py`, `nightly.sh`; T `junit_sums.py`; P §15 | J nightly; K declared schedule | row W2-M407 only; **needs a ticket**: "gov.close.nightly applies DEC-933 item 2" | NO |
| A3 | Clean start (no close, no MERGE_HEAD, clean tree, head stable 5 min); holds the NIGHTLY-RUNNING and verification locks; no heavy work meanwhile; closes resume at its end | DEC-933 items 2.3–2.5 | O `nightly.sh`; LB; P §15 | J machine lock read by close, launch and verify; K brief-lead | W2-M407; **needs a ticket** (or a W2-20 KPI) | NO |
| A4 | An estimate that no longer fits: a package to the owner; never cut | DEC-933 item 2.6 | O `nightly.sh` | J nightly | W2-M407; **needs a ticket** | NO |
| A5 | Cron runs only committed, reviewed code (the entry refuses unless the folder is HEAD; `test_nightly.sh`) | DEC-934 item 1 | O `nightly_cron.sh`, `test_nightly.sh`; P §15 | the pinned judge's nightly; K a scheduler template at adoption | W2-16, W2-18; **the schedule needs a ticket** (adopt skill) | NO |
| A6 | Dated logs rotated under a budget; a green night removes only its own clone by stamp; a red one keeps it | DEC-934 item 2; DEC-939 item 5 (draft) | O `rotate.sh`; J `nightly.py` prunes repo-wide instead (W2-M406) | J | W2-77 (draft); W2-M407 | PART |
| A7 | A missed night is never silent: `status.txt` ran / FAILED / MISSED; FAILED or MISSED is a P1 | DEC-934 item 2; DEC-936 item 1 | O `nightly_check.sh`; P §7, §15 | J `gov status` or `gov doctor` names a missed night; K skill | **needs a ticket** | NO |
| A8 | Night pings held until 07:30 unless the owner is active; an unreadable reading holds, never loses | DEC-936 item 1; DEC-938 item 3 | O `ping_gate.sh` | K skill (generic slots); the notifier stays project config | none (fold into B1) | NO |
| A9 | 01:00 cut-off: no lead full run that cannot finish before 02:00 | DEC-939 item 6 (draft) | nowhere yet | J gate or launch; K brief-lead | **needs a ticket** (W2-20 KPI) | NO |
| A10 | The host's needs at 02:00 (awake, WSL, the wake task) | DEC-934 items 3, 4 | O README; `ACT-NIGHTLY-1.md` | K adopt checklist | none (fold into A5) | NO |

## B. The morning package and notification

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| B1 | Investigate every finding (alone and in the close's form, bisect, flaky vs real, root cause); one six-part `P1-MORNING-<date>.md` with the P2s at its end; one ping and a chat summary at 07:30, even with no items | DEC-938 items 1–3 | P §7; T `wake_at.sh` and schedule; O `packages/` | K skill and morning template; J alone re-run and bisect | **needs a ticket** (widen W2-11) | NO |
| B2 | Hold only what an item blocks (a red nightly holds closes); one answer, then resume | DEC-938 items 4, 5 | P §7 | J close refuses on an open red nightly; K skill | **needs a ticket** | NO |
| B3 | Emergencies stop the affected work at once; Pushover for emergencies (draft) | DEC-938 item 6; DEC-939 item 7 (draft) | P §7; draft `push_emergency.sh` | K skill; the notifier stays project config | none (fold into B1) | NO |
| B4 | Long commands in the background; 07:45 watchdog | DEC-939 item 1 (draft) | P v3.38 pending; T `wake_at.sh` | K skill | none (fold into B1) | NO |
| B5 | The six-part package in the message and `packages/<id>.md`; starts first, `owner-ping` last; only P1s and ACTs ping; no question box, no secrets; leads never ping | DEC-818; DEC-850; DEC-855; DEC-936 item 2.5 | P §7; LB; K `decision-package.md` (older form); K skill (DEC-220 cap) | K template in six parts; K skill | W2-11 (**add a KPI**) | PART |
| B6 | ACT commands in `packages/ACT-<id>.md`; "a plain terminal" only for a gov reinstall; the operator runs a patch commit | DEC-925 item 2; DEC-928 item 3 | P §7 | K `act.md` template and skill | **needs a ticket** (or a W2-11 KPI) | NO |
| B7 | P2s delegated and listed in the digest, with the exceptions | DEC-936 item 2.5; MR-6; DEC-220 | P §7; K skill (older conditions) | K skill | W2-11 (**add a KPI**) | PART |

## C. Closes: the queue, gates (a)–(h), merges

W2-07's gates are pinned in pin-5c401220 (DEC-935; `command.py` lines 192–221); W2-07 is merged, not closed.

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| C1 | (a) collection in one process | DEC-868 item 1(a); DEC-896 item 4 | T `close_queue.sh`; LB; J `gates.check_collection` | J | W2-07 | YES |
| C2 | (b) gov check after the rebuild, no commit between; the close reads its result | DEC-868; DEC-780; DEC-889 item 2 | T; J `_check_governance_blocks`, `--check-result`, STORE_STALE | J | W2-07, W2-66 | YES |
| C3 | (c) a fresh ticket checkpoint | DEC-867 item 4; DEC-868 | T writes and commits it; J `_check_checkpoint` | J; K skill (the write) | W2-07 | YES (refusal) |
| C4 | (d) the tree as the close reads it | DEC-868 | T `tree_diff.py`; J `_check_tree` | J | W2-07 | YES |
| C5 | (e) trailers present | DEC-182; DEC-476; DEC-868 | T `trailer_gate.py`; J `_check_trailers`; K skill | J, K | W2-07 | YES |
| C6 | `Implements:` resolves (a DEC the register holds or a CAP the store holds), caught in the ticket | DEC-927 item 2; DEC-928 item 1 | T `trailer_gate.py`, `build_lead_brief.py`; LB; J only after a close (`gov.close.traceability`; K `product-traceability-trailers.yaml`) | J close commit gate; W2-06 tier | **none names it**: a W2-07 follow-up or a W2-44 KPI | PART |
| C7 | (f) the record-reading suites | DEC-882; DEC-885; DEC-896 item 4 | T `close_queue.sh` | J record-reading set first | P-SCOPE-RECORDS-1 (package only); **needs a ticket** | NO |
| C8 | (g) allowlisted hosts reachable, or hold and retry | DEC-892 | T `net_check.py` | J close reads `research-allowlist.yaml` | **needs a ticket** | NO |
| C9 | (h) work without a task, with the pinned code | DEC-896 item 1; DEC-923 item 2 | T `unmeasured_gate.py`; J `_check_unmeasured`, `decision_records` | J | W2-07 r2 | YES |
| C10 | A stale probe named before the close spends its run (W2-M403) | DEC-896 item 3 | J `_check_probe` first | J | W2-07 | YES |
| C11 | Stale probe at merge time: `probe_impact.py` after each merge, a fresh probe scheduled | DEC-895 item 2 | T `probe_impact.py`; P §3, §15; LB | J post-merge check or status flag; K skill | **needs a ticket** | NO |
| C12 | Disk floor of 100 GiB and 10,000,000 inodes | DEC-898 item 1; DEC-899 item 5 | T and O `disk_gate.sh`; P; LB; J `check_disk` (close only) | J launch and resources too | W2-20 (DAEO-r30l); W2-07 | PART |
| C13 | Resource gate in the launch command (load below 20, MemAvailable ≥ 6,710,886 kB, embedder 2.4 GB, every session counted) | DEC-798 item 4; DEC-847; DEC-898 | P §3, §15; T `lead_usage.py`; LB; K skill (older, by hand) | J launch and resources | W2-20; W2-21; row W2-M374 | PART |
| C14 | Quiet window: CLOSE-RUNNING lock, one close at a time, leads wait | DEC-780; DEC-806; DEC-867 | T `close_queue.sh`; LB; P §15 | J close lock read by launch and verify | W2-68 in part; **needs a KPI** (W2-20 or W2-21) | NO |
| C15 | A refused close exits 4 and stops the queue; a new round, no re-run without a change, never worked round; two refusals to the owner | DEC-929 item 3; DEC-868 | T `close_queue.sh`, `test_close_queue_refusal.sh`; J ratchet, state, repair tickets | J batch exit codes | W2-68; W2-07 | PART |
| C16 | Interim skip guard (an unknown skip, or the rulesync skip) stops before outputs are committed | DEC-899 item 7; DEC-915 items 1, 2 | T `skip_gate.py`, `skip_known.json`; J records skips (`evidence.py`) | J refuses a present-but-skipped tool | W2-57 | PART |
| C17 | Row W2-L423's rule: 12-digit hashes, no keywords, early warning, gate (b) as backstop | DEC-911; DEC-923; DEC-926 | T `keyword_warn.py`, `record_checks.sh`; P §15; LB; AC; J secrets check | J W2-71's exemption | W2-71 | PART |
| C18 | The close's outputs committed, gitleaks over the staged set | DEC-868 (queue); `a1565e56` | T `close_queue.sh` | J close commits its own outputs | **needs a ticket** | NO |
| C19 | Batched closes, reuse, fingerprints, no merges during a batch, a red batch bisected | DEC-883; DEC-889 item 2 | J `batch.py`, `fingerprint.py` (off until W2-77) | J | W2-68; W2-77 | YES (off) |
| C20 | Path-scoped regression; the test map in its own file | DEC-880 item 2; DEC-889; DEC-896 item 2 | J `select.py`; `test-map.yaml` | J | W2-66 (closed) | YES |
| C21 | Non-urgent record commits wait between queues; the lists move to record files | DEC-929 items 1, 2 | P §15 | J record-only list and record files | P-SCOPE-RECORDS-1; **needs a ticket** | NO |

## D. Verification, rebuilds, scratch and disk

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| D1 | One verification run at a time (`flock /tmp/gov-os-verify.lock`) until W2-67 lands | DEC-904 item 3; DEC-905 item 4; DEC-906 item 3 | P §15; LB; O `nightly.sh` | J runner or gate | **needs a KPI** (W2-20); W2-67 ends it | NO |
| D2 | `-o tmp_path_retention_policy=failed` on full runs | DEC-904; DEC-905 | J `select.py`, `nightly.py`; LB; P §15 | J; K brief-lead; W2-19 | W2-19; W2-11 | PART |
| D3 | The lead's verification in the close's form under the lock | DEC-889 items 6, 12; DEC-892; DEC-732 | LB step 4 | J `gov verify`; K template | **needs a ticket** | NO |
| D4 | Rebuild lock and 30-minute watchdog (draft) | DEC-939 item 2 (draft) | T `rebuild_diag.sh` | J `gov rebuild` | W2-76 (draft; rows W2-M408, W2-L451) | NO |
| D5 | Rebuild just before the close; never `--no-embeddings` | DEC-719; DEC-780 | P §5, §15; LB; J STORE_STALE | J; W2-06 | W2-06 | PART |
| D6 | Scratch budgets (30 GB and 2,000,000 per auditor, trial, research or nightly; 20 GB and 1,000,000 per lead with workers); own TMPDIR; no per-run `--basetemp`; clean as you go; du in evidence; over budget, stop and P1 | DEC-898 items 2, 3 | P §3; LB; AC; nothing in K or J | K roles and templates (slot); J launch enforces | **needs a ticket** (W2-21 or W2-20 KPI) | NO |
| D7 | Weekly sweep under its conditions | DEC-902 | T `sweep.py`; P §15 | J `gov sweep`; K skill | **needs a ticket** (W2-21 covers only worker temps) | NO |
| D8 | The orchestrator removes a returned lead's temp folder | DEC-902; DEC-922 | P §15; LB | J launch removes temps | W2-21 (DEC-902 KPI) | NO |
| D9 | No clone under `.gov-runtime`; runs go in `~/gov-os-runs/<id>` | DEC-673; DEC-728 | J guard, launcher; P | J | W2-50 (closed) | YES |

## E. Pins and owner entries

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| E1 | Re-pin cadence: each improvement re-pinned as it lands, never during a queue; ladder (clone run, two identical wheel sha256s, smoke test); old pin kept for rollback | DEC-933 item 1; DEC-935; DEC-922; `P-REPIN-2.md` | P §3, §15; `ACT-REPIN-*.md`; scratch `pin/smoke_repin2.sh` | J release and update; K change skill | W2-16, W2-17, W2-18 (**add KPIs**) | NO |
| E2 | Owner entries validated with the pinned judge's readers before sending | DEC-895 item 1 | T `validate_entry.py`; P §5 | J `gov approve` | W2-12 (DAEO-j8gn) | NO |
| E3 | Settings changes: a full close-form run on a clone plus a sweep of dependent tests before the owner's commit | DEC-925 item 2; DEC-931 item 2 | T `act_clone_run.sh`; P §5 | J update and regeneration; K change skill | W2-17 (**add a KPI**) | NO |
| E4 | Only the test designer commits under `tests/acceptance`; the owner's commits limited to ratchet, history and exemption entries | DEC-906 item 1; DEC-862 (a); DEC-891 | P §5; J guard, `EXEMPTIONS_KEY`; W1-01 test | J W2-44 | W2-44; W2-12 | PART |
| E5 | The ratchet lists only shrink; each entry names its fix | DEC-757; DEC-762; DEC-766 | J `ratchet.py`; P; LB | J | W2-53; W2-19 | YES |

## F. Records and decisions

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| F1 | The rule about rules: each standing rule written into the register, prompt, RESUME HERE, briefs and cards; the report says where | DEC-851 | P §7 | K change and orchestration skills; J a check that each place cites it | W2-55 (card only) in part; **needs a KPI** | NO |
| F2 | Supersession propagates: mark at once, sweep by id and value, update or keep with a reason, a check | DEC-866 | P §7; LB; K retrieval skill (CAP-51); J `gov context` refusal, ACTIVE_SUPERSEDED | J W2-55's check; K change skill | W2-55 | PART |
| F3 | Placeholder scan (unfilled times, TBD, TODO, XXX, xx, ???, angle-bracket slots) before anything reaches the owner or a commit | DEC-893 | T `placeholder_scan.py`, `record_checks.sh`, `validate_entry.py`; P §15 | J declared check or commit tier; `gov approve` | **none names it**: W2-06 and W2-12 KPIs | NO |
| F4 | Record checks before record commits | DEC-868 item 2 | T `record_checks.sh`; K declared checks | J pre-commit tier | W2-06, W2-08 | PART |
| F5 | Commits only after green checks (slip `1916501d`; never after `;`) | DEC-936 status line and item 2 | P §3; habit | J pre-commit hook | W2-08, W2-06 | NO |
| F6 | Decision records by the orchestrator (`decision-record`, `Role: orchestrator`, `Decided-by`); the push is the acceptance; history-entry split | DEC-861; DEC-862; DEC-891 | P §5; LB; J `decision_records`, `history.py`; K skill | J `gov approve`; K skill | W2-12; W2-11 | PART |
| F7 | Ticket-file commits carry that ticket's Task | DEC-896 item 2 | P §7; K skill (DEC-537); J WORK_WITHOUT_TASK | K, J | done | YES |
| F8 | Reports go in commits of their own | DEC-924 item 2 | P §15; LB | K skill | W2-11 (**add a KPI**) | NO |
| F9 | Policy 1: RESUME HERE at every handover; `record/w2` sync with gitleaks; session summaries | DEC-819; DEC-837; DEC-887 | P §15; LB; O `sync_context.py`; J session-start (W2-62); K checkpoint skill | J record-branch sync; K skills | W2-62 (closed); **the record branch needs a ticket** | PART |

## G. Ticket loop, reviews, judgement

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| G1 | Red-first test design: tests before the implementation, red for the README's reason, the lead checks red, nobody edits a test | MR-3; DEC-069; DEC-136; DEC-462 | K role test-designer, `brief-test-designer.md`, `brief-lead.md`, skill; LB; P A1 — **not in K `test-design/SKILL.md`**; J does not check | K test-design skill; J red-first record (DEC-936 item 3.1) | W2-11 (its test-design KPI); mutation testing: row W2-M401 and the re-plan (proposed) | PART |
| G2 | FULL reviews: at most 2 (2 per declared round); a 3rd is the owner's exception; after the last, only fail-open or loss is fixed; nothing after the probed head; only a passing record committed | DEC-413; DEC-916; DEC-498; DEC-733 | K skill and `brief-lead` (DEC-413); J probe gate; DEC-916 only in P §14 and LB | K skill; J counts rounds | W2-11 (**add DEC-916**) | PART |
| G3 | Judgement rules: the two questions, the two finding lines, deliberate construction becomes a Wave 3 row, no extra round, feature-gated entry criteria, classification line | DEC-801–803; DEC-807–809 | P §14; JG; not in K (schemas and `brief-reviewer` lack them) | K `brief-reviewer`, audit skill, probe and audit schemas | W2-11 (DEC-808; row W2-M377) | NO |
| G4 | Twelve return fields first; two-refusal stop | AR-5; AR-6; DEC-793 | P §5; LB; K `subagentstop.py` | K templates and skill; J W2-10 | W2-10, W2-11 | PART |
| G5 | Proportional tests | DEC-221 | K skill and templates; P §9 | K | done | YES |
| G6 | Loop count held; 3 non-converging iterations escalate | DEC-096 | K skill and role | K | done | YES |
| G7 | Learning metrics at close | DEC-106 | K skill; J share | K, J | done | YES |
| G8 | Finish line: classify new work; one more run, then a residual | P §13; DEC-725 | P §13; LB | K skill | none (W2-11 KPI) | NO |

## H. Sessions, launch, memory

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| H1 | Model and effort per role; full window; no compaction threshold | DEC-838; DEC-839 | P §4, §12; LB | K role defaults; J launch | W2-60 (revised plan §4; no tk) | NO |
| H2 | Workers through `gov launch`, sandboxed; step-0 check; tripwire | DEC-789; DEC-799 | LB; T `tripwire.py`; J `launch/` | J | W2-56 (card), W2-21 | PART |
| H3 | Leads in one exact background form with the identity in settings | DEC-715; DEC-731 | P §4; T `build_lead_brief.py` | J `gov launch lead` | W2-21 | NO |
| H4 | Memory used: `gov retrieve` in briefs, `gov context` briefs, targeted code graph, batches | DEC-836; DEC-859; DEC-860 | P §5; LB; K retrieval skill | K templates; J `gov context` | W2-04, W2-11, W2-37 | PART |
| H5 | Policy 2: reads open, writes closed, four refusals | DEC-820 | J guard (W2-58 merged); P §2; LB | J | W2-58 | PART |
| H6 | One writing worker per tree; no commit during a worker's run | DEC-254 | K skill; P | K | done | YES |
| H7 | History never rewritten; `--no-ff`; merge tree equals `merge-tree`; never `-s ours` | DEC-412; DEC-718; DEC-750; DEC-754 | K skill; J probe gate, `containment_merge.py`; P; LB | K, J | W2-53, W2-72 | YES |
| H8 | No fixed parallelism; carry on without waiting; ceiling 10 | DEC-847; DEC-936 item 2 | P §3; K skill (stale fixed ceiling) | K skill; J planner (DEC-936 item 3.4) | W2-11; the planner has no ticket | PART |

## I. Reporting

| # | Practice | Source | Lives today | Must live | Carrier | Inh. |
|---|---|---|---|---|---|---|
| I1 | Countdown and progress line; success rate; leads in flight and why; OWNER_ACTION line | DEC-787; DEC-788; DEC-878; DEC-823; DEC-847 | P §8, §15; K skill (`gov status`, CAP-28) | J `gov status` progress line | **needs a ticket** | NO |
| I2 | Four weekly numbers | DEC-930 item 2 | P §15 | J telemetry (CAP-36.a) and status | W2-60 (cost) in part; **the rest needs a ticket** | NO |
| I3 | Daily digest contents | DEC-861; DEC-838; DEC-849; DEC-836; DEC-898; DEC-902; DEC-852 | P §15 | K skill and template | none (fold into B1) | NO |

**Project-only by design:**
- the workbench (DEC-723);
- EXAMIN (DEC-723, DEC-727, DEC-728);
- the Node PATH;
- the owner's push of both branches (DEC-848, DEC-887);
- `w1/W1-42` (DEC-711);
- CAP-10's figures (DEC-833);
- the recalibration (DEC-834);
- W2-00;
- the host parts of A8, A10 and B3.

**Retired:**
- DEC-897's re-run (W2-69 is pinned, DEC-922);
- the bridge cap (DEC-905);
- hooks off (until W2-08);
- read-refusal counting (until W2-58).

**The 39 that live only in this repository's tooling, prompt or briefs:**
- A2–A5, A7–A10
- B1–B4, B6
- C7, C8, C11, C14, C18, C21
- D1, D3, D4, D6, D7, D8
- E1–E3
- F1, F3, F5, F8
- G3, G8
- H1, H3
- I1–I3
