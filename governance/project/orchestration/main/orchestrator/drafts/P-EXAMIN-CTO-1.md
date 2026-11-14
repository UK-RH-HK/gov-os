# P-EXAMIN-CTO-1: a separate EXAMIN CTO runs EXAMIN's adoption and Wave 0 using only the product

**(1) Context.** You decided: no plan change. The Gov OS CTO finishes the two tickets EXAMIN's adoption waits on.
EXAMIN's adoption and the rest of its Wave 0 are run by a separate EXAMIN CTO: a session in the copy, using only the
product, never this repository's scratch tools. The Gov OS CTO keeps W2-27 to W2-30 and W2-94 as records and measures
their KPIs from the EXAMIN CTO's reports.

**(2) The two tickets, confirmed.**
- W2-27's start under DEC-1167 needs W2-88 and W2-60a merged, and only those two.
  - W2-88 is landing now (df9f4910e00e).
  - W2-60a is DONE at a7aa762ab890; it lands after your P-9 commit.
- Already met: W2-42a merged today, and W2-116, W2-145 and W2-61h are merged (merged dependencies count as met,
  DEC-1157).
- Cut from the start by DEC-1167: W2-60b, W2-156, W2-93, W2-94 and W2-174. W2-27's stale dependency list is fixed
  right after W2-88's land.
- **One more step before the EXAMIN CTO starts, from W2-27's own KPI lines:** "The first numbered, frozen release is
  cut by the owner and hash-checked", and "W2-16's numbered, frozen release is the one installed, never this
  repository's branch".
  - The live pin (pin-797495bdfc70, 11-11) predates W2-88 and W2-60a, and no Wave 2 release tag exists yet.
  - So once both have merged: I prepare the release with the release skill (W2-102: freeze, version, changelog,
    provenance note, the tag request to you). You cut and tag it. Your operator installs it as the pin (the re-pin
    ladder, P-REPIN-2).
  - About half a day after the second merge.

**(3) How the EXAMIN CTO is started, and from where.**
- **The folder:** your operator clones the workbench copy (clean at 0a82082) into
  `/home/usain/gov-os-runs/W2-27/examin`. Agents never read the workbench (DEC-723).
- **The session:** your operator starts it in tmux, with no add-dir and no access to this repository's tools:
  ```
  tmux new -d -s examin-cto "cd /home/usain/gov-os-runs/W2-27/examin && ~/.local/bin/claude --remote-control 'EXAMIN CTO' --settings '{\"env\":{\"GOV_ROLE\":\"orchestrator\"}}'"
  ```
  - It uses `~/.local/bin/gov`, the pinned release.
  - After adoption, the kernel's CTO role, templates and guard live in the clone's own `.claude/`, and its own
    coordination ticket gives its `GOV_TICKET` (W2-113: the adopt step names the CTO).
- **Its first message:** a fixed brief, approved by you, as with the walled writers' briefs. It covers:
  - the order (W2-27's KPI lines, then W2-28's handoff);
  - the product commands only: `gov adopt` (A0 to A11), `gov doctor`, `gov brief`, `gov launch`, `gov plan`,
    `gov close`, `gov retrieve`, `gov context`, and the adopt skill;
  - the findings channel;
  - the may-write list;
  - "stop and write a finding; never work around the product".

**(4) Which tickets it runs.**
- **W2-27**, adoption on the copy:
  - install the release and check its hash;
  - `gov adopt` A0 to A11;
  - W2-88's tools at adoption: the assessment, the refactoring plan as proposals, the full index and embeddings;
  - `gov doctor` green;
  - one LITE ticket through the whole cycle (test designer, red, implement, green, `gov close` at exit 0 with EXAMIN's
    own test command);
  - EXAMIN's red tests named with their causes.
- **Then EXAMIN's own Wave 0 work:** the refactoring proposals as EXAMIN's tickets, and the memory preparation.
- **Not run by the EXAMIN CTO:**
  - **W2-28 and W2-30, the verdicts:** a fresh independent auditor that wrote none of the adoption. I launch it from
    here through the launch script (W2-149), reading the clone.
  - **W2-94's memory measure:** the hidden half stays walled. Your operator runs the hidden-form measure, as with
    W2-61h.
  - **W2-29, the real repository:** only after W2-28's healthy verdict, W2-15b's results and your go (DEC-727). It is
    run the same way, on an adoption branch you merge.

**(5) The findings channel.**
- **The EXAMIN CTO writes one fixed file:** `/home/usain/gov-os-runs/W2-27/FINDINGS.md`. It only appends. Each
  finding is one block:
  `F-NNN | time | stage (A0..A11, the LITE ticket, a command) | what failed | the exact command | exit code | expected
  / observed | evidence path (under /home/usain/gov-os-runs/W2-27/evidence/) | its guess: product or EXAMIN`.
- **It also writes stage reports** to `/home/usain/gov-os-runs/W2-27/reports/` (one per adoption stage, plus the
  LITE ticket's close record). I measure W2-27's KPI lines from these.
- **My side:**
  - A watcher (a 20-line script, mine) turns each new finding into an inbox item within a minute.
  - I triage each finding within the hour:
    - **(i) a defect inside a closed ticket's scope:** my P2 fix under DEC-1164 (18), with a narrow independent
      check, landed;
    - **(ii) new scope:** a package to you, because new tickets are yours (DEC-974);
    - **(iii) EXAMIN's own problem:** back to the EXAMIN CTO as one of its tickets.
- **Fixes reach EXAMIN as a re-pin:** batched, through the re-pin ladder, applied by your operator.
- **I answer in one file of mine:** `/home/usain/gov-os-runs/W2-00/examin-replies.md`, which the EXAMIN CTO reads
  before each stage. It holds a line per finding (fixed in pin X / new ticket, waiting on you / yours to fix). The
  EXAMIN CTO restarts on a new pin when told.

**(6) What it may and may not write.**
- **May write:**
  - the clone `/home/usain/gov-os-runs/W2-27/examin/**`, as the product's guard allows its roles after adoption;
  - `/home/usain/gov-os-runs/W2-27/**` (findings, reports, evidence, scratch).
- **May not write:**
  - this repository, or any of its worktrees or scratch tools;
  - `~/gov-os-workbench` (DEC-723);
  - the operator's folders, the real EXAMIN repository, `~/.claude`, `~/.local`, the machine's services;
  - push or tag anything.
- **May not read:** the evaluation sets root `/home/usain/gov-os-eval`, in particular W2-94's hidden half (it is
  measured).
  - **A precondition I check before it starts:** after A0, the clone's guard must refuse a read of the sets root.
  - If the product cannot declare that held-out root in an adopted project's path map, that is the first finding,
    and the session does not start until it is fixed (W2-84's guard rule in the product).

**(7) Its cost.**
- **Session cost:** the EXAMIN CTO is one Opus session over about 3 working days, plus its workers: one test designer
  and one engineer for the LITE ticket, and a few short sessions for the assessment. Today's lead runs cost $3.7 to
  $8.9 each at list price (lead session only).
- **My estimate:** $40 to $80 a day for the EXAMIN CTO and its workers, so $150 to $300 for W2-27. The auditor's
  verdict (W2-28) adds about $10.
- **Indexing and embeddings:** these run on the machine (GPU and CPU), not the API, but they take heavy slots for a
  few hours.
- **On my side:** about an hour a day of triage, plus the fixes the findings call for.

**(8) What I need from you.**
- `yes P-EXAMIN-CTO-1`: the setup as above, recorded as a decision (it changes who runs W2-27 to W2-30's work, not the
  plan).
- After W2-88 and W2-60a merge: the release cut and tag, and your operator's re-pin.
- **Your operator:**
  - makes the clone;
  - starts the `examin-cto` session;
  - later runs W2-94's hidden-form measure.
- **Your approval of the EXAMIN CTO's fixed first brief.** I bring it with the release.

**(9) Recommendation:** yes. It tests the product as a customer would. Every gap becomes a finding with its evidence,
rather than a fix made quietly with this repository's tools.

Your line: `yes P-EXAMIN-CTO-1` (or name changes).
