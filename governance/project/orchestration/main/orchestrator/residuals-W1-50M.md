
## W1-50 closing follow-up residuals (the freeze mirror and the ticket lead's role, 2026-10-06)

- **The mirror** is the file `freeze` in a folder under `~/.local/state/gov-os/` named by the SHA-256, in hex, of
  the real path of the repository's git common directory (DEC-437). The main tree and every worktree share one
  entry. A moved repository has a new key: its old mirror no longer freezes it, and the in-repository flag
  alone does.
- **The mirror's place follows the home directory the process sees.** A session that starts a child with
  another home makes that child's guard read another mirror. The orchestrator's own unsandboxed session can do
  that; it is inside the residual the owner accepted (DEC-429: an opaque write by that session).
- **A launched worker's sandbox gives it a redirected home,** so it cannot reach the real mirror; its guard
  therefore reads the in-repository flag only. A worker cannot write under `.gov-runtime/` outside its scratch,
  and the containment check around the caller's Bash calls restores a removed flag from the mirror.
- **An empty or unmarked mirror file means frozen;** a lift that cannot remove the mirror refuses and changes
  nothing (DEC-437; the owner may overturn).
- **The role `ticket-lead` exists in the guard** with no allowed paths; it writes its scratch through the
  existing scratch rule. It is not a worker role: `gov launch` does not start it. **No lead runs under it yet:**
  the lead start line in the orchestrator prompt is the owner's to change (`"GOV_ROLE":"ticket-lead"` in place
  of `"GOV_ROLE":"orchestrator"` in the `--settings` of appendix A5). Until then leads keep the orchestrator's
  write rights (DEC-156), and the four rules at the top of the leads' common brief are the only bar.
- **Tests and the real mirror.** In the second start, unit tests wrote six entries into the real
  `~/.local/state/gov-os/` (keys of temporary projects, none of this repository; nothing was frozen). They are
  the owner's to remove. Since then every test that runs the pause command or the guard uses a throwaway home,
  and a tripwire fails the test session if the real folder's listing or modification time changes
  (`tests/acceptance/conftest.py` and the conftest files of `tests/unit/pause`, `guard` and `containment`); it
  finds the real folder from the password database, so a changed `HOME` does not blind it. A new suite that
  runs `gov pause` without a throwaway home is caught by it, not prevented.
- **Cases of other tickets revised for the mirror** (reason "owner decision DEC-429"): W1-07's read-act
  snapshot cases and W1-28's freeze cases; one W1-50 freeze-marker case.
- **The engineer's commit `9f294a9e` carries no `Role:` trailer;** the second start's lead wrote a unit test
  itself, which was removed from the branch and redone by an engineer. The merge `94bb68d7` was flagged once by
  the containment check for the aligned W1-07 support file: a record.
- **The owner's manual check of freeze, pause and lift from a plain terminal** is run at the wave's exit
  (W1-42, DEC-428), now including: after `gov pause`, both the flag and the mirror exist; removing the flag by
  hand leaves the project frozen and the next Bash call of a session restores it with a finding; the lift
  removes both.
- **Learning metrics of the follow-up:** 6 packages (all decided by the orchestrator, DEC-437); 0 KPI disputes;
  5 cases of earlier suites revised after implementation began, each for the mirror; source 159 lines against
  an estimate of 150; three starts (one ended on a running reviewer, one for the packages).
- **Regression at `5d830d3e`:** every suite green (W1-50 642 passed), no latency occurrence; the real mirror
  folder unchanged by it.
