# W2-149 — the narrow review of the wiring review's F18 to F23 (DAEO-52ku)

You are a fresh, read-only independent reviewer. **Narrow scope:** the fixes for F18 to F23 of set-up A's wiring
review. Its record is in your worktree at `.gov-runtime/scratch/ref/W2-149-sgx-review-r1.md`; read those six findings.
The CTO decided (DEC-1112 (3)) to fix them before the owner is asked for the install ACT.

In the ticket (`.tickets/DAEO-52ku.md`), read the changed lines **S25** and **S27** and the new lines **S29, S30 and
S31**, each marked `[changed, DEC-1112 (3)]`, and its last note. The rest of set-up A's wiring was reviewed READY and
merged (`7f0e71519`). Re-open it only where these fixes touch it. READY is computed by `verdict.py` from your block.

The five owner-approved briefs are in `.gov-runtime/scratch/ref/sgx1-briefs/`. Their bytes do not change. The fixes
must meet them: the overlap auditor's brief says the two labels arrive blind as `x` and `y`, and that its decision
replaces both labels.

## What to review
- **The branch:** `w2/W2-149-sgx` in `/home/usain/gov-os-worktrees/W2-149-sgx`, head `d388da2f2`. The change is the diff
  from `944f39165` (`w2/integrate`, the ticket changed) to the head.
  - The designer's cases: `939da2755` (51 new, six revised, with its `Rewrite-Reason`; the README's interface items for
    F18 to F23).
  - The engineer's commits: `6a959ffc5` (the build, F26 and the unit tests) and `d388da2f2` (the evidence).
- **The runs:**
  - The lead's, at `d388da2f2`, outside the sandbox (2026-11-10 12:0x UTC): the acceptance folder (but `live`) and the
    two unit files with `GOV_W2_149_BWRAP=1`: **289 passed, 0 failed** (every `bwrap` case included). The 3 live cases
    (haiku, planted roots): **3 passed**.
  - The engineer's `gov accept W2-149` in the sandbox: 165 passed, 0 failed, 35 skipped (3 live, 32 `bwrap`).
  - The designer's red check before the build: 32 red in the sandbox, and 21 more `bwrap` red outside it (lead), each
    for its stated reason.
- **Check:**
  1. **Each fix does what its line says, and only that.** Read the code path, not only the tests:
     - F18: the round-1 check;
     - F19: the stopped rule, for every flow;
     - F20: labeller 2's check;
     - F21: the reason blanking;
     - F22: the settled-line form;
     - F23: the `rule_class` forms, accepted and stored.
  2. **The round-1 check is the same confinement as round 2's.** Is anything weaker at round 1? Is every failure 20,
     with nothing landing? A missing `bwrap` included?
  3. **Independence:** can the overlap auditor still tell the labellers apart from anything in `disputes.jsonl` (the
     reason, the clauses' form, key order, the `rule_class` form)? Say what remains, if anything.
  4. **No regression:**
     - the memory flows, and S1 to S24, S26 and S28, unchanged;
     - the revised cases weaken nothing;
     - the F26 change (a planted listener instead of the shared Ollama port).
  5. **Failure lines:** none now passes where it should fail.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`. Mark it `scope: in` only if it concerns F18 to F23's fixes.

## Write and return
- **You write nothing in any tree.** You may run the tests read-only (`-p no:cacheprovider --optin=lifted
  --optin=breadth`) through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx/src` and an empty scratch HOME
  (`PYTHONUSERBASE=/home/usain/.local`).
- A nested `bwrap` cannot start in your sandbox. The lead ran the `bwrap` cases outside it (above).
- Never run anything against the real `~/gov-os-eval/`, `~/gov-os-runs/`, `~/gov-os-wall-trees/`, `~/.claude/` or a
  real `claude` session. No GPU. Single simple Bash commands (DEC-1080). The hidden-half rule holds. Read the template
  folder with the Read tool only, never naming it in a Bash line. Never name a git revision range in a Bash line's text
  beyond what one `git diff` needs.
- **Search again once (DEC-1092 (1))** if a search does not answer.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md`, as single-line labelled fields, with the sandbox and `ps` checks
    first;
  - your answers to checks 1-5;
  - every finding with its two lines and its scope (ids from F36);
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "S25", "verdict": "pass|fail", "findings": [...]}, {"kpi": "S27", ...}, {"kpi": "S29", ...}, {"kpi": "S30", ...}, {"kpi": "S31", ...}]}`,
    with each finding `{"id", "scope", "ordinary_work", "consequence"}`.

Refused twice for the same call: stop and say so; no third try.
