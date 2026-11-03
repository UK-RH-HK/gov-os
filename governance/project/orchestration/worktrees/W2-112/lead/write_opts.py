import json
d = json.load(open('/tmp/gov-os-lead-W2-112/select.json'))
opts = list(d['pytest_options'])
open('/tmp/gov-os-lead-W2-112/pytest_options.txt', 'w').write(' '.join(opts) + '\n')
print(len(opts), 'options;', len(d['selected']), 'selected;', len(d['ignore']), 'ignore;', len(d['deselect']), 'deselect')
