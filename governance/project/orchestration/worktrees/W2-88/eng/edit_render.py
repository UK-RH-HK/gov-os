p = "/home/usain/gov-os-runs/W2-88/render_evidence.py"
s = open(p).read()
s = s.replace('''- **scale:** lexical {sc['routes']['lexical']} ms, semantic {sc['routes']['semantic']} ms (the stand-in's route), retrieve {sc['routes']['retrieve']} ms; the vector scan {sc['vector_scan_ms']} ms against the budget {n(sc['budget_ms'])} ms; {'`SCALE-PROPOSAL.md` written' if v['scale_proposal'] else 'no `SCALE-PROPOSAL.md`'}.''',
'''- **scale:** lexical {sc['routes']['lexical']} ms, semantic route's reply {sc['routes']['semantic']} ms (recorded as a route time only: {'it answered available' if sc['vector_scan_ms'] is not None else 'an unavailable answer, no scan ran'}), retrieve {sc['routes']['retrieve']} ms; {scan_text(sc)}; {'`SCALE-PROPOSAL.md` written' if v['scale_proposal'] else 'no `SCALE-PROPOSAL.md`'}.
- **installed by A9's copy step:** {v['installed']['count']} files (the retrieval and discovery skills, T-0, T-8{', and Gov OS\\'s `retrieval.yaml`' if v['installed']['retrieval_yaml'] else ''}), kept: {len(v['installed']['kept'])} (the repository's own `retrieval.yaml`); the standard's departures: {len(v['standard']['departures'])}.''')
s = s.replace('''def section(name, v):''', '''def scan_text(sc):
    if sc["vector_scan_ms"] is None:
        return (f"**no vector scan was measured** (`vector_scan_ms` null; reason: {sc.get('vector_scan_reason')}): the "
                f"budget of {n(sc['budget_ms'])} ms was compared with no scan, so this run says nothing of whether a scan "
                "is under it")
    return f"the vector scan {sc['vector_scan_ms']} ms against the budget {n(sc['budget_ms'])} ms"


def section(name, v):''')
s = s.replace('''embedded`, `memory_class: governance`) and Gov OS's shipped `retrieval.yaml` committed, then A0, A1, A2, MA, A3''',
'''embedded`, `memory_class: governance`) committed (**no hand copy of `retrieval.yaml` any more**: A9's copy step installs
Gov OS's as shipped, B-1.3, and the standard is judged on that copy), then A0, A1, A2, MA, A3''')
s = s.replace('''a hash of each chunk, written as the real stage writes them; there is no embedder manifest, so the semantic route
answers unavailable and retrieval is the keyword and code routes. The measure below is therefore not a measure of the
standard.''', '''a hash of each chunk, written as the real stage writes them; there is no embedder manifest, so the semantic route
answers unavailable (`available: false`) and **no vector scan was measured on any of the five repositories**: each
section's `vector_scan_ms` is null with the route's reason, and the budget was compared with no scan (RV1-7; the figure
the first run of this proof gave as a scan time was an unavailable route's reply and was never a scan). Retrieval is
the keyword and code routes; the measure below is therefore not a measure of the standard.''')
s = s.replace("| success S10 (the standard) | `fabric.read_standard`, `departures`, `settings_of` | built; only the pool has a key `gov.config.loader` accepts (package) |",
"| success S10 (the standard) | `fabric.read_standard`, `departures`, `settings_of`, `check_keys` | built; the pool is the whole shipped block; the reranker, its service and the bundle are the pin's constants, and a `retrieval.yaml` with `rerank:` or `bundle:` is `CONFIG_INVALID` |")
s = s.replace("| success S12 to S14, S16, S17 | not this ticket's code (the sets are the writer's and checker's; S17 is W2-88a's); S15's copy has no stage today (package P-6) | not built here |",
"| success S12 to S14, S17 | not this ticket's code (the sets are the writer's and checker's; S17 is W2-88a's) | not built here |\n| success S15, S16 (the kernel copy) | `fabric.install`, `undo`; called by `fabric.a9` | built (B-1.1, B-1.3); its own unit tests |")
s = s.replace("| success 5 (scale) | `fabric.scale`, `over`, `proposal` | built; the vector scan is the stand-in's here |",
"| success 5 (scale) | `fabric.scale`, `vector_scan`, `over`, `proposal` | built; no vector scan was measured here (no query embedder): null with its reason |")
open(p, "w").write(s)
