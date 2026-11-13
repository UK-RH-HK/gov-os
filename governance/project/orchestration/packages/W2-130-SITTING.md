# W2-130: the owner's one sitting — decision statuses to rule on

**For:** the owner, one sitting (DEC-1074 (7) O2 (A); DEC-1097 (9)). **By:** the CTO's helper, 2026-11-08, a draft.
Nothing here is applied. The register, the two hand lists and the tickets stay as they are until you rule.
**Read at:** `w2/integrate` `3552f0f59`.

## How to read this

- **Your job:** say "accept group X" for each group you agree with, and name any row you want changed.
- **About 30 minutes** if you accept by group; the rows are there to spot one you disagree with.
- **The list:** the 110 decisions the archive calls *spent* while the register still lists them as current
  (DEC-1073 (2)), plus the 40 entries still marked PROPOSED. DEC-1074 (7)'s "150 ids" are these same two lists
  (110 + 40). The "about 110" of DEC-1073 (5)(a) is the first part of it. Then a few rows the readiness review added.
- **"Spent" today:** 109 ids come from the archive's §B; one more, DEC-063, from §C's range line "DEC-038 to
  DEC-063 … Spent". `gov links` counts 110 findings because DEC-937 sits on two §B lines.
- **What each answer does, once you rule** (the CTO applies it in one commit, then `gov links` checks):
  - **DONE:** the entry's status word ACCEPTED becomes DONE; nothing else in the entry changes. A DONE decision is a
    finished one-off, not a working rule.
  - **In force:** the register stays as it is; the archive drops the word "spent" for it.
  - **ACCEPTED / SUPERSEDED / WITHDRAWN / DEFERRED:** the PROPOSED status word is replaced by that word, naming the
    decision that settled it.
  - **Marks:** "Changed by" notes are added to the status line, in the same commit series as W2-130's marks.
- **Confidence:** high = an entry says it in words; medium = the CTO's reading of several entries.

## Summary

| Group | What | Ids | Proposal |
|---|---|---|---|
| A | PROPOSED entries DEC-083 ratified as written | 19 | ACCEPTED |
| B | PROPOSED entries DEC-083 accepted as later decisions realised them | 13 | ACCEPTED, with a Changed-by mark |
| C | PROPOSED entries superseded, withdrawn or deferred | 8 | SUPERSEDED 5, WITHDRAWN 1, DEFERRED 2 |
| D | Spent one-offs nothing still rests on | 90 | DONE |
| E | Spent one-offs an open ticket names as its origin | 13 | DONE |
| F | "Spent" but still carrying a standing rule, or product record | 7 | stay in force; the archive line changes |
| G | Rows the readiness review added (no status word changes) | 4 | see each |
| H | Two choices only you can make | 2 | see each |

**Totals:** 150 decision ids: DONE 103, stay in force
7, ACCEPTED 32, SUPERSEDED 5, WITHDRAWN 1, DEFERRED 2.

## A. PROPOSED, ratified as written by DEC-083 — accept as a group?

DEC-083 (owner, 30 Sep) ratified these by name; their own status lines were never updated.

| Id | Title | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|---|
| DEC-001 | Assemble first | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): DEC-083: 'assemble first stands'; DEC-064 turned its revisit trigger into a per-wave review |
| DEC-003 | Governance is code, not prose | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-004 | Governance overhead budget (hard SLO) | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): as settled by DEC-086 |
| DEC-005 | Proportionality profiles keyed to impact radius | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): its readiness part as settled by DEC-085 |
| DEC-006 | Progressive adoption | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-010 | Agent harness | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-011 | Specification & change control | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-012 | Decisions | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-014 | Code-structural memory | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-015 | Symbol navigation & refactoring | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): native LSP; Serena not adopted |
| DEC-022 | Provider adapters | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-023 | Distribution | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-025 | Enforcement stack | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-026 | Telemetry | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): as settled by DEC-086 |
| DEC-027 | Root of trust (solo scope) | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-041 | Path guards are default-deny allow-lists | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-044 | Hard loop budget per surface | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-046 | Assets carried from the Rust repository | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |
| DEC-050 | Workstation hygiene | register still PROPOSED | **ACCEPTED (by DEC-083)** | high | DEC-083 (`f88aac89`, register line 744): accepted as written |

## B. PROPOSED, accepted as realised by later decisions — accept as a group?

| Id | Title | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|---|
| DEC-007 | Native harness features first | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-075** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-016 | Lexical + semantic index | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-074 (R1)** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-017 | Embedding & reranking models | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-074 (R1)** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-024 | Method skills | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-074 (Q5)** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-031 | Two separate budgets | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-080** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-032 | Retrieval loop runs in a disposable context | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-080** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-033 | Deterministic worklist for closure facets | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-080** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-034 | Stopping reasons (enumerated) | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-080** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-035 | Radius-scaled budgets and task-class facets | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-080 (numbers stay placeholders)** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-036 | Synthesis notes | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-080** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-037 | Zero-result canaries on every index | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-080** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-040 | The Gov OS never executes install commands | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-083 (installs: owner approval per tool); DEC-095 states it** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |
| DEC-042 | Evidence classes and verifier context | register still PROPOSED | **ACCEPTED as realised; mark Changed by DEC-083 (MR-3 for every task)** | high | DEC-083 (`f88aac89`, register line 744): 'accepted as realised by later decisions' |

## C. PROPOSED, superseded, withdrawn or deferred — accept as a group?

DEC-013 is the one DEC-083 does not name: DEC-074's tool bake-off chose `tk` (wedow/ticket) and says it supersedes
DEC-013. DEC-019 is the one guess in this group (medium).

| Id | Title | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|---|
| DEC-002 | Contract v3 retained as normative property spec | register still PROPOSED | **SUPERSEDED by DEC-058, DEC-064** | high | DEC-083 (`f88aac89`, register line 744) |
| DEC-043 | Products resume immediately | register still PROPOSED | **SUPERSEDED by DEC-064** | high | DEC-083 (`f88aac89`, register line 744) |
| DEC-045 | Original governance documents preserved unchanged | register still PROPOSED | **SUPERSEDED by DEC-058** | high | DEC-083 (`f88aac89`, register line 744) |
| DEC-047 | New control panel | register still PROPOSED | **SUPERSEDED by DEC-058** | high | DEC-083 (`f88aac89`, register line 744) |
| DEC-013 | Task DAG & claims | register still PROPOSED | **SUPERSEDED by DEC-074** | high | DEC-074 (`8e5bbe14`, line 490): 'tasks T3 wedow/ticket … Supersedes DEC-013 (`br`)' |
| DEC-062 | GitHub access through `gh` with a read-only fine-grained token | register still PROPOSED | **WITHDRAWN by DEC-842** | high | DEC-842 (`a5789de1`): withdrawn, it landed nowhere |
| DEC-018 | Local T1 model | register still PROPOSED | **DEFERRED to Wave 3 (model routing)** | high | DEC-083 (`f88aac89`, register line 744): 'Deferred: DEC-018' |
| DEC-019 | Research corpus ingestion | register still PROPOSED | **DEFERRED to Wave 3 (research corpus)** | medium | not in DEC-083; contract.yaml names 'Docling (pinned)' as a provider of a W3 capability |

## D. Spent one-offs: rounds, packages, closes, re-pins — accept as a group?

Each was a single act (a round, a merge order, a refused close and its repair, a re-pin) that is finished. Where
later decisions changed them, those "Changed by" marks are added after the sitting (W2-130's last tranche).

| Id | Title | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|---|
| DEC-063 | Repository settings files | ACCEPTED; archive: 'the Rust archive, the restructure and repository set-up. Spent; part A has the …' | **DONE** | medium | ARCHIVE §C (`2e5c9cd9`); its range line 'DEC-038 to DEC-063 … Spent'; its settings clean-up is done |
| DEC-739 | W2-01 gets one third round, beyond DEC-413 | ACCEPTED; archive: 'W2-01's rounds and split. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-743 | W2-50's CIT-P approved | ACCEPTED; archive: 'W2-50's CIT-P (the scratch root). Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-746 | W2-02's packages of run 1, decided by the orchestrator (delegated) | ACCEPTED; archive: 'delegated run packages. Spent; containment's feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-748 | W2-49's apply round | ACCEPTED; archive: 'delegated run packages. Spent; containment's feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-749 | W2-02's shape check measures the verdict's list of conditions (delegated) | ACCEPTED; archive: 'delegated run packages. Spent; containment's feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-750 | W2-01 gets a fourth and last round, then closes or splits | ACCEPTED; archive: 'W2-01's rounds and split. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-751 | W2-50's last review | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-752 | Stacked early starts for W2-03 and W2-16 | ACCEPTED; archive: 'stacked early starts for W2-03 and W2-16. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-753 | W2-16's new `gov release` command is recorded after W2-20 closes (delegated) | ACCEPTED; archive: 'delegated run packages. Spent; containment's feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-754 | W2-01 is split as DEC-750 item 2 orders | ACCEPTED; archive: 'W2-01's rounds and split. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-755 | W2-03's packages of run 1, decided by the orchestrator (delegated) | ACCEPTED; archive: 'delegated run packages. Spent; containment's feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-756 | W2-50's repair | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-758 | W2-50's last round | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-761 | W2-16's last round, tests first | ACCEPTED; archive: 'W2-16's rounds and sources. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-772 (marks after the sitting) |
| DEC-763 | W2-53's lesser packages become list rows (delegated) | ACCEPTED; archive: 'W2-53's lesser packages become rows. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-764 | W2-50 one more short round | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-765 | The guard reads option values as values and honours `--`, in the… | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-767 | W2-16's case defect P-R3-2 | ACCEPTED; archive: 'W2-16's rounds and sources. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-768 | The three pre-existing reds are cleared, never weakened | ACCEPTED; archive: 'reds cleared before W2-53's close. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-771 | W2-16's never-recorded sources go to W2-17 and W2-18 | ACCEPTED; archive: 'W2-16's rounds and sources. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-773 | The same text always gets the same query vector | ACCEPTED; archive: 'reds cleared before W2-53's close. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-774 | W2-50's finding D is fixed in W2-50's round | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-775 | One blocker sweep before W2-54's round | ACCEPTED; archive: 'reds cleared before W2-53's close. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-776 | The machine is kept busy | ACCEPTED; archive: 'the machine kept busy; W2-05's early start. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-847 (marks after the sitting) |
| DEC-777 | W2-05's early start leaves every unmerged ticket's files alone (delegated, stricter-only) | ACCEPTED; archive: 'the machine kept busy; W2-05's early start. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-779 | W2-50's run 7 is its last | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-781 | openspec-validate never stays silently yellow | ACCEPTED; archive: '`gov check` rows (openspec-validate, drift). Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-783 | W2-05's settings re-sort is re-baselined | ACCEPTED; archive: 'W2-05's settings re-sort; the W1-46 fixture. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-785 | W2-50's last review | ACCEPTED; archive: 'W2-50's rounds. Spent. The guard product stays; its gate is lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-790 | W2-50's close goes through the resume probe (P-W2-35 (a)) | ACCEPTED; archive: 'W2-50's close through the resume probe. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-794 | The quality-control check again at the Track A gate | ACCEPTED; archive: 'quality control at the Track A gate. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-800 | W2-52 widened by the entry point's stages and the skill's two synced… | ACCEPTED; archive: 'W2-52 widened; the adopt skill regenerated. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-804 | W2-05 | ACCEPTED; archive: 'W2-05, W2-54 and W2-37 rides-along. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-807 (marks after the sitting) |
| DEC-805 | W2-M281 | ACCEPTED; archive: '`gov check` rows (openspec-validate, drift). Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-971 (marks after the sitting) |
| DEC-807 | F-B and D-1 are Wave 3 rows | ACCEPTED; archive: 'W2-05, W2-54 and W2-37 rides-along. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-811 | W2-54's three test corrections and its query-embedder interface (PKG-W2-54-4-1, -4-2, -4-3 (a) | ACCEPTED; archive: 'W2-05, W2-54 and W2-37 rides-along. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-812 | W2-37 | ACCEPTED; archive: 'W2-05, W2-54 and W2-37 rides-along. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-813 | W1-46's 23 load_sensitive entries stay until W2-M364 | ACCEPTED; archive: 'W1-46's `load_sensitive` entries. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-889, DEC-899 (marks after the sitting) |
| DEC-814 | W2-52 regenerates the Claude adopt skill in its resume (P-W2-43 (b)) | ACCEPTED; archive: 'W2-52 widened; the adopt skill regenerated. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-817 | The owner's exception to accepted recommendations (standing for DEC-814 to DEC-816) | ACCEPTED; archive: 'the owner's exception for DEC-814 to DEC-816. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-821 | W2-58 | ACCEPTED; archive: 'W2-58's guard changes approved and brought forward. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-873 (marks after the sitting) |
| DEC-823 | P-S2 (a) and (b) | ACCEPTED; archive: 'batch, re-plan and set-up acts of 2026-10-19. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-869 (marks after the sitting) |
| DEC-824 | P-S3 (a) | ACCEPTED; archive: 'batch, re-plan and set-up acts of 2026-10-19. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-834 | Every estimate is recalibrated after keystone 2 (item 1c) | ACCEPTED; archive: 'batch, re-plan and set-up acts of 2026-10-19. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-835 | W2-59's scope is approved, with the two packaging gaps | ACCEPTED; archive: 'batch, re-plan and set-up acts of 2026-10-19. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-840 | DEC-460's stated cause is corrected (lens F R8, F9) | ACCEPTED; archive: 'batch, re-plan and set-up acts of 2026-10-19. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-842 | DEC-062 and DEC-140 are withdrawn (plan §11 item 4 | ACCEPTED; archive: 'batch, re-plan and set-up acts of 2026-10-19. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); both withdrawals made; DEC-062 and DEC-140 carry their marks |
| DEC-853 | P-W2-49 (a) | ACCEPTED; archive: 'the secrets scan's time limit (W2-50). Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-884 (marks after the sitting) |
| DEC-854 | P-W2-48 (a) | ACCEPTED; archive: 'batch, re-plan and set-up acts of 2026-10-19. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-857 | The read restrictions come off as fast as possible | ACCEPTED; archive: 'W2-58's guard changes approved and brought forward. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-858 | The pings reach the owner | ACCEPTED; archive: 'the raw record leaves memory; pings confirmed. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-863 | W2-62's two integration packages, both (a) | ACCEPTED; archive: 'W2-62, W2-59 and W2-63 packages. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-864 | W2-59's packages | ACCEPTED; archive: 'W2-62, W2-59 and W2-63 packages. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-865 | P-W2-52 (a) | ACCEPTED; archive: 'W2-62, W2-59 and W2-63 packages. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-867 | W2-53's fourth close refused for four causes, three of them the orchestrator's… | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-870 | W2-53's escalation is lifted | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-871 | P-W2-55 (a) | ACCEPTED; archive: 'accepted history, merge rules, containment. Spent; feature lifted. DEC-912 and DEC-918 …' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-872 | W2-02 resumes now with its original scope, since every close needs its… | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-874 | P-W2-02-R4 (b) | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-879 | W2-59 merges after the queued closes, so one re-pin holds every check… | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-883, DEC-884 (marks after the sitting) |
| DEC-882 | DEC-843's install approval stands | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-884 | W2-66 takes the first slot | ACCEPTED; archive: 're-pins and their ACTs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-889, DEC-896, DEC-899, DEC-918, DEC-921, DEC-953 (marks after the sitting) |
| DEC-885 | W2-02's close refused on two reds | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-886 | If W1-07's `doctor` envelope case fails again in a close's regression and… | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-888 | While the owner is away | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-894 | DEC-892's entry names its test in full | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-895 | Owner entries validated with the pinned judge's own readers before they are… | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **DONE** | medium | ARCHIVE §B (`2e5c9cd9`); its rules (owner entries, probe staleness) are in DEC-953's lifted list; changed by DEC-922, DEC-953 (marks after the sitting) |
| DEC-897 | The secrets check's chance red | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-909 (marks after the sitting) |
| DEC-903 | W1-39's overlay case named for W2-66's test designer | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-904 | A full verification run against the scratch budget | ACCEPTED; archive: 'the retention trial and its bridge. Spent (DEC-905).' | **DONE** | medium | ARCHIVE §B (`2e5c9cd9`); §A: item 3's cap ended by DEC-905; the lock it kept is DEC-905's; changed by DEC-905, DEC-922 (marks after the sitting) |
| DEC-907 | W2-67's ticket role is engineer, its acceptance files named for its test… | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-908 | W2-07's test-designer batch gains the 14 W1-30 cases its KPIs also change | ACCEPTED; archive: 'W2-07's batch; W2-69's last rounds. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-909 | W2-69's last round | ACCEPTED; archive: 'W2-07's batch; W2-69's last rounds. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-910 | R3-A, W2-69's third review | ACCEPTED; archive: 'W2-07's batch; W2-69's last rounds. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-911 (marks after the sitting) |
| DEC-913 | W2-65 | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-914 | W2-67's rounds 2 and 3 run together as its run 3, with… | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-916 (marks after the sitting) |
| DEC-915 | The interim skip guard reads skip reasons from the close's evidence block | ACCEPTED; archive: 'the interim skip guard. Spent; lifted as a gate.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-953 (marks after the sitting) |
| DEC-917 | W1-38 holds the three guard lines to the exit-mapping form and the… | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-919 | W2-66's lead-verification case is a known red on a ticket branch that… | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-920 | W2-67's rounds 2 and 3 | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-921 | The two unpushed W2-59 and W2-65 merges are replaced by one merge… | ACCEPTED; archive: 'accepted history, merge rules, containment. Spent; feature lifted. DEC-912 and DEC-918 …' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-922 | The first re-pin is done (ACT-REPIN-1) | ACCEPTED; archive: 're-pins and their ACTs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-923 | P-W2-L423-Q (a) | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-925, DEC-953 (marks after the sitting) |
| DEC-926 | After W2-74's merge, the keyword warning leaves out only the four JUnit… | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished; changed by DEC-953 (marks after the sitting) |
| DEC-931 | W2-57's `load_sensitive` removals timed to where each fix lives | ACCEPTED; archive: 're-pins and their ACTs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-932 | DEC-931's reading accepted | ACCEPTED; archive: 're-pins and their ACTs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-935 | The second re-pin is done | ACCEPTED; archive: 're-pins and their ACTs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-937 | (delegated) — W2-58's close refused on W2-54's green-here fixture timing out under… | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); a one-off act, finished |
| DEC-940 | The state of the Gov OS | ACCEPTED; archive: 'the state of the Gov OS, answered by DEC-941. Spent.' | **DONE** | high | ARCHIVE §B (`2e5c9cd9`); answered by DEC-941 |

## E. Spent one-offs that an open ticket names as its origin — accept as a group?

Same as D, but an open ticket lists the decision in its `sources:` or a KPI bracket, as where it came from. DONE
keeps that link valid: `gov links` only objects to PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED ids in rule places.

| Id | Title | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|---|
| DEC-721 | The adoption-readiness block is built with W2-01 first and shown to pass… | ACCEPTED; archive: 'the adoption-readiness block, W2-01 first. Spent.' | **DONE** | medium-high | a one-off act, finished; open W2-46 cite it as origin (DONE keeps the link valid); changed by DEC-953 (marks after the sitting) |
| DEC-738 | The orchestrator's delegated choices of 2026-10-16, accepted by the owner | ACCEPTED; archive: 'the delegated choices of 2026-10-16. Spent.' | **DONE** | medium-high | a one-off act, finished; open W2-52 cite it as origin (DONE keeps the link valid) |
| DEC-747 | W2-20's packages of run 1, decided by the orchestrator (delegated) | ACCEPTED; archive: 'delegated run packages. Spent; containment's feature lifted.' | **DONE** | medium-high | a one-off act, finished; open W2-20 cite it as origin (DONE keeps the link valid) |
| DEC-757 | W2-01 closes by the owner's decision | ACCEPTED; archive: 'W2-01 closed by the owner, with the ratchet. Spent; feature lifted.' | **DONE** | medium-high | a one-off act, finished; open W2-19 cite it as origin (DONE keeps the link valid); changed by DEC-899, DEC-900, DEC-953 (marks after the sitting) |
| DEC-784 | W1-46's fixture removes every CLAUDE* variable (P-W2-34 (a)) | ACCEPTED; archive: 'W2-05's settings re-sort; the W1-46 fixture. Spent.' | **DONE** | medium-high | a one-off act, finished; open W2-56 cite it as origin (DONE keeps the link valid) |
| DEC-856 | P-W2-50 (a) and (b) | ACCEPTED; archive: 'the raw record leaves memory; pings confirmed. Spent.' | **DONE** | medium-high | a one-off act, finished; open W2-91 cite it as origin (DONE keeps the link valid); changed by DEC-887 (marks after the sitting) |
| DEC-877 | W2-59 | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | medium-high | a one-off act, finished; open W2-56 cite it as origin (DONE keeps the link valid) |
| DEC-890 | W2-66 split in two FULL tickets in sequence | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | medium-high | a one-off act, finished; open W2-19 cite it as origin (DONE keeps the link valid); changed by DEC-896, DEC-899 (marks after the sitting) |
| DEC-891 | W2-62's claim commit 162f17ea9caf accepted as history | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **DONE** | medium-high | a one-off act, finished; open W2-66b cite it as origin (DONE keeps the link valid); changed by DEC-906, DEC-924, DEC-953 (marks after the sitting) |
| DEC-892 | W2-63 waits for W2-07's ticket-class close | ACCEPTED; archive: 'refused closes and their repairs. Spent; feature lifted.' | **DONE** | medium-high | a one-off act, finished; open W2-82 cite it as origin (DONE keeps the link valid); changed by DEC-896, DEC-899 (marks after the sitting) |
| DEC-896 | Decision records measured by their decision (a W2-07 KPI) | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **DONE** | medium-high | a one-off act, finished; open W2-82 cite it as origin (DONE keeps the link valid); changed by DEC-891, DEC-923, DEC-953, DEC-1057 (marks after the sitting) |
| DEC-899 | The review point | ACCEPTED; archive: 'merge orders, splits and review points. Spent.' | **DONE** | medium-high | a one-off act, finished; open W2-136, W2-20, W2-81 cite it as origin (DONE keeps the link valid); changed by DEC-902, DEC-912, DEC-915, DEC-918, DEC-924, DEC-925, DEC-953 (marks after the sitting) |
| DEC-900 | The AR-9 ruling | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **DONE** | medium-high | a one-off act, finished; open W2-13 cite it as origin (DONE keeps the link valid); changed by DEC-906 (marks after the sitting) |

## F. "Spent" but still in force, or product record — accept as a group?

These seven should not be on the spent list. Five carry a standing rule; two are product record, which the archive's own line says.

| Id | Title | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|---|
| DEC-729 | The Wave 2 plan is approved | ACCEPTED; archive: 'the Wave 2 plan approved; W2-00. Spent.' | **In force until W2-00 closes; off the spent list** | medium | its item 3: commits of no other ticket carry W2-00's id, and W2-00 closes last; W2-00 (DAEO-sdxk) is open |
| DEC-786 | Stacked starts by rule | ACCEPTED; archive: 'stacked starts by rule. Spent, within DEC-942.' | **In force (item 1, stacked starts); mark Changed by DEC-847, DEC-942; off the spent list** | medium | §A: only its cap was replaced (DEC-847, then DEC-942); DEC-942 does not restate stacking; W2-55, W2-56, W2-60a cite it; changed by DEC-847 (marks after the sitting) |
| DEC-912 | W1-01's merge rule passes a merge whose acceptance files equal git's own… | ACCEPTED; archive: 'accepted history, merge rules, containment. Spent; feature lifted. DEC-912 and DEC-918 …' | **Stays ACCEPTED (product record); reword the archive line** | high | the archive line itself says 'DEC-912 and DEC-918 stay product record' |
| DEC-918 | Containment's merge rule matches DEC-912 exactly | ACCEPTED; archive: 'accepted history, merge rules, containment. Spent; feature lifted. DEC-912 and DEC-918 …' | **Stays ACCEPTED (product record); reword the archive line** | high | the archive line itself says 'DEC-912 and DEC-918 stay product record' |
| DEC-924 | P-W2-07-DR2 | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **In force (item 2: reports in commits of their own); off the spent list** | medium-high | its status line says 'item 2 standing'; nothing lifts it; changed by DEC-925, DEC-953 (marks after the sitting) |
| DEC-927 | P-TRACE-IMPL-1 (a) with two conditions | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **In force (item 2, re-adopted by DEC-1074 (7)); mark Changed by DEC-1057 (item 2); off the spent list** | medium | DEC-1057 lifted item 2; LINK-INTEGRITY §5, adopted by DEC-1074 (7), cites it again; W2-128, W2-129, W2-130 rest on it; changed by DEC-928, DEC-953, DEC-1057 (marks after the sitting) |
| DEC-928 | DEC-927's reading accepted (Contract ids the store holds are valid `Implements:` targets) | ACCEPTED; archive: 'history entries, readers, work without a task, `Implements:`. Lifted or spent.' | **In force (items 1 and 3); off the spent list** | medium-high | its status line says 'item 3 standing'; item 1 (CAP ids are valid Implements: targets) is how the trailer check reads; changed by DEC-953 (marks after the sitting) |

## G. Rows the readiness review added (reviewer 2, `reviews/readiness-2-links.md`)

| Row | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|
| MR-1 to MR-6 | the generated `docs/contract/master-rules/MR-n.md` say PROPOSED; `contract.yaml` says ACCEPTED; a search marks every master rule "not in force" | **Regenerate the six files from `contract.yaml`** (product-spec, before the release; no ruling on the rules themselves) | high | `gov links` STATUS_CONFLICT ×6; reviewer 2 F1; DEC-1074 (8)'s MR row |
| CONDITIONAL and DONE read as in force | DEC-020 (RAGFlow, CONDITIONAL) and DEC-056, DEC-071, DEC-077, DEC-078, DEC-079 (DONE) show "in force" in a search | **Confirm: DONE = not in force; CONDITIONAL = not in force until its trigger fires.** Then a code row for W2-92's status mark (D-6). No register change | high | reviewer 2 F5; W2-55's own rule: a done entry "is not in force" |
| Wrong "changed by" links | the loader reads a "Changed by:" note with no verb, or a clause with no subject, as naming changers: 11 links have a changer older than the decision it "changes" (e.g. DEC-880 <- DEC-843) | **Approve: no mark is committed on them** (5 would have been: DEC-072 <- DEC-064, DEC-162 <- DEC-156, DEC-501 <- DEC-512, DEC-780 <- DEC-775, DEC-1053 <- DEC-880); **the loader's fix is a D-6 row** (one changer per clause, by its leading id). The register's text is not edited | high | reviewer 2 F2; the list with a fix per link: `drafts/w2-130/e-spurious-changers.md` |
| ADR-0002 (PROPOSED file) | the architecture ADR is still PROPOSED | **Not in this sitting:** DEC-1097 (8) already brings its refresh to you before the lift | high | DEC-1093 (3), DEC-1097 (8) |

## H. Two choices only you can make

**H1. Closed tickets' `sources:`.** W2-130's patch adds 875 missing decision ids to 154 tickets. 104 of the tickets
are closed (481 ids). Since DEC-1088 (6), editing a closed ticket is itself a finding, "a decision id does not excuse
the edit", so that half would add 104 permanent CLOSED_TICKET_EDITED findings.
- (a) Allow this one links-only commit on closed tickets, named in the record. 0 UNLINKED_ID afterwards, 104 standing S16 findings.
- **(b) Recommended (medium):** link the 50 open and in-progress tickets only (394 ids). List the closed tickets'
  ids in W2-130's record. Change W2-130's KPI 4 to say "open and in-progress tickets". 1,097 UNLINKED_ID stay as
  history on closed tickets. Retrieval already reaches those ids through the commits.

**H2. The marks the auditor finds wrong.** The 180 marks go through an independent auditor first (KPI 3). 30
carry a mechanical warning (`drafts/w2-130/marks-audit.md`), for example the archive line that gives five decisions
four changers at once (DEC-454 to DEC-492).
- **Recommended:** a wrong mark is dropped. Where the archive's §A wording caused it, the line is rewritten one
  decision per line, with only the changer that decision's own entry names. W2-130's allowed paths include the archive.
- No allow-list, as LINK-INTEGRITY §9 says. Any finding left over is named in the record.

## What happens after you rule

1. The CTO applies your statuses in one commit: the register's status words, the archive and DECISIONS-IN-FORCE
   made to agree.
2. `gov links --propose-marks` is regenerated, because a decided status changes who counts as a changer:
   PROPOSED entries count once they are ACCEPTED.
3. The marks go to the auditor, then into commits: no-hint first (82 entries), then the rest.
4. Then the `sources:` commit, as you choose in H1.
5. Expected afterwards (measured on a scratch copy): STATUS_CONFLICT 116 → 0; UNMARKED_CHANGE 185 → 5 (the
   wrong links, until the loader row); UNLINKED_ID 1,877 → 1,097 with H1 (b), or → 0 with H1 (a).
