cd /home/usain/gov-os-worktrees/W2-188
for p in .gov-runtime/scratch/ps/x.py .gov-runtime/scratch/lead/x.py .gov-runtime/scratch/x.py docs/probes/DAEO-zlog/x.py; do
  printf '{"tool_name":"Write","tool_input":{"file_path":"/home/usain/gov-os-worktrees/W2-188/%s","content":"x"},"cwd":"/home/usain/gov-os-worktrees/W2-188","session_id":"t"}' "$p" | env PYTHONPATH=/home/usain/gov-os-worktrees/W2-188/src GOV_ROLE=product-spec GOV_TICKET=DAEO-zlog CLAUDE_PROJECT_DIR=/home/usain/gov-os-worktrees/W2-188 python3 .claude/hooks/pretooluse.py; echo " -> $p rc=$?"
done
