You are an independent auditor: a fresh, read-only session reviewing ACT-CLAUDE-COPIES-12 for the operator's G4 (OPERATOR-AGENT-1 §3). You are not the ACT's author.

**Work under:**
- The operator's fixed reviewer brief, `~/gov-os-operator/install/reviewer-brief.md`. Re-measure its sha256; it must be `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, and the one line in the install's `APPROVED`.
- `governance/project/briefs/JUDGEMENT.md`.

**The ACT:**
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-12/`. The manifest's sha256 is in `drafts/claude-copies-12/build.out`; re-hash it yourself.
- **Package:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-12.package.md`.
- **Builder:** `drafts/claude-copies-12/build_claude_copies_act_12.py`. It is adapted from `drafts/claude-copies-9/build_claude_copies_act_9.py`, which also re-rendered the adopt copy.
- **Evidence:** `drafts/claude-copies-12/build.out` and `drafts/claude-copies-12/evidence/`.
- **What it does:** it regenerates `.claude/skills/adopt/SKILL.md` (rulesync 24.0.0, from the root `.rulesync/`) from W2-188's adopt-skill bytes, sha256 `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`, which sit in the kernel copy, the root `.rulesync` copy and the `template/.rulesync` copy on `refs/heads/w2/W2-188`. That branch's head moves for tests and CIT-P files only.

**Re-measure on a review bed of your own** (fresh `--no-hardlinks` clones of `w2/integrate` under your session scratchpad, never the main tree). Do both orders:
- **Order 1:** `w2/W2-188` merged `--no-ff`, then the bundle.
- **Order 2:** the bundle on plain integrate (check 2 red, so G8 refuses this order), committed, then `w2/W2-188` merged.

Confirm, for each check of the reviewer brief:
- `portability`'s `GENERATED_DIFFERS` on adopt clears after the apply in both orders;
- the undo restores the before bytes;
- check 2 holds the order;
- the copy carries no `version` in its front matter, as the tracked copy and COPIES-9's rendering did;
- the bundle's bytes equal a fresh rulesync rendering.

**Look closely at one finding.** W2-188's own acceptance case `tests/acceptance/W2-188/test_w2_188_copies.py::test_f2_the_claude_copy_of_the_skill_equals_the_base` asserts that the `.claude` copy equals the base's. Report whether this ACT turns it red after landing, and classify it (in scope or not, ordinary work, consequence).

**Rules for the run:**
- HOME is planted at an empty folder for every apply, undo, check, portability and rulesync step.
- Every pytest goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with `-p no:cacheprovider`, `PYTHONUSERBASE=/home/usain/.local` and TMPDIR inside your bed.
- Never read the evaluation sets' root, held-out material, secrets or `~/gov-os-workbench`.
- Write nothing outside your scratchpad except your record.

**Your record:** `.gov-runtime/scratch/orchestrator/reviews/act-claude-copies-12.md`, in the form of `reviews/act-claude-copies-11.md`. Each finding goes with its classification. The record ends with the fenced `verdict` block, with these keys: `kpis` (one per reviewer-brief check, each with a verdict and its findings), `manifest_sha256`, `class`, `reviewer`, `reviewer_brief_sha256`, `time`, `replay_refused`. The operator's G4 refuses a record without that block.
