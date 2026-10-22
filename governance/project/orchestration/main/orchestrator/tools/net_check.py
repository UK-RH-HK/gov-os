"""Gate (g) of the close queue (DEC-892): the live tests' allowlisted hosts are reachable.

Reads the research allowlist the launcher reads (the kernel's and the project's `research-allowlist.yaml`) and asks
each plain host for an HTTPS answer within 20 s; any HTTP status counts as reachable (a 403 at a site's root is an
answer). Wildcard entries (`*.readthedocs.io`) are checked at the host W1-46's live case uses. Prints one line per
unreachable host; exits 1 if any.
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
hosts = []
for rel in ("template/governance/kernel/launch/research-allowlist.yaml", "governance/project/research-allowlist.yaml"):
    p = ROOT / rel
    if p.is_file():
        hosts += (yaml.safe_load(p.read_text()) or {}).get("hosts") or []
checked = sorted({("docs.readthedocs.io" if h == "*.readthedocs.io" else h) for h in hosts if isinstance(h, str)
                  and "*" not in h.replace("*.readthedocs.io", "")})
bad = []
for host in checked:
    done = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", f"https://{host}/"],
                          capture_output=True, text=True)
    if done.returncode != 0 or done.stdout.strip() in ("", "000"):
        bad.append(host)
        print(f"unreachable: {host} ({done.stderr.strip()[:120] or done.stdout})")
print(f"allowlisted hosts checked: {len(checked)}; unreachable: {len(bad)}")
sys.exit(1 if bad else 0)
