
## 282. The owner's two rules of 2026-10-22 from W2-50's refused close (register v0.282, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-895 — Owner entries validated with the pinned judge's own readers before they are sent; a stale probe found at merge time, not at close time
- **Status:** ACCEPTED (owner, standing, 2026-10-22, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`) · **Under:** DEC-862 (a), DEC-891, DEC-893, DEC-754, DEC-894, DEC-861, DEC-851 · **Basis:** W2-50's refused close of 2026-10-22 (DEC-894). The DEC-892 entry reached the owner's commit, and then the close, unvalidated. W2-58's merge (`4845b9b8`, 2026-10-21) changed five files W2-50's probe judged, and only the close, a day later, found it.
- **Decision:**
  1. **Validate before sending.** Before sending the owner any ratchet entry (`accepted_reds`, `load_sensitive`) or accepted-history entry to commit, the orchestrator validates it with the pinned judge's own readers: the ratchet and the close's history reader. It validates against the register text as it will stand, and says in the ACT ping that it passed. A wrong entry must never reach the owner's commit, let alone a close.
     - **How:** `~/.local/share/gov-os/pin-fecb870c/bin/python -E .gov-runtime/scratch/orchestrator/tools/validate_entry.py <patch> [<register as it will stand>]`. It runs `gov.close.ratchet._refused_because` and `gov.close.history._refused_because` from the pin, and the placeholder scan (DEC-893).
     - The one refusal expected before the owner's commit ("no commit of the history adds it") is reported as pending.
     - Tested: against the register as it stood at `49c24ac9` it refuses the DEC-892 entry with the close's own message; against today's register it passes.
  2. **Find a stale probe at merge time, not at close time.** When a merge into `w2/integrate` (or into a ticket branch) changes any file that a merged-but-not-closed FULL ticket's probe judged, the orchestrator schedules that ticket's fresh probe straight away, in parallel with other work, and notes it in the queue. Then its close never spends a full run to discover a stale probe. Row W2-M403 stays as the close's own backstop.
     - **How:** after each merge, `PYTHONPATH=<main tree>/src python3 .gov-runtime/scratch/orchestrator/tools/probe_impact.py <merge>` names each such ticket and the files. Its judged files are those its own commits changed, as the probe gate names them.
     - Tested: on W2-58's merge `4845b9b8` it names W2-50 and the five files its refused close listed; on W2-02's merge `94ac7951`, none.
     - A lead that merges `w2/integrate` into a FULL ticket's branch whose probe has already passed checks the same before it returns.
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §5 (the decision-record rule: validate before the ACT) and §3 and §15 (merges: the probe-impact check), v3.15;
  - `LEAD-w2-common.md` (a lead's merge into a FULL branch with a passed probe);
  - RESUME HERE;
  - the orchestrator's `tools/validate_entry.py` and `tools/probe_impact.py`.
- Next free id: DEC-896.

| Version | Date | Change |
|---|---|---|
| 0.282 | 2026-10-22 | Owner (recorded by the orchestrator, DEC-861): DEC-895 (validate every ratchet or accepted-history entry with the pinned judge's own readers before sending it, and say so in the ACT; at merge time, a merge that changes a merged-but-not-closed FULL ticket's judged files schedules its fresh probe at once). Next free id: DEC-896. |
