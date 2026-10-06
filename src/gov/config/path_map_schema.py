"""The W1-08 path-map schema (DEC-228), replacing the minimal W1-07 schema.

Validates ``governance/project/path-map.yaml`` against the kernel's schema at
``template/governance/kernel/schemas/path-map.schema.json``.

Required top-level keys: state_class, namespaces, capabilities, policies, systems.
"""

from __future__ import annotations

REQUIRED_TOP_LEVEL = ("state_class", "namespaces", "capabilities", "policies", "systems")

NAMESPACE_FIELDS = (
    "paths", "memory_class", "sensitivity", "permitted_roles", "retention",
    "export_policy", "provenance", "deletion_rebuild",
)

NAMESPACE_OPTIONAL_FIELDS = ("embedding_policy",)

MEMORY_CLASSES = ("governance", "product")

CAPABILITIES = ("code_intelligence", "research_corpus")

POLICY_KEYS = (
    "security", "authority", "test", "change", "human_gate", "tool",
    "memory", "context", "checkpoint",
    "model_routing", "budget", "learning", "archive",
)

HARD_BLOCK_ONLY = ("security", "authority", "test", "change", "human_gate", "tool")
WARNING_OR_STRONGER = ("memory", "context", "checkpoint")
ANY_STRENGTH = ("model_routing", "budget", "learning", "archive")

STRENGTHS = {"informational", "warning", "hard-block"}
WARNING_STRENGTHS = {"warning", "hard-block"}
HARD_BLOCK_STRENGTHS = {"hard-block"}

SYSTEM_KEYS = (
    "constitution-and-policies", "knowledge-fabric", "repository-contract",
    "agent-organisation", "skills", "tools-and-capabilities", "command-surface",
    "model-adapters", "orchestration-and-handoffs", "specification-and-planning",
    "research-and-experiments", "task-system", "product-delivery",
    "verification-and-governance-tests", "change-impact-control",
    "checkpoint-and-recovery", "observability-and-cost", "organisational-learning",
    "independent-audit", "security-and-permissions", "budget-governance",
    "emergency-stop-and-rollback",
)

SYSTEM_STATUSES = ("implemented", "minimal", "absent")

PATH_MAP_SCHEMA = {
    "state_class": {"required": False, "type": str},
    "namespaces": {"required": True, "type": dict, "values": dict},
    "capabilities": {"required": False, "type": dict},
    "policies": {"required": False, "type": dict},
    "systems": {"required": False, "type": dict},
}

W1_08_EXTENDED_KEYS = ("state_class", "capabilities", "policies", "systems")
