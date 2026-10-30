"""Fill <<DESIGN>> in a brief draft with the design note's sections 1 to 9. Args: draft, design, output."""
import sys

draft, design, out = sys.argv[1:4]
text = open(design, encoding="utf-8").read()
body = text[text.index("## 1."):].replace("\n## ", "\n### ")
body = "### " + body[3:] if body.startswith("## ") else body
filled = open(draft, encoding="utf-8").read().replace("<<DESIGN>>", body.strip())
assert "<<DESIGN>>" not in filled
open(out, "w", encoding="utf-8").write(filled)
print(len(filled.splitlines()), "lines")
