"""Scratch: per visible gold span, the chunks holding it and whether each has a vector; corpus counts."""
import sqlite3, sys
from pathlib import Path
import yaml
from gov.retrieval.measure import _span

root = Path(sys.argv[1])
db = sqlite3.connect((root / ".gov-runtime/store.db").as_uri() + "?mode=ro", uri=True)
print("chunks", db.execute("select count(*) from lexical_chunk").fetchone(), "vectors",
      db.execute("select count(*) from semantic_vector").fetchone(), "files", db.execute("select count(*) from lexical_file").fetchone())
for qid in sys.argv[2:]:
    q = yaml.safe_load((root / "fixtures/evaluation/memory-retrieval/visible" / f"{qid}.yaml").read_text())
    for a in (a for s in q["sources"] for a in (s if isinstance(s, list) else [s])):
        p, f, l = a["path"], *_span(a, root, "visible", qid)
        rows = db.execute("select c.start_line, c.end_line, v.chunk_id is not null from lexical_chunk c left join semantic_vector v "
                          "on v.chunk_id = c.chunk_id where c.path=? and c.start_line<=? and c.end_line>=?", (p, l, f)).fetchall()
        print(qid, p, f, l, rows)
