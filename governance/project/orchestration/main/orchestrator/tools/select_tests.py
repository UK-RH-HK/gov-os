"""The one test-selection tool for every level (owner, DEC-953 item 4): workers, leads, the close and the nightly.

It runs the product's own selection (gov.close.select.plan, W2-66) unchanged, with two inputs set by DEC-953:
  1. the governance files are left out of the change before tests are chosen (item 4a): briefs, prompts, the
     orchestration record (the nightly's folder included), the record places of the test map's record_only list,
     and .gov-runtime/. They never widen a run to the full suite. No test-map change.
  2. the change is the ticket's own: by default the merge base with w2/integrate (a lead's worktree), or, with
     --merge <commit>, that merge's first parent (the close on the merged code). The nightly runs everything.
  3. DEC-1045 item 2: the tests whose subject is the real gitleaks binary, listed in nightly_only.txt beside this
     file (one place to change), are left out of every selection and named in `left_out_nightly_only`: a target
     inside one is dropped, a target holding one is split into its other parts, and each is added to the
     ignore/deselect lists. They run only in the nightly full suite, which does not use this tool. Since D-4's cut
     (DEC-1061) the list is empty: its entries moved into the opt-in suite `lifted` (tests/optin-lifted.txt).
  4. DEC-1061 item 9, T-7: a test helper listed in helper_exceptions.txt beside this file reaches only the suites
     that import it directly (a plain scan of tests/), not every suite the product's helper rule reaches through
     other helpers; each suite so dropped is named in `helper_exceptions_dropped`. The test map's schema is closed,
     so the list is here, not in the map.
  5. DEC-1061 item 9, T-10: the tree's opt-in suite `lifted` (every tests/optin-lifted*.txt but the *breadth* ones)
     is left out of the selection as the nightly-only list is, named in `left_out_lifted`; the lifted entries the
     change reaches (by the rule that would have selected them) are named in `lifted_reached`, to run report-only
     with `--optin=lifted` (never run by the selection). When nothing is left to run, `nothing_to_run` is true and
     the target list is empty: start no pytest (it would collect nothing and exit 5).

Run with the tree's own src first on PYTHONPATH (DEC-732):
    PYTHONPATH=<tree>/src python3 select_tests.py <tree> <W2 id> <ticket id> [--merge <commit>] [--base <commit>]
Prints one JSON object: scope ("scoped"), core_changed and unplaced (what the product would have run in full for),
base, the governance paths left out, the change that counted, the selected suites with their reasons, and
pytest_options (--ignore/--deselect to add to `pytest tests`). There is no "full" any more (DEC-968): the full suite
runs only in the nightly. Exit 2 with scope "refused" when the selection cannot be made (fix the cause)."""
import argparse
import json
import re
import subprocess
from pathlib import Path

from gov.close import select

GOVERNANCE = [
    "governance/project/briefs/**",
    "governance/project/prompts/**",
    "governance/project/orchestration/**",
    ".gov-runtime/**",
]


NIGHTLY_ONLY = Path(__file__).resolve().parent / "nightly_only.txt"  # DEC-1045 item 2: one place to change
HELPER_EXCEPTIONS = Path(__file__).resolve().parent / "helper_exceptions.txt"  # DEC-1061 item 9, T-7
LIFTED_GLOB = "optin-lifted*.txt"  # the tree's opt-in lists (tests/conftest.py); *breadth* ones are not `lifted`


def nightly_only(path=NIGHTLY_ONLY):
    """The list's entries, [(path or node id, why)], in order; None when the file is absent (nothing left out: more
    runs, never fewer). A line is `<entry>  # <why>`; blank and comment lines are skipped."""
    path = Path(path)
    if not path.is_file():
        return None
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#"):
            continue
        entry, _, why = line.partition("#")
        entry = entry.strip().rstrip("/")
        if entry:
            out.append((entry, why.strip()))
    return out


def helper_exceptions(path=HELPER_EXCEPTIONS):
    """T-7's list (the nightly_only.txt form): [(helper path, why)]; None when the file is absent (the product's
    helper rule unchanged: more runs, never fewer)."""
    return nightly_only(path)


def lifted_lists(root):
    """The tree's `lifted` lists: every tests/optin-lifted*.txt whose name does not hold `breadth` (tests/conftest.py's
    optin_name), sorted."""
    return [p for p in sorted((Path(root) / "tests").glob(LIFTED_GLOB)) if "breadth" not in p.name]


def lifted_entries(root):
    """The `lifted` entries of the tree, [(path or node id, why)] in list order, and the `rep:` lines skipped (a `rep:`
    entry keeps one case of its function in every run, so it never leaves a target out). None when the tree has no
    `lifted` list."""
    lists = lifted_lists(root)
    if not lists:
        return None, []
    out, reps = [], []
    for listing in lists:
        for entry, why in nightly_only(listing) or []:
            if entry.startswith("rep:"):
                reps.append(entry[len("rep:"):].strip())
            else:
                out.append((entry, why))
    return list(dict.fromkeys(out)), reps


def importers(root, helper):
    """The suites (gov.close.select.suite_of) whose files import the helper module directly: a plain scan of tests/
    for `import <module>` or `from <module> import`, the helper's own file left out."""
    root = Path(root)
    mod = re.escape(Path(helper).stem)
    pattern = re.compile(rf"^\s*(?:from\s+{mod}\s+import\b|import\s+(?:[\w.]+\s*,\s*)*{mod}\b)", re.M)
    found = set()
    for path in sorted((root / "tests").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if rel == helper or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if pattern.search(text) and select.suite_of(rel):
            found.add(select.suite_of(rel))
    return found


def narrow_helper_reach(reach, listed, dropped):
    """The product's _helper_reach, with T-7's exceptions: a listed helper stays in a suite's reach only where the
    suite imports it directly. Each (suite, helper) taken out is appended to `dropped`."""
    listed = set(listed)
    cache = {}

    def narrowed(root_, suites, changed_paths):
        out = {}
        for suite, hit in reach(root_, suites, changed_paths).items():
            keep = set()
            for helper in hit:
                if helper in listed:
                    if helper not in cache:
                        cache[helper] = importers(root_, helper)
                    if suite not in cache[helper]:
                        dropped.append({"suite": suite, "helper": helper})
                        continue
                keep.add(helper)
            if keep:
                out[suite] = keep
        return out

    return narrowed


def reached(left_out, selected):
    """The entries a selection's targets would have run, each with the targets and the reasons that selected them
    (`lifted_reached`): [{entry, targets, selected_by}] in order."""
    why_of = {s["target"]: s["why"] for s in selected}
    out = {}
    for d in left_out:
        item = out.setdefault(d["entry"], {"entry": d["entry"], "targets": [], "selected_by": []})
        if d["target"] not in item["targets"]:
            item["targets"].append(d["target"])
        for w in why_of.get(d["target"], []):
            if w.get("reason") and not w["reason"].endswith("_SPLIT") and w["reason"] not in item["selected_by"]:
                item["selected_by"].append(w["reason"])
    return list(out.values())


def _is_test(path: Path) -> bool:  # pytest's default python_files: test_*.py and *_test.py
    return path.suffix == ".py" and (path.name.startswith("test_") or path.stem.endswith("_test"))


def _test_names(path: Path):
    """The top-level tests of a test file (the product's own reading, gov.close.select)."""
    return select._top_level_tests(path)


def leave_out_nightly(root: Path, selected, entries, split_reason="NIGHTLY_ONLY_SPLIT"):
    """Take the nightly-only entries out of a selection (DEC-1045 item 2). A selected target that lies inside an entry
    is dropped; one that holds an entry is split into its parts without it (a folder into its children, a file into
    its other top-level tests), so the targets alone (a batch's run) leave it out too; and every entry present in the
    tree is added to the ignore (a file) or deselect (a node id) list, for the `pytest tests` form. Returns a dict:
    selected, ignore, deselect, left_out ([{entry, why, target}] the selection would have run) and absent (entries
    naming nothing in this tree). The same reading leaves out the opt-in suite `lifted` (split_reason
    "LIFTED_SPLIT", DEC-1061 item 9, T-10)."""
    root = Path(root)
    present = [(e, w) for e, w in entries if (root / e.partition("::")[0]).exists()]
    absent = [e for e, _ in entries if not (root / e.partition("::")[0]).exists()]
    why_of = dict(present)
    names = [e for e, _ in present]

    def inside(t, e):  # t lies inside (or is) the entry e
        return t == e or t.startswith(e + "/") or t.startswith(e + "::") or t.startswith(e + "[")

    def held(t):  # the entries inside target t
        return [e for e in names if e != t and (e.startswith(t + "/") or e.startswith(t + "::"))]

    left_out = []

    def split(t):
        """t's parts without the entries it holds; each entry left out is named."""
        path = root / t.partition("::")[0]
        if "::" in t or not (path.is_dir() or path.is_file()):  # a case's own parts are left to --deselect
            return [t]
        if path.is_file():
            nodes = [e for e in held(t)]
            keep = [n for n in _test_names(path) if f"{t}::{n}" not in nodes]
            return [f"{t}::{n}" for n in keep]
        parts = []
        for child in sorted(path.iterdir()):
            rel = child.relative_to(root).as_posix()
            if child.is_dir():
                if child.name == "__pycache__" or not any(_is_test(f) for f in child.rglob("*.py")):
                    continue
            elif not _is_test(child):
                continue
            hit = next((e for e in names if inside(rel, e)), None)
            if hit:
                continue
            parts.extend(split(rel) if held(rel) else [rel])
        return parts

    out = []
    for item in selected:
        t = item["target"].rstrip("/")
        hit = next((e for e in names if inside(t, e)), None)
        if hit:
            left_out.append({"entry": hit, "why": why_of[hit], "target": item["target"]})
            continue
        inner = held(t)
        if not inner:
            out.append(item)
            continue
        left_out.extend({"entry": e, "why": why_of[e], "target": item["target"]} for e in inner)
        out.extend({"target": p, "why": list(item["why"]) + [{"reason": split_reason, "from": item["target"]}]}
                   for p in split(t))
    seen, uniq = set(), []
    for item in out:
        if item["target"] not in seen:
            seen.add(item["target"])
            uniq.append(item)
    ignore = [e for e in names if "::" not in e]
    deselect = [e for e in names if "::" in e]
    dedup = list({(d["entry"], d["target"]): d for d in left_out}.values())
    return {"selected": uniq, "ignore": ignore, "deselect": deselect, "left_out": dedup, "absent": absent}


def leave_out_lists(root, scope, entries, lifted=None):
    """The nightly-only entries, then the tree's `lifted` entries, taken out of the plan `scope` (changed in place:
    selected, ignore, deselect). `lifted` is (entries, rep lines), read from the tree when None. Returns the fields
    of the output that come from the two lists, with nothing_to_run true when no target is left."""
    # DEC-1045 item 2: the tests whose subject is the real gitleaks binary run only in the nightly; left out here
    night = leave_out_nightly(root, scope.get("selected", []), entries or [])
    scope["selected"] = night["selected"]
    scope["ignore"] = list(dict.fromkeys(scope.get("ignore", []) + night["ignore"]))
    scope["deselect"] = list(dict.fromkeys(scope.get("deselect", []) + night["deselect"]))
    # DEC-1061 item 9, T-10: the opt-in suite `lifted` is left out the same way; what the change reaches of it is
    # named for one report-only run with --optin=lifted, never run here
    lifted, reps = lifted_entries(root) if lifted is None else lifted
    before = scope["selected"]
    lift = leave_out_nightly(root, before, lifted or [], split_reason="LIFTED_SPLIT")
    scope["selected"] = lift["selected"]
    scope["ignore"] = list(dict.fromkeys(scope["ignore"] + lift["ignore"]))
    scope["deselect"] = list(dict.fromkeys(scope["deselect"] + lift["deselect"]))
    reach = reached(lift["left_out"], before)
    return {"nothing_to_run": not scope["selected"],
            "left_out_nightly_only": night["left_out"], "nightly_only_absent": night["absent"],
            "left_out_lifted": lift["left_out"], "lifted_reached": reach,
            "lifted_run": ({"report_only": True, "never_run_by_this_selection": True,
                            "pytest_args": ["--optin=lifted"] + [d["entry"] for d in reach]} if reach else None),
            "lifted_rep_lines_kept": reps, "lifted_absent": lift["absent"]}


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree")
    ap.add_argument("wbs")
    ap.add_argument("ticket")
    ap.add_argument("--merge")
    ap.add_argument("--base")
    ap.add_argument("--integration", default="w2/integrate")
    a = ap.parse_args()
    root = Path(a.tree).resolve()

    merges = [git(root, "rev-parse", m) for m in (a.merge or "").split(",") if m]
    if a.base:
        since = git(root, "rev-parse", a.base)
    elif merges:
        since = git(root, "rev-parse", merges[-1] + "^1")  # the oldest merge's parent
    else:
        since = git(root, "merge-base", "HEAD", a.integration)
    # the change: each merge's own (parent..merge), all of a ticket's merges together; else since..HEAD
    spans = [(m + "^1", m) for m in merges] if merges and not a.base else [(since, "HEAD")]

    test_map, _ = select.load_map(root)
    record_places = list((test_map or {}).get("record_only") or [])
    left_out = []

    def is_governance(path):
        return any(select.match(path, p) for p in GOVERNANCE + record_places)

    def changed(root_, since_):
        # the merges' own change, not everything merged after them; tests still run on HEAD
        paths = set()
        for lo, hi in spans:
            names = select._git(root_, "-c", "core.quotePath=false", "diff", "-z", "--no-renames", "--name-only",
                                lo, hi)
            paths.update(filter(None, names.split("\0")))
        paths = sorted(paths)
        keep = []
        for p in paths:
            (left_out if is_governance(p) else keep).append(p)
        return keep

    select.changed = changed
    select.base = lambda root_: since

    # DEC-968 (owner, 2026-10-31): the full suite runs only in the nightly. No lead, close or merge runs it, core
    # changes included: they run the scoped set, the ticket's own suite and every suite the selection says the change
    # can reach. So the product's two shortcuts to "everything" are taken out here, and only here:
    #   - shared core (SHARED_CORE): a core file reaches what its normal rules reach (the tickets whose paths hold
    #     it, test helpers, couplings), plus the unit tests and the every-close and record-reading suites;
    #   - a file nothing places (UNPLACED): named in `unplaced`, reaching nothing beyond those same suites.
    # Any other reason for "everything" (an unreadable test map, an unknown base, an unresolved target) stops the
    # selection with exit 2: nothing runs blind.
    load_map = select.load_map
    extra_record = []

    def load_map_scoped(root_):
        m, why = load_map(root_)
        if m is not None:
            m = dict(m, shared_core=[], record_only=list(m.get("record_only") or []) + extra_record)
        return m, why

    select.load_map = load_map_scoped
    # DEC-1061 item 9, T-7: a listed helper reaches only the suites that import it directly
    exceptions = helper_exceptions()
    helper_dropped = []
    if exceptions:
        select._helper_reach = narrow_helper_reach(select._helper_reach, [e for e, _ in exceptions], helper_dropped)
    scope = select.plan(root, a.wbs, ticket=a.ticket)
    unplaced = [p for w in scope.get("why_full", []) if w.get("reason") == "UNPLACED" for p in w.get("paths", [])]
    if scope["scope"] == "full" and unplaced:  # place them as reaching nothing beyond the always-run suites
        extra_record.extend(unplaced)
        helper_dropped.clear()
        scope = select.plan(root, a.wbs, ticket=a.ticket)
    if scope["scope"] == "full":
        print(json.dumps({"scope": "refused", "why": scope.get("why_full", []),
                          "note": "DEC-968: no full run outside the nightly; fix the cause"}, indent=1))
        raise SystemExit(2)
    # what the product would have run in full for, kept as evidence
    shared = list((test_map or {}).get("shared_core") or [])
    core = [p for p in scope.get("changed", []) if any(select.match(p, c) for c in shared)]

    # The product's plan leaves the ticket's own acceptance suite out (gov close runs it in a phase of its own); one
    # run at every level must include it, so it is not ignored here (W2-85's finding, 2026-10-30).
    own = next((s["target"] for s in scope.get("selected", []) if any(w.get("reason") == "OWN" for w in s["why"])),
               None)
    keep = {own.rstrip("/")} if own else set()
    scope["ignore"] = [rel for rel in scope.get("ignore", []) if rel.rstrip("/") not in keep]
    entries = nightly_only()
    lists = leave_out_lists(root, scope, entries)
    opts = [f"--ignore={root / rel}" for rel in scope.get("ignore", []) if rel != "tests"]
    for node in scope.get("deselect", []):
        opts.append(f"--deselect={node}")
        if node.startswith("tests/"):
            opts.append(f"--deselect={node[len('tests/'):]}")
    print(json.dumps({"scope": scope["scope"], "why_full": [], "core_changed": core, "unplaced": unplaced,
                      "base": since,
                      "head": scope.get("head"), "governance_left_out": sorted(set(left_out)),
                      "changed": scope.get("changed", []), "selected": scope.get("selected", []),
                      "nothing_to_run": lists["nothing_to_run"],
                      "pytest_options": opts, "ignore": scope.get("ignore", []),
                      "deselect": scope.get("deselect", []), "per_test_timeout": scope.get("per_test_timeout"),
                      "left_out_nightly_only": lists["left_out_nightly_only"],
                      "nightly_only_list": (f"{NIGHTLY_ONLY}: {len(entries)} entries" if entries is not None
                                            else f"absent: {NIGHTLY_ONLY}; nothing left out"),
                      "nightly_only_absent": lists["nightly_only_absent"],
                      "helper_exceptions_list": (f"{HELPER_EXCEPTIONS}: {len(exceptions)} entries"
                                                 if exceptions is not None
                                                 else f"absent: {HELPER_EXCEPTIONS}; the helper rule unchanged"),
                      "helper_exceptions_dropped": helper_dropped,
                      "left_out_lifted": lists["left_out_lifted"],
                      "lifted_reached": lists["lifted_reached"],
                      "lifted_run": lists["lifted_run"],
                      "lifted_lists": [p.relative_to(root).as_posix() for p in lifted_lists(root)],
                      "lifted_rep_lines_kept": lists["lifted_rep_lines_kept"],
                      "lifted_absent": lists["lifted_absent"]}, indent=1))


if __name__ == "__main__":
    main()
