# ACT-LOAD-BALANCER-A: the agent's G4 refusal and the frozen copy (the CTO's filing slip, 2026-11-12 00:40 UTC)

**What happened.** After the owner's `yes ACT-LOAD-BALANCER-A 0b40f1bf` (chat, 2026-11-11 ~23:38), the CTO queued the
request; the operator agent took it at 23:40:07, passed G1-G3 and refused at G4: "the review record holds no verdict
block" (`~/gov-os-operator/log/operator.jsonl`, lines 96-100). The CTO had filed the reviewer's markdown section into the
bundle's `review.md` without the reviewer's fenced `verdict` block. Nothing was applied; the live launcher is unchanged
(`apply.sh check` prints `state before (sha256 03b93044ff98)`).

**Fixed on the CTO's side.** The bundle's `review.md` (`.gov-runtime/scratch/orchestrator/acts/ACT-LOAD-BALANCER-A/`) now
carries the reviewer's own verdict block verbatim (READY by `verdict.py`, three rows); the operator's own reader finds
it; `reviews/ACT-LOAD-BALANCER-A-review.md` likewise (commit `31a4f050c`). The manifest is unchanged (`0b40f1bf...`): the
ACT itself is not changed.

**Why it still needs the owner's operator.** G1 reuses an already frozen copy and never replaces it (F8), so the next
request for the same manifest would read the old `review.md` from
`~/gov-os-operator/acts/ACT-LOAD-BALANCER-A-0b40f1bfd84b/` and refuse again. That folder is the operator's; the CTO does
not write there.

**For the owner's operator (one of the two):**
1. **Recommended:** move the frozen copy aside (it was never applied):
   `~/gov-os-operator/acts/ACT-LOAD-BALANCER-A-0b40f1bfd84b` → `~/gov-os-operator/acts/rejected/ACT-LOAD-BALANCER-A-0b40f1bfd84b-g4-20261111`;
   then tell the CTO, who re-queues `ACT-LOAD-BALANCER-A 0b40f1bfd84b65d043a7e7e2599d0717139461885f8f73462a3f24751b7a8e5f`;
   the agent re-freezes from the corrected bundle and runs G1-G9 (the owner's yes of 23:38 stands; same manifest).
2. Or apply ACT A by hand from the bundle as its package §3-5 says (`apply.sh check`, `apply`, the four checks, the commit).

**Undo.** Option 1: move the folder back. Option 2: `apply.sh undo`, as the package §5 says.

The same slip would have hit ACT-PATHMAP-EXP-1 (not yet queued); its `review.md` is corrected too. The CTO's memory now
holds the rule: copy the verdict block and check with the operator's reader before any request.
