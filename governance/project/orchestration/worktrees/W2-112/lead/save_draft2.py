import sys
from pathlib import Path

sys.path.insert(0, '/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools')
import verdict

text = Path('/tmp/gov-os-lead-W2-112/rev2-result.md').read_text()
start = text.index('```yaml\n') + len('```yaml\n')
end = text.index('```', start)
front = text[start:end].strip().splitlines()
lines = []
for line in front:
    lines.append(line)
    if line.startswith('task:'):
        lines.append('reviewer_session: 466fc8b2-409a-46e3-ba15-b92368fc2655')
        lines.append('implementer_session: f828ddfe-8d6f-4c83-80f7-210571776dfc')
body_start = text.index('## Probe record')
body_end = text.rindex('\n---\n')
record = '---\n' + '\n'.join(lines) + '\n---\n\n' + text[body_start:body_end].strip() + '\n'
out = Path('/home/usain/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/probes/PR-DAEO-clon-round2-DRAFT-fail.md')
out.write_text(record)
print(out, len(record))
print('READY:', verdict.ready(record))
