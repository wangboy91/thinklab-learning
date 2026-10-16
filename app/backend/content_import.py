"""Version 1 intake. Incoming reference code is data, never executed here."""
import hashlib,json,re,sqlite3,os
from pathlib import Path
from .storage import ConflictError

LANGUAGES={'csharp':'cs','python':'py','java':'java','javascript':'js','typescript':'ts'}
FIELDS=['title','difficulty','topic','concept','question','think','hints','explain','why','complexity','errors','exampleText','challenge','boardLabel','examples','source','trace']
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def text(value):
    if not isinstance(value,str) or not value.strip() or len(value)>20000 or re.search(r'[<>&\x00-\x08\x0b\x0c\x0e-\x1f]',value):raise ValueError('Plain nonempty teaching text required; HTML/entities rejected')
def safe_path(root,relative):
    root=Path(root).resolve();path=root/relative
    if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path,*path.parents] if p!=root):raise ValueError('Unsafe content path')
    return path
def existing(root,id):
    lesson=json.loads(safe_path(root,f'content/problems/{id:04}.json').read_text(encoding='utf-8'))
    solutions={lang:safe_path(root,f'solutions/{lang}/{id:04}.{ext}').read_text(encoding='utf-8').strip() for lang,ext in LANGUAGES.items()}
    if lesson.get('id')!=id or any(not lesson.get(k) for k in FIELDS if k!='trace') or len(lesson['hints'])<3 or (id not in [1,20] and not lesson.get('trace')):raise ValueError('Existing lesson incomplete')
    return {'lesson':lesson,'solutions':solutions}
def validate_candidate(root,id,candidate):
    if not isinstance(candidate,dict) or set(candidate)!={'lesson','solutions','rights'} or candidate['rights']!='original':raise ValueError('Original teaching/code declaration required')
    l=candidate['lesson'];codes=candidate['solutions']
    if not isinstance(l,dict) or l.get('id')!=id or any(not l.get(k) for k in FIELDS):raise ValueError('Incomplete lesson')
    allowed=set(FIELDS+['id','time','domain','type','codeNote'])
    if set(l)-allowed or l.get('domain')!='algorithm' or l.get('type')!='algorithm_trace':raise ValueError('Unsupported lesson fields/type')
    for k in FIELDS:
        if k not in ['hints','errors','examples','source']:text(l[k])
    for key in ['time','codeNote']:
        if key in l:text(l[key])
    for key,minimum in [('hints',3),('errors',1)]:
        if not isinstance(l[key],list) or not minimum<=len(l[key])<=20:raise ValueError('Invalid teaching list')
        for v in l[key]:text(v)
    source=l['source']
    if not isinstance(source,dict) or source.get('kind')!='original_authoring' or not re.fullmatch(r'https://leetcode\.(?:com|cn)/problems/[a-z0-9-]+/',source.get('officialUrl','')):raise ValueError('Official problem permalink required')
    text(source.get('license'))
    for v in source.values():text(v)
    # Only shipped, maintainer-owned trace code can be selected. No incoming JS trace code.
    templates=[]
    for p in (Path(root)/'content/problems').glob('*.json'):
        trusted=json.loads(p.read_text(encoding='utf-8'))
        if trusted.get('trace')==l['trace']:templates.extend(trusted['examples'])
    if not templates:raise ValueError('New trace requires normal source review outside the intake API')
    if not isinstance(l['examples'],list) or not 1<=len(l['examples'])<=12:raise ValueError('Invalid examples')
    for e in l['examples']:
        if not isinstance(e,dict) or not any(set(e)==set(t) for t in templates):raise ValueError('Example does not match trusted trace contract')
        if not any(all(type(e[k])==type(t[k]) for k in e) for t in templates if set(e)==set(t)):raise ValueError('Example field types do not match trusted trace')
        text(e.get('label'))
        for k,v in e.items():
            if k=='label':continue
            if isinstance(v,list):
                if len(v)>100 or any((x is None and k!='tree') or (x is not None and (type(x)!=int or abs(x)>1000000)) for x in v):raise ValueError('Invalid example array')
            elif type(v)==int:
                if abs(v)>1000000:raise ValueError('Invalid example integer')
            elif isinstance(v,str):
                if len(v)>300 or '<' in v or '>' in v or '&' in v:raise ValueError('Invalid example string')
            else:raise ValueError('Unsupported example value')
        if l['trace'] in ['mergeListTrace','sortedPairTrace','binarySearchTrace','searchInsertTrace','removeDuplicateTrace']:
            for k in ['a','b','nums']:
                if k in e and (any(type(v)!=int for v in e[k]) or e[k]!=sorted(e[k])):raise ValueError('Sorted trace requires sorted integer arrays')
    if not isinstance(codes,dict) or set(codes)!=set(LANGUAGES):raise ValueError('Exactly five language references required')
    for code in codes.values():
        if not isinstance(code,str) or not code.strip() or len(code)>64000 or '\x00' in code:raise ValueError('Invalid reference text')
    return {'lesson':l,'solutions':{k:v.strip() for k,v in codes.items()}}
def validate(root,batch):
    if not isinstance(batch,dict) or set(batch)!={'schemaVersion','batchId','day','items'} or type(batch['schemaVersion'])!=int or batch['schemaVersion']!=1:raise ValueError('Unsupported batch schema')
    if not isinstance(batch['batchId'],str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}',batch['batchId']):raise ValueError('Invalid batch ID')
    if re.fullmatch(r'(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])',batch['batchId'],re.IGNORECASE):raise ValueError('Reserved batch ID')
    from .storage import SQLiteProgressStore
    day=SQLiteProgressStore.day(batch['day'])
    if not isinstance(batch['items'],list) or not 1<=len(batch['items'])<=10:raise ValueError('Batch must contain 1..10 items')
    ids=[];pending=[]
    for item in batch['items']:
        if not isinstance(item,dict) or type(item.get('id'))!=int or not 0<item['id']<100000 or item['id'] in ids:raise ValueError('Invalid/duplicate problem ID')
        id=item['id'];ids.append(id)
        if set(item)=={'id','sha256'}:
            try:known=existing(root,id)
            except (OSError,ValueError):raise ValueError('Referenced lesson is not complete')
            if item['sha256']!=digest(known):raise ConflictError('Existing lesson digest changed')
        elif set(item)=={'id','candidate'}:
            proposed=validate_candidate(root,id,item['candidate'])
            if safe_path(root,f'content/problems/{id:04}.json').exists():
                if digest(existing(root,id))==digest(proposed):continue
                raise ConflictError('Existing teaching cannot be overwritten')
            for lang,ext in LANGUAGES.items():
                if safe_path(root,f'solutions/{lang}/{id:04}.{ext}').exists():raise ConflictError('Existing reference cannot be overwritten')
            pending.append(id)
        else:raise ValueError('Unsupported item fields')
    return {'batchId':batch['batchId'],'day':day,'sha256':digest(batch),'problemIds':ids,'pendingReview':pending}

class ContentIntake:
    def __init__(self,root,store):self.root=Path(root);self.store=store
    def run(self,batch,dry_run=True):
        if type(dry_run)!=bool:raise ValueError('dryRun must be boolean')
        result=validate(self.root,batch)
        with self.store.connect() as db:
            found=db.execute("SELECT 1 FROM sqlite_master WHERE name='content_intake_batches'").fetchone()
            old=db.execute('SELECT digest FROM content_intake_batches WHERE id=?',(result['batchId'],)).fetchone() if found else None
        if old and old[0]!=result['sha256']:raise ConflictError('Batch ID reused with different content')
        if dry_run:return dict(result,status='pending_review' if result['pendingReview'] else 'ready',dryRun=True)
        # Reserve the immutable batch identity before plan merge; interrupted merges can retry safely.
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE IF NOT EXISTS content_intake_batches(id TEXT PRIMARY KEY,digest TEXT NOT NULL)')
            row=db.execute('SELECT digest FROM content_intake_batches WHERE id=?',(result['batchId'],)).fetchone()
            if row and row[0]!=result['sha256']:raise ConflictError('Batch conflict')
            db.execute('INSERT OR IGNORE INTO content_intake_batches VALUES(?,?)',(result['batchId'],result['sha256']))
        if result['pendingReview']:
            path=safe_path(self.root,f'local/incoming/{result["batchId"]}.json');path.parent.mkdir(parents=True,exist_ok=True)
            try:
                with path.open('x',encoding='utf-8') as f:json.dump(batch,f,ensure_ascii=False,indent=2)
            except FileExistsError:
                if digest(json.loads(path.read_text(encoding='utf-8')))!=result['sha256']:raise ConflictError('Staged batch differs')
            return dict(result,status='pending_review',dryRun=False)
        joined=self.store.join_daily(result['day'],result['problemIds'])
        return dict(result,status='planned',dryRun=False,planResult=joined['result'])
