import json,re,collections,datetime,statistics as st,os,sys
T="/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/tasks/"
RUNS={"P2-AR-0001":"acd625f1a7a02cb66","P2-AR-0002":"a580c60bcf9ca053c","P2-AR-0003":"ac1af56f407a4d313","P2-AR-0004":"aed59613a824f71df","P2-AR-0005":"a8118e506a90cdc2c","P2-AR-0006":"add097cec84312ca7",
"P2-AR-0008":"a1756bd922dbe5367","P2-AR-0009":"af1da13c49e22af80","P2-AR-0010":"af768351f17720c81","P2-AR-0011":"aba7690f08aab7801","P2-AR-0012":"ab0d8137efc17ee91","P2-AR-0013":"a2d82e6872a879b2a","P2-AR-0007":"a4393f7b0db79b48e",
"P2-AR-0014":"a2e4803e60a8edf30","P2-AR-0015":"ac628e58e21bb0577","P2-AR-0016":"a3881a55c191801b3","P2-AR-0017":"a7e33ee0f2348afb4","P2-AR-0018":"ac5d7fa8516f7e05a","P2-AR-0019":"a16382040908bae85","P2-AR-0020":"a394829b1c1a440cd","P2-AR-0021":"acb0161949db70435","P2-AR-0022":"ab4a7b05becdea5a7",
"P2-AR-0023":"a7694899cc43c0175","P2-AR-0024":"a4b5ea2b0de4dff36","P2-AR-0025":"af7e4a0a21e0aa837","P2-AR-0026":"a0e2b6942b8020feb","P2-AR-0027":"a65c1faf61e0b8b6c","P2-AR-0028":"a0883a7a3aaa34d16","P2-AR-0029":"a3eb955765a5ec45c","P2-AR-0030":"a3b970e8feee83c6a","P2-AR-0031":"ac3105c25f7eab01d","P2-AR-0032":"a4aae03844d0969ff",
"P2-AR-0034":"a52181cae6b866a94","P2-AR-0037":"a6d196e7ec614c7f9","P2-AR-0038":"acc945cb3b9180702","P2-AR-0039":"a540621cf27a048b1","P2-AR-0040":"af05d534b83631800"}
CONTRACT=re.compile(r"Governance_OS_Capability_Acceptance_Contract_v3\.md|GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3\.md")
GATES=[("A",130,179),("B",182,203),("C",207,302),("D",305,357),("E",360,393),("F",396,438),("G",441,455),("H",458,530),("I",533,591),("J",594,617),("K",620,651),("L",654,684),("M",687,712),("N",715,747),("O",749,809),("P",812,839),("Q",842,867),("R",870,891),("S",894,951),("T",954,973),("U",976,1009),("V",1012,1062),("W",1066,1194),("PREQUAL",1197,1256),("HEAD",1,129)]
def cat_path(p):
    p=p or ""
    if CONTRACT.search(p): return "contract_v3"
    if re.search(r"DYNAMIC_AGENTIC|GOVERNANCE_OS_ADOPTION|GOVERNANCE_OS_RELEASE",p): return "governing_docs"
    if "release/orchestration/phase-2/HANDOFFS" in p or "PHASE-2-FROZEN" in p or "AGENT_RUNS/README" in p: return "handoffs_protocol"
    if "release/orchestration" in p: return "orchestration_state"
    if "release/capability-baseline/audit-0" in p: return "audit0_evidence"
    if "release/capability-baseline/repair-1" in p: return "repair_evidence"
    if re.search(r"release/(verification|root-of-trust)",p): return "phase1_evidence"
    if re.search(r"(^|/)(runtime|cli)/src",p): return "product_source"
    if re.search(r"(^|/)tests/",p): return "product_tests"
    if re.search(r"(^|/)(framework|migrations|capabilities|tools|fixtures)/",p): return "kernel_payload_fixtures"
    if re.search(r"(^|/)(spec|docs)/",p): return "spec_docs"
    if re.search(r"/tmp/|scratch|p2-|probe",p): return "scratch_probe_outputs"
    return "other"
def cat_bash(cmd):
    c=cmd or ""
    if re.search(r"\bgit\s+(log|show|diff|blame|rev-list|cat-file)\b",c): return "git_history"
    if re.search(r"\bcargo\s+(test|build|clippy|fmt|run)\b",c): return "build_test"
    if re.search(r"(^|[\s/])(gov)(\s|$)|target/(release|debug)/gov|RUN-ALL|run-all|\.sh\b|python3?\s+[^|]*\.py",c): return "execute_probe"
    m=re.findall(r"[\w./-]+\.(?:rs|md|yaml|yml|json|py|toml|txt|out|sh|jsonl)",c)
    if re.search(r"\b(cat|sed|head|tail|grep|rg|awk|wc|less|nl)\b",c) and m:
        cats=collections.Counter(cat_path(x) for x in m)
        return "read:"+cats.most_common(1)[0][0]
    if re.search(r"\b(grep|rg|find|ls)\b",c): return "search_listing"
    return "other_bash"
def contract_ranges(inp,name):
    s=json.dumps(inp)
    if not CONTRACT.search(s): return []
    if name=="Read":
        off=inp.get("offset") or 1; lim=inp.get("limit") or 2000
        return [(off,off+lim-1)]
    rs=[(int(a),int(b)) for a,b in re.findall(r"sed\s+-n\s+['\"]?(\d+),(\d+)p",s)]
    if rs: return rs
    if re.search(r"\b(cat|less)\b",s): return [(1,1256)]
    if re.search(r"\bgrep\b",s): return [("grep",)]
    return [("other",)]
def ts(x): return datetime.datetime.fromisoformat(x.replace("Z","+00:00"))
out={}
for run,aid in RUNS.items():
    reqs={}; tool_cat={}; tool_name={}; res_chars=collections.Counter(); calls=collections.Counter(); contract=[]; files_read=collections.Counter()
    model=collections.Counter(); effort=collections.Counter(); order=[]; tool_time=0.0; last_asst_ts={}; model_time=0.0; prev_user_ts=None
    thinking_tokens=0
    for line in open(T+aid+".output"):
        d=json.loads(line); typ=d.get("type")
        if typ=="assistant":
            m=d["message"]; rid=d.get("requestId") or m.get("id")
            u=m.get("usage") or {}
            ctx=(u.get("input_tokens") or 0)+(u.get("cache_read_input_tokens") or 0)+(u.get("cache_creation_input_tokens") or 0)
            r=reqs.setdefault(rid,{"ctx":0,"out":0,"t":d["timestamp"]})
            r["ctx"]=max(r["ctx"],ctx); r["out"]=max(r["out"],u.get("output_tokens") or 0)
            if rid not in order: order.append(rid)
            model[m.get("model")]+=1; effort[d.get("effort")]+=1
            otd=u.get("output_tokens_details") or {}
            for b in m.get("content",[]):
                if b.get("type")=="tool_use":
                    nm=b.get("name"); inp=b.get("input") or {}
                    if nm=="Bash": c=cat_bash(inp.get("command"))
                    elif nm=="Read": c="read:"+cat_path(inp.get("file_path")); files_read[inp.get("file_path")]+=1
                    elif nm in("Grep","Glob"): c="search_listing"
                    elif nm in("Write","Edit","NotebookEdit"): c="write_edit"
                    else: c="other_tool"
                    tool_cat[b["id"]]=c; tool_name[b["id"]]=nm; calls[c]+=1; last_asst_ts[b["id"]]=d["timestamp"]
                    for rg in contract_ranges(inp,nm): contract.append(rg)
                    if nm=="Bash":
                        for f in re.findall(r"[\w./-]+\.(?:rs|md|yaml|yml|json|py|toml)",inp.get("command") or ""):
                            if re.search(r"\b(cat|sed|head|tail|less|nl)\b",inp.get("command") or ""): files_read[f]+=1
            if prev_user_ts: model_time+=max(0,(ts(d["timestamp"])-ts(prev_user_ts)).total_seconds()); prev_user_ts=None
        elif typ=="user":
            c=(d.get("message") or {}).get("content")
            if isinstance(c,list):
                for b in c:
                    if isinstance(b,dict) and b.get("type")=="tool_result":
                        cc=b.get("content"); n=len(cc) if isinstance(cc,str) else sum(len(x.get("text","")) for x in (cc or []) if isinstance(x,dict))
                        res_chars[tool_cat.get(b.get("tool_use_id"),"unknown")]+=n
                        if b.get("tool_use_id") in last_asst_ts: tool_time+=max(0,(ts(d["timestamp"])-ts(last_asst_ts[b["tool_use_id"]])).total_seconds())
                prev_user_ts=d["timestamp"]
    ctxs=[reqs[r]["ctx"] for r in order]; outs=[reqs[r]["out"] for r in order]
    drops=sum(1 for a,b in zip(ctxs,ctxs[1:]) if b < 0.6*a and a>100000)
    # calibrate chars->tokens: context growth attributable to tool results over the run (excluding drops)
    growth=sum(max(0,b-a) for a,b in zip(ctxs,ctxs[1:]) if not (b<0.6*a)) ; total_res=sum(res_chars.values())
    out[run]={"model":dict(model),"effort":dict(effort),"requests":len(order),"peak_context":max(ctxs) if ctxs else 0,"final_context":ctxs[-1] if ctxs else 0,
      "first_context":ctxs[0] if ctxs else 0,"sum_input_processed":sum(ctxs),"sum_output":sum(outs),"compaction_like_drops":drops,
      "crossed":{k:any(c>=v for c in ctxs) for k,v in (("200k",200000),("500k",500000),("750k",750000),("1M",1000000))},
      "tool_calls":dict(calls),"tool_result_chars":dict(res_chars),"tool_result_chars_total":total_res,"context_growth_tokens":growth,
      "chars_per_token_calibrated":round(total_res/growth,2) if growth else None,
      "contract_reads":[list(x) for x in contract],"distinct_files_read":len(files_read),"repeat_file_reads":sum(v-1 for v in files_read.values() if v>1),
      "top_repeat_files":[(k,v) for k,v in files_read.most_common(6) if v>1],
      "model_time_s":round(model_time),"tool_time_s":round(tool_time)}
json.dump(out,open(sys.argv[1],"w"),indent=1)
print("extracted",len(out))
