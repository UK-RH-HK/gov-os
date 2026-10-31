---
type: probe
task: DAEO-cv58
reviewer_session: 3c32abb2-c43a-41e3-96bd-43ac8f77e57b
implementer_session: 100abccd-a36a-469a-9b37-2a9b35a7e109
reviewer_wrote_nothing: true
commissioned_by: ticket lead (orchestrator role)
judged_by: ticket lead (orchestrator role)
judgement: pass
probed_commit: 0e11b5db743df0967b7ee131e9593a1cdb05407d
---

# Probe record: W2-60a (DAEO-cv58), review 3

## Summary
A fresh reviewer (independent-auditor role, brief A3, session 3c32abb2-c43a-41e3-96bd-43ac8f77e57b) probed head
0e11b5db743d and wrote nothing in the repository. It probed round 3's five items (DEC-951 item 4) and nothing else,
then the brief's routes to a worker's local settings and the refusals of today. Method:
- 95 runs of `gov launch` from this worktree's `src` (DEC-732), with the ticket's own stand-in CLI
  (`w2_60a_support.py`, imported with bytecode off), against fixture repositories, worktrees and adopted trees built
  from scratch in the reviewer's temp folder;
- CLI 2.1.292's settings resolver, worktree resolution, owner check, git-root walk, permission-mode aliases and
  hidden options, read from its binary;
- this machine's main-checkout local settings file, read for its keys only (`env`, `permissions.allow` 24,
  `permissions.deny` 1: none of the refused keys, so round 3 refuses no real worktree launch today);
- the diffs of items (iii), (iv) and (v), and round 3's new acceptance and unit cases, by reading.
No live session (no network): the CLI side of each finding comes from its code and option text, and is marked so.
No suite or test file was run (DEC-959 item 1). `gov retrieve` returned FACET_UNAVAILABLE. Guard read refusals: 0;
one command was refused twice in two forms (the CLI's `--help` into a temp file) and not tried a third time.

## Findings

### R3-1. A gov root below the git toplevel: the local settings file the session loads is not checked
- **What was done.**
  - Read CLI 2.1.292's resolver. The local settings base is `nL(cwd, canonicalGitRoot(cwd))`.
    `canonicalGitRoot` walks up from the cwd to the first folder that holds `.git` (a folder or a file), then
    resolves a linked worktree to its main checkout. When the result differs from the cwd, is not the home folder,
    and the result, its `.git` and its `.claude` belong to the user, the session loads
    `<result>/.claude/settings.local.json`; the cwd's own copy is then only the "legacy" one.
  - `gov` takes the project root from the working directory or `--root`, and never walks up. The launcher treats a
    root with no `.git` as its own main checkout and judges only the root's two files.
  - With the stand-in, a full fixture gov project was put in `outer/proj/` of a committed repository `outer/`, with
    no `.git` in `proj/`. Each key in turn went into `outer/.claude/settings.local.json`:
    `permissions.additionalDirectories`, a `sandbox` key, `disableAllHooks`, `autoCompactWindow`.
- **What happened.**
  - Each launched from `proj/` (C1–C4): exit 0, one start, a record saying `compaction_threshold: "none"`.
  - The same from `proj/` inside a linked worktree of `outer/`, with the main checkout's local file bad, also
    launched (C6).
  - The same key in `proj/.claude/settings.local.json` is refused (C5). The control launches (C0).
- **What should have happened.** The launcher finds the local settings file as the CLI does (the first folder at or
  above the root that holds `.git`, then its main checkout) and judges it. Failing that, it refuses a root that
  holds no `.git` but lies inside a git repository.
- **Severity.** Would be high (review 2's F1 again) if the layout were in use. Today it is not.
- **Reproduced:** the launcher side, with the stand-in. The CLI side from its code, not live.
- Ordinary work: no, because every gov project in use (this repository, its worktrees and DEC-487's adopted layout) has its root at the git toplevel, and a root below it needs a whole gov project (tickets, guard-wired settings, role files) in a subfolder of another repository, which no current work or adoption form produces; it is an entry criterion (DEC-803) for any ticket that supports that layout.
- Consequence: fails open

### R3-2. `--project-config-root` after `--` moves the project and local settings out of the launcher's sight
- **What was done.**
  - Read CLI 2.1.292. It has a hidden option `--project-config-root <dir>` ("Read project settings, .mcp.json and the
    .claude config trees (commands, agents, skills, workflows, routines, output-styles) from this directory rather
    than the working directory (for a session a host starts in a worktree of it)").
  - By its resolver, the local settings then come from `<dir>/.claude/settings.local.json` as well.
  - With the stand-in, `<dir>` held a `.claude/settings.json` with `permissions.defaultMode: bypassPermissions` and
    a local file with `permissions.additionalDirectories`.
- **What happened.**
  - `-- --project-config-root <dir>` and `-- --project-config-root=<dir>` both launched (F1, F2): exit 0, one start,
    the argument passed unchanged.
  - By the CLI's code, such a session loads neither the tree's guard-wired `.claude/settings.json` nor the files the
    launcher judged, and its skills are not the ones the record names.
- **What should have happened.** It is refused after `--`, as `--settings` and `--setting-sources` are.
- **Severity.** High in effect: no guard hooks. It is reachable only through a hidden option.
- **Reproduced:** the launcher side, with the stand-in. The CLI side from its code and option text (hidden from
  `--help`), not live.
- Ordinary work: no, because the option is hidden from `--help` and documented only for a host that starts a session in a worktree, and the common lead brief fixes the worker form, which does not carry it; it joins review 2's R4 (arguments on no refusal list), unchanged by round 3.
- Consequence: fails open

### R3-3. A broken `.git` is now refused at the repository-settings step
- **What was done.** A worktree's `.git` file was pointed at a missing admin folder, and the CLI was also moved away
  (B11). In a second run the ticket was unknown (B12).
- **What happened.**
  - The refusal is now the `.git` look-up's: "the tree's .git cannot be read or gives no common directory, so the
    local settings file the CLI loads for a worktree session cannot be found". It comes at Behaviour 10's step 4,
    before the CLI check (step 5), the built settings (step 6) and the role file (step 7). In round 2 it came at the
    record folder (step 8).
  - The argument and ticket checks still come first (B12: "unknown ticket").
  - No launch refused before now launches; only the message shown when two faults coincide changed. The design
    states this order (Behaviour 10, step 4).
  - W2-60a's acceptance case for this asserts `LAUNCH_REFUSED` only, and still holds.
- Ordinary work: yes, because a worktree folder whose admin folder was pruned or moved has such a `.git`.
- Consequence: other

### R3-4. The adopted layout's limits fail closed
- **What happened.**
  - **An unrelated `template/`.** An adopted tree with an unrelated folder of its own named `template/` keeps the
    template path and is refused, naming `template/governance/kernel/roles/engineer.md` (D5). This is the CIT-E's
    stated rule.
  - **A research launch.** In an adopted tree it is still refused, on `template/governance/kernel/launch/research-allowlist.yaml` (D8).
    Item (ii) moves the role file's path only (DEC-951 item 4). Every other worker role now launches there.
- Ordinary work: yes, because a repository may carry a `template/` folder of its own, and an adopted copy may start a research worker.
- Consequence: other

### R3-5. A `.git` file straight at another repository's `.git` folder
- **What happened.**
  - The tree's `.git` file was pointed straight at another repository's `.git` folder, which has no `commondir`
    (B8, B9). The launcher judged that repository's local file and refused a bad key there (B8).
  - By the CLI's code the session itself falls back to the tree's own file, since the admin folder is not under
    `worktrees/` with a matching back-link. So this check is extra, not missing.
  - With that repository's file clean, the launch wrote its record in that repository's `.gov-runtime/launches/`
    (B9).
  - This comes from round 1's record-folder look-up and is unchanged in round 3, which only shares it.
- Ordinary work: no, because git writes such a file only for a separate git directory named `.git` elsewhere, or by hand.
- Consequence: other

## Probed and found sound
- **(i), the main checkout's local file, from a linked worktree.**
  - Refused, naming the file by its full path, with no start and no record (A2–A14): `sandbox`, `disableAllHooks`,
    `permissions` not a map, `defaultMode: bypassPermissions`, `additionalDirectories`, `agent`, `env` not a map,
    `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `autoCompactWindow`, `env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`,
    `env.CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`, `modelSettings.<another model>.autoCompactWindow`, and a
    `modelSettings` that is not a map of maps.
  - Also refused: a top level that is a list or `null` (A15, A16; the message is DEC-233's "carries a sandbox key",
    which covers "not a map" too, the base's wording); an empty file, a BOM, a comment, text that is not JSON
    (A17–A20); a link to a bad file (A21); a dangling link (A22); mode 000 (A23); a folder at the name (A24); the
    main checkout's `.claude` as a link to a folder holding a bad file (A25).
  - A file shaped as this machine's real one (`env`, allow and deny rules) launches (A1). Controls launch before
    and after (A0, A29).
- **A launch from the main checkout** judges its own local file once, named by its relative path (A26).
- **The tree's own local file is still judged.** When both files are bad, the tree's own is named first (A27).
- **The `.git` forms.** A relative `gitdir:`, a CRLF line and an absolute `commondir` all find the main checkout
  and judge its file (B1–B3). A missing admin folder, an empty `.git` and one without `gitdir:` refuse, naming the
  look-up (B5–B7). A `commondir` at a bare repository refuses (B10). A clean main checkout adds no refusal (B4,
  B13).
- **The CLI side (from its code).** For a root that holds `.git`, the CLI's local file is the main checkout's when
  the worktree's admin folder lies under `<common>/worktrees/` with a matching back-link and the owner check
  passes; otherwise it is the cwd's own. Both are among the files the launcher judges.
- **The CLI's schema has no other spelling of the refused keys.** `permissions.additionalDirectories`,
  `disableAllHooks` and `permissions.defaultMode` are the only forms. The modes are `acceptEdits`, `auto`,
  `bypassPermissions`, `default`, `dontAsk` and `plan`, and the only alias is `manual` for `default`.
- **Settings after `--`.**
  - `--settings`, `--setting-sources=user` and `--bare` are refused (E4–E6).
  - `--managed-settings` launches (F3), but by the CLI's own text it is filtered to restrictive settings only, so it
    cannot loosen the launcher's.
  - `--forward-home-settings` needs `--cloud` or `--environment` (R4's class).
- **(ii), the adopted layout.**
  - The adopted control records `governance/kernel/roles/engineer.md` with the hash of exactly the bytes appended
    (D0).
  - A `template` that is a file or a dangling link refuses, naming the template path (D1, D3).
  - Both layouts present: the template's file is read, recorded and appended (D4).
  - Neither present: refused, naming the adopted path (D6).
  - A `template`, or the adopted role file, that is a link is read through the link and recorded under the tree's
    path, with the hash of the bytes appended (D2, D7), as round 1 read the template path. The record and the
    appended text never part.
- **The refusals of today all still refuse with their messages (E1–E21).**
  - Arguments: DEC-313's three; `--settings`, `--setting-sources`, `--bare`; `--agent`; a model not the role's;
    `--autocompact`; `--append-system-prompt-file=`; `--session-id`; a resume with no record.
  - Role and ticket: the worker-role check; a closed ticket; another role's ticket.
  - Repository settings, in both of the tree's files: a sandbox key (DEC-233), DEC-313's keys, the agent key, a
    compaction threshold; and the guard not wired.
  - The rest: DEC-218's malformed held-out list; a missing role file; a `.gov-runtime` that is a file.
- **DEC-392 and DEC-386.** SIGTERM during the session: exit 130, the temp folder removed, the session's record kept
  (G1).
- **(iii).** The diffs of `test_runs.py`, `test_w1_28.py` and `test_w1_32.py` add only the role file in each
  fixture (the `ROLE` text and `_role_file`). No assertion, monkeypatch or other expectation changed.
- **(iv).** The line routes `test_w2_60a_live_sessions.py` (`local_only`) to the nightly, where every listed entry
  runs alone. The close deselects it from its phases and never skips or ignores it.
- **(v).** The Haiku role file moves into the base commit through the builder's existing `extra` parameter, so the
  tree is clean when the session starts. The assertions of the phantom-deletion pair are untouched.
- **No acceptance expectation is lowered.**
  - Round 3 changed no existing acceptance case but W2-58's fixture.
  - The 10 new cases cover 8 of the main-checkout keys, a file that is not JSON and the adopted control; the probes
    above cover the rest.
  - The ticket's own unit files gained cases. Their removed lines are a docstring line, an import line and a
    builder's signature.

## The lead's judgement (JUDGEMENT.md)
- R3-1 and R3-2: "Ordinary work: no" with "fails open": rows for the Wave 3 hardening pass, never a round (DEC-801).
  R3-1 is an entry criterion (DEC-803) of any ticket that supports a gov project below its repository's git toplevel;
  R3-2 joins review 2's R4 (arguments on no refusal list; W2-56's refusal list).
- R3-3 and R3-4: "Ordinary work: yes" with "Consequence: other" (each fails closed): residuals.
- R3-5: "Ordinary work: no", "Consequence: other": a row.
- No finding has "yes" with "fails open" or "loses work": the probe passes. Review 3 was the ticket's last round
  (DEC-951 item 4).
