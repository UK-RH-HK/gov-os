import sys
sys.path.insert(0,"/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/5009a8bf-a263-4632-bdc3-6bf820075cc1/scratchpad/ar0033/probe")
from derive import SIG, WRITE, matches, writes

# Each probe: (bullet, label, code a PLAUSIBLE future author of THIS product would write,
#              whether the effect really happens, whether a RUNTIME sink still catches it)
PROBES = [
 ("human_gate_approve","approve via Value::String instead of json!()", '''
fn a_future_approver(p: &Project, g: &mut Record) -> Result<()> {
    g.set("gate_status", Value::String("ANSWERED".into()));
    g.set("answered_by", json!("someone"));
    crate::util::write_yaml(&p.root.join(&g.path), &g.data)
}
'''),
 ("human_gate_approve","approve via a named constant", '''
const ANSWERED: &str = "ANSWERED";
fn a_future_approver2(p: &Project, g: &mut Record) -> Result<()> {
    g.set("gate_status", json!(ANSWERED));
    crate::util::write_yaml(&p.root.join(&g.path), &g.data)
}
'''),
 ("human_gate_approve","approve by direct data assignment", '''
fn a_future_approver3(p: &Project, g: &mut Record) -> Result<()> {
    g.data["gate_status"] = "ANSWERED".into();
    crate::util::write_yaml(&p.root.join(&g.path), &g.data)
}
'''),
 ("release_certification","certify with a differently-spelled field", '''
fn a_future_certifier(out_root: &Path, version: &str) -> Result<()> {
    let manifest = json!({"version": version, "certification": {"status": "CERTIFIED", "by": "ci"}});
    crate::util::write_json(&out_root.join("releases").join(version).join("manifest.json"), &manifest)
}
'''),
 ("release_certification","certify writing only a status field", '''
fn a_future_certifier2(out_root: &Path, version: &str) -> Result<()> {
    let manifest = json!({"version": version, "certified": true, "status": "CERTIFIED"});
    crate::util::write_json(&out_root.join("releases").join(version).join("release.json"), &manifest)
}
'''),
 ("trust_policy_mutation","anchor write with a computed role filename", '''
fn a_future_role_writer(ms: &MachineState, role: &str, bytes: &[u8]) -> Result<()> {
    let p = ms.root.join("trust").join(format!("{role}.json"));
    std::fs::write(p, bytes)?;
    Ok(())
}
'''),
 ("trust_policy_mutation","anchor write via a path constant", '''
const ROOT_REL: &str = "trust/root.json";
fn a_future_anchor_writer2(ms: &MachineState, bytes: &[u8]) -> Result<()> {
    std::fs::write(ms.root.join(ROOT_REL), bytes)?;
    Ok(())
}
'''),
 ("privileged_plugin_acquisition","capability registry write via a computed dir name", '''
fn a_future_capability_installer(p: &Project, kind: &str, descriptor: &Value) -> Result<()> {
    let dir = p.overlay_dir().join(format!("{kind}s"));
    crate::util::write_yaml(&dir.join("new.yaml"), descriptor)
}
'''),
 ("floor_lower_or_reset","floor reset by public-field assignment + save (the repair's own example)", '''
fn a_future_floor_reset(ms: &MachineState, product: &str) -> Result<()> {
    let mut f = crate::srr::state::Floors::load(ms, product);
    f.release_high_water_sequence = 0;
    f.minimum_secure_sequence = 0;
    f.save(ms)
}
'''),
 ("present_below_floor_release_as_current","a new in-process reporting surface", '''
fn a_future_release_report(p: &Project) -> Value {
    json!({"framework": crate::FRAMEWORK_NAME, "installed": p.framework_version(), "state": "current"})
}
'''),
 ("present_below_floor_release_as_current","a new CLI print that exits before the envelope", '''
fn a_future_serve_mode(id: &str) -> ! {
    let resp = json!({"protocol": "gov-capability/1", "ok": true, "provider": {"id": id}, "installed": crate::FRAMEWORK_VERSION});
    println!("{}", serde_json::to_string(&resp).unwrap());
    std::process::exit(0);
}
'''),
 ("human_gate_create","gate file written by a hand-built literal path", '''
fn a_future_gate_writer2(p: &Project, id: &str, fields: &Value) -> Result<()> {
    crate::util::write_yaml(&p.root.join("spec/decisions").join(format!("{id}.yaml")), fields)
}
'''),
]

print(f"{'bullet':40s} {'sig?':5s} {'write?':7s} {'acc?':5s} {'DETECTED':9s} probe")
print("-"*130)
missed=[]
for act,label,code in PROBES:
    sig,acc = SIG[act]
    m=matches(code,sig); w=writes(code); a=matches(code,acc)
    det = m and w and not a
    if not det: missed.append((act,label,m,w,a))
    print(f"{act:40s} {str(m):5s} {str(w):7s} {str(a):5s} {('YES' if det else '**NO**'):9s} {label}")
print()
print("MISSED BY THE DERIVATION:", len(missed), "of", len(PROBES))
for act,label,m,w,a in missed:
    why = "signature does not match" if not m else ("not seen as writing" if not w else "accepted by a marker without enforcement")
    print(f"  - [{act}] {label}  ({why})")
