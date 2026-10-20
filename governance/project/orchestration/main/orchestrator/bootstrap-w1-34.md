
## W1-34 residuals (decision-package template, 2026-10-04)

Recorded at W1-34's close, from the ticket lead's summaries. None is a defect of the ticket; each names who should
settle it.

- **Nothing enforces the template.** The tests check what the template lets through: nothing renders a package or
  records an answer. Refusing a package without a recommendation or confidence, or an answer without a date, falls to
  W1-35 and W1-11.
- **The schema does not hold the five `status` values** (DEC-328). `status` is still any non-empty string and extra
  keys are accepted, so the five values, "no second state key", `rank`, `cit` and `constrains` hold only in the
  template and its test. W1-34 could not change schemas.
- **What a declined, revoked or stale package does to waiting tickets** is W1-11's (DEC-308).
- **Choices the sources do not fix.** The CIT id has no grammar (`CIT-0000` is a placeholder). The frontmatter key
  `rank` and its default `P2`. Packages over the cap "wait, highest rank first" (DEC-093 gives only the cap and the
  P1 bypass). "Human-resolvable" is read as "precedence does not settle it, or it is one of MR-6's questions that
  matter". "Only an answered gate of the same CIT permits the next actions" also excludes an open gate, which
  CAP-34.d does not list. The answer form reads `ACCEPTED (who, YYYY-MM-DD)`, not `owner`, because DEC-220 records
  delegated answers under the orchestrator.
- **The rules sit in an HTML comment inside the form**, which the author deletes from a filled package. W1-35's
  skills need to carry the routing, batching and state rules themselves.
