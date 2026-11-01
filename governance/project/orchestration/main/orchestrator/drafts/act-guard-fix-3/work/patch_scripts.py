import sys
p = sys.argv[1]
s = open(p).read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


# 1. A heredoc written to a file that the same command runs is that runner's code.
rep('''        ecwd, stage, held = cwd, [], []
        with environ(env, drop | set(loopvals)):
            for words, reds, sep in simples(tokens(text)):
                for w in words + [r[1] for r in reds]:
                    for k in map(int, re.findall(r"__gov_sub_(\\d+)__", w)):
                        self.sub(subs[k], ecwd, whole, depth)
                head = lead(words)
                name = os.path.basename(head[0]) if head else ""
                args = head[1:]
                part = " ".join(words)
                if name in ("cd", "pushd", "popd"):''', '''        ecwd, stage, held, staged = cwd, [], [], []
        scripts = {}  # the name of a file a data heredoc was written to: its body
        with environ(env, drop | set(loopvals)):
            for words, reds, sep in simples(tokens(text)):
                for w in words + [r[1] for r in reds]:
                    for k in map(int, re.findall(r"__gov_sub_(\\d+)__", w)):
                        self.sub(subs[k], ecwd, whole, depth)
                head = lead(words)
                name = os.path.basename(head[0]) if head else ""
                args = head[1:]
                part = " ".join(words)
                ran = _ran_script(head)
                if ran and ran[0] in scripts:
                    body = scripts[ran[0]]
                    self.body(body, ran[1] if ran[1] != "exec" else _shebang(body["text"]), part, ecwd, whole,
                              depth)
                if name in ("cd", "pushd", "popd"):''')
rep('''                stage.append(_kind(words))
                held += [(int(m), len(stage) - 1, part, ecwd)
                         for r in reds for m in re.findall(r"^__gov_heredoc_(\\d+)__$", r[1])]
                if sep not in ("|", "|&"):
                    for k, at, part_, where in held:
                        # The body is read by its own command and, through a pipe, by the stages after it:
                        # data if all of them take it as data; the one that runs it otherwise; code (unknown)
                        # if more than one could.
                        runs = [kind for kind in stage[at:] if kind != "data"]
                        kind = "data" if not runs else runs[0] if len(runs) == 1 else "code"
                        self.body(self.bodies[k], kind, part_, where, whole, depth)
                    stage, held = [], []''', '''                stage.append(_kind(words))
                staged.append((words, reds))
                held += [(int(m), len(stage) - 1, part, ecwd)
                         for r in reds for m in re.findall(r"^__gov_heredoc_(\\d+)__$", r[1])]
                if sep not in ("|", "|&"):
                    for k, at, part_, where in held:
                        # The body is read by its own command and, through a pipe, by the stages after it:
                        # data if all of them take it as data; the one that runs it otherwise; code (unknown)
                        # if more than one could.
                        runs = [kind for kind in stage[at:] if kind != "data"]
                        kind = "data" if not runs else runs[0] if len(runs) == 1 else "code"
                        self.body(self.bodies[k], kind, part_, where, whole, depth)
                        if kind == "data":
                            for written in _written(staged[at:]):
                                scripts[written] = self.bodies[k]
                    stage, held, staged = [], [], []''')
rep('''def _kind(words):''', '''def _written(stages):
    """The names of the files a pipeline's stages write by a redirect or tee (a heredoc's body lands there)."""
    out = []
    for words, reds in stages:
        out += [os.path.basename(t) for op, t in reds if ">" in op and op not in (">&",) and not t.isdigit()]
        head = lead(words)
        if head and os.path.basename(head[0]) == "tee":
            out += [os.path.basename(a) for a in head[1:] if not a.startswith("-")]
    return [w for w in out if w]


def _ran_script(head):
    """(the name of the script file a command runs, how it runs it), or None."""
    if not head:
        return None
    name, args = os.path.basename(head[0]), head[1:]
    operands = [a for a in args if not a.startswith("-")]
    if name in _SHELLS or name in ("source", "."):
        return (os.path.basename(operands[0]), "shell") if operands and not any(_short(a, "c") for a in args) \\
            else None
    if _PY.match(name):
        i = 0
        while i < len(args) and args[i].startswith("-") and args[i] != "-":
            if not args[i].startswith("--") and args[i][-1:] in "cm":
                return None
            i += 2 if args[i] in ("-W", "-X") else 1
        return (os.path.basename(args[i]), "python") if i < len(args) and args[i] != "-" else None
    if name in ("perl", "node", "ruby", "php", "Rscript", "awk", "make"):
        return (os.path.basename(operands[0]), "code") if operands else None
    if "/" in head[0]:
        return name, "exec"
    return None


def _shebang(text):
    first = text.split("\\n", 1)[0]
    if not first.startswith("#!"):
        return "code"
    return "python" if "python" in first else "shell" if re.search(r"\\b(ba|da|z|k)?sh\\b", first) else "code"


def _kind(words):''')
# reads_view: keep a data body that is run later in the command.
rep('''    kinds, stage, at = {}, [], []
    for words, reds, sep in cmds:
        stage.append(_kind(words))
        at += [(int(m), len(stage) - 1) for r in reds for m in re.findall(r"^__gov_heredoc_(\\d+)__$", r[1])]
        if sep not in ("|", "|&"):
            for k, i in at:
                kinds[k] = "data" if set(stage[i:]) <= {"data"} else "code"
            stage, at = [], []
    out, last, extra = [], 0, []
    for k, b in enumerate(bodies):
        if kinds.get(k) != "data":
            continue
        s, e = b["span"]''', '''    kinds, names, stage, staged, at = {}, {}, [], [], []
    for words, reds, sep in cmds:
        stage.append(_kind(words))
        staged.append((words, reds))
        at += [(int(m), len(stage) - 1) for r in reds for m in re.findall(r"^__gov_heredoc_(\\d+)__$", r[1])]
        if sep not in ("|", "|&"):
            for k, i in at:
                kinds[k] = "data" if set(stage[i:]) <= {"data"} else "code"
                names[k] = _written(staged[i:])
            stage, staged, at = [], [], []
    out, last, extra = [], 0, []
    for k, b in enumerate(bodies):
        s, e = b["span"]
        # A body written to a file the command then runs is code: kept, as before.
        if kinds.get(k) != "data" or any(n in command2[e:] for n in names.get(k, [])):
            continue''')

# 2. Inline Python: an unknown function handed an acceptance path may write it.
rep('''        elif attr == "extract":
            target = arg(node, 1, "path")
            sink(target if target is not None else ast.Constant("."))
    return out''', '''        elif attr == "extract":
            target = arg(node, 1, "path")
            sink(target if target is not None else ast.Constant("."))
        elif not _safe_call(q, attr) and any(handed(a) for a in node.args + [k.value for k in node.keywords]):
            # A function the guard does not know, handed the acceptance tests' path: it may write them.
            out.append((SENT, None))
    return out''')
rep('''    def arg(call, i, kw):''', '''    def handed(node):
        """Whether an argument is (or holds) a path naming the acceptance tests; a call's result is not."""
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return any(handed(e) for e in node.elts)
        if isinstance(node, ast.Dict):
            return any(handed(e) for e in node.keys + node.values if e is not None)
        if isinstance(node, ast.Starred):
            return handed(node.value)
        if isinstance(node, ast.Call):
            return False
        text = ev(node)
        return bool(text) and "tests/acceptance" in text

    def arg(call, i, kw):''')
rep('''def _bound(stmt):''', '''_SAFE_MODULES = ("re", "os.path", "json", "yaml", "fnmatch", "glob", "shlex", "textwrap", "difflib", "hashlib", "ast",
                 "math", "itertools", "collections", "functools", "operator", "string", "datetime", "time",
                 "random", "statistics", "pprint", "typing", "dataclasses", "enum", "base64", "binascii",
                 "urllib.parse", "html", "sys", "unicodedata", "decimal", "fractions", "uuid", "heapq", "bisect",
                 "copy", "inspect", "tomllib", "csv")
_SAFE_FUNCS = frozenset("print len str repr sorted set list dict tuple frozenset any all isinstance issubclass "
                        "enumerate zip map filter min max sum int float bool range type id hash iter next abs round "
                        "format chr ord hex bin oct divmod pow reversed slice hasattr callable input Path PurePath "
                        "PosixPath PurePosixPath pathlib.Path pathlib.PurePath pathlib.PosixPath "
                        "pathlib.PurePosixPath os.listdir os.scandir os.walk os.stat os.lstat os.access os.getcwd "
                        "os.fspath os.environ.get os.getenv os.cpu_count os.getpid os.get_terminal_size "
                        "pytest.main".split())
_SAFE_METHODS = frozenset("read_text read_bytes exists is_file is_dir is_symlink is_absolute glob rglob iterdir stat "
                          "lstat resolve absolute relative_to is_relative_to joinpath with_name with_suffix with_stem "
                          "match samefile as_posix as_uri startswith endswith find rfind index rindex count split "
                          "rsplit splitlines partition rpartition strip lstrip rstrip replace format format_map join "
                          "encode decode lower upper title casefold zfill ljust rjust center expandtabs isdigit "
                          "isalpha get items keys values append extend insert add discard pop popitem clear copy "
                          "sort reverse search fullmatch findall finditer sub subn group groups groupdict span "
                          "start end read readline readlines load loads dumps setdefault update remove difference "
                          "union intersection issubset issuperset most_common write writelines close flush seek "
                          "tell __contains__".split())


def _safe_call(q, attr):
    """A call that writes no file it is handed: builtins, read-only modules and the common read and text methods."""
    if q in _SAFE_FUNCS or (q and any(q == m or q.startswith(m + ".") for m in _SAFE_MODULES)):
        return True
    return attr in _SAFE_METHODS


def _bound(stmt):''')
open(p, "w").write(s)
print("patched")
