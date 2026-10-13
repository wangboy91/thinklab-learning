import tempfile,sqlite3,json
from pathlib import Path
from storage import SQLiteProgressStore,ConflictError
with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
    path=Path(tmp)/'progress.sqlite3';store=SQLiteProgressStore(path)
    legacy={'2026-10-12':{'list':[1,20],'done':[1]}}
    first=store.import_legacy(legacy);assert store.import_legacy(legacy)==first
    assert first['records']['2026-10-12']['done']==[1]
    rev=first['revisions']['2026-10-12|1|done']
    a={'id':'client-a','day':'2026-10-12','problem':1,'field':'done','value':False,'revision':rev}
    second=store.apply([a]);assert store.apply([a])==second
    b=dict(a,id='client-b',value=True)
    try:store.apply([b]);raise AssertionError('Conflict was not rejected')
    except ConflictError:pass
    assert store.snapshot()==second
    b['revision']=second['revisions']['2026-10-12|1|done'];third=store.apply([b]);assert third['records']['2026-10-12']['done']==[1]
    remove={'id':'remove','day':'2026-10-12','problem':20,'field':'planned','value':False,'revision':third['revisions']['2026-10-12|20|planned']};store.apply([remove])
    fresh={'2026-10-12':{'list':[1,20,3],'done':[20]}}
    merged=store.import_legacy(fresh);assert 20 not in merged['records']['2026-10-12']['list'];assert 3 in merged['records']['2026-10-12']['list'];assert 20 in merged['records']['2026-10-12']['done']
    assert SQLiteProgressStore(path).snapshot()==merged
    backup=Path(tmp)/'backup.sqlite3';store.backup(backup);assert SQLiteProgressStore(backup).snapshot()==merged
    # Batch conflict rolls back earlier valid writes and operation IDs.
    ops=[{'id':'valid-before-conflict','day':'2026-10-12','problem':99,'field':'done','value':True,'revision':0},dict(b,id='stale')]
    try:store.apply(ops);raise AssertionError('Expected conflict')
    except ConflictError:pass
    assert store.snapshot()==merged
    with store.connect() as db:assert db.execute('PRAGMA journal_mode').fetchone()[0]=='delete';assert db.execute('PRAGMA foreign_keys').fetchone()[0]==1
print('SQLite',sqlite3.sqlite_version,': import confirmation path/additive/idempotent/tombstone, two-client conflict/retry, batch rollback, restart persistence, online backup checks passed.')
