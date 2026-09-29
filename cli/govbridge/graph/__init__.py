"""govbridge.graph -- whole-repository dependency/WHY lineage (ARCHITECTURE.md section 6, node B5).

Every edge carries ``derivation in {EXACT_*, HEURISTIC_*}`` and the occurrence/line that justifies it; a heuristic
edge is never rendered without its label (ARCHITECTURE.md section 6.1). The graph returns ``DerivedItem``, never a
``MandatoryItem`` -- section A is filled only by ``govbridge.authority.resolver`` (ARCHITECTURE.md section 5.3).
"""
