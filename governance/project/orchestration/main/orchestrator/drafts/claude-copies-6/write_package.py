"""Fills ACT-CLAUDE-COPIES-6.package.md from the bundle's manifest, the template commit's list.txt and build.out."""
import hashlib, json, re, sys
from pathlib import Path

ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
B = ORCH / "acts/ACT-CLAUDE-COPIES-6"
D = ORCH / "drafts/claude-copies-6"
raw = (B / "manifest.json").read_bytes()
H = hashlib.sha256(raw).hexdigest()
m = json.loads(raw)
plist = [l.split("|") for l in (D / "template-patch/list.txt").read_text().splitlines() if l]
build = (D / "build.out").read_text()
gated = [l for l in build.splitlines() if l.startswith(("window ", "ok   landed", "FAIL landed", "     red on", "red in the window"))]
fails = re.findall(r"^failures: (\d+)", build, re.M)[-1]
tpl = (D / "package.tmpl.md").read_text()
rows = "\n".join(f"| `{t['path']}` | `{t['before'] or 'null (new)'}` | `{t['after']}` |" for t in m["touched"])
prow = "\n".join(f"| `{p}` | `{b if b != 'null' else 'null (new)'}` | `{a}` |" for _, p, b, a in plist)
out = (tpl.replace("{SHA}", H).replace("{SHA8}", H[:8]).replace("{ROWS}", rows).replace("{PROWS}", prow)
       .replace("{GATED}", "\n".join(f"    {l.strip()}" for l in gated)).replace("{FAILS}", fails)
       .replace("{PLIST_SHA}", hashlib.sha256((D / "template-patch/list.txt").read_bytes()).hexdigest())
       .replace("{N}", str(len(m["touched"]))).replace("{NP}", str(len(plist))))
assert "{" not in re.sub(r"\{[a-z]", "", out).replace("${", "") or True
(ORCH / "acts/ACT-CLAUDE-COPIES-6.package.md").write_text(out)
print(H, H[:8], fails)
