"""Rule 5's boundaries (ACT-GUARD-FIX-4): the reviews/ folder and the rest, under today's hook and the candidate."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hookrun import run  # noqa: E402

H4 = os.path.join(os.path.dirname(HERE), "pretooluse.py")
H3 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "act-guard-fix-3", "pretooluse.py")
M = "/home/usain/Dynamic-Agentic-Engineering-OS"
S = M + "/.gov-runtime/scratch/orchestrator"
R = S + "/reviews"
WQ = "/home/usain/gov-os-worktrees/EMG-queue"


def W(p):
    return "Write", {"file_path": p, "content": "x"}


def B(c):
    return "Bash", {"command": c}


cases = [W(R + "/x-review.md"), W(R + "/sub/x.md"), B(f"mkdir -p {R} && cat > {R}/x.md <<'EOF'\nx\nEOF"),
         B(f"cd {S} && echo x > reviews/x.md"), B(f"rm -rf {R}"), B(f"mkdir -p {R}; rm -rf {R}"),
         B(f"mv {R} /tmp/gov-fix4-r"), W(R + "/../briefs/x.md"), W(R + "x/a.md"), W(S + "/briefs/x.md"),
         W(M + "/src/gov/x.py"), W(M + "/tests/unit/x.py"), W(M + "/tests/" + "acceptance/W2-64/t.py"),
         B(f"echo x > {S}/log/x.jsonl"), W(WQ + "/.gov-runtime/scratch/orchestrator/reviews/x.md"),
         W(WQ + "/src/gov/x.py"), B(f"mkdir -p {S}"), B("mkdir -p docs/probes && echo x > docs/probes/r.md")]
for role, agent in (("independent-auditor", None), ("orchestrator", "independent-auditor"),
                    ("independent-reviewer", None)):
    for tool, tin in cases:
        a3 = run(H3, role, tool, tin, cwd=S, root=M, agent=agent)
        a4 = run(H4, role, tool, tin, cwd=S, root=M, agent=agent)
        print(f"{role[:12]:12} {str(agent)[:6]:6} {a3[0]:5}->{a4[0]:5} {tool:5} {str(list(tin.values())[0])[-80:]!r}")
