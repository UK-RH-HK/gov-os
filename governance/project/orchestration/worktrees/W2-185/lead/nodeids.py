import xml.etree.ElementTree as ET
t = ET.parse('/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/lead/log/verify/parallel.xml')
for tc in t.iter('testcase'):
    if tc.find('failure') is None: continue
    parts = tc.get('classname').split('.')
    i = max(k for k, p in enumerate(parts) if p.startswith('test_'))
    path = '/'.join(parts[:i+1]) + '.py'
    print('::'.join([path] + parts[i+1:] + [tc.get('name')]))
