
## Ollama: started by `gov`, not stopped by `gov` (DEC-261, 2026-10-04)

ADR-0002 §3 says the Ollama daemon is "started and stopped by `gov`". W1-18 (`DAEO-1ve2`) delivers the first half
only: `gov` starts `ollama serve` on demand and never stops it. Ollama's 5-minute idle unload frees the model's GPU
memory, which was the owner's intent; the `serve` process itself stays. The owner accepted this difference (DEC-261).
The ADR is not changed.
