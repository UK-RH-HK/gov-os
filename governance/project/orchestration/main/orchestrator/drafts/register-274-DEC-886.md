
## 274. The owner's pre-decision of 2026-10-21 for queue run 4: W1-07's `doctor` envelope case (register v0.274, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-886 — If W1-07's `doctor` envelope case fails again in a close's regression and passes alone, it becomes load-sensitive until W2-57, by the owner's commit; any other new red stays a package
- **Status:** ACCEPTED (owner, 2026-10-21, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-757, DEC-766, DEC-862 (a), DEC-871 (the precedent: W1-38's rulesync cases), DEC-885 · **Basis:** W2-02's refused close of 2026-10-21 (DEC-885). The case was red in the parallel regression and green alone at load 5. Row W2-L409.
- **Decision:**
  1. **The trigger.** In queue run 4, `tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` fails again in a close's regression but passes alone, the same pattern as W1-38's rulesync cases.
  2. **Then, no package.** The orchestrator:
     - prepares its `load_sensitive` entry in the path map: test, `decision: DEC-886`, the measured reason, and `fixed_by: W2-57`, with fix row W2-L409;
     - pings `ACT` for the owner's `Role: owner` commit, since the close reads that list only from one (DEC-862 (a));
     - re-runs that close once the commit is in.
  3. **Any other new red** still comes to the owner as a package.
  4. **The entry shrinks away** when W2-57 fixes the case: the orchestrator commits the removal (DEC-861: a removal only shrinks the list).
- **Where it goes (DEC-851):** this register; RESUME HERE; row W2-L409 (its "closes when" names W2-57 and this entry). It is one case's pre-decision, not a standing rule: it does not reach the prompt or the briefs.
- Next free id: DEC-887.

| Version | Date | Change |
|---|---|---|
| 0.274 | 2026-10-21 | Owner (recorded by the orchestrator, DEC-861): DEC-886 (pre-decision for queue run 4: W1-07's `doctor` envelope case, if red in a close's regression and green alone, goes on `load_sensitive` by the owner's commit, fixed by W2-57, row W2-L409; any other new red is a package). Next free id: DEC-887. |
