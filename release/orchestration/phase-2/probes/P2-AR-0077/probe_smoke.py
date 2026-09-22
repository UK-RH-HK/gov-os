#!/usr/bin/env python3
"""P2-AR-0077 smoke: the conforming path still works, ungated, with zero gate records.

This is negative control NC1 and also proves the harness itself drives the product.
"""
import json
from harness4 import fresh, security_review, descriptor, install, verdict, save

p = fresh("smoke")
rev = security_review(p, "TOOL-P77", "1.0")
e = install(p, descriptor(rev), "smoke")
v = verdict(e, p)
print(json.dumps(v, indent=2, default=str))
save("smoke", {"NC1_conforming_install": v, "review_record": rev})
