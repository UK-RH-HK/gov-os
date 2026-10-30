"""Put the design note's text (less its title line) into a brief at the <<DESIGN>> marker."""
import sys

brief, design, out = sys.argv[1:4]
text = open(design, encoding="utf-8").read().split("\n", 1)[1].strip()
body = open(brief, encoding="utf-8").read().replace("<<DESIGN>>", text)
open(out, "w", encoding="utf-8").write(body)
