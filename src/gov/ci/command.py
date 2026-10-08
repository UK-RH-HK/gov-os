"""``gov ci`` (W1-40, CAP-39.a): the gates ``lefthook.yml`` and the CI workflow name.

``gov ci checks <tier>...`` runs the declared checks of the tiers named (the ``tier`` field of a declaration,
DEC-186) and refuses when a hard-block check among them is RED. ``gov ci staged-secrets`` runs gitleaks over what
is staged, twice: with the project's ``.gitleaks.toml`` as it stands, then with the project's rules alone
(DEC-347, DEC-369). A result is measured or it is refused: a named tier with no declared check, a name that is no
tier, a gitleaks that cannot run or does not decide, and rules that cannot be read all refuse.

``gov ci job`` is the gate of the CI job (DEC-087, DEC-489): every check ``gov check`` runs but the declared
checks of a tier above G2, so the checks of ``gov check`` that carry no tier (openspec, skill version, readiness,
the policy keys) run there, the one place left for them. It refuses as ``gov ci checks G1 G2`` does, and beside
that (DEC-497): a check that reports its tool absent (``TOOL_ABSENT``) is named as unmeasured and refused, whatever
its status, and a declared check of a family ``gov check`` does not know is refused as ``gov check`` refuses it.

``gov ci push <remote>`` is the pre-push gate (DEC-489): it runs the declared checks of tier G3, writes the
evidence record, a git note on the head commit under ``refs/notes/gov-evidence``, and pushes that ref to
``<remote>``. The note is JSON: ``{"commit": <id>, "result": "passed" | "failed" | "no G3 check declared",
"checks": {<check id>: <status>}}``. ``gov ci record`` is what the CI job runs after fetching the ref: it refuses
unless the note of the head commit is there, names that commit and holds an accepted result. It prints the
record: for one that says "no G3 check declared" those words are its report, and it does not refuse (DEC-497).
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from gov.cli.errors import GovError

CLASS = "read"
HELP = "the gates of the lefthook hooks and the CI job: checks by tier, staged secrets, the evidence record"
EXIT_CODES = {3: "refused: a hard-block check failed, or a secret is staged"}
NOT_MEASURED = "CI_NOT_MEASURED"
_LEAKS = 3
TIERS = ("G0", "G1", "G2", "G3", "G4", "G5", "G6")  # CAP-39
JOB_TIERS, JOB_NEVER = ("G1", "G2"), TIERS[3:]  # the job: G1 and G2 must have a check; none above G2 runs there
EVIDENCE_REF = "refs/notes/gov-evidence"
PASSED, FAILED, NO_G3 = "passed", "failed", "no G3 check declared"
# The results the CI job accepts (DEC-497): a record that says NO_G3 is printed in those words and not refused.
ACCEPTED = (PASSED, NO_G3)
# The finding code by which a check of `gov check` says its tool is not there -> the tool, as the sources emit
# them: gov.check.runner._check_openspec, gov.adapters.portability._version_finding. Never read from a message.
TOOL_ABSENT = {"OPENSPEC_ABSENT": "openspec", "RULESYNC_ABSENT": "rulesync"}


def add_arguments(parser) -> None:
    parser.add_argument("gate", choices=("checks", "job", "staged-secrets", "push", "record"))
    parser.add_argument("tiers", nargs="*", metavar="<name>",
                        help="for checks: the tiers to run (G1 G2); for push: the remote")


def _checks(root: Path, tiers: list[str], job: bool = False) -> dict:
    from gov.check import runner
    from gov.cli.checks import load_declarations

    unknown = [tier for tier in tiers if tier not in TIERS]
    if unknown or not tiers:
        raise GovError("CI_TIER_UNKNOWN", f"not a tier ({', '.join(TIERS)}): {' '.join(unknown) or '(none named)'}")
    every = load_declarations(root)
    # the job: every declared check but those of a tier above G2; a hook: the declared checks of the tiers named
    declarations = [each for each in every if (each["tier"] not in JOB_NEVER if job else each["tier"] in tiers)]
    missing = [tier for tier in tiers if tier not in {each["tier"] for each in declarations}]
    if missing:  # a named tier is run or the gate refuses: it is never passed over beside one that has a check
        raise GovError(NOT_MEASURED, f"no check of tier {' or '.join(missing)} is declared", {"tiers": missing})
    runner._augment_declarations(declarations, root)
    commit = runner._head(root)
    results = [runner._run_declared_check(each, root, commit) for each in declarations]
    if job:  # the checks of `gov check` that carry no tier, as runner.run_checks runs them
        results += [runner._check_openspec(root, commit), runner._check_skill_version(root, commit),
                    runner._check_readiness(root, commit)]
        known = {runner._normalise_family(family) for family in runner.FAMILIES}
        families = set(runner.FAMILIES) | {each["family"] for each in every
                                           if runner._normalise_family(each["family"]) not in known}
        results += runner._check_policy_enforcement(root, commit, families)
    statuses = {each["id"]: each["status"] for each in results}
    red = sorted({each["id"] for each in results if each["status"] == runner.RED})  # by result: two may share an id
    refused = ["hard-block checks failed: " + ", ".join(red)] if red else []
    if job:  # DEC-497: a check whose tool is absent was not measured, whatever its status; an unknown family fails
        absent = sorted({f"{each['id']} ({TOOL_ABSENT[finding['code']]} is not on the runner)"
                         for each in results for finding in each["findings"]
                         if isinstance(finding, dict) and isinstance(finding.get("code"), str)
                         and finding["code"] in TOOL_ABSENT})
        unknown = sorted(families - set(runner.FAMILIES))
        if unknown:
            refused.insert(0, "a declared check is of a family gov check does not know: " + ", ".join(unknown))
        if absent:
            raise GovError(NOT_MEASURED, "; ".join(["unmeasured: " + ", ".join(absent)] + refused),
                           {"checks": statuses})
    if refused:
        raise GovError("CHECK_FAILED", "; ".join(refused), {"checks": statuses}, exit_code=3)
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


def _git(root: Path, *args: str) -> str:
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    except OSError as error:
        raise GovError(NOT_MEASURED, f"git {args[0]} could not run: {error}") from None
    if done.returncode != 0:
        raise GovError(NOT_MEASURED, f"git {' '.join(args[:3])} failed: {done.stderr.strip()}")
    return done.stdout


def _push(root: Path, remotes: list[str]) -> dict:
    from gov.check import runner

    if len(remotes) != 1:
        raise GovError(NOT_MEASURED, "gov ci push takes the one remote that is pushed to")
    record, failure = {"commit": runner._head(root), "result": PASSED, "checks": {}}, None
    try:
        record["checks"] = _checks(root, ["G3"])["checks"]
    except GovError as error:
        if error.code == NOT_MEASURED:  # DEC-489: the push is not refused for that alone, and it is no pass
            record["result"] = NO_G3
        elif error.code == "CHECK_FAILED":
            record.update(result=FAILED, checks=error.details["checks"])
            failure = error
        else:
            raise
    _git(root, "notes", "--ref", EVIDENCE_REF, "add", "-f", "-m", json.dumps(record, indent=2), record["commit"])
    if failure is not None:
        raise failure  # the record that says failed stays here: it is not pushed
    _git(root, "push", "--no-verify", remotes[0], EVIDENCE_REF)  # --no-verify: this push does not start the hook again
    return record


def _record(root: Path) -> dict:
    from gov.check import runner

    commit = runner._head(root)
    note = _git(root, "notes", "--ref", EVIDENCE_REF, "show", commit)
    try:
        record = json.loads(note)
    except ValueError:
        record = None
    if not isinstance(record, dict) or record.get("commit") != commit:
        raise GovError(NOT_MEASURED, f"the evidence record of {commit} cannot be read or is for another commit")
    if record.get("result") not in ACCEPTED:
        raise GovError("EVIDENCE_REFUSED", f"the evidence record of {commit} says: {record.get('result')}")
    return record


def run(root: Path, args, config: dict) -> dict:
    if args.gate == "checks":
        return _checks(root, args.tiers)
    if args.gate == "job":
        if args.tiers:
            raise GovError(NOT_MEASURED, "gov ci job takes no tier: " + " ".join(args.tiers))
        return _checks(root, list(JOB_TIERS), job=True)
    if args.gate == "push":
        return _push(root, args.tiers)
    return _record(root) if args.gate == "record" else _staged_secrets(root)
