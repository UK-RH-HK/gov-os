"""Self-check of the Gov OS specification and Wave 1 plan (S1 stage 6).

Read-only. Prints PASS, FAIL or SKIP per check and exits non-zero on any FAIL.

Run from anywhere:  python3 docs/plan/tools/validate_s1.py

Inputs inside the repository are always checked. Four checks compare against files outside it (the S1 workbench:
coverage matrix, architecture v0.3, register v0.12, the S1-A round-1 fingerprints) and one against `docs/source/`,
which is archived after S1-A closes. Those checks are SKIPped when their input is absent. Set GOV_OS_WORKBENCH to
point at the workbench (default: ~/gov-os-workbench).
"""
import glob, os, re, sys, fnmatch, csv, yaml
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
W = os.path.expanduser(os.environ.get('GOV_OS_WORKBENCH', '~/gov-os-workbench'))
fails = []
def skip(name, path):
    print(f'SKIP {name} — input not present: {path}')
def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + (f' — {detail}' if detail else ''))
    if not ok: fails.append(name)

def frontmatter(p):
    s = open(p).read()
    assert s.startswith('---\n'), p
    return yaml.safe_load(s[4:s.index('\n---\n', 4)])

# 1. every YAML parses (files + frontmatter of charter, contract md, ADRs, WBS, tickets)
bad = []
yfiles = glob.glob(f'{R}/docs/**/*.yaml', recursive=True)
for p in yfiles:
    if '/docs/source/' in p: continue
    try: yaml.safe_load(open(p))
    except Exception as e: bad.append((p, str(e)[:80]))
fm_files = [f'{R}/docs/charter/CHARTER_v5.md', f'{R}/docs/contract/CONTRACT_v4.md', f'{R}/docs/plan/WAVE_1_WBS.md'] + glob.glob(f'{R}/docs/adr/ADR-*.md') + glob.glob(f'{R}/.tickets/*.md')
fms = {}
for p in fm_files:
    try: fms[p] = frontmatter(p)
    except Exception as e: bad.append((p, str(e)[:80]))
check('YAML parses', not bad, f'{len(yfiles)} files + {len(fm_files)} frontmatters' + (f'; bad: {bad}' if bad else ''))

# 2. capabilities
c = yaml.safe_load(open(f'{R}/docs/contract/contract.yaml'))
caps = c['capabilities']
req = ['outcome', 'acceptance', 'wave', 'provider', 'sources', 'disposition']
miss = [(e['id'], f) for e in caps for f in req if not e.get(f)]
check('60 capabilities, CAP-01..CAP-60', [e['id'] for e in caps] == [f'CAP-{i:02d}' for i in range(1, 61)])
check('every capability has outcome/acceptance/wave/provider/sources/disposition', not miss, str(miss) if miss else '')
check('waves valid', all(e['wave'] in ('W1', 'W2', 'W3') or (e['wave'] == 'NONE' and e['disposition']['class'] == 'DROP') for e in caps))
check('DEC-080 W1 set', all(e['wave'] == 'W1' for e in caps if e['id'] in {'CAP-15', 'CAP-16', 'CAP-18', 'CAP-55', 'CAP-56', 'CAP-57'}))
check('LITE states lite form; DROP states non-goal + DEC', all(('lite_form' in e['disposition']) if e['disposition']['class'] == 'LITE' else ('non_goal' in e['disposition'] and e['disposition']['decisions']) if e['disposition']['class'] == 'DROP' else True for e in caps))
check('MR-1..MR-6 clauses with acceptance', [m['id'] for m in c['master_rules']] == [f'MR-{i}' for i in range(1, 7)] and all(m['acceptance'] for m in c['master_rules']))
# scenario ids exist in the coverage matrix
_p = f'{W}/synthetic/COVERAGE_MATRIX.md'
if os.path.exists(_p):
    matrix = open(_p).read()
    unknown = [s for e in caps for s in e['scenarios']['dev'] + e['scenarios']['qual'] if not re.search(r'\b' + re.escape(s) + r'\b', matrix)]
    check('scenario ids exist in COVERAGE_MATRIX', not unknown, str(unknown[:5]))
else: skip('scenario ids exist in COVERAGE_MATRIX', _p)

# 3. tickets
tk = {v['wbs_id']: (p, v) for p, v in fms.items() if '/.tickets/' in p}
check('44 W1 tickets', sorted(tk) == [f'W1-{i:02d}' for i in range(1, 45)], str(len(tk)))
bad = [i for i, (p, v) in tk.items() if not (v.get('role') and v.get('allowed_paths') and v.get('kpis', {}).get('success') and v.get('kpis', {}).get('failure'))]
check('every W1 ticket has role, allowed_paths, success and failure KPIs', not bad, str(bad))
fields = ['title', 'class', 'role', 'depends_on', 'allowed_paths', 'kpis', 'profile', 'sources', 'est_loc', 'acceptance_tests']
bad = [(i, f) for i, (p, v) in tk.items() for f in fields if f not in v]
check('every W1 ticket has all ten fields', not bad, str(bad[:5]))
probes = ['tests/acceptance/W1-02/test_guard.py', 'tests/acceptance/x', 'tests/acceptance/W1-43/a/b.py']
viol = []
for i, (p, v) in tk.items():
    if v['role'] == 'independent-test-designer': continue
    for pat in v['allowed_paths']:
        if any(fnmatch.fnmatch(pr, pat) for pr in probes) or pat.startswith('tests/acceptance') or pat in ('**', '*', 'tests/**'):
            viol.append((i, pat))
check('no implementer allowed_paths covers tests/acceptance/**', not viol, str(viol))
# DAG: W1 depends_on and tk deps agree, acyclic
idof = {v['id']: i for i, (p, v) in tk.items()}
agree = all(sorted(idof[d] for d in v['deps']) == sorted(v['depends_on']) for i, (p, v) in tk.items())
check('tk deps match depends_on', agree)
color = {}
def dfs(n):
    color[n] = 1
    for d in tk[n][1]['depends_on']:
        if color.get(d) == 1 or (d not in color and not dfs(d)): return False
    color[n] = 2; return True
check('ticket DAG acyclic', all(color.get(n) == 2 or dfs(n) for n in tk))
check('W1 providers exist as tickets', all(p in tk for e in caps for p in e['provider'] if re.fullmatch(r'W1-\d\d', p)))

# 3b. S1-A round-1 repairs
check('every capability has a non-empty covers list (DEC-092)', all(e.get('covers') and all(cv.get('item') and cv.get('source') and cv.get('wave') in ('W1', 'W2', 'W3', 'NONE') for cv in e['covers']) for e in caps))
oneway = []
for e in caps + c['master_rules']:
    for pv in e['provider']:
        if re.fullmatch(r'W1-\d\d', pv) and e['id'] not in tk[pv][1]['sources']: oneway.append((e['id'], '->', pv))
for i, (p_, v) in tk.items():
    for src in v['sources']:
        m = re.fullmatch(r'(CAP-\d\d|MR-\d)', src)
        if m:
            ent = next(e for e in caps + c['master_rules'] if e['id'] == m.group(1))
            if i not in ent['provider']: oneway.append((i, '->', src))
check('provider <-> ticket-source links are two-way (F-14)', not oneway, str(oneway[:6]))
def anc(n, seen=None):
    seen = seen if seen is not None else set()
    for d in tk[n][1]['depends_on']:
        if d not in seen: seen.add(d); anc(d, seen)
    return seen
check('first install (W1-06) is after the install rule and switch-over (W1-04, W1-05) (F-04)', {'W1-04', 'W1-05'} <= anc('W1-06'))
w34 = ' '.join(tk['W1-34'][1]['kpis']['success'])
check('decision package template has ten fields (F-08)', 'current state' in w34 and 'exact permitted next actions' in w34)
mr = {m['id']: m for m in c['master_rules']}
check('MR-4 acceptance names specification milestones and owner packages (F-01)', 'audit ticket' in mr['MR-4']['acceptance'] and 'decision packages' in mr['MR-4']['acceptance'])
check('MR-2 acceptance requires linked gap tickets in W1 (F-02)', 'linked gap ticket' in mr['MR-2']['acceptance'])
wbs = open(f'{R}/docs/plan/WAVE_1_WBS.md').read(); adr2 = open(f'{R}/docs/adr/ADR-0002-architecture-and-stack.md').read()
code = sum(v['est_loc'] for i, (p_, v) in tk.items() if v['class'] == 'implementation')
fig = f'≈ {code:,} LOC'
check('one Wave 1 glue figure in WBS and ADR-0002 (F-16)', fig in wbs and fig in adr2, fig)
texts = {p_: open(p_).read() for p_ in [f'{R}/docs/charter/CHARTER_v5.md', f'{R}/docs/contract/CONTRACT_v4.md', f'{R}/docs/contract/contract.yaml', f'{R}/docs/plan/WAVE_1_WBS.md', f'{R}/docs/spec/gov-os/READINESS.md', f'{R}/docs/contract/SOURCE_MAP.csv'] + glob.glob(f'{R}/docs/adr/*.md') + glob.glob(f'{R}/.tickets/*.md')}
stale = [os.path.basename(p_) for p_, t_ in texts.items() if re.search(r'two (review|audit)|at most two|two rounds|third (review )?round|second round', t_, re.I)]
check('no "two rounds" loop text left outside the register (DEC-096)', not stale, str(stale))
check('CAP-59 acceptance follows DEC-096', 'three consecutive' in next(e for e in caps if e['id'] == 'CAP-59')['acceptance'])

# 3c. S1-A round-2 repairs (F-21..F-24)
cov = {cv['id']: (e, cv) for e in caps for cv in e['covers']}
check('covers item ids are unique and well-formed', len(cov) == sum(len(e['covers']) for e in caps) and all(re.fullmatch(e['id'] + r'\.[a-z]', cv['id']) for e, cv in cov.values()), f'{len(cov)} items')
w1 = {i: cv for i, (e, cv) in cov.items() if cv['wave'] == 'W1'}
def named(ticket, cid):
    k = tk[ticket][1]['kpis']
    return any(re.search(r'\[[^\]]*\b' + re.escape(cid) + r'\b[^\]]*\]\s*$', line) for line in k['success'] + k['failure'])
miss = [(i, t) for i, cv in w1.items() for t in (cv.get('provider') or ['<none>']) if t == '<none>' or t not in tk or not named(t, i)]
check('every Wave 1 covers item is named by a KPI of its provider ticket (F-21)', not miss, f'{len(w1)} W1 items' + (f'; missing {miss[:6]}' if miss else ''))
stray = []
for t, (p_, v) in tk.items():
    for line in v['kpis']['success'] + v['kpis']['failure']:
        m = re.search(r'\[([^\]]*CAP-\d\d\.[a-z][^\]]*)\]\s*$', line)
        for cid in (re.findall(r'CAP-\d\d\.[a-z]', m.group(1)) if m else []):
            if cid not in w1 or t not in (w1[cid].get('provider') or []): stray.append((t, cid))
check('every covers id cited by a ticket KPI is a Wave 1 item naming that ticket as provider', not stray, str(stray[:6]))
unlinked = [(i, t) for i, cv in w1.items() for t in cv['provider'] if t not in cov[i][0]['provider'] or cov[i][0]['id'] not in tk[t][1]['sources']]
check('covers providers are capability providers and ticket sources, both ways (F-24)', not unlinked, str(unlinked[:6]))
check('non-W1 covers items keep their wave tags (no item re-tagged)', sum(1 for e, cv in cov.values() if cv['wave'] == 'W1') >= 120)
cap44 = ' '.join(cv['item'] for cv in next(e for e in caps if e['id'] == 'CAP-44')['covers'])
w41 = ' '.join(tk['W1-41'][1]['kpis']['success'])
check('native-layout clause in CAP-44 covers and W1-41 (F-22)', 'healthy native' in cap44 and 'healthy native' in w41)
check('LITE wave-exit audit KPI in W1-36 (F-23)', any('one row per LITE feature specification' in l for l in tk['W1-36'][1]['kpis']['success']))
adr2fm = fms[f'{R}/docs/adr/ADR-0002-architecture-and-stack.md']
check('ADR-0002: DEC-092 in frontmatter and DEC range to DEC-096', 'DEC-092' in adr2fm['decisions'] and 'DEC-064…DEC-096' in open(f'{R}/docs/adr/ADR-0002-architecture-and-stack.md').read())
import hashlib
_p = f'{W}/s1a-round1.sha256'
if os.path.exists(_p):
    bad_h = []
    for line in open(_p):
        h, rel = line.strip().split('  ', 1)
        fp = os.path.join(W, 's1a', rel)
        if not os.path.exists(fp) or hashlib.sha256(open(fp, 'rb').read()).hexdigest() != h: bad_h.append(rel)
    check('s1a round-1 files unchanged (fingerprints)', not bad_h, str(bad_h))
else: skip('s1a round-1 files unchanged (fingerprints)', _p)

# 3d. S1-A round-3 repairs (F-25, F-26)
c02 = next(e for e in caps if e['id'] == 'CAP-02')['covers']
a02 = next(cv for cv in c02 if cv['id'] == 'CAP-02.a')
tag02 = [cv for cv in c02 if 'git tag -v' in cv['item']]
check('CAP-02.a is the W1 manifest item; the signed tag is a separate W3 item with no W1 provider (F-25)',
      a02['wave'] == 'W1' and 'signed' not in a02['item'].lower() and len(tag02) == 1 and tag02[0]['wave'] == 'W3' and not tag02[0].get('provider'))
need = {'W1-30': ['W1-24'], 'W1-36': ['W1-24', 'W1-26'], 'W1-11': ['W1-34'], 'W1-15': ['W1-08'], 'W1-24': ['W1-09', 'W1-34'],
        'W1-35': ['W1-21', 'W1-26'], 'W1-28': ['W1-09'], 'W1-09': ['W1-10'], 'W1-44': ['W1-21']}
lack = [(t, d) for t, ds in need.items() for d in ds if d not in anc(t)]
check('tickets depend on the tickets their KPIs need (F-26 and the cases found on review)', not lack, str(lack))
fam = [(t, l) for t, (p_, v) in tk.items() for l in v['kpis']['success'] if 'CAP-38.b' in l]
reg_t = sorted(t for t, l in fam if l.startswith('Registers the'))
check('each governance test family check is registered by its subject ticket; W1-42 asserts 17 of 17 (F-26)',
      reg_t == ['W1-15', 'W1-17', 'W1-21', 'W1-24', 'W1-25', 'W1-27', 'W1-30', 'W1-35', 'W1-36', 'W1-38'] and any(t == 'W1-42' and '17 of 17' in l for t, l in fam)
      and any(t == 'W1-26' and 'registered by the ticket that builds its subject' in l for t, l in fam))
check('WBS points to docs/plan/tools/validate_s1.py, and the file is this script', 'docs/plan/tools/validate_s1.py' in wbs and os.path.abspath(__file__) == os.path.join(R, 'docs/plan/tools/validate_s1.py'))

# 4. readiness dimensions = Framework §37 verbatim
rd = yaml.safe_load(open(f'{R}/docs/contract/readiness-dimensions.yaml'))
_p = f'{R}/docs/source/originals/DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md'
if os.path.exists(_p):
    fw = open(_p).read()
    sec = fw[fw.index('## 37.'):fw.index('## 38.')]
    names = re.findall(r'^\d+\. (.+?);?\.?$', sec, re.M)
    check('26 readiness dimensions match Framework §37', [d['name'] for d in rd['dimensions']] == [n.rstrip(';.') for n in names] and len(names) == 26)
else: skip('26 readiness dimensions match Framework §37', _p)
check('26 readiness dimensions, numbered 1..26', [d['n'] for d in rd['dimensions']] == list(range(1, 27)))
check('five cell states', [s['state'] for s in rd['cell_states']] == ['PRESENT', 'MISSING', 'PROVISIONAL', 'BLOCKED', 'N/A_WITH_REASON'])
rt = open(f'{R}/docs/spec/gov-os/READINESS.md').read()
rows = re.findall(r'^\| (\d+) \| (.+?) \| (PRESENT|MISSING|PROVISIONAL|BLOCKED|N/A_WITH_REASON) \|', rt, re.M)
check('READINESS.md: 26 rows, all PRESENT or N/A_WITH_REASON', len(rows) == 26 and all(r[2] in ('PRESENT', 'N/A_WITH_REASON') for r in rows) and [r[1] for r in rows] == [d['name'] for d in rd['dimensions']])

# 5. master rules verbatim
_p = f'{W}/input/GOV_OS_ARCHITECTURE_v0.3.md'
if os.path.exists(_p):
    arch = open(_p).read().split('\n')
    block = '\n'.join(arch[55:92])
    check('MR-1..MR-6 verbatim in Charter v5', block in open(f'{R}/docs/charter/CHARTER_v5.md').read())
else: skip('MR-1..MR-6 verbatim in Charter v5', _p)

# 6. register: v0.12 prefix intact, DEC-083..087 appended
reg = open(f'{R}/docs/DECISION_REGISTER.md').read()
_p = f'{W}/input/GOV_OS_DECISION_REGISTER_v0.12.md'
if os.path.exists(_p): check('register starts with exact v0.12', reg.startswith(open(_p).read()))
else: skip('register starts with exact v0.12', _p)
check('DEC-083..DEC-087 ACCEPTED (owner, 2026-09-30)', all(re.search(rf'### {d} .*\n- \*\*Status:\*\* ACCEPTED \(owner, 2026-09-30\)', reg) for d in ['DEC-083', 'DEC-084', 'DEC-085', 'DEC-086', 'DEC-087']))
check('DEC-088..DEC-096 ACCEPTED (owner, 2026-10-01)', all(re.search(rf'### DEC-{n:03d} .*\n- \*\*Status:\*\* ACCEPTED \(owner, 2026-10-01\)', reg) for n in range(88, 97)))

# 7. ADR frontmatter
for p in glob.glob(f'{R}/docs/adr/ADR-*.md'):
    v = fms[p]; check(f'{os.path.basename(p)} frontmatter id/status/depends_on/decisions', bool(v.get('id')) and v.get('status') == 'PROPOSED' and 'depends_on' in v and v.get('decisions'))

# 8. source map
with open(f'{R}/docs/contract/SOURCE_MAP.csv') as f: sm = list(csv.DictReader(f))
check('SOURCE_MAP rows all carried or disposed', sm and all(r['carried_by_or_disposition'].strip() for r in sm), f'{len(sm)} rows')
check('SOURCE_MAP has a class column with DEC-070 classes', all(r.get('class') in ('OK', 'MISSING', 'WEAKENED', 'CONTRADICTS', 'UNJUSTIFIED_DROP', 'SCOPE_CREEP') for r in sm))

# 9. write scope: only docs/ (not docs/source, SOURCES.md) and .tickets/ changed vs main
import subprocess
ch = subprocess.run(['git', '-C', R, 'diff', '--name-only', 'main...HEAD'], capture_output=True, text=True).stdout.split()
ch += subprocess.run(['git', '-C', R, 'status', '--porcelain'], capture_output=True, text=True).stdout.split('\n')
ch = [x.strip().split()[-1] for x in ch if x.strip()]
out = [x for x in ch if not ((x.startswith('docs/') and not x.startswith('docs/source/') and x != 'docs/SOURCES.md') or x.startswith('.tickets/'))]
check('writes only under docs/ and .tickets/', not out, str(out))
print('\nRESULT:', 'ALL PASS' if not fails else f'{len(fails)} FAIL')
sys.exit(1 if fails else 0)
