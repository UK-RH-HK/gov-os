import os, sys, json, re
ROOT = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/5009a8bf-a263-4632-bdc3-6bf820075cc1/scratchpad/wt/srr1-r1-verify-4"

SIG = {
 "human_gate_create": (["save_record(","record_path_for(","record_dir_for("],
   ["Effect::HumanGateCreate","guarded_record_effect(","save_record(","_clearance: &crate::srr::breakglass::Clearance"]),
 "human_gate_approve": (['json!("ANSWERED")','"gate_status", json!("ANSWERED")'], ["Effect::HumanGateApprove"]),
 "release_certification": (["certification_status",'"certification": {"status"'], ["Effect::ReleaseCertification"]),
 "trust_policy_mutation": (["root_metadata_path(","provisioned_path(",'join("root.json")','join("provisioned.json")'],
   ["Effect::TrustPolicyMutation","set_root_metadata("]),
 "privileged_plugin_acquisition": (['join("plugins")','join("tools")',"guard_acquisition"],
   ["Effect::PrivilegedPluginAcquisition","guard_acquisition"]),
 "floor_lower_or_reset": (["floors_path(",'join("floors")'],
   ["floor_lower_or_reset","raise_metadata(","raise_release(","raise_minimum_secure("]),
 "present_below_floor_release_as_current": (['"command": name','"ok": true, "command"'],
   ["Effect::PresentBelowFloorReleaseAsCurrent","present::attach(","present::presentation("]),
}
WRITE = ["write_durable(","std::fs::write(","fs::write(","std::fs::rename(","File::create(",
         "write_yaml(","write_text(","write_json(","save_record(",".save(","write_all(","println!","print!"]
EXEMPT = {("human_gate_create","runtime/src/cit/mod.rs::take_snapshot")}

def sources(cut=True):
    out=[]
    for base in ("runtime/src","cli/src"):
        for dp,_,fns in os.walk(os.path.join(ROOT,base)):
            for fn in fns:
                if not fn.endswith(".rs"): continue
                p=os.path.join(dp,fn)
                t=open(p,encoding="utf-8").read()
                full=t
                if cut:
                    i=t.find("#[cfg(test)]")
                    if i>=0: t=t[:i]
                out.append((os.path.relpath(p,ROOT).replace("\\","/"),t,full))
    out.sort()
    return out

FNPREFIX=("fn ","pub fn ","pub(crate) fn ","pub(super) fn ","async fn ","pub async fn ")
def split_indent(path,text):
    lines=text.split("\n"); out=[]
    for i,l in enumerate(lines):
        tr=l.lstrip(); indent=l[:len(l)-len(tr)]
        if not any(tr.startswith(p) for p in FNPREFIX): continue
        name=""
        try: rest=tr.split("fn ",1)[1]
        except IndexError: continue
        for c in rest:
            if c.isalnum() or c=="_": name+=c
            else: break
        if not name: continue
        close=indent+"}"
        end=len(lines)-1
        for j in range(i+1,len(lines)):
            if lines[j]==close: end=j; break
        out.append((path,name,"\n".join(lines[i:end+1]),i+1,end+1))
    return out

def split_brace(path,text):
    """Independent splitter: track brace depth, ignoring braces in strings/comments (approximate)."""
    lines=text.split("\n"); out=[]
    i=0
    while i<len(lines):
        l=lines[i]; tr=l.lstrip()
        if any(tr.startswith(p) for p in FNPREFIX):
            name=""
            rest=tr.split("fn ",1)[1]
            for c in rest:
                if c.isalnum() or c=="_": name+=c
                else: break
            if name:
                depth=0; started=False; end=i
                for j in range(i,len(lines)):
                    s=lines[j]
                    s=re.sub(r'"(\\.|[^"\\])*"','""',s)
                    s=re.sub(r'//.*$','',s)
                    for c in s:
                        if c=="{": depth+=1; started=True
                        elif c=="}": depth-=1
                    if started and depth<=0: end=j; break
                    end=j
                out.append((path,name,"\n".join(lines[i:end+1]),i+1,end+1))
                i=i+1
                continue
        i+=1
    return out

def matches(body,ms): return any(m in body for m in ms)
def writes(body): return matches(body,WRITE)

def census(splitter,cut=True,label=""):
    funcs=[]
    srcs=sources(cut)
    for p,t,_ in srcs: funcs.extend(splitter(p,t))
    print(f"--- {label}: {len(srcs)} files, {len(funcs)} functions")
    for act,(sig,acc) in SIG.items():
        der=[f for f in funcs if matches(f[2],sig)]
        wr=[f for f in der if writes(f[2])]
        viol=[];ex=[]
        for f in wr:
            if matches(f[2],acc): continue
            site=f"{f[0]}::{f[1]}"
            (ex if (act,site) in EXEMPT else viol).append(site)
        print(f"  {act:42s} derived {len(der):3d} / writers {len(wr):3d} / exempt {len(ex)} / violations {len(viol)}"
              + (f"  ==> {viol}" if viol else ""))
    return funcs

if __name__=="__main__":
    f1=census(split_indent,True,"indentation splitter, cfg(test) cut (the product's own)")
    f2=census(split_brace,True,"brace-depth splitter, cfg(test) cut (independent)")
    f3=census(split_indent,False,"indentation splitter, NO cfg(test) cut")
