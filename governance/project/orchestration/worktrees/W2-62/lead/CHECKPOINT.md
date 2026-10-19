# W2-62 (DAEO-juee) lead checkpoint

## RESUME HERE

- **What is happening:** run 1 of W2-62, ticket lead (orchestrator role) in /home/usain/gov-os-worktrees/W2-62, branch w2/W2-62, base 162f17ea. Step 2 (tests first) about to start.
- **Decided (by the lead, for the briefs):** the prompt in force is read from `governance/project/roster.yaml` → `roles.orchestrator.prompt` (interface given to the test designer and engineer). That roster line is outside the ticket's paths: package P-1 to the orchestrator, exact line `    prompt: governance/project/prompts/w2-orchestrator.md` under `  orchestrator:` (after its `agent:` line). Without it the hook names no prompt (KPI 4 allows it).
- **Decided:** the instruction form `lines <first>-<last>` and `<n> characters`; the word "truncated" never appears; whole section when it fits. Earlier W1-49/W1-29 assertions (truncated word, w1 prompt) are revised by the test designer as named rewrites.
- **Where things are:** briefs in .gov-runtime/scratch/lead/briefs/ (td-1.md), logs in log/. Rebuild 1 started (log/rebuild-1.json, .exit).
- **Refusals met (DEC-849):** 4 (a `.rulesync/hooks.jsonc` read; an `ls governance/project/`; a Glob `governance/project/*`; a git grep with a `governance/project/*.yaml` pathspec).
- **Next:** rebuild done → tripwire snapshot 1 → launch td-1 (independent-test-designer, --effort high, gov launch) → check twelve fields, tripwire, commit trailers → red check myself (W2-62 suite, the live case too, the revised W1-49/W1-29 suites).
- **Loop count:** 0 implementation iterations so far.
