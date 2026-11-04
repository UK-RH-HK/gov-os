# W2-32 test designer, S7: one case's premise (the CTO)

`gov accept W2-32` outside the sandbox on the engineer's head (`eb24e57a`): every line passes but S7 (4 of 6). One of the
two reds is the case's, not the code's: `test_w2_32_s7_whole_chunk.py::test_the_embedder_reads_the_whole_chunk_and_the_semantic_route_finds_words_past_the_old_cut`.
Its first check (the stand-in was sent the whole chunk of `docs/ferry-office.md`) passes. Its second (the long note is the
semantic route's **first** hit) fails because of the stand-in's similarity, not a cut: `stand_in_vector` is a bag of words
compared by cosine, and `LONG_TEXT` is seven lines of repeated filler with the question's words in its last line only, so the
filler words dominate its vector and a short note sharing the question's common words ("the", "at", "to") ranks first. The
first hit would fail at any cut. Revise the case so its second check tests what S7 says (the words past the old cut now
reach the semantic route): e.g. the long note is in the semantic route's hits, or it ranks above where it ranks with the
text cut at 512 (plant both in a scratch copy and compare), or the stand-in scores the planted words without the filler
drowning them; keep it red on code that cuts the chunk at 512 (plant it in a scratch copy, never committed). Same rules as
before (stand-ins only, no `gov retrieve`, the real-model exclusion, the `ps` check; do not merge: the CTO merges). Commit
with `Task: DAEO-0pyc`, `Implements: DEC-1066`, `Role: independent-test-designer`, `Rewrite-Reason: S7's first-hit premise
(the stand-in's bag of words, not the cut)`, Co-Authored-By. Return the twelve fields, brief.
