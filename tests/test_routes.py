import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import tempfile,json,sqlite3
from pathlib import Path
from storage import SQLiteProgressStore,ConflictError
root=Path(__file__).resolve().parents[1]
routes=json.loads((root/'content/routes/routes.json').read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(dir=root) as tmp:
    path=Path(tmp)/'progress.sqlite3';s=SQLiteProgressStore(path)
    initial=s.import_legacy({'2020-1-1':{'list':[3,1],'done':[1]}})
    before=initial['plan'];original_progress=initial['records']
    response=s.join_route('thinking-basics','route-1');after=response['snapshot'];first=routes[0]['problemIds']
    assert set(first)<=set(after['plan']);assert after['plan'][:len(before)]==before
    assert after['plan'][len(before):]==[id for id in first if id not in before]
    assert after['records']==original_progress,'route must not reset daily/completed records'
    repeat=s.join_route('thinking-basics','route-1');assert repeat['snapshot']==after;assert repeat['result']['replayed']
    twice=s.join_route('thinking-basics','route-2');assert twice['result']['addedCount']==0;assert twice['snapshot']==after
    other=s.join_route('array-toolkit','route-3');expected=after['plan']+[id for id in routes[2]['problemIds'] if id not in after['plan']]
    assert other['snapshot']['plan']==expected;assert len(expected)==len(set(expected));assert other['snapshot']['records']==original_progress
    assert SQLiteProgressStore(path).snapshot()==other['snapshot'],'restart persistence'
    unchanged=s.snapshot()
    try:s.join_route('unknown','bad');raise AssertionError('invalid route accepted')
    except ValueError:pass
    assert s.snapshot()==unchanged
    # A client with a stale global-plan revision cannot silently remove a route addition.
    op={'id':'stale-plan-remove','day':'2026-10-13','problem':217,'field':'planned','value':False,'revision':0}
    try:s.apply([op]);raise AssertionError('stale global plan removal accepted')
    except ConflictError:pass
    op['revision']=s.snapshot()['planRevisions']['217'];removed=s.apply([op]);assert 217 not in removed['plan'];assert removed['records']['2020-1-1']['done']==[1]
    restored=s.join_route('thinking-basics','route-4');assert restored['result']['added']==[217];assert restored['snapshot']['plan'][-1]==217
    backup=Path(tmp)/'backup.sqlite3';s.backup(backup);assert SQLiteProgressStore(backup).snapshot()==s.snapshot()
    for route in routes:s.join_route(route['id'],'all-'+route['id'])
    assert set(id for r in routes for id in r['problemIds'])<=set(s.snapshot()['plan']);assert s.snapshot()['records']['2020-1-1']['done']==[1]
print('Routes: whole-route atomic addition, ordered append, duplicate request/route, overlapping routes, no completion reset, global CAS, re-add, all presets, backup/restart persistence passed.')
