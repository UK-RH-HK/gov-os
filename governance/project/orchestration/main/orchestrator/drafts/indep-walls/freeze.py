"""ACT-INDEP-WALLS-1: write the built files' sha256s into apply.sh (idempotent), and the two review diffs."""
import hashlib, os, re, subprocess
H = os.path.dirname(os.path.abspath(__file__))
sha = lambda p: hashlib.sha256(open(os.path.join(H, p), "rb").read()).hexdigest()
vals = {"AFTER_HOOK": sha("pretooluse.candidate.py"), "AFTER_MAP": sha("path-map.candidate.yaml")}
names = {"README.md": "SHA_README", "settings.json.tmpl": "SHA_SETTINGS", "wall_hook.py": "SHA_HOOK",
         "CLAUDE.md.tmpl": "SHA_CLAUDE", "kinds.yaml": "SHA_KINDS", "tree-exclude.txt": "SHA_EXCLUDE"}
s = open(os.path.join(H, "apply.sh")).read()
for k, v in vals.items():
    s = re.sub(rf"^{k}=\S+$", f"{k}={v}", s, flags=re.M)
for n, k in names.items():
    s = re.sub(rf"^  \[{re.escape(n)}\]=\S+$", f"  [{n}]={sha('template/' + n)}", s, flags=re.M)
open(os.path.join(H, "apply.sh"), "w").write(s)
M = "/home/usain/Dynamic-Agentic-Engineering-OS"
for live, cand, out, label in ((".claude/hooks/pretooluse.py", "pretooluse.candidate.py", "pretooluse.diff", ".claude/hooks/pretooluse.py"),
                               ("governance/project/path-map.yaml", "path-map.candidate.yaml", "path-map.patch", "governance/project/path-map.yaml")):
    d = subprocess.run(["diff", "-u", "--label", "a/" + label, "--label", "b/" + label,
                        os.path.join(M, live), os.path.join(H, cand)], capture_output=True, text=True).stdout
    open(os.path.join(H, out), "w").write(d)
for p in ("pretooluse.candidate.py", "path-map.candidate.yaml", "pretooluse.diff", "path-map.patch", "apply.sh",
          "build_wall.py", "walls_check.py", *("template/" + n for n in names)):
    print(sha(p)[:12], p)
