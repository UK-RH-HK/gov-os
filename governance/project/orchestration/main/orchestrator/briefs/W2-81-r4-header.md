# W2-81 (DAEO-l78m) — a records-only repair: the two probe records fit the probe schema (DEC-968, the CTO, 2026-11-02)

**Read this first; it overrides the steps below where they differ.** No new review round and no code change: the merge
queue ejected W2-81 at `166f459f4b5c` (`git rev-parse --short=12 HEAD` must show it, `git status --short` nothing; else
return PACKAGES naming it) because its probe records break three record checks:
W1-08 `test_the_probe_schema_accepts_this_repository_s_probe_records`, W1-26's probe-record check and W2-02's
`test_core_schema_is_green_on_this_repository`. Reproduced on your head alone:
- `docs/probes/DAEO-l78m/PR-DAEO-l78m-moderated.md`: its front matter is not valid YAML (`judgement: computed (DEC-1010: …)`,
  an unquoted colon), and it lacks the schema's required `type`, `task`, `reviewer_session`, `implementer_session`,
  `reviewer_wrote_nothing`;
- `docs/probes/DAEO-l78m/PR-DAEO-l78m.md`: `judgement: 'superseded by …'` is not one of the schema's four words
  (`pass`, `passed`, `fail`, `failed`; `template/governance/kernel/schemas/probe.schema.json`, DEC-490).
**Do:** make both records valid against that schema without changing what they say: the reviewer's record keeps its
own verdict word (its findings and verdict block unchanged; a note that the moderator's triage supersedes it goes in its
body, not in `judgement`); the moderator's record carries every required field with honest values and `judgement`
from the verdict block as computed (READY true -> `pass`), the computation stated in its body. Never edit the
schema or any test. Then run W1-08's, W1-26's and W2-02's record cases and the scoped selection once (in a heavy-job
slot), and return DONE with the head. Commit with `Task: DAEO-l78m`, `Implements: DEC-1010, DEC-490`,
`Role: orchestrator` (you, the lead: records only).

---

