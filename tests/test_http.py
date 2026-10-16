import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import os,subprocess,tempfile,time,json,http.client,sqlite3
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(dir=root) as tmp:
    env=dict(os.environ,LEARNING_HOST='127.0.0.1',LEARNING_PORT='18879',LEARNING_DB=str(Path(tmp)/'test.sqlite3'))
    def start():
        proc=subprocess.Popen([os.sys.executable,str(root/'server.py')],env=env,cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for _ in range(50):
            try:
                if req('/api/progress')[0]==200:return proc
            except OSError:time.sleep(.1)
        proc.terminate();raise RuntimeError('Test server did not become ready')
    def req(path,body=None,extra=None):
        conn=http.client.HTTPConnection('127.0.0.1',18879,timeout=5)
        headers={'Content-Type':'application/json','X-Learning-Request':'1'} if body is not None else {}
        if extra:headers.update(extra)
        conn.request('POST' if body is not None else 'GET',path,json.dumps(body) if body is not None else None,headers)
        response=conn.getresponse();raw=response.read();result=(response.status,raw,dict(response.getheaders()));conn.close();return result
    proc=start()
    try:
        for name in ['index.html','style.css','app.js','content.js','codes.js','algorithms.js','sync.js','bootstrap.js','routes.js','lessons.js','algorithms-extra.js']:
            status,body,headers=req('/' if name=='index.html' else '/'+name);assert status==200;assert body==(root/'dist'/name).read_bytes();assert headers['Cache-Control']=='no-store'
        for path in ['/data/learning.sqlite3','/source-snapshots/','/source-manifest.json','/.git/config','/../README.md','/%2e%2e/README.md']:
            assert req(path)[0]==404,path
        assert req('/api/progress',{'operations':[]},{'Origin':'https://evil.example'})[0]==403
        assert req('/api/progress',{'operations':[]},{'X-Learning-Request':''})[0]==403
        assert req('/api/progress',{'operations':[]},{'Host':'evil.example'})[0]==403
        health=req('/health');assert health[0]==200;assert 'ThinkLab 已连接电脑'.encode() in health[1]
        counters=json.loads(req('/api/health')[1]);assert counters['ok'];assert '/health' in counters['routes'];assert not any('ip' in key.lower() or 'agent' in key.lower() for key in counters)
        locked=sqlite3.connect(env['LEARNING_DB']);locked.execute('BEGIN EXCLUSIVE')
        started=time.monotonic();assert req('/api/progress')[0]==503;assert time.monotonic()-started<3
        locked.rollback();locked.close();assert req('/api/progress')[0]==200
        status,body,_=req('/api/import',{'records':{'2026-10-12':{'list':[1,20],'done':[1]}}});assert status==200;first=json.loads(body)
        assert json.loads(req('/api/import',{'records':{'2026-10-12':{'list':[1,20],'done':[1]}}})[1])==first
        op={'id':'http-a','day':'2026-10-12','problem':1,'field':'done','value':False,'revision':first['revisions']['2026-10-12|1|done']}
        status,body,_=req('/api/progress',{'operations':[op]});assert status==200;next=json.loads(body)
        assert json.loads(req('/api/progress',{'operations':[op]})[1])==next
        other=dict(op,id='http-b',value=True);status,body,_=req('/api/progress',{'operations':[other]});assert status==409;conflict=json.loads(body);assert conflict['snapshot']==next
        other['revision']=next['revisions']['2026-10-12|1|done'];assert req('/api/progress',{'operations':[other]})[0]==200
        final=json.loads(req('/api/progress')[1]);assert final['records']['2026-10-12']['done']==[1]
        presets=json.loads(req('/api/routes')[1]);assert len(presets)==4
        base=final['records'];status,body,_=req('/api/plan/route',{'routeId':'thinking-basics','operationId':'http-route-1'});assert status==200;joined=json.loads(body);assert joined['snapshot']['records']==base
        assert set(presets[0]['problemIds'])<=set(joined['snapshot']['plan'])
        replay=json.loads(req('/api/plan/route',{'routeId':'thinking-basics','operationId':'http-route-1'})[1]);assert replay['snapshot']==joined['snapshot'];assert replay['result']['replayed']
        duplicate=json.loads(req('/api/plan/route',{'routeId':'thinking-basics','operationId':'http-route-2'})[1]);assert duplicate['result']['addedCount']==0
        overlap=json.loads(req('/api/plan/route',{'routeId':'array-toolkit','operationId':'http-route-3'})[1]);assert overlap['snapshot']['records']==base;assert len(overlap['snapshot']['plan'])==len(set(overlap['snapshot']['plan']))
        assert req('/api/plan/route',{'routeId':'unknown','operationId':'invalid'})[0]==400
        assert req('/api/plan/route',{'routeId':'thinking-basics','operationId':'cross-site'},{'Origin':'https://evil.example'})[0]==403
        baseline=json.loads(req('/api/progress')[1])
        payload={'day':'2026-10-14','problemIds':[206,21]}
        assert req('/api/plan/daily',payload,{'Origin':'https://evil.example'})[0]==403
        assert req('/api/plan/daily',payload,{'X-Learning-Request':''})[0]==403
        assert req('/api/plan/daily',{'day':'2026-10-14','problemIds':[21,33]})[0]==400
        assert json.loads(req('/api/progress')[1])==baseline
        status,body,_=req('/api/plan/daily',payload);assert status==200
        joined=json.loads(body);daily=joined['snapshot']
        assert daily['plan']==baseline['plan']+[p for p in [206,21] if p not in baseline['plan']]
        assert daily['records']==baseline['records'] and daily['revisions']==baseline['revisions']
        for p in baseline['plan']:assert daily['planRevisions'][str(p)]==baseline['planRevisions'][str(p)]
        assert json.loads(req('/api/plan/daily',payload)[1])['snapshot']==daily
        final=json.loads(req('/api/progress')[1])

    finally:proc.terminate();proc.wait(timeout=5)
    proc=start()
    try:assert json.loads(req('/api/progress')[1])==final
    finally:proc.terminate();proc.wait(timeout=5)
print('HTTP simulation: 11 assets/no-store, no-JS health/counters, DB lock returns 503 under 3s and recovers, whitelist/origin/header/Host, two-client conflict/import/routes/overlap/no-progress-reset/idempotency/restart passed. No real phone test.')
