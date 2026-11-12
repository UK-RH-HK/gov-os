import sys, xml.etree.ElementTree as ET
t = ET.parse(sys.argv[1])
for tc in t.iter('testcase'):
    for f in list(tc.findall('failure')) + list(tc.findall('error')):
        cls = tc.get('classname', '')
        if 'W2_11' in cls or 'W2-11' in cls:
            continue
        msg = (f.get('message') or '')[:400]
        print('##', cls, '::', tc.get('name'))
        print('  ', msg.replace('\n', ' | '))
