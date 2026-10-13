"""Repository boundary. Replace SQLiteProgressStore to support another database."""
import sqlite3,json,hashlib,datetime,contextlib
from pathlib import Path

class ConflictError(Exception):pass
class SQLiteProgressStore:
    def __init__(self,path):
        self.path=str(path);Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''PRAGMA journal_mode=DELETE;
            CREATE TABLE IF NOT EXISTS progress(day TEXT, problem INTEGER, field TEXT, value INTEGER, updated TEXT, revision INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(day,problem,field));
            CREATE TABLE IF NOT EXISTS imports(digest TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS operations(id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value INTEGER);
            INSERT OR IGNORE INTO meta VALUES('version',0);''')
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
            return {'records':records,'revisions':revisions,'version':db.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0]}
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
                            db.execute('INSERT OR IGNORE INTO progress VALUES(?,?,?,?,?,1)',(day,problem,field,1,datetime.datetime.now(datetime.timezone.utc).isoformat()))
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
                current=db.execute('SELECT revision FROM progress WHERE day=? AND problem=? AND field=?',(day,problem,field)).fetchone()
                revision=current[0] if current else 0
                if type(op.get('revision'))!=int or op['revision']!=revision:raise ConflictError('Revision conflict')
                db.execute('INSERT INTO operations VALUES(?)',(identity,))
                db.execute('INSERT INTO progress VALUES(?,?,?,?,?,?) ON CONFLICT(day,problem,field) DO UPDATE SET value=excluded.value,updated=excluded.updated,revision=excluded.revision',(day,problem,field,int(value),datetime.datetime.now(datetime.timezone.utc).isoformat(),revision+1));changed=True
            if changed:db.execute("UPDATE meta SET value=value+1 WHERE key='version'")
        return self.snapshot()
    def backup(self,path):
        with self.connect() as source:
            target=sqlite3.connect(str(path))
            try:source.backup(target)
            finally:target.close()
