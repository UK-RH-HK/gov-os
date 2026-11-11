import re,sys,collections
pat = re.compile(r'^(\S+) \S+ kernel: \[\s*(\d+)\]\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(.*)$')
first=True; S=collections.Counter(); n=0; hist=collections.Counter()
for line in open(sys.argv[1],errors='replace'):
    m=pat.match(line)
    if not m: 
        if n and first: first=False
        continue
    if not first: break
    g=m.groups(); pid=int(g[1]); vm,rss,anon,file_,shm,pgt,swp,adj=map(int,g[4:12]); name=g[12].strip()
    if name!='rg': continue
    n+=1; S['vm']+=vm; S['rss']+=rss; S['anon']+=anon; S['file']+=file_; S['shm']+=shm; S['pgt']+=pgt; S['swp']+=swp
    hist[rss//1000]+=1
print(n, {k:(v*4096/1e9 if k!='pgt' else v/1e9) for k,v in S.items()})
print(sorted(hist.items())[:12])
