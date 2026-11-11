# E0 and E0b, declared before any run (SEVEN-ANSWERS §7; DEC-1087 (11), DEC-1090 (1))

The CTO, 2026-11-07, session `ad44f5fe`. This record is committed before E0 starts.

## E0: the 138 through the live product on window 4's pin
- **What it measures:** what ships.
  - The pinned gov (`~/.local/bin/gov` → `pin-bcea09060ebc`), with the pool switched on.
  - The live shared servers: the two embedders and the 0.6B reranker service.
  - The 138: visible 40, hidden 39 (h24 apart), spent 59 (m60 apart), all from `~/gov-os-eval`.
- **Where:**
  - A measure clone at `~/gov-os-runs/D4B/w4-e0/repo`, at `c00d525fd420`. This is window 4's commit with the pool on, the first commit that ships what the pin runs.
  - Its store is built by the pinned gov, seeded from the integration store.
  - The measure runs on the pin's own python (`python -m gov.retrieval.measure`).
- **The script:** `.gov-runtime/scratch/orchestrator/drafts/d4b/e0_run.sh`.
  - One GPU job, in its own process group, with the GPU backstop armed.
  - Heavy steps go through `heavy_slot.sh`; the store rebuild takes the D-4b rebuild lock.
- **Gold:** re-anchored in memory per commit by the measure itself (W2-134), with a reason line for each re-anchor. Nothing writes the sets root. Before the run, the sets root's visible q12 was synced to integrate's approved label (`c48d7ce8`, 11-05; the only visible file that differed). The old copy is kept in `~/gov-os-runs/PAT-1/q12-sets-root-before-e0.yaml`.
- **Figures** (`drafts/d4b/e0_figures.py`; counts only, the hidden set as figures, never as text):
  - per set and for the 138: hit@5, hit@10 and hit@20 (from the first gold rank in the first call's ranked items);
  - MRR of the first gold source;
  - in the bundle (the measure's flag: a gold piece in an item of the first call);
  - full evidence;
  - the spread of hit@5 between the three sets;
  - the median call time;
  - unresolved anchors counted.
- **Compared with:** S11's check of 11-06 (`~/gov-os-runs/D4B/w4-32-product`: 108/138, MRR 0.5669, with the clone's code at S11's merge and the pool on). The per-question differences are given (`score138.py --same`). This is a check that the pin equals the code it was built from, not a choice.
- **What E0 decides:** nothing on its own. It is the baseline for E1 to E5 and for G3's decision (DEC-1090 (4)). The hidden half never chooses (DEC-1067).
- **Every search's ranked output is kept** in `~/gov-os-eval/runs/w4-e0/` (DEC-1069).

## E0b: the same 138 through the harness (B0's form), deferred
**Status: blocked as planned.** The score-once harness (`drafts/score-once/rx.py`) cannot run on window 4's code, for three reasons:
- its search overrides don't take the `depth` and `top_k` arguments window 4 passes;
- its cache's stored search answers are keyed without the store's root or commit, so on a new clone they would silently reuse g1's;
- in replay mode, a text with no kept score stops the run.

**Plan:**
1. Fix `rx.py`, with its tests and one review.
2. Turn the product's pool off in the harness clone, since the harness applies v456 itself.
3. Seed the cache from the kept q06 scores, with the stored search answers dropped.
4. Score the new texts on the live 0.6B, as a light GPU job with the backstop.
5. Run it twice: without L3's normalised lift (the fair test of "the harness within 2 of the product", W2-32 S11), and with it (B0's form, for E4's M3 bundles).

E0b is needed only for E4 (M3's bundles come from the harness). **E1 and E2 do not wait for it.**

**Basis:** question 1 (the experiments measure the product as it ships, declared before the figures are seen).
