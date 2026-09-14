#!/usr/bin/env python3
"""AR-0017 attrprec6 (held-out RV6-C-A08): can any in-tree .gitattributes override the revision-6 trust member `* -text` and
force line-ending conversion of the kernel, producing a tree a RoT-1 binary treats as valid? Real Git, scratch only.

Precedence Git applies: `.git/info/attributes` (out of tree) > a deeper in-tree `.gitattributes` > a shallower one. The member
lives at `governance/trust/.gitattributes`. Rows:
  ROOT_ATTR   a repo-root `.gitattributes` `governance/trust/** text` + autocrlf: the member is deeper, so it wins (kernel LF)
  KERNEL_ATTR a `governance/trust/kernel/.gitattributes` `* text` + autocrlf: deeper than the member, so it converts; but it
              is an extra kernel file not in the release content set, so the installation state is PARTIAL (fail closed)
  INFO_ATTR   `.git/info/attributes` `* text` + autocrlf: out of tree, highest precedence, converts; PARTIAL (covered by gitops6)
  CONTROL     member only + autocrlf: kernel stays LF (COMPLETE)
Output: JSON on stdout.
"""
import json,os,subprocess,sys,tempfile
sys.dont_write_bytecode=True; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import c6lib as L
S=tempfile.mkdtemp(prefix="attrprec6-",dir=os.environ["AR17_SCRATCH"])
ENV={"PATH":"/usr/bin:/bin","HOME":os.path.join(S,"home"),"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.path.join(S,"home",".gc"),
     "GIT_AUTHOR_NAME":"t","GIT_AUTHOR_EMAIL":"t@t","GIT_COMMITTER_NAME":"t","GIT_COMMITTER_EMAIL":"t@t"}
os.makedirs(ENV["HOME"])
KERNEL=b"version: 1\nsecret_content_patterns:\n  - id: aws\n    regex: '(AKIA|ASIA)[0-9A-Z]{16}'\n"
def git(a,cwd):
    r=subprocess.run(["git"]+a,cwd=cwd,env=ENV,capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode())
    return r.stdout
def origin(name,root_attr=None,kernel_attr=None):
    d=os.path.join(S,name); os.makedirs(os.path.join(d,"governance/trust/kernel"))
    git(["init","-q"],d)
    open(os.path.join(d,"governance/trust/kernel/POLICY.yaml"),"wb").write(KERNEL)
    open(os.path.join(d,"governance/trust/.gitattributes"),"wb").write(b"* -text\n")
    if root_attr is not None: open(os.path.join(d,".gitattributes"),"w").write(root_attr)
    if kernel_attr is not None: open(os.path.join(d,"governance/trust/kernel/.gitattributes"),"w").write(kernel_attr)
    git(["add","-A"],d); git(["commit","-q","-m",name],d); return d
def clone_convert(src,name,autocrlf=True,info_attr=None):
    d=os.path.join(S,name); git(["clone","-q","--no-checkout",src,d],S)
    if autocrlf: git(["config","core.autocrlf","true"],d)
    if info_attr is not None:
        os.makedirs(os.path.join(d,".git/info"),exist_ok=True); open(os.path.join(d,".git/info/attributes"),"w").write(info_attr)
    git(["checkout","-q","HEAD","--","."],d)
    got=open(os.path.join(d,"governance/trust/kernel/POLICY.yaml"),"rb").read()
    extra=os.path.isfile(os.path.join(d,"governance/trust/kernel/.gitattributes"))
    # RCS = the committed kernel bytes for POLICY.yaml (LF) only; a kernel .gitattributes is an extra file -> mismatch
    rcs={"POLICY.yaml":L.sha(KERNEL)}
    kmap={k:v[1] for k,v in L.kernel_file_map(os.path.join(d,"governance/trust/kernel")).items() if v[0]=="file"}
    mismatch = kmap!=rcs
    return {"kernel_crlf":b"\r\n" in got,"kernel_equals_committed":got==KERNEL,"extra_kernel_gitattributes":extra,
            "kernel_content_mismatch_vs_RCS":mismatch}
rows={
 "ROOT_ATTR_governance_trust_star_text": clone_convert(origin("o_root","governance/trust/** text\n"),"c_root"),
 "KERNEL_ATTR_star_text": clone_convert(origin("o_kern",kernel_attr="* text\n"),"c_kern"),
 "INFO_ATTR_star_text": clone_convert(origin("o_info"),"c_info",info_attr="* text\n"),
 "CONTROL_member_only": clone_convert(origin("o_ctl"),"c_ctl"),
}
verdicts={
 "root_attr_cannot_override_member": not rows["ROOT_ATTR_governance_trust_star_text"]["kernel_crlf"],
 "kernel_attr_override_trips_content_mismatch": rows["KERNEL_ATTR_star_text"]["kernel_crlf"] and rows["KERNEL_ATTR_star_text"]["kernel_content_mismatch_vs_RCS"],
 "info_attr_override_converts_fail_closed": rows["INFO_ATTR_star_text"]["kernel_crlf"] and rows["INFO_ATTR_star_text"]["kernel_content_mismatch_vs_RCS"],
 "control_member_protects": not rows["CONTROL_member_only"]["kernel_crlf"] and rows["CONTROL_member_only"]["kernel_equals_committed"],
}
print(L.scrub(json.dumps({"probe":"AR-0017 attrprec6 (RV6-C-A08 attribute precedence)","git":subprocess.run(["git","--version"],capture_output=True,text=True).stdout.strip(),"rows":rows,"verdicts":verdicts},indent=1,sort_keys=True)))
