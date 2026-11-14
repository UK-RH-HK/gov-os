"""Step 2 of the build: the re-anchoring flow's planning, its checks on the result, its delivery and the wiring in
build_and_run (run in the work clone after edit1.py)."""
import sys

p = sys.argv[1]
s = open(p).read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old, s.count(old))
    s = s.replace(old, new)


# -- the planner, after plan_fix ---------------------------------------------------------------------------------
rep('''    return [(src, f"input/{fix_id}.yaml")], staged


''', '''    return [(src, f"input/{fix_id}.yaml")], staged


def plan_reanchor(root, set_name, week, commit):
    """ACT-WALLS-REANCHOR-1: the weekly re-anchoring flow's inputs, read and checked before anything is written:
    (plan, staged, counts). The request is runs/<set>/REANCHOR-<week>.json under the root, in the memory audit's fixed
    form (week, audit_commit, set, changed, count; each row a question id and an entry number); its audit_commit must be
    the commit the tree is built at (14). Each requested id with a hidden/<id>.yaml is staged as a byte copy; an id with
    none is counted as absent; a hidden file that is not a plain file, a form that is not the fixed one, or no id staged: 10."""
    path = os.path.join(root, "runs", set_name, f"REANCHOR-{week}.json")
    data = read_plain(path, root)
    if data is None or len(data) > MOST_RESULT_BYTES:
        raise Refuse(10, "input")
    try:
        req = load_json_strict(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise Refuse(10, "input")
    if not isinstance(req, dict) or set(req) != {"week", "audit_commit", "set", "changed", "count"}:
        raise Refuse(10, "input")
    rows = req["changed"]
    if (req["week"] != week or req["set"] != set_name or not full(HEX40, req["audit_commit"])
            or not isinstance(rows, list) or not 0 < len(rows) <= REANCHOR_MOST or req["count"] != len(rows)
            or isinstance(req["count"], bool)):
        raise Refuse(10, "input")
    if req["audit_commit"] != commit:
        raise Refuse(14, "reanchor_commit")  # the lines were listed at another commit than the tree's
    seen, by_id = set(), {}
    for row in rows:
        if not (isinstance(row, dict) and set(row) == {"id", "entry"} and full(REANCHOR_ID_RX, row["id"])
                and is_count(row["entry"]) and row["entry"] >= 1) or (row["id"], row["entry"]) in seen:
            raise Refuse(10, "input")
        seen.add((row["id"], row["entry"]))
        by_id.setdefault(row["id"], []).append(row["entry"])
    hidden = os.path.join(root, "fixtures", "evaluation", set_name, "hidden")
    plan, present = [], []
    for qid in sorted(by_id):
        src = os.path.join(hidden, f"{qid}.yaml")
        if not os.path.lexists(src):
            continue
        if not real_inside(src, root) or not regular(src):
            raise Refuse(10, "input")
        plan.append((src, f"input/{qid}.yaml"))
        present.append(qid)
    if not present:
        raise Refuse(10, "input")
    request = {"week": week, "changed": [{"id": q, "entry": n} for q in present for n in sorted(by_id[q])]}
    staged = {"input/reanchor.json": (json.dumps(request, indent=1) + "\\n").encode("utf-8")}
    return plan, staged, {"entries": len(rows), "ids": len(present), "absent": len(by_id) - len(present),
                          "present": present}


''')

# -- the delivery, after deliver_fix ------------------------------------------------------------------------------
rep('''    st.counts["delivered"].update(files=1, sha256=h, to="set")


''', '''    st.counts["delivered"].update(files=1, sha256=h, to="set")


def deliver_reanchor(st, ctx):
    """ACT-WALLS-REANCHOR-1: the weekly re-anchoring flow's delivery. out/ holds exactly out/<id>.yaml for each staged id
    and out/result.json; each YAML is a mapping whose `id` is its id; every check first, then only the staged ids'
    hidden/<id>.yaml are replaced, all or nothing (the old files kept for the run's tar as replaced-hidden/<id>.yaml).
    Any refusal leaves the set unchanged: 20."""
    ids, out = ctx["reanchor"]["present"], os.path.join(st.wall, "out")
    hidden = os.path.join(ctx["root"], "fixtures", "evaluation", ctx["set"], "hidden")
    try:
        entries = sorted(os.listdir(out))
    except OSError:
        raise Refuse(20, "missing")
    if entries != sorted([f"{q}.yaml" for q in ids] + ["result.json"]):
        raise Refuse(20, "entries")
    land, new, old, shas = Landing(ctx["root"]), {}, {}, []
    try:
        for qid in ids:
            name, dst = f"{qid}.yaml", os.path.join(hidden, f"{qid}.yaml")
            data = read_plain(os.path.join(out, name), out)
            if data is None or len(data) > MOST_RESULT_BYTES:
                raise Refuse(20, "missing")
            try:
                q = yaml.safe_load(data.decode("utf-8"))
            except (UnicodeDecodeError, yaml.YAMLError, RecursionError):
                raise Refuse(20, "yaml")
            if not isinstance(q, dict) or q.get("id") != qid:
                raise Refuse(20, "yaml")
            if not real_inside(dst, ctx["root"]) or not regular(dst):
                raise Refuse(20, "destination")
            before = read_plain(dst, hidden)
            if before is None:
                raise Refuse(20, "destination")
            old[name] = before
            new[name] = (dst, data)
        kept = st.wall + ".replaced"
        os.mkdir(kept, 0o700)
        st.replaced = kept
        for name in sorted(new):
            write_new(os.path.join(kept, name), old[name], 0o400)
            shas.append((name, land.add(new[name][0], new[name][1], replace=True)))
        land.commit()
    except BaseException:
        land.abort()
        if st.replaced:
            remove_tree(st.replaced)
            st.replaced = None
        raise
    st.counts["delivered"].update(files=len(ids), sha256=delivered_sha(shas), to="set")


''')

# -- the result's checks -------------------------------------------------------------------------------------------
rep('''            st.counts["fix"]["action"] = res["action"]
    st.counts["out"]["schema_ok"] = True''', '''            st.counts["fix"]["action"] = res["action"]
        if ctx.get("reanchor"):  # the staged ids' count, and `corrected` and `replaced` summing to it
            n = len(ctx["reanchor"]["present"])
            if (res["questions"] != n or sum(res["by_kind"].values()) != n or sum(res["by_area"].values()) != n
                    or not is_count(res.get("corrected")) or not is_count(res.get("replaced"))
                    or res["corrected"] + res["replaced"] != n):
                raise Refuse(20, "reanchor_result")
            st.counts["reanchor"].update(corrected=res["corrected"], replaced=res["replaced"])
    st.counts["out"]["schema_ok"] = True''')

# -- build_and_run -------------------------------------------------------------------------------------------------
rep('''    spec = kinds[kind]
    ex_globs = excludes_of(tmpl["tree-exclude.txt"])''', '''    spec = kinds[kind]
    if o.reanchor is not None and "reanchor" not in spec.get("input_reanchor", ()):
        raise Refuse(11, "kinds")  # the approved template does not declare the re-anchoring input for this kind
    ex_globs = excludes_of(tmpl["tree-exclude.txt"])''')
rep('''    fix = (o.fix, o.reason) if o.fix is not None else None  # W2-94: validated by check_args (17)
    model, schema_name, sample_n, brief_id, entry = resolve_brief(fm, kind, spec, briefs, fix is not None)''',
    '''    fix = (o.fix, o.reason) if o.fix is not None else None  # W2-94: validated by check_args (17)
    rea = o.reanchor is not None  # ACT-WALLS-REANCHOR-1: validated by check_args (17)
    model, schema_name, sample_n, brief_id, entry = resolve_brief(fm, kind, spec, briefs, fix is not None or rea)''')
rep('''        plan, fix_staged = plan_fix(root, walls, runs_indep, set_name, *fix)
        tree_ex = excluded
''', '''        plan, fix_staged = plan_fix(root, walls, runs_indep, set_name, *fix)
        tree_ex = excluded
    elif rea:
        plan, fix_staged, rea_info = plan_reanchor(root, set_name, o.reanchor, commit)
        c["reanchor"].update({k: rea_info[k] for k in ("entries", "ids", "absent")})
        tree_ex = excluded
''')
rep('''(WALL_FIXED + len(plan) + RUN_EXTRA + (len(fix_staged) if fix else 0)) if not sgx \\''',
    '''(WALL_FIXED + len(plan) + RUN_EXTRA + (len(fix_staged) if fix or rea else 0)) if not sgx \\''')
rep('''    staged = dict(fix_staged) if fix else {}  # set-up A's files (or the fix flow's): wall-relative path -> bytes''',
    '''    staged = dict(fix_staged) if fix or rea else {}  # set-up A's files (or a fix flow's): wall-relative path -> bytes''')
rep('''           "sgx": sgx, "brief_id": brief_id, "fix": fix}''',
    '''           "sgx": sgx, "brief_id": brief_id, "fix": fix, "reanchor": rea_info if rea else None}''')
rep('''            elif fix:
                deliver_fix(st, ctx)''', '''            elif fix:
                deliver_fix(st, ctx)
            elif rea:
                deliver_reanchor(st, ctx)''')
open(p, "w").write(s)
print("step 2 ok")
