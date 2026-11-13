from pathlib import Path
RW = "# Rewrite-Reason: DEC-1159 (2) (MAX_REQUEST_CHARS 24,000 -> 48,000; the pair read stays 24,000)\n"
def sub(path, old, new):
    p = Path(path); s = p.read_text(); assert s.count(old) == 1, (path, old[:50], s.count(old)); p.write_text(s.replace(old, new))

a = "tests/unit/retrieval/test_w2_137_request_cap.py"
sub(a, "    assert rerank.MAX_REQUEST_CHARS == 24_000  # the padded bound stays\n",
    "    " + RW + "    assert rerank.MAX_REQUEST_CHARS == 48_000  # the padded bound (DEC-1159 (2)); a pair is still read to 24,000\n")
sub(a, "    per_request = rerank.MAX_REQUEST_CHARS // (len(QUERY) + 2_000)  # 11: the padded bound binds, not the count\n",
    "    " + RW + "    per_request = rerank.MAX_REQUEST_CHARS // (len(QUERY) + 2_000)  # 23: the padded bound binds, not the count\n")
sub(a, """    texts = ["l" * 23_000] + _short(POOL_DEPTH - 1)
    groups = rerank.requests(QUERY, texts)
    assert [indices for indices, _ in groups] == [[0], list(range(1, POOL_DEPTH))]
""", """    texts = ["l" * 23_000] + _short(POOL_DEPTH - 1)
    groups = rerank.requests(QUERY, texts)
    # DEC-1159 (2): the bound holds two pairs of 23,000, so the long one takes the first short one with it and no
    # more: the other 38 short ones are never padded to 23,000
    assert [indices for indices, _ in groups] == [[0, 1], list(range(2, POOL_DEPTH))]
""")
sub(a, "    assert indices == [0] and len(QUERY) + len(texts[0]) == rerank.MAX_REQUEST_CHARS\n",
    "    " + RW + "    assert indices == [0] and len(QUERY) + len(texts[0]) == rerank.MAX_PAIR_CHARS\n")

b = "tests/unit/retrieval/test_w2_32_whole_chunk.py"
sub(b, """    # the reranker: up to one request's size bound (DEC-1067 (f)), above the chunker's MAX_CHARS
    from gov.retrieval import rerank
    assert fusion.RERANK_CHARS == fusion.RERANK_LIMIT_CHARS == rerank.MAX_REQUEST_CHARS == 24_000
""", """    # the reranker: up to one pair's size bound (DEC-1067 (f); the request bound is 48,000), above the chunker's MAX_CHARS
    from gov.retrieval import rerank
    """ + RW + """    assert fusion.RERANK_CHARS == fusion.RERANK_LIMIT_CHARS == rerank.MAX_PAIR_CHARS == 24_000
""")
sub(b, "    room = rerank.MAX_REQUEST_CHARS - len(query)\n", "    " + RW + "    room = rerank.MAX_PAIR_CHARS - len(query)\n")
sub(b, """    groups = rerank.requests(query, ["x" * 23_000] + ["y" * 50] * 15)
    assert [len(indices) for indices, _ in groups] == [1, 15]  # the long one alone, the 15 short ones together
""", """    groups = rerank.requests(query, ["x" * 23_000] + ["y" * 50] * 15)
    """ + RW + """    assert [len(indices) for indices, _ in groups] == [2, 14]  # the long one with one short; the others together
""")
sub(b, """    assert shape([9_000] * 5) == [(2, 18020), (2, 18020), (1, 9010)]  # the padded size binds
    # in the given order, pairs of 1,000 and 7,000 would make four requests; grouped by length, two
    assert shape([1_000, 7_000, 1_000, 7_000, 1_000, 7_000, 1_000]) == [(3, 21030), (4, 4040)]
""", """    """ + RW + """    assert shape([9_000] * 5) == [(5, 45050)]  # the padded size binds (48,000 / 9,010: five fit)
    assert shape([9_000] * 6) == [(5, 45050), (1, 9010)]
    # grouped by length: the three 7,000 with three of the 1,000, then the last 1,000
    assert shape([1_000, 7_000, 1_000, 7_000, 1_000, 7_000, 1_000]) == [(6, 42060), (1, 1010)]
""")
sub(b, "    assert indices == [0] and len(query) + len(texts[0]) == rerank.MAX_REQUEST_CHARS\n",
    "    " + RW + "    assert indices == [0] and len(query) + len(texts[0]) == rerank.MAX_PAIR_CHARS\n")

c = "tests/unit/retrieval/test_w2_112_shared_reranker.py"
sub(c, """    # DEC-1090 (2): the texts' cap raised from 16 to 64; the padded bound and the service's bound as they were
    assert (rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS, rerank_service.MAX_TEXTS) == (64, 24_000, 512)""",
"""    # DEC-1090 (2): the texts' cap raised from 16 to 64; DEC-1159 (2): the padded bound from 24,000 to 48,000; the
    # service's bound as it was
    """ + RW + """    assert (rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS, rerank_service.MAX_TEXTS) == (64, 48_000, 512)""")
