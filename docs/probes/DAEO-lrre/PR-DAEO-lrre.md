---
type: probe
task: DAEO-lrre
reviewer_session: bf9dae7f-1b6d-4e7e-80bf-517a182f778a
narrow_check_session: df3266a7-78dc-4a12-a435-1990cc97d20c
implementer_sessions: [3ab69be5-e7a0-44ac-a4be-2f8f6b384243, 1ddf88ff-eaff-47e5-8712-3e229e6e9d82]
fix_session: ps-4 (product-spec, commit c4b977161)
test_designer_sessions: [89acd12a (td-1), cb31b557 (td-2), 47dc5eaf-eca2-4a04-8ddc-43beab668764 (td-3, W1-35 revision)]
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 3b3a90d74c3e0c5478f366453b07cb921c0c6f88
narrow_check_commit: 1221ee0e4feb0585bc452fca2bab2ae00a9bc087
narrow_check_2_session: rv-3 (independent-auditor, Opus 5.5 high, read-only)
narrow_check_2_commit: 9ace61e8ce72e7371b88be5c6a65abfd9baaa1fd
test_designer_session_td4: td-4 (W1-33 revision, commit 4452d6b8c)
decisions_applied: [DEC-1052, DEC-1010, DEC-801, DEC-808, DEC-1156, DEC-957, DEC-1154, DEC-1160]
---

# Probe record: W2-33 (DAEO-lrre), STANDARD review round 1 and the narrow check after it

## Summary

- **What was probed.** Head `3b3a90d74c3e` of `w2/W2-33`, base `3df1ac2deb1b` (the acceptance tests merged, red).
  The change gives the kernel roles folder nine role files: the six existing ones plus `ticket-lead.md`,
  `qa-engineer.md` and `senior-engineer.md`. Each carries the Interface's defaults lines, RUBRIC-2's model and
  effort, the work-order sentence and the one-writer sentence. `orchestrator.md` loses the ticket-lead section and
  becomes the CTO's file. Both orchestrator copies get the CTO-only install rule.
  Commits:
  - `aa8b0fc0f`, `4c6a47d8c`: product-spec;
  - `e7d1c833f`: the W1-35 revision, by the independent test designer, merged in `27ffbe201`;
  - `3b3a90d74`: the lead's CIT-P.
- **Who probed.**
  - Round 1: a fresh read-only reviewer, role `independent-auditor`, session `bf9dae7f-…`, Opus 5.5, effort high
    (class C2), under its OS sandbox (trial write refused, as it should be). It wrote nothing; `git status` was
    empty at its end.
  - The narrow check: a second fresh read-only session, `df3266a7-…`, after a post-review fix (`c4b977161`) and the
    CIT-P update (`1221ee0e4`). It checked only `git diff 3b3a90d74c3e 1221ee0e4`.
- **Threat model (DEC-801, DEC-808).** Honest mistakes in ordinary work. Only a finding that is in scope, reachable in
  ordinary work and fails open or loses work fails the review.
- **Verdict: PASS**, 7 findings in round 1 and 3 in the narrow check. None blocks, none fails open or loses work, and
  no new round starts.

## The reviewer's verdict block (round 1)

```verdict
verdict: PASS
probed_commit: 3b3a90d74c3e0c5478f366453b07cb921c0c6f88
findings: 7
```

Per KPI:
- S1, S2, S3, S5, S6, S7, F1: pass.
- S3 pass (R3); S4 pass (R5).
- S8 pass (R2); S9 pass (R6).
- F2 pass (R1, R4, R7).

The clauses the Interface routes elsewhere are judged there:
- S2's launcher plan: W2-60a;
- S3's guard refusal and S5's launcher refusal: W2-60b;
- S7's generated agents and F2's generation drift: W2-153.

## The narrow check's verdict block

```verdict
verdict: PASS
probed_commit: 1221ee0e4feb0585bc452fca2bab2ae00a9bc087
findings: 3
```

## S6: the planted review brief, run as a probe (the Interface)

The reviewer took `qa-engineer.md` as its role and triaged a planted brief. The brief: ticket X, STANDARD, KPI S1
"the CLI prints the version", round 2 just ended. Finding F-a is in scope: the version misses its patch number.
Finding F-b is out of scope: the help-text colours on one terminal.

How `qa-engineer.md` decided each step:
- `qa-engineer.md:14` (Moderator) put each finding against the ticket's scope.
- `:15` (Wave 3 row) listed F-b as a Wave 3 row.
- `:16` (Verdict) gave the structured verdict per KPI.
- `:17` (Rounds) started no third round.

The verdict it returned:

```
{"kpis": [{"kpi": "S1", "verdict": "fail", "findings": [{"id": "F-a", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-b", "scope": "out", "ordinary_work": "yes", "consequence": "other", "disposition": "Wave 3 row"}]}], "next_round": "none (two-round limit reached); F-a escalated to the Senior Engineer"}
```

F-b is listed as a Wave 3 row and no third round starts, so S6's probe passes.

## W1-35's three revised cases, case by case (the CTO's request)

The test designer revised three cases. Each carries a `Rewrite-Reason:` citing DEC-1156 (3) and DEC-957 Q2, and
nothing else in the file changed (the reviewer compared `3df1ac2de` with HEAD).

1. **`TestTicketLeadSection` → `TestTicketLeadRoleFile`.** It reads `ticket-lead.md`. The five intent cases (what a
   lead is, does, never does, returns, cites) are unchanged and pass. Point kept.
2. **`test_the_section_adds_no_labelled_field_to_the_role` → `test_the_orchestrator_role_holds_no_ticket_lead_section`.**
   The old point (the lead stayed prose inside the orchestrator's file) is moot once the lead has its own file. The
   case now asserts the decision's other half: `orchestrator.md` holds no lead section and names `ticket-lead.md`.
3. **`test_the_roster_stays_at_the_same_roles` → `test_the_roles_folder_holds_the_nine_role_files`.** Exactly the nine
   files, and no `independent-reviewer.md`.
   - The dropped half pinned `template/.rulesync/subagents/` to the kernel roster: no source for a role the kernel
     lacks, and none missing.
   - That guard now lives with W2-153's generation check. `portability._kernel_findings` (`src/gov/adapters/portability.py:253-292`)
     flags a kernel role with no source and a source with no kernel role. It runs on the real tree in
     `test_w2_153_sources.py`'s drift guard and the unit composition case, and is live: both are red on this branch
     until the copies ACT.
   - The generated side is covered by W1-33's `.claude/agents` roster case and W1-38's field agreement.
   - One gap remains, recorded as row R7: a missing or extra `template/.rulesync` source for the three new roles is
     flagged by nothing in this repository until the copies ACT's own check covers `template/.rulesync`.

`TestWording._texts` reads `ticket-lead.md` minus the Interface's defaults lines. All W1-35 cases pass on HEAD.

## Findings and their triage (the lead)

| id | finding (as described behaviour) | where | triage |
|---|---|---|---|
| R1 | CIT-P §4 named only W1-33's and W1-38's reds; 23 W2-153 cases and 2 unit cases also go red until the copies ACT | `docs/changes/W2-33-CIT-P.md` §4 | in scope, not blocking: fixed in `1221ee0e4` (records) |
| R2 | the CTO's file states no brief contents (ROLES-SPEC-1 §3.1:244-254); S8's Verify asks it only of `senior-engineer.md` | `roles/orchestrator.md` | row (Wave 3 / the next roles change) |
| R3 | the ticket lead's file says a fresh QA probes "for a FULL ticket"; DEC-959 checks core tickets one by one whatever their profile | `roles/ticket-lead.md:12` | Wave 3 row |
| R4 | the orchestrator's generated source opens with the ticket-lead template (`ROLE_TEMPLATES` maps orchestrator to role-lead) and preloads only `orchestration`, not the five skills in the file | `template/.rulesync/subagents/orchestrator.md:7,10`; `src/gov/launch/launcher.py:78`; `portability.py:61-68` | Wave 3 row, routed to W2-153 / W2-60b (the source is exactly `compose()`) |
| R5 | the engineer's reads sentence ("before they are merged and ready, and then only runs them") can be read as allowing reads after the merge; the guard refuses them anyway (fails closed) | `roles/engineer.md` (Allowed paths) | Wave 3 row |
| R6 | the file says the missing-key refusal names `GOV_TICKET`; the guard's text names the key and roster, not `GOV_TICKET` | `roles/orchestrator.md:22`; `src/gov/guard/install.py:335-340` | Wave 3 row (W2-113's refusal text) |
| R7 | a missing or extra `template/.rulesync` source for the three new roles is flagged by nothing in this repository | `portability.py:253-292` | Wave 3 row (the copies ACT's check) |
| N1 | the CTO's new sentence says it "starts each ticket lead"; `ticket-lead.md` and `senior-engineer.md` say the Senior Engineer starts leads once Senior Engineers run | `roles/orchestrator.md:11` | row |
| N2 | CIT-P §4's count sat in the copies bullet, which lists 46 of the 50 | CIT-P §4 | cosmetic: reworded with this record |
| N3 | the CIT-P's `review:` header cited the narrow check before it ran | CIT-P:12 | row; true with this PASS |

## Verification

- `gov accept W2-33` on the final head: outcome pass, 96 passed, 0 failed, 11 lines mapped, 0 unmapped.
- The lead's full-suite run (`lead_verify`) on `1221ee0e4feb`: 5590 tests, 47 failed, 7 skipped. Every red is named:
  - 46 wait on the copies ACT: W2-153 sources (23), W1-38 held-out step (10), W1-38 rulesync (6), W1-33 agent
    definitions (5), and the unit adapters (2);
  - 1 is an older case the CTO revises under DEC-1156 (7): `tests/acceptance/W1-33/test_w1_33_kernel_role_files.py:149-155`.
- On `3b3a90d74c3e` the run had 50 reds; the three W2-128 reds turned green with the fix `c4b977161`.

## Run 4: W1-33's two revised cases and the second narrow check (DEC-1156 (3), (7); DEC-1154)

- **What changed.** The CTO put two older W1-33 cases in the ticket's paths (DEC-1156 (7), `aa3bfdc19`, merged from
  `w2/integrate` in `707d23b82`). An independent test designer (td-4, Sonnet 5.5 high, class C2, its own tests
  worktree) revised exactly those two in `4452d6b8c`, merged in `54ba5bcd2`, each with a `Rewrite-Reason:`:
  - `test_w1_33_kernel_role_files.py`: `test_the_research_role_file_is_unchanged` becomes
    `test_the_research_role_file_body_is_unchanged` (DEC-163). It keeps the one-file glob; research.md's lines less
    the seven Interface line heads hash to a pin computed from W1-46's file (`c70bbb69d`); and four Interface lines
    (Launch default Sonnet high, Model tier, Work order, One writer) are asserted once and whole. Green on this head.
  - `test_w1_33_agent_definitions.py`: the agents roster wants nine definitions (the six plus `ticket-lead`,
    `qa-engineer`, `senior-engineer`), no `independent-reviewer`, each once. **Red until the copies ACT** generates the
    three agents (DEC-315); the CTO pairs that ACT with the land.
- `9ace61e8c` writes the owner's approval line into CIT-P §6 (DEC-1160); records only; the role files are byte for
  byte those at `c4b97716164e` (`git diff --stat c4b97716164e HEAD -- template/governance/kernel/roles
  template/.rulesync/subagents/orchestrator.md` is empty).
- **Who checked.** rv-3, a fresh read-only session (independent-auditor, Opus 5.5 high), checked only
  `git diff 707d23b82 4452d6b8c`. It wrote nothing (`git status --porcelain` empty at its end). It recomputed the pin
  (`4793c8eb…3596`) from `c70bbb69d` and found it equal; it confirmed `c70bbb69d`'s whole file hashes to the old
  `60f9092f…`; 19 mutations of a copy of research.md in its TMPDIR (body lines added, removed, changed; the asserted
  lines dropped, changed, duplicated) each turned case 1 red as they should; it compared the asserted strings with the
  ticket's Interface programmatically and found none fitted to HEAD's file (`Version` and `Skills` values not asserted).
  The designer's own note, that it printed HEAD's Interface-head lines by an oversight while computing the pin, was
  checked under this question.

```verdict
verdict: PASS
probed_commit: 9ace61e8ce72e7371b88be5c6a65abfd9baaa1fd
findings: 2
```

| id | finding (as described behaviour) | where | triage |
|---|---|---|---|
| N1 (rv-3) | lines starting with one of the seven heads are invisible to case 1's body hash, and case 1 asserts only four of them: a duplicate or extra head line, or a dropped `Version`/`Skills` line, leaves it green | `tests/acceptance/W1-33/test_w1_33_kernel_role_files.py:182-187` | row, not blocking: W2-33's `test_w2_33_lines` turns red on each (each head once, whole, at column 0; `Launch by criticality` absent where RUBRIC-2 does not vary) |
| N2 (rv-3) | `splitlines` and `"\n".join(...) + "\n"` normalise line endings and the final newline | same, `:182-184` | row, negligible: DEC-163 pins the body's text |

W1-33 on `9ace61e8c` (rv-3, through the heavy slot, twice): 6 failed, 105 passed, 1 skipped, 2 deselected. Case 1
passes; the six reds are case 2 and the five `test_the_definition_agrees_with_its_kernel_role_file[*]`, all the
copies ACT's. The run-3 red at `test_w1_33_kernel_role_files.py:149-155` is gone.

The lead's run on `9ace61e8c` (W1-33, W2-33 and W1-35 together, through the heavy slot):
`6 failed, 325 passed, 1 skipped, 44 deselected in 312.72s`; the six reds are the same six W1-33 cases above
(the copies ACT's); every W2-33 and W1-35 case passes.
