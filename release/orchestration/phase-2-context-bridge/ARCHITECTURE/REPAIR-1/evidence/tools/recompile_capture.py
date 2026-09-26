"""Re-run the run-1 compile read-only against a COPY of the demonstration store, with the records ref pinned to the
demonstration's records commit, capturing pre-budget candidates and every budget drop (the manifest keeps only a
compact drop summary). Prints a JSON summary; writes full captures to argv[2]."""
import json, sys, dataclasses
from govbridge.core.yamlutil import load_yaml_file
from govbridge.compile import packet as P, budgets as B
cap = {}
orig = B.apply_budgets
def wrapped(sections, profile):
    cap['pre'] = {k: [dataclasses.asdict(i) for i in v] for k, v in sections.items()}
    out = orig(sections, profile)
    cap['post'] = {k: [i.item_id for i in v] for k, v in out[0].items()}
    cap['drops'] = out[1]
    return out
B.apply_budgets = wrapped
P.budgetsmod.apply_budgets = wrapped
ts = load_yaml_file(sys.argv[1])
res = P.compile_packet(ts, routes=P.real_routes_for(ts))
def ser(x):
    try: return dataclasses.asdict(x)
    except Exception: return str(x)
json.dump({'pre': cap['pre'], 'post': cap['post'], 'drops': [ser(d) if not isinstance(d, dict) else d for d in cap['drops']],
           'manifest': res['manifest'], 'queries_log': res['queries_log']}, open(sys.argv[2], 'w'), default=str)
print(json.dumps({'status': res['status'], 'packet_sha256': res['packet_sha256'],
                  'pre_counts': {k: len(v) for k, v in cap['pre'].items()},
                  'post_counts': {k: len(v) for k, v in cap['post'].items()},
                  'n_drops': len(cap['drops'])}, indent=1))
