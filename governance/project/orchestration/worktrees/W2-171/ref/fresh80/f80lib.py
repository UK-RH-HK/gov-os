"""The fresh 80's shared parts (FRESH-80-1 §2 items 14 to 20, §3.4, §3.5, §4.3; DEC-1097 (1)).

Every fresh-80 tool takes the sets root (``--sets-root ~/gov-os-eval``) and derives, here and only here, the set's
folder (``<root>/fixtures/evaluation/memory-verdict-2/hidden``) and the run folder (``<root>/runs/fresh-80``), so no
command line the CTO types names a hidden folder. ``say`` is the only way a tool prints: it refuses a line that names
the sets root's hidden folders or the run folder, and the tools never pass it a question, an answer, or a question's
category beside its id.

The reader's instruction, schema, grader, prompt form, attempt cap and A1/A2/A3 cut are E2's, byte for byte
(``e2_parts``: read from ``drafts/d4b/e2_run.py`` by its syntax tree, never retyped; readiness review F6). The file is
pinned by its sha256 (``E2_SHA256``): a changed e2_run.py refuses every reader run.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

HOME = Path.home()
R = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
O = R / ".gov-runtime/scratch/orchestrator"
D4B = O / "drafts/d4b"
HERE = Path(__file__).resolve().parent
PIN = HOME / ".local/share/gov-os/pin-bcea09060ebc"
PINPY = PIN / "bin/python"
CLONE = HOME / "gov-os-runs/D4B/w4-e0/repo"  # E0's clone (FRESH-80-1 §2 item 10)
GOV = str(HOME / ".local/bin/gov")
CLAUDE = str(HOME / ".local/bin/claude")
COMMIT = "c00d525fd4200303f4ad0fcc7e013d49e60dc2a6"  # window 4, the pool on (DEC-1097 (1)(b))
SET, PART = "memory-verdict-2", "hidden"
EVALUATION = "fixtures/evaluation"
APART_CATEGORY = "nonexistent-id"  # ACT-MSET-3 §2: scored apart (DEC-1071 (5), DEC-1078 (1))
FAMILIES = "families: contract (4 members), kernel (3 members), agents (2 members)"  # item 5
DEC1078_CLOSE = "2026-11-05T18:44:26+00:00"  # the commit that recorded DEC-1078 (83db7540)
CONTROL_WANT, CONTROL_SPREAD = 34, 2  # item 11: the visible 40 at E0's 34 within 2
E2_SHA256 = "f0099fd67ef0cb6d9f6f296a86dc4893a1fe15f3110e30074397d7cbcab9d60a"  # drafts/d4b/e2_run.py as run on the 138
E2G_SHA256 = "35e7a4e549b2a16fd52a46c2aed1d16d736e794fe4a93e02a885b6bc1c4de5fd"
E3_SHA256 = "95718dbc6986a4adc264097c45fe519557968eb8730123dfdb8c1699e5effed0"
UNRESOLVED_IDS = "UNRESOLVED_IDS"  # gov.closure.UNRESOLVED_ALONE
HOLD_FILE = O / "log/act-in-progress.txt"
HOLD_MARK = "FRESH-80 HOLD"


# ---- paths, derived from the sets root only

def paths(sets_root) -> dict:
    root = Path(os.path.expanduser(str(sets_root))).resolve()
    runs = root / "runs" / "fresh-80"
    return {"root": root, "set": root / EVALUATION / SET / PART, "runs": runs, "used": runs / "USED",
            "counts": runs / "COUNTS", "preflight": runs / "preflight.json", "reader": runs / "reader",
            "data": runs / "data"}


def attempt_dir(sets_root, n: int) -> Path:
    return paths(sets_root)["runs"] / f"attempt-{n}"


def counting_attempt(sets_root) -> Path:
    """The attempt whose figures count (COUNTS, written by run_measure.sh when an attempt ends clean)."""
    p = paths(sets_root)
    try:
        name = p["counts"].read_text().strip()
    except OSError:
        raise SystemExit("REFUSED: no attempt of the measure counts yet (run_measure.sh has not ended clean)")
    if not re.fullmatch(r"attempt-[12]", name) or not (p["runs"] / name / "DONE").is_file():
        raise SystemExit("REFUSED: the counting attempt is not a finished attempt")
    return p["runs"] / name


# ---- printing: ids and counts only, never a hidden path

_HIDDEN_TOKENS = ("memory-verdict-2/", "fresh-80/", "runs/fresh-80", EVALUATION + "/" + SET)
_ROOTS: list[str] = []


def guard_root(sets_root) -> None:
    """Remember the sets root so ``say`` refuses any line naming a folder inside it."""
    r = str(paths(sets_root)["root"])
    if r not in _ROOTS:
        _ROOTS.append(r)


def forbidden(line: str) -> bool:
    if any(t in line for t in _HIDDEN_TOKENS):
        return True
    return any(r + os.sep in line for r in _ROOTS)


def say(*parts) -> None:
    line = " ".join(str(p) for p in parts)
    if forbidden(line):
        print("REFUSED: a line that names a hidden folder was not printed", flush=True)
        raise SystemExit(3)
    print(line, flush=True)


# ---- E2's prompt, schema, grader and cut, byte for byte (F6)

E2_NAMES = ("READER_SYS", "READER_SCHEMA", "GRADER_SYS", "GRADER_SCHEMA")
E2_FUNCS = ("prompt_of", "outcome", "mcnemar", "items_of")


def _parts_of(path: Path, names, funcs, want_sha=None) -> dict:
    src = path.read_bytes()
    if want_sha and hashlib.sha256(src).hexdigest() != want_sha:
        raise SystemExit(f"REFUSED: {path.name} is not the file run on the 138 (its sha256 changed)")
    tree = ast.parse(src.decode())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id in names:
                out[t.id] = ast.literal_eval(node.value)
            elif isinstance(t, ast.Tuple) and any(isinstance(e, ast.Name) and e.id in names for e in t.elts):
                vals = ast.literal_eval(node.value)
                for e, v in zip(t.elts, vals):
                    if isinstance(e, ast.Name) and e.id in names:
                        out[e.id] = v
        elif isinstance(node, ast.FunctionDef) and node.name in funcs:
            ns = {"math": math}
            exec(compile(ast.Module([node], []), path.name, "exec"), ns)
            out[node.name] = ns[node.name]
    missing = [n for n in (*names, *funcs) if n not in out]
    if missing:
        raise SystemExit(f"REFUSED: {path.name} lacks {missing}")
    return out


def e2_parts(path: Path = D4B / "e2_run.py", check: bool = True) -> dict:
    return _parts_of(path, (*E2_NAMES, "CAP"), E2_FUNCS, E2_SHA256 if check else None)


def e2g_parts(path: Path = D4B / "e2g_run.py", check: bool = True) -> dict:
    return _parts_of(path, ("REFINE_SYS", "REFINE_SCHEMA"), (), E2G_SHA256 if check else None)


def e3_parts(path: Path = D4B / "e3_run.py", check: bool = True) -> dict:
    return _parts_of(path, ("UNRANKED_NOTE", "READER_SYS"), ("prompt_of", "right"), E3_SHA256 if check else None)


# ---- the questions, by the measure's own loader at the measured commit

def measured_refusal(sets_root) -> None:
    """The measure's own rule (DEC-820 (d)): a session the set measures is refused its hidden part."""
    import yaml
    try:
        with open(paths(sets_root)["root"] / "governance/project/path-map.yaml", encoding="utf-8") as f:
            roles = yaml.safe_load(f)["evaluation_sets"][SET]["measures"].get("roles") or []
    except (OSError, KeyError, TypeError, AttributeError, yaml.YAMLError):
        raise SystemExit("REFUSED: the sets root's map does not declare the set with its measures")
    if os.environ.get("GOV_ROLE", "") in roles:
        raise SystemExit("REFUSED: the set measures this session: its hidden part is refused (DEC-820 (d))")


def load(sets_root, clone=CLONE) -> list[dict]:
    """The 80 as the measure loads them (``gov.retrieval.measure._load``: re-anchored at the clone, families), with
    the gold answer and the category kept inside the tool, never printed."""
    import yaml
    from gov.retrieval import measure as M
    measured_refusal(sets_root)
    p = paths(sets_root)
    entry = M.evaluation_sets(str(p["root"])).get(SET)
    quoting = M._Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{M.EVALUATION}/**"], "")
    declared = M.families(p["root"], Path(clone))
    cache, out = {}, []
    for f in sorted(p["set"].glob("*.yaml")):
        q = M._load(f, PART, Path(clone), quoting, declared, cache)
        raw = yaml.safe_load(f.read_text(encoding="utf-8"))
        q.update(gold=raw.get("gold_answer"), category=raw.get("category"),
                 apart=raw.get("category") == APART_CATEGORY)
        out.append(q)
    return out


def first_calls(measure_txt: Path) -> dict:
    """{id: (first call number, calls)} from a measure's text output (calls are numbered in question order)."""
    starts, n = {}, 1
    for line in Path(measure_txt).read_text().splitlines():
        m = re.match(r"(\S+) \((\w+)\):.*?; (\d+) calls?(?:;|$)", line)
        if m:
            starts[m[1]] = (n, int(m[3]))
            n += int(m[3])
    return starts


def kept_doc(kept: Path, n: int) -> dict:
    return json.loads((Path(kept) / f"{n:05d}.json").read_text())


def text_of(clone: Path, path: str, a: int, b: int) -> str:
    try:
        lines = (Path(clone) / path).read_text(errors="replace").splitlines(keepends=True)
    except OSError:
        return ""
    return "".join(lines[max(0, a - 1):b])


def hit(item, q) -> bool:
    from gov.retrieval import measure as M
    return any(M._match(item, e) for e in q["sources"])


def ids_named(question: str) -> list[str]:
    from gov.retrieval import lexical
    return lexical.ids_in(question)


def gap_names_ids(result: dict, question: str) -> bool:
    """DEC-1071 (5): the product stopped with UNRESOLVED_IDS, its gaps naming every id the question names."""
    if (result or {}).get("stopping_reason") != UNRESOLVED_IDS:
        return False
    named = set(ids_named(question))
    gaps = {g.get("id") for g in (result.get("gaps") or []) if isinstance(g, dict)}
    return bool(named) and named <= gaps


# ---- model calls: E2's call, run once more when it returned nothing (§3.5), every cost in a ledger

class Ledger:
    """The run's spend, kept in <run>/spend.jsonl (one line per call), so a resumed run starts from what was spent."""

    def __init__(self, folder: Path):
        self.path = Path(folder) / "spend.jsonl"
        self.lock = threading.Lock()
        self.total = 0.0
        if self.path.is_file():
            for line in self.path.read_text().splitlines():
                try:
                    self.total += float(json.loads(line).get("usd") or 0)
                except ValueError:
                    pass

    def add(self, usd: float, what: str) -> None:
        with self.lock:
            self.total += usd or 0
            with open(self.path, "a") as f:
                f.write(json.dumps({"usd": usd or 0, "what": what, "at": time.time()}) + "\n")


class Brake:
    """DEC-1091 (2): no new question starts once the measured spend passes twice the projection."""

    def __init__(self, projection: float, ledger: Ledger):
        self.projection, self.limit, self.ledger, self.reason = projection, 2 * projection, ledger, None

    def passed(self) -> bool:
        if self.ledger.total > self.limit:
            self.reason = self.reason or (f"the runaway brake: spend {self.ledger.total:.2f} USD passed "
                                          f"{self.limit:.2f} (twice the projection)")
            return True
        return False


def _run_claude(argv: list[str], prompt: str, cwd) -> str:  # the one seam the tests replace
    return subprocess.run(argv, input=prompt, capture_output=True, text=True, cwd=cwd).stdout


def claude_once(model, system, schema, prompt, budget, cwd, ledger: Ledger, what: str):
    """e2_run.py's claude(), its spend into the ledger."""
    t = time.monotonic()
    stdout = _run_claude([CLAUDE, "-p", "--safe-mode", "--tools", "", "--no-session-persistence", "--output-format",
                          "json", "--model", model, "--effort", "high", "--max-budget-usd", str(budget),
                          "--system-prompt", system, "--json-schema", json.dumps(schema)], prompt, cwd)
    wall = round(time.monotonic() - t, 1)
    try:
        d = json.loads(stdout)
    except ValueError:
        return {"error": "unparsed output", "wall_s": wall}, None
    out = d.get("structured_output")
    if out is None:
        try:
            out = json.loads(d.get("result") or "")
        except ValueError:
            out = None
    u = d.get("usage") or {}
    cost = d.get("total_cost_usd") or 0
    ledger.add(cost, what)
    return {"wall_s": wall, "cost_usd": cost, "is_error": d.get("is_error"),
            "tokens": {k: u.get(k) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
                                             "output_tokens")}}, out


def claude(model, system, schema, prompt, budget, cwd, ledger: Ledger, what: str):
    """One call; a call that returned nothing is run once more (FRESH-80-1 §3.5), never a third time."""
    meta, out = claude_once(model, system, schema, prompt, budget, cwd, ledger, what)
    if out is None:
        meta2, out = claude_once(model, system, schema, prompt, budget, cwd, ledger, what + " (again)")
        meta = {**meta2, "retried": True, "first_error": meta.get("error") or "no structured output",
                "cost_usd": (meta.get("cost_usd") or 0) + (meta2.get("cost_usd") or 0)}
    return meta, out


# ---- searches: a failure is counted, never silent (item 17)

def degraded(result) -> str | None:
    """Why a retrieval was not answered as the judged condition declares, or None (code review F1): no bundle; a route
    (lexical or semantic) missing or not available; a non-empty bundle not reranked by the shared service
    (``rerank.by`` other than ``service``: a private worker or ``unavailable``); the pool's rerank fallen back. The
    empty UNRESOLVED_IDS bundle (the stated gap, which carries no rerank) is no degradation."""
    if not isinstance(result, dict) or not isinstance(result.get("evidence"), list):
        return "no bundle"
    if result.get("stopping_reason") == UNRESOLVED_IDS and not result["evidence"]:
        return None
    facets = result.get("facets") if isinstance(result.get("facets"), dict) else {}
    for route in ("lexical", "semantic"):
        f = facets.get(route)
        if not isinstance(f, dict):
            return f"route {route} missing"
        if not f.get("available"):
            return f"route {route} unavailable"
    if result["evidence"]:
        by = (result.get("rerank") or {}).get("by") if isinstance(result.get("rerank"), dict) else None
        if by != "service":
            return f"reranker {by}"
    if isinstance(result.get("pool"), dict) and result["pool"].get("fallback"):
        return "pool fallback"
    return None


def rerank_by(result) -> str | None:
    r = (result or {}).get("rerank")
    return r.get("by") if isinstance(r, dict) else None


def search(words: str, clone: Path, extra=()) -> tuple[dict, bool, str | None, str | None]:
    """``gov retrieve <words> --json`` on the clone: (result, ok, why, rerank.by). A failure, or a degraded answer
    (``degraded``: code review F1), gives an empty result, as E2's search() gave on a failure, and ok False so it is
    counted (item 17)."""
    env = {k: v for k, v in os.environ.items() if k not in ("GOV_STORE", "GOV_TICKET", "PYTHONPATH")}
    env["GOV_ROLE"] = "orchestrator"  # as the measure ran (e0_run.sh)
    p = subprocess.run([GOV, "retrieve", words, "--json", *extra], capture_output=True, text=True, cwd=clone, env=env)
    try:
        doc = json.loads(p.stdout)
        result = doc["result"]
        if not isinstance(result, dict) or not isinstance(result.get("evidence"), list):
            raise TypeError
    except (ValueError, KeyError, TypeError):
        return {}, False, f"exit {p.returncode}; no bundle in the output", None
    if p.returncode != 0 or doc.get("ok") is False:
        return {}, False, f"exit {p.returncode}; ok {doc.get('ok')}", None
    why = degraded(result)
    if why:
        return {}, False, why, rerank_by(result)
    return result, True, None, rerank_by(result)


def outside_citations(cites, bundles) -> list:
    """The cited ranges that overlap no item the reader received (item 18)."""
    got = [it for b in bundles for it in b]
    return [c for c in cites if not any(p == c[0] and s <= c[2] and c[1] <= e for p, s, e, *_ in got)]


def write_row(folder: Path, name: str, row: dict) -> None:
    """Written whole or not at all, so a resume never takes a half-written row for a finished question."""
    tmp = Path(folder) / f".{name}.tmp"
    tmp.write_text(json.dumps(row, indent=1))
    os.replace(tmp, Path(folder) / name)


PIN_FILE = HERE / "FRESH80-REVIEWED.sha256"


def pinned() -> bool:
    """The fresh-80 files as reviewed (READY), pinned by sha256 after the review, as E0b's harness was (item 19)."""
    try:
        lines = [x.split() for x in PIN_FILE.read_text().splitlines() if x.strip()]
    except OSError:
        return False
    if not lines:
        return False
    for digest, name in lines:
        try:
            if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
                return False
        except OSError:
            return False
    return True


def set_digest(sets_root) -> str:
    """The 80's combined digest: ``LC_ALL=C sha256sum *.yaml | sha256sum`` in the set's folder (item 1)."""
    files = sorted(paths(sets_root)["set"].glob("*.yaml"), key=lambda f: f.name.encode())
    lines = "".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n" for f in files)
    return hashlib.sha256(lines.encode()).hexdigest()


ACT_GLOBS = ("runs/fresh-80/**", "fixtures/evaluation/memory-verdict-2/**")


def act_applied(sets_root, main: Path | None = None) -> tuple[bool, str]:
    """ACT-GUARD-SETS-1 applied (readiness-7 F1), judged by content, never by hash (the ACT is rebuilt): the main
    tree's governance/project/path-map.yaml holds a sets_root_hidden block whose root is this sets root, whose hidden
    globs hold runs/fresh-80/** and fixtures/evaluation/memory-verdict-2/**, and whose refused roles hold the
    orchestrator; and the live .claude/hooks/pretooluse.py holds the sets-root rule (sets_root_rule, sets_root_hidden)."""
    import yaml
    main = Path(main or R)
    try:
        block = yaml.safe_load((main / "governance/project/path-map.yaml").read_text(encoding="utf-8")).get(
            "sets_root_hidden")
    except (OSError, AttributeError, yaml.YAMLError):
        return False, "the main tree's path map cannot be read"
    if not isinstance(block, dict):
        return False, "the main tree's path map has no sets_root_hidden block"
    hidden, roles = block.get("hidden") or [], block.get("refused_roles") or []
    root = os.path.realpath(os.path.expanduser(str(block.get("root") or "")))
    if root != str(paths(sets_root)["root"]):
        return False, "the sets_root_hidden block names another sets root"
    names = {ACT_GLOBS[0]: "the run folder's glob", ACT_GLOBS[1]: "the 80's glob"}  # never a hidden path printed
    missing = [names[g] for g in ACT_GLOBS if g not in hidden]
    if missing:
        return False, f"the sets_root_hidden block lacks {' and '.join(missing)}"
    if "orchestrator" not in roles:
        return False, "the sets_root_hidden block does not refuse the orchestrator"
    try:
        hook = (main / ".claude/hooks/pretooluse.py").read_text(encoding="utf-8")
    except OSError:
        return False, "the live guard hook cannot be read"
    if "def sets_root_rule(" not in hook or "sets_root_hidden" not in hook:
        return False, "the live guard hook has no sets-root rule"
    return True, "applied"


def run_tool(name: str, main_fn, argv=None) -> int:
    """A Python tool's frame (readiness-7 F1, F10): ACT-GUARD-SETS-1 checked before anything is written; standard
    error then goes to <run folder>/<name>.err (a traceback may hold a question's text); the CTO sees one line: a
    refusal's text, or the error's class."""
    argv = list(sys.argv[1:] if argv is None else argv)
    root = next((a.split("=", 1)[1] for a in argv if a.startswith("--sets-root=")), None)
    if root is None and "--sets-root" in argv and argv.index("--sets-root") + 1 < len(argv):
        root = argv[argv.index("--sets-root") + 1]
    if root is None:
        return main_fn(argv)  # argparse's own refusal: no set opened
    guard_root(root)
    ok, why = act_applied(root)
    if not ok:
        say(f"REFUSED: ACT-GUARD-SETS-1 is not applied ({why}): nothing is written (DEC-1097 (2))")
        return 2
    runs = paths(root)["runs"]
    runs.mkdir(parents=True, exist_ok=True)
    os.chmod(runs, 0o700)
    old = sys.stderr
    with open(runs / f"{name}.err", "a") as err:
        sys.stderr = err
        try:
            return main_fn(argv)
        except SystemExit as e:
            if isinstance(e.code, str):
                say(e.code)
                return 2
            return e.code or 0
        except Exception as e:  # noqa: BLE001: the class to the CTO, the traceback to the run folder
            import traceback
            traceback.print_exc(file=err)
            say(f"ERROR: {type(e).__name__} (its traceback is in the run folder's {name}.err)")
            return 1
        finally:
            sys.stderr = old


def hold_on() -> bool:
    try:
        return HOLD_MARK in HOLD_FILE.read_text()
    except OSError:
        return False


# ---- the bar (§4.3) and the exact interval

def bar(right: int, wrong: int, n: int) -> dict:
    """K9 (DEC-1097 (1)(d)): right >= 85 % and wrong claims <= 5 % on the observed figure; target 95 %."""
    need = -(-85 * n // 100)
    cap = 5 * n // 100
    target = -(-95 * n // 100)
    return {"n": n, "right": right, "wrong": wrong, "need_right": need, "max_wrong": cap, "target_right": target,
            "right_ok": 100 * right >= 85 * n, "wrong_ok": 100 * wrong <= 5 * n, "target_ok": 100 * right >= 95 * n,
            "passes": 100 * right >= 85 * n and 100 * wrong <= 5 * n}


def _tail_ge(x, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(x, n + 1))


def _tail_le(x, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(0, x + 1))


def exact_interval(x: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Clopper-Pearson, by bisection on the binomial tails."""
    a = (1 - level) / 2
    if n == 0:
        return 0.0, 1.0

    def solve(f, rising):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if (f(mid) < a) == rising:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if x == 0 else solve(lambda p: _tail_ge(x, n, p), True)
    upper = 1.0 if x == n else solve(lambda p: _tail_le(x, n, p), False)
    return lower, upper


def wilson_interval(x: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson's score interval: FRESH-80-1 §4.3's example (70 of 79: 79.7 to 93.9 %) is this one, not the exact."""
    if n == 0:
        return 0.0, 1.0
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def pct(x, n) -> str:
    return f"{100 * x / n:.1f} %" if n else "-"
