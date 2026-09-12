"""Project context: locates governance dirs, loads lock/kernel/overlay/policies/contract lazily."""
from __future__ import annotations

import os
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Any

from govos import CLI_VERSION
from govos.runtime.kernel import KERNEL_MANIFEST, read_manifest
from govos.runtime.lock import read_lock
from govos.runtime.paths import RepositoryContract
from govos.runtime.policy import PolicySet, load_overlay
from govos.runtime.schemas import SchemaRegistry
from govos.runtime.security.secrets import SecretScanner, scanner_from_policies
from govos.runtime.util import GovError, new_session_id

GOVERNANCE = "governance"


def find_root(start: Path | None = None) -> Path | None:
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / GOVERNANCE / "framework.lock").exists():
            return p
    return None


class Project:
    def __init__(self, root: Path, session_id: str | None = None, role: str | None = None):
        self.root = Path(root).resolve()
        self.session_id = session_id or os.environ.get("GOV_SESSION") or new_session_id()
        self.role = role or os.environ.get("GOV_ROLE") or "orchestrator"

    # --- paths ---
    @property
    def governance_dir(self) -> Path:
        return self.root / GOVERNANCE

    @property
    def kernel_dir(self) -> Path:
        return self.governance_dir / "kernel"

    @property
    def overlay_dir(self) -> Path:
        return self.governance_dir / "project"

    @property
    def generated_dir(self) -> Path:
        return self.governance_dir / "generated"

    @property
    def lock_path(self) -> Path:
        return self.governance_dir / "framework.lock"

    @property
    def runtime_dir(self) -> Path:
        return self.root / ".governance-runtime"

    @property
    def spec_dir(self) -> Path:
        return self.root / "spec"

    def is_installed(self) -> bool:
        return self.lock_path.exists() and (self.kernel_dir / KERNEL_MANIFEST).exists()

    def require_installed(self) -> None:
        if not self.is_installed():
            raise GovError(f"No Governance OS installation at {self.root} (run gov init or gov adopt)", "NOT_INSTALLED")

    # --- loaded state ---
    @cached_property
    def lock(self) -> dict[str, Any]:
        return read_lock(self.lock_path)

    @cached_property
    def kernel_manifest(self) -> dict[str, Any]:
        return read_manifest(self.kernel_dir)

    @cached_property
    def schemas(self) -> SchemaRegistry:
        sd = self.kernel_dir / "schemas"
        return SchemaRegistry(sd if sd.exists() else None)

    @cached_property
    def overlay(self) -> dict[str, Any]:
        data, problems = load_overlay(self.overlay_dir, self.schemas)
        self.overlay_problems = problems
        return data

    @cached_property
    def policies(self) -> PolicySet:
        return PolicySet(self.kernel_dir, self.overlay, self.schemas)

    @cached_property
    def contract(self) -> RepositoryContract:
        data = self.overlay.get("REPOSITORY_CONTRACT.yaml")
        if not data:
            raise GovError("REPOSITORY_CONTRACT.yaml missing or invalid", "CONTRACT_MISSING")
        return RepositoryContract(data)

    @cached_property
    def project_policy(self) -> dict[str, Any]:
        return self.overlay.get("PROJECT_POLICY.yaml") or {}

    @cached_property
    def secret_scanner(self) -> SecretScanner:
        return scanner_from_policies(self.policies["SECURITY_POLICY"], self.overlay.get("DATA_SENSITIVITY.yaml"))

    @property
    def project_name(self) -> str:
        return str((self.project_policy.get("project") or {}).get("name", self.root.name))

    @property
    def project_alias(self) -> str:
        return str((self.project_policy.get("project") or {}).get("alias", "project-alias"))

    @property
    def framework_version(self) -> str:
        return str(self.lock.get("version"))

    def invalidate(self) -> None:
        for k in ("lock", "kernel_manifest", "overlay", "policies", "contract", "project_policy", "secret_scanner"):
            self.__dict__.pop(k, None)

    # --- git ---
    def git(self, *args: str, check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=check)

    def git_commit(self) -> str:
        r = self.git("rev-parse", "HEAD")
        return r.stdout.strip() if r.returncode == 0 else "unknown"

    def git_available(self) -> bool:
        return self.git("rev-parse", "--is-inside-work-tree").returncode == 0

    def cli_version(self) -> str:
        return CLI_VERSION
