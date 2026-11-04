# W2-32 test designer, S7: the continuation case's premise (the CTO)

`gov accept W2-32` outside the sandbox on the engineer's head with your revision merged (`60e19d63`): 92 passed, 1 failed,
every line passes but S7 (5 of 6). The red: `test_w2_32_s7_whole_chunk.py::test_across_continuations_no_span_is_sent_twice`
fails its own premise: "premise: a later bundle holds another chunk of the almanac's section". The engineer's fix
(`0222b25b`) leaves out a chunk whose parent an earlier call already expanded, and **names it in the bundle** (its
evidence: a span inside a parent an earlier call sent is left out and named), so no later bundle carries another almanac
chunk. Revise the case so its premise accepts what S7 asks for: either a later bundle holds another chunk of the section,
or it names such a chunk as left out (already sent within an expanded parent); the check (no span sent twice, contained
spans included) stays; keep it red on code that sends the span again (planted in a scratch copy, never committed). Same
rules as before; commit with `Task: DAEO-0pyc`, `Implements: DEC-1066`, `Role: independent-test-designer`,
`Rewrite-Reason: S7's continuation premise (a left-out span is named, not sent)`, Co-Authored-By. Return the twelve fields,
brief.
