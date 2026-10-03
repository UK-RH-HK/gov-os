"""Self-check of the Gov OS specification and Wave 1 plan (S1 stage 6, extended by the S2 specification change, DEC-155).

Read-only. Prints PASS, FAIL or SKIP per check and exits non-zero on any FAIL.

Run from anywhere:  python3 docs/plan/tools/validate_s1.py

Inputs inside the repository are always checked. Four checks compare against files outside it (the S1 workbench:
coverage matrix, architecture v0.3, register v0.12, the S1-A round-1 fingerprints) and one against `docs/source/`,
which is archived after S1-A closes. Those checks are SKIPped when their input is absent. Set GOV_OS_WORKBENCH to
point at the workbench (default: ~/gov-os-workbench).

Section 3e checks what the S2 change added (Contract v4.1, tickets W1-45…W1-48, DEC-150…DEC-162). Section 3f checks the
repair after the S2-A round-1 audit (S2A-F-01…F-10, DEC-163…DEC-171). Section 3g checks the repair after the round-2 audit
(S2A-F-11…F-16, DEC-172, DEC-173). Section 3h checks the fixes at the round-3 closure check (S2A-F-17, F-18, DEC-174).
The write-scope check of S1 (section 9) applies on branch
`s1/spec` only; on `s2/spec` the S2 write scope is checked instead.
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
        # the owner retired the s1a session (DEC-101): its PROMPT.md was renamed, content unchanged. The fallback is for that one file only (DEC-169).
        ret = os.path.join(W, 's1a', 'PROMPT.retired.md')
        if os.path.normpath(rel) == 'PROMPT.md' and not os.path.exists(fp) and os.path.exists(ret): fp = ret
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
carried = {'DEC-102': 'W1', 'DEC-103': 'W1', 'DEC-104': 'W2', 'DEC-105': 'W1', 'DEC-106': 'W1', 'DEC-136': 'W1', 'DEC-137': 'W1', 'DEC-158': 'W1', 'DEC-159': 'W1', 'DEC-160': 'W2',
           'DEC-163': 'W1', 'DEC-164': 'W2', 'DEC-165': 'W3', 'DEC-166': 'W2', 'DEC-167': 'W1', 'DEC-168': 'W1'}
lost = [d_ for d_, w_ in carried.items() if not any(d_ in cv['source'] and cv['wave'] == w_ for e, cv in cov.values())]
check('every carried decision (DEC-102..106, 136, 137, 158..160, 163..168) is the source of a covers item in its wave', not lost, str(lost))
check('installs unchanged (DEC-157): envelope keeps the DEC-083 sentence, CAP-25.b is untouched, worker roles never install system-wide',
      c['envelope']['tool_installs']['statement'].startswith('The orchestrator installs a tool only after the owner approves a decision package in chat') and 'Worker roles never install system-wide' in c['envelope']['tool_installs']['statement']
      and cov['CAP-25.b'][1]['item'].startswith('Orchestrator-only install on owner approval in chat') and cov['CAP-25.d'][1]['provider'] == ['W1-48'])
def T(n): return tk[n][1]
shape = {'W1-45': ('engineer', 'FULL', ['W1-05']), 'W1-46': ('engineer', 'FULL', ['W1-07', 'W1-47', 'W1-48']), 'W1-47': ('engineer', 'FULL', ['W1-45']), 'W1-48': ('orchestrator', 'LITE', ['W1-06'])}
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

# 3f. Repair after the S2-A round-1 audit (S2A-F-01..F-10; DEC-163..DEC-171; docs/changes/S2-CIT-E.md §6)
check('DEC-163..DEC-171 ACCEPTED (owner, 2026-10-03)', all(re.search(rf'### DEC-{n} .*\n- \*\*Status:\*\* ACCEPTED \(owner, 2026-10-03\)', reg) for n in range(163, 172)))
k45 = kp('W1-45')
citp_t, cite_t = open(citp).read(), open(cite).read()
check('F-01: W1-45 states that the W1-02 and W1-03 tests of the old orchestrator rule are revised by the test designer; both CIT records say so',
      'revised by the Independent Test Designer' in k45 and 'rewrite after implementation' in k45 and 'owner correction, DEC-156' in k45 and 'DEC-106' in T('W1-45')['sources']
      and all('no existing acceptance test is invalidated' not in t_ and 'revised by the Independent Test Designer' in t_ for t_ in (citp_t, cite_t))
      and 'for every role other than the orchestrator' in k45 and 'test design batch' in k45 and 'a record, not a containment finding' in k45
      and 'except the orchestrator (`CAP-58.e`)' in cov['CAP-58.a'][1]['item'] and 'a record, not a containment finding' in cov['CAP-58.e'][1]['item'] and 'DEC-171' in cov['CAP-58.e'][1]['source'] and 'DEC-171' in T('W1-45')['sources']
      and all('DEC-156' in open(tk[t_][0]).read() for t_ in ('W1-02', 'W1-03')))
f47 = ' '.join(T('W1-47')['kpis']['failure'])
HO = 'governance/project/held-out.yaml'
check('F-04: W1-47 tests the committed deny rule statically, from the value in held-out.yaml, and the guard against a stand-in; no test names the oracle; the launcher takes the path from the same file',
      all(x in k47 for x in ('checks the committed rule statically', 'its presence and its exact path', 'the test file carries no literal path', 'tested against a stand-in path, never the qualification oracle', HO))
      and 'Any tool call whose input names the oracle path is allowed, whatever the tool' in f47 and 'An acceptance test of this ticket reads or names the qualification oracle' in f47 and HO in T('W1-47')['allowed_paths']
      and all(x in k46 for x in ('the test uses a stand-in directory, never the qualification oracle', 'reads or names the qualification oracle', HO)) and 'W1-47' in T('W1-46')['depends_on'] and HO in c49)
src_self = open(os.path.abspath(__file__)).read()
check('F-08: the fingerprint rename fallback applies to PROMPT.md only, and the S2 write-scope check excludes docs/SOURCES.md (DEC-169)',
      "os.path.normpath(rel) == 'PROMPT.md' and not os.path.exists(fp)" in src_self and "fp[:-3] + '.retired" + ".md'" not in src_self and src_self.count("x != 'docs/SOURCES.md'") >= 3)
def cv_(i): return cov[i][1]
check('DEC-163: a minimal research role in the Wave 1 roster, delivered by W1-46; installs only inside its experiment folder',
      cv_('CAP-22.d')['wave'] == 'W1' and cv_('CAP-22.d')['provider'] == ['W1-46'] and cv_('CAP-25.e')['provider'] == ['W1-46'] and 'write fence' in cv_('CAP-25.e')['item'] and 'DEC-158' in cv_('CAP-22.d')['item']
      and all(x in k46 for x in ('minimal research role', "sandbox's write fence", 'A research session installs system-wide, or writes to a path that existed at launch outside its experiment folder')) and '.claude/agents/research.md' in T('W1-46')['allowed_paths']
      and 'DEC-163' in c['envelope']['tool_installs']['statement'] and 'full research lifecycle (CAP-32) stays W3' in cv_('CAP-22.d')['item'] and cap['CAP-32']['wave'] == 'W3')
check('DEC-164: subagents in a sandboxed worker and excludedCommands are open residuals in EXP-002 (W2); the launcher sets no excludedCommands',
      all(x in cv_('CAP-61.f')['item'] for x in ('subagents inside a sandboxed worker session', '`excludedCommands`', 'EXP-002')) and cv_('CAP-61.f')['wave'] == 'W2'
      and 'sets no `excludedCommands`' in cv_('CAP-61.a')['item'] and 'carry no excludedCommands' in k46 and 'carry an excludedCommands entry' in k46
      and all(x in boot for x in ('Subagents inside a sandboxed worker session', '`excludedCommands`', 'EXP-002', 'DEC-164')) and 'EXP-002' in wbs[wbs.index('## 6. Wave 2'):])
c41 = {i: cv_(i) for i in cov if i.startswith('CAP-41.')}
check('DEC-165: the lite upstream lesson loop is Wave 3 (CAP-41.g..j, CAP-45.b, CAP-58.g); CAP-41.e keeps the full loop a non-goal',
      all(c41[f'CAP-41.{x}']['wave'] == 'W3' and 'DEC-165' in c41[f'CAP-41.{x}']['source'] for x in 'ghij') and c41['CAP-41.e']['wave'] == 'NONE'
      and 'severity (low, medium, high or critical)' in c41['CAP-41.f']['item'] and all(x in c41['CAP-41.g']['item'] for x in ('~/gov-os-lessons-inbox/', 'gitleaks', 'no product code, data or secrets'))
      and 'decision package' in c41['CAP-41.h']['item'] and 'release' in c41['CAP-41.i']['item'] and 'never leave their repository' in c41['CAP-41.j']['item']
      and cv_('CAP-45.b')['wave'] == 'W3' and 'gov doctor' in cv_('CAP-45.b')['item'] and cv_('CAP-58.g')['wave'] == 'W3' and '~/gov-os-lessons-inbox/' in cv_('CAP-58.g')['item']
      and cap['CAP-41']['wave'] == 'W1' and 'DEC-165' in wbs[wbs.index('## 7. Wave 3'):])
check('DEC-166, DEC-167: gov discover is W2; a plain-language impact question runs a proposal plus gov closure in W1 (W1-35) and gov impact in W2',
      cv_('CAP-32.d')['wave'] == 'W2' and 'gov discover' in cv_('CAP-32.d')['item'] and cv_('CAP-33.f')['provider'] == ['W1-35'] and 'gov closure' in cv_('CAP-33.f')['item']
      and cv_('CAP-33.g')['wave'] == 'W2' and 'gov impact' in cv_('CAP-33.g')['item'] and 'DEC-166' in wbs[wbs.index('## 6. Wave 2'):] and 'W1-20' in anc('W1-35'))
k31 = kp('W1-31')
check('F-02, F-03: a research session runs as GOV_ROLE=research; its network grant comes from the launcher profile; its write fence inside the repository is a generated deny list, with a sibling-directory test',
      'GOV_ROLE=research' in k46 and 'GOV_ROLE=research' in cv_('CAP-22.d')['item'] and "launcher's network profile" in cv_('CAP-58.b')['item'] and "launcher's network profile" in kp('W1-33')
      and all(x in k46 for x in ('generates at launch an Edit deny rule for every other path of the repository', 'Bash write to a sibling directory inside the repository fails')) and 'generates at launch' in cv_('CAP-61.c')['item'])
check('F-06, F-07: bootstrap.md keeps the outside-the-repository qualifier on the install misses; the sandbox cost is in ADR-0002 and W1-31',
      all(x in boot for x in ('for installs that write outside the repository', 'A research session can install', '+3,250 input tokens')) and all(x in adr2 for x in ('+65 ms per Bash command', '+3,250 input tokens')) and '3,250 input tokens' in k31
      and 'decided at the Wave 1 exit, using measured figures (DEC-170)' in k31 and 'DEC-170' in adr2 and 'not governance tokens' not in k31 + adr2)
check('F-09, F-10: W1-30 and W1-31 are re-estimated and the WBS says the other new KPIs fit; W1-48 records bubblewrap and socat',
      (T('W1-30')['est_loc'], T('W1-31')['est_loc']) == (220, 150) and 'fit their existing estimates' in wbs and 'bubblewrap 0.9.0 and socat 1.8.0.0' in kp('W1-48') and 'DEC-141' in T('W1-48')['sources'])
check('DEC-168: scope and severity are in the Wave 1 lesson schema (CAP-41.f, W1-08); the loop stays Wave 3',
      cv_('CAP-41.f')['wave'] == 'W1' and cv_('CAP-41.f')['provider'] == ['W1-08'] and 'severity (low, medium, high or critical)' in kp('W1-08') and 'severity' in kp('W1-44'))
ch = open(f'{R}/docs/charter/CHARTER_v5.md').read()
check('Charter v5 carries the two changes the decisions require: the research role in the Wave 1 roster (DEC-163) and the lesson-loop non-goal row (DEC-165)',
      'research, in a minimal form (DEC-163)' in ch and 'reversed for framework lessons only by DEC-165' in ch and {'DEC-163', 'DEC-165'} <= set(fms[f'{R}/docs/charter/CHARTER_v5.md']['decisions']))
check('ADR-0002 carries the research role, EXP-002, gov discover and the lesson loop', all(x in adr2 for x in ('DEC-163', 'EXP-002', 'gov discover', '~/gov-os-lessons-inbox/', 'DEC-138…DEC-174')) and 'DEC-167' in adr2fm['decisions'])

# 3g. Repair after the S2-A round-2 audit (S2A-F-11..F-16; DEC-172, DEC-173; docs/changes/S2-CIT-E.md §7)
check('DEC-172, DEC-173 ACCEPTED (owner, 2026-10-03)', all(re.search(rf'### DEC-{n} .*\n- \*\*Status:\*\* ACCEPTED \(owner, 2026-10-03\)', reg) for n in (172, 173)))
citp_t, cite_t = open(citp).read(), open(cite).read()
k46, k47, k31 = kp('W1-46'), kp('W1-47'), kp('W1-31')
INST = ('pip', 'pip3', 'python -m pip', 'python3 -m pip', 'uv', 'npm install', 'cargo install', 'apt', 'apt-get', 'curl', 'wget')
perm = json.load(open(f'{R}/.claude/settings.json')).get('permissions', {})
left = [x for x in perm.get('ask', []) if any(x == f'Bash({i}:*)' for i in INST)]
check('DEC-172 (F-11): W1-47 removes the install and download ask rules from the committed settings (CAP-25.f); W1-46 tests its install with the committed settings loaded; the rules are gone once W1-47 is closed',
      cv_('CAP-25.f')['wave'] == 'W1' and cv_('CAP-25.f')['provider'] == ['W1-47'] and 'DEC-172' in cv_('CAP-25.f')['source'] and 'W1-47' in cap['CAP-25']['provider']
      and all(x in k47 for x in ('carries no install or download ask rule', 'Bash(sudo:*) deny rule', 'still carries an install or download ask rule')) and 'DEC-172' in T('W1-47')['sources']
      and all(x in k46 for x in ('meets no settings ask rule', "runs with the repository's committed settings loaded", 'is stopped by a settings ask rule')) and 'DEC-172' in T('W1-46')['sources']
      and 'W1-47' in T('W1-46')['depends_on'] and 'The settings ask rules are withdrawn (DEC-172)' in boot and 'DEC-172' in adr2 and 'DEC-172' in open(tk['W1-04'][0]).read()
      and (T('W1-47')['status'] != 'closed' or (not left and 'Bash(sudo:*)' in perm.get('deny', []))), str(left))
EXC = 'except the research role, inside its experiment folder (DEC-163)'
check('DEC-173, F-12: the Charter, ADR-0001, ADR-0002 §6 and W1-33 name the research exception to "only the orchestrator installs"',
      EXC in ch and 'DEC-173' in fms[f'{R}/docs/charter/CHARTER_v5.md']['decisions'] and re.search(r'denied for every other role, except the research role inside\s+its experiment folder \(DEC-163\)', adr1)
      and re.search(r'the only role that installs tools, except the research role inside its experiment folder\s+\(DEC-163\)', adr2) and 'except the research role inside its experiment folder (DEC-163)' in kp('W1-33'))
LATE, c61 = "guard's per-ticket allow-list", cv_('CAP-61.c')['item']
check('F-13: the deny list is computed at launch; a path created later is covered by the guard\'s per-ticket allow-list; the exceptions (.git/, glob characters) are listed, with a test of a later path',
      all(x in k46 for x in ('the deny list is computed at launch', LATE, '.git/', 'a new path created after launch', 'leaves out exactly the named exceptions', 'neither refused by the guard nor reported by the containment check'))
      and all(x in c61 for x in ('the deny list is computed at launch', LATE, '`.git/`')) and LATE in cv_('CAP-25.e')['item']
      and all(x in t_ for t_ in (adr2, boot) for x in (LATE, '`.git/`', 'computed at launch')) and 'computed at launch' in wbs)
HIST = 'register entry DEC-067 names the directory historically'
check('F-14: the oracle path is held in held-out.yaml and in the committed deny rule built from it; DEC-067 names the directory historically; the owner confirms the value at close',
      all('held in one file' not in t_ and 'the one file that holds' not in t_ for t_ in (c49, adr2, boot, open(tk['W1-47'][0]).read()))
      and all('committed deny rule built from it' in t_ for t_ in (cov['CAP-49.c'][1]['item'], adr2, k47)) and all(re.search(r'register\s+entry DEC-067 names the directory historically', t_) for t_ in (cov['CAP-49.c'][1]['item'], adr2, boot, open(tk['W1-47'][0]).read()))
      and 'the owner confirms at close' in k47)
check('F-15: DEC-170 is a Wave 1 covers item of the telemetry capability (CAP-40.d), delivered by W1-31',
      cv_('CAP-40.d')['wave'] == 'W1' and cv_('CAP-40.d')['provider'] == ['W1-31'] and 'DEC-170' in cv_('CAP-40.d')['source'] and 'DEC-170' in cap['CAP-40']['sources'] and '[CAP-40.d]' in k31 and 'separate line' in cv_('CAP-40.d')['item'])
check('F-16: S2-CIT-P §6 lists DEC-170 and DEC-171, and §7 the round-2 repair; the WBS header cites DEC-102…DEC-174; S2-CIT-E §7 records DEC-172 and DEC-173',
      all(f'| {d_} ' in citp_t for d_ in ('DEC-170', 'DEC-171', 'DEC-172 (DP-3, S2A-F-11)', 'DEC-173 (DP-4, S2A-F-12)')) and 'DEC-102…DEC-174' in wbs and 'DEC-172' in fms[f'{R}/docs/plan/WAVE_1_WBS.md']['decisions']
      and '## 7. Repair after the S2-A round-2 audit' in cite_t and {'DEC-172', 'DEC-173'} <= set(frontmatter(cite)['decisions_recorded']) and 'Five lines' in cite_t)

# 3h. Fixes at the S2-A round-3 closure check (S2A-F-17, F-18, O-12; DEC-174; docs/changes/S2-CIT-E.md §8)
UVF = ('uv add', 'uv sync', 'uv run --with', 'uvx')
f46 = T('W1-46')['kpis']['failure']
check('DEC-174: ACCEPTED; W1-47 extends the guard\'s install rule to uv add, uv sync, uv run --with and uvx (CAP-25.g); the research exception still applies',
      re.search(r'### DEC-174 .*\n- \*\*Status:\*\* ACCEPTED \(owner, 2026-10-03\)', reg) and cv_('CAP-25.g')['wave'] == 'W1' and cv_('CAP-25.g')['provider'] == ['W1-47'] and 'DEC-174' in cv_('CAP-25.g')['source']
      and all(f'`{x}`' in cv_('CAP-25.g')['item'] for x in UVF) and any('[CAP-25.g]' in l and all(x in l for x in UVF) and 'DEC-163' in l for l in T('W1-47')['kpis']['success'])
      and 'DEC-174' in T('W1-47')['sources'] and 'tests/unit/install/**' in T('W1-47')['allowed_paths'] and 'DEC-174' in k46 and all(x in t_ for t_ in (adr2, wbs, boot) for x in ('DEC-174', '`uvx`')))
check('F-18: W1-46 failure KPI 4 covers a system-wide install and a path that existed at launch; the later-path case is failure KPI 5',
      f46[3] == 'A research session installs system-wide, or writes to a path that existed at launch outside its experiment folder' and 'created after launch' in f46[4] and 'neither refused by the guard nor reported' in f46[4])
check('F-17, O-12: bootstrap.md and S2-CIT-E record the commands that lose their settings prompt from a run of the classifier; .git/hooks and .git/config stay protected by the sandbox',
      all('201 commands' in t_ and '159' in t_ and 'run --with-requirements' in t_ and 'round3-classifier-run' in t_ for t_ in (boot, cite_t)) and 'from a run of the classifier' in boot and 'not a reading' in cite_t
      and '`.git/hooks` and `.git/config` stay protected' in boot and "aren't seen by the containment check" in boot and '## 8. Fixes at the S2-A round-3 closure check' in cite_t and 'DEC-174' in frontmatter(cite)['decisions_recorded'])

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
    out = [x for x in changed('w1/integrate') if not ((x.startswith('docs/') and not x.startswith('docs/source/') and x != 'docs/SOURCES.md') or x.startswith('.tickets/') or x == 'governance/project/bootstrap.md')]
    num = subprocess.run(['git', '-C', R, 'diff', '--numstat', 'w1/integrate', '--', 'docs/charter/CHARTER_v5.md'], capture_output=True, text=True).stdout.split()
    added = [l[1:] for l in subprocess.run(['git', '-C', R, 'diff', '-U0', 'w1/integrate', '--', 'docs/charter/CHARTER_v5.md'], capture_output=True, text=True).stdout.split('\n') if l.startswith('+') and not l.startswith('+++')]
    marks = ('decisions: [', 'research, in a minimal form (DEC-163)', 'research, with the full research lifecycle', 'reversed for framework lessons only by DEC-165', EXC)
    which = sorted(next((i for i, m_ in enumerate(marks) if m_ in l), -1) for l in added)
    check('S2 writes only docs/**, .tickets/** and governance/project/bootstrap.md; the Charter changes five lines only, each one named (DEC-163, DEC-165, DEC-173)', not out and num[:2] == ['5', '5'] and which == [0, 1, 2, 3, 4], str(out) + ' ' + str(num[:2]) + ' ' + str(which))
else: print(f'SKIP S2 write scope — applies to branch s2/spec only; this is {branch or "a detached HEAD"}')
print('\nRESULT:', 'ALL PASS' if not fails else f'{len(fails)} FAIL')
sys.exit(1 if fails else 0)
