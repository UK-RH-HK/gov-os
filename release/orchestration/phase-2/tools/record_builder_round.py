"""Record a completed repair builder's outcome into its P2-AR run record (orchestrator tooling).
usage: record_builder_round.py <P2-AR-NNNN> <ws> "<orchestrator notes>" [r2|r3|r4]
Reads the builder's report and claims from its branch; writes an outcome block (notes JSON-quoted)."""
import json
import sys,subprocess,yaml,re
run,ws,notes=sys.argv[1],sys.argv[2],sys.argv[3]
RND=sys.argv[4] if len(sys.argv)>4 else 'r3'   # round prefix: r2, r3, ... (round 1 used no prefix)
br=f"phase2/repair-1-{RND}-{ws}"
g=lambda *a: subprocess.run(["git",*a],capture_output=True,text=True,check=True).stdout.strip()
rep=yaml.safe_load(g("show",f"{br}:release/orchestration/phase-2/AGENT_RUNS/{run}.report.yaml"))
tip=g("rev-parse",br)
pcd=re.search(r"product_code_digest: (\w+)",subprocess.run(["python3","release/orchestration/phase-2/tools/product_identity.py",br],capture_output=True,text=True).stdout).group(1)
claims=yaml.safe_load(g("show",f"{br}:release/capability-baseline/repair-1/{RND}-{ws}/claims.yaml"))
cl=claims.get("claims") or claims.get("classes") or claims.get("items") or claims
if isinstance(cl,dict): cl=[{"class":k,**(v if isinstance(v,dict) else {"status":v})} for k,v in cl.items()]
summ={str(c.get("item") or c.get("class") or c.get("id")):c.get("status") for c in cl} if isinstance(cl,list) else str(cl)[:200]
p=f"release/orchestration/phase-2/AGENT_RUNS/{run}.run.yaml"
t=open(p).read().replace("status: RUNNING\n",f"""status: COMPLETED_AWAITING_INTEGRATION
outcome:
  verdict: {rep['verdict']}
  work_commit: {rep['output']['commit']}
  branch_tip_commit: {tip}
  branch_product_code_digest: {pcd}
  agent_model_self_reported: {rep.get('agent_model')}
  claims: {summ}
  orchestrator_checks: {json.dumps(notes)}
""")
open(p,"w").write(t)
print(run,rep['verdict'],summ)
