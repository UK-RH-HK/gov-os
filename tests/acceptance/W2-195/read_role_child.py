"""Child of the W2-195 launch cases: ``gov.launch.role.read_role(<root>, <role>)``, its answer printed as one JSON line.

``{"ok": true, "skills": [...]}`` (the record's skills, each without its text) or ``{"ok": false, "code", "message"}`` for a
``GovError``; any other exception is printed as ``{"ok": false, "code": null, "type", "message"}``.
"""

import json
import sys
from pathlib import Path


def main() -> None:
    root, role = Path(sys.argv[1]), sys.argv[2]
    try:
        from gov.cli.errors import GovError
        from gov.launch.role import read_role
    except Exception as error:  # noqa: BLE001
        print(json.dumps({"ok": False, "code": None, "type": type(error).__name__, "message": str(error)}))
        return
    try:
        out = read_role(root, role)
    except GovError as error:
        print(json.dumps({"ok": False, "code": error.code, "message": str(getattr(error, "message", error))}))
        return
    except Exception as error:  # noqa: BLE001
        print(json.dumps({"ok": False, "code": None, "type": type(error).__name__, "message": str(error)}))
        return
    print(json.dumps({"ok": True, "skills": out.get("skills")}, default=str))


if __name__ == "__main__":
    main()
