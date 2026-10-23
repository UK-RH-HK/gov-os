
## 291. The owner's answer of 2026-10-23 on P-W1-01-H (register v0.291, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-906 — Only an independent test designer commits under tests/acceptance/ (standing); W1-01's history case reads an exact-commit exemption list holding c9a08678 alone; the lock until W2-67 lands
- **Status:** ACCEPTED (owner, 2026-10-23, in the chat; item 1 standing; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-23)`) · **Under:** MR-3, DEC-253, DEC-889 item 16 d, DEC-891, DEC-862 (a), DEC-895, DEC-900, DEC-905, DEC-861, DEC-851 · **Basis:** package P-W1-01-H (`governance/project/orchestration/packages/P-W1-01-H.md`). `tests/acceptance/W1-01/test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests` has been red on `w2/integrate` since the owner's `Role: owner` commit `c9a08678644485a7528bc875164e110881b63d93` (DEC-900's retirement of W1-42's two cases).
- **Decision:**
  1. **(c), standing.**
     - From now on, test retirements and any other change under `tests/acceptance/` are committed by an independent test designer, under the owner's named decision.
     - Only ratchet entries (`accepted_reds`, `load_sensitive`) and `accepted_history` entries stay the owner's own `Role: owner` commits.
     - Any owner commit that touches tests is validated with a full run in the close's form before the ACT ping.
  2. **(a), narrowed to a list, not a rule.** A `Role: owner` trailer is only text until W2-44 binds trailers to the launch, so W1-01's history case must not trust it as a standing rule.
     - **The list:** W2-70's test designer revises the case to read an owner-committed exemption list naming exact commits: the path map's `acceptance_exemptions`, beside `accepted_history`. Each entry is `{commit: <full sha>, decision: <DEC id>}`.
     - **Its only entry:** `c9a08678644485a7528bc875164e110881b63d93`, citing DEC-900.
     - **Everything else stays red:** any other owner commit touching `tests/acceptance/`, and any commit not listed by its exact sha.
     - **The entry** is the owner's own `Role: owner` commit, prepared by the orchestrator and validated first with a full run in the close's form (item 1).
     - **W2-70 merges early,** so the red leaves `w2/integrate` then.
     - **Until then,** leads report W1-01's case by name as known and not theirs, and the orchestrator does not count it against them.
  3. **The one-run-at-a-time lock** (`flock /tmp/gov-os-verify.lock`, DEC-904 item 3, kept by DEC-905 item 4) stays until W2-67 lands. Then the resource gate decides.
- **Changes:**
  - DEC-862 (a) and DEC-891 (which owner commits stay `Role: owner`: the ratchet and accepted-history entries, plus this exemption list's entries);
  - DEC-900 (its form: a retirement is a test-designer commit from now on);
  - DEC-905 item 4 (the lock's end).
- **Where it goes (DEC-851):**
  - this register, with DEC-862's, DEC-891's, DEC-900's and DEC-905's status lines marked;
  - the prompt §5 (the owner's commits) and §15 (the lock), v3.23;
  - `LEAD-w2-common.md` (W1-01's case as a known red until W2-70 merges; acceptance changes by test designers only);
  - RESUME HERE;
  - W2-70's ticket file and card (its own commit);
  - the prepared owner entry.
- Next free id: DEC-907.

| Version | Date | Change |
|---|---|---|
| 0.291 | 2026-10-23 | Owner (recorded by the orchestrator, DEC-861): DEC-906 (standing: changes under tests/acceptance/ only by an independent test designer under the owner's named decision; only ratchet and accepted-history entries stay Role: owner commits; an owner commit touching tests validated with a full run first; W1-01's history case reads an exact-commit exemption list, acceptance_exemptions, holding c9a08678 alone (DEC-900), by W2-70's test designer; the lock until W2-67 lands). Next free id: DEC-907. |
