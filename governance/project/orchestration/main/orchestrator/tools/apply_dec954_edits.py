"""DEC-954 TICKET-EDITS (drafts/plan-dec954/TICKET-EDITS.md), adjusted for DEC-957: one commit per ticket file, own
Task. Done tickets are listed in log/dec954-edits-done.txt, so a re-run resumes. Prints one line per commit."""
import json
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
from te_lib import ORCH, T, commit  # noqa: E402

NEW = json.loads((ORCH / "log/tickets-2026-10-30d.json").read_text())
W86, W88, W91, W92, W93, W94 = (NEW[k] for k in ("W2-86", "W2-88", "W2-91", "W2-92", "W2-93", "W2-94"))
W90 = "DAEO-8lmb"
DONE = ORCH / "log/dec954-edits-done.txt"
done = set(DONE.read_text().split()) if DONE.exists() else set()
ROLES = ("**Roles spec approved (DEC-957);** builds to ROLES-SPEC-1 as approved, with the work order and the escalation "
         "rubric. Its CIT-P is part of the one combined K3 CIT-P (DEC-954 Q7).")
log = []


def run(w2, tid, fn, impl="DEC-954", what=""):
    if tid in done:
        return
    t = T(tid)
    fn(t)
    t.save()
    sha = commit(f"{w2} ({tid}): {what} (DEC-954{', DEC-957' if 'DEC-957' in impl else ''})", [t.path],
                 [f"Task: {tid}", f"Implements: {impl}", "Role: orchestrator"])
    with open(DONE, "a") as f:
        f.write(tid + "\n")
    print(sha, w2, tid, what, flush=True)


# 1. The 19 deferred to Wave 3
DEFER = {
    "W2-09": ("DAEO-a3m2", 1, "The guard keeps only its four, then five, rules (DEC-953 item 2); DEC-946 already held it"),
    "W2-10": ("DAEO-cuao", 1, "Deferred in REPLAN §2.2; the guard is down to its rules; W2-11 no longer depends on it"),
    "W2-12": ("DAEO-j8gn", 1, "K5, `gov approve` (DEC-941 item 3)"),
    "W2-14": ("DAEO-7y6v", 1, "REPLAN §2.2; the governance share is measured on W2-81 and EXAMIN instead (W2-60b's records)"),
    "W2-17": ("DAEO-sdhj", 1, "The rest of K7 (DEC-941 item 3); CAP-45.a moves to Wave 3 by a CIT-P note or is a named exception"),
    "W2-18": ("DAEO-057v", 1, "The rest of K7 (DEC-941 item 3); W2-81 and EXAMIN install W2-16's release (DEC-954 Q8c)"),
    "W2-19": ("DAEO-jzvg", 1, "EXAMIN's tests are pytest (W2-26's README, finding 1), so DEC-727's condition is not met"),
    "W2-22": ("DAEO-xm6l", 1, "K8 (DEC-941 item 3); `gov doctor` green on EXAMIN's copy is W2-27's KPI"),
    "W2-31": ("DAEO-wbdh", 2, "CAP-04 moved to Wave 3 (DEC-841); REPLAN §2.2"),
    "W2-34": ("DAEO-yadm", 2, "CAP-30.c moved to Wave 3 (DEC-841)"),
    "W2-35": ("DAEO-2keg", 2, "CAP-30.g moved to Wave 3 (DEC-841)"),
    "W2-36": ("DAEO-w19l", 2, "CAP-32.d moved to Wave 3 (DEC-841)"),
    "W2-38": ("DAEO-g23i", 2, "CAP-53.b moved to Wave 3 (DEC-841); W2-66 covers selection"),
    "W2-39": ("DAEO-wudw", 2, "CAP-37.e moved to Wave 3 (DEC-841)"),
    "W2-41": ("DAEO-s694", 2, "`gov close` is not a gate here; its high rows go to Wave 3's hardening; W2-81's proof shows whether any bites"),
    "W2-42": ("DAEO-fau3", 2, "The guard is down to its rules; write scope is lifted (DEC-953 item 2)"),
    "W2-43": ("DAEO-u5g6", 2, "K8 (DEC-941); the nightly is the integration check (DEC-952 1b; DEC-953 item 3)"),
    "W2-44": ("DAEO-zndm", 2, "Trailers are lifted as a gate (audit §4.3)"),
    "W2-45": ("DAEO-neam", 2, "K8 (DEC-941); W2-26 found no trigger (indexing about 30 % of the envelope)"),
}
for w2, (tid, prio, why) in DEFER.items():
    def fn(t, prio=prio, why=why):
        t.set("priority", "4", was=str(prio))
        t.add_tags("wave-3", "deferred")
        t.body_line(f"**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** {why}.")
    run(w2, tid, fn, what="deferred to Wave 3")


# 2. Parked, withdrawn
def w78(t):
    t.set("status", "open", was="in_progress")
    t.set("priority", "4", was="1")
    t.add_tags("parked", "wave-3")
    t.body_line("**Parked by the owner (DEC-954 Q5; P-W2-78-PARK (a), 2026-10-30).** The branch w2/W2-78 and its "
                "worktree's commits are kept unmerged for Wave 3's hardening or for when the lifted gates come back. "
                "Nothing on w2/integrate changes. DEC-953 item 4a gets the effect: the selection leaves governance files "
                "out. Its discoveries are filed as Wave 2 list rows (W2-H064, W2-L453, W2-L454). For whoever resumes it: "
                "(1) src/gov/close/command.py:233-234 decides from the path map's own accepted_reds and load_sensitive "
                "keys whether runs report each test's result, so a move of the lists must move that reading too; (2) "
                "W1-01's support (w1_01_support.acceptance_exemptions) reads the path map itself; (3) W2-66's live case "
                "test_the_record_only_paths_are_dec_891_s_places_and_nothing_else enforces DEC-891's place list; (4) the "
                "merge needed about half a day of test revisions in 79 earlier-suite cases, two path-map ACTs, a re-pin "
                "and the outside readers' updates (P-W2-78-PARK §2).")


run("W2-78", "DAEO-v4is", w78, what="parked (P-W2-78-PARK (a))")


def w79(t):
    t.set("status", "closed", was="open")
    t.add_tags("withdrawn")
    t.body_line("**WITHDRAWN by the owner (DEC-953 item 10c, approved by DEC-954, 2026-10-30), unbuilt.** The brief "
                "builder changes with W2-11 and W2-60a. This ticket's KPI that every fixed brief gap stays fixed "
                "(brief-gaps.md's \"Fixed by\" column) passes to W2-11 (DAEO-k7hz). It ends by that decision, not by a "
                "10-practice close.")


run("W2-79", "DAEO-av72", w79, what="withdrawn")


def w80(t):
    t.set("status", "closed", was="open")
    t.add_tags("withdrawn")
    t.body_line("**WITHDRAWN by the owner (DEC-953 item 10c, approved by DEC-954, 2026-10-30), unbuilt.** The close "
                "queue's gates (a) to (h) are lifted (LIFTED-BY-DEC953.md A: ended). It ends by that decision, not by a "
                "10-practice close.")


run("W2-80", "DAEO-03dg", w80, what="withdrawn")


# 3. Dependency changes
def w11(t):
    t.drop("deps", "DAEO-cuao")
    t.drop("depends_on", "DAEO-cuao")
    t.kpi_append("Every gap the orchestrator fixed in the common brief or the brief builder "
                 "(governance/project/orchestration/brief-gaps.md, its \"Fixed by\" column) has a case that builds a "
                 "brief today and shows the fix is still in it; taken from the withdrawn W2-79 (DEC-954, PLAN-W2-DEC953 "
                 "§4.2) [DEC-943 item 1]")
    t.add("sources", "DEC-954", "DEC-943", "DEC-957")
    t.body_line("**DEC-954 (2026-10-30):** W2-10 (Wave 3) dropped from the dependencies; it takes W2-79's KPI. "
                + ROLES + " A second edit follows if the roles work widens these KPIs.")


run("W2-11", "DAEO-k7hz", w11, impl="DEC-954, DEC-957", what="drops W2-10, takes W2-79's KPI, roles spec approved")


def w23(t):
    t.set_list("deps", [x if x != "DAEO-057v" else "DAEO-49o5" for x in t.list_items("deps")])
    t.set_list("depends_on", [x if x != "DAEO-057v" else "DAEO-49o5" for x in t.list_items("depends_on")])
    t.add("sources", "DEC-954")
    t.body_line("**DEC-954:** depends on W2-16 (DAEO-49o5), not W2-18 (Wave 3). It shares src/gov/adopt/ with W2-52 "
                "and W2-88, split by file; whichever merges second merges back.")


run("W2-23", "DAEO-kmcr", w23, what="depends on W2-16, not W2-18")

W24 = ["DAEO-g0ip", "DAEO-zflj", "DAEO-ym8a", "DAEO-u4oz", "DAEO-0z8c", "DAEO-kia7", "DAEO-r9ss", "DAEO-7r5e",
       "DAEO-k7hz", "DAEO-zqvn", "DAEO-rd0g", "DAEO-49o5", "DAEO-r30l", "DAEO-1ahb", "DAEO-kmcr", "DAEO-ha8z",
       "DAEO-kl5e", "DAEO-7rr2", "DAEO-cy5o", "DAEO-siiz", "DAEO-wnnz", "DAEO-egsy", W88]


def w24(t):
    gone = {"DAEO-a3m2", "DAEO-cuao", "DAEO-j8gn", "DAEO-7y6v", "DAEO-sdhj", "DAEO-057v", "DAEO-jzvg", "DAEO-xm6l",
            "DAEO-xxgp"}
    assert gone <= set(t.list_items("deps")), set(t.list_items("deps"))
    assert set(t.list_items("deps")) - gone <= set(W24)
    t.deps(W24)
    t.add("sources", "DEC-954")
    t.body_line("**DEC-954:** dependencies are the Wave 2 tickets only (W2-57, W2-52, W2-56, W2-51 and W2-88 added as "
                "later Track A tickets). The AR lines whose tickets moved to Wave 3 are named Wave 3 in this ticket's "
                "report (exit criterion 5). W2-17 is Wave 3, so the \"gov update\" step is a named Wave 3 line. The "
                "release is W2-16's.")


run("W2-24", "DAEO-0mab", w24, what="dependencies are the Wave 2 tickets only")

W27 = ["DAEO-g0ip", "DAEO-ym8a", "DAEO-u4oz", "DAEO-0z8c", "DAEO-kia7", "DAEO-49o5", "DAEO-r30l", "DAEO-1ahb",
       "DAEO-kmcr", "DAEO-2ds6", "DAEO-ha8z", "DAEO-kl5e", "DAEO-siiz", "DAEO-wnnz", "DAEO-0pyc", "DAEO-cv58",
       "DAEO-ecac", "DAEO-k7hz", "DAEO-lrre", "DAEO-l78m", "DAEO-4k3l", "DAEO-dy7j", W88, W94]


def w27(t):
    t.deps(W27)
    t.kpi_append("W2-16's numbered, frozen release is the one installed, never this repository's branch [DEC-954 Q8c]")
    t.kpi_append("A clean gov close of the LITE ticket on the copy, at exit 0, on that release, is exit criterion 1's "
                 "proof; gov doctor green on the copy is exit criterion 3's [DEC-953, DEC-954]")
    t.kpi_append("W2-88's tools run on the copy at adoption (the assessment, the refactoring plan as proposals, the full "
                 "index and embeddings), and EXAMIN's question set (W2-94) is measured with both figures, hit@5 against "
                 "CAP-10's floor of 85 and the owner's target of 95 % [DEC-954 Q9f, DEC-957]")
    t.add("sources", "DEC-953", "DEC-954", "DEC-957")
    t.body_line("**DEC-954 Q1:** this ticket starts only when K9's entry criteria are met: memory proven, the roles, "
                "skills and briefs landed, the proving ground passed, the rest of the minimum closed. Never because a "
                "date arrived.")


run("W2-27", "DAEO-h4rh", w27, impl="DEC-954, DEC-957", what="K9's criteria, W2-88 and W2-94 as deps")


def w29(t):
    t.add("deps", "DAEO-49o5")
    t.add("depends_on", "DAEO-49o5")


run("W2-29", "DAEO-b926", w29, what="depends on W2-16's release")


def w33(t):
    t.drop("deps", "DAEO-1ahb")
    t.drop("depends_on", "DAEO-1ahb")
    t.set("title", "'The three layers'' roles and the typed handoff: the CTO, the Senior Engineer, the ticket lead''s role "
          "file, machine-readable defaults per role (the roles spec defines it)'",
          was="Wave 2 roles and typed handoff records")
    t.add_tags("three-layers")
    t.kpi_set_all([
        "Role files for the CTO (the master orchestrator) and the Senior Engineer (a stream's sub-orchestrator, with its "
        "stream's skills), generated as agents, each with its reads and writes, skills, model, brief contents and "
        "handover, as ROLES-SPEC-1 (approved, DEC-957) states them [DEC-954 Q6, Q13, DEC-957]",
        "The ticket lead's own role file (today a section of orchestrator.md) [DEC-954, DEC-236]",
        "Machine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a's launcher; effort "
        "high for the CTO and the Senior Engineers [DEC-954, DEC-839 item 5, DEC-957]",
        "A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step "
        "identically; the twelve-field return is one [CAP-22.b (lite), AR-6]",
        "Any role the roles spec finds undefined is scoped and drafted here [DEC-954 Q13a]",
    ])
    t.failure_set(["A role built other than as the approved roles spec states it; a role file placed by hand rather "
                   "than generated; a role without its machine-readable defaults."])
    t.add("sources", "DEC-954", "DEC-957")
    t.drop("closes", "CAP-22.c")
    t.body_line("**Re-scoped by DEC-954 (Q6, Q13).** The earlier KPIs (test-execution, integration and UX roles) and "
                "CAP-22.c become Wave 3 rows unless the roles spec places them; CAP-22.b is carried lite (DEC-841 had "
                "moved CAP-22.b/c to Wave 3). " + ROLES)


run("W2-33", "DAEO-lrre", w33, impl="DEC-954, DEC-957", what="re-scoped to the three layers' roles")

W46_DROP = {"DAEO-a3m2", "DAEO-cuao", "DAEO-j8gn", "DAEO-7y6v", "DAEO-sdhj", "DAEO-057v", "DAEO-jzvg", "DAEO-xm6l",
            "DAEO-wbdh", "DAEO-yadm", "DAEO-2keg", "DAEO-w19l", "DAEO-g23i", "DAEO-wudw", "DAEO-s694", "DAEO-fau3",
            "DAEO-u5g6", "DAEO-zndm", "DAEO-neam", "DAEO-xxgp"}
W46 = ["DAEO-g0ip", "DAEO-zflj", "DAEO-ym8a", "DAEO-u4oz", "DAEO-0z8c", "DAEO-kia7", "DAEO-r9ss", "DAEO-7r5e",
       "DAEO-k7hz", "DAEO-zqvn", "DAEO-rd0g", "DAEO-swdu", "DAEO-49o5", "DAEO-r30l", "DAEO-1ahb", "DAEO-kmcr",
       "DAEO-0mab", "DAEO-btt7", "DAEO-2ds6", "DAEO-h4rh", "DAEO-csj8", "DAEO-b926", "DAEO-60rw", "DAEO-0pyc",
       "DAEO-lrre", "DAEO-6n5k", "DAEO-6ox0", "DAEO-ha8z", "DAEO-kl5e", "DAEO-egsy", "DAEO-siiz", "DAEO-7rr2",
       "DAEO-0rfi", "DAEO-arrl", "DAEO-wnnz", "DAEO-cy5o", "DAEO-5j8b", "DAEO-kh9l", "DAEO-cv58", "DAEO-ecac",
       "DAEO-iw1f", "DAEO-h2k3", "DAEO-juee", "DAEO-pl6k", "DAEO-0uhh", "DAEO-e82f", "DAEO-c1uz", "DAEO-9nys",
       "DAEO-2gc7", "DAEO-rmbe", "DAEO-uzme", "DAEO-e8f0", "DAEO-ye2a", "DAEO-qty6", "DAEO-2azm", "DAEO-ebmh",
       "DAEO-tgk2", "DAEO-b6hm", "DAEO-l78m", "DAEO-4k3l", "DAEO-dy7j", "DAEO-mc6n", "DAEO-m1u3", "DAEO-gdzh",
       "DAEO-s9qc", W86, W88, W90, W91, W92, W93, W94]


def w46(t):
    cur = set(t.list_items("deps"))
    assert W46_DROP <= cur, W46_DROP - cur
    assert cur - W46_DROP <= set(W46), (cur - W46_DROP) - set(W46)
    t.deps(W46)
    t.add("sources", "DEC-953", "DEC-954")
    t.body_line("**DEC-954:** dependencies are the Wave 2 tickets only (Wave 3, withdrawn and parked removed; W2-86, "
                "W2-88, W2-90 and W2-91 to W2-94 added). The exit run checks §5 as revision 4 states it: 10-practice "
                "close records; a clean gov close on W2-81 and EXAMIN's copy; the governance share on W2-81 and EXAMIN; "
                "gov doctor green on EXAMIN's copy. Each stream's coordination ticket is added when filed.")


run("W2-46", "DAEO-nn1s", w46, what="dependencies are the Wave 2 tickets only")


def w15a(t):
    t.add("deps", "DAEO-h2k3")
    t.add("depends_on", "DAEO-h2k3")
    t.kpi_append_to(0, " Answered by DEC-954 Q9 and DEC-957: the metric is W2-61's measure, both figures, on the "
                       "enlarged set of 48 questions (24 visible, 24 hidden), the hidden half used only once the "
                       "five-rule hook and W2-84 refuse it from every worktree; hit@5 is judged against the owner's "
                       "target of 95 % with CAP-10's 85 the floor, memory proven on the hidden half at least 21 of 24, "
                       "judged on the combined memory spec (Q9c) [DEC-954 Q9, DEC-957]",
                    startswith="The metric is defined")
    t.add("sources", "DEC-954", "DEC-957")


run("W2-15a", "DAEO-rd0g", w15a, impl="DEC-954, DEC-957", what="Q-2 answered; the hidden half before it runs")


def w15b(t):
    t.add("deps", W88)
    t.add("depends_on", W88)
    t.kpi_append("Memory is judged on the combined memory spec (semantic and lexical search, full indexing, full "
                 "embeddings, the knowledge and code graph, the SQLite and vector-store structure); EXAMIN's clone and "
                 "~/workspace are indexed with W2-88's tools [DEC-954 Q9c, Q9f]")
    t.kpi_append("hit@5 is judged against the owner's target of 95 %, CAP-10's 85 the floor; at 85 or above with room "
                 "for improvement found, memory is not closed: an escalation to the owner [DEC-957]")
    t.add("sources", "DEC-954", "DEC-957")


run("W2-15b", "DAEO-swdu", w15b, impl="DEC-954, DEC-957", what="on the combined spec, with W2-88; target 95 %")


# 4. Re-scopes and KPI additions
def w61h(t):
    t.set_list("deps", ["DAEO-m1u3"], inline=True)
    t.set("title", "'W2-61''s enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by "
          "an independent session'")
    t.kpi_replace(0, "Twenty-eight new questions about this repository's governance and code, each with its gold answer "
                     "and the governing source or sources an answer must cite, in the form W2-61's visible half takes; "
                     "after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 "
                     "to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml, and "
                     "hidden/) [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d)]",
                  startswith="Twenty hidden questions")
    t.kpi_replace(2, "The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 "
                     "whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, "
                     "callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) "
                     "3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, "
                     "ticket or path-map fact 1, an id that exists nowhere 1 [DEC-954 Q9a, Q9c, DEC-833, DEC-866]",
                  startswith="The same spread")
    t.kpi_append("The hidden half is used for a measure only after ACT 1's five-rule hook and W2-84 refuse it from every "
                 "worktree and run clone [DEC-954 Q9b, DEC-950]")
    t.add("allowed_paths", *[f"fixtures/evaluation/memory-retrieval/visible/q{n}.yaml" for n in (21, 22, 23, 24)])
    t.add("sources", "DEC-954", "DEC-957", "DEC-950")
    t.body_line("**Re-scoped by DEC-954 Q9a; the size confirmed by DEC-957:** 48 questions with lens B's 20 (24 visible, "
                "24 hidden); K9's \"memory proven\" is judged on the hidden half, at least 21 of 24 hit@5, against the "
                "owner's target of 95 %. Est. 12 to 14 lead-hours (MEMORY-SPEC-MAP B.2).")


run("W2-61h", "DAEO-h2k3", w61h, impl="DEC-954, DEC-957", what="the enlarged set, 28 new questions")


def w32(t):
    t.kpi_append("If memory is below 85 % after two improvement rounds, the orchestrator escalates to the owner with the "
                 "reasons; at the third the owner decides: a discovery and research ticket benchmarking market tools in "
                 "a separate worktree, accepting the level reached, or another course. At 85 % or above but under the "
                 "owner's target of 95 %, with room for improvement found, memory is not closed: an escalation to the "
                 "owner [DEC-954 Q9e, DEC-957]")
    t.add("sources", "DEC-954", "DEC-957")


run("W2-32", "DAEO-0pyc", w32, impl="DEC-954, DEC-957", what="the escalation after two rounds; target 95 %")


def w81(t):
    t.kpi_append("In each synthetic repository, a ticket closes with gov close at exit 0 on a pinned release (W2-16's "
                 "numbered, frozen release): the clean gov close of exit criterion 1; its real run is the orchestrator's "
                 "[DEC-953, DEC-954 Q8c]")
    t.kpi_append("The builders and the per-repository question sets serve W2-88's proof of memory for any repository, "
                 "read-only; the hidden half is W2-93's [DEC-954 Q9f, DEC-957]")
    t.add("sources", "DEC-953", "DEC-954", "DEC-957")


run("W2-81", "DAEO-l78m", w81, impl="DEC-954, DEC-957", what="the gov close proof on a pinned release")


def w83b(t):
    t.set("title", "'One playbook per stream (the Senior Engineer''s brief), placing annex D''s standing practices'")
    t.set("priority", "1", was="2")
    t.set("tags", "[wave-2, documentation, playbooks, standard, three-layers]",
          was="[wave-2, documentation, playbooks, standard, spare-capacity]")
    t.kpi_replace(0, "One playbook per stream (S1 memory; S2 roles, skills and briefs; S3 sandbox and launch; S4 adoption "
                     "and the proving ground), under docs/playbooks/, in W2-83a's form: the stream's purpose, its "
                     "standing practices each citing its decision, its usual ticket classes, its roles with their "
                     "skills, its handovers to the CTO, and the escalation rubric (P3, P2, P1, emergency); each is the "
                     "stream's Senior Engineer's brief; gov check is green on them [DEC-954 Q13, DEC-953 item 8, DEC-944 "
                     "item 3, DEC-957]", startswith="One playbook per keystone")
    t.set("est_loc", "250", was="500")
    t.add("sources", "DEC-953", "DEC-954", "DEC-957")
    t.body_line("**Re-scoped by DEC-953 and DEC-954 (PLAN-W2-DEC953 §6):** the stream playbooks, a three-layer "
                "foundation built in S2 before ACT 2; no longer spare capacity. " + ROLES)


run("W2-83b", "DAEO-mc6n", w83b, impl="DEC-954, DEC-957", what="one playbook per stream")


def roles_only(t):
    t.add("sources", "DEC-954", "DEC-957")
    t.body_line("**DEC-954, DEC-957:** " + ROLES)


run("W2-83a", "DAEO-dy7j", roles_only, impl="DEC-954, DEC-957", what="roles spec approved")
run("W2-60b", "DAEO-ecac", roles_only, impl="DEC-954, DEC-957", what="roles spec approved")


def w20(t):
    t.add("sources", "DEC-954")
    t.body_line("**DEC-954 Q12:** in Wave 2, built on the owner's measured rule for this machine (DEC-950). "
                "Machine-agnostic in Wave 3: a parking-list row (W3-P12).")


run("W2-20", "DAEO-r30l", w20, what="DEC-950's rule (Q12)")


def w16(t):
    t.add("sources", "DEC-954")
    t.body_line("**DEC-954 Q8c:** cuts a numbered, frozen release that W2-81 and EXAMIN's copy install; the owner tags "
                "it. Finished after ACT 1.")


run("W2-16", "DAEO-49o5", w16, what="the numbered, frozen release (Q8c)")


def w61(t):
    t.add("sources", "DEC-957")
    t.body_line(f"**DEC-957 (2026-10-30):** KPI 6 (EXAMIN's set, the same split) moves to W2-94 ({W94}), filed for "
                "MEMORY-SPEC-MAP gap 7; this ticket's close record names it as moved.")


run("W2-61", "DAEO-iw1f", w61, impl="DEC-954, DEC-957", what="KPI 6 moves to W2-94")
print("edits done")
