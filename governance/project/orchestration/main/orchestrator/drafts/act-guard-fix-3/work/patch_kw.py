import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)
rep('''def lead(words):''', '''def parser_text(text):
    """``text`` as the product's parser is to read it: the same tokens, with a ``;`` after the shell keywords and
    the prefixes that run a command (do, then, if, !, {, time, timeout 60, env -i, nohup, ...), which the parser
    takes for the command's name; so ``do touch x`` is read as ``touch x``."""
    toks = tokens(text)
    out, words, start = [], [], 0

    def flush():
        cut = len(words) - len(lead([w for w, _ in words]))
        if cut and any(not _ASSIGN.match(w) for w, _ in words[:cut]) and cut < len(words):
            out.insert(words[cut][1], ";")

    i = 0
    while i < len(toks):
        t = toks[i]
        if t and all(c in _PUNCT for c in t):
            if ("<" in t or ">" in t) and i + 1 < len(toks) and not all(c in _PUNCT for c in toks[i + 1]):
                out += [t, shlex.quote(toks[i + 1])]
                i += 2
                continue
            if not ("<" in t or ">" in t):
                flush()
                words = []
            out.append(t)
            i += 1
            continue
        words.append((t, len(out)))
        out.append(shlex.quote(t))
        i += 1
    flush()
    # The ";" go in from the last to the first, so the positions taken above stay right.
    return " ".join(out)


def lead(words):''')
open(p, "w").write(s)
print("patched")
