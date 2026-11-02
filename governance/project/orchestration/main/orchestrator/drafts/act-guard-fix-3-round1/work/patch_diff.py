import sys
p = sys.argv[1]
s = open(p).read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)


# 1. An escaped \$ or \` is no expansion.
rep('''_EXPANSION = re.compile(r"\\$[A-Za-z_{(]|`")''', '''_EXPANSION = re.compile(r"(?<!\\\\)\\$[A-Za-z_{(]|(?<!\\\\)`")''')

# 3. getattr with a literal, harmless name is a read; setattr writes no file.
rep('''_DYNAMIC = frozenset("exec eval compile __import__ getattr setattr importlib.import_module importlib.__import__ "''',
    '''_DYNAMIC = frozenset("exec eval compile __import__ importlib.import_module importlib.__import__ "''')
rep('''        if q in _DYNAMIC or (q and q.split(".")[0] in ("pty",)) or \\''', '''        if q == "getattr":
            name = node.args[1] if len(node.args) > 1 else None
            if not (isinstance(name, ast.Constant) and isinstance(name.value, str)) or name.value in _WRITE_NAMES:
                out.append((SENT, None))  # getattr(os, "remove"), or a name the guard cannot read
        elif q in _DYNAMIC or (q and q.split(".")[0] in ("pty",)) or \\''')
rep('''_SAVES = frozenset(''', '''_WRITE_NAMES = frozenset("open system popen run call check_call check_output Popen spawn execv execve execl "
                         "execvp write_text write_bytes touch mkdir makedirs unlink remove rmdir removedirs rename "
                         "renames replace symlink link symlink_to hardlink_to truncate chmod copy copy2 copyfile "
                         "copytree move rmtree make_archive unpack_archive extractall".split())
_SAVES = frozenset(''')

# 6. A name bound to a list of the tests' paths, handed to an unknown function.
rep('''        if isinstance(node, ast.Call):
            return False
        text = ev(node)
        return bool(text) and "tests/acceptance" in text''', '''        if isinstance(node, ast.Call):
            return False
        if isinstance(node, ast.Name) and node.id in scope[-1] and \\
                isinstance(scope[-1][node.id][0], (ast.List, ast.Tuple, ast.Set, ast.Dict)):
            value, where = scope[-1][node.id]
            scope.append(consts if where is None else where)
            try:
                return handed(value)
            finally:
                scope.pop()
        text = ev(node)
        return bool(text) and "tests/acceptance" in text''')

# 2. Inline code the shell rewrites only with variables it resolves (its own, a literal loop's words): each reading.
rep('''        env, loopvals, drop = variants(text, expand)
        ptext = parser_text(text)''', '''        env, loopvals, drop = variants(text, expand)
        self.ctx = (env, loopvals, drop)
        ptext = parser_text(text)''')
rep('''    def code(self, code, scope, ecwd, whole, depth, shell_text):
        """Python code: its writes; code the shell rewrites first ($VAR, $(...), backticks) is judged as code the
        guard cannot read, with the whole command as its scope."""
        if shell_text and _EXPANSION.search(code):
            self.findings.append(([(SENT, None)], whole))
        try:
            targets = python_writes(code, ecwd, self.nested(whole), depth)
        except (SyntaxError, ValueError, RecursionError):
            targets = [(SENT, None)]
        self.findings.append((targets, scope + "\\n" + code))''', '''    def code(self, code, scope, ecwd, whole, depth, shell_text, definite=False):
        """Python code: its writes. Code the shell rewrites first is read once for each value of the variables it
        uses when the guard resolves them all (the command's own, a literal loop's words); otherwise ($(...),
        backticks, a variable it cannot resolve) it is code the guard cannot read, with the whole command as its
        scope. ``definite``: only a target that names or lands in the tests counts (a script file the command
        wrote and runs, which is otherwise not read, as any script file)."""
        texts = [code]
        if shell_text and _EXPANSION.search(code):
            texts = []
            env, loops, drop = self.ctx
            if "$(" not in code and not re.search(r"(?<!\\\\)`", code):
                for one in each(env, loops):
                    with environ(one, drop):
                        texts.append(self.expand(code))
            if not texts or None in texts:
                texts = [code]
                if not definite:
                    self.findings.append(([(SENT, None)], whole))
        for text in dict.fromkeys(texts):
            try:
                targets = python_writes(text, ecwd, self.nested(whole), depth)
            except (SyntaxError, ValueError, RecursionError):
                targets = [(SENT, None)]
            self.findings.append((targets, "" if definite else scope + "\\n" + text))''')
rep('''        self.bodies = [] if bodies is None else bodies  # every heredoc body met, nested commands' too''',
    '''        self.bodies = [] if bodies is None else bodies  # every heredoc body met, nested commands' too
        self.ctx = ({}, {}, set())  # the variables of the command being walked''')

# 4. A data heredoc written to a file the command then runs: shell is judged; Python only for definite targets.
rep('''                ran = _ran_script(head)
                if ran and ran[0] in scripts:
                    body = scripts[ran[0]]
                    self.body(body, ran[1] if ran[1] != "exec" else _shebang(body["text"]), part, ecwd, whole,
                              depth)''', '''                ran = _ran_script(head)
                if ran and ran[0] in scripts:
                    body = scripts[ran[0]]
                    how = ran[1] if ran[1] != "exec" else _shebang(body["text"])
                    if how == "shell":
                        self.body(body, "shell", part, ecwd, whole, depth)
                    elif how == "python":
                        self.code(body["text"], part, ecwd, whole, depth, shell_text=not body["quoted"],
                                  definite=True)''')

# 5. Patch-appliers write the files their patch names: unknown targets, judged by the whole command.
rep('''                elif name in ("git", "dd", "truncate", "sort", "rsync", "patch"):''', '''                elif _applies_patch(name, args):
                    self.findings.append(([(SENT, None)], whole))
                if name in ("git", "dd", "truncate", "sort", "rsync", "patch"):''')
rep('''def _ran_script(head):''', '''def _applies_patch(name, args):
    """git apply, git am, git stash apply or pop, and patch: they write the files the patch names."""
    if name == "patch":
        return "--dry-run" not in args
    if name != "git":
        return False
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
    sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
    if sub == "apply":
        return not (set(rest) & {"--check", "--stat", "--numstat", "--summary"}) or "--apply" in rest
    if sub == "am":
        return True
    return sub == "stash" and rest[:1] in (["apply"], ["pop"])


def _ran_script(head):''')
open(p, "w").write(s)
print("patched")
