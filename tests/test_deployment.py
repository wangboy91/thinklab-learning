from intake_support import *
import tempfile,subprocess,os,socket,time,http.client,signal,re,threading
from http.server import BaseHTTPRequestHandler,HTTPServer
def freeport():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def get(port,path='/api/progress'):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=1);c.request('GET',path);r=c.getresponse();b=r.read();c.close();return r.status,json.loads(b)
with tempfile.TemporaryDirectory() as d:
    root=fixture(d);port=freeport();env=dict(os.environ,LEARNING_DB=str(root/'data/test.sqlite3'))
    command=[getattr(sys,'_base_executable',sys.executable),str(root/'scripts/start_local.py'),'--host','127.0.0.1','--port',str(port)]
    def start():
        proc=subprocess.Popen(command,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        pid=None
        for line in proc.stdout:
            match=re.search(r'PID=(\d+)',line)
            if match:pid=int(match[1]);break
        assert pid is not None,'Launcher failed to start in isolated fixture'
        return proc,pid
    proc,pid=start()
    try:
        stamp=(root/'dist/content.js').stat().st_mtime_ns
        repeated=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=10);assert repeated.returncode==0 and 'already healthy' in repeated.stdout
        assert (root/'dist/content.js').stat().st_mtime_ns==stamp
        c=http.client.HTTPConnection('127.0.0.1',port,timeout=3);c.request('POST','/api/plan/daily',json.dumps({'day':'2030-1-1','problemIds':[206,21]}),{'Content-Type':'application/json','X-Learning-Request':'1'});r=c.getresponse();assert r.status==200;r.read();c.close();before=get(port)[1]
    finally:os.kill(pid,signal.SIGTERM);proc.wait(timeout=5)
    proc,pid=start()
    try:assert get(port)[1]==before
    finally:os.kill(pid,signal.SIGTERM);proc.wait(timeout=5)
    class Other(BaseHTTPRequestHandler):
        def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write(b'{}')
        def log_message(self,*args):pass
    other=HTTPServer(('127.0.0.1',port),Other);thread=threading.Thread(target=other.serve_forever,daemon=True);thread.start()
    try:
        failed=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=10);assert failed.returncode!=0 and 'occupied' in failed.stderr
        assert get(port,'/api/health')[0]==200
    finally:other.shutdown();other.server_close()
    (root/'local/start.lock').write_text('synthetic-existing-lock')
    command[-1]=str(freeport())
    locked=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=10);assert locked.returncode!=0 and 'lock exists' in locked.stderr
assert 'no-new-privileges' in (ROOT/'compose.yaml').read_text() and 'thinklab-data:/state' in (ROOT/'compose.yaml').read_text()
assert 'local' in (ROOT/'.dockerignore').read_text() and 'data' in (ROOT/'.dockerignore').read_text()
assert 'exec python3' in (ROOT/'start-learning.sh').read_text()
print('Windows actual isolated launcher: build/start, health reuse without rebuild/second service, occupied port rejection, startup lock, SQLite survives process restart. Shell/container checks here are static only.')
