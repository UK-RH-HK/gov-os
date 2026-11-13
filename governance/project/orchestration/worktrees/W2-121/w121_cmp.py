import xml.etree.ElementTree as ET, collections
c = collections.Counter()
for tc in ET.parse('/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/log/verify/parallel.xml').iter('testcase'):
    cl = tc.get('classname') or ''
    k = 'acc-W2-121' if 'W2-121' in cl else ('unit-dispatch' if 'unit.dispatch' in cl else None)
    if k:
        o = 'fail' if (tc.find('failure') is not None or tc.find('error') is not None) else ('skip' if tc.find('skipped') is not None else 'pass')
        c[(k, o)] += 1
print(dict(c))
