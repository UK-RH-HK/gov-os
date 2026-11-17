---
name: brief-worker-model-launcher-picks
description: "Before naming a worker model in a brief, check criticality.yaml and W2-184's promotion (a fails-open finding in any probe record forces Opus); otherwise the launch is refused"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6ff2ee7c-f234-443c-8484-b5e93fc3d159
  modified: 2026-11-16T17:16:01.464Z
---

Two of my briefs named `claude-sonnet-5-5` for a worker, and `gov launch` refused both: W2-188 c12 at 16:12 (the class map said C2, criticality.yaml said C3) and W2-94 s13b at 18:08 (W2-184's `_promotion` in src/gov/launch/launcher.py forces Opus when any probe record of the ticket has a `fails open` finding, even scope out). Each cost a lead round trip and counts as a missed item in the trial.

**Why:** the launcher runs the worktree's own code. A merge of integrate can change its model rules after the brief is written.

**How to apply:** before writing a worker's model into a brief, grep `docs/probes/<ticket>/` for `fails open` and check criticality.yaml. Better still, write "the model the launcher requires (Opus if a promotion or C3 applies)" rather than a fixed Sonnet. Same for effort: a brief that names effort `max` must also give the `--reason "<text>"` gov launch requires (DEC-1120 (3)); W2-187's rev-1 was refused at 19:43 on 11-14 for this (missed 8). And before writing "the promotion applies": check that the ticket's branch has W2-184's launcher (else Opus is refused, DEC-839 item 1, so the lead must merge integrate first) and that every `docs/probes/<ticket>/` verdict block parses in JUDGEMENT.md's form (findings as objects, not id strings), or W2-184's launcher refuses; W2-88 r8 was blocked at 22:00 on 11-14 by its round-1/round-2 records (missed 9). Related: [[check-before-ready-line]].

**Again 2026-11-15 16:10 (W2-94 td-4, en-2, as ticket lead):** `gov launch --plan <role> DAEO-g87r` printed `claude-sonnet-5-5`, but the real launch refused Sonnet: "a promotion applies (a fail-open finding)" (W2-94's probe records). `--plan` does not show the promotion; grep `docs/probes/<ticket>/` for `fails open` as well, and pass `--model claude-opus-5-5 --promoted "a fail-open finding"`.

**Third time 2026-11-15 23:10 (W2-174 r2b en-3, as ticket lead):** the assignment said "pass the model `--plan` prints"; `--plan` printed Sonnet; the launch refused it (a fail-open finding in W2-174's probes). The `--plan` output is NOT the model when a promotion applies: always grep `docs/probes/<ticket>/` for `fails open` right after `--plan`, even when a brief says to pass the printed model.

**Fourth time 2026-11-16 00:00 (W2-174 r2c td-4, as ticket lead):** the assignment named Opus for the engineer only; I launched the test designer on Sonnet and it was refused for the same promotion. The promotion is per ticket: it applies to EVERY worker role launched on that ticket (test designer included), not only the role the assignment names.

**Again 2026-11-15 05:31 (W2-60a td-1, DAEO-cv58):** I named Opus/C3 from log/ticket-class.json, but the launcher computed C2 for the test designer and refused Opus. Before naming a worker model, ask the launcher (or criticality.yaml against the ticket's allowed_paths), not the class map alone.

**Fifth time 2026-11-16 05:51 (W2-81 td-1, DAEO-l78m reopen, as ticket lead):** the memory was in context and I still skipped the probe grep after `--plan` printed Sonnet; refused at once. Make the `fails open` grep part of the SAME command as `--plan`, every time.

**Sixth time 2026-11-16 09:25 (W2-88 eng-19, DAEO-2bdu S27-W, as ticket lead):** `--plan` printed Sonnet, I skipped the probe grep again, launch refused (a fail-open finding). W2-88's probes have one, so every W2-88 worker is Opus `--promoted "a fail-open finding"`. Do the grep in the same Bash call as `--plan`, no exceptions.

**Research launch fence (11-15 16:12, W2-15a):** a launched research worker needs exactly one `experiments/<folder>/**` allowed path naming an existing folder (DEC-242, DEC-273; launcher.py:229). A research ticket that writes `docs/research/**` cannot launch one, so its lead writes or the ticket gains the experiments folder. Check this before briefing a research worker.

**11-16:** leads still launch Sonnet first and get LAUNCH_REFUSED (W2-81 td-1, W2-88 eng-19), costing one retry each, though the standing paragraph says "run gov launch --plan first". In part files, name the model outright when a ticket has a docs/probes/<id>/ fails-open finding (check `gov launch --plan <role> <id>` myself before writing the brief) instead of leaving the lead to discover it.

**11-16 17:15 (W2-195 en-1, DAEO-d8df, as ticket lead):** no probes, `--plan engineer DAEO-d8df` printed Sonnet, but the launch with `--class C3` was refused: "not the session's model claude-opus-5-5 (the engineer's for criticality C3)". `--plan` without the class does not reflect C3: when the assignment says C3 (kernel), the engineer is Opus; trust the launcher's C3 rule over a bare `--plan`.

**Again 11-16 (W2-81 re-run):** the owner-approved adopter brief 31acaf29 fixed `--model claude-opus-5-5` for every worker; `gov launch` refused the test designer (routed to Sonnet). In every brief, say "the model `gov launch --plan` names", never a fixed model.
