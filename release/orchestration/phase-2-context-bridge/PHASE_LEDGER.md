# Phase-2 Context/Retrieval Bridge: ledger (P2X-FAIL-1)

## BR-L-0001: the bridge domain is established (2026-09-25)

A fresh outer session (`034abd76…`, `claude-opus-5-5`) was launched by the owner's launcher BR-0001. It self-located
from Git rather than from the launcher's summary.

**What was verified directly.** The frozen product `3c880d8` is the tip of `phase2/approved-delta`, and its
product_code_digest is `f6b1b886…d8ef`. Review 8 is `P2-AR-0097`, committed at `58219d5` on `phase2/review-8`. Its
probe run shows 3 passed and 3 failed by design: the three failures are a2, b1 and b2, the reproductions of F1, F2 and
F3, and each asserts the secure outcome. The regression subset is 64/0. The zombie measurement shows `starttime`
unchanged in state `Z`. Contract v3 hashes to `4c2df291…5ed3`, the same value Phase 2 recorded. The owner's Review-8
disposition, OD-P2-10A/B, was committed at `6e7a2a3` while this session was starting. It authorises the bridge under
"P2X-FAIL-1" and names the acceptance token `P2_CONTEXT_RETRIEVAL_BRIDGE_READY`.

**Two things that were not where the launcher implied.** First, the Review-8 report was never committed as a file.
The full return survives only as the hand-back in the Phase-2 session transcript. It is now preserved, byte for
byte and with its provenance, under `EVIDENCE/review-8/`. Where the copy and the review commit disagree, the commit
governs. Second, no repository file defines "P2X-FAIL-1". The bridge treats it as OD-P2-10 §3–§12 plus OD-P2-10A/B
plus the launcher, and records that resolution in the launcher record. This is not an owner question: the three
records agree, and they leave no trade-off open.

**Where the work lives.** Everything is on branch `bridge/p2-context-retrieval`, a worktree based at `6e7a2a3`. The
Phase-2 integration branch `release/4.1.6-rc1` is not written, and neither is `release/orchestration/phase-2/`.
`tools/check_state.py verify` enforces this as a mutation boundary on every commit. Bridge code must stay inside this
domain, because `product_identity.py` counts top-level `tools/` as product code.

**A hazard carried forward.** `~/.claude/settings.json` sets `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6`. Every
spawn therefore passes its model explicitly, and each run's observed model is read back from its transcript.

**Next:** dispatch `BR-AR-0001`, a fresh Context/Retrieval Architect on model `opus`. It must return the architecture,
an implementation DAG and explicit reuse-vs-build decisions before any builder touches bridge code.
