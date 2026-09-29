"""govbridge -- a generic, provider/model-replaceable, whole-repository Governance OS self-memory and context
foundation (OC-BR-02). Orchestration support only (OD-P2-10 section 3); not product, not an authority source.

The package's only coupling to its filesystem location is GOV_BRIDGE_DOMAIN, the default path to config/, schemas/
and the rest of the domain files (ARCHITECTURE.md section 13). Everything else is reached relative to it, so the
package can be moved wholesale (promotion, ARCHITECTURE.md section 10) without redesign.
"""
import os

#: default path to release/orchestration/phase-2-context-bridge, resolved from this file's location so the package
#: works from any worktree; override with the GOV_BRIDGE_DOMAIN environment variable.
GOV_BRIDGE_DOMAIN = os.environ.get(
    "GOV_BRIDGE_DOMAIN",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

__version__ = "0.1.0"
