# ACT-QUERY-CPUS-1: the query embedder on CPUs of its own, still on the CPU (DEC-1033 interim, until the re-pin)

For the owner's operator, in a plain terminal (it restarts the query embedding server at 127.0.0.1:11435; no
repository commit). It changes only where and how the query server runs on the CPU: the GPU stays hidden from it,
because the pinned gov (pin-5c401220) still uses a question's vector only when the model is wholly on the CPU
(`_on_cpu`); the GPU move waits for the re-pin (ACT-QUERY-GPU-2).

## Why
The query server runs with affinity 12-19 at nice 10, the same 8 CPUs as the shared embedding server, whose rebuild
batches it waits behind. Measured at 14:16 (load 17): a two-text question took 8.8, 8.7 and 10.1 s; 09:00-13:00 its
median was 15 s and p95 53 s (the servers' logs). The shared embedder now runs on the GPU and uses about 5 of its 8
CPUs; the query server needs about 2 to 4 CPUs for a two-text question (estimated well under 1 s on idle CPUs).

## The change
The query server moves to CPUs 8-11 (four of its own, away from the shared server's 12-19) at nice 0 (the normal
priority, like the leads' processes, instead of 10), still with `CUDA_VISIBLE_DEVICES=-1`. (No CPU can be reserved for
it alone without root; it competes fairly on those four instead of queuing behind rebuild batches.)

## The commands
```
# 1. the query server's pid, from its port, and its command line (must read .../ollama serve)
Q=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); echo "query server pid $Q"; tr '\0' ' ' < /proc/$Q/cmdline; echo
# 2. a question's time before (three tries)
for i in 1 2 3; do curl -s -m 120 -o /dev/null -w "%{time_total}s " http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":["what decides a close","the guard rules"]}'; done; echo
# 3. stop it (its runner ends with it) and start it again on CPUs 8-11 at nice 0, the GPU hidden, the same log
kill $Q; sleep 3
CUDA_VISIBLE_DEVICES=-1 OLLAMA_HOST=127.0.0.1:11435 setsid -f taskset -c 8-11 /home/usain/.local/ollama/bin/ollama serve >> /home/usain/.ollama/serve-11435.log 2>&1 < /dev/null
sleep 5
# 4. load and pin its model (on the CPU)
curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
# 5. the check
N=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); taskset -cp $N; ps -o ni= -p $N
curl -s -m 5 http://127.0.0.1:11435/api/ps | grep -o '"size_vram":[0-9]*'
for i in 1 2 3; do curl -s -m 120 -o /dev/null -w "%{time_total}s " http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":["what decides a close","the guard rules"]}'; done; echo
```
- Step 5 must show affinity `8-11`, nice `0`, `"size_vram":0` (wholly on the CPU, as the pinned gov requires), and the
  three times (the after figure; target under 2 s at this load).
- Questions in flight during the 10 seconds of the restart fail once; their callers start the server again if it is
  down (the pinned code starts it CPU-only, without these caps: the dispatcher's watch shows it).

## Undo
The same, with `nice -n 10 taskset -c 12-19` in step 3.
