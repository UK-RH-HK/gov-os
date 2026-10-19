---
type: probe
task: DAEO-0z8c
reviewer_session: cd5641a4-d169-42bf-ab83-ffe330d97688
implementer_session: e4bcc3a3-009a-4fe2-9bad-62b1645f677d
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: f19f156ed606eb9997cefce07e32d601b4ce3b7b
---

# Probe record: W2-05, round 2 (the second and last review, DEC-413; draft, not committed: the round failed)

- **What was probed.** Head `f19f156ed606eb9997cefce07e32d601b4ce3b7b` of `w2/W2-05` (DAEO-0z8c), running this
  worktree's `src/`. The round-2 implementer was engineer session `e4bcc3a3-009a-4fe2-9bad-62b1645f677d` (commit
  `2e108d85`), and the round-1 implementers were `e28a6c37-e973-43dd-a132-c65e94e529ee` and
  `89af54b4-d8ce-4955-a686-6e5434e9b27d`. A fresh read-only reviewer did the probe: role `independent-auditor`,
  session `cd5641a4-d169-42bf-ab83-ffe330d97688`, started through `gov launch` and sandboxed, 2026-10-19,
  commissioned and judged by the orchestrator. Its only writes were the sandbox check's git object and index
  refresh (DEC-789), and the tripwire saw no change in any tree.
- **Findings that fail the round.**
  - F-A (high, loses work, a partial regression): a project-declared check that runs git in a temporary
    repository of its own acts on the project's index. That happens on a hooked commit in the main tree
    (plain, `-a`) and in a linked worktree. The declared-check runner gives the check the helper's environment,
    which keeps git's own index as an absolute path. The commit landed with a deletion nobody staged, and a
    variant left the project's index naming a missing object. At the base, the main-tree plain commit was safe:
    the relative `.git/index` resolved inside the temporary repository.
  - F-B (high, a gate fails open, a regression): when a secret's blob lives only in an object directory named by
    `GIT_OBJECT_DIRECTORY` (or alternates), the helper clears those variables. gitleaks then cannot read the blob,
    logs git's error and exits 0, so the staged-secrets gate passes and the commit lands. The base refused it.
- **Other findings.**
  - D-1 (pre-existing, gate fails open): a replace ref makes gitleaks scan the clean replacement.
  - D-2 (low, fails closed): a relative `GIT_INDEX_FILE` is read from the process's folder, not the work tree's
    top.
  - D-3 (not verified): `rulesync import` and `rulesync generate` start with the whole environment.
- **Found sound.** Round 1's F1 refusal cannot be passed around by any route tried. Git's own indexes are still
  scanned. No clean commit is newly refused (main tree, separate git dir, submodule). Containment still catches
  the change. `lefthook install` leaves the settings byte-identical (two shapes, main tree and linked worktree),
  and the restore after `uninstall` is clean. All 45 sweep rows match the git literals under `src/gov/`. No
  DEC-777 file is changed.
- **Judgement: fail** (F-A, F-B). Under DEC-413 this was the last review: no third round without the owner.
