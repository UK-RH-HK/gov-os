"""``gov ci`` (W1-40, CAP-39.a): the gates ``lefthook.yml`` names.

``gov ci checks <tier>...`` runs the declared checks of the tiers named (the ``tier`` field of a declaration,
DEC-186) and refuses when a hard-block check among them is RED. ``gov ci staged-secrets`` runs gitleaks over what
is staged, twice: with the project's ``.gitleaks.toml`` as it stands, then with the project's rules alone
(DEC-347, DEC-369). A result is measured or it is refused: no check of the tiers, a gitleaks that cannot run or
does not decide, and rules that cannot be read all refuse.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from gov.cli.errors import GovError

CLASS = "read"
HELP = "the gates of the lefthook hooks: checks by tier, gitleaks over what is staged"
EXIT_CODES = {3: "refused: a hard-block check failed, or a secret is staged"}
NOT_MEASURED = "CI_NOT_MEASURED"
_LEAKS = 3


def add_arguments(parser) -> None:
    parser.add_argument("gate", choices=("checks", "staged-secrets"))
    parser.add_argument("tiers", nargs="*", metavar="<tier>", help="for checks: the tiers to run (G1 G2)")


def _checks(root: Path, tiers: list[str]) -> dict:
    from gov.check import runner
    from gov.cli.checks import load_declarations

    declarations = [each for each in load_declarations(root) if each["tier"] in tiers]
    if not declarations:
        raise GovError(NOT_MEASURED, f"no check of tier {' or '.join(tiers) or '(none named)'} is declared")
    runner._augment_declarations(declarations, root)
    commit = runner._head(root)
    statuses = {each["id"]: runner._run_declared_check(each, root, commit)["status"] for each in declarations}
    red = sorted(check_id for check_id, status in statuses.items() if status == runner.RED)
    if red:
        raise GovError("CHECK_FAILED", "hard-block checks failed: " + ", ".join(red), {"checks": statuses}, exit_code=3)
    return {"tiers": tiers, "checks": statuses}


def _staged_secrets(root: Path) -> dict:
    from gov.secrets import CONFIG_REL, _rules

    scan = ["gitleaks", "git", "--pre-commit", "--staged", "--no-banner", "--redact", "--verbose",
            "--log-level", "error", "--exit-code", str(_LEAKS)]
    # A configuration path in the environment would win over the rules given there.
    env = {key: value for key, value in os.environ.items() if key != "GITLEAKS_CONFIG"}
    try:
        alone = _rules(root)[-1]  # the project's rules without `extend`: gitleaks' built-in allowlist is not in it
        for extra, scan_env in ((["--config", CONFIG_REL], env), ([], env | {"GITLEAKS_CONFIG_TOML": alone})):
            code = subprocess.run(scan + extra, cwd=str(root), env=scan_env).returncode
            if code == _LEAKS:
                raise GovError("SECRET_STAGED", "gitleaks found a secret in what is staged", exit_code=3)
            if code != 0:
                raise GovError(NOT_MEASURED, f"gitleaks did not decide (exit code {code})")
    except (OSError, RuntimeError) as error:
        raise GovError(NOT_MEASURED, f"the staged content could not be scanned: {error}") from None
    return {"scans": 2, "secrets": 0}


def run(root: Path, args, config: dict) -> dict:
    return _checks(root, args.tiers) if args.gate == "checks" else _staged_secrets(root)
