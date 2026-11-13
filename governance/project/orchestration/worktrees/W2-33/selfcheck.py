import re,os,sys,glob
R='template/governance/kernel/roles/'
files=sorted(glob.glob(R+'*'))
print(len(files),[os.path.basename(f) for f in files])
assert all(f.endswith('.md') for f in files) and len(files)==9
WORK="- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are ready, through gov accept; the QA engineer alone reads both."
ONE="- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works in its own tests worktree, merged by the lead."
MODEL=r"claude(?:-[a-z0-9]+)+"
VER=re.compile(r"- \*\*Version:\*\* (\d+\.\d+\.\d+)")
DEF=re.compile(rf"- \*\*Launch default:\*\* model ({MODEL}), effort (low|medium|high|xhigh|max)")
SK=re.compile(r"- \*\*Skills:\*\* ([a-z0-9-]+(?:, [a-z0-9-]+)*)")
ENT=rf"model {MODEL}, effort (?:low|medium|high|xhigh|max)"
CR=re.compile(rf"- \*\*Launch by criticality:\*\* C3 {ENT}; C2 {ENT}(?: on FULL, {ENT} otherwise)?; C1 {ENT}; C0 {ENT}")
skills=set(os.listdir('template/governance/kernel/skills'))|set(os.listdir('template/governance/kernel/skills/superpowers'))
exp={'orchestrator':('claude-opus-5-5',0),'ticket-lead':('claude-opus-5-5',0),'senior-engineer':('claude-opus-5-5',0),
'engineer':('claude-sonnet-5-5',1),'independent-test-designer':('claude-sonnet-5-5',1),'qa-engineer':('claude-sonnet-5-5',1),
'independent-auditor':('claude-opus-5-5',0),'product-spec':('claude-sonnet-5-5',0),'research':('claude-sonnet-5-5',0)}
def one(lines,head,form,name,req=True):
    f=[l for l in lines if l.lstrip().startswith(head)]
    if not f:
        assert not req,(name,head); return None
    assert len(f)==1 and form.fullmatch(f[0]),(name,head,f); return form.fullmatch(f[0])
bad=0
for f in files:
    n=os.path.basename(f)[:-3]; t=open(f).read(); L=t.split('\n')
    m=one(L,'- **Version:**',VER,n); d=one(L,'- **Launch default:**',DEF,n)
    em,cr=exp[n]; assert d.group(1)==em and d.group(2)=='high',(n,d.groups())
    c=one(L,'- **Launch by criticality:**',CR,n,bool(cr))
    s=one(L,'- **Skills:**',SK,n)
    for k in s.group(1).split(', '): assert k in skills,(n,k)
    assert L.count('- **Model tier:** see Launch default')==1 and sum(l.startswith('- **Model tier:**') for l in L)==1,n
    assert L.count(WORK)==1 and L.count(ONE)==1,n
    assert not re.search(r'D-10|through-D',t),n
    print(n,m.group(1),d.groups(),s.group(1))
tl=open(R+'ticket-lead.md').read()
prose='\n'.join(l for l in tl.split('\n') if not re.match(r'- \*\*(Version|Launch default|Launch by criticality|Model tier):',l))
for pat in [r'W[12]-\d',r'DAEO-',r'\bw[12]/',r'/home/',r'tests/acceptance',r'\bpython|pytest|\.py\b|\.md\b|\.yaml|\.json',r'claude|Opus|Sonnet|Haiku',r'\d+\.\d+\.\d+']:
    h=re.findall(pat,prose); print('ticket-lead',pat,h); assert not h
for n in ('ticket-lead','senior-engineer','qa-engineer'):
    t=open(R+n+'.md').read()
    for h in {'ticket-lead':['Reads','Writes','Handover','Allowed paths','Handoff format'],'senior-engineer':['Reads','Writes','Skills','Launch default','Brief contents','Handover'],'qa-engineer':['Per stream','Moderator','Wave 3 row','Verdict','Rounds','Allowed paths','Tools']}[n]:
        assert len(re.findall(r'^- \*\*%s:\*\*'%h,t,re.M))==1,(n,h)
o=open(R+'orchestrator.md').read()
assert not re.search(r'(?im)^#+ .*ticket lead',o); print('ticket lead heading lines',len(re.findall(r'(?i)the ticket lead',o)))
for p in [r'asks? on (every|each|all)',r'(every|each|all) install',r'prompts? on']:
    assert not re.search(p,o,re.I),p
assert 'coordination_ticket' in o and 'GOV_TICKET' in o and 'ticket-lead.md' in o
print('OK')
