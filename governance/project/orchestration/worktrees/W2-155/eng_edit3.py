from pathlib import Path
def sub(path, old, new):
    p = Path(path); s = p.read_text(); assert s.count(old) == 1, (path, old[:40]); p.write_text(s.replace(old, new))
sub("src/gov/retrieval/rerank_service.py", """  ``rerank.MAX_REQUEST_CHARS``, 48,000 since DEC-1159 (2), already sets the largest; a pair is read to 24,000), and below it
  the cache would still climb to the bound's peak
  and hold it beside the embedder.""", """  ``rerank.MAX_REQUEST_CHARS``, 48,000 since DEC-1159 (2), already sets the largest; a pair is read to 24,000), and
  below it the cache would still climb to the bound's peak and hold it beside the embedder.""")
sub("src/gov/retrieval/fusion.py", """# sets no length of its own; its memory is bounded by a request's texts and its padded size (``rerank.MAX_REQUEST_CHARS``,
# 48,000 since DEC-1159 (2), W2-155; the pair read stays 24,000), and a pair still above 24,000 (the path and the
# question added) is read up to it by ``rerank.requests``.""", """# sets no length of its own; its memory is bounded by a request's texts and its padded size
# (``rerank.MAX_REQUEST_CHARS``, 48,000 since DEC-1159 (2), W2-155; the pair read stays 24,000), and a pair still
# above 24,000 (the path and the question added) is read up to it by ``rerank.requests``.""")
sub("src/gov/retrieval/rerank.py", """    the shared service or one given, carries more (48,000 since DEC-1159 (2)); each text is read up to ``MAX_PAIR_CHARS``. Each score goes back to its candidate, so the order is the
    unbatched one;""", """    the shared service or one given, carries more (48,000 since DEC-1159 (2)); a text is read up to ``MAX_PAIR_CHARS``
    with the question. Each score goes back to its candidate, so the order is the unbatched one;""")
