#!/bin/sh
# Round 4: a full rebuild, then the context check timed (DEC-768), the cache cold for the new device key.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
LOG=/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log
sh /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/run_rebuild.sh rebuild9
git log --oneline -1 > "$LOG/ctx4.txt"
uptime >> "$LOG/ctx4.txt"
nproc >> "$LOG/ctx4.txt"
/usr/bin/time -v env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src \
  python3 -m gov.context.context_check >> "$LOG/ctx4.txt" 2>&1
echo $? > "$LOG/ctx4.exit"
uptime >> "$LOG/ctx4.txt"
python3 -c "
import sqlite3
c=sqlite3.connect('file:/home/usain/gov-os-worktrees/W2-54/.gov-runtime/query-vector-cache.db?mode=ro',uri=True)
for (n,) in c.execute(\"select name from sqlite_master where type='table'\"): print('cache table', n, c.execute(f'select count(*) from {n}').fetchone()[0])
" >> "$LOG/ctx4.txt" 2>&1
echo done > "$LOG/ctx4.done"
