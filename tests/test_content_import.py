from intake_support import *
import tempfile,importlib.util,unittest.mock,sqlite3
from app.backend.content_import import ContentIntake,validate,digest,safe_path
from app.backend.storage import SQLiteProgressStore,ConflictError
spec=importlib.util.spec_from_file_location('publisher',ROOT/'scripts/publish_reviewed_batch.py');publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
def fails(call,kind=ValueError):
    try:call()
    except kind:return
    raise AssertionError('Expected rejection')
with tempfile.TemporaryDirectory() as d:
    root=fixture(d);store=SQLiteProgressStore(root/'data/test.sqlite3',content_root=root);service=ContentIntake(root,store)
    initial=store.import_legacy({'2029-1-1':{'list':[206,1],'done':[206]}});batch=reference(root)
    before_db=(root/'data/test.sqlite3').read_bytes();assert service.run(batch)['status']=='ready';assert store.snapshot()==initial
    assert (root/'data/test.sqlite3').read_bytes()==before_db
    first=service.run(batch,False);after=store.snapshot();assert first['planResult']['added']==[167] and first['planResult']['already']==[1]
    assert after['plan']==initial['plan']+[167] and after['records']==initial['records'] and after['revisions']==initial['revisions']
    for id in initial['plan']:assert after['planRevisions'][str(id)]==initial['planRevisions'][str(id)]
    service.run(batch,False);assert store.snapshot()==after
    assert SQLiteProgressStore(root/'data/test.sqlite3',content_root=root).snapshot()==after
    altered=copy.deepcopy(batch);altered['day']='2030-1-3';fails(lambda:service.run(altered,False),ConflictError)
    bad=copy.deepcopy(batch);bad['items'][0]['sha256']='0'*64;fails(lambda:service.run(bad),ConflictError)
    for change in [dict(schemaVersion=2),dict(batchId='../escape'),dict(batchId='CON'),dict(items=[]),dict(items=[batch['items'][0],batch['items'][0]])]:
        bad=dict(batch,**change);fails(lambda:service.run(bad,False));assert store.snapshot()==after
    new=candidate(root);newhash=digest(new);preview=service.run(new);assert preview['pendingReview']==[99001]
    service.run(new,False);service.run(new,False);assert store.snapshot()==after
    staged=root/'local/incoming/synthetic-candidate.json';assert staged.is_file() and not (root/'content/problems/99001.json').exists()
    for key,value in [('trace','unknownTrace'),('question','<img src=x onerror=alert(1)>'),('examples',[{'label':'wrong','a':'not array','b':[]}])]:
        bad=copy.deepcopy(new);bad['items'][0]['candidate']['lesson'][key]=value;fails(lambda:service.run(bad))
    bad=copy.deepcopy(new);del bad['items'][0]['candidate']['solutions']['java'];fails(lambda:service.run(bad))
    bad=copy.deepcopy(new);bad['items'][0]['candidate']['path']='../../README.md';fails(lambda:service.run(bad))
    fails(lambda:safe_path(root,'../escape'))
    review={'schemaVersion':1,'batchSha256':newhash,'approved':True,'reviewer':'synthetic test fixture only','checks':{k:'passed' for k in ['rights','semantics','traceOracle','fiveLanguages','ui']},'evidence':'Synthetic fixture: tests the publication gate; does not claim this code is reviewed production teaching.'}
    fails(lambda:publisher.publish(root,new,dict(review,approved=False),newhash))
    fails(lambda:publisher.publish(root,new,review,'0'*64))
    oldcatalog=(root/'content/catalog.json').read_bytes()
    with unittest.mock.patch.object(publisher.subprocess,'run',side_effect=RuntimeError('synthetic build failure')):
        fails(lambda:publisher.publish(root,new,review,newhash),RuntimeError)
    assert (root/'content/catalog.json').read_bytes()==oldcatalog and not (root/'content/problems/99001.json').exists()
    result=publisher.publish(root,new,review,newhash);assert result['status']=='published'
    assert publisher.publish(root,new,review,newhash)['status']=='already_published'
    final=service.run(new,False);assert final['status']=='planned' and store.snapshot()['plan']==after['plan']+[99001]
    assert store.snapshot()['records']==after['records']
    stable=store.snapshot();service.run(new,False);assert store.snapshot()==stable
    db=sqlite3.connect(root/'data/test.sqlite3')
    try:assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    finally:db.close()
print('Intake: isolated preflight/no writes; original-source/hash/batch conflicts; no overwrite/path/HTML/new trace; stage only; local review gate/build rollback; published source build; daily merge/replay/restart preserved state. Incoming code never executed.')
