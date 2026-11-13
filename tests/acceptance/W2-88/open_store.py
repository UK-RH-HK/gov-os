"""Child program of the S10 cases: open the store at ``argv[1]`` through the product's open path (``gov.store.loader.
connect``) and print one JSON line: ``{"outcome": "opened"}`` or ``{"outcome": "error", "code", "message", "details"}``,
with the layout version this ``gov`` reads when ``gov.store.layout`` exists."""

import json
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.store import loader

out = {}
try:
    version = None
    try:
        from gov.store import layout
        version = layout.LAYOUT_VERSION
    except ImportError:
        pass
    conn = loader.connect(Path(sys.argv[1]))
    conn.close()
    out = {"outcome": "opened", "layout_version": version}
except GovError as error:
    out = {"outcome": "error", "code": error.code, "message": error.message, "details": error.details,
           "layout_version": version}
print(json.dumps(out, default=str))
