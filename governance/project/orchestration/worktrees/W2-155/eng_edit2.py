from pathlib import Path
def sub(path, old, new):
    p = Path(path); s = p.read_text(); assert s.count(old) == 1, (path, old[:40]); p.write_text(s.replace(old, new))
sub("src/gov/retrieval/chunking.py", "# (the pair read, ``rerank.MAX_PAIR_CHARS``, 24,000; the request bound ``rerank.MAX_REQUEST_CHARS`` is 48,000, DEC-1159 (2)).",
"# (the pair read, ``rerank.MAX_PAIR_CHARS``, 24,000; a request's bound, ``rerank.MAX_REQUEST_CHARS``, is 48,000).")
sub("src/gov/retrieval/rerank_service.py", "``rerank.MAX_REQUEST_CHARS``, already sets the largest), and below it the cache would still climb to the bound's peak",
"``rerank.MAX_REQUEST_CHARS``, 48,000 since DEC-1159 (2), already sets the largest; a pair is read to 24,000), and below it\n  the cache would still climb to the bound's peak")
