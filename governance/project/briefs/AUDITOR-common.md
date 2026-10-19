# Auditor brief template (W2-25, W2-28, W2-30, W2-47): the judgement part, word for word

Every independent-auditor brief the orchestrator writes for W2-25, W2-28, W2-30 and W2-47 starts from this file: the sections below go into it unchanged, before the audit's own task.

## Standing rules for your session (owner, DEC-836, DEC-838, DEC-849, DEC-850)

- You use your model's full window; nobody asks you to stop or compact early. You run at `--effort max`.
- Use `gov retrieve` for what you need to know, and say in your report which questions it answered. Take a large question in batches (`--batch-size`, `--continue`), ranked and stacked, never one giant query or context (DEC-860); ask a code question through the code-graph tool's own traversal, small and targeted, and read the whole graph only in pages, never one query over its row cap (DEC-859).
- Until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`): take the refusal, never look for another form, search named folders instead, and count the refusals in your report.
- You never ask or notify the owner directly, never use a question box and never run `owner-ping` (DEC-855): anything that needs the owner goes into your report as a package, in the six parts of DEC-818, saying whether it blocks your audit or only part of it.

## How you judge (owner, the w2 prompt's section 14)

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

## Your findings

- Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding in your audit report carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the audit's item.
