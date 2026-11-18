"""The scope of a committed path: which paths a role on a ticket may commit (W1-50; DEC-136, DEC-156, DEC-176,
DEC-359, DEC-728).

What the close's commit check (``gov.containment.commits``) asks of each path a commit holds. It is the write half of
the retired guard's ``decide`` (``gov.guard.decide``, EMERGENCY-2 6.1) for a file path, unchanged: nothing is written
while the freeze flag or its mirror says frozen; an orchestrator's own commit may hold any path; another role's, only
the ``allowed_paths`` of its ticket in progress (the test designer: ``tests/acceptance/**`` only, and no other role an
acceptance test); ``.gov-runtime/`` outside ``scratch/`` is no role's; scratch and the session's own run folder are
every role's. The guard's other rules (held-out paths, secrets, the counterpart's work, the Bash parser) are not
carried: reads are open, and what a session reads is caught afterwards, not prevented (EMERGENCY-2 2.1, 2.7).
"""

from __future__ import annotations

import os
import tempfile

from gov.util import runs
from gov.util.freeze import FreezeLookupUnavailable, _mirror_frozen, freeze_state
from gov.util.patterns import ACCEPTANCE, _is_under_acceptance, _match_pattern
from gov.util.tickets import _load_ticket

KNOWN_ROLES = frozenset({
    "orchestrator", "product-spec", "independent-test-designer",
    "engineer", "independent-auditor",
    "research",  # DEC-163: held to its ticket's allowed_paths, like engineer
    "ticket-lead",  # DEC-434: may write only scratch/checkpoint; no path patterns
    "qa-engineer",  # DEC-959 item 3: held to its own ticket's allowed_paths (its findings report)
})
WRITE_TOOLS = frozenset({"Edit", "Write", "NotebookEdit", "MultiEdit"})
_GOV_RUNTIME = ".gov-runtime"


def _get_allowed_paths(role: str, tid: str | None, root: str,
                       *, session_role: str | None = None) -> list[str]:
    if role == "orchestrator":
        # DEC-156: the wide scope applies only in an orchestrator session.
        # An orchestrator subagent in a non-orchestrator session falls
        # through to the ticket-path rule (DEC-136 batch 3).  A missing
        # session role gives no wide scope (DEC-179).
        if session_role == "orchestrator":
            return ["**"]
        # Fall through: use the ticket's allowed_paths when the ticket's
        # role is orchestrator; otherwise the orchestrator subagent gets
        # nothing beyond the scratch set.
    if role == "ticket-lead":
        return []
    if role not in KNOWN_ROLES or not tid:
        return []
    t = _load_ticket(root, tid)
    if not t or t.get("status") != "in_progress":
        return []
    if role == "independent-test-designer":
        return [ACCEPTANCE + "/**"]
    if t.get("role") != role:
        return []
    return [p for p in t.get("allowed_paths", [])
            if not _is_under_acceptance(p.rstrip("*/ "))]


# -- path helpers --------------------------------------------------------------

def _is_gov_runtime_protected(relpath: str) -> bool:
    """True when *relpath* is under ``.gov-runtime/`` but NOT under ``scratch/``.

    DEC-176: the freeze flag, snapshots, findings and records are denied
    to the orchestrator.  ``scratch/**`` stays writable.
    """
    if relpath != _GOV_RUNTIME and not relpath.startswith(_GOV_RUNTIME + "/"):
        return False
    scratch = _GOV_RUNTIME + "/scratch"
    return relpath != scratch and not relpath.startswith(scratch + "/")


def _is_in_scratch(path: str, root: str) -> bool:
    real = os.path.realpath(path)
    rr = os.path.realpath(root)
    scratch = os.path.join(rr, ".gov-runtime", "scratch")
    if real == scratch or real.startswith(scratch + "/"):
        return True
    tmp = os.path.realpath(tempfile.gettempdir())
    if rr == tmp or rr.startswith(tmp + "/"):
        return False
    return real == tmp or real.startswith(tmp + "/")


def _at_or_under(real: str, rr: str) -> bool:
    return real == rr or real.startswith(rr + "/")


def _path_allowed(path: str, root: str, patterns: list[str], role: str,
                  own: str | None = None) -> bool:
    real = os.path.realpath(path)
    if real == "/dev/null":
        return True
    if role not in KNOWN_ROLES:
        return False
    if role == "independent-test-designer" and not patterns:
        return False
    if _is_in_scratch(real, root):
        return True
    # DEC-728, DEC-743: the session's own folder under ~/gov-os-runs.
    if own is not None and runs.holds(own, real):
        return True
    rr = os.path.realpath(root)
    if not real.startswith(rr + "/") and real != rr:
        return False
    rel = real[len(rr) + 1:]
    if role != "independent-test-designer" and _is_under_acceptance(rel):
        return False
    # DEC-176, DEC-180: .gov-runtime/ other than scratch/** is denied to
    # every role (the freeze flag, snapshots, findings and records), also
    # on a ticket that names it.
    if _is_gov_runtime_protected(rel):
        return False
    return any(_match_pattern(rel, p) for p in patterns)



def decide(tool_name: str, tool_input: dict, project_root: str, role: str | None, ticket_id: str | None,
           subagent_type: str | None = None, cwd: str | None = None, flag: str | None = None) -> tuple[str, str]:
    """``("allow", "")`` or ``("deny", "<reason>")`` for one file path of a commit, as the retired guard decided it for
    the same call: a freeze look-up that cannot be made refuses (DEC-580); else ``Read`` is allowed (reads are open,
    DEC-820) and a write tool's path is judged by the frozen state and the acting role's allowed paths. *flag* is the freeze flag's state when the caller has read it."""
    frozen = (flag or freeze_state(project_root)) == "frozen"
    if not frozen:
        try:
            frozen = _mirror_frozen(project_root, strict=True)
        except FreezeLookupUnavailable as exc:
            return "deny", f"the freeze look-up failed: {exc} (fail closed, DEC-580)"
    if tool_name not in WRITE_TOOLS:
        return "allow", ""
    ps = tool_input.get("notebook_path" if tool_name == "NotebookEdit" else "file_path", "")
    if not isinstance(ps, str) or not ps or "\0" in ps:
        return "deny", f"{tool_name}: no file path"
    if not os.path.isabs(ps):
        ps = os.path.join(cwd or project_root, ps)
    target = os.path.realpath(ps)
    if target == "/dev/null":
        return "allow", ""
    if frozen:
        return "deny", "frozen: all writes denied"
    erole = (role or "").strip()
    if subagent_type is not None and subagent_type not in KNOWN_ROLES:
        return "deny", f"subagent type '{subagent_type}' is not a known role"
    if erole not in KNOWN_ROLES:
        return "deny", f"role '{erole}' is not a known role"
    acting_role = subagent_type if subagent_type is not None else erole
    pats = _get_allowed_paths(acting_role, ticket_id, project_root, session_role=erole)
    # The own folder neither holds the project nor lies in it, so only a target outside the project needs it.
    own = (runs.own_folder(project_root, ticket_id, acting_role)
           if not _at_or_under(target, os.path.realpath(project_root)) else None)
    if not _path_allowed(target, project_root, pats, acting_role, own):
        return "deny", f"{tool_name} to '{target}' denied for role '{acting_role}'"
    return "allow", ""
