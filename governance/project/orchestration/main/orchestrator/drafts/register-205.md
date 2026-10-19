
## 205. W1-38 round returns PACKAGES: one delegated decision on a test helper (register v0.205, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-675 — The W1-33 helper of the designer pass is split so that W1-28's fixture-copy check still sees and runs its copy; the second W1-49 case is kept as written
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-13; told to the owner, who may replace it) · **Under:** DEC-385, DEC-665, DEC-669, DEC-584 · **Basis:** the W1-38 round lead's return (`log/W1-38-lead-runM.json`, PACKAGES at `832fd8d4` on `w1/W1-38`): the DEC-664 piece is built and verified (W1-38 201 passed; in a project made from the template the guard allows the independent test designer under the test folder and refuses the five other roles); the designer pass of DEC-665 rewrote the three cases (`9dd9c052`), and its new helper in W1-33's support module leaves two cases of `tests/acceptance/W1-28/test_w1_28_fixture_copies.py` red
- **Decision** (P3, test-only, reversible; the lead's recommendation and mine agree; confidence medium):
  - **DP-1, option (a):** W1-28's synthetic repository gets one more made-up file at the adapter source's place for the research definition, and W1-33's helper is split into a copy step the check can call and a generation step with no root parameter. The check keeps its reach: it still sees and runs the copy. One test-designer session writing in W1-28 and W1-33, with a `Rewrite-Reason:` trailer for each existing case it changes. This is the round's one further run (DEC-584); the probe follows.
  - Option (b), a helper the check no longer sees, is not taken: it narrows what the check for copies of the held-out file can catch.
  - **The second rewritten W1-49 case is kept as written** (the pass designer's recommendation): it holds a session's environment to a window of 270,000 to 330,000 and the project to not setting it; it is skipped outside a Claude Code session and cannot tell the user-level settings from another source of the variable. Named residual; no case reads under the user's own settings folder.

| Version | Date | Change |
|---|---|---|
| 0.205 | 2026-10-13 | Orchestrator, delegated: DEC-675 (W1-38 round's DP-1 option (a): W1-28's synthetic repository gets one more file and W1-33's helper is split, the fixture-copy check keeps its reach; the second rewritten W1-49 case kept as written, named residual). Next free id: DEC-676. |
