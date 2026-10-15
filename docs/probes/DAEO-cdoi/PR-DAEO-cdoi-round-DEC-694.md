---
type: probe
task: DAEO-cdoi
reviewer_session: 687d031c-8fb8-4096-b64f-1d81a51b9d0d
implementer_session: 6f24fcd6-3f24-4e3b-b6e9-e0a5e79ba324
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: dc14bf4e827a3db4c6dbd4d842ed45cb82c9902d
---

# Probe record: W1-41 round, adoption names and enforces the two embedding policies, rebuild and doctor say "no namespace is embedded" (DEC-694, DEC-700)

- **What was probed.** The round's code at `dc14bf4e` on `w1/W1-41` (one lead session since `53e27923`; test designer session `1a562658…`, commit `46ec34b3`; engineer session `6f24fcd6…`, commit `a3895a4b`, 50 source lines added):
  - Adoption's stage A3 refuses, with `ADOPT_EMBEDDING_POLICY` and nothing written, a project path map in which a namespace states an `embedding_policy` other than exactly `embedded` or `not embedded`, states none (DEC-700), or in which no namespace says `embedded`.
  - `gov rebuild` and `gov doctor` carry the words "no namespace is embedded" in that case, with exit codes and statuses unchanged.
  - The kernel's adopt skill names the two values.
- **Who.** A fresh reviewer session started by the orchestrator through `gov launch independent-auditor`, read-only, other than the implementers. It wrote nothing to the repository; the worktree was clean when it left.
- **What held.**
  - A0 to A3 on 25 stand-in path maps. Every near spelling (`Embedded`, a trailing space, `not_embedded`), free text, a missing field, all `not embedded` and no namespaces at all were refused at A3. Empty `paths`, a namespace that is not a mapping and non-text values were refused at A0 by the config loader (`CONFIG_INVALID`). No refusal changed a file, a commit, a ref or `.gov-runtime`. Duplicate keys and YAML anchors resolve through the one loader that adoption and retrieval share.
  - Old and new `gov rebuild` and `gov doctor`, side by side on five stand-ins, both rebuild modes: identical exit codes, `ok`, store and section statuses; the only difference is the added words, present exactly when no namespace is embedded and a path map exists.
  - Nothing under `src/gov/retrieval/`, `src/gov/config/`, the schemas, the template's path map, the generated files, the guard or the launcher changed. `none_embedded()` compares with retrieval's own `EMBEDDED` constant. Outside adoption nothing refuses an unknown or missing value (DEC-380, DEC-388 stand).
  - No existing assertion was weakened: the 119 rewritten W1-41 stand-ins come from one change of the support's default policy to `embedded`. 12 of the 36 new cases pass on the old code (controls against over-refusal and over-reporting).
- **Judged against the finish line (DEC-584).** No finding is a fail-open hole that ordinary work produces, and none breaks a Wave 1 exit criterion. PASS.
- **Residuals for the Wave 2 list** (the reviewer's severity):
  - R1 (medium): A3 checks what namespaces state, not what retrieval would embed. A map whose embedded namespace is overlapped by a not-embedded catch-all, matches no tracked file, or (template-style) has no `paths` passes A3 with no file embedded, and rebuild and doctor stay silent. Fix: have A3 and `none_embedded()` count the files retrieval's per-file rule would embed.
  - R3 (low): A3 does not pin the project path map's hash, so A6 and A8 go on after a later edit that embeds nothing (the rebuild's words in A6 and A8 do say it).
  - R4 (low): the doctor's words sit only under its semantic canary answer; if the canary raises or gives no semantic entry, they are absent.
  - R5 (info): A3's embedding check runs before its `--map` check.
  - R6 (info): while the reviewer's sandboxed session ran, eleven root dot-files appeared in the worktree's status as character devices `1,3` owned by `nobody`, with one timestamp, and `docs/source` as untracked; after the session the worktree was clean. This is the sandbox placeholder of DEC-693 and DEC-697, seen at denied paths that do not exist in the worktree. The session left no containment finding.
- **Containment in the worktree during the round.** Two entries of 2026-10-14, both `flagged` (not reverted), on the test designer's two new files, against the lead's waiting commands while the designer wrote them ("attribution uncertain", then "already dirty, not restored"). The files are the designer's commit `46ec34b3` (Role independent-test-designer). Attribution records, not a breach (DEC-253, DEC-254).
