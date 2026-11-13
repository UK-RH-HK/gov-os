"""Fills ACT-CLAUDE-COPIES-8.package.md from the two bundles' manifests and rehearsal logs and the operator gates' output
(drafts/claude-copies-8/gates-<act>.json)."""
import hashlib, json, re
from pathlib import Path

ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
D = ORCH / "drafts/claude-copies-8"
FORMS = {"D": "ACT-CLAUDE-COPIES-8", "W": "ACT-CLAUDE-COPIES-8-with-sources"}
out = (D / "package.tmpl.md").read_text()
gates = []
for k, act in FORMS.items():
    B = ORCH / "acts" / act
    raw = (B / "manifest.json").read_bytes()
    H = hashlib.sha256(raw).hexdigest()
    m = json.loads(raw)
    log = (B / "rehearsal.log").read_text().splitlines()
    g = json.loads((D / f"gates-{act}.json").read_text())
    assert g["manifest_sha256"] == H, act
    rows = "\n".join(f"| `{t['path']}` | `{t['before']}` | `{t['after']}` |" for t in m["touched"])
    start = log.index(next(l for l in log if l.startswith("--- the gated runs")))
    end = log.index("--- the by-hand steps literally")
    gated = "\n".join(f"       {l.strip()}" for l in log[start + 1:end])
    ostart = log.index(next(l for l in log if l.startswith("--- out of order")))
    ooo = "\n".join(f"   - {l[5:].strip()}" for l in log[ostart + 1:start])
    port = next(l for l in log if l.strip().startswith("portability before the apply")).strip()
    port = port.replace("portability before the apply: ", "")
    fails = re.findall(r"^failures: (\d+)", "\n".join(log), re.M)[-1]
    out = (out.replace(f"{{SHA_{k}}}", H).replace(f"{{SHA8_{k}}}", H[:8]).replace(f"{{ROWS_{k}}}", rows)
           .replace(f"{{N_{k}}}", str(len(m["touched"]))).replace(f"{{GATED_{k}}}", gated)
           .replace(f"{{FAILS_{k}}}", fails).replace(f"{{CLASS_{k}}}", f"({g['act_class']})")
           .replace(f"{{PORT_{k}}}", port))
    if k == "D":
        out = out.replace("{OOO}", "   Default form:\n" + ooo + "\n{OOO}")
    else:
        out = out.replace("{OOO}", "   With-sources form:\n" + ooo)
    rowtxt = "; ".join(f"`{p}` {r} ({c})" for p, r, c in g["rows"])
    gates.append(f"- `{act}`: check_act {g['check_act']}; validate_manifest {g['validate_manifest']}; path_rule "
                 f"{g['path_rule']}; hash mismatches {g['hash_mismatches']}, unnamed on disk {g['unnamed_on_disk']}; "
                 f"act_class **({g['act_class']})**, hits {g['hits']}; rows: {rowtxt}.")
out = out.replace("{GATES}", "\n".join(gates))
left = re.findall(r"\{[A-Z_0-9]+\}", out)
assert not left, left
(ORCH / "acts/ACT-CLAUDE-COPIES-8.package.md").write_text(out)
for k, act in FORMS.items():
    print(act, hashlib.sha256((ORCH / "acts" / act / "manifest.json").read_bytes()).hexdigest())
