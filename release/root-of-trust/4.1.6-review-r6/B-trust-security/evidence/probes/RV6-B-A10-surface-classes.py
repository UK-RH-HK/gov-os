#!/usr/bin/env python3
"""RV6-B-A10 — constitutional floors as a class on the revision-6 checker: non-security-classified and content-registered
units, R-CON-5 listing, first-hand derivation, default deny (review r6 reviewer B, AR-0016). Executed (pack checker).
Scratch only; the repository is never written.

Instrument, executed unmodified: `release/root-of-trust/4.1.6/constitutional-surface/csi_check.py` (modes `check`,
`derive-registration`, `verify-registration`, `registration-changes`) with the committed inventory.

Kernels (copies of `framework/`, each changing only the named unit):
  K0  genuine.
  K1  `commands/COMMAND_CONTRACT.yaml` (pinned_file; not in `csi_lib.SECURITY_CLASSIFIED_NAMES` or its prefixes): an internal
      operation `approve` re-mapped from `cit approve` to `decide`.
  K2  `overlay-templates/TOOL_PERMISSIONS.yaml` (pinned_file; seeds a new project's TOOL_PERMISSIONS overlay at `gov init`,
      `runtime/src/init.rs`): `research-agent` gains `SECRET_READ`.
  K3  `taxonomy/CAPABILITY_TAXONOMY.yaml` (pinned_file): one byte appended as a comment.
  K4  control: `policies/SECURITY_POLICY.yaml` aws-access-key regex weakened (security-classified).
  K5  unknown constitutional key added to `policies/AUTHORITY_POLICY.yaml`.
  K6  a new constitutional file `contracts/NEW_CONTRACT.yaml` with no inventory rule.
Questions: (i) does `registration-changes` list K1–K3 (exit 8) as it lists K4? (ii) does `verify-registration` refuse a proposal
derived from each changed kernel when the custodian's own build is K0 (R-CON-1)? (iii) do K5 and K6 fail default deny (exit 2)?
(iv) which 4.1.5 runtime consumers read the K1–K3 files (code)?
Environment: REVIEW_REPO (export of 4106885), SCRATCH. Output: JSON on stdout.
"""
import json, os, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
CS = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "constitutional-surface")
SCR = tempfile.mkdtemp(prefix="a10-", dir=os.environ["SCRATCH"])
ENV = {"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"}


def chk(*args):
    r = subprocess.run([sys.executable, "-B", os.path.join(CS, "csi_check.py")] + list(args), capture_output=True, text=True, env=ENV)
    try:
        j = json.loads(r.stdout)
    except Exception:
        j = {"stdout_tail": r.stdout[-300:], "stderr_tail": r.stderr[-300:]}
    return r.returncode, j


def kernel(name, edit):
    d = os.path.join(SCR, name)
    shutil.copytree(os.path.join(REPO, "framework"), d)
    if edit:
        edit(d)
    return d


def sub_file(rel, old, new):
    def f(d):
        p = os.path.join(d, rel)
        t = open(p).read()
        assert old in t, (rel, old)
        open(p, "w").write(t.replace(old, new, 1))
    return f


def append_file(rel, text):
    def f(d):
        open(os.path.join(d, rel), "a").write(text)
    return f


sec = open(os.path.join(REPO, "framework", "policies", "SECURITY_POLICY.yaml")).read()
m = re.search(r"id: aws-access-key[^\n]*\n(?:[^\n]*\n){0,4}?[^\n]*regex: ([^\n]+)", sec)
aws_line = m.group(0) if m else None
K = {
    "K0": kernel("K0", None),
    "K1": kernel("K1", sub_file("commands/COMMAND_CONTRACT.yaml", '{operation: approve, cli: "cit approve"}', '{operation: approve, cli: "decide"}')),
    "K2": kernel("K2", sub_file("overlay-templates/TOOL_PERMISSIONS.yaml", "research-agent: [READ_REPO, NETWORK_READ]", "research-agent: [READ_REPO, NETWORK_READ, SECRET_READ]")),
    "K3": kernel("K3", append_file("taxonomy/CAPABILITY_TAXONOMY.yaml", "\n# review probe\n")),
    "K5": kernel("K5", append_file("policies/AUTHORITY_POLICY.yaml", "\nreview_probe_unknown_key: allow_everything\n")),
    "K6": kernel("K6", lambda d: (os.makedirs(os.path.join(d, "contracts"), exist_ok=True), open(os.path.join(d, "contracts", "NEW_CONTRACT.yaml"), "w").write("schema_version: 1.0.0\nacceptance_threshold: 0\n"))),
}
if aws_line:
    reg = re.search(r"regex: ([^\n]+)", aws_line).group(1)
    K["K4"] = kernel("K4", sub_file("policies/SECURITY_POLICY.yaml", "regex: " + reg, "regex: '(?:AKIA)[0-9A-Z]{16}'"))
out = {"probe": "RV6-B-A10 surface classes on the revision-6 checker (AR-0016)", "aws_access_key_line_found": bool(aws_line)}

regs = {}
for name, d in K.items():
    if name in ("K5", "K6"):
        continue
    p = os.path.join(SCR, name + ".registration.json")
    rc, j = chk("derive-registration", d, "--release-id", "4.1.8" if name != "K0" else "4.1.7", "--sequence", "18" if name != "K0" else "17")
    json.dump(j, open(p, "w"))
    regs[name] = (rc, p)
out["derive_registration_exits"] = {k: v[0] for k, v in regs.items()}
changes = {}
for name in regs:
    if name == "K0":
        continue
    rc, j = chk("registration-changes", "--held", regs["K0"][1], "--new", regs[name][1], "--json")
    changes[name] = {"exit": rc, "changes": [c.get("unit") for c in j.get("changes", [])][:4], "security_classified": [c.get("unit") for c in j.get("security_classified_changes", [])][:4]}
out["registration_changes_vs_K0"] = changes
verify = {}
for name in regs:
    rc, j = chk("verify-registration", "--registration", regs[name][1], "--source-kernel", K["K0"], "--json")
    verify[name] = {"exit": rc, "problems": (j.get("problems") or j.get("errors") or [])[:3] if isinstance(j, dict) else None}
out["verify_registration_proposal_vs_custodian_build_K0"] = verify
dd = {}
for name in ("K0", "K5", "K6"):
    rc, j = chk("check", "--json", K[name])
    dd[name] = {"exit": rc, "unclassified": (j.get("unclassified") or j.get("summary", {}).get("unclassified") if isinstance(j, dict) else None)}
out["default_deny_check"] = dd

rt = {}
for rel, needle in (("runtime/src/init.rs", "overlay-templates"), ("runtime/src/orchestration/intents.rs", "COMMAND_CONTRACT"), ("runtime/src/verification/mod.rs", "COMMAND_CONTRACT"),
                    ("runtime/src/adapters.rs", "COMMAND_CONTRACT"), ("runtime/src/tools.rs", "TOOL_PERMISSIONS.yaml")):
    t = open(os.path.join(REPO, rel)).read()
    rt[rel] = [i + 1 for i, l in enumerate(t.splitlines()) if needle in l][:6]
out["runtime_4_1_5_consumers_lines"] = rt
lib = open(os.path.join(CS, "csi_lib.py")).read()
out["security_classified_names_and_prefixes"] = re.findall(r"SECURITY_CLASSIFIED_(?:NAMES|FILE_PREFIXES) = \(([^)]*)\)", lib)
out["verdicts"] = {
    "K4_security_change_listed_exit_8": changes.get("K4", {}).get("exit") == 8,
    "K1_command_contract_change_not_listed": changes["K1"]["exit"] == 0,
    "K2_tool_permissions_template_change_not_listed": changes["K2"]["exit"] == 0,
    "K3_taxonomy_change_not_listed": changes["K3"]["exit"] == 0,
    "verify_registration_refuses_every_changed_proposal_against_K0_build": all(v["exit"] != 0 for k, v in verify.items() if k != "K0"),
    "verify_registration_accepts_K0": verify["K0"]["exit"] == 0,
    "K5_unknown_key_default_deny": dd["K5"]["exit"] == 2,
    "K6_new_file_default_deny": dd["K6"]["exit"] == 2,
}
print(json.dumps(out, indent=1, sort_keys=True).replace(SCR, "<scratch>").replace(REPO, "<export>"))
