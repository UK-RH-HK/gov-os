#!/usr/bin/env python3
"""P2-AR-0028 evidence adapter — NOT product code, and NOT used for any WS-7 class claim.

Purpose: show that the capabilities OTHER families' probes exercise with hand-declared fixture plugins (beta-r C5/D4/D5,
gamma-r F5, ...) still work once those fixture plugins are registered the governed way, which BC-P2-39 now requires.

Before passing an invocation on (through the round-1 integration adapter gov-owner-channel-shim.py, unmodified), this
wrapper looks at the project's plugin descriptors and, for every descriptor that is UNREGISTERED and refused only for
that reason (`plugins list` denial with details.cause == UNREGISTERED_EXECUTABLE), performs the governed registration:
`plugins register` as orchestrator -> `gate present` -> the product owner's signed answer A (WS-3's test signer, via the
integration adapter's relay) -> `plugins register` again. It never touches a descriptor that is registered, mismatched,
unbound, invalid or refused for any other reason, so a probe's tamper/drift/authority checks keep their meaning; it
never registers a descriptor whose file name is not `<plugin_id>.yaml` (reported instead). A probe's own
`plugins register` that raises a registration gate has that gate presented and answered A by the owner (the same
relay), and is then run again; the probe sees the final result. Every action is logged to
$P2AR0022_SHIM_LOG. Environment: as gov-owner-channel-shim.py (P2AR0022_REAL_GOV, P2AR0022_HC_OWNER) plus
P2AR0028_SHIM (path of gov-owner-channel-shim.py).
"""
import glob
import json
import os
import subprocess
import sys

REAL = os.environ["P2AR0022_REAL_GOV"]
SHIM = os.environ["P2AR0028_SHIM"]
LOG = os.environ.get("P2AR0022_SHIM_LOG")
SKIP = {"init", "plugins", "version", "contract", "oracle", "trust", "gate", "decide"}


def log(msg):
    if LOG:
        with open(LOG, "a") as f:
            f.write("[ws07-preregister] " + msg + "\n")


def opt(lst, name):
    return lst[lst.index(name) + 1] if name in lst and lst.index(name) + 1 < len(lst) else None


def shim(*args):
    p = subprocess.run([sys.executable, SHIM, "--json", *args], capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"ok": False}


def owner_approves_registration(argv, root):
    """A probe's own `plugins register`: when it raises a gate, the owner answers A and the registration is re-run."""
    p = subprocess.run([sys.executable, SHIM, *argv], capture_output=True, text=True)
    try:
        v = json.loads(p.stdout)
    except Exception:
        sys.stdout.write(p.stdout)
        sys.stderr.write(p.stderr)
        return p.returncode
    gate = (v.get("result") or {}).get("human_gate")
    if v.get("ok") and not (v.get("result") or {}).get("registered") and gate and not (v.get("result") or {}).get("declined"):
        base = ["--root", root, "--role", "orchestrator", "--session", "S-ws07-prereg"]
        shim(*base, "gate", "present", gate)
        a = shim("--root", root, "--role", "human", "--session", "S-owner", "decide", gate, "--option", "A", "--by", "owner")
        log(f"probe's plugins register raised {gate}: owner answered A (ok={a.get('ok')}); registration re-run")
        p = subprocess.run([sys.executable, SHIM, *argv], capture_output=True, text=True)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    return p.returncode


def main():
    argv = sys.argv[1:]
    words = [a for a in argv if not a.startswith("-")]
    root = opt(argv, "--root") or os.getcwd()
    first = next((a for i, a in enumerate(argv) if not a.startswith("-") and (i == 0 or argv[i - 1] not in ("--root", "--role", "--session"))), "")
    if first == "plugins" and "register" in argv:
        sys.exit(owner_approves_registration(argv, root))
    pdir = os.path.join(root, "governance", "project", "plugins")
    if first and first not in SKIP and os.path.isdir(pdir) and glob.glob(os.path.join(pdir, "*.y*ml")):
        base = ["--root", root, "--role", "orchestrator", "--session", "S-ws07-prereg"]
        lst = shim(*base, "plugins", "list")
        for d in (lst.get("result") or {}).get("denied", []):
            if ((d.get("details") or {}).get("details") or {}).get("cause") != "UNREGISTERED_EXECUTABLE" and \
                    (d.get("details") or {}).get("cause") != "UNREGISTERED_EXECUTABLE":
                continue
            src = d.get("source") or ""
            pid = d.get("plugin_id")
            if os.path.basename(src) not in (f"{pid}.yaml", f"{pid}.yml"):
                log(f"not registering {pid}: descriptor file {src} is not named after the plugin id")
                continue
            r = shim(*base, "plugins", "register", "--descriptor", src)
            res = r.get("result") or {}
            gate = res.get("human_gate")
            if res.get("registered"):
                log(f"registered {pid} (no gate needed)")
                continue
            if not gate:
                log(f"could not register {pid}: {r.get('error')}")
                continue
            shim(*base, "gate", "present", gate)
            a = shim("--root", root, "--role", "human", "--session", "S-owner", "decide", gate, "--option", "A", "--by", "owner")
            r2 = shim(*base, "plugins", "register", "--descriptor", src)
            log(f"registered {pid} through gate {gate}: answer ok={a.get('ok')} registered={(r2.get('result') or {}).get('registered')}")
    os.execv(sys.executable, [sys.executable, SHIM, *argv])


if __name__ == "__main__":
    main()
