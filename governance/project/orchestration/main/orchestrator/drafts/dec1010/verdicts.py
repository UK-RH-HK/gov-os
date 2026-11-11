import re, sys, json, glob, os, subprocess
ROOT = '/home/usain/Dynamic-Agentic-Engineering-OS'
dirs = [ROOT + '/governance/project/orchestration/reviews', ROOT + '/.gov-runtime/scratch/orchestrator/reviews']
BLOCK = re.compile(r"```verdict\s*\n(.*?)\n```", re.S)
paths = []
for d in dirs:
    for p in sorted(glob.glob(d + '/*.md')):
        paths.append(p)
paths += sorted(glob.glob(ROOT + '/docs/probes/*/*.md'))
for p in paths:
    try:
        t = open(p, errors='replace').read()
    except Exception as e:
        continue
    mt = os.path.getmtime(p)
    import datetime
    dt = datetime.datetime.fromtimestamp(mt).strftime('%m-%d %H:%M')
    blocks = BLOCK.findall(t)
    res = []
    for b in blocks:
        try:
            d = json.loads(b)
            nblock = 0; nf = 0; nfail = 0
            for k in d.get('kpis', []):
                if k.get('verdict') == 'fail':
                    nfail += 1
                for f in k.get('findings', []) or []:
                    nf += 1
                    if f.get('scope') == 'in' and f.get('ordinary_work') == 'yes' and f.get('consequence') in ('fails open', 'loses work'):
                        nblock += 1
            res.append('%dblk/%dfind/%dfail' % (nblock, nf, nfail))
        except Exception:
            res.append('bad')
    rel = p.replace(ROOT + '/', '')
    print(dt, '|', rel, '|', len(blocks), 'blocks', '|', ' ; '.join(res))
