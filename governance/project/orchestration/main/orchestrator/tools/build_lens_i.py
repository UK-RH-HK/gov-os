"""Build lens I's four area briefs (DEC-889 item 16): the head, the area, the tail with AUDITOR-common's body."""
from pathlib import Path

B = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs")
COMMON = Path("/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/briefs/AUDITOR-common.md").read_text()
auditor_common = COMMON[COMMON.index("## Standing rules for your session"):].rstrip("\n")

AREAS = {
    "1": ("The guard, the launcher and the sandbox", "guard-launcher-sandbox",
          "- **Acceptance suites:** W1-01 (the interim guardrails), W1-02 (the PreToolUse guard), W1-03 (containment), "
          "W1-04 (the install-approval rule), W1-05 (the dogfood switch-over and its live hooks), W1-28 (`gov pause`), "
          "W1-45 (the orchestrator's write scope), W1-46 (`gov launch`), W1-47 (guard hardening), W1-50 (containment by "
          "commit trailers), W2-50 (the durable scratch root), W2-58 (Policy 2: reads open, four refusals).\n"
          "- **Builder tests:** `tests/unit/guard/`, `tests/unit/containment/`, `tests/unit/launch/`, `tests/unit/pause/`, "
          "`tests/unit/install/`, `tests/unit/hooks/`.\n"
          "- **Decisions that changed this area since Wave 1** include DEC-508 and DEC-820 (the read rules: Policy 2 "
          "replaced the listing refusals), DEC-821 and DEC-873 (the sandbox clause re-baselined), DEC-857, DEC-880 item "
          "1 (`~` paths), DEC-728 and DEC-750 (the scratch root), DEC-799 (`gov launch` for workers), DEC-838 (no "
          "compaction threshold). Search the register for more."),
    "2": ("`gov close`, the checks and the ratchet", "close-checks-ratchet",
          "- **Acceptance suites:** W1-26 (`gov check` G0 to G2), W1-30 (`gov close`), W1-31 (the governance share), "
          "W1-40 (lefthook and CI), W1-42 (the Wave 1 exit run: its two accepted reds), W1-15 (the secret rules and the "
          "pre-index filter; the secrets-indexing check), W1-48 (the Claude Code version pin), W2-01 (the close's "
          "traceability), W2-53 (the probe gate, the ratchet's lists).\n"
          "- **Builder tests:** `tests/unit/close/`, `tests/unit/check/`, `tests/unit/secrets/`, `tests/unit/ci/`, "
          "`tests/unit/telemetry/`, `tests/unit/validate/`.\n"
          "- **Decisions that changed this area since Wave 1** include DEC-726, DEC-843, DEC-852, DEC-876 and DEC-880 "
          "(the cache, then its withdrawal), DEC-757, DEC-762, DEC-766 and DEC-871 (the ratchet's lists), DEC-780 and "
          "DEC-868 (the pre-close gate), DEC-883 to DEC-886 and DEC-889 (batched closes, the record-reading set), "
          "DEC-822 and DEC-835 (the pinned judge). Search the register for more."),
    "3": ("Retrieval, context, checkpoints and resume", "retrieval-context-resume",
          "- **Acceptance suites:** W1-10 (the store and record graph), W1-16 (the codebase-memory wrapper), W1-17 "
          "(the lexical index), W1-18 (Ollama's lifecycle), W1-19 (semantic retrieval), W1-20 (`gov closure`), W1-21 "
          "(`gov retrieve`), W1-22 (the evidence validator and canaries), W1-23 (synthesis notes), W1-24 (`gov "
          "context`), W1-25 (`gov checkpoint`), W1-29 (the session hooks), W1-49 (the auto-resume hooks), W2-54 (the "
          "context packet's order and time limit, the audit-report type), W2-62 (resume in full).\n"
          "- **Builder tests:** `tests/unit/retrieval/`, `tests/unit/retrieve/`, `tests/unit/semantic/`, "
          "`tests/unit/store/`, `tests/unit/context/`, `tests/unit/checkpoint/`, `tests/unit/codeintel/`, "
          "`tests/unit/ollama/`, `tests/unit/synthesis/`, `tests/unit/closure/`, `tests/unit/rebuild/`.\n"
          "- **Decisions that changed this area since Wave 1** include DEC-636 and DEC-838 (the context window), "
          "DEC-792 and DEC-837 (resume in full), DEC-856 and DEC-887 (the orchestration record out of the index and of "
          "the tree), DEC-859 and DEC-860 (code-graph traversal, stacked batches), DEC-836 (memory used). Search the "
          "register for more."),
    "4": ("Records, the plan, tickets and the remaining suites", "records-plan-rest",
          "- **Acceptance suites:** W1-06 (the tool prerequisites and approvals), W1-07 (the CLI skeleton and its "
          "envelope), W1-08 (the record schemas and the path map), W1-09 (tickets, claims and the READY rule), W1-11 "
          "(the decision checker), W1-12 (the readiness schema), W1-13 (`gov readiness`), W1-14 (the proposal-to-ticket "
          "bridge), W1-27 (`gov doctor` and `gov rebuild`), W1-32 (`gov status`), W1-33 (the role definitions), W1-34 "
          "(the decision-package template), W1-35 and W1-36 (the skills), W1-37 (the vendored skill packs), W1-38 (the "
          "rulesync adapters), W1-39 (the copier template), W1-41 (`gov adopt --lite`), W1-44 (lessons), W2-02 (the "
          "record types).\n"
          "- **Builder tests:** `tests/unit/records/`, `tests/unit/tasks/`, `tests/unit/decisions/`, "
          "`tests/unit/readiness/`, `tests/unit/bridge/`, `tests/unit/doctor/`, `tests/unit/status/`, `tests/unit/cli/`, "
          "`tests/unit/adopt/`, `tests/unit/adapters/`, `tests/unit/lock/`.\n"
          "- **Decisions that changed this area since Wave 1** include DEC-441, DEC-872 and DEC-874 (the record types), "
          "DEC-819 and DEC-887 (the orchestration record's place: suites that copy or walk the tree), DEC-866 (the "
          "supersession sweep), DEC-861 and DEC-862 (the owner's records), DEC-882 and DEC-885 (the record-made reds). "
          "Search the register for more."),
}

head = (B / "assessment-I-head.md").read_text()
tail = (B / "assessment-I-tail.md").read_text()
for n, (title, slug, scope) in AREAS.items():
    text = (head + tail).replace("{AREA_N}", n).replace("{AREA_TITLE}", title).replace("{AREA_SLUG}", slug)
    text = text.replace("{AREA_SCOPE}", scope).replace("{AUDITOR_COMMON}", auditor_common)
    text = text.replace("head `{HEAD}`", "at the head `git log -1` shows when you start")
    assert "{" not in "".join(ch for ch in text if ch == "{") or "{AREA" not in text, n
    out = B / f"assessment-I{n}.md"
    out.write_text(text)
    print(out.name, len(text))
