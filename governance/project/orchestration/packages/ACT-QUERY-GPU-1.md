**SUPERSEDED by ACT-QUERY-GPU-2 (DEC-1033): never apply this one; with the old code every new search would lose its semantic facet.**

# ACT-QUERY-GPU-1: the query embedder on the GPU (DEC-1032, the sprint's step 2; DEC-798 and DEC-975 amended)

For the owner's operator, in a plain terminal (it restarts the query embedding server at 127.0.0.1:11435, which runs
outside any session; the repository is not touched, so no commit).

## Why
The query server runs on the CPU by DEC-798 (`CUDA_VISIBLE_DEVICES=-1`), on the same 8 CPUs (12-19) as the shared
server. Today a single question waited 19 to 53 s (median) and up to 120 s; 342 of 2,213 requests failed overnight.
The determinism test (DEC-1031 item 1, the standing memory measure, visible half, the same store) changed no
answer's pass or fail on the GPU (GPU hit@5 11/20, CPU 10/20, the one difference also varying run to run on the CPU
itself; the first-call top 5 identical in 18 of 20). DEC-1032 amended DEC-798 and DEC-975 accordingly.

## The GPU budget, checked
Now: 7.4 of 15.9 GB used (the shared embedder, pinned, about 2.4 GB; three rerankers from before the slot limit,
which leave as their sessions end; at most two from now on). The query model adds about 2.5 GB, and both embedders
together stay within the embedder's first share. The commands refuse to start it with less than 4 GiB free.

## The commands
```
# 1. the query server's pid, from its port, and its command line (must read .../ollama serve)
Q=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); echo "query server pid $Q"; tr '\0' ' ' < /proc/$Q/cmdline; echo
# 2. room on the GPU (at least 4096 MiB free), else stop here
FREE=$(/usr/lib/wsl/lib/nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits); echo "free MiB $FREE"; [ "$FREE" -ge 4096 ] || echo "STOP: not enough GPU memory"
# 3. stop it (its runner ends with it) and start it again with the GPU visible, same caps and log
kill $Q; sleep 3
OLLAMA_HOST=127.0.0.1:11435 setsid -f nice -n 10 taskset -c 12-19 /home/usain/.local/ollama/bin/ollama serve >> /home/usain/.ollama/serve-11435.log 2>&1 < /dev/null
sleep 5
# 4. load and pin its model on the GPU
curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
# 5. the check
grep -E 'offloaded [0-9]+/[0-9]+ layers' /home/usain/.ollama/serve-11435.log | tail -1
curl -s -m 5 http://127.0.0.1:11435/api/ps
```
- Step 5's first line must read `offloaded 29/29 layers to GPU`; `/api/ps` must show `size_vram` close to `size`.
- Questions in flight during the 10 seconds of the restart fail once; their callers start the server again if it is
  down. **That automatic start (`ensure_query_available` in `src/gov/retrieval/ollama.py`) still hides the GPU**
  (`NO_GPU`): if the server dies before the code follows (a KPI line the CTO adds to W2-123, which owns that file),
  it comes back on the CPU; the dispatcher's GPU watch then alerts (the CTO switches the watch to expect the GPU on
  the query server once this is applied).

## After it
The CTO sets the dispatcher's `gpu_expected` for the query server to true (so a 0-layer or partial load there
alerts) and measures a question's latency (target: under 1 s at p95, in the morning log scan).

## Undo
The same, with `CUDA_VISIBLE_DEVICES=-1` before `setsid` in step 3.
