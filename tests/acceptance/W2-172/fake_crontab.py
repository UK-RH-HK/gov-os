"""A planted ``crontab`` first on the children's PATH: it logs any call to ``crontab_calls.log`` in ``W172_STATE`` and
changes nothing. F4: the driver and the wrapper never call it."""
import os
import sys

STATE = os.environ.get("W172_STATE") or os.path.join(os.path.dirname(os.path.realpath(__file__)), "state")
os.makedirs(STATE, exist_ok=True)
with open(os.path.join(STATE, "crontab_calls.log"), "a", encoding="utf-8") as f:
    f.write(" ".join(sys.argv) + "\n")
sys.exit(0)
