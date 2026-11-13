import glob, os, xml.etree.ElementTree as ET
fs = sorted(glob.glob('/home/usain/gov-os-worktrees/*/.gov-runtime/scratch/lead/log/verify*/parallel.xml'), key=os.path.getmtime)[-14:]
for f in fs:
    run = fail = 0
    try:
        for tc in ET.parse(f).iter('testcase'):
            if 'test_w2_96' in (tc.get('classname') or ''):
                run += 1
                if tc.find('failure') is not None or tc.find('error') is not None: fail += 1
    except Exception as e:
        print(f, e); continue
    print(f"{os.path.getmtime(f):.0f} w2_96 run={run} fail={fail} {f.split('/')[4]} {f.split('/')[-2]}")
