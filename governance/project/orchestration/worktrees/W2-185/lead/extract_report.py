import json,sys
f=sys.argv[1]
texts=[]
for line in open(f):
    try: d=json.loads(line)
    except: continue
    if d.get('type')!='assistant': continue
    c=d.get('message',{}).get('content',[])
    for b in c if isinstance(c,list) else []:
        if b.get('type')=='text' and 'task:' in b.get('text','') and 'status:' in b['text']:
            texts.append(b['text'])
print(len(texts)); print(texts[-1] if texts else 'none')
