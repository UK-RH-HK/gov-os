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

## BR-L-0002: the owner's Review-8 disposition is reconciled as mandatory input, with its authority classes kept exact (2026-09-25)

The owner sent a message during the session: refresh the Phase-2 durable records, then take OD-P2-10A/B and its
`evidence_for_the_synthesis` references in as mandatory bridge inputs, with the authority distinctions preserved.
The bridge had already been based on `6e7a2a3`, which records OD-P2-10A/B, and the architect had not yet been
dispatched. Nothing validly completed was therefore restarted.

**Refreshed.** The `release/4.1.6-rc1` tip was re-read. It is still `6e7a2a3`; no Phase-2 record is newer than the
bridge base, and the main checkout is clean. `P2-AR-0096.checkpoint.md` is not under `release/orchestration/phase-2/`
where the Review-8 brief implied it would be. It lives in the frozen product tree at
`3c880d8:telemetry/checkpoints/`, and is recorded there.

**Reconciled.** The state now carries `mandatory_bridge_inputs`, in which each item is hash-bound where it is a file
and carries an explicit class:

* `OWNER_DECISION`: OD-P2-10A, OD-P2-10B, Property-A preservation, the standing state;
* `OWNER_DIRECTION_TO_TEST`: F1 deletion/simplification, which is **not yet authority**;
* `HYPOTHESIS_TO_TEST`: F2/F3 as one class, which has **no classificatory force**;
* `HYPOTHESIS_RELEVANT_OBSERVATION`: the Phase-2 orchestrator's three reasoning errors, which concern its reasoning
  rather than the implementation;
* `EVIDENCE`, and `EVIDENCE_WITHDRAWN` for the withdrawn AR96 positive-control finding;
* `ORCHESTRATION_RECORD`: the context pack, the design records, ledger entries P2-L-0033..0047 and the Phase-2 state.

`check_state.py verify` now re-hashes these items. BR-HO-0001 makes them mandatory reading. It requires the
architect's authority model to represent these exact classes, and a direction or hypothesis must be structurally
incapable of entering packet section A. The demonstration's grading now fails any packet that blurs the classes.

## BR-L-0003: the enforced pre-merge checkpoint is proven on synthetic branches (2026-09-25)

`integrate-check` was run against four synthetic cases before any real run depended on it:

* a conforming branch: **PERMITTED**;
* a branch with a stray `runtime/` file and a tampered output: **REFUSED** on both counts;
* a branch without its typed report: **REFUSED**;
* a run whose declared scope lies outside the domain: **REFUSED**.

The throwaway branches and worktree were removed. The script is `selftest_integrate.sh` in the session scratchpad; it
is not committed.

The test surfaced one defect, and it has been fixed. Empty domain directories were not tracked, so role worktrees
had no `AGENT_RUNS/`. `.gitkeep` files now keep them.

## BR-L-0004: the owner clarifies the corpus and purpose (OC-BR-02), and the running architect is redirected (2026-09-25)

The owner clarified the bridge's scope while BR-AR-0001 was running. The bridge is **not** a retrieval system for
Review 8. Its corpus is the **whole canonical Governance OS repository**, with principled exclusions. Its purpose is a
**generic, provider/model-replaceable Governance OS self-memory/context foundation** that can later be promoted into
V8.3, rather than thrown away. Review 8 stays as the **first mandatory benchmark**, a difficult known case, and must
not bias the design.

The clarification is recorded verbatim, hash-bound, as `GATES/OWNER-CLARIFICATION-BR-0002-CORPUS-AND-PURPOSE.md`.
The orchestrator's reading of it is in `HANDOFFS/BR-HO-0001-A1`, which now governs over BR-HO-0001 where they
differ. The addendum names the ten items the architecture must define, one heading each. It adds a design test:
*if every Review-8 reference were deleted, would the architecture change?* Only the demonstration and oracle should.
It also adds a corpus-coverage node to the DAG.

**Liveness was checked, not assumed.** The architect's transcript was written seconds before the redirect. Its branch
had no commits and no `ARCHITECTURE.md`, only spike outputs, so the clarification reached it before any design was
frozen, and nothing is restarted. The write boundary is unchanged: the bridge reads the whole repository and still
writes only its own domain.

## BR-L-0005: the architecture lands, the first wave is dispatched (2026-09-25)

**BR-AR-0001 returned COMPLETED.** The orchestrator ran `integrate-check` itself rather than taking the architect's
word: the result was PERMITTED. It read the model from the transcript: `claude-opus-5-5` on all 256 turns. The branch
fast-forwarded into the bridge at `ae656ef`. GATE-BR-ARCH-DAG is SATISFIED.

**What the design is.** The design is generic, whole-repository and multi-ref. The inputs are a records ref (following
the tip), the frozen product and Review-8 evidence (both pinned, reporting `REF_MOVED` rather than drifting), and the
`phase2/*` tips as history. Current-ness is decided per path by partition ownership, reusing `product_identity.py`'s
PRODUCT_CODE line. It is never decided by score or by date. The routes are:

* exact;
* FTS5 lexical;
* tree-sitter Rust plus the existing Python AST plugin, with every call edge labelled exact or heuristic;
* a provisional `BAAI/bge-small-en-v1.5` over ONNX Runtime (CPU, bitwise-deterministic in the spike) behind the
  existing `gov-capability/1` protocol.

The hard authority invariant is enforced four ways: by type (only the resolver constructs a section-A item), by an
import boundary, by an independent validator that re-derives section A, and by an ordering invariant that no score
can invert. The `mandatory_bridge_inputs` classes are verbatim. OD-P2-10A/B are section-scoped, so the F1 direction
cannot inherit OWNER_DECISION from its file. D is split into D.1 decisions, D.2 directions and D.3 hypotheses.

**Why the product's own memory engine is not used.** Running it would call `gov init`, which writes the machine
adoption-floor store that F3's union reads. The bridge reuses the engine's designs instead.

**Three things the orchestrator checked or changed before dispatch:**

1. **OA-P2-06.** The architect models OA-P2-06 as ACTIVE, with only its stop condition superseded. The orchestrator's
   own memory said more had been superseded. The committed records support the architect, and no record supports
   the memory, so the memory claim is noted as unsupported (OBS-BR-01).
2. **Store isolation (BR-DAG-AMEND-1).** The store path had no override, and B2–B5 will run in parallel. B1 must
   therefore make the store root configurable through `GOVBRIDGE_STORE`, and each builder gets its own store.
3. **The sealed oracle.** Its directory is created outside every worktree, mode 0700, with an unguessable name. Its
   secrecy is procedural, because every role is the same OS user, so it is made **detective**: before grading, every
   non-TA transcript is grepped for the sealed name. Its integrity is cryptographic: the commitment is merged before
   any demonstration run.

**Dispatched in parallel (PG0):** BR-AR-0002, the fresh test-author on opus, which writes the held-out oracle; and
BR-AR-0003, builder B1 (core) on sonnet.

## BR-L-0006: the held-out oracle is written and committed by hash (2026-09-25)

**BR-AR-0002 returned COMPLETED.** The model was `claude-opus-5-5` on all 308 turns. The orchestrator ran
`integrate-check` itself, and it was PERMITTED. It merged with a merge commit, because the bridge branch had moved.

**What is sealed.** A 141 KB oracle sits in the sealed directory. It holds two 11-stage chains, each with exactly one
enforcement point. It also holds the side-by-side, the F1 evidence both ways, the 30 query-class answers, the
authority rows, the three generic controls, and 16 authority rows, one per `mandatory_bridge_inputs` item. The TA
verified 458 anchors against their Git blobs: 458 OK. The oracle asserts facts only. It does not classify F2/F3 and
does not dispose of F1.

**What the orchestrator checked, rather than accepted:**

* the sealed file's sha256 equals the committed commitment;
* the sealed directory's name appears nowhere in the branch diff;
* of 695 substantive oracle lines, the only one found verbatim in Git is the author-model metadata line.

**Routed:**

* OI-3 goes to I1. The grader's oracle validator must agree with the TA's stricter checker.
* OI-4 goes to I1. Section placement for EVIDENCE and ORCHESTRATION_RECORD items must be reconciled before grading.
* OI-1 goes to GRADE, which copies only `oracle.yaml`.
* OI-2 goes to the post-bridge synthesis. The TA found places where the code at `3c880d8` is more precise than, or
  differs from, the Review-8 return and the Phase-2 records. Those details stay sealed until grading.

## BR-L-0007: B1 (core) lands, and PG1 is dispatched in parallel (2026-09-25)

**BR-AR-0003 returned COMPLETED.** The model was `claude-sonnet-5` on all 269 turns. `integrate-check` was
PERMITTED, run by the orchestrator. The orchestrator re-ran part of the work itself instead of taking the report's
word:

* `tests/core`: 68 passed;
* a from-clean build into a **separate** store: FULL, 503,331 occurrences across 98 refs, 16 s, zero LLM calls;
* an immediate re-run: NOOP in 0.013 s;
* `exact show` on a product line: the right blob, labelled canonical.

**The coverage figure differs from the architect's, and this is correct.** B1 reports INCLUDED 3,639 against the
architect's 6,489. The difference is not a lost corpus. B1 implemented the architecture's `L-MACHINE-OUTPUT` rule,
under which 2,850 logs and outputs are indexed lexically and exactly but not embedded, and 3,639 + 2,850 = 6,489.
Unclassified is 0 on all 98 refs. B1 documented this rather than tuning a rule to hit the number.

**PG1 is dispatched in parallel** (model sonnet), each in its own worktree and with its own store
(BR-DAG-AMEND-1):

* B2 lexical: BR-AR-0004;
* B3 code: BR-AR-0005;
* B4 semantic: BR-AR-0006;
* B5 authority and graph: BR-AR-0007.

Their mutation scopes are copied from the DAG into the state, where `integrate-check` enforces them.
