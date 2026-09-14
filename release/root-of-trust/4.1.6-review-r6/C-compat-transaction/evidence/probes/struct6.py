#!/usr/bin/env python3
"""AR-0017 struct6: structural tampering against the revision-6 closed entry sets (`18` §9.1) and root discovery (`18` §9.2).
Each case copies the R6 tree, applies one tamper an ordinary/legacy operation or a user could produce, and evaluates
c6lib.state_r6 (encoded from the text by AR-0017). Property: every tamper of governance/trust/**, the occupation entries or
the `.gitattributes` member leaves a state that is NOT COMPLETE (fail closed). Environment: SCRATCH. Output: JSON on stdout.
"""
import os,sys,json,shutil
sys.dont_write_bytecode=True; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import c6lib as L
T=json.load(open(os.path.join(os.environ["AR17_SCRATCH"],"trees2","trees.json"))); R6=T["trees"]["R6"]; rcs=T["rcs"]
BASE=os.path.join(os.environ["AR17_SCRATCH"],"struct6")
if not os.path.isdir(BASE): os.makedirs(BASE)
n=[0]
def mk(t):
    d=os.path.join(BASE,t+str(n[0])); n[0]+=1; shutil.copytree(R6,d,symlinks=True); return d
def S_(d):
    s=L.state_r6(d,rcs=rcs); return {"state":s["state"],"reasons":s["reasons"],"kernel_tampered":s.get("kernel_tampered")}
def firstkernel(d):
    for dp,dn,fn in os.walk(os.path.join(d,"governance/trust/kernel")):
        for f in sorted(fn):
            if f.endswith(".yaml"): return os.path.join(dp,f)
def run():
    o={}
    o["baseline_R6"]=S_(mk("base"))
    d=mk("occsym"); p=os.path.join(d,"governance/kernel"); os.unlink(p); os.symlink("/etc/hostname",p); o["occ_kernel_to_symlink"]=S_(d)
    d=mk("occdir"); p=os.path.join(d,"governance/project"); os.unlink(p); os.makedirs(p); o["occ_project_to_dir"]=S_(d)
    d=mk("occfile"); p=os.path.join(d,"governance/framework.lock"); shutil.rmtree(p); open(p,"w").write("x"); o["occ_fwlockdir_to_file"]=S_(d)
    d=mk("ksym"); os.symlink("../../../../etc/passwd",os.path.join(d,"governance/trust/kernel/EVIL")); o["symlink_in_kernel"]=S_(d)
    d=mk("gadel"); os.unlink(os.path.join(d,"governance/trust/.gitattributes")); o["gitattributes_deleted"]=S_(d)
    d=mk("gachg"); open(os.path.join(d,"governance/trust/.gitattributes"),"w").write("* text\n"); o["gitattributes_content_changed"]=S_(d)
    d=mk("kedit"); open(firstkernel(d),"a").write("\n# tamper\n"); o["kernel_edited"]=S_(d)
    d=mk("kadd"); open(os.path.join(d,"governance/trust/kernel/EXTRA.yaml"),"w").write("x: 1\n"); o["kernel_file_added"]=S_(d)
    d=mk("krm"); os.unlink(firstkernel(d)); o["kernel_file_removed"]=S_(d)
    d=mk("stfor"); open(os.path.join(d,"governance/trust/state/NOTES.txt"),"w").write("x"); o["foreign_in_state_dir"]=S_(d)
    d=mk("ttop"); open(os.path.join(d,"governance/trust/backup.tar"),"w").write("x"); o["foreign_toplevel_in_trust"]=S_(d)
    d=mk("occrm"); os.unlink(os.path.join(d,"governance/kernel")); o["occ_kernel_removed"]=S_(d)
    d=mk("migrm"); os.unlink(os.path.join(d,".governance-runtime/migration")); o["migration_occupation_removed"]=S_(d)
    d=mk("occx"); open(os.path.join(d,"governance/framework.lock/EXTRA"),"w").write("x"); o["occ_dir_extra_file"]=S_(d)
    d=mk("occhl"); p=os.path.join(d,"governance/kernel"); os.link(p,os.path.join(d,"HARDLINK")); r=S_(d); r["nlink"]=os.lstat(p).st_nlink; o["occ_hardlinked_nlink2"]=r
    o["property_every_trust_or_occupation_or_member_tamper_not_COMPLETE"]=all(
        v["state"]!="COMPLETE" for k,v in o.items() if k not in ("baseline_R6","occ_hardlinked_nlink2","property_every_trust_or_occupation_or_member_tamper_not_COMPLETE"))
    o["note_hardlink"]="the installation-state predicate does not check st_nlink; VU-12/§3 SecureDir enforce link count at use-time (unimplemented). The hard-linked occupation entry stays COMPLETE in the state machine (C-4/VU-12 carried)."
    return o
print(L.scrub(json.dumps({"probe":"AR-0017 struct6 closed-entry-set tamper","results":run()},indent=1,sort_keys=True)))
