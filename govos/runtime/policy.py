"""Canonical policy layer: kernel policies + project overlay overrides + accepted exceptions."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from govos.runtime.schemas import SchemaRegistry
from govos.runtime.util import GovError, deep_get, deep_set, read_yaml, today

POLICY_NAMES = ["AUTHORITY_POLICY", "MEMORY_POLICY", "CHANGE_POLICY", "SECURITY_POLICY", "TOOL_POLICY",
                "MODEL_ROUTING_POLICY", "CONTEXT_POLICY", "HUMAN_GATE_POLICY", "BUDGET_POLICY", "CHECKPOINT_POLICY",
                "TEST_POLICY", "LEARNING_POLICY", "ARCHIVE_POLICY"]
OVERLAY_FILES = ["PROJECT_POLICY.yaml", "REPOSITORY_CONTRACT.yaml", "CAPABILITY_PROFILE.yaml", "TOOL_PERMISSIONS.yaml",
                 "MODEL_ROUTING_OVERRIDES.yaml", "DATA_SENSITIVITY.yaml", "PROJECT_EXCEPTIONS.yaml"]
OVERLAY_SCHEMA = {"PROJECT_POLICY.yaml": "project-policy", "REPOSITORY_CONTRACT.yaml": "repository-contract",
                  "CAPABILITY_PROFILE.yaml": "capability-profile", "TOOL_PERMISSIONS.yaml": "tool-permissions",
                  "MODEL_ROUTING_OVERRIDES.yaml": "model-routing-overrides", "DATA_SENSITIVITY.yaml": "data-sensitivity",
                  "PROJECT_EXCEPTIONS.yaml": "project-exceptions"}


class PolicySet:
    """Effective policies = kernel policy (+ overlay policy_overrides) (+ unexpired accepted exceptions)."""

    def __init__(self, kernel_dir: Path, overlay: dict[str, Any] | None = None, schemas: SchemaRegistry | None = None):
        self.kernel_dir = Path(kernel_dir)
        self.schemas = schemas or SchemaRegistry(self.kernel_dir / "schemas")
        self.raw: dict[str, dict] = {}
        self.effective: dict[str, dict] = {}
        self.applied_overrides: list[dict[str, Any]] = []
        self.problems: list[str] = []
        for name in POLICY_NAMES:
            p = self.kernel_dir / "policies" / f"{name}.yaml"
            if not p.exists():
                self.problems.append(f"kernel policy missing: {name}")
                continue
            try:
                data = read_yaml(p)
            except Exception as e:  # noqa: BLE001
                self.problems.append(f"{name}: unreadable ({e})")
                continue
            errs = self.schemas.errors(f"policy-{name}", data) if (self.schemas.schema_dir / f"policy-{name}.schema.json").exists() else []
            if errs:
                self.problems.append(f"{name}: " + "; ".join(errs[:3]))
            self.raw[name] = data
            self.effective[name] = _deepcopy(data)
        overlay = overlay or {}
        pp = overlay.get("PROJECT_POLICY.yaml") or {}
        for key, value in (pp.get("policy_overrides") or {}).items():
            pol, _, dotted = key.partition(".")
            if pol in self.effective and dotted:
                deep_set(self.effective[pol], dotted, value)
                self.applied_overrides.append({"policy": pol, "key": dotted, "value": value, "source": "PROJECT_POLICY.policy_overrides"})
            else:
                self.problems.append(f"policy override targets unknown policy/key: {key}")
        exc = overlay.get("PROJECT_EXCEPTIONS.yaml") or {}
        for e in exc.get("exceptions") or []:
            if str(e.get("expires", "")) < today():
                self.problems.append(f"expired exception {e.get('id')} still listed")
                continue
            pol = e.get("policy")
            if pol in self.effective:
                deep_set(self.effective[pol], e["key"], e.get("value"))
                self.applied_overrides.append({"policy": pol, "key": e["key"], "value": e.get("value"), "source": e.get("id"), "decision": e.get("decision")})

    def get(self, policy: str, dotted: str | None = None, default: Any = None) -> Any:
        pol = self.effective.get(policy)
        if pol is None:
            return default
        if dotted is None:
            return pol
        return deep_get(pol, dotted, default)

    def __getitem__(self, policy: str) -> dict:
        if policy not in self.effective:
            raise GovError(f"policy not loaded: {policy}", "POLICY_MISSING")
        return self.effective[policy]


def _deepcopy(d):
    import copy
    return copy.deepcopy(d)


def load_overlay(overlay_dir: Path, schemas: SchemaRegistry | None = None, strict: bool = False) -> tuple[dict[str, Any], list[str]]:
    """Load all overlay files; returns (data_by_filename, problems)."""
    data: dict[str, Any] = {}
    problems: list[str] = []
    for fn in OVERLAY_FILES:
        p = overlay_dir / fn
        if not p.exists():
            problems.append(f"overlay file missing: {fn}")
            continue
        try:
            d = read_yaml(p) or {}
        except Exception as e:  # noqa: BLE001
            problems.append(f"{fn}: unreadable ({e})")
            continue
        if schemas is not None:
            errs = schemas.errors(OVERLAY_SCHEMA[fn], d)
            if errs:
                problems.append(f"{fn}: " + "; ".join(errs[:3]))
                if strict:
                    raise GovError(f"{fn} invalid: {errs[:3]}", "OVERLAY_INVALID")
        data[fn] = d
    return data, problems
