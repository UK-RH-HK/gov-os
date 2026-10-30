---
type: probe
task: DAEO-cv58
reviewer_session: 1f4229a8-5f95-43e8-83e5-9b9e23bfafcc
implementer_session: 475f2678-ffe4-4227-9e70-952a668336e6
reviewer_wrote_nothing: true
commissioned_by: ticket lead (orchestrator role)
judged_by: ticket lead (orchestrator role)
judgement: fail
probed_commit: 3b32a1070af1
---

# Probe record: W2-60a (DAEO-cv58), review 1

## Summary

A fresh independent-auditor session (brief A3, CLI 2.1.292, sandboxed, read-only on the repository) probed head
3b32a1070af1 against base a1629f1860ca. Every gov run used this worktree's src (DEC-732; gov.__file__ =
/home/usain/gov-os-worktrees/W2-60a/src/gov/__init__.py). Memory first: one batched gov retrieve call. The
code-graph tool was not used: the three changed modules were read whole.

Method:
- A stand-in CLI and fixture repositories built from scratch in the session's temp folder, using the suite's own
  w2_60a_support.py; about 55 gov launch runs over five probe scripts.
- The CLI's own option list (claude --help, under a throwaway HOME), and the CLI binary searched for the settings and
  variables it reads.
- The real CLI run once with a mistyped option, under a throwaway home with no sign-in.
- Four single test files run.

No live session was possible (no network). What a real session would do is marked as read from the CLI's code or
help, not measured.

Outcome:
- Three findings. F1 and F2 are "Ordinary work: yes" with "fails open" or "loses work", so the judgement is fail.
  F3 is yes/other.
- Six rows for the Wave 3 hardening pass, and one entry criterion (DEC-803).
- W2-56's items are named, not counted as findings.

## Findings

### F1. The project's command skills are loadable in every launch and in no launch record

- Done:
  - A fixture project with two command files (.claude/commands/opsx/apply.md and .claude/commands/top.md) beside
    the four fixture skills under .claude/skills/, then one engineer launch.
  - Read the repository: it tracks six command files under .claude/commands/opsx/ (apply, archive, explore,
    propose, sync, update).
  - This reviewer's own CLI 2.1.292 session offers all six as skills its Skill tool can load (opsx:apply …
    opsx:update), each with the description written in the matching file. No user-level ~/.claude/commands/
    exists, so they come from the project.
- Happened:
  - The launch started. The record's skills held only the four .claude/skills/ entries; nothing in the record names
    a command file.
  - The launcher describes only .claude/skills/*/SKILL.md (src/gov/launch/role.py:90-119).
  - The CIT-E (Behaviour 2), the research record and the acceptance tests never mention .claude/commands/.
- Should have happened:
  - KPI line 2: "The skills the session can load are in the launch record … taken from the copy the session loads".
  - Failure line 1: "A launch that starts with … an unrecorded skill".
  - Each command file recorded (name, path, version or "no version", hash), or the launch refused, as Behaviour 2
    refuses a skills folder the record could not describe.
- Not measured: a live start under --setting-sources project,local listing them. That switch keeps the project
  source that holds them (w3: "the project's hooks, agents and skills stay").
- Severity: medium (every launch in this repository; provenance, not a permission).
- Ordinary work: yes, because this repository tracks six command files, so every launch made here after the merge
  starts with six loadable skills its record does not name.
- Consequence: fails open

### F2. The owner's user-level ask rules no longer reach launched workers

- Done:
  - Read ~/.claude/settings.json (key names and permission patterns only; no values printed).
  - Read the repository's .claude/settings.json.
  - Read the CLI's Bash permission code.
  - A stand-in launch shows the new line's --setting-sources project,local.
- Happened:
  - The user settings hold seven ask rules: rm, rm -r and rm -rf, and four forms of owner-ping. They hold no deny
    rule and no hook.
  - The repository's settings hold no ask rule.
  - The new line drops the user source, so a launched worker has none of the seven.
  - In CLI 2.1.292, matching deny and ask rules are taken before the sandbox's auto-allow ("Auto-allowed with
    sandbox"), and a -p session cannot answer an ask (the print-mode message "… but you haven't granted it yet").
  - So today a gov launch worker's rm is asked, and so refused. After this change a sandboxed rm runs unasked.
  - The guard still treats rm as a write and checks its operands against the ticket's allowed paths
    (src/gov/guard/decide.py:52, :676), so the exposure is the worker's own paths and folders.
  - The user's defaultMode acceptEdits goes too. A launch form without --permission-mode then has its edits asked
    and so refused (fails closed).
- Should have happened: Behaviour 4 names that the drop takes "the user's model, permissions and hooks", and the
  launcher re-sets only model, effort and subagent model. The protections in the dropped permissions should be
  carried into what the launcher or the repository sets, or named to the owner as accepted.
- Not reproduced live (read from the CLI's code).
- Severity: medium.
- Ordinary work: yes, because every launched worker after the merge runs without them, and workers run rm in
  ordinary work.
- Consequence: loses work (a mistaken rm -r inside the ticket's allowed paths can delete uncommitted work that the
  owner's ask rule stops today; owner-ping also runs unasked where the sandbox lets it)

### F3. A CLI that starts and then refuses its arguments leaves the record of a session that never ran

- Done:
  - The stand-in set to exit 1 at once.
  - The real CLI with a mistyped option (--allowedTool), under a throwaway home: "Error: unknown option
    '--allowedTool'", exit 1, at parse time.
- Happened: the launch exits 1 and leaves one record, keyed by a session id the CLI never used. The record is written
  before the start, as designed, and is removed only when the CLI cannot be started at all
  (src/gov/launch/launcher.py:439-444).
- Should have happened: Behaviour 9 says "so no record names a session that never ran". A CLI's own refusal at start
  (a mistyped argument, the x1 refusal, a sign-in failure) is such a case.
- Severity: low.
- Ordinary work: yes, because a mistyped argument or a start error happens in ordinary work.
- Consequence: other (a stray record with no transcript; nothing runs, nothing is lost; W2-60b, which reads the
  session's own log, can mark it)

### Rows for the Wave 3 hardening pass

R1. CLI 2.1.292 options on neither ticket's refusal list. Each was launched with the role's --model on the line and
the record unchanged:
- --fallback-model (spaced and "="): turns can run on another model when the default is overloaded, while the record
  names the role's (KPI line 4).
- --from-pr, --teleport, --cloud: resume or attach another session; the record says resumes null.
- --bg / --background: the CLI returns at once. The launcher then removes the temp folder that holds role-<role>.md
  and the sandbox's write folder, and signals no longer reach the session.
- --chrome, --ide: connectors (KPI line 6).
- -w / --worktree: the session moves to a new worktree and loads that tree's skills, not the copies recorded.
- --system-prompt-snapshot off: a resumed session then takes the resume's text, not the original's that its record
  holds.
- --system-prompt-file is P-W2-60a-3, already named.
- Ordinary work: no, because no launch form in the prompt, the briefs or lens F's record carries any of them.
  Lens F notes the absence of --fallback-model.
- Consequence: fails open for --fallback-model, --chrome, --ide and --cloud; other for the rest. This is the class
  W2-56's CIT-E weighs as an accepted-arguments list (lens E R6).

R2. Compaction spellings the repository-settings check does not know, each launched with compaction_threshold
"none" in the record, from .claude/settings.json or .claude/settings.local.json:
- env CLAUDE_AUTOCOMPACT_PCT_OVERRIDE (the CLI reads it from its environment as a compaction percentage);
- modelSettings.<model>.autoCompactWindow (the CLI reads it per model from every settings source);
- env CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS.
- Ordinary work: no, because the repository's settings are the owner's (generated, CIT-P), workers cannot edit
  .claude/** (DEC-315), and none sets them today.
- Consequence: fails open

R3. Project settings that add context the record does not describe: enabledPlugins (plugin skills, agents and hooks)
and outputStyle, both launched.
- Ordinary work: no, the settings are the owner's and none sets them.
- Consequence: fails open for enabledPlugins; other for outputStyle.

R4. The CLI's help says a resumed session reuses its recorded system prompt "until the conversation is compacted".
After a compaction, a resumed session may take this launch's role text while its record holds the original's
(Behaviour 8). The two differ only when the role file changed between the launches. Not reproduced (help text).
- Ordinary work: no, because resumes stay fresh sessions from the checkpoint until W2-21 (w2 prompt, line 77).
- Consequence: other

R5. A prompt that begins with -r or -c (for example -p "-rf is a flag") is refused as a resume or continue spelled
otherwise. Behaviour 7 says a prompt that only names one as a word passes.
- Ordinary work: no, such prompts are rare.
- Consequence: other (fails closed)

R6. A main-checkout session and the record folder: there the folder lies inside the session's working folder. The
two literal Edit rules and the guard's DEC-180 refusal stand; the operating system's refusal waits on W2-56's literal
write list, as the CIT-E names.
- Ordinary work: no, workers start in worktrees, where the folder is outside every write path.
- Consequence: fails open, if the sandbox does not turn the Edit rule into a write denial (not measured, DEC-873).

### Entry criterion (DEC-803)

E1. When a lead's own session is sandboxed (W2-56, W2-21), its write list must hold the main checkout's
.gov-runtime/launches/. gov launch makes that folder and writes the record from the lead's process, and a folder it
cannot make or write refuses every launch. The probe confirmed the refusal with a read-only folder, and no temp
folder was left behind. This fails closed.

### W2-56's (named; not this ticket's findings)

- The process environment: the caller's CLAUDE_CODE_AUTO_COMPACT_WINDOW reaches the session (the one known red).
  So do CLAUDE_AUTOCOMPACT_PCT_OVERRIDE, CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS, ANTHROPIC_MODEL and the effort
  variables, because the CLI is started with the caller's environment plus the settings' env.
- At this head, as at the base, --mcp-config, --safe-mode (which skips the hooks, so no guard), --agents,
  --plugin-dir and --system-prompt reach the CLI. They are on W2-56's refusal list.

## Probed and found sound

- The line: the launcher's switches come first (--setting-sources project,local, --strict-mcp-config, the role's
  --model and --effort, a fresh --session-id, --append-system-prompt-file, and --fork-session only on a resume); the
  caller's arguments follow, unchanged and in order.
- Model:
  - Refused, naming both: --model opus, another model, and claude-opus-5-5[1m].
  - The repository's model key, env ANTHROPIC_MODEL, env CLAUDE_CODE_SUBAGENT_MODEL, effortLevel and
    modelSettings.<model>.effortLevel all launch with the role's --model and --effort on the line. The settings' env
    and the process environment carry the role's subagent model, also when the caller's environment names another.
    Their precedence over the project settings follows the CLI's documented order (not measured live).
  - The project's agents carry no model line.
- Compaction: --autocompact with any value (including auto) is refused. env CLAUDE_CODE_AUTO_COMPACT_WINDOW and a
  top-level autoCompactWindow are refused, committed or local. The launcher's line and settings carry none, and the
  record says none.
- Memory and connectors: autoMemoryEnabled false is in --settings, also when the repository sets true (precedence,
  not measured live). .mcp.json with enableAllProjectMcpServers is launched under --strict-mcp-config (w1).
- Resume:
  - Refused: --resume without a UUID, an upper-case UUID, -r<id>, -pr, --continue, -c, -pc, -dc, --fork-session and
    --session-id.
  - A resume with no record (a session started before this change) is refused with a clear message. No record is
    left and no work is lost; resumes stay fresh sessions from the checkpoint until W2-21 (prompt, line 77).
  - A resume after the role file changed records the original's role text (f2).
- The record:
  - Written before the start; created exclusively.
  - A read-only folder refuses the launch and leaves no temp folder; a role refusal leaves none either.
  - Two literal deny rules name the folder; the record file is mode 0644.
  - It sits in the main checkout's .gov-runtime/launches/. For a worktree session that is outside every write path:
    the working folder, the temp folder, the own run folder and the common .git.
- Today's refusals still refuse:
  - test_w2_60a_refused_arguments.py, 49 passed: DEC-313, DEC-218, DEC-233, the settings checks, --bare,
    --setting-sources, the guard wiring, the role and ticket checks, DEC-205, DEC-242.
  - test_w2_58_fails_closed.py, 6 passed: DEC-873 and DEC-820.
  - DEC-315's Edit rules are present for .tickets, .claude and tests/acceptance.
  - DEC-392 and DEC-386: SIGTERM, SIGINT and SIGHUP each give exit 130, end the session and remove the temp folder,
    with nothing on stderr.
- Scope:
  - The engineer's commits stay inside the ticket's allowed paths.
  - The earlier acceptance tests changed only in independent-test-designer commits with Rewrite-Reason. They swap
    --model haiku for the role's model or a fixture default line and remove no assertion.
  - The sandbox's write list is unchanged; deny rules are only added.
- The real role files have no version or default line at this head, so every real launch is refused at the role
  read until W2-11 (fail closed, as the ticket holds the merge). No tracked skill file is a link.
- Unit tests: test_role.py 21 passed; test_launch_record.py 9 passed.
