# W2-92 engineer, S6 continued (the CTO)

S6's acceptance tests are merged into `w2/W2-92` (`00a3daa0`, from `e8d51868`) by the CTO outside the sandbox (from now
on the CTO makes every merge into your branch: do not merge yourself). Your three stale folders were refreshed by the CTO.
Same rules as before (no `gov retrieve`, no real model, no scoped set).

Run `gov accept W2-92 --json` (pass or fail per KPI line only). Fix what fails inside your allowed paths, building to
S6's line and the ticket's notes; never read `tests/acceptance/W2-92/`. Note the designer's reading (S6-P1): titles come
from the store after a rebuild. Update `docs/changes/W2-92-evidence.md` with the result per line; commit with your
trailers. Then stop and return the twelve fields, with the `ps` check.
