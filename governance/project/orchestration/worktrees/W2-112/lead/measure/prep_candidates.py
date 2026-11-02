"""Lead's measure, step 1: the candidates of the 20 visible questions, built from the lexical route only.

No embedder is asked (the shared Ollama servers are never touched). Each question's candidate texts take the form
the search gives the reranker: "[path: <p>]\n" and the chunk's first 500 characters, at most 30 chunks.
Usage: python3 prep_candidates.py <root> <out.json>
"""
import json
import re
import sys
from pathlib import Path

import yaml

from gov.retrieval import lexical

TOP, CHARS = 30, 500


def chunk_text(root, record):
    lines = (root / record["path"]).read_text(encoding="utf-8", errors="replace").splitlines()
    body = "\n".join(lines[record["start_line"] - 1:record["end_line"]])
    return f"[path: {record['path']}]\n{body[:CHARS]}"


def main(root, out):
    root = Path(root)
    records = {r["chunk_id"]: r for r in lexical.chunks(root)}
    questions = []
    for path in sorted((root / "fixtures/evaluation/memory-retrieval/visible").glob("*.yaml")):
        q = yaml.safe_load(path.read_text())
        query = str(q["question"])
        terms = [query] + sorted(set(re.findall(r"[A-Za-z0-9_.-]{4,}", query)), key=len, reverse=True)
        ids = []
        for term in terms:
            for hit in lexical.search(root, term, refresh=False)["hits"]:
                if hit["chunk_id"] not in ids and hit["chunk_id"] in records:
                    ids.append(hit["chunk_id"])
            if len(ids) >= TOP:
                break
        texts = [chunk_text(root, records[i]) for i in ids[:TOP]]
        questions.append({"id": q.get("id", path.stem), "query": query, "texts": texts})
    Path(out).write_text(json.dumps(questions))
    print(json.dumps([[q["id"], len(q["texts"])] for q in questions]))


if __name__ == "__main__":
    main(*sys.argv[1:3])
