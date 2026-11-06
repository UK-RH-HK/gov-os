# W2-61h's engineer: S7, the source families, in the measure's code (DEC-1078 (4), DEC-1079)

You are W2-61h's engineer (`DAEO-h2k3`), launched by `gov launch` under that ticket's id, so the guard keeps you from
the ticket's acceptance tests. The CTO acts as the ticket's lead.

**Read first, whole:** `/home/usain/gov-os-worktrees/W2-61h-s7/.gov-runtime/scratch/brief/EMG-d4b-launched.md` (its "Engineer" paragraph is your job's form), `/home/usain/gov-os-worktrees/W2-61h-s7/.gov-runtime/scratch/brief/EMG-common.md`,
`governance/project/orchestration/INTENT-DEC-1052.md`, and the ticket `.tickets/DAEO-h2k3.md`: KPI line **S7**, the new
failure line, the note "DEC-1079 placed here" and the note **"S7's interface"** (build exactly to it).

**Your worktree:** `/home/usain/gov-os-worktrees/W2-61h-s7` (branch `w2/W2-61h-s7`, today's integrate with the
designer's tests merged). Write only the ticket's `allowed_paths` (`src/gov/retrieval/measure.py`,
`tests/unit/retrieval/test_w2_61h_families*`, `governance/project/path-map.yaml`). Never read `tests/acceptance/W2-61h/`.

**What you build:** in `gov.retrieval.measure`, the families read from the path map's `evaluation_families:`; an
evidence item in another member of the gold source's family counts as a hit on that source only when its text holds
the gold span's text, normalised (whitespace; Markdown and YAML formatting such as `#` heading marks, list marks,
quotes and `key:` prefixes), never by path alone; each family hit named in the question's line; no family declared
means every figure as today; `--kept <dir>` re-scores kept outputs without calling a retriever. Then, in the same
change, declare this repository's families in `governance/project/path-map.yaml` (the Contract's
`docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml`, `docs/contract/capabilities/*.md`,
`docs/contract/master-rules/*.md`; the kernel `template/governance/kernel/**` with its generated `.claude/**` and
`.rulesync/**` copies; `AGENTS.md` with `CLAUDE.md`), with a comment naming DEC-1078 (4).

**Your own unit tests** (stand-ins, `tests/unit/retrieval/test_w2_61h_families*.py`), and the existing measure tests
(`tests/unit/retrieval/` with the exclusions) still green. Evidence file `docs/changes/W2-61h-evidence.md` is not in
your paths: put the S7 row's text in your return instead. **Stop when your unit tests pass**; the CTO then runs
`gov accept W2-61h` outside the sandbox. Runs through the heavy slot as the rules say.

**Commits:** `Task: DAEO-h2k3`, `Implements: DEC-1078, DEC-1079`, `Role: engineer`, `Co-Authored-By: Claude Opus 5.5
<noreply@anthropic.com>`. **Return:** the sandbox and `ps` checks, then the twelve labelled fields. Est.: 2-3 hours.
