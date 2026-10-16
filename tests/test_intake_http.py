from intake_support import *
import tempfile,subprocess,os,socket,time,http.client
def freeport():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
with tempfile.TemporaryDirectory() as d:
    root=fixture(d);port=freeport();env=dict(os.environ,LEARNING_HOST='127.0.0.1',LEARNING_PORT=str(port),LEARNING_DB=str(root/'data/test.sqlite3'),LEARNING_CONTENT_IMPORT='0')
    def req(path,body=None,extra=None,raw=None):
        c=http.client.HTTPConnection('127.0.0.1',port,timeout=5);headers={'Content-Type':'application/json','X-Learning-Request':'1'}
        if extra:headers.update(extra)
        c.request('POST' if body is not None or raw is not None else 'GET',path,raw if raw is not None else json.dumps(body) if body is not None else None,headers)
        r=c.getresponse();data=r.read();status=r.status;c.close();return status,json.loads(data)
    def start(enabled):
        env['LEARNING_CONTENT_IMPORT']=str(enabled)
        proc=subprocess.Popen([getattr(sys,'_base_executable',sys.executable),str(root/'server.py')],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for _ in range(70):
            if proc.poll() is not None:raise AssertionError('Isolated HTTP server failed')
            try:
                if req('/api/progress')[0]==200:return proc
            except OSError:time.sleep(.1)
        proc.terminate();raise AssertionError('HTTP server not ready')
    batch=reference(root);payload={'batch':batch,'dryRun':False};proc=start(0)
    try:assert req('/api/v1/content/import',payload)[0]==403
    finally:proc.terminate();proc.wait(timeout=5)
    proc=start(1)
    try:
        baseline=req('/api/progress')[1]
        assert req('/api/v1/content/import',{'batch':batch})[1]['dryRun'] is True
        assert req('/api/progress')[1]==baseline
        for headers in [{'Origin':'https://evil.invalid'},{'Host':'evil.invalid'},{'X-Learning-Request':''}]:assert req('/api/v1/content/import',payload,headers)[0]==403
        for body in [[],{'batch':batch,'publish':True},{'batch':dict(batch,schemaVersion=2)},{'batch':batch,'dryRun':'false'}]:assert req('/api/v1/content/import',body)[0]==400
        assert req('/api/v1/content/import',raw='{"batch":{},"batch":{}}')[0]==400
        status,first=req('/api/v1/content/import',payload);assert status==200 and first['status']=='planned'
        after=req('/api/progress')[1];assert after['plan']==[1,167] and after['records']==baseline['records']
        assert req('/api/v1/content/import',payload)[0]==200 and req('/api/progress')[1]==after
        assert req('/api/v1/content/import',{'batch':dict(batch,day='2030-1-3'),'dryRun':False})[0]==409
        pending=candidate(root);status,result=req('/api/v1/content/import',{'batch':pending,'dryRun':False});assert status==200 and result['status']=='pending_review'
        assert not (root/'content/problems/99001.json').exists() and req('/api/progress')[1]==after
        assert req('/local/incoming/synthetic-candidate.json')[0]==404
        # Synthetic remote client and forwarded-port Host checks, without changing OS networking.
        script=root/'check_boundaries.py'
        script.write_text('''import importlib.util,os
spec=importlib.util.spec_from_file_location('backend','app/backend/server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
h=m.Handler.__new__(m.Handler);h.client_address=('192.168.7.99',123);h.headers={'Host':'127.0.0.1:8791'};assert not h.trusted()
m.HOST='0.0.0.0';m.PORT=8791;m.PUBLIC_HOST='127.0.0.1';m.PUBLIC_PORT=18881
h.client_address=('172.18.0.1',123);h.headers={'Host':'127.0.0.1:18881'};assert h.trusted()
h.headers={'Host':'evil.invalid:18881'};assert not h.trusted()
import io
m.HOST='192.168.0.200';h.client_address=('192.168.0.201',123);h.trusted=lambda: True
h.path='/api/v1/content/import';h.headers={'Content-Type':'application/json','X-Learning-Request':'1','Content-Length':'2'};h.rfile=io.BytesIO(b'{}');out=[];h.reply=lambda status,body:out.append(status)
h.do_POST();assert out==[403],out

''',encoding='utf-8')
        subprocess.run([getattr(sys,'_base_executable',sys.executable),str(script)],cwd=root,env=dict(env,LEARNING_DB=str(root/'data/boundary.sqlite3')),check=True)
    finally:proc.terminate();proc.wait(timeout=5)
    proc=start(1)
    try:
        assert req('/api/progress')[1]==after
        assert req('/api/v1/content/import',payload)[0]==200 and req('/api/progress')[1]==after
    finally:proc.terminate();proc.wait(timeout=5)
print('HTTP intake actual isolated service: disabled by default, preflight no changes, JSON/header/Host/Origin/duplicate-key restrictions, apply/replay/conflict, staged content private, restart preserves plan. Container network boundary only simulated, not a container run.')
