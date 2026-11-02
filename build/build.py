import sys,os,csv,json,math,collections
sys.path.insert(0,os.path.expanduser('~/work'))
from parse_rules import parse
SRC=os.path.expanduser('~/mnt/Parking Utility')
LAT0,LON0=45.48,-73.62; KX=math.cos(math.radians(LAT0))*111320; KY=110574
def P(lon,lat): return ((lon-LON0)*KX,(lat-LAT0)*KY)
g=json.load(open(f'{SRC}/geobase.json',encoding='utf-8'))
BORO='Côte-des-Neiges'
segs=[]
for f in g['features']:
    p=f['properties']
    if not (BORO in (p['ARR_GCH'] or '') or BORO in (p['ARR_DRT'] or '')): continue
    if f['geometry']['type']!='LineString': continue
    pts=[P(*c) for c in f['geometry']['coordinates']]
    segs.append({'id':p['ID_TRC'],'name':(p['ODONYME'] or '').strip(),'nom':p['NOM_VOIE'],'typ':p['TYP_VOIE'],'dir':p['DIR_VOIE'],
      'L':[p['DEB_GCH'],p['FIN_GCH']],'R':[p['DEB_DRT'],p['FIN_DRT']],'pts':pts,'rules':{'L':collections.Counter(),'R':collections.Counter()},'posts':[]})
print('segments',len(segs))
# spatial index on segment pieces
CELL=40; grid=collections.defaultdict(list)
for si,s in enumerate(segs):
    for k in range(len(s['pts'])-1):
        (x1,y1),(x2,y2)=s['pts'][k],s['pts'][k+1]
        for gx in range(int(min(x1,x2)//CELL)-1,int(max(x1,x2)//CELL)+2):
            for gy in range(int(min(y1,y2)//CELL)-1,int(max(y1,y2)//CELL)+2):
                grid[(gx,gy)].append((si,k))
def nearest(x,y):
    best=None
    for si,k in set(grid[(int(x//CELL),int(y//CELL))]):
        (x1,y1),(x2,y2)=segs[si]['pts'][k],segs[si]['pts'][k+1]
        dx,dy=x2-x1,y2-y1; L2=dx*dx+dy*dy or 1e-9
        t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L2))
        px,py=x1+t*dx,y1+t*dy; d=math.hypot(x-px,y-py)
        # whole-segment position: penalise posts that fall off the ends of the full line
        end=(k==0 and t==0) or (k==len(segs[si]['pts'])-2 and t==1)
        score=d+(8 if end else 0)
        cross=dx*(y-y1)-dy*(x-x1)
        if best is None or score<best[0]: best=(score,d,si,'L' if cross>0 else 'R',end)
    return best
posts={}
for r in csv.DictReader(open(f'{SRC}/signalisation_stationnement.csv',encoding='utf-8-sig')):
    if r['DESCRIPTION_REP']!='Réel' or BORO not in r['NOM_ARROND']: continue
    pr=parse(r['DESCRIPTION_RPA'])
    if not pr: continue
    key=json.dumps(pr,sort_keys=True)
    po=posts.setdefault(r['POTEAU_ID_POT'],{'xy':P(float(r['Longitude']),float(r['Latitude'])),'rules':set(),'text':set()})
    po['rules'].add(key); po['text'].add(r['DESCRIPTION_RPA'].strip())
print('sweep posts',len(posts))
unmatched=0; dists=[]
for pid,po in posts.items():
    b=nearest(*po['xy'])
    if not b or b[1]>30: unmatched+=1; continue
    _,d,si,side,end=b; dists.append(d)
    for k in po['rules']: segs[si]['rules'][side][k]+=1
    segs[si]['posts'].append((round(po['xy'][0],1),round(po['xy'][1],1),side,sorted(po['rules'])))
print('unmatched',unmatched,'median dist',sorted(dists)[len(dists)//2])
# consistency check
agree=tot=0; mixed=[]
for s in segs:
    for side in 'LR':
        c=s['rules'][side]
        if sum(c.values())>=2:
            tot+=1; top=c.most_common(1)[0][1]
            if top==sum(c.values()): agree+=1
            else: mixed.append((s['name'],side,dict(c)))
print(f'segment-sides with >=2 signs: {tot}, all agree: {agree} ({100*agree/tot:.0f}%)')
# control: same-segment opposite sides identical?
same=both=0
for s in segs:
    if s['rules']['L'] and s['rules']['R']:
        both+=1; same+= s['rules']['L'].most_common(1)[0][0]==s['rules']['R'].most_common(1)[0][0]
print('segments with both sides signed',both,'same top rule on both sides',same)
import pickle; pickle.dump(segs,open(os.path.expanduser('~/work/segs.pkl'),'wb'))
for m in mixed[:12]: print('MIXED',m)
