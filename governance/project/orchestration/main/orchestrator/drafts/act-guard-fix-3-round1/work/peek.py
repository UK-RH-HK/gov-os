"""Structural peek at a corpus row: heredoc operators, delimiter lines, and Python write calls (no secrets shown)."""
import json, os, re, sys
c = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus.json")))
i = int(sys.argv[1])
cmd = c[i]["input"]["command"]
lines = cmd.split("\n")
print("lines:", len(lines))
for n, l in enumerate(lines):
    if "<<" in l or l.strip() in ("EOF", "PYEOF") or re.search(r"open\(|write_text|\.replace\(", l):
        print(n, repr(l[:160]))
print("last line:", repr(lines[-1][:120]))
