---
type: probe
task: DAEO-cv58
reviewer_session: 8518ee3b-b06f-44f8-b227-d86dd910a497
implementer_session: 9e1deba3-3000-4a78-b816-dba717d47925
reviewer_wrote_nothing: true
commissioned_by: ticket lead (orchestrator role)
judged_by: ticket lead (orchestrator role)
judgement: pass
probed_commit: 97f208456bdb1836382a553409b2c7ca5c3f3f00
---

# Probe record: W2-60a (DAEO-cv58), the narrow independent check after review 3

Review 3 passed at 0e11b5db743d (record: `PR-DAEO-cv58-round-3.md`, beside this one). The review rounds are spent
(DEC-1010), so the changes made since were checked by a narrow independent check, not a review round (DEC-1167 (2)).

## Who and what
- Reviewer: a fresh independent auditor, read-only (session 8518ee3b-b06f-44f8-b227-d86dd910a497, Opus 5.5 at high).
  It was launched by `gov launch` under the sandbox, wrote nothing in the repository, and left `git status` empty at
  both ends. Brief: `.gov-runtime/scratch/lead/briefs/b20-auditor-narrow-check.md` (lead records, not committed).
- Implementer sessions:
  - 69f4716b-6367-40f4-8107-528cbc36c860 (b14): S2's version reader, and the plan's work;
  - 9e1deba3-3000-4a78-b816-dba717d47925 (b16): P-6 (a)'s wiring and P-7 (a).
  The schema's field names the last.
- Probed head: 97f208456bdb. Scope: `git log e1a3e2214266..97f208456bdb`, in four items.
- Method: about 40 `gov launch` and `gov launch --plan` runs from the worktree's `src`. They ran against fixture
  projects in the reviewer's temp folder, with the acceptance suite's stand-in CLI. `read_role` and
  `launch_default` were run on this tree for every role. No pytest run, no live session.

## Items and outcome
1. **S2's version reader (7c789919b): pass.**
   - The top-level `version`, else `metadata.version` when `metadata` is a mapping, else `no version`.
   - Every generated copy on this tree is read with its version, so none is refused (F3).
   - A named skill whose `metadata` is not a mapping still refuses.
2. **P-7 (a), a vendored skill's version from its manifest (8a21a9c1a): pass.**
   - `read_role` passes for engineer on this tree: its three Superpowers skills are recorded as `v6.4.2`, with
     `version_source` naming the manifest, and the hash is the loaded copy's.
   - An unlisted skill, a missing or malformed manifest, a non-string version, or empty `token_sizes` each still
     refuses a named skill.
   - The adopted layout reads `governance/kernel/skills/superpowers/vendored.yaml`.
3. **The plan line (the ticket's S10, called S12 in run 4's briefs) and P-6 (a) (2ef612682, 4ebf55fb4): pass.**
   - `gov launch --plan` prints exactly the role file's `Launch default` line, and never reads `Launch by
     criticality`.
   - It starts nothing: no CLI call, no record, no temp folder, no lock, no gate.
   - A missing or malformed line, and the role and ticket refusals, each exit 1 with `LAUNCH_REFUSED`, naming the
     role file where it is the cause.
   - Without `--plan`, a launch takes the same path as before.
4. **S3, S4 and S8 back to their DEC-839 forms, and the merge of w2/integrate (5b7941b66): pass.**
   - No RUBRIC-2 code (criticality, tier, trial, promotion) is read or recorded.
   - The merge's resolution of `launcher.py` loses no refusal from either side. The line, the settings and the
     record keep S3 to S8's behaviour:
     - the role's model, recorded with `model_source`;
     - an effort after `--` recorded as the launch's own;
     - a model that is not the role's refused, naming both;
     - `CLAUDE_CODE_SUBAGENT_MODEL` equal to the model, in both the settings and the process environment;
     - no threshold;
     - S7's arguments refused;
     - one record, keyed by `--session-id`, present before the start;
     - an unwritable record folder refused.
   - The one appended file is the role file, its named skills, a blank line, then the template, placed last
     (P-4 (A)).
   - No integrate-side path starts a worker without these checks.

## Findings (none blocking; all out of scope, recorded as rows)
- **R1** (`launcher.py:632-646`). A lead launch writes no launch record and appends no role text. After `--` it runs
  only `_check_cli_args`, not S5's and S7's checks. This is W2-136 S9's decided lead form (DEC-1088 (5)(a)), and the
  merge keeps it. Whether S8's "every launch" covers leads is for the owner or the CTO: a row for W2-184 or W2-60b.
- **R2** (`role.py:158-160`). The manifest's version is matched to a skill by name only. The generated copies differ
  byte for byte from the vendored copies (rulesync's front matter), but the record carries the loaded copy's hash
  and `version_source`. This is P-7 (a) as decided. A per-skill hash check against the manifest is a row for W2-60b.
- **R3** (`role.py:119`). A manifest reached through a link that points outside the root is read. This is
  consistent with how the role file's links are handled in the reviewed code. A Wave 3 row.
- **R4** (`launcher.py:602-613`). `--plan` ignores what follows `--`, and prints the default line even where a launch
  would refuse the role file on another line. This follows DEC-1167 (2) ("the default line alone"), and the plan
  starts nothing.

## Process notes
- The reviewer's Write of a scratch script under its own `$TMPDIR` was refused by the harness's permission prompt.
  It then ran its probes as Python fed on standard input, under `$TMPDIR` only. Nothing was written in the
  repository. Under DEC-1142 (9) that is another form for the same action, so it is reported here as a process
  deviation. It does not touch the verdict.
- The lead's scoped run at this head was red for reasons outside this check: integrate-side fixtures that predate
  W2-60a (P-8 (a), a test-designer batch), and DEC-253 on 5b7941b66 (P-9 (a), the owner's exemption). Neither
  changes code under `src/`.
