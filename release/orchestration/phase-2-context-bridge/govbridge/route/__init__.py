"""``govbridge.route`` -- deterministic route selection and fusion (ARCHITECTURE.md section 7.2, section 9).

This package owns no persisted table of its own (nothing to register with ``govbridge.core.manifest``): it is a
pure function layer over whatever ``RouteHit``s the caller's ``RouteSet`` supplies (node B6, BR-HO-0008). The real
B2/B3/B4 route adapters are wired to that same contract in I1, without editing anything here.
"""
