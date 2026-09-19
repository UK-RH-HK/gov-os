import statistics as st, yaml, json, collections
# Harness completion notifications: <usage><subagent_tokens/><tool_uses/><duration_ms/></usage>.
# Model: self-reported agent_model in each run report; dispatch: "default" = Agent tool model param omitted, "opus" = pinned.
R=[
# run, phase, role, ws, dispatch, self_model, sub_tokens, tools, dur_ms, outcome, findings_total, findings_blocking, claims_R, claims_partial, claims_not
("P2-AR-0001","audit-0 first pass","family-auditor","alpha","default","claude-opus-4-6",63277,116,1789127,"COMPLETED_NONCONFORMING",4,0,None,None,None),
("P2-AR-0002","audit-0 first pass","family-auditor","beta","default","claude-opus-4-6",69863,79,1692790,"COMPLETED_NONCONFORMING",4,0,None,None,None),
("P2-AR-0003","audit-0 first pass","family-auditor","gamma","default","claude-opus-4-6",64479,100,1650335,"COMPLETED_MODEL_DEVIATION",3,0,None,None,None),
("P2-AR-0004","audit-0 first pass","family-auditor","delta","default","claude-opus-4-6",69460,81,1630020,"COMPLETED_NONCONFORMING",4,0,None,None,None),
("P2-AR-0005","audit-0 first pass","family-auditor","epsilon","default","claude-opus-4-6",69715,74,1547584,"COMPLETED_NONCONFORMING",7,1,None,None,None),
("P2-AR-0006","audit-0 first pass","family-auditor","zeta","default","claude-opus-4-6",81169,89,1596989,"COMPLETED_NONCONFORMING",5,0,None,None,None),
("P2-AR-0008","audit-0 re-audit","family-auditor","epsilon","opus","claude-opus-5[1m]",678030,185,2958639,"COMPLETED",36,27,None,None,None),
("P2-AR-0009","audit-0 re-audit","family-auditor","beta","opus","claude-opus-5[1m]",955317,261,4332385,"COMPLETED",30,22,None,None,None),
("P2-AR-0010","audit-0 re-audit","family-auditor","gamma","opus","claude-opus-5[1m]",929426,219,4074693,"COMPLETED",36,19,None,None,None),
("P2-AR-0011","audit-0 re-audit","family-auditor","delta","opus","claude-opus-5[1m]",727452,179,3297020,"COMPLETED",26,17,None,None,None),
("P2-AR-0012","audit-0 re-audit","family-auditor","zeta","opus","claude-opus-5[1m]",772313,180,3602582,"COMPLETED",27,24,None,None,None),
("P2-AR-0013","audit-0 re-audit","family-auditor","alpha","opus","claude-opus-5[1m]",368601,285,4788608,"COMPLETED",25,7,None,None,None),
("P2-AR-0007","audit-0 synthesis","baseline-synthesis","all","opus","claude-opus-5[1m]",894062,156,4557126,"COMPLETED (REJECTED verdict)",10,8,None,None,None),
("P2-AR-0014","repair r1","repair-builder","WS-1/12","opus","claude-opus-5[1m]",644373,146,4264481,"COMPLETED_INTEGRATED",None,None,2,0,0),
("P2-AR-0015","repair r1","repair-builder","WS-2","opus","claude-opus-5[1m]",892479,286,8165545,"COMPLETED_INTEGRATED",None,None,4,0,0),
("P2-AR-0016","repair r1","repair-builder","WS-3","opus","claude-opus-5[1m]",244051,343,7942041,"COMPLETED_INTEGRATED",None,None,7,0,0),
("P2-AR-0017","repair r1","repair-builder","WS-4","opus","claude-opus-5[1m]",726000,208,5466288,"COMPLETED_INTEGRATED",None,None,4,0,0),
("P2-AR-0018","repair r1","repair-builder","WS-5","opus","claude-opus-5[1m]",679943,230,6401329,"COMPLETED_INTEGRATED",None,None,2,0,0),
("P2-AR-0019","repair r1","repair-builder","WS-6","opus","claude-opus-5[1m]",785452,212,5819461,"COMPLETED_INTEGRATED",None,None,5,0,0),
("P2-AR-0020","repair r1","repair-builder","WS-8","opus","claude-opus-5[1m]",928942,247,7179400,"COMPLETED_INTEGRATED",None,None,4,0,0),
("P2-AR-0021","repair r1","repair-builder","WS-9/11","opus","claude-opus-5[1m]",850682,249,7293431,"COMPLETED_INTEGRATED",None,None,3,1,0),
("P2-AR-0022","repair r1 integration","integration-builder","all","opus","claude-opus-5[1m]",865332,318,6201774,"COMPLETED_MERGED",None,None,None,None,None),
("P2-AR-0023","repair r2","repair-builder","WS-2","opus","claude-opus-5[1m]",936671,319,11130938,"COMPLETED_INTEGRATED",None,None,1,0,0),
("P2-AR-0024","repair r2","repair-builder","WS-3","opus","claude-opus-5[1m]",786274,266,6642001,"COMPLETED_INTEGRATED",None,None,10,1,1),
("P2-AR-0025","repair r2","repair-builder","WS-4","opus","claude-opus-5[1m]",449313,437,14012483,"COMPLETED_INTEGRATED",None,None,5,0,0),
("P2-AR-0026","repair r2","repair-builder","WS-5","opus","claude-opus-5[1m]",203868,365,11378082,"COMPLETED_INTEGRATED",None,None,4,0,0),
("P2-AR-0027","repair r2","repair-builder","WS-6","opus","claude-opus-5[1m]",804652,265,8334380,"COMPLETED_INTEGRATED",None,None,2,1,0),
("P2-AR-0028","repair r2","repair-builder","WS-7","opus","claude-opus-5[1m]",783088,222,8166069,"COMPLETED_INTEGRATED",None,None,5,0,0),
("P2-AR-0029","repair r2","repair-builder","WS-8","opus","claude-opus-5[1m]",918895,306,8124354,"COMPLETED_INTEGRATED",None,None,2,2,0),
("P2-AR-0030","repair r2","repair-builder","WS-9/11","opus","claude-opus-5[1m]",787654,226,5767082,"COMPLETED_INTEGRATED",None,None,5,0,0),
("P2-AR-0031","repair r2","repair-builder","WS-10","opus","claude-opus-5[1m]",877925,231,7433928,"COMPLETED_INTEGRATED",None,None,3,0,0),
("P2-AR-0032","repair r2 integration","integration-builder","all","opus","claude-opus-5[1m]",835855,284,4854843,"COMPLETED_MERGED",None,None,None,None,None),
("P2-AR-0034","repair r3","repair-builder","WS-3","opus","claude-opus-5[1m]",140375,309,11723323,"COMPLETED_AWAITING_INTEGRATION",None,None,13,3,1),
("P2-AR-0037","repair r3","repair-builder","WS-6","opus","claude-opus-5[1m]",808403,278,9475366,"COMPLETED_AWAITING_INTEGRATION",None,None,8,0,0),
("P2-AR-0038","repair r3","repair-builder","WS-7","opus","claude-opus-5[1m]",810731,286,8369009,"COMPLETED_AWAITING_INTEGRATION",None,None,5,0,0),
("P2-AR-0039","repair r3","repair-builder","WS-8","opus","claude-opus-5[1m]",825364,262,10531391,"COMPLETED_AWAITING_INTEGRATION",None,None,6,3,0),
("P2-AR-0040","repair r3","repair-builder","WS-9/11","opus","claude-opus-5[1m]",610209,203,8161394,"COMPLETED_AWAITING_INTEGRATION",None,None,5,0,0),
]
RUNNING=[("P2-AR-0033","repair r3","repair-builder","WS-2"),("P2-AR-0035","repair r3","repair-builder","WS-4"),("P2-AR-0036","repair r3","repair-builder","WS-5")]
def agg(rows):
    t=[r[6] for r in rows]; u=[r[7] for r in rows]; d=[r[8]/3.6e6 for r in rows]
    return {"agents":len(rows),"subagent_tokens_total":sum(t),"subagent_tokens_mean":round(st.mean(t)),"subagent_tokens_median":round(st.median(t)),
            "tool_calls_total":sum(u),"tool_calls_mean":round(st.mean(u),1),"tool_calls_median":st.median(u),
            "wall_clock_hours_total":round(sum(d),2),"wall_clock_hours_mean":round(st.mean(d),2),"wall_clock_hours_median":round(st.median(d),2)}
out={"by_model":{},"by_role":{},"by_phase":{},"by_workstream":{}}
for key,idx in (("by_model",5),("by_role",2),("by_phase",1),("by_workstream",3)):
    g=collections.defaultdict(list)
    for r in R: g[r[idx]].append(r)
    for k,v in sorted(g.items()): out[key][k]=agg(v)
out["all_completed"]=agg(R)
# yields
fp=[r for r in R if r[1]=="audit-0 first pass"]; ra=[r for r in R if r[1]=="audit-0 re-audit"]
out["finding_yield"]={"first_pass_default_model":{"findings":sum(r[10] for r in fp),"blocking":sum(r[11] for r in fp)},
 "re_audit_opus5":{"findings":sum(r[10] for r in ra),"blocking":sum(r[11] for r in ra)},
 "synthesis":{"own_findings":10,"own_blocking":8,"family_findings_reviewed":180,"confirmed":165,"corrected":15,"refuted":0,"blocking_total":134,"classes":52}}
bl=[r for r in R if r[12] is not None]
out["builder_claims"]={"items_claimed_repaired":sum(r[12] for r in bl),"items_partial":sum(r[13] for r in bl),"items_not_repaired":sum(r[14] for r in bl),
 "note":"builder claims only (Contract v3 O3); independent repair success rate NOT_OBSERVABLE until iteration-1 verification"}
print(json.dumps(out,indent=1))
json.dump({"rows":R,"running":RUNNING,"agg":out},open("/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/telemetry.json","w"))
