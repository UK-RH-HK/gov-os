---
type: probe
task: DAEO-cv58
reviewer_session: b4e10217-0b62-4ac3-8912-49006c77e2e5
implementer_session: e4fca52c-08d5-47ca-833c-2a068fbca603
reviewer_wrote_nothing: true
commissioned_by: ticket lead (orchestrator role)
judged_by: ticket lead (orchestrator role)
judgement: fail
probed_commit: e34e07b7ce32
---

# Probe record: W2-60a (DAEO-cv58), review 2

## Summary
A fresh reviewer (independent-auditor role, brief A3, session b4e10217-0b62-4ac3-8912-49006c77e2e5) probed head
e34e07b7ce32 and wrote nothing in the repository. Round 2's changes came first (command files as skills, the user's
ask and deny rules, the compaction spellings, the four refused arguments), then the brief's full list. Method:
- `gov launch` from this worktree's `src` (DEC-732), against a stand-in CLI and fixture repositories and worktrees
  built from scratch in the reviewer's temp folder with the ticket's own `w2_60a_support.py`;
- CLI 2.1.292's `--help`, run with a throwaway home, and its binary read for compaction spellings, setting-source
  resolution, skill and command loading, the memory switch, `/autocompact` and `/add-dir`;
- the owner's user settings file and the main checkout's local settings file, read for their shapes only;
- DEC-392's 18 signal cases rerun with a fixture role file;
- 12 test files, one at a time (the nightly was running).
No live session (no network): the CLI's side of each finding comes from its code and help, and is marked so.
`gov retrieve` returned FACET_UNAVAILABLE (facets stale). Guard refusals: 0.

## Findings

### F1. A worktree launch never checks the local settings file the session loads
- **What was done.**
  - Read CLI 2.1.292's settings resolver. For a session started in a git worktree it takes the local settings from
    the canonical git root, that is the main checkout's `.claude/settings.local.json`. This applies on POSIX when
    the main checkout, its `.git` and its `.claude` belong to the session's user.
  - The CLI's worktree code skips copying `settings.local.json` into a new worktree "because it resolves
    localSettings to the canonical repo root". This reviewer's own worktree session has the main checkout's
    `settings.local.json` on its sandbox's write-deny list, beside the worktree's own settings files.
  - The CLI's `/add-dir` prompt offers "Yes, and remember this directory", which it saves as
    `permissions.additionalDirectories` in the local settings source.
  - With the stand-in: a fixture repository and a worktree of it. Each of eight keys was put in turn into the main
    checkout's `.claude/settings.local.json`, then `gov launch engineer <ticket>` ran from the worktree. The keys:
    `autoCompactWindow`, `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `modelSettings.<model>.autoCompactWindow`, `agent`,
    a `sandbox` block, `permissions.defaultMode: bypassPermissions`, `permissions.additionalDirectories` and
    `disableAllHooks`.
- **What happened.**
  - All eight launched: exit 0, one session, a record saying `compaction_threshold: "none"`.
  - The same eight keys in the worktree's own `.claude/settings.local.json` were each refused, with the existing
    message or this ticket's.
  - On this machine the main checkout's local settings file exists, and by the CLI's code every worker launched in a
    worktree loads it. It holds `env` (`GOV_ROLE=orchestrator`, `GOV_TICKET`, `GOV_DEV_TIERS`), 24 allow rules and
    1 deny rule, and none of the eight keys today.
  - The gap is unchanged from base a1629f1860ca for DEC-233, DEC-313 and the hooks check. This ticket's new agent
    and compaction refusals (Behaviour 6) have it too, and its `--setting-sources project,local` keeps that source.
- **What should have happened.** The launcher checks the local settings file the CLI loads for the tree: for a
  worktree, the main checkout's as well as its own. Then DEC-233, DEC-313, the hooks check, this ticket's agent and
  compaction refusals, and the record's "none" all hold for worktree launches.
- **Severity.**
  - High for DEC-313's added-directory refusal. One ordinary CLI prompt writes the key, and a worker then runs with
    an added directory DEC-313 refuses. With `--permission-mode acceptEdits` the file tools may edit there without
    asking, leaving the guard's allowed-paths check as the remaining layer. Whether the CLI also puts the directory
    on the sandbox's write list was not established.
  - Medium for this ticket's compaction and agent checks: only a hand edit puts those keys there, since the CLI's
    `/autocompact` saves to the user settings file, which the launch drops.
- **Reproduced:** the launcher side, with the stand-in; the CLI side from its code and this session's sandbox,
  not live.
- Ordinary work: yes, because the CLI's own `/add-dir` prompt ("Yes, and remember this directory") writes an added directory into that file during the owner's interactive work; the file already holds the owner's env and allow rules; and every Wave 2 worker is launched in a worktree.
- Consequence: fails open

### R1. A worktree without `.claude/skills/` or `.claude/commands/` loads the main checkout's
- **What was done.** Read CLI 2.1.292's project-folder walk: when the worktree's folder of that name is absent, it
  adds the canonical root's, for skills and for commands and agents. With the stand-in:
  - commands present only in the main checkout (untracked): the worktree launch's record listed the four skills and
    no command;
  - skills present only in the main checkout, with no `.claude/skills/` in the worktree: the record listed none.
- **What should have happened.** The record names what the session can load, wherever the CLI finds it.
- **Reproduced:** CLI side from its code, not live.
- Ordinary work: no, because this repository tracks both folders, so every worktree of a current branch has its own; it arises on a branch that removes one, or in a repository that does not commit `.claude/` (an entry criterion for EXAMIN's copy if its `.claude/` is generated and untracked, DEC-803).
- Consequence: fails open

### R2. Skills found during the session are not in the record
- **What was done.** Read CLI 2.1.292: skills under a `.claude/skills/` in a subfolder become available while the
  agent works there ("New skills discovered in …, now available via the Skill tool"). The record is written before
  the start and names only the root's skills. No tracked file of this repository lies under a nested `.claude/`.
- Ordinary work: no, because no nested `.claude/skills/` exists in this repository and a worker would have to create one inside its allowed paths.
- Consequence: fails open

### R3. A resumed session that compacts takes this launch's role text; its record names the original's
- **What was done.**
  - The CLI's help for `--system-prompt-snapshot` says the recorded prompt is reused on every request and resume
    "until the conversation is compacted". Probe f2 measured a resumed session without compaction.
  - With the stand-in: launch, change the role file's version, resume, resume again. Both resume records name the
    original's version (1.4.2) and link the chain through `resumes`. The file handed to the resumed session is the
    new role file (1.4.3), so its hash differs from the record's `appended_sha256`. This is as designed.
  - After the resumed session compacts, its prompt would come from that handed file.
- **Reproduced:** from the help text, not live.
- Ordinary work: no, because the two differ only when the role file or a named skill changed between the original launch and the resume, and only after the resumed session compacts.
- Consequence: other

### R4. CLI arguments on no refusal list
- **What was done.** With the stand-in, each of these launched after `--`: `--bg`, `--from-pr 12`, `--teleport`,
  `--cloud x`, `--desktop`, `--remote-control`, `-w probe`, `--debug-file <path>`, `--permission-mode auto`.
  `--environment` is in the help but was not run.
- **Per the CLI's help:**
  - `--bg` returns at once and runs the session in the background. The launcher then removes the temp folder that
    holds `role-<role>.md` (DEC-386). With `--resume`, `--bg` "continues that session ... under the same ID".
  - `--from-pr` and `--teleport` resume a session the record does not name.
  - `--cloud`, `--desktop` and `--remote-control` run the session elsewhere.
  - `--debug-file` writes from the unsandboxed CLI process to any path.
- **Reproduced:** the launches only, not live.
- Ordinary work: no, because the common lead brief fixes the worker form (`-p … --permission-mode acceptEdits --allowedTools …`, with `--resume <session_id>` for a resume), and none of these is in it.
- Consequence: fails open

### R5. The user's `disableAutoMode` is dropped
- **What was done.** The owner's user file sets `permissions.disableAutoMode: "disable"` and `defaultMode:
  acceptEdits`. `--setting-sources project,local` drops both, and the launcher carries only ask and deny. With the
  stand-in, `--permission-mode auto` after `--` launched, and the settings do not carry `disableAutoMode`. The CLI
  ignores `defaultMode: auto` from project and local settings (its code), so only the caller's argument reaches
  auto mode.
- Ordinary work: no, because every prescribed form passes `--permission-mode acceptEdits`.
- Consequence: fails open

### R6. With `CLAUDE_CONFIG_DIR` set, the rules carried come from another file
- **What was done.** With the stand-in: ask and deny rules in `$CLAUDE_CONFIG_DIR/settings.json` (the CLI's user
  file when the variable is set, which the launch drops) and none in `~/.claude/settings.json`. Nothing was carried,
  and the variable reached the session.
- Ordinary work: no, because it is not set on this machine, and W2-56's cleaned environment drops it.
- Consequence: fails open

### R7. `CLAUDE_CODE_DISABLE_AUTO_MEMORY=0` forces model-side memory on
- **What was done.** Read CLI 2.1.292's memory switch: it reads the variable before `autoMemoryEnabled`. A true
  value turns memory off and a false one forces it on. A settings `env` block that carries the variable (the
  repository's, or the main checkout's local) is not refused. The process environment is W2-56's.
- Ordinary work: no, because nothing on this machine sets it.
- Consequence: fails open

### R8. A record stays for a session that never ran
- **What was done.** With the stand-in exiting 1 on its own, as the CLI does on an argument it rejects: the record
  stayed. A later `gov launch … -- --resume <that id>` passed the launcher's check, where the CLI would find no
  conversation. Only a CLI that cannot be started removes the record.
- Ordinary work: yes, because a typo in an argument after `--` is ordinary.
- Consequence: other

### R9. A carried user rule written as `/path` would change meaning
- **What was done.** Read CLI 2.1.292's resolver: each settings source gives its own base for rule paths, and for
  `--settings` that base is the folder of the CLI's temp copy of the value. A user Read or Edit rule written as
  `/path` would therefore point elsewhere once carried. The owner's 7 ask rules are all `Bash(...)` command
  patterns, and there are no deny rules, so nothing on this machine is affected.
- Ordinary work: no, because the owner's user file carries no Read or Edit ask or deny rule.
- Consequence: fails open

### Named for other tickets (not findings of this ticket)
- **W2-56.**
  - A parent's `CLAUDE_CODE_AUTO_COMPACT_WINDOW` reaches the session's process: the one red acceptance case.
  - `--safe-mode`, `--restricted`, `--mcp-config`, `--plugin-dir`, `--plugin-url`, `--agents` and `--system-prompt`
    launch at this head.
  - `GOV_DEV_TIERS` from the main checkout's local settings `env` reaches every worktree worker through the CLI's own
    settings env, so a cleaned process environment alone does not remove it.
- **W2-21**, when leads are sandboxed: `gov launch` writes `<main checkout>/.gov-runtime/launches/` from the lead's
  Bash, so a lead's write list without it refuses every launch (fails closed). An entry criterion (DEC-803).
- P-W2-60a-2 and P-W2-60a-3 are unchanged; not re-raised.

## Probed and found sound
- **Round 2, F1 (command files).**
  - `.claude/commands/<ns>/<name>.md` is recorded as `<ns>:<name>`, and two levels deep (`a:b:deep`) too, in path
    order, after the skills.
  - The CLI's command loader also takes `.md` case-sensitively: `UPPER.MD` is neither loaded nor recorded.
  - A file directly under `.claude/skills/` is no skill to either. Project skills load from the folder's direct
    children, as the record reads them.
  - Links are refused (the CLI would follow them). 12 tests pass.
- **Round 2, F2 (user rules).** The owner's 7 ask rules reach `permissions.ask`. Nothing else of the user file is
  carried: no allow rule, `defaultMode`, `env`, `effortLevel`, or `modelSettings` (where `/autocompact` saves).
  The file has no hooks and no sandbox block. 19 tests pass.
- **Ride-along, compaction spellings.** The CLI's own list of compaction names is `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`,
  `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`, `CLAUDE_CODE_MAX_CONTEXT_TOKENS`,
  `DISABLE_AUTO_COMPACT` and `DISABLE_COMPACT`; its keys are `autoCompactWindow`,
  `modelSettings.<model>.autoCompactWindow` and `autoCompactEnabled`.
  - Every threshold spelling is refused in the tree's settings.
  - `autoCompactThreshold` is an output field, not an input.
  - `CLAUDE_CODE_MAX_CONTEXT_TOKENS` applies only to models whose window is unknown.
  - The disable switches set no threshold.
- **Ride-along, refused arguments.** `--fallback-model=…`, `--chrome=true`, `--ide`, `--system-prompt-snapshot=off`,
  `--autocompact=auto`, `--model opus`, a bare `--resume`, `-pr` and `-cp` are refused, with no start and no
  record. 57 tests pass, among them the existing refusals and their order.
- **Model.** The line always carries the role's model. A repository or local `model` or env value loses to it. The
  launcher's settings env outranks local settings env: this session shows `GOV_ROLE=independent-auditor`, though the
  main checkout's local file sets `orchestrator`.
- **Records.**
  - Written before the start; the stand-in sees them at its start, on worktree launches and on resumes too.
  - Keyed by the launcher's id. A resume of a session with no record, such as one started before this change, is
    refused with no start and no record.
  - A resume chain links through `resumes`.
  - For a worktree launch, the record folder lies in the main checkout, off the session's write list (the temp
    folder and its run folder only), and is named by both literal `Edit` deny rules. `.gov-runtime/` is ignored by
    git.
- **DEC-392 and DEC-386.** All 18 signal cases pass with a fixture role file. Every started session left one
  record, and a signal before the start left no temp folder and no record.
- **This reviewer's own session** was started by a launcher from before this change: the main checkout has no
  `launches/` folder, and the session carries claude.ai connectors and user-level agents. It says nothing about this
  head.
