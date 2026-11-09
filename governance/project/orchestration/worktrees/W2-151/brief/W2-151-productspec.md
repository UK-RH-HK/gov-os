Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-151/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-151 — the product-spec brief: MR-1 to MR-6 regenerated from contract.yaml (DAEO-qzca)

You are a product-spec worker for **W2-151** (`.tickets/DAEO-qzca.md`: read it whole). It is a record regeneration,
LITE.

`02ee7e33` (DEC-623) generated `docs/contract/master-rules/MR-1.md` to `MR-6.md` from `docs/contract/contract.yaml` so
the ids resolve. The records still say `status: PROPOSED` and "Contract v4, version 4.1". `contract.yaml` says
`status: ACCEPTED`, version `4.2`. `gov links --all` reports six STATUS_CONFLICTs, owner product-spec.

## What to do
1. Read `docs/contract/contract.yaml`: its top-level `id`, `status` and `version`, and each `MR-n` entry's `title`,
   `text_source` and `acceptance`. Read the six records, and `git show 02ee7e33` for their generated form.
2. Regenerate each record in the same form. Write a one-off script in your worktree's `.gov-runtime/scratch/` (never
   committed) if that helps, and say so.
   - Front matter: `id`, `type: specification`, `status: <the Contract's status>`, `state_class: DERIVED`,
     `title: <the entry's title>`, `depends_on: [CONTRACT-v4]`.
   - Body: the heading, the "Generated from `docs/contract/contract.yaml` (Contract v4, version <version>)" sentence,
     and the **Text** and **Acceptance** lines from the entry.
   - Keep each record's wording where the contract file has not changed.
3. Add `docs/changes/W2-151-evidence.md`: what changed per record (status, version, any text), and `gov links --all`'s
   STATUS_CONFLICT count before and after (6 → 0). Run it with
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-151/src python3 -m gov.cli.main links --all`.

## Where you work
- `/home/usain/gov-os-worktrees/W2-151`, branch `w2/W2-151`, from `w2/integrate`.
- Your paths: `docs/contract/master-rules/MR-*.md` and `docs/changes/W2-151-evidence.md`. **Never touch
  `contract.yaml` or `CONTRACT_v4.md`:** W2-139 holds them.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, network or installs.
- **DEC-1080:** use the Read and Grep tools, one simple command per Bash call, and no `cd … &&` chains.
- Do not merge `w2/integrate`. Never touch `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-151` with
  `--trailer "Task: DAEO-qzca" --trailer "Implements: DEC-1074, DEC-1109" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
- The twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first).
- The commit, and each record's change in one line.
- `gov links`' counts before and after.
- Anything in `contract.yaml` that looked inconsistent, as `discoveries`.
