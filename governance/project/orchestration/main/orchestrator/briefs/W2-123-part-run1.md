# W2-123 (DAEO-qzrq), run 1 — parallel requests on the embedding server (STANDARD, engineer), at the front (DEC-1014)

**Why it matters:** the shared embedding server (ollama on 127.0.0.1:11434, started by `src/gov/retrieval/ollama.py`'s
`ensure_available` when it is down) answers one request at a time (`llama-server -np 1`), so every rebuild and retrieval
check queues behind it; the owner capped it at 8 cores (ACT-OLLAMA-CAP-1: `taskset -c 12-19`, `nice 10`). This ticket
lets it serve several requests at once, proves the vectors do not change, and measures that the 8-core cap does not
become the new limit.

**Do:** the parallel work order (DEC-959 item 7, DEC-963): a fresh independent test designer in a tests worktree, a fresh
engineer here, at once. The measure (KPI 3) must not disturb the live shared server that every lead uses: run your own
server instance on another port for the measurement (the same binary `/home/usain/.local/ollama/bin/ollama`, the same
model `qwen3-embedding:0.6b`), never restart the shared one; record the figures in `docs/changes/W2-123-evidence.md`.
Every heavy step through a slot (the common brief). Your scoped run once; the merge queue lands it. Return DONE with
the exact head, the chosen settings and their figures. Scratch budget: 20 GB and 1,000,000 files (DEC-898).
