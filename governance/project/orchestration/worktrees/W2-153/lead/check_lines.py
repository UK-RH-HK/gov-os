import re,pathlib
root=pathlib.Path('.')
pat=re.compile(r'^- \*\*(Launch default|Launch by criticality|Skills):\*\*')
bad=0
for rf in sorted((root/'template/governance/kernel/roles').glob('*.md')):
    lines=[l for l in rf.read_text().splitlines() if pat.match(l)]
    for d in ['.claude/agents','.rulesync/subagents','template/.rulesync/subagents']:
        c=(root/d/rf.name).read_text().splitlines()
        for l in lines:
            if l not in c:
                bad+=1; print('MISSING',d,rf.name,l[:60])
    print(rf.name,len(lines))
print('bad',bad)
