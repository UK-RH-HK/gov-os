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

## BR-L-0008: B2 (lexical) and B3 (code) land; B2 exposes a cross-module hazard (2026-09-25)

Both returned COMPLETED on `claude-sonnet-5`, B2 with 210 turns and B3 with 230. Both `integrate-check`s were
PERMITTED, run by the orchestrator. The orchestrator re-ran the following itself, in separate stores:

* **B3.** 108 tests pass. The caller of the kernel-partition function at `3c880d8` is exactly `cit/mod.rs:1623`,
  labelled EXACT_PATH, with one target. `reads-key mutation` reaches `tools.rs`. The control on an unrelated
  subsystem (`resolve_state_root`) has 30 call sites, none unlabelled.
* **B2.** 83 tests pass. A from-clean build with the lexical layer takes 22 s, with 0 LLM calls. The query returns
  the frozen product's occurrence as CANONICAL, the review commit's as SAME_AS_CANONICAL and older `phase2/*` tips as
  HISTORICAL_VERSION, in 0.35 ms. This is the multi-ref model working.

After merging, the integrated tree passes **123 tests together**.

**The hazard B2 found.** The core manifest calls every registered layer's digest even where that layer's tables do
not exist, and layers register only on import. B2 fixed its own digest. B4 and B5 were confirmed live and got a
one-line advisory within their scopes. The central fix, and the CLI importing every layer, go to I1 under
BR-DAG-AMEND-2, together with B3's unwired Python-AST index. B4 (semantic) and B5 (authority/graph) are still running.

## BR-L-0009: B4 (semantic) lands; the four routes are integrated (2026-09-25)

**BR-AR-0006 returned COMPLETED** on `claude-sonnet-5` (376 turns). `integrate-check` was PERMITTED, run by the
orchestrator. The orchestrator re-ran the following itself:

* 106 tests (core plus semantic);
* the determinism check in **two separate processes**, with an identical vectors digest each time and batch-1 equal
  to batch-32;
* a query against B4's built store. The results carry full provenance (path, commit, lines, canonical ref and
  version status) and are labelled `RETRIEVED`. The authority fields are the fail-closed placeholders
  `UNCLASSIFIED`/`UNKNOWN`, because B5's classifier is not in B4's base. This is the correct default.

The 36-minute full rebuild was not repeated, because I1 must rebuild from clean twice anyway. The builder's store
recorded 40,187 embedded chunks, with **no** machine-output or history-only chunk embedded.

**After merging**, the full bridge suite passes together: **161 tests**. The exact, lexical, code and semantic routes
are now all on the bridge branch.

B4's six open issues go to I1:

* layer auto-discovery;
* where the semantic pins sit in the manifest;
* wiring B5's classifier into every route's results;
* a model-pin path mismatch;
* per-batch commits for resumable rebuilds;
* a stale local manifest.

I1's scope therefore also gains `config/model-pin.yaml` and `bootstrap/**`.

**B5 (authority and graph) is the only PG1 node still running.** It received the BR-DAG-AMEND-3 clarification while
live.

## BR-L-0010: B5 (authority and graph) lands; the authority classes are verified by the orchestrator; B6 is dispatched (2026-09-25)

**BR-AR-0007 returned COMPLETED** on `claude-sonnet-5` (544 turns). `integrate-check` was PERMITTED. This node holds
the foundations of the hard authority invariant, so the orchestrator checked the resolver's real output itself, item
by item:

* OD-P2-10A is `OWNER_DECISION`, scoped to its own section;
* **F1-DIRECTION is `OWNER_DIRECTION_TO_TEST`**;
* **F2-F3-COMMON-CLASS is `HYPOTHESIS_TO_TEST`**;
* the reasoning-errors item is `HYPOTHESIS_RELEVANT_OBSERVATION`;
* the AR96 gap is `EVIDENCE_WITHDRAWN`;
* the whole-file OD-P2-10A/B reference **fails closed to `UNCLASSIFIED`**, so a file's class never flows into its
  sections.

`resolver.py` and `lifecycle.py` import no retrieval route. BR-DAG-AMEND-3 is implemented: the records, edges and
class rows are persisted and digested, and the resolver stays store-independent.

**The first real integration defect.** Plain `pytest tests -q` fails at collection. B3's and B5's
`test_history.py` share a basename, which no single builder could see. With `--import-mode=importlib` the integrated
suite passes: **240 tests**. The fix, plus B5's five open issues, goes to I1. Those issues include the hard-coded
state-file aliases in code, which break the letter of OC-BR-02.

**Dispatched B6** (route and compile, BR-AR-0008, sonnet), based on `e49b8a4`.

## BR-L-0011: B6 (route and compile) lands; the orchestrator finds mandatory inputs demoted to "supplementary" and rules on it (2026-09-25)

**BR-AR-0008 returned COMPLETED** on `claude-sonnet-5` (377 turns), and its `integrate-check` was PERMITTED. Its code
enforces the hard invariant as B6 was briefed:

* the only path into A is an isinstance-checked `MandatoryItem`;
* the validator re-derives A;
* ordering is by stratum;
* the directions and hypotheses land in D.2 and D.3 with their banners.

It merged at `a935c76`, and the integrated tree passes **274** tests.

**What the orchestrator found by compiling the real demonstration task itself.** Ten mandatory inputs were placed
in **section H, "supplementary retrieved context"**, among them **Contract v3**, the frozen gate contract and the
owner's own launcher. The builder had reported this as "correctly excluded". The cause lies in the design, not in
the builder:

* `packet.py:178` admits a mandatory item to A only when its lifecycle is `ACTIVE`;
* files without a machine-readable status map to `UNKNOWN`;
* the registry may never raise a lifecycle.

Together these mean a contract without a status line can never be delivered as a mandatory input. That is exactly
the substitution the owner forbade.

**BR-ARCH-RULING-1** resolves the conflict in favour of the owner text (launcher; OD-P2-10 §6; W10). Section A
membership is decided by the resolver and the class, **never by lifecycle**. Lifecycle stays visible, is flagged in
J, and still gates D.1 and ordering. Nothing is raised to ACTIVE. It is recorded as an **orchestrator ruling, not an
owner decision**, so the verifier may challenge it.

A **fresh** builder implements it (B6R, BR-AR-0013). Its tests must include a validator negative control and the
real-view section map. I1 waits for B6R.

## BR-L-0012: B6R lands; every mandatory input is now delivered as mandatory; I1 is dispatched (2026-09-25)

**BR-AR-0013 returned COMPLETED** on `claude-sonnet-5` (224 turns). `integrate-check` was PERMITTED. The orchestrator
read the invariant-module diff itself. It changes three things and nothing else:

* the one conjunct in `place_item` is removed;
* a lifecycle banner and a J notice are added;
* the validator's `!= ACTIVE` refusal is replaced with a *stricter* banner check.

Section A is still re-derived through a single function.

**Re-run by the orchestrator:** the integrated tree passes **280** tests. The orchestrator also compiled the real
demonstration task itself. All 20 A-admissible mandatory items are now in A, including Contract v3, the frozen gate
contract and the owner launcher, each carrying an honest `UNKNOWN` lifecycle banner and a J notice. The other items
are placed as follows:

* **F1-DIRECTION** is only in D.2, with "NOT YET AUTHORITY".
* **F2-F3-COMMON-CLASS** is only in D.3, with "NO CLASSIFICATORY FORCE".
* The reasoning-errors observation and the withdrawn finding are in F, each with its banner.
* The whole-file reference is in H as `UNCLASSIFIED`.

**Dispatched I1** (BR-AR-0009, sonnet, the cross-cutting integrator). It carries every routed open issue from B1–B6,
the TA and the ruling. The orchestrator will check its merge rules by `git diff`:

* existing test files are frozen, apart from pure renames;
* the invariant modules are near-frozen;
* plain `pytest tests -q` must pass.

## BR-L-0013: I1 lands; the integrated bridge is reproducible; the view is frozen for the demonstration (2026-09-25)

**BR-AR-0009 returned COMPLETED** on `claude-sonnet-5` (777 turns, about 3.5 h). `integrate-check` was PERMITTED.
The orchestrator enforced I1's merge rules by `git diff` rather than on trust:

* no existing test was modified; there are 15 additions and one pure rename, which fixes the basename clash;
* `validate.py` is untouched;
* the three authority-module edits are the sanctioned move of path constants into config, plus a **stricter**
  multi-path check;
* the resolver still imports no route.

Plain `pytest tests -q` passes **308** tests.

**The proofs hold, and one was earned by accident.**

* **Reproducibility.** Two from-clean builds at the same records commit give an identical `manifest_sha256`
  (`3b68840c…1b2c`).
* **Incremental ≡ full.** The orchestrator's own commit landed between I1's first two builds (OBS-BR-03).
  Freshness correctly reported INCREMENTAL, and the incrementally updated first store then reached **the same hash**
  as the from-clean build at the new tip.

A full from-clean build of all 98 refs, including embeddings, takes about 38 minutes and makes **zero LLM calls**.

**The records ref follows the bridge tip,** so the demonstration needs a fixed view. This commit therefore opens a
**freeze**: no commits to the bridge branch until grading returns. D1, DEMO and GRADE record their progress on their
own branches, which the state names, so a resumed orchestrator can pick them up without this conversation.

## BR-L-0014: D1 measures the whole repository, and finds that the code layer was never in the reproducibility proof (2026-09-25)

The orchestrator ran D1 itself on `bridge/d1-0010`, at the frozen view `cf7efe7`.

**Coverage holds across the whole repository.** For every one of the **98** view refs, the per-rule file counts sum
exactly to `git ls-tree -r --full-tree`. Nothing is unclassified, and every exclusion names its rule. `X-SELF` excludes
only the bridge's own generated outputs, one of which is `DEMONSTRATION/**`. That keeps the oracle out of every index
once it is unsealed.

**Cost, measured.** A from-clean build takes **2,302 s** wall and **9,253 CPU-seconds**, peaks at 530 MB RSS, occupies
838 MB of local store, and makes **0 LLM calls**. Semantic embedding is 89% of the time (2,047 s); the authority and
graph layer takes 230 s, core 17 s and lexical 5 s. The no-change check is a NOOP in **0.02 s**.

**Two gaps D1 found.**

1. **I1 never committed** the build manifest or the telemetry rows that the DAG assigned it. `integrate-check`
   verifies format and scope, not a node's deliverable list. D1 closes this.
2. **The code layer was empty in the manifest**: 0 rows, with the digest of the empty string. B3 built the code
   route **lazily**, parsing only on a query, so both of I1's reproducibility proofs, and the incremental ≡ full
   proof, **never covered code symbols, calls or literals**, although §8.1 requires them. The digest also omits
   call sites and literals altogether, and the layer's contents drift with whichever queries have run.

**Secrecy audit, and a flaw of the orchestrator's own.** The orchestrator recorded the sealed path in the state,
which builders read, so four roles saw the path string passively. Across every non-TA transcript there were **zero**
tool calls touching `.local/share`, `govbridge-sealed` or `.authoring` (OBS-BR-04). The name was exposed; the oracle
was not accessed.

**Action.** The freeze is lifted *before any demonstration run*. A fresh bounded repair, **B3R (BR-AR-0014)**, makes
the code layer eager for the non-history refs, with a digest over all three row kinds that is query-invariant.
Afterwards the demonstration store is updated incrementally, the freeze is re-established, and D1 is finalised.

## BR-L-0015: B3R lands; the code layer is eager, deterministic, query-invariant and honours exclusions; the view is frozen again (2026-09-25)

**Pass 1** of BR-AR-0014 closed D1's finding. The code layer now builds eagerly for the non-history refs; the ref set
is derived from the view's roles, never from names. Its digest covers symbol, call-site and literal rows, is
reproducible across two fresh stores, and does not change when a history query parses more blobs.

**The orchestrator found one more defect before merging:** a **security-policy bypass**. Eleven `.rs` blobs that
the corpus rules exclude as `X-SEC-CONTENT` had been parsed into the code tables, contributing 7,551 literal rows.
They include `runtime/src/security/secrets.rs` and `tests/certification/brownfield.rs`. The flaw was already
present in B3's lazy route; making the layer eager would have put it into every build and into the digest. B3R was
reopened.

**Pass 2** fixed this, and the orchestrator re-measured it in B3R's fresh store. The code route now classifies every
blob through the existing corpus API, on both the eager and the lazy path. The measured result:

* the 11 excluded blobs leave **0** rows in any code table;
* all 11 are recorded as disclosed exclusions, each with its rule id;
* `blobs_parsed` = **233**, equal to the independent count of INCLUDE-verdict blobs;
* an idempotent in-place migration lets the existing demonstration store take the new schema.

Plain `pytest tests -q` passes **325** tests on the merged tree.

**This commit re-establishes the freeze.** Next, D1 is finalised against it by an incremental update of the
demonstration store, followed by the demonstration itself.

## BR-L-0016: the demonstration packet is compiled and not dispatched, because section G is empty; B6R2 is dispatched (2026-09-25)

D1 was finalised on its own branch at the frozen view `fa25492`:

* coverage across all 98 refs matches `git ls-tree --full-tree`, with 0 unclassified;
* the demonstration store was brought to the tip. The update ran **FULL** (2,215 s), because the bridge's own code
  tree changed;
* the manifest now carries a real code layer: 233 blobs, 197,348 rows and 11 disclosed exclusions;
* freshness is a NOOP (0.012 s);
* the build manifest and telemetry are committed, which closes I1's gap.

**The orchestrator then compiled the real demonstration packet itself.** `packet verify` PASSES, and every authority
class is placed exactly. **Section G, code/test/enforcement surfaces, is empty.** §7.2 fills G from *seed symbols*,
but the task seeds are records and nothing derives symbols from them. The query pass also calls the code route only
for symbol-shaped tokens, and code-file hits are placed by class, which puts them in H. This is a generic compiler
gap, and it sits exactly where the demonstration's code chains need context. So **the packet was not given to an
agent**. It is preserved as `run-0-predispatch-g-empty` evidence, and a fresh bounded repair was dispatched: **B6R2,
BR-AR-0015**. Its acceptance includes an **unrelated D-0006 control**, so the fix cannot be shaped around Review 8.

**Two further gaps are recorded for the verifier rather than repaired:**

* **OBS-BR-05:** the grader's G7 "≤ 1% of corpus" check is silently disabled. The rubric grader will compute it.
* **OBS-BR-06:** queries write no supplementary packets. The agent saves its query outputs instead.

**The freeze is lifted again.** It is re-established after B6R2.

## BR-L-0017: B6R2 needed two passes; the demonstration packet now carries the enforcement points; third freeze (2026-09-25)

**Pass 1** populated section G, and it passed its own checks. The orchestrator then compiled the real packet itself
and found it unusable, for four reasons:

* `packet.md` was **890 KB**, over 1% of the corpus. The G budget counted item content, not the ~300 bytes of
  metadata per rendered item.
* `manifest.json` was **6.1 MB**, above the 5 MB committed-file limit, because of drop records.
* G held 1,947 fan-out items from unrelated files, while **the anchors that the seed record itself cites**
  (`tools.rs:1817`, `policy_precedence.rs:911/940/786`) had been dropped by the budget.
* A cited line was resolved to a heuristic call target instead of its own enclosing definition.

That is the recurring failure in this programme: upstream noise crowding out the real decision point. B6R2 was
reopened.

**Pass 2** fixed all four, and one more defect it found itself. The orchestrator re-measured the real compile:

* `packet.md` is **274,572 bytes** and `manifest.json` 417 KB;
* `packet verify` PASSES and section A is unchanged;
* G has 325 items, tiered with seed citations pinned first, so **every Review-8-cited anchor is present as the
  cited line plus its enclosing definition**;
* the compile takes 88 s, down from 8 minutes;
* 329 tests pass, and `validate.py` was never touched.

**The third freeze begins at this commit.** Next, the demonstration store is updated to this tip, and D1 records an
addendum. Then `run-1` is compiled and a fresh demonstration agent is dispatched.

## BR-L-0018: the demonstration ran and failed on recall and size; four owner directions; checkpoint discipline is enforced; the freeze lifts (2026-09-26)

**Run-1 was compiled and dispatched at the third frozen view, `94d0211`.** The packet was 274,798 bytes,
`packet verify` PASSED, and all mandatory inputs sat in A, with the F1 direction in D.2 and the F2/F3 hypothesis in
D.3. A fresh Opus agent answered all 41 queries. It reached `RepositoryContract::decide` as the enforcement point for
both chains, and it found things Review 8 had not stated. The orchestrator's secrecy audit found 0 accesses and 0
oracle-substance overlaps; the 73 verbatim overlaps were all `path:` locators.

**GRADE, a fresh Opus, returned DEMONSTRATION_FAIL.**

* Pass: G1–G3. Authority preservation held exactly.
* Fail:
  * **G4**: the chains miss required stage facts and anchors;
  * **G5**: 1 of 10 query classes pass, with recall below 0.8 on decisions, failed approaches, tests, stale evidence,
    current-vs-superseded and deletable;
  * **G6**: consumer recall 0.75;
  * **G7**: 1.34 MB of packet and raw query outputs, 1.67% of an 80.3 MB corpus;
  * **G8**: the controls.
* The grader also found nine defects in the deterministic grader itself, GD-1..9.

**The shape of the failure is informative.** The bridge delivered authority correctly but did not deliver
**complete relevance**. The agent had to issue 103 queries of its own, and it still missed facets. That points
directly at the gap OD-BR-05 names: no facet decomposition, no multi-round retrieval, no budgeted supplementary
packets.

**Four owner directions arrived during the freeze.** Each was recorded verbatim on a side branch, so the view did not
move:

* **OD-BR-03**: verifier challenge items.
* **OD-BR-04**: checkpoint discipline. Before it, there had been no outer checkpoint since BR-CP-0002. Enforcement is
  now in place: `check_state.py checkpoint`; `verify` refuses a state without a matching checkpoint, effective from
  this commit; `integrate-check` enforces schema-2 worker checkpoints; PreCompact/SessionEnd hooks exist, but are
  **not confirmed live in this session**. A labelled retrospective reconstruction was also added.
* **OD-BR-05**: multi-batch / multi-hop retrieval, assessed as not conforming.
* **OD-BR-06**: the durable architecture and continuity record, with a deterministic resume order and the V8.3
  carry-forward in `V8_3_CARRY_FORWARD_FROM_CONTEXT_BRIDGE.md`.

**The freeze lifts.** D1, DEMO and the side branch merge. **GRADE stays QUARANTINED** on `bridge/grade-0012`,
because it holds the unsealed oracle. Builders and any run-2 agent must never read it, and run-2 needs a fresh sealed
oracle (OBS-BR-10).

**Next:** a fresh failure analyst classifies each failed gate and produces a generic repair DAG that contains no
oracle content.

## BR-L-0019: REPAIR-1 builds and integrates all twelve nodes; the integration audit is dispatched (2026-09-26)

**Every REPAIR-1 build node is integrated, and the full domain suite passes (731 passed, 0 failed).** The nodes, in
`ORCHESTRATOR_STATE.yaml` → `agent_runs` BR-AR-0017 … 0027 and 0034:

| Node | Run | What it delivered |
|---|---|---|
| R1-RN | BR-AR-0017 | Evidence notes |
| R1-RX | BR-AR-0018 | `retrieval_exclusions` applied automatically |
| R1-RL | BR-AR-0019 | A lineage layer over every eager ref: TESTS edges including Rust binary and harness-method dispatch and test-registry rows; DEPENDS_ON_DATA; CITES_REQUIREMENT |
| R1-RG | BR-AR-0020 | The grader repaired: GD-1..10 and D-1..D-5 |
| R1-TA2 | BR-AR-0021 | The run-2 oracle, sealed; commitment `a2030be9…7a7e` |
| R1-RM | BR-AR-0022 | Mandatory fidelity: declared-versus-delivered hashes; Markdown and YAML entries in document order |
| R1-GA1 | BR-AR-0023 | `govbridge gather`: facets, deterministic parallel retrieval, scope pushed down, paging |
| R1-GA2 | BR-AR-0024 | A multi-hop follow-up priority queue, count-only content budgets, provenance merge, versions by role |
| R1-RS | BR-AR-0025 | Supplementary packets and exact rendered-body re-extraction |
| R1-GA3 | BR-AR-0026 | Compile from gather: facet quotas, content slices, overflow to notes and supplementary packets |
| R1-RA | BR-AR-0027 | `cite`, `answers lint`, `gather` multi-hop by default, `compile --out` persisting the overflow |
| R1-XC | BR-AR-0034 | Cross-cutting fixes, read-only query paths, and one resolved view per operation |

**Amendments.** The orchestrator recorded BR-DAG-AMEND-R1-1 … R1-23 and template amendments R1-T1 (the full suite
last), R1-T2 (a conformance table; no silent narrowing) and R1-T3 (the pinned interpreter only).

**What verification caught.** Almost every builder returned at least one narrowed deliverable or false zero at
first. Each was caught by the orchestrator's re-measurement and reopened.

**Breach.** One rule-6 breach: BR-AR-0034 installed an unpinned package into a private venv. Its evidence was
rejected (OBS-BR-18); the shared venv was untouched.

**Secrecy.** 0 oracle, sealed or grading accesses in any transcript.

**Now running.** **R1-INT, BR-AR-0028, on Opus**, an audit-only integration audit with 15 checks. Its handoff is
BR-HO-0028; it pins the view and builds two from-clean stores. It started at 2026-09-26T18:34Z.

**Remaining path to BUILT:**
1. The R1-INT verdict.
2. Routed fixes for any of its defects.
3. R1-MB, the multi-batch demonstration. CONTROL-B is chosen at dispatch.
4. R1-D2, the frozen-tip store.
5. R1-DEMO2.
6. The secrecy audit of DEMO2.
7. R1-GRADE2, on a quarantined branch.
8. On DEMONSTRATION_PASS only: finalise the verifier handoff §5, then BUILT.
