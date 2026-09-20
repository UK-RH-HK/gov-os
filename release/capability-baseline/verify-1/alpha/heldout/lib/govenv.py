"""P2-AR-0046 (verify-1 alpha) — held-out probe harness.

Simulated machines: a machine is a distinct `XDG_STATE_HOME` + `HOME` pair (the product derives its
protected state root from `XDG_STATE_HOME`, `runtime/src/srr/state.rs::default_state_root`).
`GOV_MACHINE_STATE_DIR` is deliberately never set, so every probe takes the same path a real
installation takes.

The administrator domain is a directory outside every project and outside any path the product
treats as repository content (no `.git`, no `governance` component).
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import srrsign  # noqa: E402

WT = pathlib.Path(__file__).resolve().parents[5].parent
# .../release/capability-baseline/verify-1/alpha/heldout/lib -> worktree root
while not (WT / "Cargo.toml").exists() and WT != WT.parent:
    WT = WT.parent
GOV = WT / "target" / "release" / "gov"
PRODUCT = "agentic-engineering-os"

SCRATCH = pathlib.Path(
    os.environ.get(
        "ALPHA_SCRATCH",
        "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
        "1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/alpha",
    )
)


def fresh(name):
    d = SCRATCH / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


class Machine:
    """One simulated machine: its own protected state root and HOME."""

    def __init__(self, name):
        self.name = name
        self.home = fresh(f"machines/{name}/home")
        self.state_home = fresh(f"machines/{name}/state")

    def env(self, extra=None):
        e = dict(os.environ)
        e.pop("GOV_MACHINE_STATE_DIR", None)
        e["HOME"] = str(self.home)
        e["XDG_STATE_HOME"] = str(self.state_home)
        e["XDG_CACHE_HOME"] = str(self.home / ".cache")
        if extra:
            e.update(extra)
        return e

    @property
    def state_root(self):
        return self.state_home / "governance-os" / "machine"

    def run(self, args, cwd=None, env=None, json_out=True):
        argv = [str(GOV)] + (["--json"] if json_out else []) + [str(a) for a in args]
        # Default cwd: the machine's own (empty) home, never an ancestor of the administrator domain,
        # because `gov trust *` treats the current directory as the governed project root.
        p = subprocess.run(
            argv, cwd=str(cwd) if cwd else str(self.home), env=self.env(env),
            capture_output=True, text=True,
        )
        return Out(p, argv)

    def ok(self, args, cwd=None, env=None):
        o = self.run(args, cwd=cwd, env=env)
        assert o.ok, f"expected success from {args}: {o.text[:2000]}"
        return o.result

    def provision(self, root_file):
        return self.run(["trust", "provision", "--anchor", str(root_file)])

    def bind(self, authority_file, key_file):
        return self.run(
            ["trust", "bind", "--authority", str(authority_file), "--key", str(key_file)]
        )


class Out:
    def __init__(self, p, argv):
        self.p = p
        self.argv = argv
        self.text = (p.stdout or "") + (p.stderr or "")
        try:
            self.env = json.loads(p.stdout)
        except Exception:
            self.env = None

    @property
    def ok(self):
        return bool(self.env and self.env.get("ok"))

    @property
    def result(self):
        return (self.env or {}).get("result")

    @property
    def code(self):
        return ((self.env or {}).get("error") or {}).get("code", "")

    @property
    def message(self):
        return ((self.env or {}).get("error") or {}).get("message", "")


class Owner:
    """The owner's throw-away signing material, in an administrator-domain directory."""

    def __init__(self, name="owner", root_version=1, product=PRODUCT):
        self.dir = fresh(f"admin-domain/{name}")
        self.product = product
        self.pub = srrsign.new_publisher()
        self.root_file = self.dir / "root-1.json"
        srrsign.write_root(self.pub, self.root_file, version=root_version, product=product)
        self.binding_key = os.urandom(32)
        self.authority_id = f"{name}-authority"
        self.authority_file = self.dir / "t2-binding-authority-1.json"
        self.key_file = self.dir / "t2-binding-key.json"
        self.write_authority(1, [(self.binding_key, "active")])
        srrsign.write_binding_key(self.key_file, self.binding_key)

    def write_authority(self, version, keys, machines=None, path=None, signers=None,
                        expires=srrsign.FAR_FUTURE):
        doc = srrsign.binding_authority_doc(
            self.authority_id, version, keys, machines=machines,
            expires=expires, product=self.product,
        )
        p = pathlib.Path(path) if path else self.authority_file
        p.write_bytes(
            srrsign.envelope(doc, signers if signers is not None else [self.pub["t2-binding"]])
        )
        return p

    def sign_release(self, kernel_dir, sequence, meta_dir=None, **kw):
        meta_dir = meta_dir or pathlib.Path(kernel_dir).parent / "metadata"
        kw.setdefault("product", self.product)
        return srrsign.publish(kernel_dir, meta_dir, self.pub, sequence, **kw)


def answer_gate(machine, owner, proj, gate_id, option="A", by="probe-owner",
                nonce=None, doc_type="human-gate-answer"):
    """Answer a Human Decision Gate through the owner-signed human channel (L3/ARCH-0003 §8).

    The answer is signed with the owner's root-delegated `human-gate` key and dropped into the
    machine's protected human-channel inbox, out of band: no CLI flag, environment variable or
    repository file can substitute for it.
    """
    show = machine.run(["--role", "orchestrator", "gate", "show", gate_id], cwd=proj)
    g = (show.result or {})
    pkg = g.get("package_sha256") or (g.get("gate") or {}).get("package_sha256")
    inst = (g.get("gate") or {}).get("gate_instance") or g.get("gate_instance")
    opts = [o.get("id") for o in ((g.get("gate") or {}).get("options") or []) if o.get("id")]
    hc = machine.run(["trust", "human-channel"], cwd=proj)
    inbox = pathlib.Path((hc.result or {}).get("inbox"))
    inbox.mkdir(parents=True, exist_ok=True)
    nonce = nonce or f"n-{gate_id}-{option}"
    doc = srrsign.human_answer_doc(gate_id, inst, pkg, option, by, nonce,
                                   product=PRODUCT, doc_type=doc_type)
    (inbox / f"{nonce}.json").write_bytes(
        srrsign.envelope(doc, [owner.pub["human-gate"]]))
    return {"gate": gate_id, "instance": inst, "package_sha256": pkg, "options": opts,
            "inbox": str(inbox)}


def break_glass(machine, owner, proj, recovery_kernel, nonce="bg-1", reason="held-out probe"):
    """Drop an owner-signed `recovery`-role break-glass authorisation into the machine's inbox."""
    bg = machine.run(["trust", "break-glass"], cwd=proj).result or {}
    mid = (machine.run(["trust", "status"], cwd=proj).result or {}).get("machine_id")
    inbox = pathlib.Path(bg["inbox"])
    inbox.mkdir(parents=True, exist_ok=True)
    files, ph, kmh, ver = srrsign.measure_payload(recovery_kernel)
    doc = srrsign.break_glass_doc(mid, nonce, reason, ver, ph, kmh, product=PRODUCT)
    (inbox / f"{nonce}.json").write_bytes(srrsign.envelope(doc, [owner.pub["recovery"]]))
    return {"machine_id": mid, "inbox": str(inbox), "release_version": ver,
            "payload_hash": ph}


def build_release(version="4.1.6", tag=None, certification=None):
    """Use the product's own release builder to produce a payload tree (measurement, not authority).

    Each suite gets its own copy, so that one suite's owner signing the payload can never
    invalidate another suite's metadata (the suites are independent by construction).
    """
    tag = tag or pathlib.Path(sys.argv[0]).stem or "rel"
    out = SCRATCH / "relbuild" / tag
    d = out / "releases" / version
    if not d.exists():
        out.mkdir(parents=True, exist_ok=True)
        argv = [str(GOV), "--json", "release", "build", "--version", version,
                "--canonical", str(WT), "--out", str(out)]
        p = subprocess.run(argv, capture_output=True, text=True)
        assert json.loads(p.stdout).get("ok"), p.stdout[:3000]
    return d


def copy_release(src_release_dir, tag):
    """A private copy of a built release, so a probe can tamper with it."""
    d = fresh(f"releases/{tag}")
    shutil.copytree(src_release_dir, d / "releases", dirs_exist_ok=True)
    return d / "releases"


def git_init(path):
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.email=v@x", "-c", "user.name=v",
                                                 "commit", "-qm", "seed"]):
        subprocess.run(["git"] + args, cwd=str(path), capture_output=True)


RESULTS = []


def check(name, condition, detail=""):
    RESULTS.append((name, bool(condition), detail))
    print(f"{'PASS' if condition else 'FAIL'} {name}" + (f" :: {detail}" if detail else ""))
    return bool(condition)


def summary():
    bad = [r for r in RESULTS if not r[1]]
    print(f"\n-- {len(RESULTS) - len(bad)}/{len(RESULTS)} checks passed")
    return 1 if bad else 0
