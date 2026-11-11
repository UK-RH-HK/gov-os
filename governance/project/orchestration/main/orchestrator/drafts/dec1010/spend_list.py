import json, sys
rows = []
for line in open('/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/spend.jsonl'):
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    rows.append(d)
for d in rows:
    print(d.get('at'), '|', d.get('kind'), '|', d.get('ticket'), '|', d.get('wbs'), '|', d.get('role'), '|', (d.get('what') or '')[:150])
