#!/usr/bin/env python3
"""D-7 (DEC-1052 M-4, DEC-1055 (3)) with G4 (DEC-1066 (3)): what memory embeds and what the keyword index holds.

Rewrites governance/project/path-map.yaml's namespaces as text (comments and order kept), in place:
- `docs`: split into explicit sub-folders (every path in exactly one namespace); embedded as before.
- new `doc-records`: docs/close, docs/checkpoints, docs/probes: not embedded (keyword index only).
- new `evaluation-sources`: lens B's report: not embedded, not indexed (the measure's own document, G4).
- `tests`: not embedded (keyword index only).
- `fixtures`: split; new `evaluation-fixtures` (fixtures/evaluation, fixtures/memory-quality): not embedded, not indexed.
- `project-overlay`: its record folders (closes, nightly, sessions, reviews) move to a new `orchestration-records`
  namespace: not embedded (keyword index only).
    d7_pathmap.py <path-map.yaml>
"""
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text()

# fields copied from the namespace being split, with the policies changed
def block(name, paths, src_fields, embedding, lexical=None, comment=None):
    out = [f"  # {comment}"] if comment else []
    out.append(f"  {name}:")
    out.append("    paths:")
    out += [f'      - "{x}"' for x in paths]
    for k, v in src_fields:
        if k == "embedding_policy":
            v = embedding
        out.append(f"    {k}: {v}")
        if k == "embedding_policy" and lexical:
            out.append(f"    lexical_policy: {lexical}")
    return "\n".join(out) + "\n"

def fields(name):
    m = re.search(rf"^  {re.escape(name)}:\n(    .*\n|      .*\n)+", t, re.M)
    assert m, name
    body = m.group(0)
    fs = re.findall(r"^    ([a-z_]+): (.+)$", body, re.M)
    return m, [(k, v) for k, v in fs if k != "paths"]

DOC_DIRS = ["adoption", "adr", "audit", "changes", "charter", "contract", "imported", "interfaces", "lessons", "plan",
            "releases", "research", "spec"]
ASSESS = sorted(x.name for x in (p.parent.parent.parent / "docs/assessment/2026-10").iterdir()
                if x.name != "B-memory-retrieval.md")

m, f = fields("docs")
new = block("docs", ["docs/*"] + [f"docs/{d}/**" for d in DOC_DIRS] + [f"docs/assessment/2026-10/{x}" for x in ASSESS],
            f, "embedded", comment="DEC-1052 M-4, DEC-1055 (3) (D-7): docs split so the records and the measure's own document sit apart")
new += block("doc-records", ["docs/close/**", "docs/checkpoints/**", "docs/probes/**"], f, "not embedded",
             comment="M-4: close, checkpoint and probe records stay in keyword search only")
new += block("evaluation-sources", ["docs/assessment/2026-10/B-memory-retrieval.md"], f, "not embedded", "not indexed",
             comment="DEC-1066 (3), G4: lens B's report quotes the measure's questions: out of both indexes")
t = t[:m.start()] + new + t[m.end():]

m, f = fields("tests")
t = t[:m.start()] + block("tests", ["tests/**"], f, "not embedded",
                          comment="M-4: tests stay in keyword search only; tickets link to their tests") + t[m.end():]

m, f = fields("fixtures")
fx = sorted(x.name for x in (p.parent.parent.parent / "fixtures").iterdir() if x.name not in ("evaluation", "memory-quality"))
fpaths = [f"fixtures/{x}/**" if (p.parent.parent.parent / "fixtures" / x).is_dir() else f"fixtures/{x}" for x in fx]
new = block("fixtures", fpaths, f, "not embedded")
new += block("evaluation-fixtures", ["fixtures/evaluation/**", "fixtures/memory-quality/**"], f, "not embedded",
             "not indexed", comment="DEC-1066 (3), G4: the measure's questions and W2-32's memory-quality events: out of both indexes")
t = t[:m.start()] + new + t[m.end():]

# the overlay's record folders into their own namespace
REC = ["governance/project/orchestration/closes/**", "governance/project/orchestration/nightly/**",
       "governance/project/orchestration/sessions/**", "governance/project/orchestration/reviews/**"]
m, f = fields("project-overlay")
body = m.group(0)
for r in REC:
    body = re.sub(rf'^      - "{re.escape(r)}"\n', "", body, flags=re.M)
body += block("orchestration-records", REC, f, "not embedded",
              comment="M-4: the orchestration's close, nightly, session and review records stay in keyword search only")
t = t[:m.start()] + body + t[m.end():]
p.write_text(t)
print("ok")
