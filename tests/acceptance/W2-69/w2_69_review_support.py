"""Support code for the W2-69 cases added after implementation, from the review (DEC-136).

Public interfaces only, as in ``w2_69_support``: the check's declared command, ``gov rebuild --json`` in a temporary
project, gitleaks itself for the premises, and two stand-ins put first on ``PATH`` by a case that asks for them: the
first batch's stand-in gitleaks, and a stand-in code-graph tool that writes a SQLite store in the tool's home (only
where the brief allows it: README, "Tests added after implementation").

Every planted key block and token is built at run time from parts and hashed characters; none stands whole in a file
of this suite, and none is printed or logged here.
"""

from __future__ import annotations

import os
import re
import sqlite3
import sys
from pathlib import Path

import w2_69_support as support

# --------------------------------------------------------------------------
# Private-key blocks of the size real keys have (behaviour 1)
# --------------------------------------------------------------------------

SHAPES = ("pem-rsa", "pkcs8", "openssh", "pgp")
KEY_SIZES = (4000, 4600, 6600, 8192)
_DASHES = "-" * 5


def _shape(shape):
    """(header, footer, line width, the body's first characters, armour) of a key block's shape."""
    priv = "PRIV" + "ATE KEY"
    if shape == "pem-rsa":
        return f"{_DASHES}BEGIN RSA {priv}{_DASHES}", f"{_DASHES}END RSA {priv}{_DASHES}", 64, "MII", False
    if shape == "pkcs8":
        return f"{_DASHES}BEGIN {priv}{_DASHES}", f"{_DASHES}END {priv}{_DASHES}", 64, "MII", False
    if shape == "openssh":   # the body begins as every OpenSSH key's does: "openssh-key-v1" and its zero bytes
        return (f"{_DASHES}BEGIN OPENSSH {priv}{_DASHES}", f"{_DASHES}END OPENSSH {priv}{_DASHES}", 70,
                "b3BlbnNzaC1" + "rZXktdjEAAAAA", False)
    if shape == "pgp":       # an armoured block: a blank line after the armour header, a checksum line at the end
        return (f"{_DASHES}BEGIN PGP {priv} BLOCK{_DASHES}", f"{_DASHES}END PGP {priv} BLOCK{_DASHES}", 64, "lQ",
                True)
    raise ValueError(shape)


def _line(seed, width):
    """``width`` base64 characters from a hash of ``seed``; the next seed where a line would hold a word gitleaks'
    global allowlist shelters (``true``, ``false``, ``null``), so no block is sheltered by chance."""
    for attempt in range(100):
        try:
            return support.chars(f"{seed}-{attempt}", width, support.B64)
        except AssertionError:
            continue
    raise AssertionError(f"no line without a sheltered word for {seed}")


def key_block(shape, size, seed, sheltered=False):
    """A private-key block of exactly ``size`` bytes in ``shape``, as gitleaks' ``private-key`` rule matches it.
    Not a key: its body is hashed base64 characters. ``sheltered`` puts the run of the alphabet that gitleaks'
    built-in global allowlist shelters under ``extend`` (DEC-347) in its first line."""
    header, footer, width, lead, armour = _shape(shape)
    head = header + ("\n\n" if armour else "\n")
    tail = ("\n=" + support.chars(f"crc-{seed}", 4, support.B64) if armour else "") + "\n" + footer
    left = size - len(head) - len(tail)
    widths = []
    while left > width:
        widths.append(width)
        left -= width + 1
    if left < 1:                      # the last line holds a character: no blank line inside the block
        widths[-1] -= 1 - left
        left = 1
    widths.append(left)
    lines = [_line(f"key-{seed}-{n}", w) for n, w in enumerate(widths)]
    first = lead + ("abcdefghijklm" + "nopqrstuvwxyz" if sheltered else "")
    lines[0] = first + lines[0][len(first):]
    block = head + "\n".join(lines) + tail
    assert len(block) == size, (len(block), size)
    return block


def cut_parts(block):
    """The two parts of ``block`` cut at three places inside it: a quarter, the middle, three quarters."""
    return [(block[:at], block[at:]) for at in (len(block) // 4, len(block) // 2, 3 * len(block) // 4)]


PRIVATE_KEY_RULE = "w2-69-private-key"


def config_with_a_private_key_rule():
    """The kernel's rules and one more of the project's own, the expression of gitleaks' ``private-key`` rule: the
    project's rules alone then find a key block too (the second rule set, DEC-347)."""
    regex = next(each["regex"] for each in support.default_config()["rules"] if each["id"] == "private-key")
    added = (f'\n[[rules]]\nid = "{PRIVATE_KEY_RULE}"\ndescription = "A private key (the W2-69 review cases)"\n'
             f"regex = '''{regex}'''\nkeywords = [\"-----begin\"]\n")
    return support.template_text() + added, support.project_rules_alone_text() + added


def paragraph_starts(content):
    return [m.end() for m in re.finditer(rb"\n\n", bytes(content))]


# --------------------------------------------------------------------------
# A full-text index with the lexical index's own tokenizer (behaviour 2)
# --------------------------------------------------------------------------

LEXICAL_TOKENIZE = "porter unicode61 tokenchars '_'"   # src/gov/retrieval/lexical.py on w2/integrate: TOKENIZE


def review_k2_strings():
    """The project's four rules, each with a token-shaped string that ends in a digit (no stemming changes it):
    (the head that holds it inside an identifier, the string). Lower case where the rule allows it, so that the index
    stores it as written; the upper-case and the canary strings are stored in lower case."""
    return {
        "gov-token-digit": ("_", "sk" + "_" + "7" + support.chars("rv-digit", 14).lower() + "5"),
        "gov-token-lower": ("_", "tok" + "_" + "a" + "7" + support.chars("rv-lower", 13).lower() + "5"),
        "gov-token-upper": ("_", "pk" + "_" + "A" + "7" + support.chars("rv-upper", 13) + "5"),
        "gov-canary": ("__", "zq" + "_" + "CAN" + "ARY" + "_" + support.chars("rv-canary", 5) + "5"),
    }


PAIRS = 240         # identifiers in an index, each with its neighbour
BATCHES = 6         # transactions the index is written in, so that it holds several segments before it is optimised


def identifier_lines(rule, pairs=PAIRS):
    """Lines of text, each with a neighbour term and the identifier after it: the neighbour shares the identifier's
    whole head up to its token-shaped string and sorts just before it, so the index stores the identifier as that
    string after the shared prefix."""
    sep, token = review_k2_strings()[rule]
    out = []
    for k in range(pairs):
        head = f"zqrv{k:03d}{sep}"
        out.append(f"{support.prose(160, f'rv{k}').strip()} {head}a7 {head}{token} closes {k}\n")
    return out


def fts_identifier_store(path, rule, extra=()):
    """A full-text index of the lexical tokenizer over ``identifier_lines(rule)`` (and ``extra`` documents), written in
    ``BATCHES`` transactions."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    documents = identifier_lines(rule) + list(extra)
    connection = sqlite3.connect(path, isolation_level=None)
    try:
        connection.execute(f'CREATE VIRTUAL TABLE notes USING fts5(text, tokenize = "{LEXICAL_TOKENIZE}")')
        step = -(-len(documents) // BATCHES)
        for start in range(0, len(documents), step):
            connection.execute("BEGIN")
            for text in documents[start:start + step]:
                connection.execute("INSERT INTO notes (text) VALUES (?)", (text,))
            connection.execute("COMMIT")
    finally:
        connection.close()
    return path


def optimise_and_vacuum(path):
    """The rebuild's compaction, as the brief states it: the index optimised, then the store vacuumed."""
    connection = sqlite3.connect(path, isolation_level=None)
    try:
        for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND sql LIKE "
                                          "'%USING fts5%'").fetchall():
            connection.execute(f'INSERT INTO "{name}" ("{name}") VALUES (\'optimize\')')
        connection.execute("VACUUM")
    finally:
        connection.close()


_WORD_BYTE = re.compile(rb"[A-Za-z0-9_]")


def stored_as_a_suffix(data, string):
    """How many times ``string`` (in lower case, as the index stores its terms) stands in ``data`` right after a byte
    that is no word character: where the index's stored text begins inside the identifier."""
    low = string.lower().encode()
    starts = [m.start() for m in re.finditer(re.escape(low), data)]
    return sum(1 for at in starts if at and not _WORD_BYTE.match(data[at - 1:at]))


# --------------------------------------------------------------------------
# A stand-in code-graph tool (behaviours 4 and 5)
# --------------------------------------------------------------------------

_HOLDER = r'''
import os, sqlite3, sys, time
path, ready, release = sys.argv[1:4]
connection = sqlite3.connect(path, isolation_level=None)
connection.execute("BEGIN EXCLUSIVE")
open(ready, "w").close()
end = time.monotonic() + 900
while time.monotonic() < end and not os.path.exists(release):
    time.sleep(0.05)
connection.execute("ROLLBACK")
connection.close()
open(release + ".done", "w").close()
'''

_CODE_STAND_IN = r'''#!@PYTHON@
"""Stand-in for codebase-memory-mcp (W2-69 review cases): writes a SQLite store with free pages in the tool's home
(CBM_CACHE_DIR); with W2_69_HOLD set, starts another process that holds the store, and returns once it does."""
import json, os, sqlite3, subprocess, sys, time
args = sys.argv[1:]
if args[:1] == ["config"]:
    sys.exit(0)
if args[:1] != ["cli"] or "index_repository" not in args:
    sys.exit(2)
home = os.environ["CBM_CACHE_DIR"]
os.makedirs(home, exist_ok=True)
path = os.path.join(home, "code.db")
connection = sqlite3.connect(path, isolation_level=None)
connection.execute("PRAGMA secure_delete = OFF")
connection.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, name TEXT)")
connection.execute("BEGIN")
for n in range(400):
    connection.execute("INSERT INTO nodes (name) VALUES (?)", ("node %d " % n + "x" * 300,))
connection.execute("COMMIT")
connection.execute("DELETE FROM nodes WHERE id > 20")
connection.close()
hold = os.environ.get("W2_69_HOLD")
if hold:
    ready, release = hold + ".ready", hold + ".release"
    subprocess.Popen([sys.executable, "-c", @HOLDER@, path, ready, release], start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    end = time.monotonic() + 60
    while not os.path.exists(ready) and time.monotonic() < end:
        time.sleep(0.02)
print(json.dumps({"isError": False, "content": [{"type": "text", "text": "{}"}]}))
'''

CODE_STORE_REL = ".gov-runtime/codeintel/home/code.db"


def install_code_stand_in(sandbox):
    folder = sandbox.elsewhere / "code-tool-stand-in"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "codebase-memory-mcp"
    path.write_text(_CODE_STAND_IN.replace("@PYTHON@", sys.executable).replace("@HOLDER@", repr(_HOLDER)),
                    encoding="utf-8")
    path.chmod(0o755)
    return folder


def with_code_stand_in(env, folder):
    env = dict(env)
    env["PATH"] = f"{folder}{os.pathsep}{env['PATH']}"
    return env
