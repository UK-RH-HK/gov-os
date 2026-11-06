import pathlib
R = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
p = R / "docs/DECISION_REGISTER.md"; s = p.read_text()
entry = '''### DEC-1080 — P-PERMISSIONS-1 approved with read-only git through `git -C` only; the CTO's command rule (Read and Grep tools, one simple command per call, a line before any prompting command) standing, and in every agent's brief
- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`; standing) · **Under:** DEC-1058 (P-ACT-SPLIT), DEC-1057, DEC-1052 · **Source:** `governance/project/orchestration/packages/P-PERMISSIONS-1.md`
- **Decision:**
  - **(1) The CTO's own rule, now and from here on:** reading with the Read and Grep tools; one simple command per
    call; no `cd … &&` chains; before any command that will prompt the owner, one line saying what it does and why.
    The same rule goes into the brief of every agent the CTO starts in its session (`briefs/EMG-common.md`).
  - **(2) P-PERMISSIONS-1 approved, with one correction:** only read-only git through `git -C` (`log`, `show`,
    `diff`, `status`, `rev-parse`, `branch --list`, `ls-files`, `merge-base`); every other git command keeps asking,
    and `git push` stays denied. The rest as proposed: the read-only commands, `~/.local/bin/gov`, and `cd` into the
    repository and the worktrees allowed; `rm`, `mv`, `cp` and `mkdir` outside the repository, writes to
    `~/gov-os-eval`, `~/.local`, `~/.cache`, `~/.config` and `~/.ollama`, GPU and job launches, `curl` and web access
    keep asking. The settings change is the operator's ACT, rehearsed end to end (`ACT-PERMISSIONS-1.md`).
  - **(3)** The work resumes as decided.
- **Basis:** question 4 (the owner's time spent only on prompts that carry a decision) and question 2 (every write
  outside the repository, deletion, job and network call still asks).

'''
i = s.rindex("| Version | Date | Change |")
s = s[:i] + entry + s[i:]
s = s.rstrip("\n") + "\n| 0.464 | 2026-11-06 | Owner (recorded by the orchestrator, DEC-861): DEC-1080. Next free id: DEC-1081. |\n"
p.write_text(s)
f = R / "governance/project/orchestration/DECISIONS-IN-FORCE.md"
f.write_text(f.read_text() + '''- DEC-1080 (2026-11-06, standing): the CTO reads with the Read and Grep tools, runs one simple command per call, no
  `cd … &&` chains, and says in one line before any command that will prompt what it does and why; the same rule in
  every agent's brief. P-PERMISSIONS-1 approved with read-only git through `git -C` only; the settings change is the
  operator's ACT (`ACT-PERMISSIONS-1.md`). Basis: questions 4 and 2.
''')
print("DEC-1080 recorded")
