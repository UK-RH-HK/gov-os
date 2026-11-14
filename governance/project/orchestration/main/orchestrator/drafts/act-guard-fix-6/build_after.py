"""ACT-GUARD-FIX-6's builder: the after copies of .claude/hooks/pretooluse.py and .claude/hooks/bash_writes.py.

python3 -B -I build_after.py <repo> <out dir>

Reads, from <repo> (a checkout of w2/integrate's head): the live hook files (the before), and the product's merged code
(src/gov/guard/bash_writes.py, decide.py, reads.py, W2-42a, DAEO-03ub). Writes <out>/bash_writes.py and
<out>/pretooluse.py. Nothing in <repo> is written.

bash_writes.py = a three-way merge (live before, base = ACT-GUARD-FIX-3's file e662684a1, theirs = the product's
module), its three conflicts resolved (see merge_conflicts below), then the hook's own additions on top:
  - Judgement.adopt takes a nested judgement's deletes and made too (the product's adopt took writes and unread);
  - a foreign reader's body takes its deletes; a command only a second reading could read carries those readings'
    deletes and ``recovered`` (the hook reads its rm crudely too);
  - git archive -o / --output (DECIDED-NOT-DONE 215, the archive form);
  - line_write_targets: the product's decide._line_write_targets, copied (R3's here-strings, unmatched globs literal),
    its module names bound from the pinned judge's decide at call time.
pretooluse.py = the live file with: the parser wiring (the copied line parser, not the pinned decide's), rule 1's and
rule 5's targets taking Judgement.writes, the crude rm read for a recovered command, R5's no-path refusal, and R4's
copies (reads.py's _blob_ref, _output_joined, REV_REFUSAL, PLACE_REFUSAL and _Judge.git, colon, placed, cat_file,
patched, stored, ask, copied into the hook's Judge subclass, W2-42a's own return, DECIDED-NOT-DONE 215)."""
import ast
import os
import re
import subprocess
import sys
import tempfile

repo, out = sys.argv[1], sys.argv[2]
HOOKS = ".claude/hooks/"
os.makedirs(out, exist_ok=True)


def read(rel):
    with open(os.path.join(repo, rel), encoding="utf-8") as handle:
        return handle.read()


def git_show(rev, rel):
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{rel}"], check=True, capture_output=True, text=True).stdout


def once(text, old, new, count=1):
    assert text.count(old) == count, (text.count(old), old[:120])
    return text.replace(old, new)


def source_of(path, qualname):
    """(source segment dedented by its indent, ast node) of a top-level def or Class.def in a product file."""
    src = read(path)
    tree = ast.parse(src)
    lines = src.split("\n")
    node = tree
    for part in qualname.split("."):
        node = next(n for n in (node.body if hasattr(node, "body") else []) if getattr(n, "name", None) == part)
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return "\n".join(lines[start - 1:node.end_lineno]), node


# ---- bash_writes.py ---------------------------------------------------------------------------------------------

live = read(HOOKS + "bash_writes.py")
base = git_show("e662684a1", HOOKS + "bash_writes.py")
product = read("src/gov/guard/bash_writes.py")
with tempfile.TemporaryDirectory() as tmp:
    paths = {name: os.path.join(tmp, name) for name in ("ours", "base", "theirs")}
    for name, text in (("ours", live), ("base", base), ("theirs", product)):
        with open(paths[name], "w", encoding="utf-8") as handle:
            handle.write(text)
    subprocess.run(["git", "merge-file", "-L", "live", "-L", "base", "-L", "product", paths["ours"], paths["base"],
                    paths["theirs"]], check=False)
    with open(paths["ours"], encoding="utf-8") as handle:
        merged = handle.read()
pattern = re.compile(r"<<<<<<< live\n(.*?)=======\n(.*?)>>>>>>> product\n", re.S)
found = pattern.findall(merged)
assert len(found) == 3, len(found)
step = []


def resolve(m):
    mine, theirs = m.group(1), m.group(2)
    step.append(1)
    if len(step) == 1:      # the hook's emptied() and _PARAM (FIX-4) beside the product's _shell_script (W2-42a's F1)
        return mine + "\n\n" + theirs
    if len(step) == 2:      # Judgement.__init__: the hook's deletes and made beside the product's writes and unread
        return mine + theirs
    return theirs           # a nested judgement is taken in by the product's adopt (which gains deletes and made)


merged = pattern.sub(resolve, merged)
bw = merged
bw = once(bw, '''        """A nested judgement's product lists, taken into this one."""
        self.writes += sub.writes
        self.unread += sub.unread
''', '''        """A nested judgement's product lists, taken into this one (the hook's ``deletes`` and ``made`` too)."""
        self.writes += sub.writes
        self.unread += sub.unread
        self.deletes += sub.deletes
        self.made += sub.made
''')
bw = once(bw, '''        self.findings += sub.findings
        self.deletes += sub.deletes
        self.made += sub.made
''', '''        self.findings += sub.findings
''', 2)
bw = once(bw, '''        self.writes += [SENT if t.startswith(UNKNOWN) else t for t in sub.targets()]
''', '''        self.writes += [SENT if t.startswith(UNKNOWN) else t for t in sub.targets()]
        self.deletes += sub.deletes  # the hook (ACT-GUARD-FIX-4): an rm in a body an unknown reader may run
''')
bw = once(bw, '''    out = Judgement(parse, expand)
    out.writes = found + list(parse(command, cwd) or [])
''', '''    out = Judgement(parse, expand)
    out.recovered = True  # the hook (ACT-GUARD-FIX-6): only a second reading read it; its rm is read crudely too
    out.deletes = deletes
    out.writes = found + list(parse(command, cwd) or [])
''')
bw = once(bw, "    found = []\n    for base, legacy, opened in product(", "    found, deletes = [], []\n    for base, legacy, opened in product(")
bw = once(bw, "        found += again.targets()\n    if not found:", "        found += again.targets()\n        deletes += again.deletes\n    if not found:")
bw = once(bw, "        self.writes, self.unread = [], []\n", '''        self.writes, self.unread = [], []
        self.recovered = False  # set by ``judge`` on a command only a second reading could read (ACT-GUARD-FIX-6)
''')
bw = once(bw, '''                elif w.startswith("--output="):
                    out.append((w[len("--output="):], where))
    elif name == "dd":''', '''                elif w.startswith("--output="):
                    out.append((w[len("--output="):], where))
        elif sub == "archive":
            # DECIDED-NOT-DONE row 215 (W2-42a r4 return, the archive form): git archive -o <file>, -o<file>,
            # --output <file> and --output=<file> write that file; a word after -- is a path, no option.
            for k, w in enumerate(rest):
                if w == "--":
                    break
                if w in ("-o", "--output") and k + 1 < len(rest):
                    out.append((rest[k + 1], where))
                elif w.startswith("--output="):
                    out.append((w[len("--output="):], where))
                elif w.startswith("-o") and len(w) > 2 and not w.startswith("--"):
                    out.append((w[2:], where))
    elif name == "dd":''')

# the module docstring: say what this file is now
bw = once(bw, """ACT-GUARD-FIX-4 (DEC-1050 (8), (12)): the hook's rules 1 and 5 use only the targets this module resolves""",
          """ACT-GUARD-FIX-6 (DEC-1174 (1), DEC-1133 (2)): this file is W2-42a's merged product module (``gov.guard.bash_writes``,
DAEO-03ub, closed 2026-11-14) merged by a three-way merge with this hook's own FIX-4 additions kept (``deletes``,
``made``, ``emptied``); ``line_write_targets``, at the end, is a copy of ``gov.guard.decide._line_write_targets`` (the
product's line parser: R3's here-strings, an unmatched glob as its literal word). A heredoc's body, comments, here-strings,
a shell given options and the here-string data run as code are read as the product reads them.

ACT-GUARD-FIX-4 (DEC-1050 (8), (12)): the hook's rules 1 and 5 use only the targets this module resolves""")

_, line_node = source_of("src/gov/guard/decide.py", "_line_write_targets")
decide_src = read("src/gov/guard/decide.py")
dl = decide_src.split("\n")
body_start = line_node.body[0].end_lineno  # the docstring's last line
head = "\n".join(dl[line_node.lineno - 1:body_start])
rest = "\n".join(dl[body_start:line_node.end_lineno])
head = once(head, "def _line_write_targets(command: str, cwd: str, literal_globs: bool = True) -> list[str] | None:",
            "def line_write_targets(command, cwd, literal_globs=True):")
glob_re = next(ln for ln in dl if ln.startswith("_GLOB_OPTIONS_RE = "))
names = ["_ASSIGN_RE", "_CP_AS_LINK", "_CP_REPLACING", "_MOST_LANDED", "_UNRESOLVABLE", "_copy_args", "_expand_token",
         "_is_punct", "_option_after_operand"]
prelude = ("    import glob\n    import stat\n    from gov.guard import decide as _decide, runs\n"
           "    from gov.util.patterns import _has_glob\n"
           + "".join(f"    {n} = _decide.{n}\n" for n in names))
tail = f'''

# -- the product's line parser, copied (ACT-GUARD-FIX-6, DEC-1174 (1), DEC-1133 (2)) ---------------------------------
# ``gov.guard.decide._line_write_targets`` of W2-42a (DAEO-03ub): one shell line's write targets; a here-string's word is
# its text (R3), an unmatched glob is the literal word bash passes. The names it uses from ``decide`` are bound at each
# call, from the pinned judge, so the copy reads the same helpers the pinned judge itself has, before and after a
# re-pin.

{glob_re}
GLOB_OPTIONS_RE = _GLOB_OPTIONS_RE  # the name the hook's parser wiring reads


{head}
{prelude}{rest}
'''
bw = bw.rstrip("\n") + "\n" + tail
with open(os.path.join(out, "bash_writes.py"), "w", encoding="utf-8") as handle:
    handle.write(bw)

# ---- pretooluse.py ----------------------------------------------------------------------------------------------

pt = read(HOOKS + "pretooluse.py")

# 1. the parser wiring
pt = once(pt, '''    import bash_writes
    from gov.guard.decide import _UNRESOLVABLE, _expand_token, _extract_bash_write_targets
    if bash_writes.SENT != _UNRESOLVABLE:
        raise RuntimeError("bash_writes.SENT differs from the parser's sentinel")
    try:
        judged = bash_writes.judge(command, cwd, _extract_bash_write_targets, _expand_token)
    except bash_writes.Unreadable:
        judged = None
''', '''    import bash_writes
    from gov.guard.decide import _UNRESOLVABLE, _expand_token
    if bash_writes.SENT != _UNRESOLVABLE:
        raise RuntimeError("bash_writes.SENT differs from the parser's sentinel")
    try:
        judged = bash_writes.judge(command, cwd, line_parser(command), _expand_token)
    except bash_writes.Unreadable:
        judged = None
''')
pt = once(pt, '''_JUDGED = {}
''', '''def line_parser(command):
    """The line parser the judgement reads shell text with (ACT-GUARD-FIX-6): the product's of W2-42a, copied into
    bash_writes.py (``line_write_targets``), with the command's own glob options deciding whether an unmatched glob is
    its literal word, as ``gov.guard.decide._extract_bash_write_targets`` hands it."""
    import bash_writes
    literal = not bash_writes.GLOB_OPTIONS_RE.search(command)

    def parse(text, where):
        return bash_writes.line_write_targets(text, where, literal)
    return parse


_JUDGED = {}
''')
pt = once(pt, '''    from gov.guard.decide import _extract_bash_write_targets
    from bash_writes import SENT
    judged = bash_judgement(command, cwd)
    if judged is None:
        return resolved(parse_both(_extract_bash_write_targets, command, cwd)), []
    return resolved(judged.shell), resolved([full for _targets, _scope, _code in judged.findings
                                             for raw, full in _targets if raw != SENT and full])
''', '''    from bash_writes import SENT
    judged = bash_judgement(command, cwd)
    if judged is None:
        return resolved(parse_both(line_parser(command), command, cwd)), []
    # ``writes``: what the product enforces beside the shell's own (git checkout, restore, rm and mv on paths, dd,
    # truncate, sort -o, rsync, a script written and run, a body an unknown reader may run as shell; W2-42a). Like the
    # findings they are not the shell's own writes: rule 1 reads them, rule 5 never did (DEC-1050 (12), G-2).
    return resolved(judged.shell), resolved([full for _targets, _scope, _code in judged.findings
                                             for raw, full in _targets if raw != SENT and full] + judged.writes)
''')
pt = once(pt, '''    deletes = judged.deletes if judged is not None else crude_deletes(command, cwd)
''', '''    deletes = judged.deletes if judged is not None else []
    if judged is None or judged.recovered:
        deletes = deletes + crude_deletes(command, cwd)  # a command only a second reading read: its rm read crudely too
''')

# 2. (the line parser's glob-options name is defined with the copy, above)

# 3. R5: a file tool's path that is no path (not text, a NUL byte) is a ruled refusal (decide.py, W2-42a)
paths_src = re.search(r"_PATH_FIELDS = \{.*?\}\n", decide_src, re.S).group(0)
no_path_src, _ = source_of("src/gov/guard/decide.py", "_no_path")
refusal_src = re.search(r"NO_PATH_REFUSAL = \(.*?\)\n", decide_src, re.S).group(0)
pt = once(pt, '''CRUDE_RM = re.compile(''', f'''# R5 (W2-42a, DEC-1133 (2); gov.guard.decide, copied): a file tool's path or glob field that is no path the system takes
# (not text, or text holding a NUL byte) is refused by its own rule, before another rule resolves it.
# The fields of a file tool's call that are resolved as a path or a glob.
{paths_src}
{refusal_src}

{no_path_src}


# R4 (W2-42a, DEC-1133 (2); gov.guard.reads, copied): a revision-colon-path in git show or cat-file, or on a side of
# git diff, is judged as a read of its path; a revision git does not resolve, or one the guard cannot read, is a ruled
# refusal, not the error path; the methods that use these are copied into ``Judge`` in ``classes`` below.
{re.search(r"REV_REFUSAL = \(.*?\)\n(?=# W2-42a R4: in <rev>)", read("src/gov/guard/reads.py"), re.S).group(0)}{re.search(r"# W2-42a R4: in <rev>:<path> the path starts.*?PLACE_REFUSAL = \(.*?\)\n", read("src/gov/guard/reads.py"), re.S).group(0)}

{source_of("src/gov/guard/reads.py", "_blob_ref")[0]}


{source_of("src/gov/guard/reads.py", "_output_joined")[0]}


CRUDE_RM = re.compile(''')
pt = once(pt, '''    command = tin.get("command") if tool == "Bash" and isinstance(tin.get("command"), str) else None

    # Rule 2, the held-out material''', '''    command = tin.get("command") if tool == "Bash" and isinstance(tin.get("command"), str) else None

    # R5 (W2-42a): a path field that is no path is refused by its rule, before a rule resolves it.
    if _no_path(tool, tin):
        answer("deny", NO_PATH_REFUSAL, "no-path")

    # Rule 2, the held-out material''')

# 4. R4: the product's _Judge methods, copied into the hook's Judge
methods = []
for name in ("git", "colon", "placed", "cat_file", "patched", "stored", "ask"):
    text, _ = source_of("src/gov/guard/reads.py", "_Judge." + name)
    methods.append("\n".join(("    " + ln) if ln.strip() else ln for ln in text.split("\n")))
copied = "\n\n".join(methods)
bound = ["HIDDEN_REFUSAL", "SECRET_REFUSAL", "PolicyError", "_ARCHIVE_VALUED", "_COUNT_RE", "_GIT_GREP_VALUED",
         "_GIT_LOG_VALUED", "_GIT_QUIET", "_GIT_SIDES", "_NO_CONVERT", "_PATTERN_OPTIONS", "_Part", "_REV_FAULT",
         "_git", "_expand_token", "_options", "_pathspecs", "_x_top"]
names_block = "\n".join(f"    {n} = reads.{n}" for n in bound)
pt = once(pt, '''    import fnmatch
    from gov.guard import reads
    matched = {}''', f'''    import copy
    import fnmatch
    from gov.guard import reads
    # R4 (W2-42a): the names the copied _Judge methods below use, from the pinned judge (the same helpers before and
    # after a re-pin); REV_REFUSAL, PLACE_REFUSAL, _blob_ref and _output_joined are this module's own copies.
{names_block}
    matched = {{}}''')
pt = once(pt, '''            return ""

    _CLASSES.append((SetsRoot, Judge, Narrow))''', f'''            return ""

        # R4 (W2-42a, DECIDED-NOT-DONE 215): the product's _Judge.git, colon, placed, cat_file, patched, stored and ask,
        # copied as merged (b42e8628b835): revision-colon-paths are judged as reads of their paths, a git answer that is
        # no is a ruled refusal, git that cannot run (and the deadline) still refuse by the error path.
{copied}

    _CLASSES.append((SetsRoot, Judge, Narrow))''')
pt = pt.replace("        # copied as merged (b42e8628b835)", "        # copied as merged (b42e8628b835)")
with open(os.path.join(out, "pretooluse.py"), "w", encoding="utf-8") as handle:
    handle.write(pt)
print("built", out)
