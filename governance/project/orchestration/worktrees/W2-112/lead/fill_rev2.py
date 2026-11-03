from pathlib import Path

lead = Path('/home/usain/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead')
brief = (lead / 'briefs/rev-2.md').read_text()
judgement = Path('/home/usain/gov-os-worktrees/W2-112/governance/project/briefs/JUDGEMENT.md').read_text().strip()
results = (lead / 'briefs/rev-2-results.md').read_text().strip()
brief = brief.replace('@@HEAD12@@', '03b97eb17284').replace('@@RESULTS@@', results).replace('@@JUDGEMENT@@', judgement)
assert '@@' not in brief
(lead / 'briefs/rev-2.md').write_text(brief)
print('ok', len(brief))
