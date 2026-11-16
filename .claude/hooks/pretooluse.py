#!/usr/bin/env python3
"""This repository's own PreToolUse guard while the Gov OS is being built (owner, DEC-953 item 2).

It keeps exactly five rules, and the catastrophic deletes (DEC-953 item 2, DEC-954, DEC-1050 (8)):
  1. the implementer never writes acceptance tests: only the independent test designer writes tests/acceptance/**
     (MR-3, DEC-906);
  2. no reads of the hidden half of an evaluation set (by the sessions it measures, DEC-820 (d)), in this tree and
     in every other worktree and run clone of this repository (W2-84's fix, DEC-954 Q9b), or of the held-out
     material (every role, DEC-820 (b));
  2b (DEC-1082 (3)). no reads, and no writes the guard resolves, of the sets root's hidden folders (the hidden halves
     kept outside the repository, the measure's --sets-root): the main tree's path-map.yaml sets_root_hidden: names the
     root, its hidden globs and the roles refused them; each role a set in evaluation_sets measures is refused that
     set's hidden globs too; under the sets root and in every tree. No block, no check. For those roles a Bash line
     that names the sets root is refused when it also names a hidden folder, or builds a path after it (a variable,
     a substitution, a glob, a cd; DEC-1097 (2), readiness review 5 F1): a plain --sets-root <root> stays allowed;
     a glob with a wildcard before its end names the hidden folder or file itself (ACT-SETS-GLOBS-1);
  2c (ACT-INDEP-WALLS-1). no reads, and no writes, of a folder outside every tree that the main tree's path-map.yaml
     session_hidden: refuses to named sessions only (a role, and the tickets it runs on): SANDBOX-GUARD-EXP-1's tuner
     (an engineer on W2-56) is refused ~/.claude/projects, the raw transcripts. File tools by the path they name (a
     search that starts at or above the folder too); a Bash line that names the folder, or names its parent with the
     folder's name, a substitution, or a variable, glob or cd after it (the line rule of 2b). Every other session,
     the CTO's tools included, is untouched. No block, no check;
  2d (ACT-OPERATOR-1, DEC-1106 (3), DEC-1108 (5)). no writes, by any session this guard judges, into a folder
     outside every tree that the main tree's path-map.yaml write_refused: names, but for the folders directly under
     it that its entry keeps open: the operator agent's folder ~/gov-os-operator (its install and commit freeze, its
     frozen ACTs, log and wall; the CTO writes only queue/) and the guard's call log ~/.gov-os/guard-calls. A file
     tool by the path it names, links followed; a Bash line by the writes the guard resolves (one it cannot work out
     is let through, as for rules 1 and 5; deletions there are already the catastrophic rule's). The operator agent's
     walled session runs outside this guard. No block, no check;
  5. independent reviewers and auditors write only their own outcomes: review and audit records under docs/probes/,
     docs/audit/, docs/assessment/ and the CTO's .gov-runtime/scratch/orchestrator/reviews/ (ACT-GUARD-FIX-4), their
     own scratch under .gov-runtime/scratch/review/ or /audit/, and /tmp;
     never code, tests, tickets, records, handovers or anything else (DEC-954);
  3. no reads of secrets or keys (every role, DEC-820 (a));
  4. no installs without the owner: an install asks the owner only in the CTO's own session (the orchestrator on the
     coordination ticket W2-00) and is refused in every other, leads included, which escalate it (DEC-957); sudo is
     refused;
  and rm is free (no ask, DEC-1050 (8)) but for the catastrophic, refused to every session: the repository's root,
  a .git, the main tree's tracked files, the folders that hold the project or its scratch, and anything outside
  the project (the main tree, ~/gov-os-worktrees/, ~/gov-os-runs/) and its scratch (/tmp, /dev/shm,
  .gov-runtime/scratch/);
  and role separation from the path map (DEC-1052 G-14, role_reads.py): what the main tree's path-map.yaml
  role_paths: denies a role to read (the engineer the acceptance tests, the test designer the engineer's new code),
  by simple path checks; no section, no check.
It reuses the product's own checks (gov.guard.reads, heldout, install, decide), imported from the pinned judge that
runs this file. The product's full guard (template/governance/kernel/hooks/pretooluse.py, src/gov/guard/) stays built
and tested; it is not wired here until the Gov OS is whole. Fail closed: an error or the 20-second deadline refuses.
Rules 1 and 5 read a Bash command through bash_writes.py beside this file (ACT-GUARD-FIX-3) and, since
ACT-GUARD-FIX-4 (DEC-1050 (12), G-1 and G-2), judge only the writes it resolves: a write whose target the guard
cannot work out is let through, never guessed at from the words the command holds. The backstops are the landing's
check that every commit touching tests/acceptance/ carries Role: independent-test-designer (G-1, in the merge queue
first) and the reviewed tree's git status after a review (G-2).

The call log (ACT-GUARD-CALLLOG-1, DEC-1106 (2)): after each decision the hook appends one JSON line to
~/.gov-os/guard-calls/<UTC day>.jsonl (folder 0700, file 0600; outside every tree, the run clones and the sets root):
the time, the session id, the role, the subagent type, the ticket, the tool, the decision, the rule that decided, the
kind of tree, the time taken, the sha256 of the normalised action (the tool name and its input as canonical JSON) and
an HMAC of it under salt.key in that folder (a key file: rule 3 refuses it by name). Never the command, a path or a
file's text. A line at most 1 KiB, one write; a day's file stops at 32 MiB (a <day>.jsonl.capped marker says so);
files older than 92 days are removed when a new day's file starts. A failure to log never changes the decision and
never blocks the call: it is noted once on stderr and the decision stands. GOV_GUARD_CALLS_DIR (an absolute path)
moves the log, for the rehearsals and the suites only.
"""
import hashlib
import hmac
import json
import os
import signal
import stat
import sys
import time

import glob
import re
import subprocess

ACCEPTANCE = "tests/acceptance/"
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
TEST_DESIGNER = "independent-test-designer"
REVIEWERS = ("independent-auditor", "independent-reviewer", "reviewer", "auditor")
REVIEW_PATHS = ("docs/probes/", "docs/audit/", "docs/assessment/", ".gov-runtime/scratch/review/",
                ".gov-runtime/scratch/audit/",
                # the CTO's review records, where its briefs tell reviewers to write them (ACT-GUARD-FIX-4: two false
                # refusals on 2026-11-02, rows 75-76, and two on 2026-11-03, of the E1 review's own record)
                ".gov-runtime/scratch/orchestrator/reviews/")
HOME = os.path.realpath(os.path.expanduser("~"))
RUNS = os.path.expanduser("~/gov-os-runs")
WORKTREES = os.path.realpath(os.path.expanduser("~/gov-os-worktrees"))
SCRATCH = "/tmp"
SHM = "/dev/shm"  # the memory-backed scratch the project's locks use (gov-os-W2-76-held.lock): scratch, like /tmp
CTO_WBS = "W2-00"  # the coordination ticket whose orchestrator session is the CTO
MOST_GLOB = 20000  # the paths one rm glob may name that the guard checks
# rm in a command the scan cannot read (ACT-GUARD-FIX-4): its words up to the next ; & | ) or newline.
# R5 (W2-42a, DEC-1133 (2); gov.guard.decide, copied): a file tool's path or glob field that is no path the system takes
# (not text, or text holding a NUL byte) is refused by its own rule, before another rule resolves it.
# The fields of a file tool's call that are resolved as a path or a glob.
_PATH_FIELDS = {"Read": ("file_path",), "Grep": ("path", "glob"),
                "Glob": ("path", "pattern"), "Write": ("file_path",),
                "Edit": ("file_path",), "MultiEdit": ("file_path",),
                "NotebookEdit": ("notebook_path",)}

NO_PATH_REFUSAL = ("a path field of the call is not a path (not text, or text holding a "
                   "NUL byte), so the guard cannot say what it names: refused to every "
                   "role (DEC-1133 (2))")


def _no_path(tool_name, tool_input: dict) -> bool:
    """True when a path or a glob field of a file tool's call is given but is
    no path the system takes: not a string, or one holding a NUL byte."""
    fields = _PATH_FIELDS.get(tool_name, ()) if isinstance(tool_name, str) else ()
    return any(tool_input.get(key) is not None and (
        not isinstance(tool_input[key], str) or "\0" in tool_input[key]) for key in fields)


# R4 (W2-42a, DEC-1133 (2); gov.guard.reads, copied): a revision-colon-path in git show or cat-file, or on a side of
# git diff, is judged as a read of its path; a revision git does not resolve, or one the guard cannot read, is a ruled
# refusal, not the error path; the methods that use these are copied into ``Judge`` in ``classes`` below.
REV_REFUSAL = ("the call names a revision the guard cannot resolve: git does not resolve "
               "it (or its <rev>:<path>) to a commit, tree or blob, or it is given at run "
               "time (a variable, a substitution, --stdin), so what the call shows cannot "
               "be judged against the parts refused to this session (DEC-820): refused; "
               "name a revision and a path that exist")
# W2-42a R4: in <rev>:<path> the path starts at the top of the tree <rev> names;
# only a commit (or the index) places it at the repository's top. A subtree's
# id, or a blob named by its id alone and shown as text, leaves the file's path
# unknown to the guard, so it cannot be judged against the parts refused here.
PLACE_REFUSAL = ("the call shows a git object whose path in the repository the guard "
                 "cannot place: a <rev>:<path> whose <rev> names a tree that is not a "
                 "commit's top (a subtree's id), or a blob named by its id alone and "
                 "shown as text, so what it shows cannot be judged against the parts "
                 "refused to this session (DEC-820): refused; name the file as "
                 "<commit>:<path from the top> or :<path>")


def _blob_ref(word: str) -> tuple[str, str] | None:
    """A revision-colon-path's revision and path (``<rev>:<path>``, the
    index's ``:<path>`` and ``:<n>:<path>``), or None: no colon, an empty
    path (a revision's whole tree), a message search (``:/<text>``), or a
    range or a negation before the colon (judged as revisions)."""
    if ":" not in word or word.startswith(":/"):
        return None
    rev, _, path = word.partition(":")
    if not rev and re.match(r"[0-3]:", path):
        path = path[2:]
    if not path or ".." in rev or rev.startswith("^"):
        return None
    return rev, path


def _output_joined(words: list[str]) -> list[str]:
    """git's ``--output <file>`` as one word, ``--output=<file>`` (W2-42a):
    the file it writes is no revision word."""
    out, k = [], 0
    while k < len(words):
        if words[k] == "--output" and k + 1 < len(words):
            out.append("--output=" + words[k + 1])
            k += 2
        else:
            out.append(words[k])
            k += 1
    return out


CRUDE_RM = re.compile(r"(?:^|[;&|(\n`]|\$\(|\b(?:do|then|else|nohup|command|exec|xargs)\s)\s*"
                      r"(?:[\w./-]*/)?\\?rm\s+([^;&|)\n`]*)")


# -- the call log (ACT-GUARD-CALLLOG-1, DEC-1106 (2)) -------------------------------------------------------------

CALLS_DIR = os.path.join(HOME, ".gov-os", "guard-calls")
CALLS_ENV = "GOV_GUARD_CALLS_DIR"  # the rehearsals' and suites' folder; an absolute path or ignored
CALLS_SALT = "salt.key"  # 64 hex characters, written by apply.sh; *.key: refused by name to every role (rule 3)
CALLS_CAP = 32 * 1024 * 1024  # a day's file at most
CALLS_KEEP_DAYS = 92
CALLS_SECONDS = 2  # the log's own deadline; the decision is made before it starts
CALLS_DAY = re.compile(r"^(\d{4}-\d{2}-\d{2})\.jsonl(?:\.capped)?$")
_FIELD = re.compile(r"[^A-Za-z0-9._:-]")
_CALL = {"t0": time.monotonic(), "event": None, "root": None, "done": False, "warned": False}


class _LogTimeout(Exception):
    pass


def _log_timeout(signum, frame):
    raise _LogTimeout("the call log took more than %d seconds" % CALLS_SECONDS)


def _field(value):
    """A name the log may hold: letters, digits and . _ : - only, at most 64; anything else is dropped."""
    return _FIELD.sub("", value)[:64] if isinstance(value, str) else ""


def action_bytes(tool, tin):
    """The normalised action: the tool name and its input as canonical JSON (keys sorted, no spaces, UTF-8). A
    reader recomputes it from a transcript's tool_use (name, input) to match a line by its sha256."""
    return json.dumps({"tool": tool, "input": tin}, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8", "surrogatepass")


def _tree_kind(root):
    """The kind of tree the session runs in, never its path: worktree, run, scratch, main (a git tree elsewhere) or
    other. Readers keep the live work (main, worktree) apart from rehearsals, replays and suites."""
    full = os.path.realpath(root) if isinstance(root, str) and root else ""
    if not full:
        return "other"
    if inside(full, WORKTREES):
        return "worktree"
    if inside(full, os.path.realpath(RUNS)):
        return "run"
    if inside(full, SCRATCH) or inside(full, SHM):
        return "scratch"
    return "main" if os.path.exists(os.path.join(full, ".git")) else "other"


def _calls_warn(exc):
    if _CALL["warned"]:
        return
    _CALL["warned"] = True
    try:
        sys.stderr.write(f"guard (ACT-GUARD-CALLLOG-1): the call log was not written ({type(exc).__name__}: "
                         f"{str(exc)[:120]}); the decision stands\n")
    except Exception:
        pass


def _calls_prune(where, now):
    """On a new day's file: the day files older than CALLS_KEEP_DAYS, by their names only."""
    cut = time.strftime("%Y-%m-%d", time.gmtime(now - CALLS_KEEP_DAYS * 86400))
    for name in os.listdir(where):
        m = CALLS_DAY.match(name)
        if m and m.group(1) < cut:
            os.unlink(os.path.join(where, name))


def _calls_write(decision, rule):
    now = time.time()
    ev = _CALL["event"] if isinstance(_CALL["event"], dict) else None
    tool = ev.get("tool_name") if ev is not None else None
    where = os.environ.get(CALLS_ENV) or ""
    where = where if os.path.isabs(where) else CALLS_DIR
    os.makedirs(where, mode=0o700, exist_ok=True)
    st = os.lstat(where)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
        raise RuntimeError("the log folder is a link, not a folder, or not this user's")
    digest = keyed = None
    if ev is not None:
        raw = action_bytes(tool if isinstance(tool, str) else None, ev.get("tool_input"))
        digest = hashlib.sha256(raw).hexdigest()
        try:
            with open(os.path.join(where, CALLS_SALT), "rb") as f:
                salt = f.read(256).strip()
            if re.fullmatch(rb"[0-9a-f]{64}", salt):
                keyed = hmac.new(bytes.fromhex(salt.decode()), raw, hashlib.sha256).hexdigest()
        except OSError:
            pass
    row = {"v": 1, "time": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + ".%03dZ" % (now % 1 * 1000),
           "session": _field(ev.get("session_id")) if ev is not None else "",
           "role": _field(os.environ.get("GOV_ROLE") or ""),
           "agent": _field(ev.get("agent_type")) if ev is not None else "",
           "ticket": _field(os.environ.get("GOV_TICKET") or ""),
           "tool": _field(tool), "decision": decision, "rule": rule,
           "tree": _tree_kind(_CALL["root"] or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()),
           "ms": int((time.monotonic() - _CALL["t0"]) * 1000), "sha256": digest, "keyed": keyed}
    line = (json.dumps(row, separators=(",", ":")) + "\n").encode("ascii")
    day = os.path.join(where, time.strftime("%Y-%m-%d", time.gmtime(now)) + ".jsonl")
    fd = os.open(day, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        size = os.fstat(fd).st_size
        if size >= CALLS_CAP:
            try:
                os.close(os.open(day + ".capped", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600))
            except FileExistsError:
                pass
            raise RuntimeError("today's file has reached its cap")
        os.write(fd, line)  # one write of at most 1 KiB to a file opened for appending: lines never interleave
    finally:
        os.close(fd)
    if size == 0:
        _calls_prune(where, now)


def record(decision, rule):
    """ACT-GUARD-CALLLOG-1: one line for this call's decision, once. Never raises, never changes the decision: the
    20-second deadline is stopped first (the decision is made), and the log has CALLS_SECONDS of its own."""
    if _CALL["done"]:
        return
    try:
        signal.alarm(0)
        _CALL["done"] = True
        signal.signal(signal.SIGALRM, _log_timeout)
        signal.alarm(CALLS_SECONDS)
        _calls_write(decision, rule)
    except Exception as exc:
        _CALL["done"] = True
        _calls_warn(exc)
    finally:
        try:
            signal.alarm(0)
        except Exception:
            pass


def judge_rule(why):
    """The rule id of a refusal by the read judge (rules 2 and 3)."""
    from gov.guard import reads
    return {reads.HIDDEN_REFUSAL: "2-hidden", reads.SECRET_REFUSAL: "3-secret",
            reads.RUNTIME_REFUSAL: "2-listing"}.get(why, "2-judge")


# -- the YAML the guard reads, parsed once per call through libyaml (W2-111, DEC-1187) ------------------------------

_YAML = {"product": None, "seen": {}}  # the product's own loader, and this call's answers by their text


def libyaml_reads_as_python(text):
    """Whether libyaml's parser is taken for *text* (W2-111, P-W2-111-R5-ROWS (a)): a str with no tab, no ``?`` and no
    BOM after its first character. libyaml reads three kinds of text the pure-Python parser refuses (rv-3 F1): a tab
    as a separator (inside or after a value, after ``key:``), a ``?`` inside a flow item (``[a? b]``, ``[a?b]``: in a
    flow the pure scanner ends a plain scalar at any ``?`` and takes it as a key indicator) and a BOM at the start of
    a later line (libyaml skips it; the pure scanner only at the first character). Whether a ``?`` lies in a flow
    cannot be told without scanning, so any ``?`` takes the pure parser; so does a byte string. The product's
    gov.util.parts.libyaml_reads_as_python, word for word."""
    return (isinstance(text, str) and "\t" not in text and "?" not in text
            and "﻿" not in text[1:])


def load_yaml_unique(stream):
    """W2-111 (DEC-1187, P-W2-111-R5-ROWS (a)): the pure-Python SafeLoader's answer with the check of a key written
    twice (the pinned product's loader), the same data or the same refusal with its text. A text
    ``libyaml_reads_as_python`` passes is parsed by libyaml's CSafeLoader when it is installed (the pure-Python
    SafeLoader took 30 ms of every call); its constructor and resolver are SafeLoader's own and the check of a key
    written twice is the product's, word for word. Any other text, and any text whose libyaml parse raises (a YAML
    error, a key written twice, no libyaml), is given to the product's own loader, so every refusal and its text are
    the pure loader's, never this one's. A stream is read first and given to the product's loader as a stream of the
    same name and text (the pure loader names a stream's file in its error's mark). Each text is parsed once per hook
    run (one run judges one call; nothing is kept on disk or across calls), and each caller gets its own copy.
    Hook-local until 0.1.1: the product's loader does the same from 0.1.1 on (gov.util.parts, W2-111)."""
    import copy
    text = stream.read() if hasattr(stream, "read") else stream
    seen = _YAML["seen"]
    key = (type(text), text) if isinstance(text, (str, bytes)) else None
    if key is None or key not in seen:
        done = False
        if libyaml_reads_as_python(text):
            try:
                import yaml

                class Loader(yaml.CSafeLoader):
                    def construct_mapping(self, node, deep=False):
                        mapping = super().construct_mapping(node, deep=deep)
                        if len(mapping) != len(node.value):
                            raise yaml.constructor.ConstructorError(
                                None, None, "a key is written twice", node.start_mark)
                        return mapping

                data, done = yaml.load(text, Loader=Loader), True
            except Exception:
                pass  # the product's answer, or its own error, below
        if not done:
            again = text
            if text is not stream:  # a stream: the same text again, under the stream's name
                import io
                again = io.BytesIO(text) if isinstance(text, bytes) else io.StringIO(text)
                if hasattr(stream, "name"):
                    again.name = stream.name
            data = _YAML["product"](again)
        if key is None:
            return data
        seen[key] = data
    return copy.deepcopy(seen[key])


def use_fast_yaml():
    """The pinned judge's held-out loader and evaluation sets read their YAML through ``load_yaml_unique`` above:
    the name in gov.util.parts (evaluation_sets) and in gov.guard.heldout (load_held_out, which imported it), for
    this hook run only. The product's loader is kept as the fallback. Hook-local until 0.1.1."""
    from gov.guard import heldout
    from gov.util import parts
    if _YAML["product"] is None:
        _YAML["product"] = parts.load_yaml_unique
    parts.load_yaml_unique = load_yaml_unique
    heldout.load_yaml_unique = load_yaml_unique


def parse_both(parse, command, cwd):
    """The product's parser on a command it is to read as before this fix, and, when the command continues a line
    with a backslash-newline, on the text with each one removed too (ACT-GUARD-FIX-3 round 2): the targets of both,
    so a write split over lines is not missed."""
    found = parse(command, cwd)
    if "\\\n" not in command:
        return found
    more = parse(command.replace("\\\n", ""), cwd)
    if found is None and more is None:
        return None
    return list(found or []) + list(more or [])


def line_parser(command):
    """The line parser the judgement reads shell text with (ACT-GUARD-FIX-6): the product's of W2-42a, copied into
    bash_writes.py (``line_write_targets``), with the command's own glob options deciding whether an unmatched glob is
    its literal word, as ``gov.guard.decide._extract_bash_write_targets`` hands it."""
    import bash_writes
    literal = not bash_writes.GLOB_OPTIONS_RE.search(command)

    def parse(text, where):
        return bash_writes.line_write_targets(text, where, literal)
    return parse


_JUDGED = {}


def bash_judgement(command, cwd):
    """ACT-GUARD-FIX-3: what ``command`` writes, read by bash_writes.py with the product's parser; None when the
    command cannot be read for certain. Read once per call of the hook."""
    if (command, cwd) in _JUDGED:
        return _JUDGED[(command, cwd)]
    import bash_writes
    from gov.guard.decide import _UNRESOLVABLE, _expand_token
    if bash_writes.SENT != _UNRESOLVABLE:
        raise RuntimeError("bash_writes.SENT differs from the parser's sentinel")
    try:
        judged = bash_writes.judge(command, cwd, line_parser(command), _expand_token)
    except bash_writes.Unreadable:
        judged = None
    _JUDGED[(command, cwd)] = judged
    return judged


def resolved(targets):
    """The targets the guard worked out (ACT-GUARD-FIX-4): the unresolvable sentinel and the unknown folder's out."""
    from bash_writes import SENT, UNKNOWN
    return [t for t in targets or [] if isinstance(t, str) and t and t != SENT and not t.startswith(UNKNOWN)]


def bash_writes_of(command, cwd):
    """The write targets of a Bash command the guard resolves (ACT-GUARD-FIX-4): the shell's own, and those of the
    code it runs inline that resolve to a path. A command the scan cannot read is read by the product's parser
    alone."""
    import bash_writes
    from bash_writes import SENT
    judged = bash_judgement(command, cwd)
    if judged is None:
        return resolved(parse_both(line_parser(command), command, cwd)), []
    # ``writes``: what the product enforces beside the shell's own (git checkout, restore, rm and mv on paths, dd,
    # truncate, sort -o, rsync, a script written and run, a body an unknown reader may run as shell; W2-42a). Like the
    # findings they are not the shell's own writes: rule 1 reads them, rule 5 never did (DEC-1050 (12), G-2).
    code = resolved([full for _targets, _scope, _code in judged.findings
                     for raw, full in _targets if raw != SENT and full] + judged.writes)
    # ACT-GUARD-FIX-6 option B (the CTO, stricter only): a run the scan cannot read for certain (the unresolvable target
    # in ``unread``: a script written and run, a body an unknown reader may run) in a call whose text names the acceptance
    # tests is a write into them, as ACT-GUARD-FIX-3's round 2 refused it; rule 1 reads it, rule 5 never did.
    if SENT in judged.unread and (bash_writes.names_tests(command) or bash_writes.names_tests(bash_writes.joined(command))):
        code.append(os.path.join(os.environ.get("CLAUDE_PROJECT_DIR") or cwd, bash_writes.ACCEPTANCE.rstrip("/")))
    return resolved(judged.shell), code


_ROOTS = {}


def tree_roots(root):
    """This tree, every worktree of its repository, and the run clones under ~/gov-os-runs (W2-84's every tree).
    Found once per call of the hook (ACT-GUARD-FIX-4)."""
    if root not in _ROOTS:
        _ROOTS[root] = _tree_roots(root)
    return _ROOTS[root]


def _tree_roots(root):
    roots = [os.path.realpath(root)]

    def worktrees(repo):
        try:
            out = subprocess.run(["git", "-C", repo, "worktree", "list", "--porcelain"], capture_output=True,
                                 text=True, timeout=5).stdout
            return realpaths([line[9:] for line in out.splitlines() if line.startswith("worktree ")])
        except Exception:
            return []

    roots += worktrees(root)
    # a run clone's origin, when it is a local repository, and that repository's worktrees
    try:
        origin = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"], capture_output=True, text=True,
                                timeout=5).stdout.strip()
        if origin.startswith("file://"):
            origin = origin[7:]
        if origin.startswith("/") and os.path.isdir(origin):
            roots += [os.path.realpath(origin)] + worktrees(origin)
    except Exception:
        pass
    roots += realpaths([os.path.dirname(g) for g in runs_gits(RUNS)])
    return list(dict.fromkeys(roots))


def realpaths(paths):
    """W2-111 (DEC-1187): ``os.path.realpath`` of each path, the folders they share resolved once (39 worktrees under
    one folder: one walk of that folder, not 39). An absolute, normal path whose last name is no link is its folder's
    real path and that name, as realpath walks it (a name it cannot stat is no link, as realpath takes it); any other
    path is realpath's own. The same code as the product's gov.guard.reads._realpaths (W2-111 r4, in 0.1.1)."""
    seen = {}

    def real(path):
        if path not in seen:
            folder, name = os.path.split(path)
            if not name or name in (".", "..") or not os.path.isabs(path) or os.path.normpath(path) != path:
                seen[path] = os.path.realpath(path)
            else:
                at = os.path.join(real(folder), name)
                try:
                    link = stat.S_ISLNK(os.lstat(at).st_mode)
                except OSError:
                    link = False
                seen[path] = os.path.realpath(path) if link else at
        return seen[path]
    return [real(p) for p in paths]


RUNS_GLOBS = ("*/.git", "*/*/.git", "*/*/*/.git", "*/*/*/*/.git")  # the run clones' .git, at depth 1 to 4


def _glob_folders(folder):
    """glob's own listing of one folder for a ``*`` that has more parts after it: the names of the entries that are
    folders (links to folders too: is_dir() follows them), not hidden (no leading dot), in the order the folder lists
    them; an entry that cannot be stat'ed is passed over, and a folder that cannot be listed gives what was listed
    before the error, as glob._iterdir and glob._listdir do."""
    names = []
    try:
        with os.scandir(folder) as it:
            for entry in it:
                try:
                    if entry.is_dir():
                        names.append(entry.name)
                except OSError:
                    pass
    except OSError:
        pass
    return [n for n in names if n[:1] != "."]


def runs_gits(top):
    """W2-111 (DEC-1187): exactly ``[g for p in RUNS_GLOBS for g in glob.glob(os.path.join(top, p))]``, the same
    paths in the same order, with each folder listed once instead of once per glob (the 4 globs listed the first
    level 4 times, the second 3 and the third 2: about 640 listings on every call). Glob k's matches are the depth-k
    folders that hold a .git (os.path.lexists, glob's test of a literal last part), in glob's order: the depth-k
    folders are each depth-(k-1) folder's listing in turn, as glob's own recursion yields them."""
    found, level = [], [top]
    for _pattern in RUNS_GLOBS:
        # os.path.join(d, n), as posixpath.join writes it for a name with no slash (a listed name has none)
        level = [(d + n if d.endswith("/") else d + "/" + n) for d in level for n in _glob_folders(d)]
        found += [g for g in (d + "/.git" for d in level) if os.path.lexists(g)]
    return found


def review_may_write(path, root, cwd, made=()):
    """Rule 5: a reviewer's or auditor's write lands only in its record paths, its own scratch, or /tmp. A record
    folder itself only when the command makes it (``made``: mkdir's folders, none of them deleted; ACT-GUARD-FIX-4),
    so ``mkdir -p <records> && cat > <records>/<its record>`` passes and ``rm -rf <records>`` does not."""
    if not isinstance(path, str) or not path:
        return False
    full = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    for tree in tree_roots(root):  # inside any tree of this repository: only the record paths
        rel = os.path.relpath(full, tree)
        if rel == "." or not rel.startswith(".."):
            if any(rel.startswith(p) for p in REVIEW_PATHS):
                return True
            return rel in (p.rstrip("/") for p in REVIEW_PATHS) and full in made
    return full == "/tmp" or full.startswith("/tmp/")


def bash_made(command, cwd):
    """The folders a Bash command makes with mkdir and does not delete with rm, real paths (ACT-GUARD-FIX-4, rule 5);
    none when the scan cannot read the command."""
    judged = bash_judgement(command, cwd)
    if judged is None:
        return set()
    gone = {os.path.realpath(p) for _w, p, how in judged.deletes if how == "names"}
    return {os.path.realpath(p) for p in judged.made} - gone


# -- rm: free but for the catastrophic (ACT-GUARD-FIX-4, DEC-1050 (8)) ------------------------------------------

def main_tree(root):
    """The repository's main working tree: the folder of the common .git of the tree at ``root``, else of the tree
    this hook file lives in (a session whose folder git cannot read, a removed worktree: its rm is not refused for
    that alone), else ``root``."""
    for where in (root, os.path.dirname(os.path.abspath(__file__))):
        try:
            out = subprocess.run(["git", "-C", where, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                 capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            out = ""
        if out and os.path.basename(out.rstrip("/")) == ".git":
            return os.path.realpath(os.path.dirname(out.rstrip("/")))
    return os.path.realpath(root)


SETS_BLOCK = "sets_root_hidden"  # DEC-1082 (3)
PATH_MAP = os.path.join("governance", "project", "path-map.yaml")
SETS_WRITE_REFUSAL = ("the call writes into the hidden part of an evaluation set, which is refused to this session "
                      "(DEC-1082 (3))")


def sets_root_rule(main):
    """DEC-1082 (3): the main tree's sets_root_hidden block (a branch cannot weaken it): the sets root as a real path,
    its hidden globs (project-relative, from the root) and the roles refused them; None with no block. A block not of
    that shape raises, and the hook refuses (fail closed)."""
    try:
        with open(os.path.join(main, PATH_MAP), encoding="utf-8") as f:
            lines = f.read().splitlines(keepends=True)
    except FileNotFoundError:
        return None
    at = [i for i, line in enumerate(lines) if re.match(SETS_BLOCK + r"\s*:", line)]
    if not at:
        return None
    if len(at) > 1:
        raise RuntimeError(f"{PATH_MAP}: {SETS_BLOCK} is written more than once")
    end = next((j for j in range(at[0] + 1, len(lines))
                if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
    from gov.guard.heldout import load_yaml_unique
    from gov.guard.reads import _paths_ok
    data = load_yaml_unique("".join(lines[at[0]:end]))
    block = data.get(SETS_BLOCK) if isinstance(data, dict) else None
    if not isinstance(block, dict):
        raise RuntimeError(f"{PATH_MAP}: {SETS_BLOCK} is not a map")
    top, globs, roles = block.get("root"), block.get("hidden"), block.get("refused_roles")
    top = os.path.expanduser(top) if isinstance(top, str) else ""
    if (not os.path.isabs(top) or os.path.realpath(top) in ("/", HOME) or not _paths_ok(globs, True)
            or not isinstance(roles, list) or not roles or not all(isinstance(r, str) and r for r in roles)):
        raise RuntimeError(f"{PATH_MAP}: {SETS_BLOCK} is not a root, a list of hidden globs and a list of roles")
    return os.path.realpath(top), list(globs), list(roles)


SETS_LINE_REFUSAL = ("the command names the sets root together with {what}, which is refused to this session "
                     "(DEC-1082 (3), DEC-1097 (2)): name only the root, as --sets-root <root>, and let the tool's own "
                     "code open its files")
_ROOT_MARK = "\x00SETSROOT\x00"


def sets_root_spellings(top):
    """The sets root as a command line spells it: its real path and, under HOME, ~/..., $HOME/... and ${HOME}/...."""
    out = [top]
    if top.startswith(HOME + "/"):
        rel = top[len(HOME) + 1:]
        out += ["~/" + rel, "$HOME/" + rel, "${HOME}/" + rel]
    return out


_KEY_NAME = r"[^/\s'\"\x00]"  # one character of a folder or file name on a command line


def sets_line_keys(globs):
    """The line rule's keys, (the path's regex, the quoted name's regex) for each hidden glob, in order, each once.
    A glob whose only wildcard is a trailing /** keeps its literal head (fixtures/evaluation/ dropped: runs/fresh-80,
    memory-verdict-2, ...) with a / beside it, or its last name quoted, as before. ACT-SETS-GLOBS-1: a glob with a
    wildcard before its end (fixtures/evaluation/*/hidden/**, fixtures/evaluation/*/XCHECK-r*.md,
    runs/*/miss-classes.json) has no literal head that is hidden: its key is its own parts (a trailing /** and
    fixtures/evaluation/ dropped), each * one name, so a line naming the root is refused for the hidden folder or file
    itself (zz/hidden/, zz/XCHECK-r1.md, runs/zz/miss-classes.json) or its last name quoted, and never for the open
    folder above it (fixtures/evaluation/zz/visible, runs/e0/counts.txt)."""
    out = []
    for g in globs:
        parts = g.split("/")
        n = next((i for i, p in enumerate(parts) if any(c in p for c in "*?[{")), len(parts))
        if n >= len(parts) - 1 and (n == len(parts) or parts[n] == "**"):
            head = "/".join(parts[:n])
            head = head[len("fixtures/evaluation/"):] if head.startswith("fixtures/evaluation/") else head
            if head:
                e = re.escape(head)
                out.append((r"(?<=/)%s(?![\w.-])|(?<![\w.-])%s(?=/)" % (e, e),
                            r"(['\"])%s\1" % re.escape(head.rsplit("/", 1)[-1])))
            continue
        if parts[-1] == "**":
            parts = parts[:-1]
        if parts[:2] == ["fixtures", "evaluation"] and len(parts) > 2:
            parts = parts[2:]
        rx = []
        for p in parts:
            if p == "**":
                rx.append(r"[^\s'\"\x00]*?")
            elif p == "*" or "[" in p or "{" in p:
                rx.append(_KEY_NAME + "+")
            else:
                rx.append("".join(_KEY_NAME + "*" if c == "*" else _KEY_NAME if c == "?" else re.escape(c) for c in p))
        out.append((r"(?<![\w.-])%s(?![\w.-])" % "/".join(rx), r"(['\"])%s\1" % rx[-1]))
    return list(dict.fromkeys(out))


def sets_line_refusal(text, top, globs):
    """DEC-1097 (2), readiness review 5 F1: the judge cannot place a path the shell builds at run time (a variable set
    on the line stays literal, decide._expand_token reads only the hook's own environment). So a Bash line that names
    the sets root (any spelling, an assignment's value included) is refused when it also
      (a) names a hidden folder as a path (a block glob's literal head, fixtures/evaluation/ dropped: runs/fresh-80,
          memory-verdict-2, ... with a / beside it), or that folder's last name as a quoted string ('fresh-80'); a
          glob with a wildcard before its end by its own parts (sets_line_keys, ACT-SETS-GLOBS-1);
      (b) holds a command substitution ($(...), `...`, <(...), >(...), $'...'), a change of folder aimed at the root
          (cd or pushd to it, -C, --chdir, --directory, chdir), or, from the word that names the root on, a shell
          variable ($!, $?, $$, $#, $-, $0 and an unassigned $HOME aside), a glob or brace (* ? [ {), or a cd or pushd.
    A plain --sets-root <root> with no variable, glob or cd after it stays allowed. The empty text: no refusal."""
    rx = "|".join(re.escape(s) for s in sorted(sets_root_spellings(top), key=len, reverse=True))
    marked = re.sub(r"(?<![\w.-])(?:%s)(?![\w.-])" % rx, _ROOT_MARK, text or "")
    at = marked.find(_ROOT_MARK)
    if at < 0:
        return ""
    mark = re.escape(_ROOT_MARK)
    for path_rx, name_rx in sets_line_keys(globs):
        if re.search(path_rx, marked):
            return SETS_LINE_REFUSAL.format(what="a hidden folder")
        if re.search(name_rx, marked):
            return SETS_LINE_REFUSAL.format(what="a hidden folder's name")
    if re.search(r"\$\(|`|[<>]\(|\$'", marked):
        return SETS_LINE_REFUSAL.format(what="a command substitution")
    if re.search(r"(?:^|[\s;&|(){}])(?:cd|pushd)\s+[^\s;&|]*" + mark, marked) or \
            re.search(r"(?:-C|--chdir|--directory)[=\s]*['\"]?" + mark, marked) or re.search(r"chdir\s*\(", marked):
        return SETS_LINE_REFUSAL.format(what="a change of folder")
    start = max(marked.rfind(c, 0, at) for c in " \t\n;&|") + 1
    tail = marked[start:]
    home_set = re.search(r"(?:^|[\s;&|(])(?:export\s+)?HOME=", marked)
    for m in re.finditer(r"\$(\{[^}]*\}?|[A-Za-z_][A-Za-z0-9_]*|[1-9@*_])", tail):
        if m.group(1) in ("HOME", "{HOME}") and not home_set:
            continue
        return SETS_LINE_REFUSAL.format(what="a shell variable after it")
    if re.search(r"[*?\[{]", tail):
        return SETS_LINE_REFUSAL.format(what="a glob after it")
    if re.search(r"(?:^|[\s;&|(){}])(?:cd|pushd)(?=[\s;&|)]|$)", tail):
        return SETS_LINE_REFUSAL.format(what="a change of folder after it")
    return ""


SESSION_BLOCK = "session_hidden"  # ACT-INDEP-WALLS-1
SESSION_REFUSAL = ("the call reaches {root}, which is refused to this session (ACT-INDEP-WALLS-1, path-map.yaml "
                   "session_hidden: {why})")
PATH_KEYS = ("file_path", "notebook_path", "path")


def session_rules(main):
    """ACT-INDEP-WALLS-1: the main tree's session_hidden block (a branch cannot weaken it): a list of entries, each a
    root outside every tree (a real path; not / or HOME), the roles refused it and the tickets (any name a ticket goes
    by; an empty list is every ticket), and why. [] with no block. A block not of that shape raises (fail closed)."""
    try:
        with open(os.path.join(main, PATH_MAP), encoding="utf-8") as f:
            lines = f.read().splitlines(keepends=True)
    except FileNotFoundError:
        return []
    at = [i for i, line in enumerate(lines) if re.match(SESSION_BLOCK + r"\s*:", line)]
    if not at:
        return []
    if len(at) > 1:
        raise RuntimeError(f"{PATH_MAP}: {SESSION_BLOCK} is written more than once")
    end = next((j for j in range(at[0] + 1, len(lines))
                if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
    from gov.guard.heldout import load_yaml_unique
    data = load_yaml_unique("".join(lines[at[0]:end]))
    block = data.get(SESSION_BLOCK) if isinstance(data, dict) else None
    if not isinstance(block, list) or not block:
        raise RuntimeError(f"{PATH_MAP}: {SESSION_BLOCK} is not a list of entries")
    out = []
    for e in block:
        top = os.path.expanduser(e.get("root")) if isinstance(e, dict) and isinstance(e.get("root"), str) else ""
        roles, tickets = (e.get("roles"), e.get("tickets")) if isinstance(e, dict) else (None, None)
        why = e.get("why") if isinstance(e, dict) else None
        if (not os.path.isabs(top) or os.path.realpath(top) in ("/", HOME)
                or not isinstance(roles, list) or not roles or not all(isinstance(r, str) and r for r in roles)
                or not isinstance(tickets, list) or not all(isinstance(t, str) and t for t in tickets)
                or not isinstance(why, str) or not why):
            raise RuntimeError(f"{PATH_MAP}: {SESSION_BLOCK}: an entry is not a root, roles, tickets and why")
        out.append((os.path.realpath(top), list(roles), list(tickets), why))
    return out


def session_applies(entry, mine, root, main, ticket):
    """Whether the entry names this session: one of its roles (the session's or the acting role), and, when the
    entry lists tickets, a name the session's ticket goes by (its id, file name or WBS id, in this tree or the main
    tree's .tickets). A ticket the guard cannot read raises (fail closed)."""
    _top, roles, tickets, _why = entry
    if not any(r in roles for r in mine if r):
        return False
    if not tickets:
        return True
    if not ticket:
        return False
    from gov.guard import reads
    here = reads._ticket(root, ticket)[0]
    # W2-111 (DEC-1187): the main tree's ticket is read only when it is another tree's (the same folder, the same
    # file: the same names, or the same refusal raised by the first read)
    there = here if os.path.realpath(root) == main else reads._ticket(main, ticket)[0]
    names = set(here) | set(there) | {ticket}
    return bool(names & set(tickets))


def session_refusal(entry, tool, tin, seen_command, cwd):
    """Why this call reaches the entry's root, or "". File tools: a path they name (file_path, notebook_path, path,
    and a Glob pattern's literal head), real, at or under the root, or a Grep or Glob whose start is at or above it.
    Bash: the line rule of 2b with the root's parent as the root and the root's name as the hidden folder (a root
    whose parent is HOME: the root itself, no folder name), so a line naming the root, or its parent with the root's
    name, a substitution, a cd to it, or a variable, glob or cd after it, is refused; and the writes the guard
    resolves into it. A recursive search from HOME or /, and a script that opens the root in its own code, are let
    through (the limits of 2b; the sandbox's job)."""
    top, _roles, _tickets, why = entry
    msg = SESSION_REFUSAL.format(root=top, why=why)

    def real(p):
        return os.path.realpath(os.path.join(cwd or "/", os.path.expanduser(p)))

    if seen_command is not None:
        parent, name = os.path.dirname(top), os.path.basename(top)
        line = (sets_line_refusal(seen_command, parent, [name + "/**"]) if parent != HOME
                else sets_line_refusal(seen_command, top, ["**"]))
        if line:
            return msg
        shell, code = bash_writes_of(tin.get("command") or "", cwd)
        if any(isinstance(t, str) and t and inside(real(t), top) for t in shell + code):
            return msg
        return ""
    for k in PATH_KEYS:
        v = tin.get(k)
        if isinstance(v, str) and v:
            full = real(v)
            if inside(full, top):
                return msg
            if tool in ("Grep", "Glob") and k == "path" and inside(top, full):
                return msg
    if tool == "Glob":
        pat = tin.get("pattern")
        if isinstance(pat, str) and pat:
            parts = pat.split("/")
            n = next((i for i, p in enumerate(parts) if any(c in p for c in "*?[{")), len(parts))
            head = "/".join(parts[:n]) or "."
            base = tin.get("path") if isinstance(tin.get("path"), str) and tin.get("path") else cwd
            full = os.path.realpath(os.path.join(real(base or "/"), os.path.expanduser(head)))
            if inside(full, top) or inside(top, full):
                return msg
    return ""


WRITE_BLOCK = "write_refused"  # ACT-OPERATOR-1 (2d)
WRITE_REFUSAL = ("the call writes into {root}, which no session writes (ACT-OPERATOR-1, path-map.yaml write_refused: "
                 "{why})")


def write_rules(main):
    """ACT-OPERATOR-1 (2d): the main tree's write_refused block (a branch cannot weaken it): a list of entries, each a
    root outside every tree (a real path; not / or HOME), the names directly under it that stay writable (except),
    and why. [] with no block. A block not of that shape raises (fail closed)."""
    try:
        with open(os.path.join(main, PATH_MAP), encoding="utf-8") as f:
            lines = f.read().splitlines(keepends=True)
    except FileNotFoundError:
        return []
    at = [i for i, line in enumerate(lines) if re.match(WRITE_BLOCK + r"\s*:", line)]
    if not at:
        return []
    if len(at) > 1:
        raise RuntimeError(f"{PATH_MAP}: {WRITE_BLOCK} is written more than once")
    end = next((j for j in range(at[0] + 1, len(lines))
                if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
    from gov.guard.heldout import load_yaml_unique
    data = load_yaml_unique("".join(lines[at[0]:end]))
    block = data.get(WRITE_BLOCK) if isinstance(data, dict) else None
    if not isinstance(block, list) or not block:
        raise RuntimeError(f"{PATH_MAP}: {WRITE_BLOCK} is not a list of entries")
    out = []
    for e in block:
        top = os.path.expanduser(e.get("root")) if isinstance(e, dict) and isinstance(e.get("root"), str) else ""
        keep = e.get("except") if isinstance(e, dict) else None
        why = e.get("why") if isinstance(e, dict) else None
        if (not os.path.isabs(top) or os.path.realpath(top) in ("/", HOME)
                or not isinstance(keep, list)
                or not all(isinstance(k, str) and k and "/" not in k and k not in (".", "..") for k in keep)
                or not isinstance(why, str) or not why):
            raise RuntimeError(f"{PATH_MAP}: {WRITE_BLOCK}: an entry is not a root, its open folders and why")
        real = os.path.realpath(top)
        # an open folder by its own name under the real root, never followed: a link there to the rest of the
        # root resolves outside it and stays refused
        out.append((real, [os.path.join(real, k) for k in keep], why))
    return out


def write_refusal(entries, tool, tin, command, cwd):
    """Why this call writes into an entry's root outside its open folders, or "". A file tool by the path it names,
    real (links followed); a Bash line by the writes the guard resolves, the shell's own and its inline code's."""
    targets = []
    if tool in WRITE_TOOLS:
        targets = [tin.get("file_path") or tin.get("notebook_path")]
    elif command is not None:
        shell, code = bash_writes_of(command, cwd)
        targets = shell + code
    for t in targets:
        if not isinstance(t, str) or not t:
            continue
        full = os.path.realpath(os.path.join(cwd or "/", os.path.expanduser(t)))
        for top, keep, why in entries:
            if inside(full, top) and not any(inside(full, k) for k in keep):
                return WRITE_REFUSAL.format(root=top, why=why)
    return ""


_CLASSES = []


def classes():
    """SetsRoot, Judge (DEC-1082 (3)) and Narrow (ACT-SETS-GLOBS-1), made once the pinned judge is imported (inside
    main's fail-closed try)."""
    if _CLASSES:
        return _CLASSES[0]
    import copy
    import fnmatch
    from gov.guard import reads
    # R4 (W2-42a): the names the copied _Judge methods below use, from the pinned judge (the same helpers before and
    # after a re-pin); REV_REFUSAL, PLACE_REFUSAL, _blob_ref and _output_joined are this module's own copies.
    HIDDEN_REFUSAL = reads.HIDDEN_REFUSAL
    SECRET_REFUSAL = reads.SECRET_REFUSAL
    PolicyError = reads.PolicyError
    _ARCHIVE_VALUED = reads._ARCHIVE_VALUED
    _COUNT_RE = reads._COUNT_RE
    _GIT_GREP_VALUED = reads._GIT_GREP_VALUED
    _GIT_LOG_VALUED = reads._GIT_LOG_VALUED
    _GIT_QUIET = reads._GIT_QUIET
    _GIT_SIDES = reads._GIT_SIDES
    _NO_CONVERT = reads._NO_CONVERT
    _PATTERN_OPTIONS = reads._PATTERN_OPTIONS
    _Part = reads._Part
    _REV_FAULT = reads._REV_FAULT
    _git = reads._git
    _expand_token = reads._expand_token
    _options = reads._options
    _pathspecs = reads._pathspecs
    _x_top = reads._x_top
    matched = {}  # Narrow.match's answers, per tuple of globs, then per path (one hook run judges one call)
    listed = {}  # Narrow's folder listings, per folder (one hook run judges one call)

    class Narrow(reads._Part):
        """ACT-SETS-GLOBS-1: a part of sets_root_hidden's globs, under the sets root or in a tree. The judge walks each
        glob from its literal head, so fixtures/evaluation/*/hidden/** would walk the whole fixtures/evaluation folder,
        and runs/*/miss-classes.json the whole runs folder, in the sets root and in each of the trees (135 on
        2026-11-09: about 0.8 s on every call that asks whether a part holds files; 3.2 s on the real sets root under
        load). Here nothing is walked recursively but what the glob's ** covers: a wildcard part is one listing of the
        folders reached (fixtures/evaluation/*, runs/*), a literal part after it is joined and stat'ed (hidden,
        miss-classes.json, misses.jsonl), and only the folders a ** covers are walked, by the judge's own _walk (.git
        left out, the same file cap, strict as the judge's), each once. The files found are the judge's, link for link.
        A glob whose only wildcard is a trailing /** is walked exactly as before. Which paths are in the part (match, inside) is the judge's own, asked once per
        path for all the parts with the same globs: a revision's listing (git grep ... HEAD) asks each tree's part
        about the same names, and a glob with a wildcard is a pattern match, not a prefix (11.7 s for one such call
        in the rehearsal without this, 0.6 s before the ACT)."""

        caches = (matched, listed)  # per hook run; a check that times several walks in one process clears them

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._seen = matched.setdefault(tuple(self.globs), {})
            heads = ["/".join(g.split("/")[:next((i for i, p in enumerate(g.split("/")) if any(c in p for c in "*?[{")),
                                                  len(g.split("/")))]).rstrip("/") for g in self.globs]
            self._heads = None if any(not h for h in heads) else heads

        def match(self, rel):
            if rel in self._seen:
                return self._seen[rel]
            hit = bool(rel) and (self._heads is None or any(rel == h or rel.startswith(h + "/") for h in self._heads)) \
                and super().match(rel)
            self._seen[rel] = hit
            return hit

        def _listed(self, folder):
            """The entries of one folder as (name, a real folder), once per hook run for every part (the trees' parts
            and the sets root's ask for the same folders); a folder that cannot be listed, but for its absence, refuses
            when the part is strict (as the judge's _walk_fault)."""
            if folder not in listed:
                try:
                    with os.scandir(folder) as it:
                        listed[folder] = [(e.name, e.is_dir(follow_symlinks=False)) for e in it]
                except (FileNotFoundError, NotADirectoryError):
                    listed[folder] = []
                except OSError:
                    if self.strict:
                        raise reads.PolicyError(reads._WALK_FAULT) from None
                    listed[folder] = []
            return listed[folder]

        def _kind(self, path):
            """'dir' (a real folder), 'other' (a file, a link, anything else) or None (absent); strict as the judge."""
            try:
                st = os.lstat(path)
            except (FileNotFoundError, NotADirectoryError):
                return None
            except OSError:
                if self.strict:
                    raise reads.PolicyError(reads._WALK_FAULT) from None
                return None
            return "dir" if stat.S_ISDIR(st.st_mode) else "other"

        def _starts(self, g):
            """Where glob g's files can be, never by a recursive walk: its literal head as the judge takes it (links
            followed); each wildcard part by one listing of each folder reached (real folders only past it, .git left
            out, as os.walk goes); each literal part after a wildcard joined and stat'ed, never listed. Returns the
            paths, whether the rest of the glob is ** (walk each path) and whether a wildcard was crossed."""
            parts = g.split("/")
            n = next((i for i, p in enumerate(parts) if any(c in p for c in "*?[{")), len(parts))
            here = [os.path.join(self.root, *parts[:n])]
            for i in range(n, len(parts)):
                p = parts[i]
                if p == "**" or "{" in p:
                    return here, True, i > n
                last = i == len(parts) - 1
                nxt = []
                for c in here:
                    if any(ch in p for ch in "*?["):
                        nxt += [os.path.join(c, x) for x, is_dir in self._listed(c)
                                if x != ".git" and (last or is_dir) and fnmatch.fnmatchcase(x, p)]
                    elif p != ".git":
                        x = os.path.join(c, p)
                        if (self._kind(x) is not None) if last else (self._kind(x) == "dir"):
                            nxt.append(x)
                here = nxt
            return here, False, len(parts) > n

        @property
        def files(self):
            if self._files is None:
                found, walked = set(), set()

                def walk(start):
                    if start in walked:
                        return
                    walked.add(start)
                    for folder, dirs, names in reads._walk(start, self.strict):
                        dirs[:] = [d for d in dirs if d != ".git"]
                        found.update(f for f in (os.path.join(folder, x) for x in names) if self.inside(f))
                        if len(found) > reads._MOST_FILES:
                            raise reads.PolicyError(reads._LONG_PART)

                for g in self.globs:
                    starts, deep, crossed = self._starts(g)
                    for start in starts:
                        if deep and not crossed:
                            walk(start)  # the literal head, as the judge walks it (a link at the top followed)
                            continue
                        kind = self._kind(start)
                        if kind == "dir":
                            walk(start)  # a set's hidden/, or a folder with the glob's own name: all below it
                        elif kind == "other" and not deep:
                            if not crossed and os.path.isdir(start):
                                walk(start)  # a literal glob naming a link to a folder: followed, as the judge
                            elif not (crossed and os.path.isdir(start)) and self.inside(start):
                                found.add(start)  # a file (or a link to one, or a broken link): os.walk names it
                        if len(found) > reads._MOST_FILES:
                            raise reads.PolicyError(reads._LONG_PART)
                self._files = sorted(found)
            return self._files

    class SetsRoot(Narrow):
        """The sets root's hidden part. The guard walks it for file names only, never their text."""

    class Judge(reads._Judge):
        def listing(self, stages, cwd):
            """A listing the guard cannot place is refused as before, but for one case: only the sets root's part
            holds files, the listing is a real feed (not the stand-in for names read from a file: xargs -a, a while
            loop fed by a redirect), it starts outside the sets root, and none of its words names the sets root or
            a folder above it (~, /). Then the sets root cannot be what it lists, and the call is not refused for it."""
            why = super().listing(stages, cwd)
            if why != reads.RUNTIME_REFUSAL or cwd is None or stages == [["cat", "--"]]:
                return why
            tops = [p.root for p in self.parts if isinstance(p, SetsRoot)]
            if not tops or any(p.held() for p in self.parts if not isinstance(p, SetsRoot)):
                return why
            if any(reads._related(os.path.realpath(cwd), t) for t in tops):
                return why
            for words in stages:
                for w in words:
                    exp = reads._expand_token(w) or w
                    if not exp or (exp.startswith("-") and exp != "-"):
                        continue
                    full = os.path.realpath(os.path.join(cwd, exp))
                    if any(reads._related(full, t) for t in tops):
                        return why
            return ""

        # R4 (W2-42a, DECIDED-NOT-DONE 215): the product's _Judge.git, colon, placed, cat_file, patched, stored and ask,
        # copied as merged (b42e8628b835): revision-colon-paths are judged as reads of their paths, a git answer that is
        # no is a ruled refusal, git that cannot run (and the deadline) still refuse by the error path.
        def git(self, args: list[str], cwd: str) -> str:
            i, addr = 0, []  # the repository and tree the command addresses
            while i < len(args) and args[i].startswith("-"):
                if args[i] == "-C" and i + 1 < len(args):
                    cwd = os.path.join(cwd, _expand_token(args[i + 1]) or args[i + 1])
                elif args[i] in ("--git-dir", "--work-tree") and i + 1 < len(args):
                    addr.append(f"{args[i]}={args[i + 1]}")
                elif args[i].startswith(("--git-dir=", "--work-tree=")):
                    addr.append(args[i])
                i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
            sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
            hidden = [p for p in self.parts if p.strict]
            if sub not in ("show", "log", "diff", "grep", "whatchanged"):
                why = self.reads("git", args, cwd)
                # W2-42a R4: git cat-file is judged on for any session with a
                # refused part (the object's place), the other two for the hidden.
                if why or sub not in ("cat-file", "format-patch", "archive") or not (
                        hidden or (sub == "cat-file" and self.parts)):
                    return why
            dd = rest.index("--") if "--" in rest else len(rest)
            before, specs = rest[:dd], rest[dd + 1:]
            if sub in ("show", "log", "diff", "whatchanged"):
                # W2-42a: --output <file> is a write (the write rules judge it);
                # its file is no revision word.
                before = _output_joined(before)
            operands = [a for a in before if not a.startswith("-")]
            if sub == "grep":
                # W2-141 (F1): the engineer's own folder, with the pathspecs'
                # exclusions; the other parts as before.
                why = self._own_git(sub, rest, cwd)
                if why:
                    return why
                others = self._not_own()
                operands, options = _options(before, _GIT_GREP_VALUED)
                if _PATTERN_OPTIONS.isdisjoint(o for o, _ in options):
                    operands = operands[1:]
                specs = [o for o in operands if os.path.lexists(os.path.join(cwd, o))] + specs
                for s in specs or ["."]:
                    why = others.spec(s, cwd, True)
                    if why:
                        return why
                revs = [o for o in operands if not os.path.lexists(os.path.join(cwd, o))]
                if hidden and (revs or "--cached" in before) and self.covers(specs, cwd, hidden):
                    return self.stored(revs, "--cached" in before, cwd, addr, hidden)
                return ""
            if sub == "archive":  # its tree-ish, then its paths
                operands = _options(before, _ARCHIVE_VALUED)[0] + specs
                return self.stored(operands[:1], False, cwd, addr, hidden) if (
                    self.covers(operands[1:], cwd, hidden)) else ""
            # W2-42a R4: a revision-colon-path in git show or cat-file, or on a
            # side of git diff, is read as its path.
            diffing = sub == "diff" and "--no-index" not in before
            shown = []
            for o in (operands if sub in ("show", "cat-file") or diffing else []):
                exp = _expand_token(o)
                ref = _blob_ref(o if exp is None else exp)
                if ref is None:
                    continue
                shown.append(o)
                why = self.colon(sub, exp, ref, cwd, addr, hidden)
                if why:
                    return why
            if sub == "cat-file":
                return self.cat_file(before, operands, shown, cwd, addr)
            if diffing and shown:
                # git diff <blob> <blob>, or <blob> <file>: those paths alone, not
                # a tree; with a revision beside them it is judged as revisions.
                files = [o for o in operands if o not in shown]
                if all(os.path.lexists(os.path.join(cwd, _expand_token(o) or o)) for o in files):
                    for o in files:
                        why = self.word(o, cwd)
                        if why:
                            return why
                    for s in specs:
                        why = self.spec(s, cwd, True)
                        if why:
                            return why
                    return ""
            quiet = (any(a in _GIT_QUIET or a.startswith("--stat=") for a in before)
                     and not any(a in ("-p", "--patch", "-u") or a.startswith("-U")
                                 for a in before))
            if sub in ("log", "whatchanged"):
                patch = not quiet and any(a in ("-p", "--patch", "-u") or a.startswith("-U")
                                          for a in before)
            else:
                patch = sub == "format-patch" or not quiet and (
                    sub == "diff" or len(shown) < len(operands) or not operands)
            if patch and sub != "format-patch":  # with no pathspec, the whole tree
                others = copy.copy(self)
                others.parts = [p for p in self.parts if not p.strict]
                for s in specs or [self.root]:
                    why = others.spec(s, cwd, False)
                    if why:
                        return why
            # git show :/<text> names a commit by its message: a patch, too.
            patch = patch or any(o.startswith(":/") for o in shown if sub == "show")
            return self.patched(sub, before, specs, cwd, addr, hidden) if (
                patch and hidden) else ""

        def colon(self, sub: str, word: str | None, ref: tuple[str, str], cwd: str,
                  addr: list[str], hidden: list[_Part]) -> str:
            """W2-42a R4: why a revision-colon-path (*word*, None when the guard
            cannot expand it; *ref*, its revision and path) is refused: by the
            rule its path names, as a read; then, with a part refused to this
            session, when git does not resolve it (git show, git diff); a tree on
            a side of git diff shows its files, judged as a folder's."""
            rev, path = ref
            here = os.path.realpath(cwd)
            top = _x_top(here) or self.root
            local = path.startswith(("./", "../"))
            at = cwd if local else top
            names = self.spellings(path, at)
            if sub != "cat-file" and any(self.secret(p) for p in names):
                return SECRET_REFUSAL
            for part in (self.parts if sub != "cat-file" else []):
                if any(part.inside(p) for p in names) and not (
                        part.base and self.base_version(rev, part.rel(
                            os.path.abspath(os.path.join(at, path))))):
                    return part.reason
            # The hidden part's path names it in whichever tree (W2-84).
            rel = os.path.relpath(os.path.normpath(os.path.join(here if local else top, path)), top)
            inside = not rel.startswith("..")
            if any(h.inside(p) for h in hidden for p in names) or (
                    inside and any(h.match(rel) for h in hidden)):
                return HIDDEN_REFUSAL
            if not self.parts:
                return ""
            if word is None:
                return REV_REFUSAL
            kind = self.ask(cwd, addr, "cat-file", "-t", "--end-of-options", word)
            if kind is None:
                return REV_REFUSAL
            # The path starts at the top of the tree <rev> names (W2-42a R4).
            if not self.placed(rev, cwd, addr):
                return PLACE_REFUSAL
            if sub != "diff" or kind.strip() == "blob":
                return ""
            why = self.above(path, at)
            if why or not hidden:
                return why
            out = self.ask(cwd, addr, "ls-tree", "-r", "--full-tree", "--name-only", "-z",
                           "--end-of-options", word)
            if out is None or not inside:
                return REV_REFUSAL
            return HIDDEN_REFUSAL if any(h.match(os.path.normpath(os.path.join(rel, n)))
                                         for h in hidden for n in out.split("\0") if n) else ""

        def placed(self, rev: str, cwd: str, addr: list[str]) -> bool:
            """W2-42a R4: whether ``<rev>:<path>`` places its path at the
            repository's top: the index (an empty *rev*), a commit, a commit's
            ``^{tree}``, or the tree HEAD's top is. A subtree's id, or what git
            cannot answer, is not placed (fail closed)."""
            if not rev:
                return True
            base = rev
            while base.endswith("^{tree}"):
                base = base[:-len("^{tree}")]
            if base and self.ask(cwd, addr, "rev-parse", "--verify", "--quiet",
                                 "--end-of-options", base + "^{commit}") is not None:
                return True
            out = (self.ask(cwd, addr, "rev-parse", "--end-of-options", rev + "^{tree}",
                            "HEAD^{tree}") or "").split()
            return len(out) == 2 and out[0] == out[1]

        def cat_file(self, before: list[str], operands: list[str], shown: list[str],
                     cwd: str, addr: list[str]) -> str:
            """W2-42a R4: git cat-file of an object named by its id alone (no
            ``<rev>:<path>``) that it prints as a file's text (``-p``,
            ``--textconv``, ``--filters``, or ``<type> <object>``) and that is a
            blob: its path cannot be placed, so a session with a refused part is
            refused; ``-t``, ``-s``, ``-e`` and a commit or a tree stay open."""
            if not self.parts:
                return ""
            objs = [o for o in operands if o not in shown]
            typed = len(objs) >= 2  # <type> <object>
            if not (typed or any(a in ("-p", "--textconv", "--filters") for a in before)):
                return ""
            for o in objs[1:] if typed else objs:
                word = _expand_token(o)
                if word is None:
                    return REV_REFUSAL
                kind = self.ask(cwd, addr, "cat-file", "-t", "--end-of-options", word)
                if kind is None:
                    return REV_REFUSAL
                if kind.strip() == "blob":
                    return PLACE_REFUSAL
            return ""

        def patched(self, sub: str, before: list[str], specs: list[str], cwd: str,
                    addr: list[str], hidden: list[_Part]) -> str:
            """Why a patch shows the hidden part, asked of git in a fixed
            read-only form: the changed paths alone, filtered by the hidden
            globs, with the command's revisions and the options that widen or
            choose its sides; merges parent by parent (W2-84)."""
            sides, revs, paths, negated = [], [], [], False
            j = 0
            while j < len(before):
                a = before[j]
                if a in _GIT_SIDES or a.startswith(("--branches=", "--tags=", "--remotes=",
                                                    "--glob=")) or _COUNT_RE.fullmatch(a):
                    sides.append(a)
                elif a in ("-n", "--max-count") and j + 1 < len(before):
                    sides += before[j:j + 2]
                    j += 1
                elif a in _GIT_LOG_VALUED:
                    j += 1
                elif a == "--not":  # what follows is taken whole: never fewer sides
                    negated = True
                elif not a.startswith("-") and not (
                        sub == "show" and _blob_ref(_expand_token(a) or a)):
                    if os.path.lexists(os.path.join(cwd, a)):
                        paths.append(a)
                    else:
                        revs += ([e or "HEAD" for e in re.split(r"\.\.\.?", a.lstrip("^"))]
                                 if negated else [a])
                j += 1
            if "--no-index" in before:  # two files, no revision
                return HIDDEN_REFUSAL if any(h.inside(p) for a in paths for h in hidden
                                             for p in self.spellings(a, cwd)) else ""
            if not self.covers(paths + specs, cwd, hidden):
                return ""
            if sub == "diff":
                query = ["diff", *_NO_CONVERT]
            else:
                query = ["log", *_NO_CONVERT, "--format=", "--diff-merges=separate",
                         "--full-history"]
                counted = any(a in ("-n", "--max-count") or _COUNT_RE.fullmatch(a)
                              for a in sides)
                if sub == "show" and not counted:
                    query.append("--no-walk")
                if (sub == "format-patch" and len(revs) == 1 and ".." not in revs[0]
                        and not counted and "--root" not in before):
                    revs = [revs[0] + "..HEAD"]  # <since> means <since>..HEAD
            words = [_expand_token(w) for w in sides + revs]
            if None in words or "--stdin" in before:  # a revision it cannot resolve
                return REV_REFUSAL
            # Each revision must be a commit: git log passes over a blob or tree;
            # a message search (:/<text>) must name one.
            ends = [e + "^{commit}" for w in words[len(sides):] if not w.startswith(":/")
                    for e in re.split(r"\.\.\.?", w.lstrip("^")) if e]
            ends += [w for w in words[len(sides):] if w.startswith(":/")]
            if ends and self.ask(cwd, addr, "rev-parse", "--end-of-options", *ends, "--") is None:
                return REV_REFUSAL
            out = self.ask(cwd, addr, *query, *words[:len(sides)], "--end-of-options",
                           *words[len(sides):], "--", *_pathspecs(hidden))
            if out is None:
                return REV_REFUSAL
            return HIDDEN_REFUSAL if out.strip() else ""

        def stored(self, revs: list[str], cached: bool, cwd: str, addr: list[str],
                   hidden: list[_Part]) -> str:
            """Why a revision's tree (or the index) holds the hidden part, asked
            of git in a fixed read-only form (W2-84)."""
            for rev in revs:
                word = _expand_token(rev)
                if word is None:
                    return REV_REFUSAL
                prefix = os.path.normpath(word.partition(":")[2] or ".")
                prefix = "" if prefix == "." else prefix
                out = self.ask(cwd, addr, "ls-tree", "-r", "--full-tree", "--name-only", "-z",
                               "--end-of-options", word)
                if out is None:
                    return REV_REFUSAL
                if any(h.match(os.path.join(prefix, n) if prefix else n) for h in hidden
                       for n in out.split("\0") if n):
                    return HIDDEN_REFUSAL
            if cached:
                out = self.ask(cwd, addr, "ls-files", "--cached", "-z", "--", *_pathspecs(hidden))
                if out is None:
                    return REV_REFUSAL
                if out:
                    return HIDDEN_REFUSAL
            return ""

        @staticmethod
        def ask(cwd: str, addr: list[str], *args: str) -> str | None:
            """git's answer in the repository the command addresses; None when
            git answers it cannot, or the repository is named by a word the guard
            cannot expand (a ruled refusal, W2-42a R5); git that cannot be run is
            a fault, which refuses (fail closed)."""
            words = [_expand_token(a) for a in addr]
            if None in words:
                return None
            try:
                out = _git(cwd, *words, *args)
            except PolicyError:
                raise PolicyError(_REV_FAULT) from None
            return None if out.returncode else out.stdout

    # W2-111 (DEC-1187; S8's rule, the product's gov.guard.reads._TreePart of r4): each tree's part is made when a path
    # at, in or above the tree is judged. A part was made for every tree on every call (94 on the live repository,
    # 18 ms), though a call's paths lie in one or two of them. Every answer is the made part's: a path not below the
    # root is in no part of the tree (rel() is None, match(None) is False); a path that is not at, in or above the root
    # is at or above none of its literal folders (each at or below the root); below() keeps the part's own first test.
    # The globs are the evaluation sets' and the block's, checked as text paths (_paths_ok), so making a part cannot
    # raise: making it later changes no refusal into an allow.
    def tree_part(base):
        class TreePart(base):
            def __init__(self, root, globs, reason):  # no set-up of the part yet
                self.root, self.globs, self.reason, self.base = root, globs, reason, None
                self.strict = reason == reads.HIDDEN_REFUSAL
                self._made = None

            def made(self):
                """The tree's part, made once."""
                if self._made is None:
                    self._made = base(self.root, self.globs, self.reason)
                return self._made

            @property
            def lead(self):
                return self.made().lead

            @property
            def rx(self):
                return self.made().rx

            @property
            def literals(self):
                return self.made().literals

            def inside(self, path):
                return self.rel(path) is not None and self.made().inside(path)

            def match(self, rel):
                return self.made().match(rel)

            def under(self, path):
                return reads._related(path, self.root) and self.made().under(path)

            def held(self):
                return self.made().held()

            @property
            def files(self):
                return self.made().files

            def below(self, folder):
                if not folder or (self.strict and not reads._related(folder, self.root)):
                    return []
                return self.made().below(folder)
        return TreePart

    _CLASSES.append((SetsRoot, Judge, Narrow))
    _LAZY.append((tree_part(reads._Part), tree_part(Narrow)))
    return _CLASSES[0]


_LAZY = []


def tree_parts():
    """W2-111: the lazy tree parts (TreePart of the judge's _Part, TreeNarrow of Narrow), made with ``classes``."""
    classes()
    return _LAZY[0]


def inside(path, folder):
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def located(path, trailing):
    """Where a delete lands: the folders above it with their links followed, the last name as it is (rm removes a
    link, not what it points to), or followed too when the word ends in / or is . or .."""
    path = os.path.normpath(path)
    if trailing or os.path.basename(path) in ("", ".", ".."):
        return os.path.realpath(path)
    return os.path.join(os.path.realpath(os.path.dirname(path)), os.path.basename(path))


def holders(main):
    """The folders whose deletion, or the deletion of a folder above them, is catastrophic."""
    return [main, os.path.join(main, ".git"), os.path.join(main, ".gov-runtime", "scratch"), WORKTREES,
            os.path.realpath(RUNS), SCRATCH, SHM, HOME]


def delete_refusal(path, main, strict):
    """Why deleting ``path`` is catastrophic, or None. ``strict``: the word names the path (every check);
    otherwise it is the path an empty variable would give, judged only for the folders that hold the project and
    for a .git (an honest ``rm -f "$out/x"`` with ``out=$(mktemp -d)`` is not refused)."""
    if ".git" in path.split("/") and not inside(path, SCRATCH):
        return f"{path} is (or is inside) a repository's .git"
    if any(inside(h, path) for h in holders(main)):
        return f"{path} is the repository's root or a folder that holds the project, its worktrees or its scratch"
    if not strict:
        return None
    if inside(path, main):
        return None  # the main tree's tracked files: checked together, below
    if inside(path, WORKTREES) or inside(path, os.path.realpath(RUNS)) or inside(path, SCRATCH) or inside(path, SHM):
        return None
    return (f"{path} is outside the project (the main tree, ~/gov-os-worktrees/, ~/gov-os-runs/) and its scratch "
            "(/tmp, /dev/shm, .gov-runtime/scratch/)")


def tracked_in(main, paths):
    """The first of ``paths`` (inside the main tree) that is a tracked file or holds one; raises when git cannot
    tell (the caller refuses: fail closed)."""
    rels = [os.path.relpath(p, main) for p in paths]
    out = subprocess.run(["git", "--literal-pathspecs", "-C", main, "ls-files", "-z", "--"] + rels,
                         capture_output=True, timeout=10)
    if out.returncode != 0:
        raise RuntimeError("git ls-files failed in " + main)
    files = [f.decode("utf-8", "replace") for f in out.stdout.split(b"\0") if f]
    for rel, path in zip(rels, paths):
        if any(f == rel or f.startswith(rel.rstrip("/") + "/") for f in files):
            return path
    return None


def crude_deletes(command, cwd):
    """rm's operands in a command the scan cannot read (ACT-GUARD-FIX-4): each word after rm up to the next
    separator, expanded by the product's expansion; a word that does not expand is judged as if its variables
    were empty."""
    import shlex
    from bash_writes import emptied
    from gov.guard.decide import _expand_token
    found = []
    for m in CRUDE_RM.finditer(command.replace("\\\n", "")):
        try:
            words = shlex.split(m.group(1))
        except ValueError:
            words = m.group(1).split()
        for w in words:
            if w.startswith("-") and len(w) > 1:
                continue
            w = w.strip("'\"")
            exp = _expand_token(w)
            how = "names" if exp is not None else "if-empty"
            exp = exp if exp is not None else emptied(w)
            if not exp:
                continue
            found.append((w, exp if os.path.isabs(exp) else os.path.join(cwd, exp), how))
    return found


def rm_refusal(command, cwd, root):
    """Why this Bash command's rm is catastrophic, or None (every role; DEC-1050 (8))."""
    if not re.search(r"(?<![\w.-])rm(?![\w.-])", command):
        return None
    judged = bash_judgement(command, cwd)
    deletes = judged.deletes if judged is not None else []
    if judged is None or judged.recovered:
        deletes = deletes + crude_deletes(command, cwd)  # a command only a second reading read: its rm read crudely too
    if not deletes:
        return None
    main = main_tree(root)
    in_main = []
    for word, path, how in deletes:
        trailing = word.endswith("/") or word.endswith("/.")
        paths = [path]
        if any(c in os.path.basename(path.rstrip("/")) or c in os.path.dirname(path) for c in "*?["):
            paths = sorted(glob.glob(path)) or [path]
            if len(paths) > MOST_GLOB:
                return f"rm {word} names more than {MOST_GLOB} paths, too many to check"
        for p in paths:
            where = located(p, trailing)
            why = delete_refusal(where, main, how == "names")
            if why:
                if how != "names":
                    why = (f"rm {word} deletes {where} if a variable in it that the guard cannot resolve is empty, "
                           f"and {why}; set the variable in this command, or write ${{NAME:?}}")
                return why
            if how == "names" and inside(where, main):
                in_main.append(where)
    if in_main:
        try:
            hit = tracked_in(main, list(dict.fromkeys(in_main)))
        except Exception:
            return "the guard could not check whether this rm deletes the main tree's tracked files"
        if hit:
            return (f"{hit} is (or holds) the main tree's tracked files; use git rm in a worktree, or ask the owner")
    return None


# -- the install check, PATH read once and only for a download (W2-111, DEC-1184 (3), DEC-1187) --------------------

_PATH_READ = {}


def _path_folders():
    """The real folders of the current PATH, read once per PATH value (r4's gov.guard.install._path_folders)."""
    value = os.environ.get("PATH", "")
    found = _PATH_READ.get(value)
    if found is None:
        found = frozenset(os.path.realpath(d) for d in value.split(":") if d)
        _PATH_READ.clear()
        _PATH_READ[value] = found
    return found


def has_install(command):
    """gov.guard.install.has_install as W2-111 r4 made it (S7, in 0.1.1): the same answer for every command, with the
    real folders of PATH read only when a download names a target to compare them with, once per PATH value. The
    pinned 0.1.0 resolved every PATH folder on every Bash call (46 in a real session, 27 under /mnt/c) before it
    looked at the command. From 0.1.1 the product's own is used; until then this copy, over the pinned module's own
    helpers (the same code in 0.1.0 and 0.1.1). Hook-local until 0.1.1."""
    from gov.guard import install
    if hasattr(install, "_path_folders"):  # 0.1.1 on: the product's own
        return install.has_install(command)
    for seg in install._segments(command):
        cs = install._split(seg, install._is_pipe)
        # Pipe to shell: curl/wget ... | sh/bash
        if len(cs) >= 2:
            ln, _ = install._head(cs[-1])
            if ln in install._SH and any(
                    install._head(c)[0] in ("curl", "wget") for c in cs[:-1]):
                return True
        for pcmd in cs:
            nm, args = install._head(pcmd)
            # Strip version suffix (pip3.11 -> pip, pip2 -> pip,
            # python2.7 -> python): any trailing digits-and-dots.
            j = len(nm)
            while j > 0 and (nm[j - 1].isdigit() or nm[j - 1] == '.'):
                j -= 1
            if 0 < j < len(nm) and nm[j].isdigit():
                nm = nm[:j]
            # Package-manager install
            if nm in install._PKG:
                if "install" in args:
                    return True
                if nm == "npm":
                    nopt = next((a for a in args if a[:1] != "-"), "")
                    if nopt == "i":
                        return True
            elif nm in ("python", "python3"):
                if (len(args) >= 3 and args[0] == "-m"
                        and args[1] == "pip" and "install" in args[2:]):
                    return True
            elif nm == "uv":
                if install._uv_install(args):
                    return True
            elif nm == "uvx":
                return True
            # Binary download into a PATH directory
            if nm in ("curl", "wget"):
                t = install._download_target(nm, args)
                if t is not None:
                    t = os.path.expanduser(t)
                    if os.path.isabs(t) \
                            and os.path.realpath(
                                os.path.dirname(t)) in _path_folders():
                        return True
    return False


def answer(decision, reason, rule):
    record(decision, rule)  # ACT-GUARD-CALLLOG-1: never raises, never changes the decision
    out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                  "permissionDecisionReason": reason + " (DEC-953 item 2)"}}
    sys.stdout.write(json.dumps(out))
    sys.exit(0)


def deadline(signum, frame):
    answer("deny", "the guard could not decide in 20 seconds, so the call is refused", "deadline")


def under_acceptance(path, root, cwd):
    if not isinstance(path, str) or not path:
        return False
    full = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    rel = os.path.relpath(full, os.path.realpath(root))
    return rel == ACCEPTANCE.rstrip("/") or rel.startswith(ACCEPTANCE)


def in_a_trees_tests(path, root, cwd):
    """A path in the acceptance tests of a tree of this repository (ACT-GUARD-FIX-4): this tree, its worktrees and
    run clones (tree_roots), or any folder under ~/gov-os-worktrees/ or ~/gov-os-runs/ (the homes of the project's
    trees, a removed one included); not a scratch folder elsewhere whose name holds tests/acceptance (row 81)."""
    if not isinstance(path, str) or not path:
        return False
    full = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    if any(under_acceptance(full, tree, cwd) for tree in tree_roots(root)):
        return True
    homes = (WORKTREES, os.path.realpath(RUNS))
    return any(inside(full, h) for h in homes) and "/tests/acceptance/" in full + "/"


def main():
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(20)
    data = json.loads(sys.stdin.read() or "{}")
    _CALL["event"] = data  # ACT-GUARD-CALLLOG-1: hashed, never written
    tool = data.get("tool_name") or ""
    tin = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    _CALL["root"] = root
    cwd = data.get("cwd") or root
    role = (os.environ.get("GOV_ROLE") or "").strip()
    ticket = os.environ.get("GOV_TICKET")
    from gov.guard import reads
    from gov.guard.heldout import load_held_out, names_held_out
    use_fast_yaml()  # W2-111 (DEC-1187): the same answers and refusals, through libyaml, each text once
    acting = reads.acting_role(role, data.get("agent_type"))
    command = tin.get("command") if tool == "Bash" and isinstance(tin.get("command"), str) else None

    # R5 (W2-42a): a path field that is no path is refused by its rule, before a rule resolves it.
    if _no_path(tool, tin):
        answer("deny", NO_PATH_REFUSAL, "no-path")

    # Rule 2, the held-out material: every role, any tool that names or reaches it.
    if names_held_out(tool, tin, root, cwd, load_held_out(root)):
        answer("deny", "the call names or reaches the held-out material", "2-heldout")

    # Rules 2 and 3, the hidden half and secrets: the product's read judge with only these parts.
    SetsRoot, Judge, Narrow = classes()
    TreePart, TreeNarrow = tree_parts()  # W2-111: each tree's part made when a path at, in or above it is judged
    mine = list(dict.fromkeys((role, acting)))
    hidden = []
    for r in mine:
        hidden += reads._hidden(root, r, ticket)
    parts = [TreePart(t, hidden, reads.HIDDEN_REFUSAL) for t in tree_roots(root)] if hidden else []
    # DEC-1082 (3): the sets root outside the repository. The main tree's block names the root, its globs and the roles
    # refused them. To those globs are added the hidden globs of each set that measures the role, from the main tree's
    # map (an older branch's map cannot drop a set). They are refused under the sets root and in every tree.
    main = main_tree(root)
    rule = sets_root_rule(main)
    sets_parts = []
    if rule:
        top, globs, refused = rule
        outside = list(globs) if any(r in refused for r in mine if r) else []
        for r in mine:
            outside += reads._hidden(main, r, ticket)
        outside = list(dict.fromkeys(outside))
        if outside:
            sets_parts = [SetsRoot(top, outside, reads.HIDDEN_REFUSAL)] + \
                         [TreeNarrow(t, outside, reads.HIDDEN_REFUSAL) for t in tree_roots(root)]
    parts += sets_parts
    seen = tin
    if command is not None:
        # ACT-GUARD-FIX-3: a heredoc that cat or tee takes as data is no read; $((n+6)) is no listing.
        import bash_writes
        seen = dict(tin, command=bash_writes.reads_view(command))
    why = Judge(root, parts).tool(tool, seen, cwd)
    if why:
        answer("deny", why, judge_rule(why))

    # DEC-1097 (2), readiness review 5 F1: for the roles the block refuses, a Bash line that names the sets root and
    # also names a hidden folder, or builds a path after it (a variable, a substitution, a glob, a cd), is refused: the
    # judge above cannot place a path the shell makes at run time.
    if rule and command is not None and any(r in refused for r in mine if r):
        why = sets_line_refusal(seen["command"], top, outside)
        if why:
            answer("deny", why, "2b-line")

    # DEC-1082 (3): no write into those hidden folders by the roles refused them. Only a write whose target the guard
    # works out is judged; one it cannot work out is let through, as for rules 1 and 5 (G-1, G-2).
    if sets_parts:
        targets = []
        if tool in WRITE_TOOLS:
            targets = [tin.get("file_path") or tin.get("notebook_path")]
        elif command is not None:
            shell, code = bash_writes_of(command, cwd)
            targets = shell + code
        for t in targets:
            if isinstance(t, str) and t:
                full = os.path.realpath(os.path.join(cwd, os.path.expanduser(t)))
                if any(p.inside(full) for p in sets_parts):
                    answer("deny", SETS_WRITE_REFUSAL, "2b-write")

    # ACT-INDEP-WALLS-1 (2c): a folder outside every tree refused to named sessions only (SANDBOX-GUARD-EXP-1's tuner:
    # ~/.claude/projects). The ticket is read only when a role matches, so no other session pays for it.
    for entry in session_rules(main):
        if session_applies(entry, mine, root, main, ticket):
            why = session_refusal(entry, tool, tin, seen["command"] if command is not None else None, cwd)
            if why:
                answer("deny", why, "2c")

    # ACT-OPERATOR-1 (2d): folders outside every tree that no session writes (the operator agent's folder but its
    # queue/, the guard's call log), every role, by the writes the guard resolves. Read only for a write tool or Bash.
    if tool in WRITE_TOOLS or command is not None:
        rules_w = write_rules(main)
        if rules_w:
            why = write_refusal(rules_w, tool, tin, command, cwd)
            if why:
                answer("deny", why, "2d")

    # G-14 (DEC-1052), role separation: what the main tree's path map's role_paths: denies the session's role and
    # the acting role to read, by simple path checks (role_reads.py beside this file). No section, no check.
    if tool in ("Read", "NotebookRead", "Grep", "Bash"):
        import role_reads
        from gov.guard.decide import _expand_token
        why = role_reads.refusal(main, os.path.realpath(root), tool, seen, cwd,
                                 [r for r in dict.fromkeys((role, acting)) if r], ticket,
                                 lambda: tree_roots(root), _expand_token)
        if why:
            answer("deny", why, "g14")

    # rm, every role: free but for the catastrophic (ACT-GUARD-FIX-4, DEC-1050 (8)).
    if command is not None:
        why = rm_refusal(command, cwd, root)
        if why:
            answer("deny", "a catastrophic delete: " + why, "rm")

    # Rule 5, reviewers and auditors write only their own outcomes. A Bash write whose target the guard cannot work
    # out is let through (ACT-GUARD-FIX-4, G-2): a stray write shows in the reviewed tree's git status.
    if acting in REVIEWERS or role in REVIEWERS:
        targets, made = [], set()
        if tool in WRITE_TOOLS:
            targets = [tin.get("file_path") or tin.get("notebook_path")]
        elif command is not None:
            targets = bash_writes_of(command, cwd)[0]  # the shell's own writes: rule 5 never read code
            made = bash_made(command, cwd)
        if targets and not all(review_may_write(t, root, cwd, made) for t in targets):
            answer("deny", "a reviewer or auditor writes only its own review or audit record (docs/probes/, "
                           "docs/audit/, docs/assessment/, .gov-runtime/scratch/orchestrator/reviews/), its own "
                           "scratch, or /tmp", "5")

    # Rule 1, acceptance tests: written only by the independent test designer. A Bash write whose target the guard
    # cannot work out is let through (ACT-GUARD-FIX-4, G-1): the landing refuses a commit touching the tests
    # without Role: independent-test-designer.
    if acting != TEST_DESIGNER and role != TEST_DESIGNER:
        targets, code = [], []
        if tool in WRITE_TOOLS:
            targets = [tin.get("file_path") or tin.get("notebook_path")]
        elif command is not None:
            targets, code = bash_writes_of(command, cwd)
        # Code's resolved writes into any tree's acceptance tests refuse too, as since ACT-GUARD-FIX-3; a tree of this
        # repository (tree_roots), not any folder whose name holds tests/acceptance (ACT-GUARD-FIX-4: row 81, a
        # scratch repository in /tmp).
        if any(under_acceptance(t, root, cwd) for t in targets + code) or \
                any(in_a_trees_tests(t, root, cwd) for t in code):
            answer("deny", "only the independent test designer writes the acceptance tests (MR-3)", "1")

    # Rule 4, installs.
    if tool == "Bash":
        from gov.guard.install import has_sudo  # has_install: this file's (W2-111, the PATH read once)
        command = tin.get("command") or ""
        if has_sudo(command):
            answer("deny", "sudo is refused to every session", "4-sudo")
        if has_install(command):
            # Only the CTO's own session asks the owner: the orchestrator role on the coordination ticket (W2-00).
            # Every other session, leads (orchestrator on a ticket of their own) included, is refused (DEC-957).
            cto = role == "orchestrator" and acting == "orchestrator" and reads._ticket(root, ticket)[1] == CTO_WBS
            if cto:
                answer("ask", "an install needs the owner's approval", "4-ask")
            answer("deny", "installs are refused here: raise the install as a P1 escalation to the CTO, who asks "
                           "the owner", "4-install")
    record("allow", "none")  # ACT-GUARD-CALLLOG-1
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # fail closed
        record("deny", "error")  # ACT-GUARD-CALLLOG-1: never raises
        sys.stderr.write(f"guard (DEC-953): could not decide: {exc}; refused\n")
        sys.exit(2)
