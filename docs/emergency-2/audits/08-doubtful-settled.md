# Audit 8: the 48 doubtful rows, settled (G4, DEC-1214)

Date: 2026-11-18 · Role: product-spec lead (the CTO's brief for G4/G5) · Basis: each entry read from `docs/DECISION_REGISTER.md` (status line and decision items; the long entries to the end of their first items, with the audit's reason beside them); the classes of `08-register.csv` where the entry is not here.

The owner approved G4 (a) in DEC-1214: all 33 groups as listed, the CTO settles the doubtful rows. This page is the settlement: **48 rows read, 44 confirmed as audit 8 classed them, 4 changed class** (DEC-109 to history, DEC-409 to kept, DEC-1149 to kept, DEC-089 to kept). DEC-027 and DEC-974 are not among the 48; they are listed at the end because the owner's answers (DEC-1214 L3 (a), K2 (c)) set their class.

`08-apply.py` reads the "Final" column of every row marked changed, so this page is the one source for them. The class of every other row is the CSV's. **Cannot settle: none.** No row needed the CTO.

| Id | Title | Audit 8 | Final | By / items | Changed | Reason |
|---|---|---|---|---|---|---|
| DEC-109 | W1-02 KD-3: the freeze flag until `gov pause` exists | superseded | **history** | §2.2 | yes | Interim until `gov pause` existed; `gov pause` now exists and writes the same flag (CAP-05, Contract v5 gives it new readers). The interim rule is spent, not contradicted. |
| DEC-409 | Lifting a freeze requires the owner in person: no Claude Code ancestor | superseded | **kept** | items: (3) the guard rule on the lift form superseded §2.2 | yes | Owner-in-person lift (no Claude Code ancestor, TTY, typed code) is what `gov pause --off` does today (`src/gov/pause/command.py:14`) and CAP-05.d (owner-gated) is kept in Contract v5. Only the guard clause goes. |
| DEC-429 | W1-50: the freeze is also written to a mirror outside the repository ( | superseded | **superseded** | §2.2 | no | The mirror existed so sandboxed workers could not erase the flag and the guard could read either copy; guard and sandbox are gone. Code still writes the mirror, but Contract v5 CAP-05 no longer rests on it. |
| DEC-365 | W1-28 DP-2 and DP-3: the orchestrator may set the freeze, only the own | history | **history** | - | no | Who may set and lift the freeze: changed by DEC-402/407/409; the live rule is DEC-409. |
| DEC-378 | W1-28 DP-10: a rollback sets the freeze flag first, and it stays | history | **history** | - | no | Ticket-level rollback behaviour of W1-28, built and tested; CAP-05.c carries it. |
| DEC-404 | W1-50 freeze branch: the marker line's layout; an unmarked file at lau | history | **history** | - | no | W1-50 marker layout and launch denial: built; its guard-reading items are spent with the guard. |
| DEC-075 | ADR-0001's hard boundary without branch protection | history | **history** | DEC-1204 | no | Interim boundary without branch protection; the boundary is restated by DEC-007 (kept) and Contract v5 §2 Boundary. |
| DEC-494 | The CI workflow installs gitleaks and the `gov` package only, each ver | superseded | **superseded** | §2.11 | no | CI gitleaks install step: no gitleaks on private repositories. The checksum-pinned install idea lives on in L3 (hash-checked releases). |
| DEC-999 | Speed: W2-90b split from W2-105 and ACT 2; ten leads; batched landings | history | **history** | - | no | One-off speed measures (W2-90b split, ten leads); the batching and capacity ideas are RT-1/RT-3 and DEC-1157. |
| DEC-1135 | A process-name match used only to detect, which can only refuse and ne | history | **history** | - | no | Clarifies DEC-1073 (4), which is itself history; the detect-only name match belongs to the nightly, off by NIGHT (c). |
| DEC-947 | The memory gate: one verification run's peak reserved once, a working  | history | **history** | DEC-961 | no | RAM-gate reserve numbers: changed by DEC-960/961/1149, lifted for this repository by DEC-953; `mem_guard` is kept through DEC-961 and DEC-1157. |
| DEC-086 | Governance share: definition and Wave 1 measurement | kept | **kept** | - | no | Governance-token definition: the counter CAP-04.b names and A-7 keeps until it exists. |
| DEC-225 | W1-08 DP-2: namespace paths and memory class | kept | **kept** | - | no | `paths`, one namespace per path, `memory_class`: the path map schema as built (CAP-06). |
| DEC-1096 | A repository glossary as part of memory (Wave 2): generated and kept c | history | **history** | DEC-1097 (6) | no | Glossary "only if its retest helped"; DEC-1097 (6) closed it, nothing built, no `gov glossary`. |
| DEC-1179 | MEMORY-AUDIT-P1: each repository keeps a standing hidden set judged en | history | **history** | DEC-1210 | no | The standing hidden set is replaced by the fresh 80 (DEC-1207 (3), DEC-1210). |
| DEC-497 | W1-40: a step whose tool is not on the runner says "unmeasured" and fa | history | **history** | Installs (gitleaks step) superseded §2.11 | no | W1-40 CI choices for one ticket, built; its gitleaks step goes with §2.11. |
| DEC-906 | Only an independent test designer commits under tests/acceptance/ (sta | kept | **kept** | items: (2),(3) history | no | Item 1 is the landing check of who wrote acceptance tests (MR-3, kept). The ratchet entries staying the owner's own commit remain true while `accepted_reds` exists. |
| DEC-938 | The morning package: investigate after the nightly, one P1-MORNING fil | superseded | **superseded** | §6.2 A-2 | no | Morning package and 07:30 ping: one daily digest line replaces them. |
| DEC-948 | Every report to the owner ends with the same five-line block (standing | retired | **retired** | - | no | Five-line owner block tied to the close queue and the 18 November copy; subjects gone. |
| DEC-972 | P-PING-1 (a) plus (d): a ping that does not stop the CTO; none at nigh | kept | **kept** | items: (2) quiet hours changed by DEC-973 and DEC-1021; (3) superseded §2.3; (4) history | no | Non-blocking owner ping through `ping_log` and PushNotification: owner T2 (DEC-1214) confirms phone pushes. |
| DEC-973 | The quiet hours 02:00 to 07:30; the nightly at 04:00; its check at 08: | kept | **kept** | items: (1) quiet hours kept, not for lead-stopping decisions (DEC-1157); (3),(4) history; 09:00 package folds into the daily digest (A-2) | no | Nightly at 04:00 and its 08:00 check are kept by A-1; DEC-1214 NIGHT (c) switches them off for now, not retired. |
| DEC-372 | A latency case that fails under parallel load is re-run alone | history | **history** | - | no | Latency cases re-run alone: the load-sensitive era of Wave 1; the landing records known reds. |
| DEC-527 | Package P-18: `gov close`'s regression step and the regression script  | history | **history** | - | no | Package answer on parallel regression in `gov close`; acted on, and `gov close` is being folded into the landing (L2). |
| DEC-760 | The load-sensitive list's first entries; W2-50's last round runs besid | history | **history** | - | no | The first `load_sensitive` entries, mostly W1-46 sandbox cases: a one-off list. |
| DEC-905 | The retention trial held: `-o tmp_path_retention_policy=failed` is the | history | **history** | DEC-962 | no | Retention trial result; changed by DEC-962; a one-off trial. |
| DEC-1117 | The dead-man's night limit kept at 2 hours; the owner checks the phone | history | **history** | - | no | Dead-man night limit kept at two hours, a one-night answer. |
| DEC-1149 | The working size 0.75 GiB per session (ACT-P95-1), the new figure ever | history | **kept** | items: (1),(2) history (the 0.75 GiB figure; RT-3 removes constants); (3) kept: usage never stops a lead or a worker, the runaway brake stays | yes | Item (3) is a standing owner rule, the same as kept DEC-1157; marking the whole entry history would lose it. |
| DEC-089 | MR-2 holds from Wave 1: every required open readiness cell has a linke | superseded | **kept** | items: Wave 2 `readiness --generate` folds into `gov discover` (W2-36) | yes | A linked gap ticket per required open cell is MR-2 and CAP-30.e in Contract v5 (audit 7 keeps both); a discovery ticket is not a second kind of feature. |
| DEC-093 | Decision packages: at most five at a time; P1 may bypass the cap | kept | **kept** | - | no | Decision packages ranked and capped: MR-6 and CAP-34 kept in Contract v5. |
| DEC-104 | UX before build, with visual testing | superseded | **superseded** | §6.2 A-4 | no | UX-before-build and the UX readiness row go to Wave 3, driven by friction (W2-35); nothing binds until friction asks for it. |
| DEC-236 | Two-level orchestration: the main orchestrator and a ticket lead per t | kept | **kept** | - | no | Orchestrator plus a ticket lead per ticket: the layering EMERGENCY-2 §4.3 still uses. |
| DEC-454 | What `gov close` measures where its KPI lines left the mechanism open | kept | **kept** | items: repair ticket and disposition arguments superseded §4.2 | no | `gov close` measures regression tests on the tree; only the repair-ticket path goes. |
| DEC-878 | Every countdown starts with one progress line: the tickets by state ou | retired | **retired** | - | no | The countdown progress line counted Wave 2 tickets and keystones; the model changed (§6). |
| DEC-944 | The Gov OS as a software company: the mapping; a Definition of Ready c | superseded | **superseded** | §6.2 A-4 | no | The mapping is done; the Definition of Ready folds into the templates, READY by code (W2-82). |
| DEC-949 | The morning package carries only the night; daytime decisions reach th | superseded | **superseded** | §6.2 A-2 | no | Morning package and daytime pings: one daily digest line and RT-6. |
| DEC-963 | P-PARALLEL-1 (b), amended: the test designer in its own worktree, retr | kept | **kept** | - | no | Test designer in its own worktree retrieving from the integration store: separation by construction (§1.2). |
| DEC-995 | A role is what it may read and write; a skill never widens it; mixed t | superseded | **superseded** | §1.2 | no | A role defined by read and write rights is permission thinking; roles are apart by templates, briefs, landing, path map. The surviving fragment (a skill never widens a role) is CAP-24.b. |
| DEC-1003 | Every practice the CTO adopts in its own tools is mapped into the prod | retired | **retired** | - | no | Same-day mapping of CTO practices into tickets: ceremony, scoped by DEC-1052/1057. |
| DEC-031 | Two separate budgets | superseded | **superseded** | §5.5 | no | Its second budget is the `gov context` packet ceiling; the first (retrieval spend by radius) lives in kept DEC-035. |
| DEC-826 | P-S5: what each role loads, reads and writes | kept | **kept** | items: (1),(2),(3) kept; (4),(5) superseded §2.2; (6),(7) history | no | Role loaded at launch, test designer reads the spec not the implementation, reviewers commit nothing. |
| DEC-1199 | EXAMIN's CTO leads EXAMIN's Wave 0 (the Gov OS CTO on Gov OS only); F- | kept | **kept** | items: (1) roles kept, refactor tickets read as direct work §7.2; (3),(4),(5) superseded §2.6/§2.2; (2) history | no | EXAMIN CTO leads Wave 0, Gov OS CTO Gov OS only: matches §7.2 and §7.3. |
| DEC-328 | W1-34 DP-1: a gate record holds its state in `status` alone | kept | **kept** | - | no | A decision package holds its state in `status` alone: the template and the checker still read it. |
| DEC-463 | Decisions recorded late are accepted; from now on the record comes fir | kept | **kept** | items: (1) history | no | Record the decision before the change; `gov check` flags a commit citing an unrecorded decision (CAP-51; allied to §10.1). |
| DEC-473 | The decision-citations check knows both register forms (W1-26, package | kept | **kept** | - | no | The citations check reads a register file named in configuration with the `### DEC-<digits>` grammar; still wired. |
| DEC-479 | The register file and the base commit of the decision-citations check  | kept | **kept** | - | no | `decision_register` and `decision_citations_base` keys of the path map; `gov close` still resolves accepted_reds through them. Repointed when the register is archived. |
| DEC-818 | The P1 decision package format, and the daily P2 digest (standing) | kept | **kept** | items: (1) retired as ceremony; (3) history | no | P2 items in one daily digest (item 2) matches §4.6; the six-part package format is dropped. |
| DEC-837 | Resume in full, pulled forward into keystone 3: ticket W2-62 (item 1f) | kept | **kept** | items: (4) history | no | The audit guessed superseded by §11.1; but §11.1 archives the old CHECKPOINT file, not the hook. CAP-37.g in Contract v5 keeps SessionStart injecting the checkpoint's RESUME HERE, and §6.1 keeps the hooks. |
| DEC-861 | The orchestrator commits the records of the owner's decisions; the own | kept | **kept** | items: (1),(2) amended by DEC-1057; (5) history | no | The CTO records owner decisions, never pushes: the A-11 approval record (§11.5) rests on it. |
| DEC-027 | Root of trust (solo scope) | kept | **superseded** | DEC-1214 (L3 (a): pinned and hash-checked releases, no signing) | yes | Not one of the 48: moved by the owner's answer L3 (a) (DEC-1214); the register already carries the "Superseded by DEC-1214" line. |
| DEC-974 | The memory-chain line back in every status block; a new ticket in the  | superseded | **superseded** | DEC-1214 (K2 (c): planning first) | yes | Not one of the 48: audit 8 had it superseded by §4.6; the owner's K2 (c) (DEC-1214) names the carrier. The register already carries the line. |

## What moves between groups

| Row | From | To |
|---|---|---|
| DEC-109 | guard × superseded | guard × history |
| DEC-409 | guard × superseded | guard × kept |
| DEC-1149 | runtime × history | runtime × kept |
| DEC-089 | tickets × superseded | tickets × kept |
| DEC-027 | releases × kept | releases × superseded |
