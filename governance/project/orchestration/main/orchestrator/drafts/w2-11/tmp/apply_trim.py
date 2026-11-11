"""Trim the resolved orchestration skill to the 2,500-token cap (10,000 body characters), scratch only.

Reads resolved/orchestration.md, writes resolved/orchestration-trim.md and prints the body size.
Each (old, new) pair must match exactly once.
"""
import math
import re
import sys
from pathlib import Path

base = Path(__file__).parent / "resolved"
text = (base / "orchestration.md").read_text()

CUTS = [
    # 1 the retired-pointer sentence of the Briefs line (integrate's; the role templates are named in full before it)
    (" The retired texts `brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md` and `brief-lead.md` are one-line pointers to these templates (DEC-1050).", ""),
    # 2 the work-order bullet of the loop
    ("; then the verification, on the ticket's acceptance tests, the scoped selection and the builder tests, once (MR-3, DEC-968).",
     "; then one scoped verification (MR-3, DEC-968)."),
    # 3 the three reference links
    ("The merge queue: [integration-queue.md](integration-queue.md). A red nightly: [nightly-sheriff.md](nightly-sheriff.md). An Emergency: [incident-response.md](incident-response.md).",
     "Merge queue, red nightly, Emergency: [integration-queue.md](integration-queue.md), [nightly-sheriff.md](nightly-sheriff.md), [incident-response.md](incident-response.md)."),
]
if len(sys.argv) > 1:
    extra = Path(sys.argv[1])
    exec(extra.read_text())  # noqa: S102 (scratch only: adds to CUTS)

for old, new in CUTS:
    if text.count(old) != 1:
        print("NO UNIQUE MATCH:", old[:70])
        continue
    text = text.replace(old, new)
(base / "orchestration-trim.md").write_text(text)
body = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S).group(2)
print("body chars", len(body), "tokens", math.ceil(len(body) / 4))
