# BR-HO-0001-A1: addendum to the architect brief (owner clarification OC-BR-02)

**Read this after BR-HO-0001. Where the two differ, this addendum governs.** Its source is
`GATES/OWNER-CLARIFICATION-BR-0002-CORPUS-AND-PURPOSE.md`, which you must read verbatim.

## Replaces BR-HO-0001 §1's last sentence and §2.2 item 1

You are designing a **generic, provider/model-replaceable, whole-repository Governance OS self-memory/context
foundation**. You may optimise implementation effort because this is a temporary bridge. You may **not** create a
bespoke Phase-2 or Review-8 retrieval mechanism. The test for this: **if you deleted every Review-8 reference from
your design, would anything in the architecture change?** Only the demonstration and the oracle should change.

**Corpus.** The corpus is the whole canonical Governance OS repository. Define the rules and justify each one:

* **inclusion/exclusion rules**, as a deterministic, versioned rule file:
  * secrets: `*.env`, `.secrets/`, `deepseek*.env`, key material, and anything the repo `.gitignore` names as
    credentials;
  * generated, binary and build artefacts: `target/`, `.claude/worktrees/`, `__pycache__`, and binaries or
    payloads;
  * anything policy marks non-indexable. **Check `framework/policies/{MEMORY,CONTEXT,ARCHIVE}_POLICY.yaml` and any
    other policy** for such markings, and cite them;
* **the canonical ref model**: what "the canonical repository" means *at a ref*. Today the records are at the bridge
  base, the frozen product is at `3c880d8`, and history lives on `phase2/*` branches. Say how the index represents
  more than one ref, or a sequence of refs, without duplicating or confusing them, and how "current" is decided per
  ref.

## Covered areas, as applicable

- contract/constitution/policies
- owner decisions and active/superseded architecture
- specifications/requirements
- source code
- tests and evidence
- research/reports
- lessons and failed approaches
- migrations
- capabilities/plugins/tools
- orchestration/checkpoint/handoff history
- dependency/impact relationships
- temporal current-vs-superseded lineage

## The architecture must now define each of these explicitly, one heading each in `ARCHITECTURE.md`

1. corpus inclusion/exclusion rules
2. document/chunk/record identity and provenance
3. incremental freshness/invalidation
4. the structured, exact, lexical, semantic, graph and code routes
5. current-vs-superseded and authority filtering
6. whole-repository dependency/WHY lineage
7. bounded context compilation
8. deterministic rebuildability
9. replaceable embedding/index/runtime interfaces
10. **promotion/reconciliation into full V8.3**. Explain how this bridge becomes implementation/evidence input to
    V8.3 (OD-P2-10 §9) instead of throwaway tooling:
    * which interfaces are stable contracts;
    * which parts are provisional;
    * what a Phase-3 qualification (OD-P2-10 §10) would measure against;
    * how it moves out of `release/orchestration/phase-2-context-bridge/` without a redesign.

## Unchanged

* Review 8 remains the **first mandatory demonstration**, and the oracle/grading design in §2.3 stands. It is a
  benchmark on a difficult known case, **not a design driver**.
* OD-P2-10A/B and the `mandatory_bridge_inputs` authority classes.
* The hard authority invariant, all prohibitions, and your mutation scope. You still **write** only
  `ARCHITECTURE/**` and `AGENT_RUNS/BR-AR-0001.*`, while reading the whole repository.

## Add to your return

In `ARCHITECTURE/REUSE_VS_BUILD.yaml` and the DAG, show that the whole-repository corpus is indexed, not a Review-8
subset. The DAG must include a node that measures corpus coverage: files included, files excluded by rule, and
unclassified files. Report the corpus size and index cost you measured or estimated for the whole repository in your
report's `claims`.
