---
record: SANDBOX-1 (b) B3 probe of route R1 (loopback TCP through the launch sandbox's proxy)
role: research helper for the Wave 2 CTO (scratch evidence record; not committed, DEC-1167 (7))
date: 2026-11-13
decisions: [DEC-1167]
sources: [DEC-1167, DEC-1114, DEC-1035, DEC-158, DEC-1064, DEC-1065, DEC-1099, DEC-1163, W2-56, W3-P28]
cli: claude 2.1.323 (Claude Code), Node 22.23.3
---

# B3: can a sandboxed worker reach a loopback TCP service? (R1)

**Question.** Through the sandbox the launcher builds (`src/gov/launch/sandbox.py`, W2-56), can a process reach a TCP
service on 127.0.0.1 if one loopback entry is added to `allowedDomains`? By which path (proxy or direct)? Is the entry
host-wide or can it be scoped to one port? What does a host-wide entry do to Ollama's API at 127.0.0.1:11434? Does
`gov retrieve`'s semantic route work in the sandbox as built?

**Decision it feeds.** DEC-1167 (7), SANDBOX-1 (b), B3: whether B4 (a port-scoped loopback route for the shared
reranker, W3-P28 brought forward) is justified.

**Stop rule.** Evidence: each of the four items has one measured outcome from a headless `claude -p` run per settings
form (one run per case, no repeats unless a harness fault); no more than about one hour. Reached after about 15
minutes of runs.

## Method

The form of the CTO's earlier probe (`.gov-runtime/scratch/orchestrator/drafts/act-sandbox-cache-1/`): one headless
`claude -p` per settings file, started from a scratch directory, running one small Python script inside the sandbox
through the Bash tool. Differences, all stated:

- Settings: the launcher's block as built (the `settings-A.json` form of the earlier probe: `enabled`,
  `failIfUnavailable`, `allowUnsandboxedCommands:false`, `strictAllowlist:true`, `allowUnixSockets` = the one reranker
  socket, `allowWrite` = the probe's own output folder and `rerank.log`), with only `allowedDomains` changed.
  `GOV_STORE` is set in the settings' `env` (as `gov launch` does for a worker) for the retrieval case.
- Session flags as in `sandbox-exp/run_b.py`: `--setting-sources "" --tools Bash --strict-mcp-config
  --disable-slash-commands --no-session-persistence --permission-prompts none --model haiku --max-budget-usd 0.5`; the
  Bash call is allowed by one exact `permissions.allow` rule per script.
- Targets: two throwaway TCP listeners (`listener.py`) on 127.0.0.1:47311 and :47312, started by me outside the
  sandbox, each answering `B3-OK <port>` after one received line and logging the peer; and Ollama at 127.0.0.1:11434
  with exactly one request, `GET /api/version`.
- The probe (`probe.py`) tries three paths per target: direct `socket.create_connection`; HTTP `CONNECT` through the
  sandbox's proxy (`HTTPS_PROXY`, which carries a per-session credential; the script sends it as
  `Proxy-Authorization`, and the record redacts it); and SOCKS5 (no-auth greeting then CONNECT by name). A "reach" is
  counted only when the round trip returns the listener's reply (or Ollama's version JSON), not on a bare 200.

## Commands run

All from `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/sandbox-b3/` (scripts
copied to `/tmp/claude-1000/b3-probe/`, which holds the settings files, per-run outputs and streams).

```
python3 gen_settings.py                       # writes /tmp/claude-1000/b3-probe/settings-{A,H127,HLH,PS127,PSLH}.json
nohup python3 listener.py /tmp/claude-1000/b3-probe/listener.log 47311 47312 &     # pid 3253553
./run_one.sh <A|H127|HLH|PS127|PSLH> probe.py     # items 1-3, five runs
./run_one.sh A retr.py                            # item 4: gov retrieve (no --root, GOV_STORE set)
python3 -I health.py ; ./run_one.sh <A|H127|HLH|PS127> health.py     # item 4 control and variants: Ollama's health call only
./run_one.sh PS127 alias.py                       # extra: alias spellings against the port-scoped entry
kill 3253553  (by pid), then kill -0 3253553 and ss -ltnp: gone, ports 47311/47312 free
```

`run_one.sh` is, in full: `claude -p --output-format stream-json --verbose --settings settings-<V>.json
--setting-sources "" --tools Bash ... --model haiku` with the one-line prompt "Run exactly this command with the Bash
tool ... python3 -I /tmp/claude-1000/b3-probe/<script>".

## Settings used (only `allowedDomains` differs; the rest is the launcher's block)

| Id | `sandbox.network.allowedDomains` |
|---|---|
| A (as built, control) | `[]` |
| H127 | `["127.0.0.1"]` |
| HLH | `["localhost"]` |
| PS127 | `["127.0.0.1:47311"]` |
| PSLH | `["localhost:47311"]` |

Full files: `data/<id>/settings.json`. Raw outputs: `data/<id>/probe.json` (and `health.json`, `retr.json`,
`alias.json`).

## Measurements

### What the sandbox is (observed, all five runs)

- A sandboxed process has its own network namespace: **every direct** `connect()` to 127.0.0.1 or `localhost`, on my
  listener ports and on 11434, ends `ConnectionRefusedError [Errno 111]` in all five settings, host entries included. It
  is the sandbox's own empty loopback, not the host's.
- The only way out is the proxy in the environment (`HTTP(S)_PROXY`, `ALL_PROXY` = `http://<session credential>@127.0.0.1:3128`;
  `ftp_proxy` = `socks5h://...@localhost:1080`; `NO_PROXY` lists localhost and 127.0.0.1, which only matters to clients
  that read it). Without the credential the proxy answers `407` (first run, before the script sent it).
- The proxy's allow list is the settings' `allowedDomains`. A refusal reads `HTTP/1.1 403 host is not on the allow list`.

### Item 1: a host entry, 127.0.0.1 and localhost (listener ports 47311, 47312)

| Settings | Target | Direct | HTTP CONNECT via proxy | SOCKS5 via proxy |
|---|---|---|---|---|
| A (`[]`) | 127.0.0.1:47311 / :47312 / localhost:47311 / :47312 | refused | 403 not on allow list (4 of 4) | denied (reply `05 02`) (4 of 4) |
| H127 (`127.0.0.1`) | 127.0.0.1:47311 | refused | **200 + `B3-OK 47311`** | denied |
| H127 | 127.0.0.1:47312 | refused | **200 + `B3-OK 47312`** | denied |
| H127 | localhost:47311 / :47312 | refused | 403 (the entry does not cover the name `localhost`) | denied |
| HLH (`localhost`) | localhost:47311 / :47312 | refused | **200 + `B3-OK` on both** | denied |
| HLH | 127.0.0.1:47311 / :47312 | refused | 403 (the entry does not cover the address) | denied |

Answer: **through the sandbox's HTTP proxy (CONNECT), not directly.** A bare entry is host-wide: every port of that
spelling, 47311 and 47312 both. `127.0.0.1` and `localhost` are two separate entries; one does not pass the other.
SOCKS5 was denied in every setting, including the host-wide ones, in my no-auth form (not pursued: HTTP CONNECT works,
and it is what an HTTP client's tunnel uses). The listener log shows each accepted connection from `127.0.0.1`
(the proxy's host-side leg), so a listener cannot tell a sandboxed caller from any other local process by peer address.

### Item 2: an entry scoped to one port

| Settings | Target | HTTP CONNECT via proxy |
|---|---|---|
| PS127 (`127.0.0.1:47311`) | 127.0.0.1:47311 | **200 + `B3-OK 47311`** |
| PS127 | 127.0.0.1:47312 (second listener) | **403 host is not on the allow list** |
| PS127 | localhost:47311 / localhost:47312 | 403 / 403 |
| PSLH (`localhost:47311`) | localhost:47311 | **200 + `B3-OK 47311`** |
| PSLH | localhost:47312, 127.0.0.1:47311, 127.0.0.1:47312 | 403 (3 of 3) |

Answer: **the settings form accepts `host:port`, and the proxy enforces it: port-scoped, not host-wide.** The scoped
entry reached its own port and the other listener on the same host was refused. (CLI 2.1.323; the form is not in the
`sandbox.py` `NETWORK_KEYS` check, which does not look at `allowedDomains` contents.)

Extra, against PS127 (`alias.py`, my own listeners only, `data/PS127/alias.json`): none of 10 alias spellings of the
denied port got through: `127.1:47312`, `127.0.0.1.:47312`, `0x7f.0.0.1:47312`, `2130706433:47312`, `[::1]:47312`,
`127.0.0.2:47312`, `LOCALHOST:47312` (all 403), and `::1:47312`, `127.0.0.1:0`, `127.0.0.1:47312:47311` (400 Bad Request).
Alias spellings of the allowed port did pass (`127.1:47311`, `127.0.0.1.:47311`: 200 + reply), so the proxy normalises the
host, then matches host and port: an alias is no widening.

### Item 3: Ollama at 127.0.0.1:11434 (one `GET /api/version`, nothing else)

| Settings | Via proxy CONNECT to 127.0.0.1:11434 | Via proxy CONNECT to localhost:11434 | Direct |
|---|---|---|---|
| A (as built) | 403 | 403 | refused |
| H127 | **200, `{"version":"0.35.0"}`** | 403 | refused |
| HLH | 403 | **200, `{"version":"0.35.0"}`** | refused |
| PS127 (`127.0.0.1:47311`) | 403 | 403 | refused |
| PSLH | 403 | 403 | refused |

Answer: **reachable with either host-wide form (through the proxy), not with the launcher's block as built and not
with a port-scoped entry for another port.** I sent nothing else to Ollama: no pull, delete, run or embed.

est. (not measured, by the same mechanism: the proxy matches host and port, a bare host entry passes every port): a
host-wide `127.0.0.1` entry also opens the other loopback services that `ss -ltnp` listed at the time: Ollama's second
daemon at 11435 (the query embedder), llama-server, Postgres (0.0.0.0:5432) and Redis (0.0.0.0:6379) if they answer on
127.0.0.1, other sessions' own local servers (Claude's per-session listeners). I did not connect to any of them.

### Item 4: `gov retrieve` in the sandbox as built (settings A, `GOV_STORE` = the integration store link, as a worker)

`retr.py`, one question ("which file builds the launcher sandbox block"), no `--root`; the sandbox lets it write
nowhere but its own folder, so the store was read-only (newest-three mtimes of the integration store and the
main tree's `store.db` and `query-vector-cache.db` unchanged after the run).

```
facets.lexical  : available true
facets.semantic : available false, reason "EMBEDDER_UNAVAILABLE: Ollama is unavailable: semantic retrieval is skipped and results are FTS-only."
merge           : candidates 20, reranked false
evidence        : 18 items; stopping_reason FACET_UNAVAILABLE; exit 0
stderr          : the EMBEDDER_UNAVAILABLE warning (twice)
```

Answer: **it falls back to keywords (FTS-only), unranked.** The semantic route does not work in the sandbox as built.

Why, and what R1 would change (`health.py`: the very call the route makes first, `gov.retrieval.ollama._healthy`,
`GET /api/version` at 127.0.0.1:11434 with `urllib` and `ProxyHandler({})`, i.e. no proxy):

| Run | `_healthy` |
|---|---|
| unsandboxed (control, same code) | true |
| sandbox A, H127, HLH, PS127 | false in all four |

So even with a host-wide entry that lets Ollama's API through the proxy (item 3), the semantic route stays down:
`ollama.py:87` builds its client without a proxy ("the endpoint is local: no proxy"), and a direct connect from the
sandbox is refused (item 1). R1's loopback entry alone does **not** restore the semantic route; it would need a client
that tunnels through the proxy (`HTTPS_PROXY` plus its credential) as well as an entry for 11434 (or 11434 and 11435),
which is the Ollama exposure the owner wants to avoid.

Harness note (not the answer): a first run with `--root <main tree>` returned both facets `stale` (the main tree's
`.gov-runtime/store.db` was last written 2026-11-11 13:38, and the sandbox cannot refresh it), so that run says nothing
about the embedder; the GOV_STORE form above is a worker's real form.

## Sources

- Repository: `.gov-runtime/scratch/orchestrator/drafts/act-sandbox-cache-1/` (probe form and result);
  `.gov-runtime/scratch/orchestrator/drafts/sandbox-package-20261113.md` §6.1 (R1 as proposed) and §1 (DEC lines);
  `src/gov/launch/sandbox.py` (the block as built; `NETWORK_KEYS`, `faults`); `src/gov/retrieval/ollama.py:87,90-96`
  (client without proxy; `_healthy`); `src/gov/retrieval/rerank.py:134-146` (AF_UNIX client);
  `src/gov/launch/store.py` (GOV_STORE); `.gov-runtime/scratch/orchestrator/drafts/sandbox-exp/run_b.py` (session flags).
- No external source was needed; all results are local measurements on claude 2.1.323.

## Verdict

1. **Port-scoped path: yes, it exists on this CLI.** `allowedDomains: ["127.0.0.1:<port>"]` lets a sandboxed process
   reach exactly that loopback port through the sandbox's HTTP proxy (CONNECT with the session credential) and no other
   port, Ollama's 11434 included; alias spellings do not widen it. As built (empty list) nothing loopback is reachable.
2. **A host entry is host-wide** and reaches Ollama's API (and, est., every loopback service); do not use it.
3. **R1 helps the reranker, not the embedder:** `gov retrieve`'s semantic route stays FTS-only in the sandbox because
   its client bypasses the proxy; it is unranked today and stays so under R1 unless the Ollama client is also changed
   and an 11434 (and 11435) entry is added.

## Draft KPI lines

- B3-K1: with `allowedDomains: ["127.0.0.1:<port>"]`, a sandboxed `CONNECT 127.0.0.1:<port>` through the proxy returns
  200 and the listener's reply, and `CONNECT 127.0.0.1:<other port>` returns 403, on claude 2.1.323.
  `verify`: `python3 gen_settings.py; ./run_one.sh PS127 probe.py; ./run_one.sh PS127 alias.py` with a listener on both
  ports; read `data/PS127/probe.json` (`http_connect 127.0.0.1:47311` ok true, `:47312` 403) and `alias.json`.
- B3-K2: with the launcher's block as built, 0 of 18 reach attempts (direct, CONNECT, SOCKS5 to 127.0.0.1 and localhost
  on the two listener ports and 11434) succeed. `verify`: `./run_one.sh A probe.py`; `data/A/probe.json`, every `ok` false.
- B3-K3: a host entry (`127.0.0.1` or `localhost`) reaches Ollama's `GET /api/version` through the proxy; a port-scoped
  entry for another port does not. `verify`: `data/H127/probe.json` and `data/HLH/probe.json` (`OLLAMA http_connect`
  ok true), `data/PS127/probe.json` (403).
- B3-K4: in the sandbox as built, `gov retrieve` (GOV_STORE set) answers with `facets.lexical.available true`,
  `facets.semantic.available false` (`EMBEDDER_UNAVAILABLE`) and `merge.reranked false`; the control call
  `ollama._healthy` is true unsandboxed and false in every sandbox form. `verify`: `./run_one.sh A retr.py`,
  `python3 -I health.py` and `./run_one.sh H127 health.py`.
- B3-K5: re-run K1 to K4 at each CLI re-pin (the proxy's matching is the CLI's, not ours).

## Residuals

- One run per case; the effect is deterministic proxy matching, but no repeat was made.
- The reranker's own protocol was not tested end to end (only a raw line round trip through CONNECT). A real B4 client
  must send CONNECT with the per-session `Proxy-Authorization` taken from `HTTPS_PROXY` (an http.client tunnel does), and
  the service must authenticate by token: the listener sees only the proxy's 127.0.0.1 peer, and any local process can
  reach a TCP port that a Unix socket's file mode would have kept to the user.
- The port in the settings entry is fixed at launch, so the service needs a fixed (or launch-time-known) port; a
  collision breaks the route silently into the unranked fallback.
- A port-scoped entry changes the empty-allowlist rule (DEC-158) for engineer, test designer and auditor, and
  `sandbox.faults` does not check `allowedDomains` contents (W2-56 R4): a check for "one loopback `host:port`, nothing
  else" is part of B4's work.
- SOCKS5 was tested only in the no-auth form; not pursued.
- Not tested: a port-scoped entry for 11434 or 11435 (it would be the Ollama exposure by design), the query embedder
  at 11435, IPv6 loopback listeners, other CLI versions, the research profile's own allowlist.
- The headless `claude -p` runs touched the CLI's own state (`~/.claude.json` and its `backups/`) as any CLI run does;
  `--no-session-persistence` kept the runs' sessions out of `~/.claude/projects`. I wrote nothing there by hand.
- Stopped by pid: the one listener (3253553), confirmed gone, ports 47311 and 47312 free. No other process started that
  outlives the runs. No repository file, service, crontab or commit was changed; `git status` shows only the
  `.tickets/DAEO-cv58.md` change that was there at the start.
