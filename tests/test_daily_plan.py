import sys,tempfile,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from storage import SQLiteProgressStore
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'plan.sqlite3';s=SQLiteProgressStore(path)
    before=s.import_legacy({'2026-10-13':{'list':[20,206],'done':[206]}})
    first=s.join_daily('2026-10-14',[206,21,21]);after=first['snapshot']
    assert after['plan']==before['plan']+[21]
    assert after['records']==before['records'] and after['revisions']==before['revisions']
    assert after['planRevisions']['206']==before['planRevisions']['206']
    assert first['result']['added']==[21] and first['result']['already']==[206]
    assert s.join_daily('2026-010-014',[21,206])['snapshot']==after
    assert SQLiteProgressStore(path).snapshot()==after
    removed=s.apply([{'id':'remove-21','day':'2026-10-14','problem':21,'field':'planned','value':False,'revision':after['planRevisions']['21']}])
    assert s.join_daily('2026-10-14',[206,21])['snapshot']==removed
    assert s.join_daily('2026-10-15',[21])['snapshot']['plan'][-1]==21
    unchanged=s.snapshot()
    for day,ids in [('bad',[21]),('2026-10-14',[True]),('2026-10-14',[]),('2026-10-14',[21,33])]:
        try:s.join_daily(day,ids);raise AssertionError('invalid input accepted')
        except ValueError:pass
        assert s.snapshot()==unchanged
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:s.join_daily('2026-10-16',[1,21]),range(8)))
    assert sum(len(r['result']['added']) for r in results)==1
    final=s.snapshot();assert len(final['plan'])==len(set(final['plan']))
    assert final['records']['2026-10-13']['done']==[206]
print('Daily plan: order/revisions/done preserved; date normalization/idempotency; remove then replay; restart; invalid batch rollback; 8 concurrent joins passed')
