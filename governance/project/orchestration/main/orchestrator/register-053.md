
## 53. Owner answers on W1-18, W1-37 and W1-49 (register v0.53, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04, on the three packages the orchestrator presented (W1-18 DP-1 and DP-2, the CAP-24
version question of W1-37), on W1-49's DP-3, and on the gap the orchestrator reported in DEC-258.

### DEC-260 — W1-18 DP-1: the public interface of the Ollama lifecycle module
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-18 package DP-1 option (a), with both riders · **Under:** DEC-074 Q4, G-22
- **Decision:**
  - One function, `gov.retrieval.ollama.ensure_available(*, timeout_s, env=None)`. It returns `available`,
    `started`, `facet`, `state` and `warning`, and never raises when the daemon is unavailable.
  - The executable comes from `GOV_OLLAMA_BIN`, then `ollama` on `PATH`, then `~/.local/ollama/bin/ollama`.
  - The endpoint comes from `OLLAMA_HOST` (default `127.0.0.1:11434`); healthy means `GET /api/version` answers 200.
  - The default total deadline is 20 s.
  - `src/gov/retrieval/__init__.py` is added to W1-18's `allowed_paths`, in its own commit with the trailer
    `Task: DAEO-1ve2`.

### DEC-261 — W1-18 DP-2: `gov` starts the daemon and never stops it
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-18 package DP-2 option (a) · **Under:** DEC-074 Q4, ADR-0002 §3
- **Decision:**
  - `gov` starts `ollama serve` on demand and never stops it. Ollama's 5-minute idle unload frees the model's GPU
    memory, which was the owner's intent.
  - W1-18 delivers "started by `gov`", not "stopped by `gov`" (ADR-0002 §3). This is an accepted difference,
    recorded in `governance/project/bootstrap.md`. The ADR is not changed.

### DEC-262 — The owner's reading of CAP-24 for vendored skills
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1-37 question left open by DEC-245, option (a) · **Under:** CAP-24, DEC-245, DEC-246
- **Decision:**
  - For a vendored skill, the version recorded beside it (`vendored.yaml`) satisfies CAP-24. The copies stay
    byte-identical to upstream.
  - This is the owner's reading of CAP-24 for vendored skills; the Contract's text is not changed.
  - It is noted in W1-30's brief: `gov close` reads a vendored skill's version from the record beside it.

### DEC-263 — W1-49 DP-3: the SessionStart injection is role-specific
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-49 package DP-3 option (b), role-specific · **Under:** DEC-248, DEC-236, CAP-37.g
- **Decision:**
  - In the main tree, the injection points to the orchestrator prompt and the orchestrator's checkpoint.
  - In a worktree, it says "you are the ticket lead for <ticket>; read appendix A5 of
    governance/project/prompts/w1-orchestrator.md and your checkpoint", plus the lead checkpoint's RESUME HERE
    section.

### DEC-264 — The PreCompact hook never blocks; it appends a generated state block
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the gap reported with DEC-258 · **Amends:** DEC-258 (no compaction is blocked; "current" is no longer a 30-minute age) · **Under:** DEC-248, DEC-250, CAP-37.g
- **Decision:**
  - The PreCompact hook doesn't block a compaction. It appends a generated state block to the checkpoint: the git
    head, the tickets in progress from `tk`, the worktree list and the pending owner decisions.
  - The SessionStart injection warns when the checkpoint's written part is older than that block, and tells the
    session to re-derive state from git and the tickets before acting.
  - This is added to W1-49's KPIs, in its own commit with the trailer `Task: DAEO-32n6`.
  - The tests that assert a blocked manual compaction are revised by a test designer, as rewrites after
    implementation where the implementation exists by then, reason "owner decision, DEC-264".

| Version | Date | Change |
|---|---|---|
| 0.53 | 2026-10-04 | Owner answers: DEC-260 (W1-18 DP-1: `ensure_available`, executable and endpoint lookup, 20 s total deadline, `src/gov/retrieval/__init__.py` in the ticket's paths), DEC-261 (W1-18 DP-2: `gov` starts the daemon and never stops it; accepted difference from ADR-0002 §3), DEC-262 (CAP-24 for vendored skills: the version in `vendored.yaml` is enough), DEC-263 (W1-49 DP-3: role-specific injection), DEC-264 (the PreCompact hook never blocks and appends a generated state block; amends DEC-258). |
