import json, sys, collections
rows=[json.loads(l) for l in open(sys.argv[1])]
c=collections.Counter()
for r in rows:
    w=str(r['what']); t=r['tool']
    if t in('Read','Write','Edit') and w.startswith('/tmp/gov-os-emg-'): c['emg',t,r['at'][:10]]+=1
    if t in('Read','Write','Edit') and w.startswith('/tmp/claude-1000/-home-usain/'): c['mistake',t,r['at'][:10]]+=1
    if t=='Monitor': c['monitor',r['session'][:8],r['at'][:10], r['outcome']]+=1
for k,v in sorted(c.items()): print(v,k)
print(sum(v for k,v in c.items() if k[0]=='emg'), sum(v for k,v in c.items() if k[0]=='mistake'), sum(v for k,v in c.items() if k[0]=='monitor'))
