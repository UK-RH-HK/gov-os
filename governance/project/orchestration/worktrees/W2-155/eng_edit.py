import re
from pathlib import Path
def sub(path, old, new):
    p = Path(path); s = p.read_text(); assert s.count(old) == 1, (path, old[:40], s.count(old)); p.write_text(s.replace(old, new))

r = "src/gov/retrieval/rerank.py"
sub(r, """# And the most characters one request carries, padded (the CTO's bound after the GPU backstop of 2026-11-04 03:53 and
# 05:37: the reranker pads every pair of a batch to the longest, so one 23,000-character chunk with 15 short ones is a
# batch of 16 x 23,000). Counted as the service scores, by pair (each text with the question): a request's size is its
# count times its longest pair, ``count * max(len(query) + len(text))``; the model's own fixed instruction (about 80
# characters a pair) is not counted and sits in the margin.
MAX_REQUEST_CHARS = 24_000
""", """# The most characters one pair, the question and a text, is read to: a longer text is cut so its pair is at most this
# (the CTO's bound after the GPU backstop of 2026-11-04 03:53 and 05:37, DEC-1067 (f): one 23,000-character chunk
# is a pair of 23,000). It was the request bound too until DEC-1159 (2); it stays what a text is read up to, so the
# results of ``gov retrieve`` do not change when the request bound rises (``fusion.RERANK_LIMIT_CHARS`` is this).
MAX_PAIR_CHARS = 24_000
# And the most characters one request carries, padded: the reranker pads every pair of a batch to the longest, so a
# request's size is its count times its longest pair, ``count * max(len(query) + len(text))``, counted as the service
# scores, by pair (each text with the question); the model's own fixed instruction (about 80 characters a pair) is
# not counted and sits in the margin. Raised from 24,000 to 48,000 by DEC-1159 (2), W2-155: a search's ~30 whole-chunk
# candidates (~1,300 characters each, ~39,000 padded) went in two requests, each costing a fixed 60-85 ms model
# forward, and now go in one. The lead's GPU reading: the worst request at the bound (2 pairs of 24,000) peaked
# +1,384 MiB, within the card's budget of total less 2,048 MiB.
MAX_REQUEST_CHARS = 48_000
""")
sub(r, """    \"\"\"The fewest requests, each of at most ``MAX_REQUEST_TEXTS`` texts and of at most ``MAX_REQUEST_CHARS`` padded
    characters (its count times its longest pair, ``len(query) + len(text)``): ``(indices, texts)``, the indices into
    ``texts``. The texts are grouped longest first: each request takes the longest left and as many of the next
    longest as fit, which is the fewest (a request's size is set by its longest text). A text whose pair alone is
    above the budget is read up to it, as a chunk is read up to ``fusion.RERANK_LIMIT_CHARS``.\"\"\"
    room = max(0, MAX_REQUEST_CHARS - len(query))""", """    \"\"\"The fewest requests, each of at most ``MAX_REQUEST_TEXTS`` texts and of at most ``MAX_REQUEST_CHARS`` padded
    characters (its count times its longest pair, ``len(query) + len(text)``): ``(indices, texts)``, the indices into
    ``texts``. The texts are grouped longest first: each request takes the longest left and as many of the next
    longest as fit, which is the fewest (a request's size is set by its longest text). A text whose pair is above
    ``MAX_PAIR_CHARS`` (24,000) is read up to it, as a chunk is read up to ``fusion.RERANK_LIMIT_CHARS``; the
    request bound (48,000) is the other limit, so a request holds two such pairs at most.\"\"\"
    room = max(0, MAX_PAIR_CHARS - len(query))""")
sub(r, "no request to any reranker,\n    the shared service or one given, carries more.", "no request to any reranker,\n    the shared service or one given, carries more (48,000 since DEC-1159 (2)); each text is read up to ``MAX_PAIR_CHARS``.")

f = "src/gov/retrieval/fusion.py"
sub(f, "from gov.retrieval.rerank import MAX_REQUEST_CHARS, last_outcome, rerank", "from gov.retrieval.rerank import MAX_PAIR_CHARS, last_outcome, rerank")
sub(f, """# the size bound of one request (``rerank.MAX_REQUEST_CHARS``, 24,000), so one chunk can always be sent. The service
# sets no length of its own; its memory is bounded by a request's 16 texts and 24,000 characters, and a pair still
# above the bound (the path and the question added) is read up to it by ``rerank.requests``.
RERANK_LIMIT_CHARS = MAX_REQUEST_CHARS""", """# the most one pair is read to (``rerank.MAX_PAIR_CHARS``, 24,000), so one chunk can always be sent. The service
# sets no length of its own; its memory is bounded by a request's texts and its padded size (``rerank.MAX_REQUEST_CHARS``,
# 48,000 since DEC-1159 (2), W2-155; the pair read stays 24,000), and a pair still above 24,000 (the path and the
# question added) is read up to it by ``rerank.requests``.
RERANK_LIMIT_CHARS = MAX_PAIR_CHARS""")
sub("src/gov/retrieval/chunking.py", "# (one request's size bound, ``rerank.MAX_REQUEST_CHARS``, DEC-1067 (f)).", "# (the pair read, ``rerank.MAX_PAIR_CHARS``, 24,000; the request bound ``rerank.MAX_REQUEST_CHARS`` is 48,000, DEC-1159 (2)).")
