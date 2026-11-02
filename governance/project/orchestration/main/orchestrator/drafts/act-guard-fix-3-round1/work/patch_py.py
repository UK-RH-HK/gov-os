import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)

rep('''    tree = ast.parse(code)
    alias, stores, consts, out = {}, {}, {}, []
    for node in ast.walk(tree):''', '''    tree = ast.parse(code)
    alias, stores, consts, out = {}, {}, {}, []
    shared = set()  # names a global or nonlocal statement names: never resolved
    for node in ast.walk(tree):''')
rep('''        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            stores[node.id] = stores.get(node.id, 0) + 1''', '''        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            stores[node.id] = stores.get(node.id, 0) + 1''')
rep('''        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for name in node.names:
                stores[name] = stores.get(name, 0) + 2
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if stores.get(node.targets[0].id) == 1:
                consts[node.targets[0].id] = node.value
    cwd_moves = any(isinstance(n, ast.Call) and qual(n.func, alias) in ("os.chdir", "os.fchdir")
                    for n in ast.walk(tree))
    seen = set()
''', '''        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            shared.update(node.names)
    # A name bound once in the whole code, by a plain assignment, is that value everywhere (in functions too).
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if stores.get(node.targets[0].id) == 1 and node.targets[0].id not in shared:
                consts[node.targets[0].id] = (node.value, None)
    # The module's own statements run in order: a name has the value its last plain assignment gave it, until a
    # statement binds it otherwise (a loop, a with, a function's body run later sees only the names bound once).
    at = {}
    env = {}
    for stmt in tree.body:
        mine = _bound(stmt)
        target = (stmt.targets[0].id if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                  and isinstance(stmt.targets[0], ast.Name) else None)
        inside = {k: v for k, v in env.items() if k not in (mine - {target} if target else mine)}
        for n in ast.walk(stmt):
            if isinstance(n, ast.Call):
                at[id(n)] = inside
        env = {k: v for k, v in env.items() if k not in mine}
        if target and target not in shared and not (mine - {target}):
            env[target] = (stmt.value, inside)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            for m in ast.walk(n):
                if isinstance(m, ast.Call):
                    at[id(m)] = consts
    cwd_moves = any(isinstance(n, ast.Call) and qual(n.func, alias) in ("os.chdir", "os.fchdir")
                    for n in ast.walk(tree))
    seen = set()
    scope = [consts]
''')
rep('''            if isinstance(node, ast.Name):
                return ev(consts[node.id]) if node.id in consts else None''', '''            if isinstance(node, ast.Name):
                if node.id not in scope[-1]:
                    return None
                value, where = scope[-1][node.id]
                scope.append(consts if where is None else where)
                try:
                    return ev(value)
                finally:
                    scope.pop()''')
rep('''    def arg(call, i, kw):
        for k in call.keywords:
            if k.arg == kw:
                return k.value
            if k.arg is None:
                return None  # **kwargs: not read
        return call.args[i] if len(call.args) > i else None''', '''    def arg(call, i, kw):
        for k in call.keywords:
            if k.arg == kw:
                return k.value
            if k.arg is None:
                return None  # **kwargs: not read
        return call.args[i] if i is not None and len(call.args) > i else None''')
rep('''    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        q = qual(node.func, alias)''', '''    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        scope[:] = [at.get(id(node), consts)]
        q = qual(node.func, alias)''')
rep('''            where = arg(node, -1, "cwd") if q.startswith("subprocess") else None''', '''            where = arg(node, None, "cwd") if q.startswith("subprocess") else None''')
rep('''def qual(func, alias):''', '''def _bound(stmt):
    """The names a statement binds or deletes, anywhere inside it."""
    out = set()
    for n in ast.walk(stmt):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, ast.arg):
            out.add(n.arg)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            out.update((a.asname or a.name).split(".")[0] for a in n.names)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            out.update(n.names)
        elif getattr(n, "name", None) and type(n).__name__ in ("MatchAs", "MatchStar"):
            out.add(n.name)
        elif type(n).__name__ == "MatchMapping" and getattr(n, "rest", None):
            out.add(n.rest)
    return out


def qual(func, alias):''')
# heredoc bodies shared across nested runs
rep('''    def __init__(self, parse, expand):
        self.parse = parse    # the product's parser: (command, cwd) -> targets or None
        self.expand = expand  # the product's word expansion: (word) -> text or None
        self.shell, self.findings = [], []''', '''    def __init__(self, parse, expand, bodies=None):
        self.parse = parse    # the product's parser: (command, cwd) -> targets or None
        self.expand = expand  # the product's word expansion: (word) -> text or None
        self.shell, self.findings = [], []
        self.bodies = [] if bodies is None else bodies  # every heredoc body met, nested commands' too''')
rep('''        text, bodies = heredocs(command)
        text, subs = lift(text)

        def expand(value, env):''', '''        text, bodies = heredocs(command)
        base = len(self.bodies)
        self.bodies += bodies
        text = re.sub(r"__gov_heredoc_(\\d+)__", lambda m: f"__gov_heredoc_{base + int(m.group(1))}__", text)
        text, subs = lift(text)

        def expand(value, env):''')
rep('''                        self.body(bodies[k], kind, part_, where, whole, depth)''', '''                        self.body(self.bodies[k], kind, part_, where, whole, depth)''')
rep('''        sub = Judgement(self.parse, self.expand)
        sub.run(command, UNKNOWN, whole, depth + 1)''', '''        sub = Judgement(self.parse, self.expand, self.bodies)
        sub.run(command, UNKNOWN, whole, depth + 1)''')
open(p, "w").write(s)
print("patched")
