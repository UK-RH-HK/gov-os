---
type: probe
task: DAEO-49o5
reviewer_session: 78cd2d3b-698b-4ade-a4bf-6fd3a481c39c
implementer_session: 86123e70-22b3-4646-abbb-7f451cdb4c16
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: d9035982bbe7023d8c2c007deb023b8e353b39fc
---

# Probe of DAEO-49o5 (W2-16), the last round (DEC-761): judgement pass

This is the one review DEC-761 allowed, and it covers that round's change only:
- the cases in `adbeea77` (test designer);
- the repair in `fe8612d9` and `861a634d` (engineer);
- the verification checkpoint `d9035982`, which is the head probed.

The reviewer was a fresh independent-auditor, session 78cd2d3b-698b-4ade-a4bf-6fd3a481c39c. It ran read-only, launched with `--allowedTools "Bash" "Read" "Grep" "Glob"`, and its `git status` stayed empty. It ran its probes in its own temporary folders. The implementer of this round was session 86123e70-22b3-4646-abbb-7f451cdb4c16.

## Findings

```yaml
probed_commit: d9035982bbe7023d8c2c007deb023b8e353b39fc
judgement: pass
findings:
  - id: R3-NAMED
    name: "the role set in the command's own environment (DEC-761 item 4)"
    severity: HIGH
    fail_open: true
    within_named_limit: true
    behaviour: >
      From an independent-auditor session, in temporary repositories, all four of these exited 0 and wrote,
      and the guard refused none of them:
      `GOV_ROLE=orchestrator gov release 1.7.0` wrote docs/releases/1.7.0/; so did
      `env -u GOV_ROLE gov release 1.7.0`; and the same two prefixes with `--lock-from <v1.4.0 source>`
      wrote a lock recording 1.4.0.
      The same call without a prefix was refused by the command (RELEASE_REFUSED, naming
      'independent-auditor'). The command reads GOV_ROLE alone, and unset counts as the owner. It does not
      check for a plain terminal or a governed session, although CLAUDECODE=1 is set in the session.
      A script that builds its own environment without GOV_ROLE also runs as the owner.
  - id: R3-F1
    severity: MEDIUM
    fail_open: false
    behaviour: >
      Update regression, fail-closed. Take a project installed from a tag that predates the source's first
      release record (v0.9.0). `copier update` to the first release (v1.4.0) is refused: Copier 9 runs the
      task on the update's old copy too, and the history check finds records there. Nothing is applied, and
      doctor still passes. `copier recopy --overwrite --vcs-ref v1.4.0` works and gives a lock recording
      1.4.0 that passes doctor.
  - id: R3-F2
    severity: MEDIUM
    fail_open: false
    behaviour: >
      Regression for locks written before this round, fail-closed. A W1-39 plain project's lock has no
      `release` key. Doctor fails it ("its release entries may have been deleted"). `copier update` from
      v0.1.0 to v0.2.0 is refused by the task after Copier has already changed the answers file and added the
      new kernel file. The way out is to delete the lock (or edit it by hand, which its header forbids) and
      update again.
  - id: R3-F3
    severity: HIGH
    fail_open: true
    within_named_limit: true
    behaviour: >
      Laundering through `release: null`. In a project of release 1.4.0, each of these passes doctor (MATCH):
      replacing the release block by `release: null`; appending one `release: null` line under the intact
      block (YAML keeps the last key); either of those with a kernel file and its lock hash also edited.
      Deleting the lock or nulling the release, then running `--lock-from` from a plain folder or a git
      source that never held a record, writes `release: null`, and an edited kernel then passes. Only the
      literal deletion of the key fails, which closes R2-F2 in that form only.
      The cause is that sources which never held a record still install (the lead's package P-R3-1), and that
      the lock is unsigned (CAP-02.c, Wave 3).
  - id: R3-F4
    severity: MEDIUM
    fail_open: true
    within_named_limit: partly
    behaviour: >
      The removed-records refusal depends on the clone's history. Make a shallow clone
      (`git clone --depth 1 --branch v1.6.0`) of a source whose records were removed, then `copier copy` from
      it: the edited kernel installs with `release: null`, and doctor passes it. A source whose history was
      rewritten (an orphan branch, tags deleted) does the same. A full clone is refused, as built.
  - id: R3-F5
    severity: MEDIUM
    fail_open: false
    behaviour: >
      A defect in the case, confirmed:
      `test_w2_16_last_round.py::test_a_source_whose_release_records_were_removed_is_refused[copier copy]`.
      It copies into tmp_path/product, which its fixture own_release_project already fills, so Copier stops at
      its overwrite prompt (exit 1) before the task runs. The fixture's own 1.4.0 lock then passes doctor, and
      the case fails whatever the code does. A copy into a fresh folder exits 1 with the history refusal, no
      traceback, and the destination removed: every assertion of the case holds there. The engineer must not
      change the case; the test designer must, as a recorded rewrite.
  - id: R3-F6
    severity: LOW
    fail_open: false
    behaviour: >
      A refused `copier update` (to v1.6.0, records removed) leaves Copier's changes in the tree: the answers
      file names v1.6.0, two kernel files are changed, and the lock still records 1.4.0. Doctor reports
      DRIFT, and git restores the clean tree. This is Copier's order of work (tasks run after files are
      written), not something new in this round.
  - id: R3-F7
    severity: LOW
    fail_open: false
    behaviour: >
      The W1-32 rewrite compares the recorded list as a set where it compared an exact tuple, so a duplicate or
      reordered entry no longer fails it. Its purpose holds: an unrecorded command other than `release`, a
      recorded command gone, or the module command offered still fails it, and a check on the module command
      was added.
```

## Found sound (run, not read)

- **`--lock-from`:** 98 runs of 7 lock states against 7 source states, each with and without a kernel edit.
  - A lock recording 1.4.0 is never rewritten without that release:
    - a plain folder, a never-recorded git source and a removed-records source are each refused, with the lock unchanged byte for byte;
    - the genuine v1.4.0 source rewrites it, but doctor still reports DRIFT naming the edited file;
    - v1.5.0 is refused while the answers name v1.4.0, and writes a 1.5.0 lock (doctor DRIFT on an edited kernel) when they name v1.5.0;
    - a source holding records but with an edited kernel is refused.
  - A lock that is unreadable, or that has no `release` key, is refused, and doctor gives ERROR.
  - No refusal changed a file, and no lock was left half-written.
- **The release block:** doctor fails each of these:
  - the key deleted, alone or with a kernel file and its hash edited;
  - the version or the manifest hash edited;
  - the held manifest removed, or edited without re-hashing;
  - `release: {}`, `false` or `''`.

  Editing the held manifest and re-hashing it consistently is the unsigned limit (CAP-02.c).
- **Removed records, full history:** refused by `copier copy` into a fresh folder (destination removed), by `copier update` from 1.4.0 (the lock still records 1.4.0), and by `--lock-from` by hand.
- **The role check, both forms:**
  - refused, naming the role and writing nothing: `engineer`, `independent-auditor`, `independent-test-designer`, `product-spec`, `research`, `ticket-lead`, an unknown name, the empty value, `' orchestrator'`, `'Orchestrator'`, `'orchestrator '` and `'orchestrator\n'`;
  - allowed: `orchestrator`, and `GOV_ROLE` unset;
  - a Copier copy with `engineer`, `independent-auditor` or an empty role is refused and its destination removed.
- **The rewritten cases keep their purpose:**
  - W1-39's case builds a never-installed project and still asserts "unmeasured, no failure, not a match" (DEC-499, DEC-488);
  - W1-32's case: see R3-F7.
- **No regression in:**
  - `copier update` 1.4.0 → 1.5.0 (lock 1.5.0, MATCH);
  - a W1-39 plain install and update v0.1.0 → v0.2.0 (`release: null`, MATCH);
  - release locks written before this round;
  - doctor on this repository (its lock part is `unmeasured`, not red).
- **Suites run by the reviewer:**
  - W2-16: 113 passed, 1 failed (R3-F5);
  - W1-39, W1-32 and the doctor unit tests: 197 passed;
  - the lock and release unit tests and the two rewritten cases: 73 passed.

## Judgement

Pass: nothing in this round's change loses work, writes outside scope or changes acceptance tests.
- R3-NAMED and R3-F3 fail open, but inside the limits the owner named: the role set in the command's own environment (W2-H058's side), and the open package on sources that never held a record together with the unsigned lock (CAP-02.c).
- R3-F4 is a narrow gap, and not ordinary work.
- R3-F1 and R3-F2 fail closed and go to the owner.
- R3-F5 needs the test designer's recorded rewrite before the suite is green.

The lead returns R3-F1 to R3-F5 as packages and R3-F6 and R3-F7 as residuals.
