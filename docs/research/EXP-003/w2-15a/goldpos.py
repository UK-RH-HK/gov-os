"""W2-15a: where each visible question's gold sits in the chunks that hold it: ``python3 goldpos.py <root> <qid>...``.
Per gold span: the chunks overlapping it (lines, chars) and the gold's first character offset inside each, against
the embedder's 512 and the reranker's 500 characters (semantic.EMBED_CHARS, fusion.RERANK_CHARS). Read-only."""
import sqlite3
import sys
from pathlib import Path

import yaml

from gov.retrieval.measure import _span

root = Path(sys.argv[1])
db = sqlite3.connect((root / ".gov-runtime/store.db").resolve().as_uri() + "?mode=ro", uri=True)
for qid in sys.argv[2:]:
    q = yaml.safe_load((root / "fixtures/evaluation/memory-retrieval/visible" / f"{qid}.yaml").read_text())
    for alt in (a for s in q["sources"] for a in (s if isinstance(s, list) else [s])):
        path, first, last = alt["path"], *_span(alt, root, "visible", qid)
        lines = (root / path).read_text(errors="replace").splitlines(keepends=True)
        rows = db.execute("SELECT start_line, end_line FROM lexical_chunk WHERE path = ? AND start_line <= ? AND "
                          "end_line >= ? ORDER BY start_line", (path, last, first)).fetchall()
        cells = []
        for s, e in rows:
            offset = sum(len(x) for x in lines[s - 1:max(first, s) - 1])
            cells.append(f"{s}-{e} ({sum(len(x) for x in lines[s - 1:e])} ch, gold at {offset})")
        print(f"{qid} {path}:{first}-{last}: " + ("; ".join(cells) or "NO CHUNK"))
