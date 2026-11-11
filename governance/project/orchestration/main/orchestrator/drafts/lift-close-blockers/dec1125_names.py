"""Does DEC-1125's text name the W1-19 test, as ratchet._refused_because requires? (read-only)"""
import re, sys
from pathlib import Path
from gov.close import history as H
root = Path(sys.argv[1])
reg = H.register_entries(root, "docs/DECISION_REGISTER.md")
test = "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95"
for dec in sys.argv[2:]:
    why, text = H.owner_decision(dec, reg)
    file, _, name = test.rpartition("::")
    print(dec, "owner_decision:", why or "ok", "| names file:", file in text, "| names test name:",
          bool(re.search(rf"(?<!\w){re.escape(name)}(?![\w\[])", text)))
