
## 58. Delegated decisions on W1-25's test design packages (register v0.58, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on four of the six packages the W1-25 (`DAEO-rrxp`) ticket
lead returned from its test design. For each, the designer's, the lead's and the orchestrator's recommendations
agree, the confidence is medium or higher, and the choice is reversible. The suite on the branch already follows
them. Two are not decided here and go to the owner: DP-1 (how the command is wired, where the designer and the lead
recommend differently) and DP-3 (the checkpoint directory, which needs a guard and containment exception). The
default age and commit thresholds of DP-5 are also the owner's to name.

### DEC-279 — W1-25 DP-2: the checkpoint's schema, keys and arguments
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-2 option (a); confidence medium-high on the schema, medium on the names · **Under:** CAP-37.a, CAP-13.b, DEC-229
- **Decision:**
  - A checkpoint conforms to W1-08's kernel checkpoint schema, extended by this ticket: a markdown record with the
    frontmatter keys `task`, `trigger`, `next_action`, `created`, and `inputs` as a list of `{id, version, hash}`
    with a sha256.
  - `template/governance/kernel/schemas/checkpoint.schema.json` and
    `template/governance/kernel/templates/checkpoint.md` are added to W1-25's `allowed_paths`, in a commit with the
    trailer `Task: DAEO-rrxp`.
  - The command is `gov checkpoint --ticket <id> --trigger <ticket-transition|compaction|stop> --next <text>
    [--input <path>]…`. The ticket file is always an input; the result gives `path` and `id`. A missing argument,
    an unknown ticket or an input that cannot be hashed is an error (exit 1) and nothing is written.

### DEC-280 — W1-25 DP-4: what W1-25 shows of "every ticket transition, compaction and stop"
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-4 option (a); confidence medium · **Under:** CAP-37.b
- **Decision:** The command accepts exactly the three triggers and records which. The watchdog reports
  `CHECKPOINT_MISSING` for a ticket with no checkpoint, and `CHECKPOINT_STALE` with the reason `ticket-transition`
  when the ticket's status changed after the latest one. The calls at the three moments belong to W1-29, W1-49 and
  W1-30.

### DEC-281 — W1-25 DP-5: the `--watch` policy comes from arguments, and stale is exit 3
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-5 option (a); confidence medium · **Under:** CAP-37.c, DEC-208, DEC-237
- **Decision:**
  - Thresholds are arguments with kernel defaults: `--max-age-minutes`, `--max-commits`, and `--max-context`
    (default 0.30). The caller passes `--context-utilisation`; without it, context is not judged. The watchdog
    only reads.
  - Fresh is exit 0 with `stale` false. Stale is `CHECKPOINT_STALE`, exit 3, with the reasons listed.
  - **Not decided here, with the owner:** the default age and the default commit count. The tests pass thresholds
    explicitly. A project value in `path-map.yaml` waits until W1-29 needs one.

### DEC-282 — W1-25 DP-6: the resume brief, the family check, and one real session
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-25 package DP-6 option (b); confidence medium-high for the check, medium for the session · **Under:** CAP-20.a, CAP-37.f, CAP-38.b, DEC-232
- **Decision:**
  - `gov checkpoint --resume --ticket <id>` prints the brief (the ticket, its inputs with their hashes, the next
    step) from the latest checkpoint alone.
  - The fresh-agent-reconstruction family check is deterministic: it passes when that brief can be built for the
    latest checkpoint of every ticket that has one, and fails on a missing next step or hash.
  - The acceptance suite adds one real short headless session per run (`local_only`, the cheapest model, two
    turns, an empty directory, only the brief), as DEC-232 did for the launcher.

| Version | Date | Change |
|---|---|---|
| 0.58 | 2026-10-04 | Delegated under DEC-220: DEC-279 (W1-25 DP-2: W1-08's checkpoint schema extended; keys and arguments; two kernel files join the ticket's paths), DEC-280 (DP-4: three triggers recorded; the watchdog detects a missing or outdated checkpoint), DEC-281 (DP-5: thresholds as arguments, stale is exit 3; the defaults go to the owner), DEC-282 (DP-6: `--resume`, a deterministic family check, one real session). DP-1 and DP-3 go to the owner. |
