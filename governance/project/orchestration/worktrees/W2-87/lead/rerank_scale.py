"""Lead's probe: the pinned reranker's score scale, on four texts (W2-87 design note)."""
import json
import sys

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-87/src")
from gov.retrieval.rerank import default_reranker  # noqa: E402

score = default_reranker()
if score is None:
    print("no reranker")
    raise SystemExit(1)
query = "how does retrieval drop superseded decisions"
texts = ["[path: docs/DECISION_REGISTER.md]\nSuperseded comes from the store: status SUPERSEDED, or being the target of a supersedes edge.",
         "[path: tests/unit/x.py]\ndef test_superseded_dropped(): assert retrieve(...)",
         "[path: docs/recipes.md]\nBake the bread for forty minutes.",
         "[path: src/gov/retrieval/retrieve.py]\n# DEC-329, G-19: superseded records\nif record_id in not_current: continue"]
print(json.dumps(score(query, texts)))
