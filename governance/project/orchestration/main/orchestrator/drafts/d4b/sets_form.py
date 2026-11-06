"""The sets-root form of the CTO's hidden-set tools (DEC-1084; ACT-GUARD-SETS-1 §5 (2a)).

Since ACT-GUARD-SETS-1 the guard refuses the CTO's command lines that name a hidden folder of the sets root. The tools
take the measure's form instead: the sets root, the set and the part, and they build the folder here, in their own
code. A command line then names only the root (`--sets-root ~/gov-os-eval`), a set name and a part.

    --sets-root <root> --set <memory-retrieval|memory-verdict|memory-verdict-2> --part <hidden|visible>

`sets_argv(sys.argv)` gives the tool its argv as the old form had it: each `--set <name> --part <part>` pair is replaced,
where its --set stands, by the folder <root>/fixtures/evaluation/<name>/<part>; --sets-root may stand anywhere, once;
`--opt=value` is taken too. A tool that takes several folders (mset_overlap.py) takes several pairs, in order, mixed
with folder paths as before. With no --set the argv is left as it is (the old form, for the visible half in a tree).

It refuses (exit 2, on stderr) a pair with no root, a root with no pair, an unknown set or part, a --set without its
--part, and a folder that is not there. Its messages name the set and part only, never a path.

The measure's own refusal comes with the form (gov.retrieval.measure._measured, DEC-820 (d)). The guard no longer
sees the hidden folder on the line, so a hidden part is refused here to a session the set measures: GOV_ROLE among the
set's measures.roles in the sets root's own map (governance/project/path-map.yaml, its evaluation_sets). It fails
closed: a hidden part is refused when that map or the set's entry cannot be read, and when the entry names tickets it
measures and GOV_TICKET is set (the measure's ticket rule needs the product's ticket reader; no set names tickets now).
"""
import os
import sys

import yaml

EVALUATION = os.path.join("fixtures", "evaluation")  # gov.retrieval.measure's EVALUATION
SETS_MAP = os.path.join("governance", "project", "path-map.yaml")  # the sets root's own map (the measure reads it)
SETS = ("memory-retrieval", "memory-verdict", "memory-verdict-2")
PARTS = ("hidden", "visible")
KEYS = ("--sets-root", "--set", "--part")


def _stop(why):
    print(f"REFUSED: {why} (the form: --sets-root <root> --set <{'|'.join(SETS)}> --part <{'|'.join(PARTS)}>)",
          file=sys.stderr)
    sys.exit(2)


def _measures_me(root, name):
    """Refuse (exit 2) a set's hidden part to a session the set measures, as the measure does; fail closed."""
    try:
        with open(os.path.join(root, SETS_MAP), encoding="utf-8") as f:
            measures = yaml.safe_load(f)["evaluation_sets"][name]["measures"]
        roles, tickets = measures.get("roles") or [], measures.get("tickets") or []
        if not isinstance(roles, list) or not isinstance(tickets, list):
            raise TypeError
    except (OSError, ValueError, KeyError, TypeError, AttributeError, yaml.YAMLError):
        _stop(f"the sets root's map does not declare the set {name} with its measures; its hidden part is refused")
    if os.environ.get("GOV_ROLE", "") in roles:
        _stop(f"the set {name} measures this session: its hidden part is refused (DEC-820 (d))")
    if tickets and os.environ.get("GOV_TICKET"):
        _stop(f"the set {name} names the tickets it measures, which this form cannot judge: its hidden part is refused")


def sets_argv(argv):
    """argv with each --set/--part pair replaced by its folder (see the module's text); argv as it is without one."""
    out, root, pending, i = [], None, None, 0

    def value(i):
        key, eq, val = argv[i].partition("=")
        if eq:
            return val, i + 1
        if i + 1 >= len(argv):
            _stop(f"{key} needs a value")
        return argv[i + 1], i + 2

    while i < len(argv):
        key = argv[i].partition("=")[0]
        if i == 0 or key not in KEYS:
            out.append(argv[i])
            i += 1
        elif key == "--sets-root":
            if root is not None:
                _stop("--sets-root is given more than once")
            root, i = value(i)
        elif key == "--set":
            if pending is not None:
                _stop("a --set without its --part")
            name, i = value(i)
            if name not in SETS:
                _stop("an unknown set")
            pending = (name, len(out))
            out.append(None)
        else:
            if pending is None:
                _stop("a --part without a --set before it")
            part, i = value(i)
            if part not in PARTS:
                _stop("an unknown part")
            out[pending[1]] = (pending[0], part)
            pending = None
    if pending is not None:
        _stop("a --set without its --part")
    pairs = [k for k, x in enumerate(out) if isinstance(x, tuple)]
    if pairs and not root:
        _stop("--set needs --sets-root")
    if root is not None and not pairs:
        _stop("--sets-root needs --set and --part")
    top = os.path.expanduser(root) if root is not None else ""
    for k in pairs:
        name, part = out[k]
        if part == "hidden":
            _measures_me(top, name)
        folder = os.path.join(top, EVALUATION, name, part)
        if not os.path.isdir(folder):
            _stop(f"the sets root holds no folder for set {name}, part {part}")
        out[k] = folder
    return out
