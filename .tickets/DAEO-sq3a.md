---
id: DAEO-sq3a
wbs_id: W2-186
external-ref: W2-186
title: "Sandboxed workers' searches ranked again: the shared reranker on one port-scoped loopback entry with a token (SANDBOX-1 B4)"
type: task
class: implementation
role: engineer
profile: FULL
status: open
state_class: AUTHORITATIVE
priority: 2
created: 2026-11-13
deps: []
allowed_paths:
- src/gov/retrieval/rerank.py
- src/gov/retrieval/rerank_service.py
- src/gov/launch/sandbox.py
- tests/unit/retrieval/test_w2_186_*.py
- tests/unit/launch/test_w2_186_*.py
- docs/changes/W2-186-evidence.md
- docs/probes/DAEO-sq3a/**  # the probe record
reads:
- governance/project/orchestration/packages/SANDBOX-1-B4.md
- .gov-runtime/scratch/orchestrator/drafts/sandbox-b3/probe-results.md
- .gov-runtime/scratch/orchestrator/drafts/sandbox-package-20261113.md
- tests/acceptance/W2-56/**
- tests/acceptance/W2-112/**
- tests/acceptance/W2-145/**
needs: []
waits_on: []
kpis:
  success:
  - 'S1: the shared reranker service also listens on a fixed `127.0.0.1:<port>` (one setting), answering only a request that carries the token from its token file (0600, beside its socket); the Unix socket stays the first route [DEC-1168 (1), DEC-1167 (7) B4] Verify: a planted service answers a request with the token and refuses one without it or with a wrong one; a request over the socket works as today'
  - 'S2: when its Unix socket is refused (EPERM, a sandbox), the client reaches the service through the sandbox''s proxy (`HTTPS_PROXY` CONNECT) to that one port with the token, and the search is ranked; a refusal of that route too leaves the search unranked and named, never a private reranker (W2-145 S1) [DEC-1168 (1)] Verify: a stand-in proxy and service: a socket-refused client is ranked through the proxy; a proxy refusing the port leaves the order given and names the cause'
  - 'S3: the worker sandbox''s network settings hold exactly one `allowedDomains` entry, `127.0.0.1:<port>`, and `sandbox.faults` refuses any other entry, a bare host (`127.0.0.1`, `localhost`) and any port but the service''s [DEC-1168 (1), DEC-158 as amended, W2-56 R4] Verify: the launcher''s block carries that one entry; planted blocks with a bare host, another port or a second entry are each refused by `sandbox.faults`'
  failure:
  - 'F1: a sandboxed session reaches another loopback service (Ollama''s 11434 or 11435, llama-server) or any non-loopback host. Verify: in a launched sandbox (B3''s probe form), a connect to a listener on another port and to 11434 is refused (403 or refused), and the service''s port is reached'
non_goals:
- 'not semantic search inside the sandbox (a proxy-aware Ollama client and its port: parked, DEC-1168 (1))'
- 'not a gate for EXAMIN''s copy: built after W2-27 starts (DEC-1168 (1))'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1168, DEC-1167, DEC-158, DEC-1114, DEC-1128]
acceptance_tests: {path: tests/acceptance/W2-186/}
---

# W2-186 Sandboxed workers' searches ranked again (SANDBOX-1 B4)

The owner's SANDBOX-1-B4 (a) (DEC-1168 (1)), on B3's evidence (`.gov-runtime/scratch/orchestrator/drafts/sandbox-b3/`):
an `allowedDomains` entry `127.0.0.1:<port>` reaches only that port through the sandbox's proxy (six alias spellings
did not widen it), while a bare host entry opens every loopback port, Ollama's API included. Built after EXAMIN's copy
starts. The owner amends DEC-158 (workers' empty network allowlist) and DEC-1114 S9 for this one entry. W2-56's S8-S10
and F4, and W2-112's and W2-145's cases, are revised by a test designer under this ticket. Re-check the proxy's matching
at each CLI re-pin.
