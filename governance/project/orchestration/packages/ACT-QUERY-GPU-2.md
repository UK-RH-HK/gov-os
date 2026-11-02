# ACT-QUERY-GPU-2: the query embedder on the GPU, after the emergency patch (DEC-1033, fix b)

**It replaces ACT-QUERY-GPU-1, which must never be applied** (with the old code, `semantic.py` drops a question's
vector unless the query server is wholly on the CPU: every new search would lose its semantic facet). Apply this one
**only after the CTO says the patch is live** (branch `emg/query`, `75f18d1118c7`, merged into `w2/integrate` after its
independent review): the patch accepts a question's vector from any device (DEC-1033 replaces DEC-798) and makes the
code's own automatic start keep the GPU visible. For the owner's operator, in a plain terminal; no repository commit.

## Step 0: the patch is live (the command must print `patch live`)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git merge-base --is-ancestor 75f18d1118c7 w2/integrate && ! git show w2/integrate:src/gov/retrieval/semantic.py | grep -q NOT_ON_CPU && echo "patch live" || echo "STOP: the patch is not on w2/integrate"
```

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
Leads' worktrees run their own `src/` until they merge `w2/integrate`; the CTO tells each running lead to merge it
before its next search-heavy step.

## After it (the CTO)
The CTO sets the dispatcher's `gpu_expected` for the query server to true (so a 0-layer or partial load there
alerts) and measures a question's latency (target: under 1 s at p95, in the morning log scan).

## Undo
The same, with `CUDA_VISIBLE_DEVICES=-1` before `setsid` in step 3.
