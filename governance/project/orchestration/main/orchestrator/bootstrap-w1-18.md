
## W1-18 residuals (Ollama on-demand lifecycle, 2026-10-04)

Recorded at W1-18's close, from the ticket lead's summary. None is a defect.

- **A `serve` that never becomes healthy is left running**, following DEC-261 ("never stops it"). No test asserts
  this either way.
- **Choices of the engineer the decisions don't name and no test asserts:** an available result has `state`
  `AVAILABLE` and `warning` `None`; `env`, when given, is read for the three variables and passed to the daemon;
  each health probe is capped at 1 s, and the health request bypasses proxy variables; the daemon gets its own
  session with its streams to `/dev/null`.
- **Readings of the test designer:** "within the deadline" allows 2 s on top of `timeout_s`; "FTS-only" matches
  `FTS-only` or `FTS only` in any letter case; the 20 s default is read from the function's signature, not waited for.
- **No test against the real daemon.** Ollama is not installed on this machine; the suite uses a stand-in executable
  and a stand-in loopback endpoint. The embedding model's registry row (DEC-195) was not added: the registry is
  outside the ticket's paths and nothing was installed. It is due when Ollama and the model are installed, at the
  latest for W1-19.
- **G-22's text** exists only in the archived sources; the decisions rest on the in-tree sources (DEC-260, DEC-261,
  DEC-257).
- **The ticket body** still says "on-demand start and stop"; DEC-261 decides start only.
