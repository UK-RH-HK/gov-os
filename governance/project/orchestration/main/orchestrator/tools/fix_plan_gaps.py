"""PLAN-GROWTH-1 §2's seven gap fixes (the orchestrator's delegated P2s, DEC-936 item 2.5). One commit per ticket."""
import json
import re
import subprocess
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
from te_lib import ROOT, ORCH, T, commit  # noqa: E402

ACC = "tests/" + "acceptance"
DONE = []

# 1. W2-90b
mp = ORCH / "log/tickets-2026-10-31d.json"
if mp.exists():
    t90b = json.loads(mp.read_text())["W2-90b"]
else:
    title = ("W2-90's next round: the cases still tied to this repository's live wiring move to the kernel's wiring "
             "now that the template's install block is removed and its hook lines pinned (W2-105, W2-106)")
    out = subprocess.run(["tk", "create", title, "-p", "1", "--external-ref", "W2-90b"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip().split()[-1]
    t90b = out
    p = ROOT / ".tickets" / (t90b + ".md")
    created = re.search(r"^created: (\S+)$", p.read_text(), re.M).group(1)
    paths = [f"{ACC}/W1-05/test_w1_05_live_hooks.py", f"{ACC}/W1-05/conftest.py",
             f"{ACC}/W1-46/test_w1_46_research_installs.py", f"{ACC}/W1-46/test_w1_46_live_sessions.py",
             f"{ACC}/W1-46/conftest.py",
             f"{ACC}/W2-59/test_w2_59_hook_lines.py", f"{ACC}/W2-59/test_w2_59_hook_lines_worker_env.py",
             f"{ACC}/W2-65/test_w2_65_hook_lines.py",
             f"{ACC}/W1-33/test_w1_33_guard_and_launcher.py", f"{ACC}/W1-33/w1_33_support.py",
             f"{ACC}/W1-47/w1_47_support.py",
             f"{ACC}/W1-50/test_w1_50_freeze_launcher.py",
             f"{ACC}/W2-54/test_w2_54_sandboxed_worker.py", f"{ACC}/W2-54/w2_54_support.py",
             f"{ACC}/W2-90/w2_90_kernel_wiring.py", f"{ACC}/W2-90/README.md", f"{ACC}/W2-90b/**"]
    q = lambda s: "'" + s.replace("'", "''") + "'"
    fm = ["---", f"id: {t90b}", "status: open", "deps: [DAEO-zpdj, DAEO-0mtg]", "links: []", f"created: {created}",
          "type: task", "priority: 1", "assignee: independent-test-designer", "external-ref: W2-90b",
          "tags: [wave-2, test-revision, guard, lite]", "wbs_id: W2-90b", "title: " + q(title), "class: test-revision",
          "state_class: AUTHORITATIVE", "role: independent-test-designer", "depends_on:", "- DAEO-zpdj", "- DAEO-0mtg",
          "allowed_paths:"] + [f"- {x}" for x in paths] + [
          "kpis:", "  success:",
          "  - " + q("W2-90's seven named reds (W1-05's two orchestrator-asks cases, W1-46's research npm-install case, "
                     "four W2-59 cases) judge the kernel's wiring and pass on the head with W2-105 and W2-106 merged "
                     "[DEC-965 item 1, DEC-966]"),
          "  - " + q("The 14 parametrized ids ACT 1 removed without a red (W2-59's 10 post-tool ids, W2-65's 4) and "
                     "W2-59's empty-parameter skip are back, on the template's post-tool lines [DEC-965 item 4]"),
          "  - " + q("W1-33's four guard-and-launcher cases and W1-05's two setup errors (their fixture repositories "
                     "lack the five-rule hook file since ACT 1) judge the kernel's wiring and pass; W2-54's "
                     "sandboxed-worker case's cause is confirmed and, if it is the same, fixed the same way "
                     "[DEC-970, DEC-953 item 2]"),
          "  - " + q("The stand-in homes of the harnesses (W1-47's installed environment, W1-46's live sessions, "
                     "W1-50's freeze launcher) use the editable install's gov, so with the hook lines pinned they "
                     "judge the worktree's code, not the installed copy [DEC-970, W2-106's P2]"),
          "  - " + q("Nothing is lowered: no case deleted, skipped, xfailed or weakened; every revised file's commit "
                     "carries Rewrite-Reason: DEC-953 item 2; a README under the ticket's folder maps every case "
                     "[DEC-906, MR-3]"),
          "  failure:",
          "  - " + q("A revised case still reads this repository's live settings, or is red with W2-105 and W2-106 "
                     "merged."),
          "  - " + q("A case deleted, skipped, xfailed or its verdict weakened."),
          "profile: LITE", "sources:", "- DEC-965", "- DEC-970", "- DEC-966", "- DEC-953", "- DEC-906", "est_loc: 300",
          "acceptance_tests:", f"  path: {ACC}/W2-90b/",
          "  author: independent-test-designer (MR-3); a test-revision ticket judged on its revised suites (DEC-892)",
          "track: A", "list_rows: []", "---"]
    body = ("# W2-90b W2-90's next round\n\n"
            "Card: DEC-965 item 4 and DEC-970, filed by PLAN-GROWTH-1 §2 gap 1 (W2-90, `DAEO-8lmb`, is closed). "
            "It starts when W2-105 (the template's install block removed) and W2-106 (its hook lines pinned) have "
            "merged, so the seven cases P1-A and P1-B held can move to the kernel's wiring.\n")
    p.write_text("\n".join(fm) + "\n" + body, encoding="utf-8")
    mp.write_text(json.dumps({"W2-90b": t90b}) + "\n")
    DONE.append((commit(f"W2-90b ({t90b}) filed: W2-90's next round (DEC-965, DEC-970; PLAN-GROWTH-1 gap 1)",
                        [p], [f"Task: {t90b}", "Implements: DEC-965, DEC-970", "Role: orchestrator"]), "W2-90b", "filed"))
    subprocess.run(["tk", "link", t90b, "DAEO-8lmb"], cwd=ROOT, check=True, capture_output=True)
    for tid in (t90b, "DAEO-8lmb"):
        DONE.append((commit(f"{tid}: linked W2-90 and W2-90b", [ROOT / ".tickets" / (tid + ".md")],
                            [f"Task: {tid}", "Implements: DEC-965", "Role: orchestrator"]), tid, "link"))


def edit(tid, w2, adds, body, impl, what):
    t = T(tid)
    cur = t.list_items("deps")
    t.deps(cur + [x for x in adds if x not in cur])
    if body:
        t.body_line(body)
    t.save()
    DONE.append((commit(f"{w2} ({tid}): {what} (PLAN-GROWTH-1 §2)", [t.path],
                        [f"Task: {tid}", f"Implements: {impl}", "Role: orchestrator"]), w2, what))


# 2 and 3: the skill tickets
H, W11 = "DAEO-drhj", "DAEO-k7hz"
for tid, w2 in [("DAEO-wi46", "W2-98"), ("DAEO-lxzn", "W2-99"), ("DAEO-hgv3", "W2-103")]:
    edit(tid, w2, [W11, H], "**Dependencies (PLAN-GROWTH-1 §2 gaps 2 and 3):** after W2-11's round 1 (the skill template) "
         "and W2-104 (the skill harness, which runs its three scenarios before adoption, DEC-959 item 5).",
         "DEC-959", "depends on W2-11 (round 1) and W2-104")
for tid, w2 in [("DAEO-uw5h", "W2-100"), ("DAEO-6icv", "W2-101")]:
    edit(tid, w2, [H], "**Dependencies (PLAN-GROWTH-1 §2 gaps 3 and 4):** after ACT 2, the WBS milestone row (the one "
         "re-pin, DEC-954 item 6), and after W2-104 (the skill harness, DEC-959 item 5).",
         "DEC-959, DEC-954", "depends on W2-104; after ACT 2 (the WBS milestone row)")
edit("DAEO-rpfv", "W2-102", [H], "**Dependencies (PLAN-GROWTH-1 §2 gap 3):** also after W2-104 (the skill harness, "
     "DEC-959 item 5).", "DEC-959", "depends on W2-104")

# 5 and 6: W2-27 and W2-46
t90b = json.loads(mp.read_text())["W2-90b"]
before = ["DAEO-h2k3", "DAEO-jsg1", "DAEO-a3u2", "DAEO-n0wb", "DAEO-6y0x", "DAEO-g87r", "DAEO-57hm", "DAEO-ouet",
          "DAEO-wq2b", "DAEO-wi46", "DAEO-lxzn", "DAEO-uw5h", "DAEO-6icv", "DAEO-rpfv", "DAEO-hgv3", "DAEO-drhj",
          "DAEO-zpdj", "DAEO-0mtg", "DAEO-kiar", "DAEO-zoex", "DAEO-6b2q", "DAEO-3r1j", t90b]
edit("DAEO-h4rh", "W2-27", before, "**Dependencies widened (PLAN-GROWTH-1 §2 gap 5):** the tickets DEC-959, DEC-966, "
     "DEC-969 and DEC-971 put before EXAMIN's copy (W2-61h, W2-86, W2-91 to W2-110, W2-90b).",
     "DEC-959, DEC-966, DEC-971", "depends on the tickets put before EXAMIN's copy")
edit("DAEO-nn1s", "W2-46", before[6:], "**Dependencies widened (PLAN-GROWTH-1 §2 gap 6):** W2-95 to W2-110 and W2-90b.",
     "DEC-959, DEC-966, DEC-971", "depends on W2-95 to W2-110 and W2-90b")

# 7: wbs_id for W2-15a and W2-15b
for tid, w2 in [("DAEO-rd0g", "W2-15a"), ("DAEO-swdu", "W2-15b")]:
    t = T(tid)
    if not any(l.startswith("wbs_id:") for l in t.fm):
        i = t._key("external-ref")
        t.fm.insert(i + 1, f"wbs_id: {w2}")
        t.save()
        DONE.append((commit(f"{w2} ({tid}): its wbs_id line (PLAN-GROWTH-1 §2 gap 7)", [t.path],
                            [f"Task: {tid}", "Implements: DEC-954", "Role: orchestrator"]), w2, "wbs_id"))

for d in DONE:
    print(*d)
