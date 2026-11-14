import ast, sys
bw = ast.parse(open(".claude/hooks/bash_writes.py").read())
pt = ast.parse(open(".claude/hooks/pretooluse.py").read())
bad = []
top = lambda tree, kind: {n.name for n in tree.body if isinstance(n, kind)}
assigned = lambda tree: {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
for name in ("judge", "reads_view", "emptied", "line_write_targets", "comment_spans", "read_view", "_more_targets", "_shell_script"):
    if name not in top(bw, ast.FunctionDef):
        bad.append("bash_writes.py lacks " + name)
for name in ("GLOB_OPTIONS_RE", "SENT", "UNKNOWN", "COMMENT_QUOTE"):
    if name not in assigned(bw):
        bad.append("bash_writes.py lacks " + name)
cls = {n.name: n for n in bw.body if isinstance(n, ast.ClassDef)}
meths = {m.name for m in cls["Judgement"].body if isinstance(m, ast.FunctionDef)}
for name in ("adopt", "targets", "removal", "making", "foreign", "xargs"):
    if name not in meths:
        bad.append("Judgement lacks " + name)
text = open(".claude/hooks/bash_writes.py").read()
if 'elif sub == "archive":' not in text:
    bad.append("the git archive form is missing")
for name in ("line_parser", "_no_path", "_blob_ref", "_output_joined", "bash_writes_of", "crude_deletes"):
    if name not in top(pt, ast.FunctionDef):
        bad.append("pretooluse.py lacks " + name)
for name in ("NO_PATH_REFUSAL", "REV_REFUSAL", "PLACE_REFUSAL", "_PATH_FIELDS"):
    if name not in assigned(pt):
        bad.append("pretooluse.py lacks " + name)
classes_fn = next(n for n in pt.body if isinstance(n, ast.FunctionDef) and n.name == "classes")
judge = next(n for n in ast.walk(classes_fn) if isinstance(n, ast.ClassDef) and n.name == "Judge")
have = {m.name for m in judge.body if isinstance(m, ast.FunctionDef)}
for name in ("listing", "git", "colon", "placed", "cat_file", "patched", "stored", "ask"):
    if name not in have:
        bad.append("Judge lacks " + name)
if "from gov.guard.decide import _UNRESOLVABLE, _expand_token\n" not in open(".claude/hooks/pretooluse.py").read():
    bad.append("the parser wiring is not the copied line parser's")
if "_extract_bash_write_targets" in open(".claude/hooks/pretooluse.py").read().replace("# ", "", 0).split("def line_parser")[0].split("def bash_judgement")[-1][:200]:
    bad.append("the hook still names the pinned judge's parser")
print("; ".join(bad) or "both files parse; the copied line parser, the merged module, R5's no-path refusal and R4's seven Judge methods are in place")
sys.exit(1 if bad else 0)
