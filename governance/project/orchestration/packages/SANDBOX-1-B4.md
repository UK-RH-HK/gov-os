# SANDBOX-1 B4: ranked search for sandboxed workers by one port-scoped loopback entry (owner's item; short form)

**The question.** B3's probe found a port-scoped route (your condition for B4, DEC-1167 (7)). Do we build it? It needs
a new ticket (yours, DEC-974) and your amendment of DEC-158 (workers' empty network allowlist) and DEC-1114 S9.

**What B3 measured** (claude 2.1.323; `.gov-runtime/scratch/orchestrator/drafts/sandbox-b3/probe-results.md`, raw data
in `data/`):
- **As built (empty list):** 0 of 18 reach attempts. Direct connects are refused (the sandbox has its own empty
  loopback), and the proxy answers 403 "not on the allow list".
- **`127.0.0.1:47311`:** that port is reached through the proxy's CONNECT, round trip confirmed; another port gets 403.
  Six alias spellings (`127.1`, a trailing dot, hex, decimal, `[::1]`, `127.0.0.2`) do not widen it.
- **A bare `127.0.0.1` or `localhost` entry:** host-wide. Both listeners are reached, and so is Ollama's
  `/api/version` (version 0.35.0). Never use it.
- **`gov retrieve` in the sandbox as built:** lexical yes, semantic `EMBEDDER_UNAVAILABLE`, `reranked` false. R1 does
  not change the semantic route, because `ollama.py:87` builds its client with `ProxyHandler({})`.

**What B4 would be** (one FULL ticket, about 1 to 2 days with its review):
- The shared reranker service also listens on a fixed `127.0.0.1:<port>`, with a token file; the client connects through
  the sandbox's proxy when its Unix socket is refused.
- One `127.0.0.1:<port>` entry in the worker sandbox's `allowedDomains`.
- A `sandbox.faults` check that allows exactly that one entry and nothing else (today it does not check
  `allowedDomains` at all: W2-56 R4).
- Revisions of W2-56 S8 to S10 and F4, and of W2-112's and W2-145's cases.

**Gains:** workers' searches ranked again. On the 138 questions, hit@5 rises from 95 to 107, and end to end about +10
to 13 answers. The 336-a-day unranked searches of 11-13 end.

**Costs and risks:**
- The token is the only authentication: any local process can reach a TCP port, unlike a Unix socket's file mode.
- A fixed port that collides falls back to unranked search, named.
- The proxy's host:port matching is the CLI's own, so it is re-checked at each CLI re-pin.
- It changes DEC-158's empty allowlist for workers, to one loopback port.
- Semantic search for sandboxed workers still needs a separate change (a proxy-aware Ollama client and an entry for its
  port). It is not in this ticket.

**The options.**
- **(a) File B4 now and build it after EXAMIN's copy starts** (1 to 2 days, off the critical path). It comes with your
  amendment of DEC-158 and DEC-1114 S9, for one loopback `host:port` for the reranker only.
- **(b) Stay on R4,** workers' search through their lead (B1). No amendment. Workers' own searches stay unranked.
- **(c) As (a), and also file the semantic route's client change.** About half a day more, and a second loopback entry
  (Ollama's API port, which can pull and delete models, so its own risk).

**Recommendation: (a).** Confidence: medium. R4 covers the ranked search a worker needs now. B4 is worth having for
workers' own ad hoc searches, but it is not needed for the copy. Keep (c) parked: opening Ollama's port to sandboxed
workers is a larger step.

Your line: `B4 (a)` (or `(b)`, `(c)`).
