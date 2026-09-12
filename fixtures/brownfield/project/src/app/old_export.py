"""Dead code: nothing imports this module."""


def export_csv(rows):
    return "\n".join(",".join(str(c) for c in r) for r in rows)
