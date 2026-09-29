"""govbridge.core -- Git object access, canonical view, corpus rules and coverage, content-addressed store,
chunking, exact route, freshness, build manifest and the local telemetry writer (DAG node B1).

Every later layer (lexical, code, semantic, authority, graph, route, compile -- nodes B2-B6) reads this store and
never re-implements Git access, corpus classification or chunk identity. Nothing here special-cases any particular
file name, review or phase (OC-BR-02): corpus scope comes only from the versioned config/corpus-rules.yaml, and the
canonical view comes only from config/canonical-view.yaml.
"""
