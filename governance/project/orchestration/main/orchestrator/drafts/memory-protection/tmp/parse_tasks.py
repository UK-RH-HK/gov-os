import re, sys, collections
path = sys.argv[1]
dumps = []
cur = None
pat = re.compile(r'^(\S+) \S+ kernel: \[\s*(\d+)\]\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(.*)$')
last_ts = None
for line in open(path, errors='replace'):
    m = pat.match(line)
    if not m:
        cur = None
        continue
    ts = m.group(1)
    if cur is None or ts != cur['ts'] and (cur['ts'][:16] != ts[:16]):
        cur = {'ts': ts, 'rows': []}
        dumps.append(cur)
    pid, uid, tgid, vm, rss, anon, file_, shm, pgt, swp, adj = map(int, m.groups()[1:12])
    cur['rows'].append(dict(pid=pid, uid=uid, vm=vm, rss=rss, anon=anon, file=file_, shm=shm, pgt=pgt, swp=swp, adj=adj, name=m.group(13).strip()))
P = 4096
for d in dumps:
    rows = d['rows']
    print('DUMP', d['ts'], 'tasks', len(rows))
    agg = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for r in rows:
        a = agg[r['name']]
        a[0] += 1
        a[1] += r['rss'] * P
        a[2] += r['swp'] * P
        a[3] += r['pgt']
        a[4] += 0
    tot_rss = sum(r['rss'] for r in rows) * P
    tot_swp = sum(r['swp'] for r in rows) * P
    print('  total rss %.2f GB swapents %.2f GB' % (tot_rss / 1e9, tot_swp / 1e9))
    for name, a in sorted(agg.items(), key=lambda kv: -kv[1][1])[:12]:
        print('  %-18s n=%5d rss=%.2f GB swap=%.2f GB pgt=%.2f GB' % (name, a[0], a[1] / 1e9, a[2] / 1e9, a[3] / 1e9))
    print('  biggest single processes (rss+swap+pgt, as the OOM killer scores it):')
    for r in sorted(rows, key=lambda r: -(r['rss'] + r['swp'] + r['pgt'] // P))[:14]:
        print('   pid %6d %-16s rss=%6.0f MB swap=%6.0f MB pgt=%5.0f MB adj=%d' % (r['pid'], r['name'][:16], r['rss'] * P / 1e6, r['swp'] * P / 1e6, r['pgt'] / 1e6, r['adj']))
    print('  non-zero adj:', [(r['pid'], r['name'], r['adj']) for r in rows if r['adj'] != 0][:20])
    # time of pid range of rg
    rg = [r['pid'] for r in rows if r['name'] == 'rg']
    if rg:
        print('  rg pid range', min(rg), max(rg))
