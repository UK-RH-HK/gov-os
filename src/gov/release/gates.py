"""The five gates of a patch release (W2-209, RELEASE-ON-BEHALF "The gates and the cut"; DEC-1223).

They run in the order G0 to G4 and stop at the first red (``GateRefused``, which names the gate): G0 the owner's
standing yes (``governance/project/release-authority.yaml``), G1 the patch rule (``gov.release.patch``), G2 the suite
on the exact commit (a nightly record), G3 the update rehearsal (``gov.release.proving``), G4 the state. A gate fails
closed: a file that cannot be read, a record that is not a map, a check that cannot be made is a red, never a pass.
Nothing here writes to the repository.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import yaml

from gov.release import RELEASES_REL, ReleaseError, patch

AUTHORITY_REL = "governance/project/release-authority.yaml"
CALLER = "orchestrator"
SUITE_TIER = "weekly"
FULL_COMMIT = re.compile(r"[0-9a-fA-F]{40}")


class GateRefused(Exception):
    """A gate is red: ``gate`` (G0 to G4), ``reason`` (a sentence), the failing ``check`` and any ``extra`` details."""

    def __init__(self, gate: str, reason: str, check: str | None = None, **extra):
        super().__init__(f"{gate}: {reason}")
        self.gate, self.reason, self.check, self.extra = gate, reason, check, extra

    @property
    def details(self) -> dict:
        found = {"gate": self.gate, "reason": self.reason}
        if self.check is not None:
            found["check"] = self.check
        found.update(self.extra)
        return found


def _git(root: Path, *args: str, ok: tuple = (0,)) -> subprocess.CompletedProcess:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if done.returncode not in ok:
        raise ReleaseError(f"git {' '.join(args)}: {done.stderr.decode('utf-8', 'replace').strip()}")
    return done


def _text(root: Path, *args: str) -> str:
    return _git(root, *args).stdout.decode("utf-8", "replace")


def head_commit(root: Path) -> str:
    return _text(root, "rev-parse", "--verify", "HEAD^{commit}").strip()


def _decided_by_owner(root: Path, rel: str) -> bool:
    message = _text(root, "log", "-1", "--format=%B", "--", rel)
    return any(value.startswith("owner") for value in patch.trailers(message).get("Decided-by", []))


def g0(root: Path) -> dict:
    """The owner's standing yes: the authority file says ``patch_releases: on``, names a decision, is committed as it
    stands and was last committed with a ``Decided-by: owner...`` trailer. Returns ``{"decision", "bake_hours"}``."""
    path = Path(root) / AUTHORITY_REL
    if not path.is_file():
        raise GateRefused("G0", f"{AUTHORITY_REL} is absent: the owner's standing yes is not on file", "absent")
    try:
        data = path.read_bytes()
        record = yaml.safe_load(data.decode("utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise GateRefused("G0", f"{AUTHORITY_REL} cannot be read: {type(exc).__name__}", "unreadable") from None
    if not isinstance(record, dict):
        raise GateRefused("G0", f"{AUTHORITY_REL} is not a map", "unreadable")
    if not (record.get("patch_releases") is True or record.get("patch_releases") == "on"):
        raise GateRefused("G0", f"patch_releases is not on in {AUTHORITY_REL}: patch releases are off", "off")
    decision = record.get("decision")
    if not isinstance(decision, str) or not decision.strip():
        raise GateRefused("G0", f"{AUTHORITY_REL} names no decision", "decision")
    try:
        committed = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{AUTHORITY_REL}"], capture_output=True)
    except OSError as exc:
        raise GateRefused("G0", f"git cannot be run: {exc}", "uncommitted") from None
    if committed.returncode or committed.stdout != data:
        raise GateRefused("G0", f"{AUTHORITY_REL} is not committed as it stands (uncommitted, untracked or changed)",
                          "uncommitted")
    try:
        owner = _decided_by_owner(Path(root), AUTHORITY_REL)
    except ReleaseError:
        owner = False
    if not owner:
        raise GateRefused("G0", f"the last commit of {AUTHORITY_REL} carries no Decided-by: owner trailer", "trailer")
    return {"decision": decision.strip(), "bake_hours": record.get("bake_hours")}


def g1(root: Path, version: str) -> dict:
    """The patch rule: the result of ``patch.evaluate`` at HEAD when it says patch; refused naming the first failed rule."""
    try:
        result = patch.evaluate(root, version)
    except ReleaseError as exc:
        raise GateRefused("G1", f"the patch rule cannot be read: {exc}") from None
    if result["kind"] != "patch":
        rule = result["failed"][0]
        raise GateRefused("G1", f"{rule} fails: {result['rules'][rule]['detail']}: this is a bigger release, "
                          "which only the owner builds", rule=rule, rules=result["rules"], kind="bigger",
                          failed=result["failed"], **{"from": result["from"], "commit": result["commit"]})
    return result


def g2(root: Path, suite, commit: str) -> dict:
    """The suite on the exact commit: a nightly record, ``scope: full``, ``verdict: green``, ``optin`` naming the weekly
    tier, ``head`` equal to ``commit`` and ``tree`` equal to its tree. Returns the evidence."""
    if not suite:
        raise GateRefused("G2", "no suite record is named (--suite <record file>)", "missing")
    path = Path(suite)
    try:
        raw = path.read_bytes()
        record = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        raise GateRefused("G2", f"the suite record {path.name} cannot be read as JSON", "unreadable") from None
    head = record.get("head") if isinstance(record, dict) else None
    if not isinstance(record, dict) or not isinstance(head, str) or not FULL_COMMIT.fullmatch(head):
        raise GateRefused("G2", f"the suite record {path.name} is not a map with a 40-character commit as its head",
                          "unreadable")
    optin = record.get("optin")
    if record.get("scope") != "full":
        raise GateRefused("G2", f"the suite record {path.name} has scope {record.get('scope')!r}, not 'full'", "scope")
    if record.get("verdict") != "green":
        raise GateRefused("G2", f"the suite record {path.name} is {record.get('verdict')!r}, not green", "verdict")
    if not isinstance(optin, list) or SUITE_TIER not in optin:
        raise GateRefused("G2", f"the suite record {path.name} does not name the {SUITE_TIER} tier in optin", "optin")
    if head.lower() != commit:
        raise GateRefused("G2", f"the suite record {path.name} is for {head[:12]}, not the release commit {commit[:12]}",
                          "head")
    try:
        tree = _text(Path(root), "rev-parse", f"{commit}^{{tree}}").strip()
    except ReleaseError as exc:
        raise GateRefused("G2", f"the tree of {commit[:12]} cannot be read: {exc}", "tree") from None
    if record.get("tree") != tree:
        raise GateRefused("G2", f"the suite record {path.name} is for another tree than {commit[:12]}'s", "tree")
    return {"record": path.name, "head": head.lower(), "tree": tree, "optin": optin, "raw": raw}


def g3(root: Path, commit: str, version: str, rehearse) -> dict:
    """The update rehearsal: ``rehearse(root, commit, version, kept)`` must answer READY. Returns its report."""
    try:
        report = rehearse()
    except Exception as exc:  # a rehearsal that fails to run is not READY
        report = {"verdict": "NOT_READY", "reasons": [f"the rehearsal could not run: {type(exc).__name__}: {exc}"],
                  "repositories": {}}
    if not isinstance(report, dict) or report.get("verdict") != "READY":
        reasons = list(report.get("reasons") or []) if isinstance(report, dict) else []
        raise GateRefused("G3", "the update rehearsal is not READY: " + ("; ".join(map(str, reasons[:5])) or "no reason"),
                          verdict="NOT_READY", reasons=reasons)
    return report


def g4(root: Path, commit: str, version: str, n: str) -> None:
    """The state: a clean tree, ``commit`` contained in ``w2/integrate``, no freeze, no tag or record for ``version``,
    and the previous release's record readable."""
    from gov import release
    from gov.util import freeze

    root = Path(root)
    try:
        dirty = _text(root, "status", "--porcelain", "--untracked-files=all").splitlines()
    except ReleaseError as exc:
        raise GateRefused("G4", f"the tree cannot be read: {exc}", "dirty") from None
    if dirty:
        raise GateRefused("G4", "the tree has uncommitted or untracked changes: "
                          + ", ".join(line[3:] for line in dirty[:10]), "dirty")
    contained = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", commit,
                                f"refs/heads/{release.INTEGRATION_BRANCH}"], capture_output=True)
    if contained.returncode:
        raise GateRefused("G4", f"{commit[:12]} is not a commit of {release.INTEGRATION_BRANCH}", "ancestor")
    try:
        state = freeze.freeze_state(str(root))
    except Exception:  # a flag that cannot be read is a freeze
        state = "frozen"
    if state == "frozen":
        raise GateRefused("G4", "the freeze flag of gov pause is set", "frozen")
    folder = f"{RELEASES_REL}/{version}"
    tag = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet", f"refs/tags/v{version}"],
                         capture_output=True)
    at_c = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{commit}:{folder}"], capture_output=True)
    if tag.returncode == 0 or at_c.returncode == 0 or (root / folder).exists():
        raise GateRefused("G4", f"release {version} exists (a tag v{version} or a record {folder}): a release is "
                          "immutable", "exists")
    try:
        release.verify_at(root, n)
    except ReleaseError as exc:
        raise GateRefused("G4", f"the previous release {n}'s record cannot be read: {exc}", "previous") from None
