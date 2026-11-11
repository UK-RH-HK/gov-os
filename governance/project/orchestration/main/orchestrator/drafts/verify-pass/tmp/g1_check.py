import sys, yaml, re, subprocess
bad = {}
for l in open('.gov-runtime/scratch/orchestrator/drafts/verify-pass/tmp/before.txt'):
    p = l.split('|'); bad[p[0]] = p[3].rstrip(',').split(',') if p[3] else []
for t in sys.argv[1:]:
    txt = open(f'.tickets/{t}.md', encoding='utf-8').read()
    fm = yaml.safe_load(txt.split('---')[1])
    k = fm['kpis']
    items = [('S', i, x) for i, x in enumerate(k.get('success') or [], 1)] + [('F', i, x) for i, x in enumerate(k.get('failure') or [], 1)]
    miss = [f'{a}{b}' for a, b, x in items if not re.search(r'Verify:\s*\S', str(x))]
    r = subprocess.run(['gov', 'brief', 'lead', t, '--run', 'tests'], capture_output=True, text=True)
    codes = sorted(set(re.findall(r'gov brief: ([A-Z_]+)', r.stdout + r.stderr)) - {'BRIEF_NOT_READY'})
    print(t, 'items', len(items), 'expected_refused_before', len(bad[t]), 'no-verify-now', miss, 'codes', codes)
