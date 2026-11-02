You are the ticket lead for ticket `DAEO-jpr0` (`W2-126`, "A machine-wide vector cache keyed by the text"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-126` on branch `w2/W2-126`.

**This is run 1: the independent tests only.** `git rev-parse --short=12 HEAD` must show `2a3c998fe786`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim):** sources resolve (DEC-1032, DEC-1031, DEC-1015, DEC-374); paths, KPIs, profile and acceptance path set; one role (engineer). Its engineer waits for W2-123 (which holds `src/gov/retrieval/semantic.py` for the bounded retry, DEC-1026), so this run builds the acceptance tests only.

## Why (the owner's DEC-1032: the infrastructure sprint)
About 503,000 texts went through the shared embedder in 13 hours on 2026-11-01/02, nine full copies of the corpus (`governance/project/orchestration/packages/P1-LOAD-BALANCE-1.md`, section a). A chunk's vector depends only on the model, its revision and the text sent; one cache keyed by them, shared on the machine, makes every text embedded once.

## The decisions for this run
- **The test designer only:** one fresh independent test designer (sandboxed through `gov launch independent-test-designer DAEO-jpr0`, effort high) in `~/gov-os-worktrees/W2-126-tests` (branch `w2/W2-126-tests`), retrieving only from the integration store, writes `tests/acceptance/W2-126/` from the KPIs: planted texts and a stand-in embedder endpoint that counts what it is sent (never the real servers 11434/11435), a temporary cache folder (never the user's real one), concurrent writers, the size bound and eviction, the model or revision change, a rebuild of an all-cached tree that sends nothing and gives the same store byte for byte. The engineer's public interface is not built yet: the designer states the interface the cases need (the cache's location setting, the result's naming of hits and misses) in the README, as earlier tickets did, and the CTO hands it to the engineer.
- **Red first:** the cases fail on today's code for the reason the README states.
- Merge the tests into this branch (`--no-ff`; a test designer's merge carries `Role: independent-test-designer`, DEC-1031 item 3), remove the tests worktree, and return **DONE (tests ready)** with the head and the interface the README states. No engineer in this run.

**Estimate:** about 300 lines of tests; 2 hours. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-126`.
