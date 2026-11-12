import json, sys, re
sys.path.insert(0, '/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools')
import verdict

raw = open('/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rv-r2.json').read()
# the last JSON object in the log
obj = None
for i in range(len(raw) - 1, -1, -1):
    if raw[i] == '{':
        try:
            obj = json.loads(raw[i:])
            if 'result' in obj:
                break
        except Exception:
            pass
res = obj['result']
open('/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/log/rv-r2-result.md', 'w').write(res)
m = re.search(r'^````\s*\n(---\ntype: probe.*?)\n````', res, re.S | re.M)
rec = m.group(1) if m else None
if rec:
    open('/home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/lead/probes-CITP-REVIEW-r2.md', 'w').write(rec + '\n')
print('record found:', bool(rec), 'chars', len(rec or ''))
print('ready:', verdict.ready(rec or res))
