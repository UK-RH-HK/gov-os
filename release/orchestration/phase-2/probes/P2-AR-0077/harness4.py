#!/usr/bin/env python3
"""P2-AR-0077 — fourth independent adversarial pre-mint review: probe harness.

Written from scratch for this review. Drives `target/release/gov` (built from the
commit under review) against disposable projects, each with its own
XDG_STATE_HOME, so the machine's shared governance state is never touched.

Lab discipline: nothing is ever deleted. Stale project trees and stale markers are
MOVED ASIDE into <LAB>/aside/ with a timestamp suffix.

Proof standard (P2-ADJ-0006 / P2-AR-0073): an effect is proven by an actual
filesystem or state outcome -- a file that appeared outside the project root, a
task that closed which should have been refused -- never by reading a status
field. Status fields are recorded alongside, as corroboration only.
"""
import hashlib, json, os, shutil, subprocess, time, pathlib

# --- review_subject, reimplemented from the product's own definition ----------
# `gov_runtime::tools::review_subject` = sha256(canonical_json({kind, tool_id,
# version, descriptor})) with INSTALLATION_NON_SUBJECT + security_review_record
# stripped from the descriptor. canonical_json = serde_json over BTreeMap-sorted
# keys => compact, sorted, UTF-8. Verified byte-for-byte against the product's
# own reported `change_class.security_review.review_subject_sha256` by
# probe_subject_selfcheck.py before any finding relies on it.
INSTALLATION_NON_SUBJECT = [
    "human_gate", "registration_gate", "approval_gate", "status", "installed_by",
    "installed_at", "approval", "installation_sha256", "security_review_evidence",
    "os_binding",
]


def canonical_json(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def installed_version(d):
    vp = d.get("version_pin")
    if isinstance(vp, str) and vp:
        return vp
    v = d.get("version")
    if v is None:
        return ""
    return v if isinstance(v, str) else json.dumps(v)


def review_subject(d):
    dd = {k: v for k, v in d.items()
          if k not in INSTALLATION_NON_SUBJECT and k != "security_review_record"}
    doc = {"kind": "tool-installation", "tool_id": d.get("tool_id"),
           "version": installed_version(d), "descriptor": dd}
    return hashlib.sha256(canonical_json(doc).encode("utf-8")).hexdigest()



HERE = pathlib.Path(__file__).resolve().parent
WT = pathlib.Path(
    "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
    "1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/wt/p2-r3-adv"
)
LAB = pathlib.Path(
    "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
    "1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/p2ar0077/lab"
)
GOV = WT / "target/release/gov"
# The marker sink. It is OUTSIDE every project root by construction: project roots
# live under LAB/p/<tag>, this lives under LAB/outside.
OUTSIDE = LAB / "outside"
ASIDE = LAB / "aside"
for d in (OUTSIDE, ASIDE, LAB / "p", LAB / "st"):
    d.mkdir(parents=True, exist_ok=True)


def aside(path: pathlib.Path):
    """Move `path` out of the way. Never delete (lab discipline)."""
    path = pathlib.Path(path)
    if path.exists() or path.is_symlink():
        shutil.move(str(path), str(ASIDE / f"{path.name}-{int(time.time() * 1000)}"))


class Proj:
    """A disposable governed project with its own state home."""

    def __init__(self, tag, fixture="greenfield"):
        self.tag = tag
        self.root = LAB / "p" / tag
        self.state = LAB / "st" / tag
        aside(self.root)
        aside(self.state)
        self.root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(WT / "fixtures" / fixture / "project", self.root)
        self.state.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q")
        self.git("config", "user.email", "p2ar0077@example.invalid")
        self.git("config", "user.name", "p2ar0077")
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture baseline")

    # --- plumbing -------------------------------------------------------
    def git(self, *a):
        return subprocess.run(["git", *a], cwd=self.root, capture_output=True, text=True)

    def commit_all(self, msg="probe"):
        self.git("add", "-A")
        self.git("commit", "-qm", msg)

    def run(self, args, session="S-p77", role="orchestrator"):
        env = dict(os.environ)
        env["XDG_STATE_HOME"] = str(self.state)
        env["GOV_CANONICAL_ROOT"] = str(WT)
        env.pop("GOV_SESSION", None)
        env.pop("GOV_ROLE", None)
        cmd = [str(GOV), "--json", "--root", str(self.root),
               "--session", session, "--role", role, *args]
        pr = subprocess.run(cmd, capture_output=True, text=True, env=env)
        try:
            return json.loads(pr.stdout.strip())
        except Exception:
            return {"ok": False, "error": {"code": "NO_JSON",
                                           "message": (pr.stderr or pr.stdout)[:4000]}}

    def ok(self, args, session="S-p77", role="orchestrator"):
        e = self.run(args, session, role)
        if not e.get("ok"):
            raise SystemExit(f"gov {' '.join(args)} FAILED: {json.dumps(e.get('error'))[:3000]}")
        return e["result"]

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def exists(self, rel):
        return (self.root / rel).exists()


def fresh(tag, fixture="greenfield"):
    p = Proj(tag, fixture)
    p.ok(["init", "--name", tag, "--alias", f"a-{tag}"])
    p.commit_all("after init")
    p.ok(["rebuild-memory"])
    return p


def security_review(p, tool_id, version, subject=None, name=None):
    """A governed independent security review of tool_id@version (another session+role)."""
    t = p.ok(["task", "create", "--class", "security", "--objective",
              f"Security review of {tool_id} {version}", "--status", "READY"])["id"]
    p.ok(["task", "claim", t], session="S-sec", role="security-engineer")
    p.ok(["rebuild-memory", "--incremental"], session="S-sec", role="security-engineer")
    pk = p.ok(["context", "compile", t], session="S-sec", role="security-engineer")
    rc = pk["receipt_contract"]
    inputs = [f"{e.get('id', '')}@{e.get('content_hash', '')}"
              for e in (rc.get("acknowledge_inputs") or [])]
    tests = [{"test": x, "result": "passed", "evidence": "P2-AR-0077 probe"}
             for x in (rc.get("tests_requiring_evidence") or [])]
    sr = {"tool_id": tool_id, "version": version, "verdict": "passed"}
    if subject:
        sr["subject_sha256"] = subject
    rec = {"work_completed": f"reviewed {tool_id} {version}", "files_changed": [],
           "tests": {"status": "not_applicable_with_reason", "reason": "P2-AR-0077 probe"},
           "outcome": "success", "evidence": [], "context_packet_hash": pk["packet_hash"],
           "inputs_consumed": inputs, "outputs_produced": [],
           "requirements_implemented": rc["trace"]["requirements"],
           "scenarios_implemented": rc["trace"]["scenarios"],
           "features_implemented": rc["trace"]["features"],
           "decisions_applied": rc["trace"]["decisions"],
           "constraints_applied": rc["trace"]["constraints"],
           "acceptance_evidence": tests, "deviations": [], "unresolved": [],
           "security_review": sr}
    d = p.root / ".governance-runtime" / "reports"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{name or ('rev-' + tool_id)}.json"
    f.write_text(json.dumps(rec))
    return p.ok(["task", "close", t, "--report", str(f)],
                session="S-sec", role="security-engineer")["report"]


BASE_ID = "TOOL-P77"


def descriptor(review, install_cmd=None, health_cmd=None, uninstall_cmd=None,
               tool_id=BASE_ID, **over):
    """The conforming, non-elevated, reviewed, pinned, reversible descriptor."""
    d = {
        "tool_id": tool_id, "name": "p77", "type": "CLI", "capabilities": ["lint"],
        "version": "1.0", "version_pin": "1.0.0",
        "required_permission_classes": ["READ_REPO"],
        "license": "MIT", "reversible": True, "cost_usd": 0,
        "security_review_record": review,
        "permissions": {"repo_write": False, "network": False},
        "install_command": install_cmd or ["true"],
        "uninstall_command": uninstall_cmd or ["true"],
        "health_check": {"kind": "command", "command": health_cmd or ["true"], "expect_exit": 0},
    }
    d.update(over)
    return d


def install(p, desc, tag, execute=True, session="S-adv", role="tooling-engineer"):
    rel = f"tools/{tag}.json"
    p.write(rel, json.dumps(desc))
    args = ["tools", "install", "--descriptor", str(p.root / rel)]
    if execute:
        args.append("--execute")
    return p.run(args, session=session, role=role)


def marker_for(tag):
    """A fresh marker path outside every project root. Stale ones move aside."""
    m = OUTSIDE / f"{tag}.marker"
    aside(m)
    return m


def bind(p, d, version="1.0.0", name=None):
    """Bind a fresh governed review to EXACTLY these descriptor bytes, then return it.

    Call after every field the descriptor will carry is set (BC-P2-41: a review
    names the exact installation subject it reviewed).
    """
    subject = review_subject(d)
    rev = security_review(p, d["tool_id"], version, subject=subject,
                          name=name or f"rev-{d['tool_id']}-{subject[:8]}")
    d["security_review_record"] = rev
    return d


def gate_records(p):
    """Human Decision Gates raised in this project (spec/decisions/HDG-*)."""
    d = p.root / "spec" / "decisions"
    return sorted(x.name for x in d.glob("HDG-*")) if d.exists() else []


def verdict(e, p, marker=None, tool_id=BASE_ID):
    r = e.get("result", {}) or {}
    err = e.get("error") or {}
    cc = (r.get("change_class") or err.get("details", {}).get("change_class") or {})
    env = cc.get("authority_envelope") or {}
    return {
        "ok": e.get("ok"),
        "error_code": err.get("code"),
        "installed": r.get("installed"),
        "branch": cc.get("branch"),
        "expands_authority": env.get("expands_authority"),
        "triggers_fired": env.get("triggers_fired"),
        "undetermined": env.get("undetermined"),
        "human_gate": r.get("human_gate"),
        "descriptor_written": p.exists(f"governance/project/tools/{tool_id}.yaml"),
        # THE PROOF: did anything appear outside the project root?
        "MARKER_OUTSIDE_PROJECT": (pathlib.Path(marker).exists() if marker else None),
        "gate_records": gate_records(p),
        "exec_result": r.get("exec_result"),
    }


def save(name, obj):
    out = HERE / "results" / f"{name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, default=str))
    print(f"[saved] {out}")
