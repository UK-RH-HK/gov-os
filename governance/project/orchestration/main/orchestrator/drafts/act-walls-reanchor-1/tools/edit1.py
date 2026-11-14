"""Step 1 of the build: the launcher's constants, kinds check, docstring, arguments and counts (run in the work clone)."""
import sys

p = sys.argv[1]
s = open(p).read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old, s.count(old))
    s = s.replace(old, new)


# the docstring: the usage line and a paragraph
rep("""  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --run 20261109T120000Z-memory-recall-3-r1 --counts-only
""", """  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/<the approved reanchor brief>.md --brief-sha256 <its sha256> --commit <the request's audit_commit> --set examin --round 2 --reanchor 2026-W47
  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --run 20261109T120000Z-memory-recall-3-r1 --counts-only
""")
rep("""Exit codes: 0 delivered or dry;""", """The weekly re-anchoring flow (ACT-WALLS-REANCHOR-1; DEC-1179 (6), DEC-1178 (1)): one flag, the ISO week of the request
that `gov.memaudit maintain` wrote, given on the writer's round 2 (the last usage line above; never with the fix flow's
pair). It reads runs/<set>/REANCHOR-<week>.json under the sets root in its own code, checks its fixed form (week,
audit_commit, set, changed, count; a question id and an entry number per row, nothing else) and that its audit_commit is
the commit the tree is built at (14), and stages `input/<id>.yaml` (a byte copy of the set's `hidden/<id>.yaml`) for each
requested id that has one, with `input/reanchor.json` (the same ids and entry numbers, nothing else). An id with no hidden
file is counted as absent and not staged; none staged refuses 10. The template's kinds.yaml must declare
`input_reanchor: [questions, reanchor]` for the writer kind (11 when it does not), so the owner's approval of that file
is what opens the input. At delivery only the staged ids' `hidden/<id>.yaml` are replaced, all or nothing, by
`out/<id>.yaml`, the old files packed into the run's tar. The result adds `corrected` and `replaced` (counts summing to
`questions`, the number of staged ids). The counts carry `reanchor` {week, entries, ids, absent, corrected, replaced},
numbers only.

Exit codes: 0 delivered or dry;""")

rep('''FIX_ACTIONS = ("corrected", "replaced")
''', '''FIX_ACTIONS = ("corrected", "replaced")
# The weekly re-anchoring flow (ACT-WALLS-REANCHOR-1): the week as the memory audit names it (layout.WEEK_RE), a question's
# id (a file's stem under hidden/), the inputs kinds.yaml's `input_reanchor` may name, the most entries in one request.
REANCHOR_WEEK_RX = re.compile(r"[0-9]{4}-W[0-9]{2}")
REANCHOR_ID_RX = re.compile(r"[a-z0-9][a-z0-9_-]{0,31}")
REANCHOR_INPUTS = ("questions", "reanchor")
REANCHOR_MOST = 400
''')

rep('''        if "model" in spec and not full(MODEL_RX, spec["model"]):
            return None
    return kinds''', '''        if "model" in spec and not full(MODEL_RX, spec["model"]):
            return None
        rea = spec.get("input_reanchor")  # the inputs the weekly re-anchoring flow may stage (ACT-WALLS-REANCHOR-1)
        if "input_reanchor" in spec and not (isinstance(rea, list) and rea
                                             and all(isinstance(x, str) and x in REANCHOR_INPUTS for x in rea)):
            return None
    return kinds''')

rep('''    p.add_argument("--fix", help=argparse.SUPPRESS)
    p.add_argument("--reason", help=argparse.SUPPRESS)
''', '''    p.add_argument("--fix", help=argparse.SUPPRESS)
    p.add_argument("--reason", help=argparse.SUPPRESS)
    p.add_argument("--reanchor", help=argparse.SUPPRESS)  # the weekly re-anchoring flow's week, documented in the docstring only
''')
rep('''        if any(v is not None for v in (o.brief, o.brief_sha256, o.commit, o.set, o.round, o.audit, o.seed, o.fix,
                                       o.reason)) or o.dry:''', '''        if any(v is not None for v in (o.brief, o.brief_sha256, o.commit, o.set, o.round, o.audit, o.seed, o.fix,
                                       o.reason, o.reanchor)) or o.dry:''')
rep('''            st.counts["fix"] = {"id": o.fix, "code": o.reason, "action": None}
''', '''            st.counts["fix"] = {"id": o.fix, "code": o.reason, "action": None}
        if o.reanchor is not None:  # the week alone, the writer's round 2 only, never with the fix flow's pair
            if (o.kind != "writer" or o.round != "2" or not full(REANCHOR_WEEK_RX, o.reanchor)
                    or o.fix is not None or o.reason is not None):
                raise Refuse(17, "reanchor")
            st.counts["reanchor"] = {"week": o.reanchor, "entries": None, "ids": None, "absent": None,
                                     "corrected": None, "replaced": None}
''')
rep('''    for v in (o.kind, o.brief, o.brief_sha256, o.commit, o.set, o.round, o.audit, o.seed, o.run):''',
    '''    for v in (o.kind, o.brief, o.brief_sha256, o.commit, o.set, o.round, o.audit, o.seed, o.run, o.reanchor):''')
rep("""if x.strip().startswith("python3 ") and "--fix" not in x.split())""",
    """if x.strip().startswith("python3 ") and "--fix" not in x.split()
                                  and "--reanchor" not in x.split())""")
open(p, "w").write(s)
print("step 1 ok")
