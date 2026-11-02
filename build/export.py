import pickle,os,json,collections,math
segs=pickle.load(open(os.path.expanduser('~/work/segs.pkl'),'rb'))
rules=[];ridx={}
def R(k):
    if k not in ridx: ridx[k]=len(rules); rules.append(json.loads(k))
    return ridx[k]
# endpoints for cross streets
ends=collections.defaultdict(set)
for i,s in enumerate(segs):
    for p in (s['pts'][0],s['pts'][-1]): ends[(round(p[0]/3),round(p[1]/3))].add(i)
def cross(i,p):
    names=set()
    kx,ky=round(p[0]/3),round(p[1]/3)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for j in ends[(kx+dx,ky+dy)]:
                if segs[j]['name']!=segs[i]['name'] and segs[j]['name']: names.add(segs[j]['name'])
    return sorted(names)[:2]
out=[]
for i,s in enumerate(segs):
    if not s['name']: continue
    out.append({'n':s['name'],'k':s['nom'],
      'p':[[round(x),round(y)] for x,y in s['pts']],
      'L':s['L'],'R':s['R'],
      'rL':[[R(k),c] for k,c in s['rules']['L'].most_common()],
      'rR':[[R(k),c] for k,c in s['rules']['R'].most_common()],
      'po':[[round(x),round(y),0 if sd=='L' else 1,[R(k) for k in ks]] for x,y,sd,ks in s['posts']],
      'xa':cross(i,s['pts'][0]),'xb':cross(i,s['pts'][-1])})
data={'origin':[45.48,-73.62],'rules':rules,'segs':out,'built':'2026-10-19'}
js=json.dumps(data,ensure_ascii=False,separators=(',',':'))
open(os.path.expanduser('~/work/data.json'),'w',encoding='utf-8').write(js)
print(len(out),'segments',len(rules),'rules',len(js)//1024,'KB')
print(json.dumps(out[100],ensure_ascii=False)[:600])
