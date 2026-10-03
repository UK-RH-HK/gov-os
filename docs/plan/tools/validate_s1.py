"""Self-check of the Gov OS specification and Wave 1 plan (S1 stage 6, extended by the S2 specification change, DEC-155).

Read-only. Prints PASS, FAIL or SKIP per check and exits non-zero on any FAIL.

Run from anywhere:  python3 docs/plan/tools/validate_s1.py

Inputs inside the repository are always checked. Four checks compare against files outside it (the S1 workbench:
coverage matrix, architecture v0.3, register v0.12, the S1-A round-1 fingerprints) and one against `docs/source/`,
which is archived after S1-A closes. Those checks are SKIPped when their input is absent. Set GOV_OS_WORKBENCH to
point at the workbench (default: ~/gov-os-workbench).

Section 3e checks what the S2 change added (Contract v4.1, tickets W1-45…W1-48, DEC-150…DEC-162). The write-scope
check of S1 (section 9) applies on branch `s1/spec` only; on `s2/spec` the S2 write scope is checked instead.
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
check('62 capabilities, CAP-01..CAP-62', [e['id'] for e in caps] == [f'CAP-{i:02d}' for i in range(1, 63)])
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
check('48 W1 tickets', sorted(tk) == [f'W1-{i:02d}' for i in range(1, 49)], str(len(tk)))
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
        ret = fp[:-3] + '.retired.md'   # the owner retired the s1a session (DEC-101): its prompt was renamed, content unchanged
        if not os.path.exists(fp) and os.path.exists(ret): fp = ret
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

# 3e. S2 specification change (DEC-150..DEC-162; docs/changes/S2-CIT-P.md, S2-CIT-E.md)
import json, subprocess, collections
cmd = open(f'{R}/docs/contract/CONTRACT_v4.md').read()
cap = {e['id']: e for e in caps}
def kp(t): return ' '.join(tk[t][1]['kpis']['success'] + tk[t][1]['kpis']['failure'])
check('Contract is version 4.1 in both files, with a change log', str(c.get('version')) == '4.1' and [x['version'] for x in c.get('change_log', [])] == ['4.0', '4.1']
      and str(fms[f'{R}/docs/contract/CONTRACT_v4.md'].get('version')) == '4.1' and '| 4.1 | 2026-10-03 |' in cmd)
gone = [e['id'] for e in caps if f"### {e['id']} — {e['title']}\n" not in cmd] + [cv['id'] for e in caps for cv in e['covers'] if f"`{cv['id']}` [{cv['wave']}] {cv['item']} — {cv['source']}" not in cmd]
gone += [e['id'] + ':' + f for e in caps for f in ('outcome', 'acceptance') if e[f] not in cmd] + [m['id'] for m in c['master_rules'] if m['acceptance'] not in cmd]
check('CONTRACT_v4.md and contract.yaml carry the same capabilities, outcomes, acceptance checks and covers items', not gone, str(gone[:6]))
cnt = collections.Counter((e['wave'], e['disposition']['class']) for e in caps)
rows_ok = all(f"| {w} | {cnt[(w, 'KEPT')]} | {cnt[(w, 'LITE')]} | {cnt[(w, 'DROP')]} | {sum(v for (ww, _), v in cnt.items() if ww == w)} |" in cmd for w in ('W1', 'W2', 'W3', 'NONE'))
check('Contract §1 counts match contract.yaml (W1 KEPT 38, 62 in all)', rows_ok and cnt[('W1', 'KEPT')] == 38 and f'| **All** | 56 | 4 | 2 | 62 |' in cmd)
check('DEC-150..DEC-162 ACCEPTED (owner, 2026-10-03)', all(re.search(rf'### DEC-{n} .*\n- \*\*Status:\*\* ACCEPTED \(owner, 2026-10-03\)', reg) for n in range(150, 163)))
check('CAP-61 and CAP-62 are W1 KEPT, provided by W1-46/W1-48 and W1-47', all(cap[i]['wave'] == 'W1' and cap[i]['disposition']['class'] == 'KEPT' for i in ('CAP-61', 'CAP-62'))
      and {'W1-46', 'W1-48'} <= set(cap['CAP-61']['provider']) and cap['CAP-62']['provider'] == ['W1-47'] and 'dangerouslyDisableSandbox' in cap['CAP-62']['acceptance'])
check('CAP-58 claim split between the sandbox (worker Bash) and the guard (file tools); providers W1-45, W1-46, W1-47', 'OS sandbox' in cap['CAP-58']['acceptance'] and 'guard' in cap['CAP-58']['acceptance']
      and {'W1-45', 'W1-46', 'W1-47'} <= set(cap['CAP-58']['provider']) and cov['CAP-58.d'][1]['provider'] == ['W1-46'] and cov['CAP-58.e'][1]['provider'] == ['W1-45'] and cov['CAP-58.f'][1]['provider'] == ['W1-47'] and 'PostToolUseFailure' in cov['CAP-58.f'][1]['item'])
check('MR-3 carries the orchestrator exception (DEC-156) and names W1-45', 'orchestrator may write anywhere in the repository except `tests/acceptance/**`' in mr['MR-3']['acceptance'] and 'W1-45' in mr['MR-3']['provider'])
c49 = cov['CAP-49.c'][1]['item']
check('CAP-49: oracle hidden by the sandbox for workers (W1-46) and by the committed Read deny rule plus the guard for every root session (W1-47, DEC-162)',
      cov['CAP-49.b'][1]['provider'] == ['W1-46'] and cov['CAP-49.c'][1]['provider'] == ['W1-47'] and '.claude/settings.json' in c49 and all(x in c49 for x in ('Read, Grep, Glob, Bash', 'accepted residual')) and cap['CAP-49']['wave'] == 'W3')
check('CAP-22.a is delivered by W1-05, then W1-33 (DEC-154)', cov['CAP-22.a'][1]['provider'] == ['W1-05', 'W1-33'] and 'W1-05' in cap['CAP-22']['provider'])
carried = {'DEC-102': 'W1', 'DEC-103': 'W1', 'DEC-104': 'W2', 'DEC-105': 'W1', 'DEC-106': 'W1', 'DEC-136': 'W1', 'DEC-137': 'W1', 'DEC-158': 'W1', 'DEC-159': 'W1', 'DEC-160': 'W2'}
lost = [d_ for d_, w_ in carried.items() if not any(d_ in cv['source'] and cv['wave'] == w_ for e, cv in cov.values())]
check('every carried decision (DEC-102..106, 136, 137, 158..160) is the source of a covers item in its wave', not lost, str(lost))
check('installs unchanged (DEC-157): envelope keeps the DEC-083 sentence, CAP-25.b is untouched, worker roles never install system-wide',
      c['envelope']['tool_installs']['statement'].startswith('The orchestrator installs a tool only after the owner approves a decision package in chat') and 'Worker roles never install system-wide' in c['envelope']['tool_installs']['statement']
      and cov['CAP-25.b'][1]['item'].startswith('Orchestrator-only install on owner approval in chat') and cov['CAP-25.d'][1]['provider'] == ['W1-48'])
def T(n): return tk[n][1]
shape = {'W1-45': ('engineer', 'FULL', ['W1-05']), 'W1-46': ('engineer', 'FULL', ['W1-07', 'W1-48']), 'W1-47': ('engineer', 'FULL', ['W1-45']), 'W1-48': ('orchestrator', 'LITE', ['W1-06'])}
bad = [n for n, (r_, p_, d_) in shape.items() if (T(n)['role'], T(n)['profile'], sorted(T(n)['depends_on'])) != (r_, p_, d_) or T(n)['acceptance_tests']['path'] != f'tests/acceptance/{n}/']
check('S2 tickets W1-45..W1-48 have the agreed role, profile, dependencies and acceptance-test path', not bad, str(bad))
check('W1-45 (orchestrator write scope) is in_progress (DEC-150)', T('W1-45')['status'] == 'in_progress')
k46 = kp('W1-46')
check('W1-46 KPIs carry the three tests DEC-161 requires, the network profiles, the temp directory and the start refusal',
      all(x in k46 for x in ('a launched worker is sandboxed', 'accepting the research domains', 'GOV_ROLE and GOV_TICKET', 'empty allowlist', 'per-session temp directory', 'refuses to start', 'Edit deny rules')))
k47 = kp('W1-47')
check('W1-47 delivers the escape-hatch denial, PostToolUseFailure and both oracle layers; it may edit .claude/settings.json',
      all(x in k47 for x in ('dangerouslyDisableSandbox', 'PostToolUseFailure', 'Read deny rule', 'Read, Grep, Glob or Bash')) and '.claude/settings.json' in T('W1-47')['allowed_paths'])
check('W1-48 pins Claude Code at 2.1.285 or later', '2.1.285' in kp('W1-48'))
check('W1-42 depends on the launcher and the guard hardening, and reports the learning metrics', {'W1-46', 'W1-47'} <= set(T('W1-42')['depends_on']) and 'learning metrics' in kp('W1-42') and 'learning metrics' in kp('W1-31'))
check('W1-30 requires the post-green probe record for FULL tickets (DEC-137)', 'post-green probe record' in kp('W1-30'))
layer = {}
def lay(n):
    if n not in layer: layer[n] = 1 + max([lay(d_) for d_ in T(n)['depends_on']], default=0)
    return layer[n]
for n in tk: lay(n)
bylayer = collections.defaultdict(list)
for n, l_ in layer.items(): bylayer[l_].append(n)
check('WBS §2 layers match the ticket DAG', all(f"| {l_} | {', '.join(sorted(ns))} |" in wbs for l_, ns in bylayer.items()))
best = {}
def longest(n):
    if n not in best:
        m = max([longest(d_) for d_ in T(n)['depends_on']], key=lambda x: x[0], default=(0, []))
        best[n] = (m[0] + (T(n)['est_loc'] or 50), m[1] + [n])
    return best[n]
cpath = max((longest(n) for n in tk), key=lambda x: x[0])[1]
check('WBS critical path is the LOC-weighted longest path of the ticket DAG', '**Critical path** (weighted by est. LOC; a ticket with no code counts as 50): ' + ' → '.join(cpath) + '.' in wbs, ' → '.join(cpath))
sizes = collections.Counter()
for n in tk: sizes[T(n)['class']] += T(n)['est_loc']
check('WBS §1 rows and §3 sizes match the tickets', all(f"| {k_} | {v_} |" in wbs for k_, v_ in sizes.items()) and f"| **Total** | **{sum(sizes.values())}** |" in wbs
      and all(re.search(rf"\| (\*\*)?{n}(\*\*)? \| `{T(n)['id']}` \| {re.escape(T(n)['title'])} \| {T(n)['class']} \| {T(n)['role']} \| {T(n)['profile']} \| {', '.join(T(n)['depends_on']) or '—'} \| {T(n)['est_loc']} \|", wbs) for n in tk))
check('WBS Wave 2 outline names the sandbox experiment (DEC-160) and UX before build (DEC-104)', 'DEC-160' in wbs[wbs.index('## 6. Wave 2'):] and 'DEC-104' in wbs[wbs.index('## 6. Wave 2'):])
adr1 = open(f'{R}/docs/adr/ADR-0001-threat-model.md').read()
check('ADR-0002 has the sandbox layer, the launcher and the Claude Code pin; ADR-0001 keeps "guardrail, not a boundary" for the sandbox',
      all(x in adr2 for x in ('**the OS sandbox**', '`launch`', '2.1.285', 'gov launch', 'DEC-162')) and 'DEC-161' in adr2fm['decisions'] and 'stronger guardrail' in adr1)
boot = open(f'{R}/governance/project/bootstrap.md').read()
check('bootstrap.md marks the residuals closed for worker sessions and restates the open ones, the oracle residual included',
      all(x in boot for x in ('Closed for Bash in launched worker sessions', "Still open for the orchestrator's own session", 'DEC-123', 'DEC-147', 'DEC-159', 'DEC-160', 'DEC-162', 'An opaque Bash read of the qualification oracle', 'MCP server')))
_p = f'{R}/.claude/settings.json'
check('the repository settings carry no sandbox block (DEC-161)', 'sandbox' not in json.load(open(_p)))
citp, cite = f'{R}/docs/changes/S2-CIT-P.md', f'{R}/docs/changes/S2-CIT-E.md'
check('S2-CIT-P is ACCEPTED and S2-CIT-E exists', os.path.exists(citp) and frontmatter(citp)['status'] == 'ACCEPTED' and os.path.exists(cite) and frontmatter(cite)['id'] == 'S2-CIT-E')

# 9. write scope, per branch (DEC-155)
def changed(base):
    ch = subprocess.run(['git', '-C', R, 'diff', '--name-only', f'{base}...HEAD'], capture_output=True, text=True).stdout.split('\n')
    ch += [x[3:] for x in subprocess.run(['git', '-C', R, 'status', '--porcelain'], capture_output=True, text=True).stdout.split('\n')]
    return [x.strip().split(' -> ')[-1] for x in ch if x.strip()]
branch = subprocess.run(['git', '-C', R, 'branch', '--show-current'], capture_output=True, text=True).stdout.strip()
if branch == 's1/spec':
    out = [x for x in changed('main') if not ((x.startswith('docs/') and not x.startswith('docs/source/') and x != 'docs/SOURCES.md') or x.startswith('.tickets/'))]
    check('writes only under docs/ and .tickets/', not out, str(out))
else: print(f'SKIP writes only under docs/ and .tickets/ — applies to branch s1/spec only (DEC-155); this is {branch or "a detached HEAD"}')
if branch == 's2/spec':
    out = [x for x in changed('w1/integrate') if not ((x.startswith('docs/') and not x.startswith('docs/source/')) or x.startswith('.tickets/') or x == 'governance/project/bootstrap.md')]
    check('S2 writes only docs/**, .tickets/** and governance/project/bootstrap.md; the Charter is unchanged', not out and 'docs/charter/CHARTER_v5.md' not in changed('w1/integrate'), str(out))
else: print(f'SKIP S2 write scope — applies to branch s2/spec only; this is {branch or "a detached HEAD"}')
print('\nRESULT:', 'ALL PASS' if not fails else f'{len(fails)} FAIL')
sys.exit(1 if fails else 0)
