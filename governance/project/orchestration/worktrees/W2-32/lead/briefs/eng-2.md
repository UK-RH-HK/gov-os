# W2-32 engineer, round 1 continued (the CTO)

Your acceptance tests are now merged into `w2/W2-32` (`dcb30ab1`, from `4776db3e`). Same rules as before (no
`gov retrieve`, no real embedder or reranker, no scoped set; the CTO runs that outside the sandbox).

1. Run `gov accept W2-32 --json` (you see pass or fail per KPI line only). Fix what fails inside your allowed paths,
   building to the ticket's interface section; never read `tests/acceptance/W2-32/`. Repeat until S1 to S5 pass or a
   line cannot pass for a reason outside your paths (then say which and why). S9 and F1 are the CTO's records: report
   their result as it stands.
2. **The CTO's ruling (P2, inside S3):** a memory-quality event for a miss on the **hidden half** of the standing
   measure is recorded by the question's **id only**: no question text, no gold answer, no sources, and no regression
   case written into the repository (the hidden half lives outside every tree, DEC-1055 (4), G-3). Make
   `gov.retrieval.learning.record` refuse a miss whose question id is a hidden one (`H` followed by digits, or a
   `part: hidden` field) unless it carries the id only, and write nothing else for it; add a unit test. Say how the
   acceptance tests' S3 cases fare.
3. Update `docs/changes/W2-32-evidence.md` with `gov accept`'s result per line and the ruling. Commit each change with
   your trailers. Then stop and return the twelve fields, with the `ps` check for `ollama`/`llama-server` again.
