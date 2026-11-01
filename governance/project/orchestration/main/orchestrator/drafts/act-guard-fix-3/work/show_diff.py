"""Print differential commands by index (redacted, cut). Usage: show_diff.py N [index ...]"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{8,}|xox[bp]-[\w-]+|AKIA[0-9A-Z]{12,}|"
                    r"(?i:(?:token|secret|password|api[_-]?key)\s*[=:]\s*)[^\s'\"]{6,}|[A-Za-z0-9+/]{40,}={0,2})")
rows = json.load(open(os.path.join(HERE, "diff_cmds.json")))
n = int(sys.argv[1])
for i in map(int, sys.argv[2:]):
    r = rows[i]
    print(f"===== #{i} {r['role']} tmp={r['tmpdir']}")
    print(SECRET.sub("<REDACTED>", r["cmd"][:n]))
