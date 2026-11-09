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


_JUDGED = {}


def bash_judgement(command, cwd):
    """ACT-GUARD-FIX-3: what ``command`` writes, read by bash_writes.py with the product's parser; None when the
    command cannot be read for certain. Read once per call of the hook."""
    if (command, cwd) in _JUDGED:
        return _JUDGED[(command, cwd)]
    import bash_writes
    from gov.guard.decide import _UNRESOLVABLE, _expand_token, _extract_bash_write_targets
    if bash_writes.SENT != _UNRESOLVABLE:
        raise RuntimeError("bash_writes.SENT differs from the parser's sentinel")
    try:
        judged = bash_writes.judge(command, cwd, _extract_bash_write_targets, _expand_token)
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
    from gov.guard.decide import _extract_bash_write_targets
    from bash_writes import SENT
    judged = bash_judgement(command, cwd)
    if judged is None:
        return resolved(parse_both(_extract_bash_write_targets, command, cwd)), []
    return resolved(judged.shell), resolved([full for _targets, _scope, _code in judged.findings
                                             for raw, full in _targets if raw != SENT and full])


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
            return [os.path.realpath(line[9:]) for line in out.splitlines() if line.startswith("worktree ")]
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
    for pattern in ("*/.git", "*/*/.git", "*/*/*/.git", "*/*/*/*/.git"):
        roots += [os.path.realpath(os.path.dirname(g)) for g in glob.glob(os.path.join(RUNS, pattern))]
    return list(dict.fromkeys(roots))


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


def sets_line_refusal(text, top, globs):
    """DEC-1097 (2), readiness review 5 F1: the judge cannot place a path the shell builds at run time (a variable set
    on the line stays literal, decide._expand_token reads only the hook's own environment). So a Bash line that names
    the sets root (any spelling, an assignment's value included) is refused when it also
      (a) names a hidden folder as a path (a block glob's literal head, fixtures/evaluation/ dropped: runs/fresh-80,
          memory-verdict-2, ... with a / beside it), or that folder's last name as a quoted string ('fresh-80');
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
    keys = []
    for g in globs:
        parts = g.split("/")
        n = next((i for i, p in enumerate(parts) if any(c in p for c in "*?[{")), len(parts))
        head = "/".join(parts[:n])
        head = head[len("fixtures/evaluation/"):] if head.startswith("fixtures/evaluation/") else head
        if head:
            keys.append(head)
    for k in dict.fromkeys(keys):
        e = re.escape(k)
        if re.search(r"(?<=/)%s(?![\w.-])|(?<![\w.-])%s(?=/)" % (e, e), marked):
            return SETS_LINE_REFUSAL.format(what="a hidden folder")
        if re.search(r"(['\"])%s\1" % re.escape(k.rsplit("/", 1)[-1]), marked):
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
    names = set(reads._ticket(root, ticket)[0]) | set(reads._ticket(main, ticket)[0]) | {ticket}
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
    """SetsRoot and Judge (DEC-1082 (3)), made once the pinned judge is imported (inside main's fail-closed try)."""
    if _CLASSES:
        return _CLASSES[0]
    from gov.guard import reads

    class SetsRoot(reads._Part):
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

    _CLASSES.append((SetsRoot, Judge))
    return _CLASSES[0]


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
    deletes = judged.deletes if judged is not None else crude_deletes(command, cwd)
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
    acting = reads.acting_role(role, data.get("agent_type"))
    command = tin.get("command") if tool == "Bash" and isinstance(tin.get("command"), str) else None

    # Rule 2, the held-out material: every role, any tool that names or reaches it.
    if names_held_out(tool, tin, root, cwd, load_held_out(root)):
        answer("deny", "the call names or reaches the held-out material", "2-heldout")

    # Rules 2 and 3, the hidden half and secrets: the product's read judge with only these parts.
    SetsRoot, Judge = classes()
    mine = list(dict.fromkeys((role, acting)))
    hidden = []
    for r in mine:
        hidden += reads._hidden(root, r, ticket)
    parts = [reads._Part(t, hidden, reads.HIDDEN_REFUSAL) for t in tree_roots(root)] if hidden else []
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
                         [reads._Part(t, outside, reads.HIDDEN_REFUSAL) for t in tree_roots(root)]
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
        from gov.guard.install import has_install, has_sudo
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
