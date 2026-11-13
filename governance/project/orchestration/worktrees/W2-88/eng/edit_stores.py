import re
p = "src/gov/adopt/fabric.py"
s = open(p).read()
old1 = s[s.index("    lexical_i, lexical_r = [], []\n"):s.index("    held = sorted(records & set(paths))")]
new1 = '''    lexical_i, lexical_r = [], []
    binary_files = _binary(run, [rel for rel in paths if verdicts.get(rel) == 1])
    for rel in paths:
        state = verdicts.get(rel)
        if state is None:
            continue  # the keyword index holds no verdict on it: it is in neither list, and check_coverage says so
        if state == 1:  # a binary the index chunked is held by the store: indexed, and named in ``binary_held`` (RV1-4)
            lexical_i.append(rel)
        elif state == 2:
            lexical_r.append({"path": rel, "reason": "not-embedded"})
        elif _memory_class(run.config, namespaces[rel]) != "governance":
            # ``gov.secrets.indexable`` lets through only a namespace whose memory_class is governance
            lexical_r.append({"path": rel, "reason": "not-embedded"})
        else:
            try:
                binary = b"\\0" in project.blob(run.root, run.tracked[rel])[:8000]
            except GovError:
                binary = False
            lexical_r.append({"path": rel, "reason": "binary" if binary else "secrets"})  # a binary the store did not take
    vec_i = [rel for rel in lexical_i if rel in vectored]
    vec_r = [{"path": rel, "reason": "not-embedded"} for rel in lexical_i
             if rel in chunked and rel not in vectored and _policy(run.config, namespaces[rel]) != "embedded"]
    code = [rel for rel in paths if Path(rel).suffix.lower() in assess.CODE_GRAPH_SUFFIXES | assess.OTHER_CODE_SUFFIXES]
    called_for = project.code_intelligence(run.config)
    code_i, code_r = [], []
    for rel in code if called_for else ():
        if Path(rel).suffix.lower() not in assess.CODE_GRAPH_SUFFIXES:
            code_r.append({"path": rel, "reason": "unsupported-language"})  # never indexed by the graph (RV1-5)
        elif (run.root / codeintel.BASE_REL / "files" / rel).is_file():
            code_i.append(rel)
        else:
            code_r.append({"path": rel, "reason": "secrets" if verdicts.get(rel) == 0 else "not-embedded"})
    nodes = edges = 0
    unreadable = None
    if called_for and code_i:
        try:
            graph, users = codeintel._graph(run.root)
            nodes, edges = len(graph), sum(len(each) for each in users.values())
        except Exception as exc:  # noqa: BLE001 - a graph that cannot be read is named, never shown as 0 nodes and edges
            unreadable = f"{type(exc).__name__}: {' '.join(str(exc).split())}"
'''
s = s.replace(old1, new1)
s = s.replace('''        "lexical": {**base, "judged": len(paths), "indexed": lexical_i, "refused": lexical_r, "chunks": n_chunks,
                    "seconds": timing.get("lexical_s", 0.0)},
        "vectors": {**base, "judged": len([rel for rel in lexical_i if rel in chunked]), "indexed": vec_i, "refused": vec_r, "chunks": n_chunks,
                    "vectors": n_vectors, "seconds": timing.get("semantic_s", 0.0)},
        "codegraph": {**base, "judged": len(code_i) + len(code_r), "indexed": code_i, "refused": code_r, "nodes": nodes,
                      "edges": edges, "seconds": timing.get("codeintel_s", 0.0),
                      **({} if called_for else {"requested": False})},''',
'''        "lexical": {**base, "judged": len(paths), "indexed": lexical_i, "refused": lexical_r, "chunks": n_chunks,
                    "binary_held": [rel for rel in lexical_i if rel in binary_files], "seconds": timing.get("lexical_s", 0.0)},
        "vectors": {**base, "judged": len([rel for rel in lexical_i if rel in chunked]), "indexed": vec_i, "refused": vec_r,
                    "chunks": n_chunks, "vectors": n_vectors, "binary_held": [rel for rel in vec_i if rel in binary_files],
                    "seconds": timing.get("semantic_s", 0.0)},
        "codegraph": {**base, "judged": len(code_i) + len(code_r), "indexed": code_i, "refused": code_r, "nodes": nodes,
                      "edges": edges, "seconds": timing.get("codeintel_s", 0.0),
                      **({} if called_for else {"requested": False}),
                      **({"built": False, "error": unreadable} if unreadable else {})},''')
open(p, "w").write(s)
