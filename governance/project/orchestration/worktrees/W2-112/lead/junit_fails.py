import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    print('##', path)
    for tc in root.iter('testcase'):
        for kind in ('failure', 'error'):
            el = tc.find(kind)
            if el is not None:
                msg = (el.get('message') or '').replace('\n', ' ')[:160]
                print(kind.upper(), tc.get('classname'), '::', tc.get('name'), '|', msg)
