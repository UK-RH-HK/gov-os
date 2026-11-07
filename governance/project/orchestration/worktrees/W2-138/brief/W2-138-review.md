Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-138/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-138 — the independent review (DAEO-rmhj), one round

You are a fresh, read-only independent reviewer. Review **W2-138** (`.tickets/DAEO-rmhj.md`: read it in full, with its
"designer's points settled" and "Built" sections): every search result names the store's commit and folder, the store
is resolved once per search, `CONTINUATION_INVALID` names both commits, each item's sha256 is its lines at that commit,
and the retrieval skill gains the line-hash line (DEC-1090 (3)).

## What to review
- **The branch:** `w2/W2-138` in `/home/usain/gov-os-worktrees/W2-138`, against `w2/integrate` (`git diff w2/integrate...w2/W2-138`):
  - `src/gov/retrieval/retrieve.py`, `src/gov/retrieve/command.py`, `src/gov/cli/main.py` (the `store:` line only);
  - `template/governance/kernel/skills/retrieval/SKILL.md`;
  - the engineer's `tests/unit/retrieval/test_w2_138_store.py`, and the six unit guards changed in `test_w2_131_register_ids.py`, `test_w2_133_gap_label.py` and `test_w2_135_item_cap.py`;
  - the designer's `tests/acceptance/W2-138/`, and W2-133's revised `test_w2_133_unchanged.py` (`Rewrite-Reason: DEC-1090 (3)`);
  - `docs/changes/W2-138-evidence.md`.
- **The CTO's runs:** the scoped regression outside the sandbox: 850 passed, 0 failed. The W2-112 socket cases: 34 passed. The engineer's `gov accept W2-138`: 18/18.

## Check, against each KPI line S1 to S5
- **S1:** the commit is the store's fingerprint `head` (the commit it was built at), in JSON and as the text form's first line. Does the text form's change break any caller that parses plain output?
- **S2:** one folder for every facet, the link resolved once, across a switch.
- **S3:** the token carries its commit. A replay on another store is refused, naming both commits. An old token is refused as "made before W2-138". A token that is not an object no longer crashes.
- **S4:** every item's sha256 is its own lines at that commit. Can an item ever be handed out from a folder whose files differ from what was indexed?
- **S5:** the skill's line says exactly what the ticket says, and the skills check passes.
- **The guard revisions** (the six unit guards, W2-133's acceptance rows): they drop only the token's `s` key and weaken nothing else.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **Write** your record at `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/w2-138.md`, the only file you write. End it with the fenced `verdict` block, `{"kpis": [{"kpi": "S1", ...}, ... "S5", {"kpi": "guards", ...}]}`.
- **Run** nothing that writes. You may run the tests read-only through the heavy slot, and `gov accept W2-138` with a scratch HOME whose `.local` links to `/home/usain/.local`. No GPU, and no `gov retrieve` on the real repository. Use single simple Bash commands (DEC-1080). The hidden-half rule holds.
- **Return** the twelve fields: your verdict per line, and every finding with its two lines.
