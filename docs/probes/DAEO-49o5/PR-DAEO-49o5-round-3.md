---
type: probe
task: DAEO-49o5
reviewer_session: 342c46c7-1ce2-4949-a888-d31502230927
implementer_session: 9e7e9698-737f-4380-a921-c1ba90dc56c8
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: df7a2a06e5ff91ac58dbf1691c17043973d17fc2
---

# Probe of DAEO-49o5 (W2-16), round 3 (DEC-772 item 1): judgement pass

This is the one review DEC-772 allows ("that round does only this (tests first, one review of that change)"), and it covers that round's change only, `2c8cfc7a..df7a2a06`:
- the build form's checks, the test seam, its unit tests and the owner's procedure in `bb495230` (engineer, session 9e7e9698-737f-4380-a921-c1ba90dc56c8);
- the cases in `2fa4a6da` and `0226a4ec` (independent test designer, session 75710576-1000-489b-a7b2-69ce41c35383), with `Rewrite-Reason: DEC-772` and `Rewrite-Reason: DEC-767` (R3-F5, P-R3-2 (a));
- the lead's merge of the tests, `b023b9c1` (no change of its own);
- the repair in `df7a2a06` (engineer, session b5d4caa8-6f84-4e0e-9084-1f9a1ab1a633): a missing version is the build's own refusal, after the code. This is the head probed.

The reviewer was a fresh independent-auditor, session 342c46c7-1ce2-4949-a888-d31502230927, launched through `gov launch` (sandboxed) with `--effort max` and `--allowedTools "Bash" "Read" "Grep" "Glob"`. It wrote no file of the repository and re-ran no suite (DEC-959 item 1); it ran its probes in its own temporary folder. It was judged by `governance/project/briefs/JUDGEMENT.md`'s two questions.

## Findings

```yaml
probed_commit: df7a2a06e5ff91ac58dbf1691c17043973d17fc2
judgement: pass
findings:
  - id: R4-1
    severity: LOW
    behaviour: >-
      In an unsandboxed session (a lead or the orchestrator), a process re-parented away from Claude Code
      (setsid, a double fork, a tmux server, ssh to localhost) has a chain that reaches process 1 with no Claude
      Code session in it, so the session sign alone does not refuse it. The role and ticket checks still refuse
      where GOV_ROLE or GOV_TICKET is set, and the terminal and typed-code checks refuse unless a constructed
      pseudo-terminal reads the code and types it back. In the reviewer's sandbox a re-parented process is adopted
      by the sandbox's own first process and refused for ancestry; the unsandboxed case was judged by reading. The
      freeze lift has the same exposure (DEC-409). The Claude Code session variables, which survive re-parenting,
      could be an extra sign.
    ordinary_work: "no, because it needs a deliberate re-parenting plus a pseudo-terminal driver that reads the code and types it back"
    consequence: fails open
    fail_open: true
  - id: R4-2
    severity: LOW
    behaviour: >-
      The unit test that runs the command on the real chain and the real descriptors, run by the owner from a
      plain terminal with output capture off, gets past every check, shows a code and waits for a typed line; if
      the owner types it, it builds in the test's temporary repository and the test fails. The acceptance case for
      the same situation skips instead. Judged by reading.
    ordinary_work: "no, because an agent's run never has a clean chain and pytest's default capture takes the output terminal away"
    consequence: other
    fail_open: false
  - id: R4-3
    severity: LOW
    behaviour: >-
      Outside this change: DEC-761's entry is not marked as changed by DEC-772 (item 1's line), in this worktree or
      on w2/integrate, and the 2026-10-20 supersession sweep does not list it (DEC-866 item 1).
    ordinary_work: "yes, because an agent served DEC-761 reads its orchestrator line as in force"
    consequence: other
    fail_open: false
  - id: R4-4
    severity: LOW
    behaviour: >-
      The release README's step 1 tells the owner that listing the GOV_ variables should show nothing; the command
      refuses only GOV_ROLE and GOV_TICKET. The README asks for more than the command needs, never less.
    ordinary_work: "no, because it is the owner's own procedure"
    consequence: other
    fail_open: false
```

## What was probed and found sound

1. **The build form refuses in each case DEC-772 names, before anything is written.** The checks run in the order: a Claude Code session or an unreadable chain, then `GOV_ROLE` (any value), then `GOV_TICKET` (any value), then a terminal on input and output, then the code. The code comes from the system's random source, is written only to an output already found to be a terminal, and only after every other check. What cannot be read refuses: a chain or check that raises gives `ancestry`, a descriptor that cannot be asked or written gives `terminal`, a read error gives `code`. Through the seam as the owner, the code with spaces around it built (as specified); the code in lower case, twice, with text after it, on a second line, on a non-blocking terminal, or a hang-up after the prompt refused for `code` with nothing written; an empty version, no version and `latest` with the right code refused as the build's own, nothing written. Nothing in `src/` calls the build but the seam.
2. **The real command from the reviewer's session is refused in every form, nothing written** (959 paths, `.git` included, unchanged in bytes and times): the session's own variables, the `GOV_ROLE=orchestrator` prefix, `env -u GOV_ROLE -u GOV_TICKET`, `env -i`, the installed `gov` script, and on a pseudo-terminal with no `GOV_` variable or with either set empty. The prefix forms that wrote a release in the last round's R3-NAMED are now refused.
3. **The command cannot be handed a planted chain or terminal:** it passes only the folder and the version; the parser rejects `--ancestry`, `--terminal` and anything after `--`; `--role` is not read. Known limit, in the freeze lift's form, not a new finding: any Python can import the private seam (as `_lift_test`) or the build function itself; that is a deliberate construction and leaves no tag.
4. **`--lock-from` is unchanged:** `engineer` and the empty role refused, `orchestrator` runs; `copier copy` at v1.4.0 records 1.4.0 and its manifest hash and doctor's lock part passes; `copier update` to v1.5.0 records 1.5.0 and doctor passes.
5. **The test rewrites keep their purpose and lower no expectation.** The suite's builds go through the seam with every assertion kept. The 25 build-refusal cases are stricter: the code must be accepted and the reason the build's own; their helper passed with the real seam and failed against four broken stand-ins (refused by a caller check; wrote then refused; code check always refusing; the dirty-tree rule removed). The hidden-edit case now depends on the build. The role cases hold the build form refused for all ten `GOV_ROLE` values; the positive control moved to the seam. R3-F5 is a one-line change to a fresh folder. No new case passes whatever the code does.
6. **The README matches the command:** the procedure, the prompt text, the reason words, and the lock task's rule.

## Judgement

Pass. No finding answers "yes" to both questions. R4-1 is a row for the Wave 3 hardening pass (a deliberate construction, the freeze lift's limit); R4-2 and R4-4 are residuals; R4-3 is outside this change and goes to the orchestrator (DEC-761 marked under DEC-866).
