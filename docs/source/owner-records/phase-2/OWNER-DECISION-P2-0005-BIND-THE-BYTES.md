# OWNER-DECISION-P2-0005 — Bind what will run, not what it means

| Field | Value |
|---|---|
| Record | Owner decision (product owner, 2026-09-21) |
| Id | **OD-P2-05** |
| Status | IN FORCE for Phase 2 and later phases until the owner changes it |
| Supersedes | nothing; it settles how OD-P2-03 requirement 3 is satisfied for tool installation |
| Raised by | P2-AR-0068, the independent adversarial pre-mint review: 25 of 33 command shapes installed ungated and wrote outside the project root, and one family — a script file — cannot be caught by any list |

## The question put to the owner

OD-P2-03 requirement 3 says an installation the OS cannot **evaluate** must gate. Requirement 6 says a conforming
installation must still proceed **without** the owner's gate. Two iterations have tried to satisfy both by enumerating the
command shapes the OS cannot read — first a per-token scan (defeated by wrapping, iteration 1), then a positive allowlist of
readable shapes (defeated 25 ways, iteration 2). The set of programs that take code as an argument is unbounded while any
list is finite, and a script file (`sh installer.sh`, `./installer.sh`, `python3 setup.py install`) is opaque by nature
while being what most real installers are.

## The decision

**Bind the bytes, not the meaning.** The OS stops trying to read what a command *does* and instead binds exactly *what
will run*:

1. **Every file a command executes must be hash-pinned in the descriptor and re-verified at the moment of every
   execution.** An unpinned file, a file whose hash no longer matches, or a file that cannot be read gates and does not run.
2. **Inline code cannot be pinned, so it gates.** A command carrying code as an argument has no artefact to bind.
3. **Classification is conservative and fails closed.** A command is admitted to the ungated path only when the OS can
   confidently classify every argument as either a pinned file it has verified, or a plain argument with no code or file
   semantics. Anything it cannot classify with confidence is `undetermined` and gates. A missed classification must fail
   towards the gate, never away from it.
4. **The independent governed review carries the judgement the OS cannot make.** This is the architecture OD-P2-03 already
   assumed: the OS binds identity and integrity; the reviewer judges intent. Both are required for the ungated path.
5. **Pinning is a lifetime property, not an install-time one.** Re-verification at execution closes the case the reviewer
   demonstrated, where a health-check script was changed after a clean install and re-executed with no gate, no re-review
   and no pin check.

## What the owner accepted

- Projects must pin the files their installations execute, and the pins must survive legitimate updates through the
  governed path rather than by hand.
- The OS still cannot tell a benign pinned script from a malicious pinned script; it guarantees only that what runs is
  exactly what was reviewed, and that any change re-gates. That is a deliberate division of labour, not an oversight.
- The enumeration weaknesses the reviewer found (exec prefixes such as `env`/`nohup`/`timeout`, combined and equals flag
  forms such as `-ce` and `--eval=`, flagless interpreters such as `awk`) must still be fixed, because classification —
  now failing closed — depends on recognising inline code.

## Relationship to the other records

- **OD-P2-03** stands: a tool installation gates only when it expands authority, and a conforming installation inside the
  authorised envelope proceeds ungated. This decision says how requirement 3's "cannot be evaluated" is discharged.
- **OC-P2-04** stands and is unaffected: the envelope's authorised side derives from authenticated or sealed state, and a
  project-editable file may narrow but never increase trusted authority.
- A verifier may find this implementation insufficient; that is a finding against the implementation, not a reopening of
  the decision. The owner may override at any time.
