import subprocess, yaml, re, sys
files = subprocess.check_output(['git','diff','--name-only'],text=True).split()
def front(t):
    return yaml.safe_load(t.split('---')[1])
def items(f):
    k=f.get('kpis') or {}
    out=[]
    for fld in ('success','failure'):
        for it in (k.get(fld) or []):
            out.append(it if isinstance(it,str) else str(it))
    return out
bad=0; tot=0; changed=0
for p in files:
    old=subprocess.check_output(['git','show','HEAD:'+p],text=True)
    new=open(p).read()
    fo,fn=front(old),front(new)
    # other front matter fields unchanged
    for k in set(fo)|set(fn):
        if k!='kpis' and fo.get(k)!=fn.get(k): print('FIELD CHANGED',p,k); bad+=1
    # body unchanged
    if old.split('---',2)[2]!=new.split('---',2)[2]: print('BODY CHANGED',p); bad+=1
    io,inn=items(fo),items(fn)
    if len(io)!=len(inn): print('COUNT',p,len(io),len(inn)); bad+=1; continue
    for a,b in zip(io,inn):
        tot+=1
        if a==b: continue
        changed+=1
        tok=lambda s: re.findall(r"\w+|[^\w\s]",s)
        ta,tb=tok(a),tok(b); i=0
        for t in tb:
            if i<len(ta) and t==ta[i]: i+=1
        # ignore sentence punctuation tokens
        miss=[t for t in ta[i:] ]
        if 'Verify' not in b or i<len(ta) and any(re.match(r'\w',t) for t in ta[i:]):
            print('REWORD?',p,a[:60],'|',miss[:6]); bad+=1
print('files',len(files),'items',tot,'changed',changed,'bad',bad)
