
## W1-26 follow-up residuals (the generic validators and "not applicable until the first audit", 2026-10-07)

- **Why the ticket was reopened:** W1-35's and W1-36's check declarations ran `true` as their command, because
  the validators their KPIs name ("the generic validator from W1-26") did not exist. The orchestrator had
  closed W1-26 without them: its own error, corrected by DEC-439.
- **Built:** `python3 -m gov.check.skill_validator (folders or files)` finds every `SKILL.md` at any depth and
  checks the frontmatter, the version, the description and body sizes (with W1-24's token count) and that
  every `gov` command the file names exists. `python3 -m gov.check.audit_validator (files or folders)` checks a
  report against DEC-441's form: the frontmatter `milestone`, `commit` (a full commit id that exists),
  `pack_sha256`; the table `item | class | evidence`; the six classes of DEC-070; an `OK` row cites at least
  one path, and every cited path exists at the cited commit. Both: any finding exits 1; nothing validated or
  an unreadable file is "unmeasured" and exits 1 (DEC-425).
- **"Not applicable until the first audit" (DEC-447):** a declaration that carries
  `allows-not-applicable: "true"`, whose command exits 2 and prints `{"not_applicable": true, "reason": …}`,
  is YELLOW with that reason. All three are needed; without the field, exit 2 is an ordinary failure. The
  audit validator answers so only when a folder it was given is missing or holds no report; with one report it
  is a hard block again.
- **The opt-in field is read only from a declaration file named `(check id).yaml`.** A declaration whose file
  name differs from its id cannot opt in (it stays red: the safe side).
- **The audit validator does not check the value of `milestone`** (any text passes), nor that `pack_sha256` is
  the hash of an existing pack beyond its form. For the exit audit (W1-43) to read by hand.
- **The skill validator checks `gov` commands against the reserved-command list,** not against what is
  installed on the machine.
- **Declared commands name paths under `template/…`,** which an installed project does not have: for the
  adoption tickets (W1-39, W1-41).
- **Learning metrics:** two lead starts (the first built the skill validator only, with a folder search one
  level deep that found nothing with the given command line), then two designer-and-engineer pairs started by
  the orchestrator (four gaps in the audit validator found by reading DEC-441 against the code; DEC-447); 0
  reviewer rounds (the ticket's two were spent); 450 lines in the two validators plus about 50 in the runner,
  against an estimate of 120; 238 cases in W1-26's suite.
- **Regression at `54b8a404`** (machine load 48): green except the load-sensitive cases of DEC-372 (W1-02,
  W1-05, W1-46), which passed alone, save one W1-05 case in one alone run that was not identified.
  **Regression at `b706e688`:** every suite green, no latency occurrence (W1-05: 99 passed).

**Correction to "W1-29 residuals" above (DEC-451):** the line "The auto-compact threshold (DEC-208) is not set"
is wrong. The project's settings set the environment variable `CLAUDE_CODE_AUTO_COMPACT_WINDOW` to `300000`
since W1-49's merge; the Claude Code documentation names that variable as the setting, and there is no
settings key `autocompact`. The orchestrator's CONTEXT_CHECKPOINT stop is dropped. The other owner items of
that block are answered by DEC-442 (Stop and SubagentStop are registered at the Wave 1 exit run), DEC-444
(the hooks' automatic checkpoints go to `.gov-runtime/scratch/checkpoints/`: W1-29 follow-up) and DEC-445 (the
utilisation-triggered checkpoint is an accepted residual).
