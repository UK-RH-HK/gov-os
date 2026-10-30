# P-TOOLS-REVIEW-1 — An independent review of the orchestrator's tools, and acceptance tests for the brief builder and the queue's gates (owner's request, 2026-10-27; DEC-930, DEC-936 item 3.3)

From: the W2 orchestrator, drafted 2026-10-29; delivered with the re-plan package. Six parts (DEC-818).

## 1. Context

- **The owner's request (2026-10-27):** most refused closes this week came from my own tooling (the brief builder, the queue tools, the sync, the ACT scripts), not from the product, and nothing independent reviews that tooling. The owner asked for:
  - a proposal for an independent review of my tools, as a short lens: what each tool does, what it could get wrong, and which of this week's slips it would have caught;
  - acceptance tests for the brief builder and the queue's gates.
- **The measured case** (annexes B and C of STATE-OF-GOV-OS):
  - my tooling or process is present in 14 of the 18 refused closes and is the only cause in 6;
  - I made 42 slips in two weeks, 9 of them tool bugs;
  - 11 slips are not yet prevented;
  - 39 of 80 standing practices live only in my prompt, briefs or tools (annex D).
- **Where the tools are:** almost all are untracked, in `.gov-runtime/scratch/orchestrator/tools/`. Only `sync_context.py` and the nightly folder (`governance/project/orchestration/nightly/`, with `test_nightly.sh`, 36 of 36 passing and 4 mutation checks) are committed and tested.

## 2. What happened: the tools, the lens, and the slips each would have caught

| Tool | What it does | What it could get wrong | Slips it caused or would have caught (annex C) |
|---|---|---|---|
| `build_lead_brief.py` | Fills the common lead brief's slots | A role in IMPL (T7: 39 + 2 commits); a read the guard refuses named in the brief (P2); the command-form rules missing (S10) | Caused T7 (now refuses a non-id IMPL); would catch P2 and S10 with a check against the role's refusals and a required "guard forms" block |
| `close_queue.sh` | Gates (a)–(h), the close, the outputs' commit | Exit 0 after a refusal (T8, fixed); a close started under load (S2); no rebuild first (S1, fixed); collect log too big (T9, fixed) | Refusal path tested (`test_close_queue_refusal.sh`); the rest untested |
| `trailer_gate.py` | Gate (e): trailers present, `Implements:` resolving | A CAP or DEC that does not resolve passed (T7); the store unreadable taken as fine | T7 now caught; untested |
| `unmeasured_gate.py` | Gate (h) with the pinned code | Old pin's code (fixed); a decision-record rule narrower than the judge's | R4 caught; untested |
| `keyword_warn.py` | Row W2-L423's early warning, by path | Read the index stores (T6, fixed); a merged-lines edit (NameError, fixed) | T6; untested |
| `skip_gate.py` | Interim skip guard | Compared dotted and path ids (T5, fixed) | T5; untested |
| `record_checks.sh` | The record checks before a record commit | Ran on untracked files, so it proved nothing about tracked ones (R12) | Would catch R12 if it checked tracked files and staged paths |
| `probe_impact.py` | Names stale probes after a merge | A judged file missed | S-6 caught; untested |
| `act_clone_run.sh` | A full run in the close's form on a clone with a patch | `-E` dropped `PYTHONPATH`, 0 serial entries read (E2, fixed and guarded); the pin hard-coded (fixed, follows `~/.local/bin/gov`) | E2; untested |
| `validate_entry.py` | Validates owner entries with the pinned readers | Scanned removed lines for placeholders (fixed) | R6 caught |
| `sync_context.py` | Policy 1 sync to `record/w2` | Copied ignored stores (T2), and paths in no namespace (T3) | T2 and T3 (fixed); untested |
| `repin_registry.py` and `repin2_registry.py` | The owner's registry edit | A wrong `approved_by` (T4) | T4; the fix in the tool is unconfirmed |
| `disk_gate.sh`, `wake_at.sh`, `launch_when_gate_opens.sh`, `rebuild_diag.sh`, `placeholder_scan.py`, `tree_diff.py`, `net_check.py`, `sweep.py` | Gates, waits, launches, diagnosis, scans | Each untested | — |
| (no tool) run-clone removal | — | The guard refuses my `rm` under `~/gov-os-runs` (E4): about 3 GB of clones and W2-65's stray folder kept | E4 |

## 3. Why it matters

- These tools decide whether a close starts, what a brief tells a lead, and what reaches the owner's commit. A bug there costs a close slot (about 85 minutes) or a night, as this fortnight measured.
- They are untracked and unreviewed. They are also this repository's habits, not part of the Gov OS: an adopted product inherits none of them (annex D).

## 4. Options

**(a) Commit, test and review the tools now** (my recommendation):
1. **Commit them,** as the nightly folder was, under `governance/project/orchestration/tools/`, with a README naming each tool's job. A gate (the queue) refuses to run a tool whose working copy differs from its commit, as `nightly_cron.sh` does.
2. **Acceptance tests from an independent test designer:**
   - **ticket W2-79, `build_lead_brief.py`:** a non-id IMPL refused; a read the role is refused flagged; the guard-forms block required; every slot filled; no placeholder left;
   - **ticket W2-80, the queue's gates (a) to (h) and the refusal path:** a planted fault per gate stops the queue with its reason; a refused close exits 4; outputs are committed only after a clean close and the skip guard; mutation checks on each gate's condition, as for the nightly.
3. **An independent auditor's review of all the tools,** read-only and fresh, with the lens in §2. It checks each tool against the slips it claims to catch, and names what each could still get wrong. Its report goes in a commit of its own (DEC-924 item 2).
4. **Run clones (E4):** a committed `runs_sweep.sh` that removes only the run clones of the nightly and the ACT runs, by their stamp and path, older than 24 hours. Cron runs it as the owner (outside the guard, like the nightly), or the guard's path rules allow the orchestrator that one path. The owner's choice.

Cost: about one day of leads (two LITE test-designer tickets) and one auditor session (about 3 hours, measured cost about 30 USD per lens-sized audit, annex E). No product code.

**(b) Tests only, no review:** half the cost, without the independent look the owner asked for.

**(c) Move the tools straight into the judge,** skipping the interim commit: the right end state (annex D's five priorities), but weeks of tickets, during which the tools stay untracked.

## 5. Recommendation

**(a)** now. Then **(c)** step by step, as annex D's five priorities, one ticket each, in the re-plan's order. Confidence: high that it would have prevented most of the 9 tool bugs and 3 of the 11 unprevented slips (R12, P2, S10).

## 6. What it blocks, and what waiting costs

- **It blocks** nothing.
- **Waiting costs** more refusals from my tooling: 3.1 h of refused test time with my tooling as the only cause, and 10.5 h with it involved, in two weeks (annex C S-1).
- **E4's disk use grows** by about 0.56 GB per ACT clone run and per day run, until the run-clone sweep exists.
