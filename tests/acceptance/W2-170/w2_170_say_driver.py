"""Call ``gov.memaudit.say.say`` on one line (W2-170 S5, F1; Interface 1 and 8).

Usage: ``python3 w2_170_say_driver.py <sets root> <line>``. The line is given as the first argument; when ``say``
names a parameter for the sets root (a name holding ``root``), the planted sets root is given by that name. The
Interface names ``say(...)`` without its parameters: this is the reading the README states. The child's exit code is
``say``'s own (it exits 4 when it refuses a line).
"""

import inspect
import sys

from gov.memaudit import say as module

ROOT, LINE = sys.argv[1], sys.argv[2]
args = [LINE]
try:
    params = [p for p in inspect.signature(module.say).parameters.values()
              if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    if any("root" in p.name.lower() for p in params):
        args, line_given = [], False
        for p in params:
            if "root" in p.name.lower():
                args.append(ROOT)
            elif not line_given:
                args.append(LINE)
                line_given = True
            if line_given and any("root" in q.name.lower() for q in params[:len(args)]):
                break
except (TypeError, ValueError):
    pass
module.say(*args)
sys.exit(0)
