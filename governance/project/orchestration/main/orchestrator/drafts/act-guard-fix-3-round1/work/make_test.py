"""Assemble test_guard_fix_3.py from make_planted.py's cases and test_tail.py."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "make_planted.py")).read()
cases = src[src.index('T = "tests/acceptance/W2-64/t.py"'):src.index("json.dump(CASES")]
head = '''"""ACT-GUARD-FIX-3: the five-rule hook's rules 1 and 5 read a Bash command by what it writes (DEC-958).

Drives the hook as Claude Code runs it (event JSON on stdin, the pinned judge's interpreter with -E) over:
- guard4_check.py's 54 planted cases (DEC-953 item 2, ACT-GUARD-FIX-1 and -2);
- ACT-GUARD-FIX-3's planted cases: real writes into the acceptance tests the hook must refuse (heredocs, inline
  Python, variables, loops, substitutions, sh -c, git checkout and restore, patches, and the writes the product's
  parser does not read), and the patterns of the logged false refusals it must pass;
- one synthetic case for each pattern of the 61 logged refusals (guard-refusals.jsonl), and, when the rebuilt corpus
  is given (GUARD_FIX3_CORPUS), the 61 themselves;
- the module bash_writes.py directly.

The hook under test: GUARD_FIX3_HOOK, else pretooluse.py beside this file, else the repository's own.
Run: python3 -m pytest -q test_guard_fix_3.py
"""
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.environ.get("GUARD_FIX3_HOOK") or (
    os.path.join(HERE, "pretooluse.py") if os.path.exists(os.path.join(HERE, "pretooluse.py"))
    else ROOT + "/.claude/hooks/pretooluse.py")
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
GUARD4 = ROOT + "/.gov-runtime/scratch/orchestrator/tools/guard4_check.py"
CORPUS = os.environ.get("GUARD_FIX3_CORPUS") or os.path.join(HERE, "work", "corpus.json")

'''
out = head + cases + open(os.path.join(HERE, "test_tail.py")).read()
open(os.path.join(os.path.dirname(HERE), "test_guard_fix_3.py"), "w").write(out)
print("written", len(out.splitlines()), "lines")
