"""Build the reviewer's brief: the design note, JUDGEMENT.md word for word (less its title) and the head."""
import sys

brief, design, judgement, head, out = sys.argv[1:6]
design_text = open(design, encoding="utf-8").read().split("\n", 1)[1].strip()
judgement_text = open(judgement, encoding="utf-8").read().split("\n", 1)[1].strip()
body = open(brief, encoding="utf-8").read()
body = body.replace("<<DESIGN>>", design_text).replace("<<JUDGEMENT>>", judgement_text).replace("<<HEAD>>", head)
open(out, "w", encoding="utf-8").write(body)
