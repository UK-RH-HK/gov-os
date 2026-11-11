import re, sys, yaml
REG = open('/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md').read()
heads = {}
for m in re.finditer(r'^### (DEC-\d+)[^\n]*\n- \*\*Status:\*\*\s*([A-Z]+)([^\n]{0,160})', REG, re.M):
    heads[m.group(1)] = (m.group(2), m.group(3)[:80])
for t in sys.argv[1:]:
    txt = open(f'/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/{t}.md').read().split('---')[1]
    d = yaml.safe_load(txt)
    out = []
    for s in d['sources']:
        if s.startswith('DEC-'):
            st = heads.get(s, ('MISSING', ''))[0]
            out.append(f'{s}:{st}')
        else:
            out.append(s)
    print(t, d['wbs_id'], ' '.join(out))
