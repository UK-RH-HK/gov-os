# one bounded wait on grafana's a6-on run (pid file post2.pid beside post2.exit), then a short status line
WAIT_FOR_LOG=/home/usain/gov-os-runs/W2-88b/grafana-logs/post2-driver.log bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/wait_for.sh /home/usain/gov-os-runs/W2-88b/grafana-logs/post2.exit "${1:-570}" | grep -E "^wait_for|rc=|chain|end " 
date -Is; grep MemAvailable /proc/meminfo
python3 -c "
import json;d=json.load(open('/home/usain/gov-os-runs/W2-88b/grafana/.gov-runtime/rebuild/record.json'));print(d.get('stage_running'),d.get('stage_running_s'),d.get('stages_done'),d.get('written_at'))" 2>/dev/null
