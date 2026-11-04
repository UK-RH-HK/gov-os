# W2-92 engineer, S6: one red (the CTO)

The CTO ran `gov accept W2-92` outside the sandbox on `a01fc5f4`: 44 passed, 1 failed; every line passes but S6 (14 of
15), so the other lines' reds you saw were the sandbox's (no code index there). The red is
`test_s6b_a_title_is_the_one_the_store_was_built_with`: "the question names SPEC-0092's title as the store holds it
('Cormorant Nesting Protocol') and the record is not in the bundle: the title was read from the working tree's file, not
the store (the bundle holds [])". So a plain question is matched against a title read from the working file somewhere on
the path, where S6 (the designer's reading S6-P1, and your own note: ids and titles from the same commit) wants the
store's title. Find where the working file is still read for a store built with `record_titles` and use the store there;
the C-loader fallback stays only for stores without the table. Unit test it. Do not merge yourself. Run your unit tests;
the CTO re-runs `gov accept` outside the sandbox. Update the evidence file; commit; return the twelve fields with the `ps`
check.
