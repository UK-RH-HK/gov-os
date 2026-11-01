"""DEC-971 items 2, 3 and 4: files W2-109 (Contract v4.3) and W2-110 (a product's CTO-only install rule), edits W2-05,
W2-08 and W2-105, one commit per ticket file, then the WBS rows in one decision-record commit.
Map: log/tickets-2026-10-31c.json. Safe to re-run. The acceptance folder is spelled as ACC."""
import json
import re
import subprocess
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
from te_lib import ORCH, ROOT, T, commit, q  # noqa: E402

ACC = "tests/" + "acceptance"
MAP = ORCH / "log/tickets-2026-10-31c.json"
ids = json.loads(MAP.read_text()) if MAP.exists() else {}
done = ids.setdefault("_done", [])
TD = ("independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer in its own tests "
      "worktree (DEC-959 item 7, DEC-963)")


def ticket(w2, title, *, prio, profile, role, cls, tags, deps, paths, kpis, fail, sources, est, track, body):
    fm = ["id: ID-PLACEHOLDER", "status: open", f"deps: [{', '.join(deps)}]", "links: []",
          "created: CREATED-PLACEHOLDER", "type: task", f"priority: {prio}", f"assignee: {role}",
          f"external-ref: {w2}", f"tags: [{', '.join(tags)}]", f"wbs_id: {w2}", f"title: {q(title)}",
          f"class: {cls}", "state_class: AUTHORITATIVE", f"role: {role}"]
    fm += ["depends_on: []"] if not deps else ["depends_on:"] + [f"- {d}" for d in deps]
    fm += ["allowed_paths:"] + [f"- {p}" for p in paths]
    fm += ["kpis:", "  success:"] + ["  - " + q(k) for k in kpis] + ["  failure:"] + ["  - " + q(f) for f in fail]
    fm += [f"profile: {profile}", "sources:"] + [f"- {s}" for s in sources]
    fm += [f"est_loc: {est}", "acceptance_tests:", f"  path: {ACC}/{w2}/", f"  author: {TD}",
           f"track: {track}", "list_rows: []"]
    return "---\n" + "\n".join(fm) + "\n---\n" + f"# {w2} {title.split(':')[0]}\n\n" + body.strip() + "\n"


NINE = "CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d, CAP-37.e and CAP-53.b"
NEW = {
    "W2-109": dict(
        title="Contract v4.3: DEC-841's nine items moved to Wave 3 by a CIT-P, CAP-53.b split, and contract.yaml the Contract's authority with its two forms checked to agree",
        prio=1, profile="STANDARD", role="product-spec", cls="specification",
        tags=["wave-2", "specification", "contract", "standard"], deps=[],
        paths=["docs/contract/contract.yaml", "docs/contract/CONTRACT_v4.md", "docs/contract/capabilities/**",
               "docs/contract/SOURCE_MAP.csv", "docs/changes/W2-109-CIT-P.md", "docs/changes/W2-109-CIT-E.md",
               "docs/plan/tools/validate_w2.py", "tests/unit/plan/test_validate_w2_forms*"],
        kpis=[f"A CIT-P addendum moves DEC-841's nine items ({NINE}) from Wave 2 to Wave 3 in both Contract forms, with its independent review, an answer round and the owner's approval before the text changes (CAP-33); the version becomes v4.3 [DEC-971 item 2, DEC-841, CAP-33]",
              "CAP-53.b is split as v4.2 split others: its id keeps the lite Wave 2 part (impact-selected tests at a close), with W2-66 its provider; the Wave 3 rest (a profile computed from impact) gets a new id [DEC-971 item 2, DEC-880]",
              "contract.yaml is the Contract's authority (DEC-971 item 2): CONTRACT_v4.md gains the three providers it lacks (W1-35 for CAP-28 and CAP-28.a, W1-26 for CAP-30.e), and the 276 capability records' authority line names DEC-971 instead of DEC-614 [DEC-971 item 2, DEC-825 item 3]",
              "A contract-forms-agree check in docs/plan/tools/validate_w2.py compares the two forms item by item (ids, waves, providers, status) and fails on any difference, with builder tests; on v4.3 it passes, and the validator's contract-items-delivered and contract-items-cited-by-tests no longer fail on the nine [DEC-971 item 2, DEC-825 item 3]",
              "A CIT-E records what changed and the validator's lines before and after [DEC-971 item 2, CAP-33]"],
        fail=["The Contract's text changed before the CIT-P's review and the owner's approval.",
              "Either form left with one of the nine in Wave 2, or the two forms differing.",
              "CAP-53.b moved whole, or split without W2-66 as the lite part's provider.",
              "A record's authority line still naming DEC-614."],
        sources=["DEC-971", "DEC-841", "DEC-825", "DEC-880", "DEC-741", "DEC-614", "CAP-33"],
        est=300, track="A",
        body="""From the owner's DEC-971 item 2 (P1-MORNING-2026-10-31 item 2, W2-49's P-A (b) and P-B).

- **Why:** DEC-841 moves nine Wave 2 items to Wave 3 "through W2-49's CIT-P", but W2-49's approved CIT-P (DEC-741) predates it. All nine are still `wave: W2` in `contract.yaml`, so the Contract and the plan disagree, and the validator fails `contract-items-delivered` (CAP-22.c) and `contract-items-cited-by-tests` (eight of the nine). W2-49 closed on v4.2 as built and approved.
- **The forms (P-B):** on v4.2 the two forms differ only on three provider lists (CAP-28 and CAP-28.a lack W1-35, CAP-30.e lacks W1-26 in `CONTRACT_v4.md`). All 276 records name `contract.yaml` the authority "by DEC-614", which names none; DEC-971 now does.
- **Paths:** W2-49's Contract files, and W2-51's validator (W2-51 is closed). No running ticket holds them.
- **The work order:** the CIT-P first, then its review and the owner's answer, then the text. The test designer writes the forms-agree and wave tests from these KPIs in parallel.""",
    ),
    "W2-110": dict(
        title="A product's CTO-only install rule: in a generated project the kernel's guard asks the owner only in the CTO's session, the orchestrator on the project's coordination ticket, and refuses every other session",
        prio=1, profile="FULL", role="engineer", cls="implementation",
        tags=["wave-2", "implementation", "guard", "installs", "full"], deps=[],
        paths=["template/governance/kernel/hooks/pretooluse.py", "src/gov/guard/install.py",
               "tests/unit/guard/test_w2_110*"],
        kpis=["In a project generated from the template (copier, then rulesync generate), an install by the orchestrator on the project's coordination ticket is asked of the owner; by any other session, a lead (the orchestrator on another ticket) included, it is refused, and the refusal tells the session to raise it as a P1 escalation, as this repository's guard does after DEC-957 [DEC-971 item 4, DEC-957]",
              "The coordination ticket is named in the project's own configuration (one key, set at adoption), never written in the code; with no such key, or a key naming no ticket, every session's install is refused and the refusal says how to set it (fail closed) [DEC-971 item 4]",
              "Nothing else in the install rule changes: sudo still refused to every role, the research role's one exception inside its experiment folder kept, a frozen project still refusing installs, the owner's record of an approved install unchanged [DEC-971 item 4, DEC-163, DEC-083]",
              "The template's own suites (W1-38, W1-39) and the guard's own suites pass on the change [DEC-971 item 4]"],
        fail=["A lead's or a worker's install in a generated project asked or allowed.",
              "The CTO's install refused when the coordination ticket is set.",
              "A missing or unreadable coordination-ticket key read as \"ask everyone\".",
              "sudo, the research exception or the freeze changed."],
        sources=["DEC-971", "DEC-957", "DEC-966", "DEC-163", "DEC-083"],
        est=80, track="A",
        body="""From the owner's DEC-971 item 4 (P1-MORNING-2026-10-31 item 4, W2-105's P-W2-105-1 (a)).

- **Why:** once W2-105 removes the template's install block, a product's kernel guard asks the owner about every orchestrator's install (`template/governance/kernel/hooks/pretooluse.py`, the install branch: `acting_role(...) == "orchestrator"` asks). Only this repository's five-rule hook has the CTO-only rule (DEC-957). In EXAMIN's copy, a lead's install would ask the owner instead of being refused and escalated.
- **The fix:** the kernel's install branch asks only for the orchestrator on the project's coordination ticket, named in the project's configuration; every other session is refused.
- **Paths, split by file:** the kernel hook's install branch, and `src/gov/guard/install.py` for the helper. W2-05 (running) lists `src/gov/**/*.py` for its git-environment sweep; it does not change the install rule, and whichever merges second merges back. W2-60b holds `src/gov/guard/decide.py`, which is not touched. W2-106 (merged) pinned the template's hook lines.
- **FULL:** it is the guard. An independent review probes for any session other than the CTO's that is asked or let through.""",
    ),
}


def dor(tid):
    r = subprocess.run(["python3", str(ORCH / "tools/dor_hand.py"), tid], capture_output=True, text=True,
                       env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin:/home/usain/.local/bin"})
    return (r.stdout.strip() + " " + r.stderr.strip()[-200:]).strip()


out = []
for w2, spec in NEW.items():
    if w2 in ids:
        out.append(f"{w2} {ids[w2]} already filed")
        continue
    text = ticket(w2, **spec)
    meta = __import__("yaml").safe_load(text.split("\n---\n")[0][4:])
    assert meta["wbs_id"] == w2
    assert not any(p.startswith(ACC) for p in meta["allowed_paths"]), w2
    tid = subprocess.run(["tk", "create", spec["title"], "-p", str(spec["prio"]), "--external-ref", w2], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    path.write_text(text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created), encoding="utf-8")
    T(tid).save()
    ids[w2] = tid
    MAP.write_text(json.dumps(ids) + "\n", encoding="utf-8")
    sha = commit(f"{w2} ({tid}) filed: {spec['title'][:90]} (DEC-971)", [path],
                 [f"Task: {tid}", "Implements: DEC-971", "Role: orchestrator"])
    out.append(f"{w2} {tid} {sha} | {dor(tid)}")

# W2-05: package H's body line (the comparison lives in src/gov/adapters/portability.py, inside src/gov/**/*.py)
if "W2-05" not in done:
    t = T("DAEO-0z8c")
    t.body_line("**DEC-971 item 3 (owner, 2026-10-31), package H (a), refined:** DEC-805's comparison of the template's "
                "hooks source with this repository's (`src/gov/adapters/portability.py`, the adapter-portability check, "
                "inside this ticket's `src/gov/**/*.py`) gets an exception covering **exactly the two hook events ACT 1 "
                "lifted** (`postToolUse` and `postToolUseFailure`), **named in the comparison**, and **ending when those "
                "events return** (with W2-08). A test designer revises the two cases "
                "(`test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources`, "
                "`test_this_repository_s_two_hooks_sources_agree`) to the exception, lowering nothing else. R3-1 is W2-08's "
                "entry criterion (DEC-971 item 3).")
    if "DEC-971" not in t.list_items("sources"):
        t.add("sources", "DEC-971")
    t.save()
    sha = commit("W2-05 (DAEO-0z8c): package H as the owner decided (DEC-805's exception for exactly the two hook events ACT 1 lifted, named, ending with W2-08)",
                 [t.path], ["Task: DAEO-0z8c", "Implements: DEC-971, DEC-805", "Role: orchestrator"])
    done.append("W2-05")
    MAP.write_text(json.dumps(ids) + "\n", encoding="utf-8")
    out.append(f"W2-05 DAEO-0z8c {sha}")

# W2-08: R3-1 as an entry criterion
if "W2-08" not in done:
    t = T("DAEO-7r5e")
    t.kpi_append("Entry criterion (DEC-971 item 3, W2-05's R3-1): before the hooks go back on, a declared check that reads "
                 "what is staged sees the staged content under `git commit -a` and `git commit -- <path>` too (git's own "
                 "index handed to it under a separate name), with a test; until then the hooks are not reinstalled [DEC-971, DEC-803]")
    t.body_line("**DEC-971 item 3 (owner, 2026-10-31):** W2-05's R3-1 is this ticket's entry criterion (a declared check that "
                "reads what is staged sees nothing under `git commit -a`; feature-gated, DEC-803). When the hooks return, "
                "DEC-805's exception for the two lifted hook events ends (W2-05's package H).")
    if "DEC-971" not in t.list_items("sources"):
        t.add("sources", "DEC-971")
    t.save()
    sha = commit("W2-08 (DAEO-7r5e): W2-05's R3-1 as its entry criterion (DEC-971 item 3)", [t.path],
                 ["Task: DAEO-7r5e", "Implements: DEC-971, DEC-803", "Role: orchestrator"])
    done.append("W2-08")
    MAP.write_text(json.dumps(ids) + "\n", encoding="utf-8")
    out.append(f"W2-08 DAEO-7r5e {sha}")

# W2-105: KPI 2 re-baselined
if "W2-105" not in done:
    t = T("DAEO-zpdj")
    t.kpi_replace(1, "In that project, an install reaches the guard's install rule (nothing denies it before the guard is "
                     "asked): the kernel's guard decides it, by its rule as it stands; a product's CTO-only rule (only the "
                     "orchestrator on the project's coordination ticket asked) is W2-110's [DEC-971 item 4, DEC-966 item 1]",
                  "In that project, an install in the CTO")
    if "DEC-971" not in t.list_items("sources"):
        t.add("sources", "DEC-971")
    t.body_line(f"**DEC-971 item 4 (owner, 2026-10-31):** KPI 2 re-baselined to what this ticket tests (an install reaches the "
                f"guard's install rule in a generated project); the product's CTO-only install rule is W2-110 (`{ids['W2-110']}`).")
    t.save()
    sha = commit("W2-105 (DAEO-zpdj): KPI 2 re-baselined to what it tests; the product's CTO-only install rule is W2-110 (DEC-971 item 4)",
                 [t.path], ["Task: DAEO-zpdj", "Implements: DEC-971", "Role: orchestrator"])
    done.append("W2-105")
    MAP.write_text(json.dumps(ids) + "\n", encoding="utf-8")
    out.append(f"W2-105 DAEO-zpdj {sha}")

# WBS rows after W2-108's, in one decision-record commit
wbs = ROOT / "docs/plan/WAVE_2_WBS.md"
lines = wbs.read_text(encoding="utf-8").split("\n")
if not any(l.startswith("| W2-109 |") for l in lines):
    at = max(i for i, l in enumerate(lines) if l.startswith("| W2-108 |"))
    rows = [
        f"| W2-109 | A | **New (DEC-971 item 2).** Contract v4.3: DEC-841's nine items to Wave 3 by a CIT-P, CAP-53.b split, `contract.yaml` the authority, the two forms checked to agree (W2-49's P-A (b), P-B) (`{ids['W2-109']}`) | specification | product-spec | STANDARD | none | 300 | DEC-971, DEC-841, DEC-825, CAP-33 |",
        f"| W2-110 | A | **New (DEC-971 item 4).** A product's CTO-only install rule: the kernel's guard asks only the orchestrator on the project's coordination ticket (W2-105's P-W2-105-1 (a)) (`{ids['W2-110']}`) | implementation | engineer | FULL | none | 80 | DEC-971, DEC-957 |",
    ]
    lines[at + 1:at + 1] = rows
    wbs.write_text("\n".join(lines), encoding="utf-8")
    sha = commit("WBS: rows W2-109 and W2-110 (DEC-971)", [wbs],
                 ["Task: decision-record", "Implements: DEC-971", "Role: orchestrator",
                  "Decided-by: owner (chat, 2026-10-31)"])
    out.append(f"WBS {sha}")
print("\n".join(out))
print(json.dumps(ids))
