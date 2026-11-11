"""scratch: replace the fenced diff in section 3 of the package with verdict.diff + operator_run.diff (indented 4 spaces)."""
import re, sys
H = sys.argv[1]
md = open(H + "/ACT-OPERATOR-ROUNDS-1.md", encoding="utf-8").read()
d1 = open(H + "/verdict.diff", encoding="utf-8").read().rstrip("\n")
d2 = open(H + "/operator_run.diff", encoding="utf-8").read().rstrip("\n")
body = "\n".join("    " + l if l else "    " for l in (d1 + "\n" + d2).split("\n"))
new, n = re.subn(r"(## 3\. The two diffs.*?```diff\n).*?(\n```\n\(The file diffs)", lambda m: m.group(1) + body + m.group(2), md, count=1, flags=re.S)
assert n == 1
open(H + "/ACT-OPERATOR-ROUNDS-1.md", "w", encoding="utf-8").write(new)
print("embedded", len(body.splitlines()), "diff lines")
