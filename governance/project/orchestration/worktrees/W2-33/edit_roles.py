import re
R='/home/usain/gov-os-worktrees/W2-33/template/governance/kernel/roles/'
WORK="- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are ready, through gov accept; the QA engineer alone reads both."
ONE="- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works in its own tests worktree, merged by the lead."
O,S,H="claude-opus-5-5","claude-sonnet-5-5","claude-haiku-5-5"
def crit(c3,c2,c1,c0):
    return "- **Launch by criticality:** C3 model %s, effort high; C2 model %s, effort high; C1 model %s, effort high; C0 model %s, effort low"%(c3,c2,c1,c0)
spec={
 'engineer':('1.1.0',S,crit(O,S,S,H),'test-driven-development, systematic-debugging, verification-before-completion, retrieval'),
 'independent-test-designer':('1.1.0',S,crit(O,S,S,H),'test-design, retrieval'),
 'independent-auditor':('1.1.0',O,None,'audit, retrieval'),
 'product-spec':('1.1.0',S,None,'planning, change, retrieval'),
 'research':('1.1.0',S,None,'discovery, retrieval'),
}
for role,(ver,model,cr,skills) in spec.items():
    p=R+role+'.md'
    s=open(p).read()
    lines=s.split('\n')
    # model tier line (single line)
    i=next(k for k,l in enumerate(lines) if l.startswith('- **Model tier:**'))
    lines[i]='- **Model tier:** see Launch default'
    # insert block before Purpose
    j=next(k for k,l in enumerate(lines) if l.startswith('- **Purpose:**'))
    block=['- **Version:** '+ver,'- **Launch default:** model %s, effort high'%model]
    if cr: block.append(cr)
    block+=['- **Skills:** '+skills,'- **Model tier:** see Launch default',WORK,ONE]
    del lines[i]
    j=next(k for k,l in enumerate(lines) if l.startswith('- **Purpose:**'))
    lines[j:j]=block
    open(p,'w').write('\n'.join(lines))
