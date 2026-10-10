---
id: CAP-61.c
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Network profile per role: engineer, independent test designer and independent auditor get an empty allowlist; research and experiment work gets a broad, owner-extensible allowlist (GitHub, PyPI, npm, Hugging Face, arXiv, documentation sites), with its writes and installs inside its own experiment folder, held there by `Edit` deny rules the launcher generates at launch for every other path of the repository; the deny list is computed at launch, so a path created later is covered by the guard''s per-ticket allow-list, not by the list; the list''s exceptions are `.git/` and any entry whose name contains `*`, `?` or `[`, which the sandbox skips on Linux; the allowlist is shown to accept the research domains; WebSearch and WebFetch run outside the sandbox'
depends_on:
- CAP-61
---

# CAP-61.c: Network profile per role: engineer, independent test designer and independent auditor get an empty allowlist; research and experiment work gets a broad, owner-extensible allowlist (GitHub, PyPI, npm, Hugging Face, arXiv, documentation sites), with its writes and installs inside its own experiment folder, held there by `Edit` deny rules the launcher generates at launch for every other path of the repository; the deny list is computed at launch, so a path created later is covered by the guard's per-ticket allow-list, not by the list; the list's exceptions are `.git/` and any entry whose name contains `*`, `?` or `[`, which the sandbox skips on Linux; the allowlist is shown to accept the research domains; WebSearch and WebFetch run outside the sandbox

A covers item of CAP-61 (Worker session launcher and OS sandbox). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** Network profile per role: engineer, independent test designer and independent auditor get an empty allowlist; research and experiment work gets a broad, owner-extensible allowlist (GitHub, PyPI, npm, Hugging Face, arXiv, documentation sites), with its writes and installs inside its own experiment folder, held there by `Edit` deny rules the launcher generates at launch for every other path of the repository; the deny list is computed at launch, so a path created later is covered by the guard's per-ticket allow-list, not by the list; the list's exceptions are `.git/` and any entry whose name contains `*`, `?` or `[`, which the sandbox skips on Linux; the allowlist is shown to accept the research domains; WebSearch and WebFetch run outside the sandbox
- **Wave:** W1
