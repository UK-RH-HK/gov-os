---
type: probe
task: DAEO-kl5e
reviewer_session: 1e0c179d-c135-4a63-a5a3-e65980db433f
implementer_session: 0f2f9377-40c4-497c-a2ef-37d5f87d8587
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: f9277098f60c747df9c52efb134dd684cd064f0c
---

# Probe record: W2-50, second and last review (DEC-413) (DRAFT, not committed — see the lead's return, package P-C)

- **What was probed.** The code at `f9277098` on `w2/W2-50` (implementation `91200c82` by session
  `bbbda207-31b9-4f4d-a58c-2fce09af7b39`, repair `86aa805c` by session `0f2f9377-40c4-497c-a2ef-37d5f87d8587`, CIT-E
  `0bbada97`, lead checkpoint `f9277098`). A fresh read-only reviewer (role `independent-auditor`, session
  `1e0c179d-c135-4a63-a5a3-e65980db433f`, 2026-10-17), launched in the owner's form with the reading tools only. 73
  hook probes, public-`decide` probes, `gov launch` probes with the stand-in CLI and 7 secrets-check probes, each with
  a temporary HOME and a sibling TMPDIR; W2-50 suite with its builder tests: 234 passed; `git status --short` empty
  before and after; real `~/gov-os-runs` ABSENT.
- **What it found.**
  1. **Another project's ticket of the same name gets this repository's ticket folder** — medium-high, reproduced
     through the guard and `gov launch`. A second Gov OS project on the same home (outside the root, or a clone inside
     an own folder) with an `in_progress` ticket whose `external-ref` is `W2-91` may write and `rm -rf`
     `~/gov-os-runs/W2-91`, another ticket's folder of this repository; its launch adds that folder to the sandbox
     write list. Lets a role write outside its scope; can lose work.
  2. **A clone's own secrets check fails open for a linked store inside the clone** — medium, reproduced. With the
     project under the root, a `.gov-runtime/index` link to a folder of the same project holding a secret is not
     followed (green); the same layout outside the root goes red. A gate fails open (the clone's own); this
     repository not scanning the clone holds.
  3. **A FIFO among the ticket files hangs `gov launch`** and makes the guard refuse every write outside the project
     (the temp folder included) until its deadline — low; fails closed (availability only).
- **Found sound.** Another ticket's folder by `..`, symbolic, relative, dangling or `cd` links, hard links, moves and
  copies across the edge; near names and case changes; the root in every spelling (13 `rmdir` forms); the launcher
  (only the root and the own folder are made, the root never added, a file or link in their place not opened); no
  role, unknown role, `ticket-lead`, forged tickets, a second ticket of any status naming the folder; the refusals that
  come first (freeze, `dangerouslyDisableSandbox`, settings, `.tickets/`, acceptance tests); the secrets check's root
  pruning.
- **Judgement: fail.** This is the last review (DEC-413). Findings 1 and 2 are fail-open and go to the owner as
  packages; finding 3 is a residual.
