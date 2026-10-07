---
name: checkpoint
description: Method for writing, watching and resuming from structured checkpoints with gov checkpoint
version: "1.0.0"
---

# Checkpoint / Resume

A method for using `gov checkpoint` to write, watch and resume from structured checkpoints. The guard and the role file decide where the session may write; this skill is the method only (CAP-24.b).

## Writing a checkpoint

Invoke `gov checkpoint` with the ticket, the trigger and the next action:

    gov checkpoint --ticket <id> --trigger <trigger> --next "<text>" [--input <path>]...

Triggers are `ticket-transition`, `compaction` and `stop` (CAP-37). Every mandatory input is listed with its id, version and sha256 hash; an input whose hash cannot be computed is refused and nothing is written (CAP-37, CAP-13).

A checkpoint is a tracked file in git with frontmatter conforming to the kernel schema, so it survives a fresh clone (CAP-20).

## Mandatory triggers

A checkpoint is written at every ticket transition, at compaction and at stop (CAP-37). The hooks that call the command at compaction and stop are delivered by W1-29 and W1-49; the command itself accepts the three triggers and records which one was used.

## Watching for staleness

`gov checkpoint --watch` marks the latest checkpoint stale by policy without relying on harness hooks (CAP-37). The watchdog checks:

- **Age** (`--max-age-minutes`): time since the checkpoint was created.
- **Commits since** (`--max-commits`): commits after the checkpoint.
- **Context utilisation** (`--max-context`, `--context-utilisation`): the fraction of the context window used; about 30 % of the window is the threshold (DEC-208, DEC-237).
- **Ticket transition**: the ticket's status changed after the latest checkpoint.

A fresh checkpoint exits 0; a stale one exits 3 with the reasons. The watchdog only reads (CAP-38).

## Resuming from a checkpoint

`gov checkpoint --resume --ticket <id>` prints the brief a session needs to resume: the ticket, its inputs with hashes, the next action and the checkpoint path. A fresh agent on a fresh clone resumes the ticket at the recorded next step from the checkpoint alone (CAP-20, CAP-37).

## Governing sources

CAP-13, CAP-20, CAP-22, CAP-37, CAP-38.
