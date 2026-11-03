# After the restart of WSL and the machine (owner, DEC-1052 "Tonight"), 2026-11-03

Written 2026-11-03 00:00 by the CTO (session debdb3f7). Run as `usain`, in a plain terminal or the operator's session,
**in this order** (the shared embedding server first: any `gov` command could otherwise start it without its caps).

## Comes back by itself
- **cron** (systemd, enabled) and with it **the dispatcher's every-minute pass**, the only active crontab line.
  Its ready list is empty, there is no `land.txt`, and the queue's approvals are parked: it starts and lands nothing;
  its status, Load Balancer and GPU alerts run. Check: `crontab -l | grep -v '^#'` shows only `run_tick.sh`.

## Start again, by hand, in this order
1. **The shared embedding server, 127.0.0.1:11434** (CPUs 12-19, nice 10, the GPU; ACT-OLLAMA-CAP-1), then pin its model:
   ```bash
   ss -ltn | grep -q ':11434 ' || setsid -f nice -n 10 taskset -c 12-19 /home/usain/.local/ollama/bin/ollama serve > /home/usain/.ollama/serve-11434.log 2>&1 < /dev/null
   sleep 5; curl -s -m 120 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
   N=$(ss -ltnp | grep ':11434 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); taskset -cp $N; ps -o ni= -p $N   # expect 12-19 and 10
   curl -s http://127.0.0.1:11434/api/ps                                              # expect qwen3-embedding:0.6b, size_vram > 0
   ```
2. **The query server, 127.0.0.1:11435** (the GPU, CPUs 8-11, nice 0; ACT-QUERY-GPU-2: the wrapper `~/.local/bin/ollama`
   reads `~/.ollama/query-server-device`, which must say `gpu`), then pin its model:
   ```bash
   cat ~/.ollama/query-server-device                                                  # expect: gpu
   ss -ltn | grep -q ':11435 ' || OLLAMA_HOST=127.0.0.1:11435 setsid -f ~/.local/bin/ollama serve < /dev/null
   sleep 5; curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
   N=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); taskset -cp $N; tr '\0' '\n' < /proc/$N/environ | grep -c '^CUDA_VISIBLE_DEVICES=-1$'   # expect 8-11 and 0
   ```
   Then the dispatcher's status (`.gov-runtime/scratch/orchestrator/dispatch/status.txt`, within a minute) shows
   "layers: shared 29/29, query 29/29".
3. **The sentinel** (ACT-SENTINEL-1; Claude Code may stop at its folder-trust prompt: `tmux attach -t cto-sentinel`,
   accept, then Ctrl-b d):
   ```bash
   tmux new -d -s cto-sentinel 'cd /home/usain/Dynamic-Agentic-Engineering-OS && ~/.local/bin/claude --remote-control "CTO sentinel" --model claude-haiku-5-5 --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"DAEO-sdxk\"}}" "$(cat governance/project/orchestration/tools/sentinel-brief.md)"'
   ```
   Check: its watch writes `.gov-runtime/scratch/orchestrator/log/deadman.log` within a few minutes.
4. **The samplers, the memory guard and the slot watcher** (the CTO's tools; light, one sample a minute or less):
   ```bash
   O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
   cd /home/usain/Dynamic-Agentic-Engineering-OS && setsid -f bash $O/tools/mem_sampler.sh > /dev/null 2>&1 < /dev/null
   cd $O && setsid -f python3 tools/kind_sampler.py --every 60 > /dev/null 2>&1 < /dev/null
   cd $O/tools && setsid -f bash oom_watch.sh > /dev/null 2>&1 < /dev/null
   cd $O && setsid -f python3 tools/rerank_service_slot_hold.py --watch >> log/rerank-slot-hold.log 2>&1 < /dev/null
   ps -eo pid,args | grep -E 'mem_sampler|kind_sampler|oom_watch|rerank_service_slot_hold' | grep -v grep   # expect 4
   ```
5. **The CTO's fresh session** (the owner starts it with the w2-orchestrator prompt): identity `orchestrator DAEO-sdxk`;
   Remote Control and one test push; register `log/cto-session.txt`; `mv log/cto-standby.txt
   log/cto-standby.ended-HHMM.txt`; arm `tools/inbox_wait_quiet.sh`; then RESUME HERE (the plan at its top).

## Must NOT start (DEC-1049, DEC-1050, DEC-1051)
- the nightly and its checks (crontab lines stay commented: `# DEC-1049 stopped:`), the runs sweep (`# DEC-1050 stopped:`);
- `tools/bench_loop.sh` and `tools/usage_watch.sh` (stopped on the owner's word);
- any lead (the ready list stays empty) and any landing (the approvals stay parked; no `dispatch/land.txt`) until the
  CTO restarts work under the plan (DEC-1052);
- W2-112's shared reranker service (it starts with W2-112's work, under the slot watcher);
- the guard-refusal harvest (off in `dispatch/config.json`: `guard_harvest_s` 10^9);
- any full suite (only P1-12's, on the owner's word), any `gov close` or queue run, any gitleaks scan.
- No change to `.wslconfig` before the RAM upgrade (DEC-1038 (3)).
