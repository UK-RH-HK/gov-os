# MODEL-TIERS-1 brief (DEC-1118 (4)): a read-only investigation for the owner

You write a short package for the owner of the Gov OS project at /home/usain/Dynamic-Agentic-Engineering-OS (branch
w2/integrate). Read-only except your outputs: the draft `.gov-runtime/scratch/orchestrator/drafts/model-tiers/MODEL-TIERS-1.md`
and any scripts beside it. Do not commit. Never open, list or name ~/gov-os-eval/. From transcripts read only usage and
metadata fields (model, effort, usage counts, timestamps, ids, tool names), never message contents. Never the Monitor
tool. Nothing changes until the owner decides: write options with a recommendation.

## Questions (answer each, with sources)
1. **The map:** find every decision (docs/DECISION_REGISTER.md; governance/project/orchestration/DECISIONS-IN-FORCE.md)
   and ticket (.tickets/*.md: e.g. W2-60a "the role, its skills and its model and effort loaded at launch", W2-33, W2-21,
   W2-153's role template `template: {ROLE_TEMPLATE}@{ROLE_VERSION}`, the role files' "model tier" field under
   template/governance/kernel/roles/ and .claude/agents/*.md) that sets which model and effort each role and each tier
   of work uses. Quote the rule and its id.
2. **In effect?** For each, is it applied today, and where would it apply: `.gov-runtime/scratch/orchestrator/tools/launch_worker.sh`
   (what model/effort it passes), `gov launch` (src/gov/launch/*: does it read a role's model or effort?), the
   dispatcher (.gov-runtime/scratch/orchestrator/dispatch/ and its tools), the resource gate (src/gov/launch/gate*,
   src/gov/resources/), the operator agent (~/gov-os-operator/install/operator_launch.py: it already uses Sonnet), and
   the CTO's own helpers launched through the Agent tool (subagent types in .claude/agents/*.md carry `model:`? the
   Agent call's `model` parameter; the session default `CLAUDE_CODE_SUBAGENT_MODEL` in ~/.claude/settings.json).
3. **Why 99.7 % Opus at high or max** (USAGE-1, governance/project/orchestration/packages/USAGE-1.md §1, §5): trace the
   actual causes (defaults, env, launch flags, the agents' front matter, effort settings) with evidence.
4. **What applying the map would take:** per place in (2), the change (and whether it is a control path that needs an
   ACT: check ~/gov-os-operator/install/class-rules.yaml), with the saving at USAGE-1's prices (its §8 price table and
   its data in .gov-runtime/scratch/orchestrator/drafts/usage-1/: calls.jsonl, sessions.json; reuse its scripts) and the
   quality risk per role (test designer, engineer, reviewer/auditor, lead, product-spec, research, ACT-preparation
   helper, the CTO). Mark what DEC-1118 already decided (C: Sonnet for ACT-preparation helpers; E and F: trials after
   the lift).
5. **Memory search instead of reading:** would more use of `gov retrieve` (memory search; the fresh 80 measured it:
   packages/LIFT-1/FRESH-80-RESULT.md) in place of reading whole files and printing long outputs cut context? Measure
   from the transcripts' tool calls: Read and Bash output sizes per session, how often whole files are read, how often
   `gov retrieve` is used, and estimate the context saved (USAGE-1 §6 noted repeats are 16 % of worker Reads and Read
   results 28 M characters). Name the risk (a search answer missing what a full read would show).

## Output
A short package (≤ 150 lines), plain English, tables over prose, figures marked M (measured, source) or E (estimated,
basis). Title `# MODEL-TIERS-1: models and effort by role, and memory search (for the owner)`. Sections: 1 Headline;
2 The map as decided; 3 In effect, and where; 4 Why 99.7 % Opus; 5 What applying it takes, saving and risk per role;
6 Memory search instead of reads; 7 Options and a recommendation; 8 Method and gaps. Reply with the path, the headline
and the options table.
