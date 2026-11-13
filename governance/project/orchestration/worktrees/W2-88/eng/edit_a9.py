p = "src/gov/adopt/fabric.py"
s = open(p).read()
start = s.index("def a9(run) -> dict:")
body = s[start:]
body = body.replace('''def a9(run) -> dict:
    """Stage A9 lite (see the module's text). ``run`` is ``gov.adopt.stages.Run``."""
    from gov.rebuild import command as rebuild

    root, args = run.root, run.args
    out = _out(args, root)
    decisions = list(getattr(args, "decision", None) or [])
    budget = getattr(args, "budget_ms", None) or RETRIEVE_BUDGET_MS
    standard = read_standard(root, decisions)  # STANDARD_DEPARTURE refuses before any store is built
    built = rebuild.run(''', '''def a9(run) -> dict:
    """Stage A9 lite (see the module's text). ``run`` is ``gov.adopt.stages.Run``. The standard is judged first (a
    refusal there writes nothing); then the kernel files are installed and staged, the stores built and the record
    committed with them in one commit; a refusal after the copies undoes them (nothing is left in the tree)."""
    root, args = run.root, run.args
    out = _out(args, root)
    decisions = list(getattr(args, "decision", None) or [])
    standard = read_standard(root, decisions)  # CONFIG_INVALID, STANDARD_DEPARTURE: before any copy and any store
    head = project.resolve(root, "HEAD")
    copies = install(run, head)
    try:
        return _stage(run, out, standard, copies)
    except BaseException:
        undo(root, head, copies)
        raise


def _stage(run, out: Path, standard: dict, copies: dict) -> dict:
    from gov.rebuild import command as rebuild

    root, args = run.root, run.args
    budget = getattr(args, "budget_ms", None) or RETRIEVE_BUDGET_MS
    built = rebuild.run(''')
body = body.replace('''    data = {"commit": project.resolve(root, "HEAD"), "stores": stores, "digests": built["digests"], "standard": standard,
''', '''    data = {"commit": project.resolve(root, "HEAD"), "installed": copies["installed"], "kept": copies["kept"],
            "stores": stores, "digests": built["digests"], "standard": standard,
''')
body = body.replace('''    return run.finish(data, None, ok=True, digests=built["digests"], over=said, out=str(out))''',
                    '''    return run.finish(data, None, ok=True, digests=built["digests"], over=said, out=str(out),
                      installed=copies["installed"], kept=copies["kept"])''')
open(p, "w").write(s[:start] + body)
