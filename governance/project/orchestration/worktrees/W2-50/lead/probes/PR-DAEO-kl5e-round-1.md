---
type: probe
task: DAEO-kl5e
reviewer_session: 9ffac555-e15e-4654-ba56-e68b45435bb3
implementer_session: bbbda207-31b9-4f4d-a58c-2fce09af7b39
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: b7981b0faf3cad33b596cdd330cd1a339fad5d8c
---

# Probe record: W2-50, first review (DRAFT, not committed — see the lead's return, package P-C)

- **What was probed.** The code at `b7981b0f` on `w2/W2-50` (implementation `91200c82`, engineer session
  `bbbda207-31b9-4f4d-a58c-2fce09af7b39`). A fresh read-only reviewer (role `independent-auditor`, session
  `9ffac555-e15e-4654-ba56-e68b45435bb3`, 2026-10-17), launched in the owner's form with the reading tools only,
  commissioned and judged by the orchestrator's lead (DEC-137). About 150 cases through the kernel's PreToolUse hook,
  `gov launch` with a stand-in CLI and the secrets check, each with a temporary HOME and a sibling TMPDIR;
  `git status --short` empty before and after; real `~/gov-os-runs` ABSENT before and after.
- **What it found.**
  1. A project lying inside the session's own folder lost every in-project rule (acceptance tests, freeze flag,
     records, `.tickets/`, settings file, guard hook, `allowed_paths`) — high, reproduced; fail-open.
  2. Glob characters in `external-ref` put `//…/gov-os-runs/*` or `/**` into the sandbox write list — medium.
  3. Two tickets naming the same folder shared it — medium-low; can lose work.
  4. A `ticket-lead` session's subagent of another role type reaches the folder (the guard's acting-role model) — low,
     owner question.
  5. The own folder's path can be written as a file — low. 6. `rmdir` of the root with an unresolvable argument —
     low (CIT-E difference 5). 7. Bash forms the guard never judged (`find -delete`, `env rm`, `git clean`, `rsync`,
     `dd`, `truncate`, `python3 -c`) — pre-existing. 8. Two cases stricter than needed (not fail-open).
- **Judgement: fail.** Findings 1 to 3 went to a test design batch as described behaviour (DEC-136, commit
  `72263054`, 54 cases) and a repair (`86aa805c`, CIT-E `0bbada97`); verified green; second review below.
