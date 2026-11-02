# W2-123 (DAEO-qzrq) lead checkpoint

## State (2026-11-02 01:35 UTC)
- Branch w2/W2-123, head 17d88232b287. Commits of the ticket (all trailers checked as they appeared):
  - e404e268f3fb engineer (eng-1): capped starts of both servers from gate.json, probe, safe restart, determinism check.
  - b87da348bbb2 independent-test-designer: 39 acceptance tests (tests/acceptance/W2-123/).
  - 65627b745bf3 orchestrator merge of w2/W2-123-tests.
  - 3dabcdaca633 engineer (eng-2): no executable found -> W1-18's result without settings.
  - 34717de9e43a, 77b44861d351 independent-test-designer: README map in gov accept's form (Rewrite-Reason each).
  - 986a77619a32 orchestrator merge of w2/W2-123-tests.
  - 17d88232b287 engineer (eng-3): docs/changes/W2-123-evidence.md; defaults' comments name their figures.
- gov accept (eng-3, after 17d88232b287): all 7 lines pass, 39/0/0, unmapped 0.
- Running: rebuild-3 then verify.sh (scratchpad): select -> parallel (verify_lock) -> serial -> gov check (heavy_slot) -> collect-only; logs log/verify/, DONE marker log/verify/DONE.
- Next: read verify results; trailer_gate; gov checkpoint record (--trigger ticket-transition) + commit (Task/Implements/Role orchestrator); remove W2-123-tests worktree and branch; return.

## Measures (measure/)
- FIGURES.md (the lead's figures, used by eng-3); sweep-1.jsonl (16 cases); det_matrix-2242.jsonl; np_check-2314.log (Ollama pins -np 1); rebuild-2-record.json (cold semantic stage 4,087 s for 54,463 chunks on the capped shared server); measure2-failed-0024.log (GPU memory full, separation not measured).

## Packages to return: packages-draft.md (P-W2-123-1 Ollama -np pin; P-W2-123-2 embedder jitter; lead readings; W2-20 note).

## Workers
- td-1 session 3dd2b42f-2064-4286-9326-1307ccc2bcd8 (3 runs: first + resume 1 + resume 2), sandboxed, tripwires 1, 4, 5 clean.
- eng-1 44fee5dc-a719-482c-a2e2-5486f9c31f07, eng-2 d30da0bb-595c-4904-af01-2865cb65899a, eng-3 37cc8df2-1c9f-4770-8fba-4dafefed501a, all sandboxed; tripwires 2, 3, 6 clean (eng-1 left pytest-of-usain/ untracked).

## Loop count: kept by lead.

## Brief gaps (running)
- No gate configuration file on w2/integrate (W2-20 unmerged) though KPIs 4 and 6 name it | the ticket file | ~15 min (est.)
- The KPIs name callables for the dispatcher without names; the lead fixed an interface spec | this ticket's part | ~20 min (est.)
- Ollama 0.35.0 ignores OLLAMA_NUM_PARALLEL for embedding models: the ticket's premise was untested | the ticket file / SIZING-1 | ~15 min (est.)
- The sandbox's TMPDIR /tmp/gov-os-lead-W2-123 is read-only inside gov launch: pytest writes pytest-of-usain/ into the worktree | common brief / tool | 5 min (est.)
- A new worktree's rebuild waits for a heavy slot before the first worker; used W2-00-store retrieval instead | common brief | ~19 min measured (22:31 to 22:50)
- gov accept's README map form (line names S1/F1, no "[a,b]" parameter shorthand) is in no test-designer brief or skill | skill test-design / common brief | ~25 min (two TD resumes)
- GPU memory full (15 of 16 GiB, held outside the Gov OS) made a private measuring server fall to the CPU; no brief says to check free GPU memory before a measure | this ticket's part | ~20 min (measured run 00:05-00:24)

## Guard refusals
- 2026-11-01 23:22 | rm -rf of the engineer's pytest-of-usain/ in this worktree | permission prompt, not the five-rule hook | true (DEC-922: no allow rule) | 1 min; named for the orchestrator
