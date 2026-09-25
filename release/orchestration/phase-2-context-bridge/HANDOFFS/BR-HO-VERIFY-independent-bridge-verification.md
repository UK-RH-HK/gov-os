# BR-HO-VERIFY: independent verification of the Phase-2 Context/Retrieval Bridge

> **Status: DRAFT until the build stage ends.** The orchestrator finalises §5 (the evidence), then commits. This
> handoff is self-contained. **You need no conversation, transcript or memory to act on it.**

| Field | Value |
|---|---|
| Your role | **Fresh, independent bridge verifier.** You did not architect, build, integrate, author the oracle, answer the demonstration or grade it. The next control-panel stage dispatches you. |
| Token you may issue | **`P2_CONTEXT_RETRIEVAL_BRIDGE_READY`** (OD-P2-10B), **only if earned**. Otherwise return `P2_CONTEXT_RETRIEVAL_BRIDGE_REJECTED`, with blocking findings. |
| Token you are verifying | `P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT`. The build-stage orchestrator emitted it. It is a **builder-level claim, not an acceptance.** |
| Routing | The owner's routing is "final independent bridge verification: fresh Opus 5". Spawn with `model: opus`, and record the model you actually are. |

## 1. Locate everything from Git. Trust no summary, including this one.

```
git -C /home/usain/Dynamic-Agentic-Engineering-OS worktree list | grep bridge-p2-orchestrator
# branch bridge/p2-context-retrieval; domain release/orchestration/phase-2-context-bridge/
python3 release/orchestration/phase-2-context-bridge/tools/check_state.py show
python3 release/orchestration/phase-2-context-bridge/tools/check_state.py verify   # exit 2 = conflict
```

Work in a **fresh worktree** of your own, cut from the bridge branch tip named in §5. **Never** write to the bridge
branch, to any `phase2/*` branch, to `release/4.1.6-rc1`, or to the frozen product `3c880d8`.

## 2. The requirements you verify against, in authority order

1. The owner records:
   * `release/orchestration/phase-2/GATES/OWNER-AMENDMENT-P2-0010-CONTEXT-RETRIEVAL-BRIDGE.md`: §3–§12, above all
     §5 (the eighteen capabilities), §6 (the authority model) and §11 (cost);
   * `…/phase-2/GATES/OWNER-DECISION-P2-0010A-B-REVIEW-8-DISPOSITION.md`;
   * `…/phase-2-context-bridge/GATES/OWNER-LAUNCHER-BR-0001-P2X-FAIL-1.md`, the launcher, verbatim. It holds the
     capability list, the ten compiler sections A–J, the **hard authority invariant**, the semantic bootstrap rule,
     and the **Review-8 demonstration** with its ten query classes;
   * `…/phase-2-context-bridge/GATES/OWNER-CLARIFICATION-BR-0002-CORPUS-AND-PURPOSE.md` (OC-BR-02). The corpus is the
     **whole canonical repository**. The bridge is a **generic, replaceable, promotable** foundation. Review 8 is a
     benchmark only.
2. `ORCHESTRATOR_STATE.yaml → mandatory_bridge_inputs`, with the authority classes that must be preserved exactly.
3. The architecture, `ARCHITECTURE/**` from BR-AR-0001. This is a design, **not** an authority over the owner records.
4. The orchestrator's rulings and amendments. **These are not owner decisions, and you may challenge them**:
   * `GATES/BR-ARCH-RULING-1-MANDATORY-INPUTS-ALWAYS-IN-A.md` and its Addendum A1;
   * the state's `dag.amendments` BR-DAG-AMEND-1, -2 and -3;
   * the state's `observations`.

## 3. What the bridge must never be. Verify each as a negative.

- It must not modify the frozen Phase-2 product `3c880d8` (`product_code_digest f6b1b886…d8ef`), or any
  `release/orchestration/phase-2/` record. `check_state.py verify` enforces a mutation boundary; **re-derive it
  yourself with `git diff`**.
- It must not change Contract v3 (sha256 `4c2df291…5ed3`), the frozen gate contract, or kernel/runtime trust
  semantics.
- It must not become an authority source. Every derived or retrieved item must be labelled as such.
- It must not claim V8.3 CURRENT, earn Phase 3, or have run a model bake-off or Phase-3A research.
- It must not repair, classify or dispose of F1–F6.

## 4. What to attack. Do not pass by re-running the builders' own checks.

- **The hard authority invariant.** Try to get a retrieved, graph-derived or code-derived item into section A, or to
  displace an A item. Try to make a superseded record outrank a current one, or enter D.1. Try to make F1-DIRECTION
  or F2-F3-COMMON-CLASS render as a decision or classification. **Move the index aside, and confirm A is
  byte-identical.**
- **BR-ARCH-RULING-1.** Is it right to deliver lifecycle-`UNKNOWN` mandatory items (Contract v3 among them) in A,
  with a banner, instead of excluding them? Does anything now reach A that should not?
- **Genericity (OC-BR-02).** Is anything Review-8-shaped in code, not just in data? Do the controls (CTRL-1..3) pass
  on their own merits? Pose your **own** unrelated query, too.
- **Whole-repository coverage.** Check coverage against `git ls-tree` yourself, at every view ref. Look for silent
  exclusions. The known ones are `L-MACHINE-OUTPUT` (lexical only) and the eight secret-content files (exact only).
- **Reproducibility and freshness.** Two from-clean builds must give an identical `manifest_sha256`. Incremental
  must equal full. The no-change check must make no LLM call. **Modify a record, then confirm that only the dependent
  layers change and a stale packet is detected.**
- **The Review-8 demonstration.** Would the grading still pass if the demonstration agent's answers stopped at an
  upstream representation? Does G7's "no dumping" measurement hold against the transcript? **Was the sealed oracle
  plausibly exposed to any builder** (the orchestrator's transcript grep result is in §5)?
- **Replaceability.** Could the provisional embedder (`BAAI/bge-small-en-v1.5`) be swapped without redesign, per
  ARCHITECTURE.md §9–§10? Is anything outside the adapter coupled to its identity or dimensions?

## 5. Evidence produced by the build stage (FINALISED BY THE ORCHESTRATOR AT BUILD END)

*(to be completed: bridge tip commit; the integration run's reproducibility and equivalence results; the D1 coverage
and cost figures; the demonstration run's packet sha256, answers and receipt; the grading report and its verdict;
the sealed-path transcript check; known limitations and open issues)*

## 6. Return

Return one verdict, READY or REJECTED. With it:

* list every finding, with severity and whether it blocks;
* answer each §3 negative explicitly;
* answer each §4 attack with the reproduction you built;
* list what you could not verify;
* give your commit SHA on your own branch.

A REJECTED verdict must name the smallest change that would earn READY.
