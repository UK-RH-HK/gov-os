import sys, xml.etree.ElementTree as ET
t = ET.parse(sys.argv[1])
for tc in t.iter('testcase'):
    for f in list(tc.findall('failure')) + list(tc.findall('error')):
        print(tc.get('classname', ''), '::', tc.get('name'), '|', (f.get('message') or '')[:140].replace('\n', ' '))
