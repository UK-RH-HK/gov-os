# ACT-QUERY-GPU-2: the query embedder on the GPU, right after the emergency re-pin (DEC-1033 fix (b), DEC-1037)

**It replaces ACT-QUERY-GPU-1, which must never be applied.** Apply it **right after window 1's re-pin
(`REPIN-COMMANDS-<C>.sh` printed `RE-PIN DONE`), in the same window, once no process of the old pin
(`pin-5c401220`) runs**: the old pin drops a question's vector unless the query server is wholly on the CPU, so a
search on the old pin after this ACT would lose its semantic facet. For the owner's operator, in a plain terminal; no
repository commit. (Revision 2, 2026-11-02 ~16:15: step 0 checks the pin and waits for the old one to drain; the
start goes through the interim wrapper `~/.local/bin/ollama`, set to the GPU, so a restart by anything else in the
gap also comes back on the GPU with its caps and log; the 15:29 incident of ACT-QUERY-CPUS-1 cannot recur.)

## Step 0: the conditions (each line must print its `ok`)
```
P=$HOME/.local/share/gov-os
readlink -f ~/.local/bin/gov | grep -q 'pin-5c401220' && echo "STOP: gov is still the old pin" || echo "ok: gov is $(readlink -f ~/.local/bin/gov)"
S=$(dirname "$(readlink -f ~/.local/bin/gov)")/../lib/python3.12/site-packages/gov/retrieval/semantic.py
grep -q -E 'NOT_ON_CPU|_on_cpu' "$S" && echo "STOP: the pin still has the CPU-only gate" || echo "ok: the pin accepts a vector from any device"
timeout 300 sh -c 'while pgrep -f pin-5c401220 >/dev/null; do sleep 2; done' && echo "ok: no process of the old pin" || { echo "STOP: old-pin processes after 5 minutes:"; pgrep -af pin-5c401220; }
head -12 ~/.local/bin/ollama | grep -q 'query-server-device' && echo "ok: the wrapper is in place" || echo "STOP: ~/.local/bin/ollama is not the wrapper"
```
Any `STOP`: do not go on; tell the CTO (the re-pin stays; the query server stays on the CPU).

## The commands
```
# 1. the query server's pid, from its port, and its command line (must read .../ollama serve)
Q=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); echo "query server pid $Q"; tr '\0' ' ' < /proc/$Q/cmdline; echo
# 2. room on the GPU (at least 4096 MiB free), else stop here
FREE=$(/usr/lib/wsl/lib/nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits); echo "free MiB $FREE"; [ "$FREE" -ge 4096 ] && echo ok || echo "STOP: not enough GPU memory"
# 3. the wrapper set to the GPU; stop the server (its runner ends with it) and start it again through the wrapper
#    (CPUs 8-11, nice 0, the GPU visible, the same log; the start is recorded in ~/.ollama/query-autostart.log)
echo gpu > ~/.ollama/query-server-device
kill $Q; sleep 3
ss -ltn | grep -q ':11435 ' && echo "(something restarted it in the gap: through the wrapper, so on the GPU; see query-autostart.log)" \
  || OLLAMA_HOST=127.0.0.1:11435 setsid -f ~/.local/bin/ollama serve < /dev/null
sleep 5
# 4. load and pin its model on the GPU
curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
# 5. the check
grep -E 'offloaded [0-9]+/[0-9]+ layers' ~/.ollama/serve-11435.log | tail -1
curl -s -m 5 http://127.0.0.1:11435/api/ps | grep -o -E '"size":[0-9]+|"size_vram":[0-9]+'
N=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); taskset -cp $N; tr '\0' '\n' < /proc/$N/environ | grep -c '^CUDA_VISIBLE_DEVICES=-1$'
for i in 1 2 3; do curl -s -m 120 -o /dev/null -w "%{time_total}s " http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":["what decides a close","the guard rules"]}'; done; echo
```
- Step 5 must show `offloaded 29/29 layers to GPU`; `size_vram` equal (or close) to `size`; affinity `8-11`; `0` (the
  GPU not hidden); and the three question times (today 13.7 s on the CPU; expected under 0.5 s).
- Questions in flight during the restart fail once; anything that restarts the server goes through the wrapper.

## Undo (also before any rollback of the re-pin: the old pin refuses GPU vectors)
```
echo cpu > ~/.ollama/query-server-device
Q=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); kill $Q; sleep 3
ss -ltn | grep -q ':11435 ' || OLLAMA_HOST=127.0.0.1:11435 setsid -f ~/.local/bin/ollama serve < /dev/null
sleep 5; curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
```

## After it (the CTO)
- The dispatcher's `gpu_expected` for the query server set to true (`dispatch/config.json`), so a 0-layer or partial
  load there alerts; a question's time measured for the after figures.
- Sessions on old code: leads' worktrees run their own `src/`; a tree from before `6ed6a5ae` drops GPU vectors in its
  own tests' searches: under the freeze only W2-112's lead runs (its tree has the fix). Each lead merges
  `w2/integrate` before its next search-heavy step.
- The wrapper stays (in its GPU setting) until the product's automatic start carries the caps (a KPI line for W2-20 /
  W2-121, DEC-1037 (4)); its removal is then a small ACT of its own.
