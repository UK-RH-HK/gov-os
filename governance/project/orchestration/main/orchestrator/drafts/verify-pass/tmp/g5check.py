import sys, yaml, subprocess, re
for t in sys.argv[1:]:
    p=f'.tickets/DAEO-{t}.md'
    txt=open(p).read()
    fm=txt.split('---')[1]
    d=yaml.safe_load(fm)
    k=d['kpis']
    miss=[]
    n=0
    for f,pre in (('success','S'),('failure','F')):
        for i,x in enumerate(k[f],1):
            n+=1
            if not re.search(r'Verify:\s*\S', x if isinstance(x,str) else str(x)): miss.append(f'{pre}{i}')
    r=subprocess.run(['gov','brief','lead',f'DAEO-{t}','--run','tests'],capture_output=True,text=True)
    codes=sorted(set(re.findall(r'gov brief: ([A-Z_]+)',r.stdout+r.stderr))-{'BRIEF_NOT_READY'})
    print(t,'lines',n,'noverify',miss,codes)
