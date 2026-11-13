# ACT-OLLAMA-CAP-1 — cap the shared embedding server's CPU (DEC-1010 item 7 (c))

## What was found (2026-11-01, about 20:40)
- Two `ollama serve` processes run, both started outside any session (parent `init`):
  - pid 422673, since 17 Oct, port 11434, the **shared** server that builds every index. Its `llama-server` runs with
    `-np 1` (one request at a time) and **no thread limit: 49 threads** on this 10-core, 20-thread machine.
  - pid 1798039, since 20 Oct, port 11435, `CUDA_VISIBLE_DEVICES=-1`: the CPU-only query embedder (DEC-798). Small; left
    alone.
- **The Gov OS starts the shared server itself** when it is down (`src/gov/retrieval/ollama.py`, `ensure_available`),
  with no cap. So a cap set by hand lasts until the server is next restarted.
- **What it costs:** history (7 days): the embedding kind uses **8.3 cores at p95, 16.2 at most**; at 20:41 it held
  5.5 of the 8.5 really busy cores. It cannot take a heavy-job slot (one shared server, called by every rebuild and
  retrieval), so it runs outside the slots, and today it was one of the causes of the load near 60 to 99.

## The cap (recommended): 8 logical CPUs at a lower priority, by a restart in a quiet minute
`taskset` and `nice` are inherited by the `llama-server` children, so the whole server then uses at most 8 of the 20
logical CPUs, and yields to test runs when the machine is full. It needs no install and no Ollama setting.
```
# 1. a quiet minute: nothing printed here (no rebuild, slot rebuild or memory measure running)
pgrep -fa 'gov.cli.main rebuild|rebuild_slot.sh|gov.retrieval.measure'
# 2. the shared server's pid, from the port, and its command line (it must read `.../ollama serve`)
PID=$(ss -ltnp | grep ':11434 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); echo "pid $PID"
tr '\0' ' ' < /proc/$PID/cmdline; echo
OLD_RUNNERS=$(pgrep -P $PID llama-server); echo "its runner(s): $OLD_RUNNERS"
# 3. stop it, wait until the port is free, start it capped, detached
kill $PID
for i in $(seq 1 40); do ss -ltn | grep -q ':11434 ' || break; sleep 0.5; done
setsid -f nice -n 10 taskset -c 12-19 /home/usain/.local/ollama/bin/ollama serve > /home/usain/.ollama/serve-11434.log 2>&1 < /dev/null
sleep 3
# 4. if the Gov OS started an uncapped server in the gap (the log says the address is in use, or the server on
#    11434 has the affinity 0-19), stop that one and repeat step 3 once
NEW=$(ss -ltnp | grep ':11434 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); taskset -cp $NEW
grep -i 'address already in use' /home/usain/.ollama/serve-11434.log && echo "RETRY: kill $NEW and repeat step 3"
# 5. check: it answers; one embedding loads its runner; the server and that runner both read 12-19
curl -s http://127.0.0.1:11434/api/version; echo
curl -s http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"cap check"}' > /dev/null
for p in $NEW $(pgrep -P $NEW llama-server); do taskset -cp $p; done
# 6. the old runner is gone: llama-server shows only the 11435 server's runner (parent pid 1798039) and the new one
for r in $OLD_RUNNERS; do [ -d /proc/$r ] && echo "OLD RUNNER $r STILL ALIVE: kill $r"; done
pgrep -fa llama-server | while read p rest; do echo "$p parent $(ps -o ppid= -p $p)"; done
```
**Risk:** a rebuild or retrieval that calls the server during the restart fails (fails closed: the lead re-runs it),
so do it in a quiet minute. Embedding-heavy work (a cold rebuild's semantic stage) runs slower on 8 CPUs than on all 20
when the machine is otherwise idle (today's measured 11.5 minutes on a quiet machine may become about 20); on a full
machine, as today, it changes little and the rest runs faster. **Undo:** `kill` it and start plain `ollama serve`.

## The durable fix (a KPI change proposal, DEC-1003): W2-20 (the resource gate)
`'The Gov OS starts its shared embedding server with a CPU cap from the gate''s configuration file (logical CPUs and a
lower priority, inherited by its runner processes), so a restart keeps the cap; the gate counts the server''s CPU p95
above what it uses now when it admits a session; a planted start shows the cap applied [DEC-1010 item 7, DEC-1003]'`,
with `src/gov/retrieval/ollama.py` added to W2-20's paths.
