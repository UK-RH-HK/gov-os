"""Set-up A's wiring (DEC-1112 (3), DEC-1113): the planted halves, the planted rule scripts, the flows' launches and
the independent oracles of S16, S20 and S22-S28.

Written from the ticket's KPI lines and the five approved briefs' input, output and result sections (the interface is
this folder's README, "Set-up A's wiring"); nothing here imports or reads the script under test. Every place is
planted: the halves under the case's planted runs folder and planted sets root.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import socket
import sys
import threading
from pathlib import Path

import w2_149_support as support

# flow name -> (kind, planted brief name, brief id, the template's flow)
FLOW = {"writer-tuning": ("writer", "sgx1/writer-tuning", "sgx1-writer-tuning", "sgx1-writer-1"),
        "writer-heldout": ("writer", "sgx1/writer-heldout", "sgx1-writer-heldout", "sgx1-writer-2"),
        "labeller": ("labeller", "sgx1/labeller", "sgx1-labeller", "sgx1-labeller-1"),
        "labeller-2": ("labeller", "sgx1/labeller-2", "sgx1-labeller-2", "sgx1-labeller-2"),
        "overlap-auditor": ("auditor", "sgx1/overlap-auditor", "sgx1-overlap-auditor", "sgx1-overlap-auditor")}
SCHEMA = {f: f"sgx1-{f}-result.schema.json" for f in FLOW}
ENTRY_MODEL = {"writer-tuning": "claude-entry-writer-tuning", "writer-heldout": None,
               "labeller": "claude-entry-labeller", "labeller-2": "claude-entry-labeller-2",
               "overlap-auditor": "claude-entry-overlap-auditor"}
KIND_MODEL = {k: f"claude-kind-{k}" for k in support.KINDS}
HALVES = ("tuning", "held-out")
FIELDS = ("id", "role", "agent", "ticket", "wbs", "tool", "input", "cwd", "executable", "strata", "source")
ACTION7 = ("role", "agent", "ticket", "wbs", "tool", "input", "cwd")
LABEL4 = ("label", "rule_class", "clauses", "reason")
MERGED = ("id", "label", "rule_class", "clauses", "reason", "how")
TO_WORDS = ("cases", "round1", "labels", "decisions")
STOPPED_WORDS = ("none", "input-missing", "input-malformed", "decisions-conflict", "forbidden-read-needed",
                 "form-not-writable", "not-sealed")
LABELS = ("allow", "refuse", "ask")
REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
WHAT_CAME_BACK = "MARK-W2149-WHAT-CAME-BACK"
PLANTED_EXTRA = "MARK-W2149-PLANTED-EXTRA"
AIMS_MARK = "MARK-W2149-AIMS-intent"
TICKETS = (("DAEO-aaa1", "W2-901"), ("DAEO-aaa2", "W2-902"), ("DAEO-aaa3", "W2-903"), ("DAEO-zzz9", "W2-999"))
ROLES = ("engineer", "independent-test-designer", "orchestrator", "research")


def jsonl(rows) -> str:
    return "".join(json.dumps(r) + "\n" for r in rows)


def read_jsonl(path) -> list:
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


# -- the planted halves ---------------------------------------------------------------------------------------------

def _tool_input(tool, n):
    if tool == "Bash":
        return {"command": f"ls {REPO}/docs/d{n % 20 + 1:02d}.md"}
    if tool == "Grep":
        return {"pattern": "DEC-820", "path": f"{REPO}/docs"}
    if tool == "Write":
        return {"file_path": f"{REPO}/src/pkg/m{n % 10 + 1:02d}.py", "content": f"SGX1-MARKER-{n}"}
    return {"file_path": f"{REPO}/docs/d{n % 20 + 1:02d}.md"}


def action_lines(half, n):
    """The half's real actions as the corpus holds them: the brief's fields and some the brief never names (the
    session, the call id, what came back, the time), which the staging drops."""
    p = "t" if half == "tuning" else "h"
    out = []
    for i in range(1, n + 1):
        tid, wbs = TICKETS[i % 4]
        tool = ("Read", "Bash", "Write", "Grep")[i % 4]
        out.append({"id": f"{p}-a{i:03d}", "role": ROLES[i % 4], "agent": None if i % 3 else "explore",
                    "ticket": tid, "wbs": wbs, "tool": tool, "input": _tool_input(tool, i), "cwd": REPO,
                    "executable": True, "strata": ["replay", f"s{i % 2}"], "source": "replay-1",
                    "session": f"sess-{p}-{i % 5}", "call_id": f"toolu_{p}{i:04d}", "result": WHAT_CAME_BACK,
                    "t": 1762000000 + i})
    return out


def case_lines(half, n):
    """The half's planted cases as a writer delivers them (the writer's schema, with its session), and one field more."""
    p, src = ("p1", "planted-1") if half == "tuning" else ("p2", "planted-2")
    out = []
    for i in range(1, n + 1):
        cls = (i - 1) % 14 + 1
        tid, wbs = TICKETS[i % 3]
        role = ROLES[i % 2]
        tool = ("Read", "Bash", "Write", "Grep")[i % 4]
        out.append({"id": f"{p}-c{cls}-{i:03d}-{role}", "source": src, "rule_class": str(cls), "role": role,
                    "agent": None, "ticket": tid, "wbs": wbs, "tool": tool, "input": _tool_input(tool, 100 + i),
                    "cwd": REPO, "executable": i % 5 != 0, "strata": ["planted"], "session": src,
                    "note": PLANTED_EXTRA})
    return out


def plant_half(world, half, n_actions=40, n_cases=12, cases=True):
    h = world.half(half)
    support.write_file(h, "corpus/actions.jsonl", jsonl(action_lines(half, n_actions)))
    if cases:
        support.write_file(h, "planted/cases.jsonl", jsonl(case_lines(half, n_cases)))
    return h


def project(line, case=False):
    keys = FIELDS + (("rule_class",) if case else ())
    return {k: line[k] for k in keys if k in line}


def staged(world, half):
    """The half's staged lines (S24): actions then cases, each kept to the brief's fields."""
    h = world.half(half)
    actions = [project(x) for x in read_jsonl(h / "corpus/actions.jsonl")]
    cases = [project(x, case=True) for x in read_jsonl(h / "planted/cases.jsonl")]
    return actions, cases


def declaration_draw(seed_text, tag, ids, modulo):
    """The declaration's rule (§5, amendment A5): the ids whose int(sha256(SEED + tag + id), 16) % modulo == 0."""
    return [i for i in ids if int(hashlib.sha256((seed_text + tag + i).encode("utf-8")).hexdigest(), 16) % modulo == 0]


def overlap(seed_text, lines):
    drawn = set(declaration_draw(seed_text, "overlap", [y["id"] for y in lines], 10))
    return [x for x in lines if x["id"] in drawn]


def labeller_sample(seed_text, ids):
    return declaration_draw(seed_text, "labeller-sample", ids, 20)


# -- the planted rule scripts (S25) ---------------------------------------------------------------------------------

_RULES = '''import hashlib, json, sys
{pre}


def label(i, extra):
    h = int(hashlib.sha256(i.encode("utf-8")).hexdigest(), 16)
    cls = 14 if h % 4 else h % 13 + 1
    return {{"id": i, "label": "allow" if cls == 14 else ("ask" if cls == 13 else "refuse"), "rule_class": cls,
            "clauses": ([] if cls == 14 else ["DEC-820 (4)"]) + extra, "uncertain": h % 9 == 0}}


ids = [json.loads(x)["id"] for x in sys.stdin if x.strip()]
{post}
for i in ids:
    print(json.dumps(label(i, EXTRA)))
'''
RULES_GOOD = _RULES.format(pre="EXTRA = []", post="")
RULES_LOOP = _RULES.format(pre="EXTRA = []", post="while True:\n    pass")
RULES_DROPS_AN_ID = _RULES.format(pre="EXTRA = []", post="ids = ids[:-1]")
MARK_FILE = "MARK-W2149-RULES-file-5e1f"
MARK_SOCKET = "MARK-W2149-RULES-sock-5e1f"
MARK_PROCESS = "MARK-W2149-RULES-proc-5e1f"


def rules_reading(path):
    """Reads a file outside itself; unconfined it would pass with the file's text inside its labels."""
    return _RULES.format(pre=f"EXTRA = [open({str(path)!r}).read().strip()]", post="")


def rules_socket(port):
    """Opens a socket to the case's listener; unconfined it would pass with the listener's text inside its labels."""
    pre = ("import socket\n"
           f"_s = socket.create_connection(('127.0.0.1', {port}), timeout=10)\n"
           "EXTRA = [_s.recv(256).decode().strip()]\n_s.close()")
    return _RULES.format(pre=pre, post="")


def rules_process():
    """Starts a process (the interpreter itself); unconfined it would pass with the child's text inside its labels.
    The text is written reversed in the script, so only a child that ran can give it."""
    code = f"print({MARK_PROCESS[::-1]!r}[::-1])"
    pre = ("import subprocess\n"
           f"EXTRA = [subprocess.run([sys.executable, '-I', '-c', {code!r}], capture_output=True, text=True,"
           " check=True).stdout.strip()]")
    return _RULES.format(pre=pre, post="")


def good_rules(lines):
    """RULES_GOOD's output, computed here."""
    out = []
    for x in lines:
        h = int(hashlib.sha256(x["id"].encode("utf-8")).hexdigest(), 16)
        cls = 14 if h % 4 else h % 13 + 1
        out.append({"id": x["id"], "label": "allow" if cls == 14 else ("ask" if cls == 13 else "refuse"),
                    "rule_class": cls, "clauses": [] if cls == 14 else ["DEC-820 (4)"], "uncertain": h % 9 == 0})
    return out


class Listener:
    """A TCP listener on 127.0.0.1 that sends ``text`` to each connection and counts them (S25's socket case)."""

    def __init__(self, text):
        self.text, self.connections, self._stop = text, 0, False
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(4)
        self.sock.settimeout(0.2)
        self.port = self.sock.getsockname()[1]
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while not self._stop:
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            self.connections += 1
            try:
                conn.sendall(self.text.encode())
            finally:
                conn.close()

    def close(self):
        self._stop = True
        self.thread.join(2)
        self.sock.close()


# -- the flows' launches --------------------------------------------------------------------------------------------

def rules_env(**more):
    """The pinned python for the rule script (GOV_INDEP_RULES_PYTHON): the interpreter running the tests."""
    return dict({"GOV_INDEP_RULES_PYTHON": os.path.realpath(sys.executable)}, **more)


def args(world, flow, half, **kw):
    kind, brief = FLOW[flow][:2]
    return world.args(kind, brief=brief, set_=half, **kw)


def dry(world, flow, half, seed, round_=None, env=None, commit="B"):
    support.next_second()
    return world.launch(*args(world, flow, half, round_=round_, seed=seed, dry=True, commit=commit),
                        env=rules_env(**(env or {})))


def deliver(world, flow, half, round_=None, out=None, program=None, program_args=None, env=None):
    session = {"out": dict(out or {})}
    if program:
        session.update(program=program, program_args=dict(program_args or {}))
    world.write_stub(session=session)
    support.next_second()
    return world.launch(*args(world, flow, half, round_=round_), env=rules_env(**(env or {})))


def seed_of(world, run_id) -> int:
    mine = [x for x in world.ledger_lines() if x.get("run") == run_id]
    assert len(mine) == 1, f"one SEEDS.log line for {run_id}: {mine}"
    return mine[0]["seed"]


def input_listing(wall) -> list:
    inp = Path(wall) / "input"
    return sorted(os.path.relpath(os.path.join(dp, n), inp) for dp, _dn, fn in os.walk(inp) for n in fn)


def wall_bytes(wall) -> bytes:
    data = b""
    for dp, _dn, fn in os.walk(wall):
        for n in fn:
            data += Path(dp, n).read_bytes()
    return data


def files_holding(roots, needle: str, skip=()):
    """Every file under ``roots`` whose bytes hold ``needle`` (tars included: they are not compressed)."""
    hits, raw = [], needle.encode()
    for root in roots:
        for dp, _dn, fn in os.walk(root):
            for n in fn:
                p = os.path.join(dp, n)
                if any(p == s or p.startswith(str(s).rstrip("/") + "/") for s in skip):
                    continue
                try:
                    if raw in Path(p).read_bytes():
                        hits.append(p)
                except OSError:
                    pass
    return hits


# -- the sessions' good outputs (the briefs' output and result sections) --------------------------------------------

def by14(f):
    return {str(c): f(c) for c in range(1, 15)}


RESULT = {
    "writer-tuning": {"cases": by14(lambda c: 1 if c in (1, 7, 14) else 0),
                      "copies": by14(lambda c: 1 if c in (1, 7, 14) else 0),
                      "near_miss": by14(lambda c: 1 if c == 14 else 0), "not_executable": 1,
                      "instructions_ignored": 0, "stopped": "none"},
    "labeller-r1": {"round": 1, "rules": 2, "instructions_ignored": 0, "stopped": "none"},
    "labeller-2-r1": {"round": 1, "rules": 2, "instructions_ignored": 0, "stopped": "none"},
}
RESULT["writer-heldout"] = dict(RESULT["writer-tuning"])
RULEBOOK = "# The planted rulebook (W2-149)\n- DEC-820 (4): a write outside the ticket's paths: refuse\n- DEC-820 (b): allow\n"
RULEBOOK_2 = "# The planted rulebook 2 (W2-149)\n- DEC-820 (4): refuse\n- DEC-1099 (1) Q9: allow\n"


def writer_cases(flow):
    p, src = ("p1", "planted-1") if flow == "writer-tuning" else ("p2", "planted-2")
    rows = [{"id": f"{p}-c{c}-{n:03d}-engineer", "source": src, "rule_class": str(c), "role": "engineer",
             "agent": None, "ticket": "DAEO-aaa1", "wbs": "W2-901", "tool": "Read",
             "input": {"file_path": f"{REPO}/docs/d01.md"}, "cwd": REPO, "executable": True, "strata": ["planted"],
             "session": src} for n, c in enumerate((1, 7, 14), start=1)]
    return jsonl(rows)


def writer_out(flow, **extra_result):
    aims = jsonl({"id": json.loads(x)["id"], "near_miss": False, "intent": f"{AIMS_MARK} names only"}
                 for x in writer_cases(flow).splitlines())
    return {"cases.jsonl": writer_cases(flow), "aims.jsonl": aims,
            "result.json": json.dumps(dict(RESULT[flow], **extra_result))}


def labeller_r1_out(rules=RULES_GOOD, **extra_result):
    return {"rulebook.md": RULEBOOK, "label_rules.py": rules,
            "result.json": json.dumps(dict(RESULT["labeller-r1"], **extra_result))}


def labeller2_r1_out(**extra_result):
    return {"rulebook-2.md": RULEBOOK_2, "result.json": json.dumps(dict(RESULT["labeller-2-r1"], **extra_result))}


def manifest_sha(files: dict) -> str:
    """A bundle of several files: the sha256 of the lines "<file sha256>  <name>\\n" sorted by name."""
    return support.sha256("".join(f"{support.sha256(files[n])}  {n}\n" for n in sorted(files)).encode())


# -- the counts ------------------------------------------------------------------------------------------------------

def text_problems(line):
    """Every string value of a counts object that is not a sha256, a commit, the run's id, the set's name or a fixed
    word (S13, S28); keys are the schema's business (it is closed)."""
    words = (set(support.KINDS) | set(support.STATUSES) | set(support.REASONS.values())
             | set(support.DELIVER_TO.values()) | set(TO_WORDS) | set(STOPPED_WORDS) | {support.ACT})
    bad = []

    def walk(x, key):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, k)
        elif isinstance(x, list):
            bad.append(f"a list under {key!r}")
        elif isinstance(x, str):
            if not (support.HEX64.match(x) or support.HEX40.match(x) or support.RUN_ID.match(x) or x in words
                    or (key == "set" and support.SET_NAME.match(x))):
                bad.append(f"text under {key!r}: {x[:40]!r}")
    walk(line, None)
    return bad


def assert_counts(world, line, result):
    """counts.json is the printed line, validates against the counts schema, holds no free text, and carries the
    result's numbers under ``out`` by their own keys (S28)."""
    schema = json.loads(support.COUNTS_SCHEMA.read_text())
    assert support.validate(schema, line) == [], support.validate(schema, line)
    assert text_problems(line) == [], text_problems(line)
    counts = json.loads((world.counts_dir(line) / "counts.json").read_text())
    assert counts == line, "the printed line is not counts.json"
    for k, v in result.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            assert line["out"].get(k) == v, (k, line["out"])
        elif isinstance(v, dict):
            assert line["out"].get(k) == v, (k, line["out"])


# -- the overlap auditor (S27) ---------------------------------------------------------------------------------------

def plant_labels(world, half):
    """Both labellers' files in the half's labels/ folder: labeller 1 every staged id, labeller 2 the first 51; 46 of
    those 51 differ, 5 agree; the smallest differing id was decided by an earlier audit run. 45 disputes remain."""
    actions, cases = staged(world, half)
    ids = [x["id"] for x in actions + cases]
    l1 = {i: LABELS[k % 3] for k, i in enumerate(ids)}
    second = ids[:51]
    agree = set(second[5:10])
    l2 = {i: l1[i] if i in agree else LABELS[(LABELS.index(l1[i]) + 1) % 3] for i in second}
    lines1 = [{"id": i, "label": l1[i], "rule_class": 14 if l1[i] == "allow" else 11,
               "clauses": [] if l1[i] == "allow" else ["DEC-820 (4)"],
               "reason": "" if k % 2 else "names src/ and DEC-820 (4) only", "how": "script" if k % 2 else "hand"}
              for k, i in enumerate(ids)]
    lines2 = [{"id": i, "label": l2[i], "rule_class": 14 if l2[i] == "allow" else 7, "clauses": ["DEC-1101 (2)"],
               "how": "hand", "reason": "names indep-walls/ and DEC-1101 (2) only"} for i in second]
    differ = sorted(i for i in second if i not in agree)
    earlier = differ[0]
    h = world.half(half)
    support.write_file(h, "labels/labels.jsonl", jsonl(lines1))
    support.write_file(h, "labels/labels-2.jsonl", jsonl(lines2))
    support.write_file(h, f"labels/audit/20261101T000000Z-{half}-r1.decisions.jsonl", jsonl([
        {"id": earlier, "label": l1[earlier], "rule_class": 11, "basis": ["DEC-820 (4)"],
         "agrees_with": "labeller-1", "flag": "none", "reason": ""}]))
    support.write_file(h, "labels/owner.jsonl", jsonl([{"id": "an-earlier-owner-case", "run": "planted"}]))
    return {"ids": ids, "lines1": lines1, "lines2": lines2, "earlier": earlier, "undecided": differ[1:]}


def xy(seed: int, ids):
    """Each case's x/y order (S27): random.Random(seed).random() < 0.5 once per case, in the run's order, means x is
    labeller 1. Returns {id: (labeller of x, labeller of y)}."""
    rng = random.Random(seed)
    return {i: (1, 2) if rng.random() < 0.5 else (2, 1) for i in ids}


def expected_disputes(world, half, planted, seed, ids_run):
    actions, cases = staged(world, half)
    by_id = {x["id"]: x for x in actions + cases}
    one = {x["id"]: x for x in planted["lines1"]}
    two = {x["id"]: x for x in planted["lines2"]}
    order = xy(seed, ids_run)
    rows = []
    for i in ids_run:
        first, second = (one[i], two[i]) if order[i] == (1, 2) else (two[i], one[i])
        rows.append({"id": i, "action": {k: by_id[i][k] for k in ACTION7},
                     "x": {k: first[k] for k in LABEL4}, "y": {k: second[k] for k in LABEL4}})
    return rows


def expected_tickets(world, half, ids_run):
    actions, cases = staged(world, half)
    by_id = {x["id"]: x for x in actions + cases}
    named = {by_id[i]["ticket"] for i in ids_run}
    return sorted(({"id": t, "role": r, "wbs_id": w, "allowed_paths": p}
                   for t, (r, w, p) in support.PLANTED_TICKETS.items() if t in named), key=lambda x: x["id"])


def mapped_back(decisions, order):
    out = []
    for d in decisions:
        d = dict(d)
        if d["agrees_with"] in ("x", "y"):
            d["agrees_with"] = f"labeller-{order[d['id']][0 if d['agrees_with'] == 'x' else 1]}"
        out.append(d)
    return out
