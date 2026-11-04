# W2-32 engineer, S7: two reds (the CTO)

The CTO merged into `w2/W2-32` outside the sandbox (do not merge yourself): the designer's S7 tests and the revised S2
cut cases (`8de8f68a`: S2's two cases now ask for a recorded cut, not 512; the ticket's interface says the same) and
today's integration head (`eb24e57a`). `gov accept W2-32` outside the sandbox: 91 passed, 2 failed; every line passes but
S7 (4 of 6). The two reds (names and messages only):
1. `test_w2_32_s7_whole_chunk.py::test_the_embedder_reads_the_whole_chunk_and_the_semantic_route_finds_words_past_the_old_cut`:
   "the note whose words lie past character 600 is not the semantic route's first hit: ['docs/lighthouse.md',
   'docs/almanac.md', ...]". Somewhere on the embedding path (indexing, or the question's side, or the chunker's span)
   the text is still cut short of the whole chunk.
2. `test_w2_32_s7_whole_chunk.py::test_across_continuations_no_span_is_sent_twice`: "bundle 2 sends docs/almanac.md:1-17,
   within 1-52 sent earlier": a span **contained in** an earlier one is a repeat too, not only an equal one.
Fix both inside your paths, with unit tests (stand-ins); same rules as before (no `gov retrieve`, no real model, the
exclusion on whole-folder runs, the `ps` check). The CTO re-runs `gov accept` outside the sandbox. Update the evidence
file's S7 row; commit; return the twelve fields, brief.
