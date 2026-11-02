"""Time the per-question cost the retrieval checks pay: ensure_query_available() (answering server: nothing started),
20 calls, and one fresh query embedding at the real query server (a read). time_ensure.py"""
import json
import time

from gov.retrieval import ollama, semantic

began = time.monotonic()
for _ in range(20):
    result = ollama.ensure_query_available()
per_call = (time.monotonic() - began) / 20
began = time.monotonic()
vectors = semantic._embed([semantic.INSTRUCTION + f"timing probe {time.time()}"], ollama.query_host())
print(json.dumps({"module": ollama.__file__, "ensure_query_available_s": round(per_call, 4),
                  "available": result["available"], "started": result["started"],
                  "one_fresh_query_embed_s": round(time.monotonic() - began, 2), "vector": vectors is not None}))
