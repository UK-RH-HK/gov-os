"""Build the B3 settings files under /tmp/claude-1000/b3-probe/ (the launcher's block as built, W2-56, plus one variant of allowedDomains)."""
import json, os, sys
W = "/tmp/claude-1000/b3-probe"; HOME = os.path.expanduser("~"); P1, P2 = 47311, 47312
VARIANTS = {
  "A":     [],                       # the launcher's block as built (control)
  "H127":  ["127.0.0.1"],
  "HLH":   ["localhost"],
  "PS127": [f"127.0.0.1:{P1}"],
  "PSLH":  [f"localhost:{P1}"],
}
for name, domains in VARIANTS.items():
    out = f"{W}/out-{name}"; os.makedirs(out, exist_ok=True)
    s = {"env": {"PROBE_OUT": out, "PROBE_P1": str(P1), "PROBE_P2": str(P2), "GOV_STORE": "/home/usain/gov-os-worktrees/W2-00-store"},
         "permissions": {"allow": [f"Bash(python3 -I {W}/probe.py)", f"Bash(python3 -I {W}/retr.py)", f"Bash(python3 -I {W}/health.py)", f"Bash(python3 -I {W}/alias.py)"]},
         "sandbox": {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                     "network": {"strictAllowlist": True, "allowedDomains": domains,
                                 "allowUnixSockets": [f"{HOME}/.cache/gov-os/rerank.sock"]},
                     "filesystem": {"allowWrite": [f"/{out}", f"//{HOME[1:]}/.cache/gov-os/rerank.log"]}}}
    json.dump(s, open(f"{W}/settings-{name}.json", "w"), indent=1)
print(sorted(VARIANTS))
