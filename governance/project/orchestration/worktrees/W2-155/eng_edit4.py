from pathlib import Path
p = Path("src/gov/retrieval/rerank_service.py"); s = p.read_text()
old = """  below it the cache would still climb to the bound's peak and hold it beside the embedder. The cost per request is the device sync and the frees of ``empty_cache`` and the
  next request's fresh allocations, estimated at a few milliseconds against a request's hundreds (to be measured on
  the GPU in window 4)."""
new = """  below it the cache would still climb to the bound's peak and hold it beside the embedder. The cost per request is
  the device sync and the frees of ``empty_cache`` and the next request's fresh allocations, estimated at a few
  milliseconds against a request's hundreds (to be measured on the GPU in window 4)."""
assert s.count(old) == 1; p.write_text(s.replace(old, new))
