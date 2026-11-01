# W2-55 packages (draft for the return)

## P-W2-55-HOOK (P1, the owner's CIT-P question, DEC-952 item 5): the session-start hook loads the digest
1. Context: KPI 7's second half: "the kernel's session-start hook loads it with RESUME HERE where the project turns
   that on". The hook (`template/governance/kernel/hooks/sessionstart.py`) is not in W2-55's paths, and DEC-952
   item 5 makes its injection a CIT-P question for the owner.
2. What happened: `gov context --in-force --json` is built and tested (S5). On this register it gives 971 lines
   (8 superseded left out, 0 done), far over the hook's 10,000-character cap (CAP_CHARS, W2-62) until the
   backfill marks the done entries.
3. Why it matters: practice 15 (SMART-WORK-1): a fresh session should start with the decisions in force.
4. Options:
   (a) CIT-P now: the hook, where the project's configuration turns it on, runs `gov context --in-force` after
       RESUME HERE and injects the digest whole when it fits the cap, else a pointer line ("N decisions in force;
       run `gov context --in-force`") plus as many lines as fit; a failure is a line saying so, never silence.
       Cost: about 30 lines + tests, one ticket's lead (W2-10 or W2-11 own the hook's file). Risk: start-up time
       (the command reads HEAD; measured here at a few seconds).
   (b) Defer until the backfill is applied, so the digest is short enough to load whole.
   (c) Keep the hand-made DECISIONS-IN-FORCE.md loaded by RESUME HERE (no product change).
5. Recommendation: (b) then (a): apply the accepted backfill first (the digest shrinks once done entries are
   marked), then the CIT-P. Confidence: medium.
6. Blocks: nothing of W2-55; KPI 7's hook half only.
CIT-P line: "CIT-P W2-55-HOOK: sessionstart.py loads `gov context --in-force` with RESUME HERE where the project
turns it on; whole within CAP_CHARS, else a pointer and the first lines; a failure is said, never silent
(DEC-952 item 5, DEC-953 item 7, DEC-983)."

## P-W2-55-WIRE (P2): the register checks' place
- Built as `gov.decisions.check_tags` / `check_propagation` and `python3 -m gov.decisions.tags|propagation`, not in
  W2-03's `gov.decisions.check()`: that list is read by `gov.check.authority` (core-authority, hard-block), the
  strict close's context (`_REGISTER_HAZARDS`) and the escalation lift (`state.py`: "no finding about it"), and by
  W1-11, W1-26, W1-30, W2-03 and W2-72's suites. With 979 untagged entries, folding them in would turn
  core-authority red here and stop every register entry from lifting an escalation until the backfill lands.
- Options: (a) as built; after the backfill is applied, add two kernel check families
  (`template/governance/kernel/checks/decision-tags.yaml`, `decision-propagation.yaml`, severity warning, then
  hard-block) and record the module commands (`RECORDED_MODULE_COMMANDS`, `src/gov/check/commands.py`); a small
  ticket or W2-11's paths. (b) fold into `check()` now (reds above).
- Recommendation: (a), high confidence.

## P-W2-55-BACKFILL (P1 owner review, DEC-791 item 1, DEC-825 item 4)
- `docs/research/W2-55-backfill.md`: 979 rows, 121 amends/refines, 40-entry sample (seed 55). Heuristic
  (keywords and citations); 828 of 979 proposed `repository`; lands-in for uncited in-force entries is "its
  domain's home", a place to write the rule, not one that states it; only 5 proposed `done` (status word DONE).
- The register also needs, with it: the 17 STATUS_RELATION_UNMARKED marks; `Kept:` lines for W2-07's four
  DEC-876 citations; `Values:` lines on the old entries of the sweep (DEC-636, DEC-665, DEC-605, and DEC-953 /
  DEC-961 / DEC-968 / DEC-979's replaced rules) so that propagation searches by value.
- Recommendation: the owner reviews the sample; low confidence in the heuristic domain/scope; a product-spec pass
  on the in-force entries (domain, scope, done) before application would raise it. The orchestrator applies.

## P-W2-55-SMART4 (finding, report only)
- KPI 5's check does not find SMART-WORK-1's four (W2-20, W2-97, W2-38, W2-12): they are value contradictions
  (a reserved peak, the full suite, accepted_reds), the register records no `Values:` lines, and DEC-983 fixed
  their KPIs. It finds them only once the replaced rules' values are recorded.
- By hand (the same search by value): the KPI lines of all four are fixed, but two ticket bodies still state the
  replaced rule: `.tickets/DAEO-r30l.md:74` (W2-20: "one verification peak reserved once", against DEC-961 and
  DEC-983's KPI change) and `.tickets/DAEO-g23i.md:60` (W2-38: "The full suite runs at milestones and in CI",
  against DEC-968). W2-97 and W2-12: none found. To update through their tickets (orchestrator; ticket files).
