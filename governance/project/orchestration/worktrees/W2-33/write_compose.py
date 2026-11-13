import re
from gov.adapters.portability import compose

root = '/home/usain/gov-os-worktrees/W2-33'
target = root + '/template/.rulesync/subagents/orchestrator.md'
text = compose(root, 'orchestrator')
open(target, 'w', encoding='utf-8').write(text)
print('lines', len(text.splitlines()))
again = open(target, encoding='utf-8').read()
print('compose equals file', compose(root, 'orchestrator') == again)
for pat in [r'asks? on (every|each|all)', r'(every|each|all) install', r'prompts? on', r'asks? [^.\n]*every install']:
    print(pat, re.findall(pat, again, re.I))
print('coordination_ticket' in again, 'GOV_TICKET' in again)
