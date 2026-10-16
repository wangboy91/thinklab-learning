"""Repository boundary. Replace SQLiteProgressStore to support another database."""
import sqlite3,json,hashlib,datetime,contextlib
from pathlib import Path

class ConflictError(Exception):pass
class SQLiteProgressStore:
    def __init__(self,path,content_root=None):
        self.content_root=Path(content_root) if content_root is not None else Path(__file__).resolve().parents[2]
        self.path=str(path);Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''PRAGMA journal_mode=DELETE;
            CREATE TABLE IF NOT EXISTS progress(day TEXT, problem INTEGER, field TEXT, value INTEGER, updated TEXT, revision INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(day,problem,field));
            CREATE TABLE IF NOT EXISTS imports(digest TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS operations(id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value INTEGER);
            INSERT OR IGNORE INTO meta VALUES('version',0);
            CREATE TABLE IF NOT EXISTS plan_items(problem INTEGER PRIMARY KEY,position INTEGER NOT NULL,active INTEGER NOT NULL,revision INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS daily_recommendations(day TEXT,problem INTEGER,PRIMARY KEY(day,problem));
            CREATE TABLE IF NOT EXISTS route_operations(id TEXT PRIMARY KEY,route TEXT NOT NULL,result TEXT NOT NULL);''')
            if not db.execute("SELECT 1 FROM meta WHERE key='plan_migrated'").fetchone():
                items={}
                for day,problem,value,revision in db.execute("SELECT day,problem,value,revision FROM progress WHERE field='planned' ORDER BY day,problem"):
                    previous=items.get(problem,(len(items),0,0));items[problem]=(previous[0],value,max(previous[2],revision))
                for problem,(position,active,revision) in items.items():db.execute('INSERT OR IGNORE INTO plan_items VALUES(?,?,?,?)',(problem,position,active,revision))
                db.execute("INSERT INTO meta VALUES('plan_migrated',1)")
    @contextlib.contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=1.5);db.execute('PRAGMA foreign_keys=ON');db.execute('PRAGMA busy_timeout=1500')
        try:
            with db:yield db
        finally:db.close()
    def snapshot(self):
        with self.connect() as db:
            db.execute('BEGIN') # Rows, revisions and version must share one read snapshot.
            records={};revisions={}
            for day,problem,field,value,revision in db.execute('SELECT day,problem,field,value,revision FROM progress ORDER BY day,problem'):
                r=records.setdefault(day,{'list':[],'done':[]})
                if value:r['list' if field=='planned' else 'done'].append(problem)
                revisions[f'{day}|{problem}|{field}']=revision
            return {'records':records,'revisions':revisions,'plan':[r[0] for r in db.execute('SELECT problem FROM plan_items WHERE active=1 ORDER BY position,problem')],'planRevisions':{str(r[0]):r[1] for r in db.execute('SELECT problem,revision FROM plan_items')},'version':db.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0]}
    @staticmethod
    def day(value):
        parts=str(value).split('-')
        if len(parts)!=3:raise ValueError('Invalid day')
        d=datetime.date(*map(int,parts));return f'{d.year}-{d.month}-{d.day}'
    def import_legacy(self,records):
        if not isinstance(records,dict) or len(records)>5000:raise ValueError('Invalid records')
        digest=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM imports WHERE digest=?',(digest,)).fetchone():
                for day,r in records.items():
                    day=self.day(day)
                    if not isinstance(r,dict):raise ValueError('Invalid record')
                    for key,field in [('list','planned'),('done','done')]:
                        for problem in r.get(key,[]):
                            if type(problem)!=int or not 0<problem<100000:raise ValueError('Invalid problem')
                            # Existing server value, including a false tombstone, wins.
                            inserted=db.execute('INSERT OR IGNORE INTO progress VALUES(?,?,?,?,?,1)',(day,problem,field,1,datetime.datetime.now(datetime.timezone.utc).isoformat())).rowcount
                            if inserted and field=='planned':
                                position=db.execute('SELECT COALESCE(MAX(position),-1)+1 FROM plan_items').fetchone()[0]
                                db.execute('INSERT OR IGNORE INTO plan_items VALUES(?,?,1,1)',(problem,position))
                db.execute('INSERT INTO imports VALUES(?)',(digest,));db.execute("UPDATE meta SET value=value+1 WHERE key='version'")
        return self.snapshot()
    def apply(self,operations):
        if not isinstance(operations,list) or len(operations)>1000:raise ValueError('Invalid operations')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE');changed=False
            for op in operations:
                day=self.day(op['day']);problem=op['problem'];field=op['field'];value=op['value'];identity=op['id']
                if type(problem)!=int or not 0<problem<100000 or field not in ['planned','done'] or type(value)!=bool or not isinstance(identity,str) or not 1<=len(identity)<=100:raise ValueError('Invalid operation')
                if db.execute('SELECT 1 FROM operations WHERE id=?',(identity,)).fetchone():continue
                current=db.execute('SELECT revision FROM plan_items WHERE problem=?',(problem,)).fetchone() if field=='planned' else db.execute('SELECT revision FROM progress WHERE day=? AND problem=? AND field=?',(day,problem,field)).fetchone()
                revision=current[0] if current else 0
                if type(op.get('revision'))!=int or op['revision']!=revision:raise ConflictError('Revision conflict')
                db.execute('INSERT INTO operations VALUES(?)',(identity,))
                if field=='planned':
                    existing=db.execute('SELECT position,active FROM plan_items WHERE problem=?',(problem,)).fetchone()
                    position=existing[0] if existing and (existing[1] or not value) else db.execute('SELECT COALESCE(MAX(position),-1)+1 FROM plan_items').fetchone()[0]
                    db.execute('INSERT INTO plan_items VALUES(?,?,?,?) ON CONFLICT(problem) DO UPDATE SET position=excluded.position,active=excluded.active,revision=excluded.revision',(problem,position,int(value),revision+1))
                db.execute('INSERT INTO progress VALUES(?,?,?,?,?,?) ON CONFLICT(day,problem,field) DO UPDATE SET value=excluded.value,updated=excluded.updated,revision=excluded.revision',(day,problem,field,int(value),datetime.datetime.now(datetime.timezone.utc).isoformat(),revision+1));changed=True
            if changed:db.execute("UPDATE meta SET value=value+1 WHERE key='version'")
        return self.snapshot()
    def backup(self,path):
        with self.connect() as source:
            target=sqlite3.connect(str(path))
            try:source.backup(target)
            finally:target.close()

    def join_route(self,route_id,operation_id):
        routes=json.loads((Path(__file__).resolve().parents[2]/'content/routes/routes.json').read_text(encoding='utf-8'))
        route=next((r for r in routes if r['id']==route_id),None)
        if not route or not isinstance(operation_id,str) or not 1<=len(operation_id)<=100:raise ValueError('Invalid route request')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            previous=db.execute('SELECT route,result FROM route_operations WHERE id=?',(operation_id,)).fetchone()
            if previous:
                if previous[0]!=route_id:raise ValueError('Operation ID belongs to another route')
                result=json.loads(previous[1]);result['replayed']=True
            else:
                if db.execute('SELECT 1 FROM operations WHERE id=?',(operation_id,)).fetchone():raise ValueError('Operation ID already used')
                added=[];already=[]
                position=db.execute('SELECT COALESCE(MAX(position),-1)+1 FROM plan_items').fetchone()[0]
                for problem in dict.fromkeys(route['problemIds']):
                    existing=db.execute('SELECT active,revision FROM plan_items WHERE problem=?',(problem,)).fetchone()
                    if existing and existing[0]:already.append(problem);continue
                    revision=(existing[1] if existing else 0)+1
                    db.execute('INSERT INTO plan_items VALUES(?,?,1,?) ON CONFLICT(problem) DO UPDATE SET position=excluded.position,active=1,revision=excluded.revision',(problem,position,revision));position+=1;added.append(problem)
                result={'routeId':route_id,'added':added,'already':already,'addedCount':len(added),'alreadyCount':len(already),'replayed':False}
                db.execute('INSERT INTO operations VALUES(?)',(operation_id,));db.execute('INSERT INTO route_operations VALUES(?,?,?)',(operation_id,route_id,json.dumps(result)))
                if added:db.execute("UPDATE meta SET value=value+1 WHERE key='version'")
        return {'snapshot':self.snapshot(),'result':result}

    def join_daily(self, day, problems):
        """Append complete lessons once per date/id; never change done or active item revisions."""
        day=self.day(day)
        if not isinstance(problems,list) or not 1<=len(problems)<=100 or any(type(p)!=int or not 0<p<100000 for p in problems):raise ValueError('Invalid daily problems')
        problems=list(dict.fromkeys(problems))
        root=self.content_root
        for problem in problems:
            lesson=root/f'content/problems/{problem:04}.json'
            if not lesson.is_file():raise ValueError('Daily lesson not complete')
            content=json.loads(lesson.read_text(encoding='utf-8'))
            required=['title','concept','question','think','hints','explain','why','complexity','errors','exampleText','challenge','boardLabel','examples','source']
            if content.get('id')!=problem or any(not content.get(k) for k in required) or len(content['hints'])<3:raise ValueError('Daily lesson not complete')
            for folder,ext in [('csharp','cs'),('python','py'),('java','java'),('javascript','js'),('typescript','ts')]:
                if not (root/f'solutions/{folder}/{problem:04}.{ext}').is_file():raise ValueError('Daily reference missing')
        added=[];already=[];replayed=[]
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            position=db.execute('SELECT COALESCE(MAX(position),-1)+1 FROM plan_items').fetchone()[0]
            for problem in problems:
                if db.execute('SELECT 1 FROM daily_recommendations WHERE day=? AND problem=?',(day,problem)).fetchone():replayed.append(problem);continue
                existing=db.execute('SELECT active,revision FROM plan_items WHERE problem=?',(problem,)).fetchone()
                if existing and existing[0]:already.append(problem)
                else:
                    revision=(existing[1] if existing else 0)+1
                    db.execute('INSERT INTO plan_items VALUES(?,?,1,?) ON CONFLICT(problem) DO UPDATE SET position=excluded.position,active=1,revision=excluded.revision',(problem,position,revision))
                    position+=1;added.append(problem)
                db.execute('INSERT INTO daily_recommendations VALUES(?,?)',(day,problem))
            if added:db.execute("UPDATE meta SET value=value+1 WHERE key='version'")
        return {'snapshot':self.snapshot(),'result':{'day':day,'added':added,'already':already,'replayed':replayed}}
