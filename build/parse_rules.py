import re, unicodedata
DAYMAP={'LUNDI':0,'LUN':0,'LUNDRI':0,'MARDI':1,'MAR':1,'MERCREDI':2,'MER':2,'JEUDI':3,'JEU':3,'VENDREDI':4,'VEN':4,'SAMEDI':5,'SAM':5,'DIMANCHE':6,'DIM':6}
MON={'JANV':1,'JAN':1,'FEV':2,'MARS':3,'MAR':3,'AVRIL':4,'AVR':4,'MAI':5,'JUIN':6,'JUIL':7,'AOUT':8,'SEPT':9,'SEP':9,'OCT':10,'NOV':11,'NOVEMBRE':11,'DEC':12}
def strip(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
TIME=r'(\d{1,2})\s*[H:]\s*(\d{2})?'
def parse(desc):
    d=strip(desc).upper().replace('\\\\','\\').replace('AVIL','AVRIL').replace('1ER','1')
    if 'EXCEPT' in d: return None
    if not re.match(r'^\s*[\\/]?P',d) and not re.match(r'^\s*\d',d): return None
    m=re.search(r'(\d{1,2})\s*(JANV|JAN|FEV|MARS|AVRIL|AVR|MAI|JUIN|JUIL|AOUT|SEPT|SEP|OCT|NOVEMBRE|NOV|DEC)\.?\s*(?:AU|A|ET|-)\s*(\d{1,2})\s*(JANV|JAN|FEV|MARS|AVRIL|AVR|MAI|JUIN|JUIL|AOUT|SEPT|SEP|OCT|NOVEMBRE|NOV|DEC)',d)
    if not m: return None
    season=[MON[m.group(2)],int(m.group(1)),MON[m.group(4)],int(m.group(3))]
    head=d[:m.start()]
    t=re.search(TIME+r'\s*(?:-|@|A|À)\s*'+TIME,head)
    if not t: return None
    s=int(t.group(1))*60+int(t.group(2) or 0); e=int(t.group(3))*60+int(t.group(4) or 0)
    rest=head[t.end():]
    days=set()
    rng=re.search(r'\b(LUN|MAR|MER|JEU|VEN|SAM|DIM)\w*\.?\s+(?:A|AU)\s+(LUN|MAR|MER|JEU|VEN|SAM|DIM)\w*',rest)
    if rng:
        a,b=DAYMAP[rng.group(1)],DAYMAP[rng.group(2)]; days=set(range(a,b+1))
    else:
        for w in re.findall(r'[A-Z]+',rest):
            if w in DAYMAP: days.add(DAYMAP[w])
    if not days: return None
    return {'days':sorted(days),'start':s,'end':e,'season':season}
