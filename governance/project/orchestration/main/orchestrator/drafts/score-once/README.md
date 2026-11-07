# score-once harness (drafts/score-once)

The CTO's copy of the research harness for D4B-SCORE-ONCE: `rx.py` (the variant switch, the score cache, the
replays), the window scripts and their tests. Run every test with
`bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh bash <this folder>/run_harness_tests.sh`.

## The product's pool on a window-4 clone (E0-DECLARATION §E0b, plan step 2)
Window 4's `retrieve` reads `governance/project/retrieval.yaml`'s `pool:` (W2-32 S11, the product's own v456). A
variant of the harness's own (v456's keys) applies the same fusion, depth rerank, cap and dedup itself, so:

- **rx.py refuses a variant of its own on a clone whose pool is on.**
- **E0b turns the product's pool off with `GOV_RX_POOL_OFF=1`** in the environment of every harness run (it passes
  through `so_measure.sh`): retrieve then gets every pool key 0 or false, in that process only. The clone, its
  `retrieval.yaml` and its store stay as they are, so E0b uses E0's own clone (`~/gov-os-runs/D4B/w4-e0/repo`).
- `GOV_RX='{}'` (the shipped path) keeps the clone's pool, as the product runs it.

The other E0b switches (`GOV_RX_LIVE_MISSING`, `GOV_RX_LEGACY_STORE`) and the exact E0b commands are in
`E0B-READINESS.md`.

## E4 (E3-E5-DESIGN §1): M3 and M1 on window 4
- `e4_prep.sh` (no GPU): the gte and zerank seeds, their window caches (`e4_prepare.py routes`: seed plus E0b's route
  answers), and the count of the texts each model lacks (`e4_count.py`, a strict replay of E0b's run B).
- `e4_window.sh` (the one GPU window, `DRY=1` first): gte, then zerank, score what they lack, one trial service at a
  time, with the live service stopped and restored by the trap.
- `e4_replays.sh` (no GPU): M3 and M1, strict.
- rx.py, so_measure.sh and seed_scores.py are unchanged. The commands, the GPU plan and the risks are in
  `E4-READINESS.md`. Tests: `test_e4.py`.
