#!/usr/bin/env python3
"""Stream an official museum bulk export; never harvest image or IIIF endpoints."""
import argparse, hashlib, io, json, re, tempfile, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
RIGHTS={'CC BY-NC-SA 4.0':'https://creativecommons.org/licenses/by-nc-sa/4.0/','CC BY-NC-ND 4.0':'https://creativecommons.org/licenses/by-nc-nd/4.0/','Open Government Licence v3.0':'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/'}
def text(value): return re.sub('<[^>]*>', '', str(value or '')).strip()
def primary(values):
 if not isinstance(values,list):return ''
 rows=sorted([v for v in values if isinstance(v,dict)],key=lambda x:not x.get('primary'))
 return next((text(v.get('value')) for v in rows if v.get('value')), '')
def year(value):
 return int(value) if re.fullmatch(r'-?\d{1,4}',str(value or '')) else None
def iterate(stream):
 """Incremental JSON-array parser with bounded record buffering."""
 decoder=json.JSONDecoder();buf='';started=False;ended=False
 while True:
  chunk=stream.read(262144)
  if chunk:buf+=chunk
  while True:
   buf=buf.lstrip()
   if not started:
    if not buf:break
    if buf[0]!='[':raise ValueError('Expected JSON array')
    started=True;buf=buf[1:];continue
   if buf.startswith(','):buf=buf[1:];continue
   if buf.startswith(']'):ended=True;buf=buf[1:];break
   try:record,pos=decoder.raw_decode(buf)
   except json.JSONDecodeError:break
   if not isinstance(record,dict):raise ValueError('Invalid museum object')
   yield record;buf=buf[pos:]
  if ended:
   if buf.strip() or stream.read().strip():raise ValueError('Unexpected trailing content')
   return
  if len(buf)>16000000:raise ValueError('Museum record exceeds supported size')
  if not chunk:raise ValueError('Truncated JSON export')
def normalize(raw,collections):
 uid=raw.get('@admin',{}).get('uid','')
 if not re.fullmatch(r'co\d+',uid):return None
 title=primary(raw.get('title')) or text(raw.get('summary',{}).get('title'))
 terms=[text(t.get('summary',{}).get('title')) for t in raw.get('term',[]) if isinstance(t,dict)]
 haystack=' '.join([title,*terms])
 groups=[c['id'] for c in collections if any(re.search(p,haystack,re.I) for p in c['patterns'])]
 if not groups or not title:return None
 creation=raw.get('creation',{});dates=creation.get('date',raw.get('date',[]));d=next((v for v in dates if isinstance(v,dict) and v.get('value')), {})
 def names(field):return list(dict.fromkeys(text(v.get('summary',{}).get('title')) or primary(v.get('name')) for v in creation.get(field,[]) if isinstance(v,dict)))
 image=None
 for m in raw.get('multimedia',[]):
  if not isinstance(m,dict):continue
  rights=m.get('legal',{}).get('rights',[])
  if not rights or any(r.get('licence') not in RIGHTS for r in rights):continue
  imagefile=m.get('@processed',{}).get('medium_thumbnail',{});path=imagefile.get('location','')
  if not re.fullmatch(r'[A-Za-z0-9_./-]+',path) or '..' in path or path.startswith('/'):continue
  image={'url':'https://coimages.sciencemuseumgroup.org.uk/'+path,'licence':rights[0]['licence'],'licenceUrl':RIGHTS[rights[0]['licence']],'credit':text(m.get('credit',{}).get('value')),'copyright':text(rights[0].get('copyright'))};break
 description=primary(raw.get('description'))
 return {'id':uid,'title':title,'groups':groups,'terms':terms,'date':text(d.get('value')) or 'Date not recorded','start':year(d.get('from')),'end':year(d.get('to')),'makers':[x for x in names('maker') if x],'places':[x for x in names('place') if x],'description':description[:6000],'materials':list(dict.fromkeys(text(v.get('term')) for v in raw.get('physical',[]) if v.get('type')=='material')),'source':'https://collection.sciencemuseumgroup.org.uk/objects/'+uid,'image':image}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path);args=ap.parse_args();config=json.loads((ROOT/'web/config.json').read_text())
 if not config['collections'] or any(not c.get('patterns') for c in config['collections']):raise ValueError('Configure collections and patterns')
 with tempfile.TemporaryDirectory() as temp:
  archive=args.input or Path(temp)/'museum.zip'
  if not args.input:
   with urlopen(Request(config['sourceUrl'],headers={'User-Agent':'CoolCode SignalRelics/1.0 (+https://coolcode.ca/signalrelics/)'}),timeout=120) as response,archive.open('wb') as out:
    size=0
    while chunk:=response.read(1048576):
     size+=len(chunk)
     if size>400000000:raise ValueError('Export exceeded download limit')
     out.write(chunk)
  records=[];scanned=0;seen=set()
  with zipfile.ZipFile(archive) as z:
   entries=[x for x in z.infolist() if x.filename.endswith('.json')]
   if len(entries)!=1 or entries[0].file_size>5000000000:raise ValueError('Unexpected museum archive')
   with z.open(entries[0]) as binary,io.TextIOWrapper(binary,encoding='utf-8') as stream:
    for raw in iterate(stream):
     scanned+=1;r=normalize(raw,config['collections'])
     if r and r['id'] not in seen:records.append(r);seen.add(r['id'])
  if scanned<config['minimumSourceRecords'] or len(records)<20:raise ValueError('Incomplete museum export; previous publication preserved')
  now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
  result={'schemaVersion':1,'checkedAt':now,'sourceEdition':config['sourceEdition'],'sourceUrl':config['sourceUrl'],'sourceSha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'scanned':scanned,'count':len(records),'records':records}
  dest=ROOT/'web/data/objects.json';dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n');tmp.replace(dest)
  print(f'Validated {scanned} source objects; retained {len(records)} matching objects from edition {config["sourceEdition"]}')
if __name__=='__main__':main()
