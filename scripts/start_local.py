"""Portable standard-library launcher. Healthy ThinkLab is reused; busy ports fail visibly."""
import argparse,http.client,json,os,socket,subprocess,sys,time,ipaddress
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PYTHON=getattr(sys,'_base_executable',sys.executable) if os.name=='nt' else sys.executable
def state(host,port):
    target='127.0.0.1' if host=='0.0.0.0' else host
    try:
        c=http.client.HTTPConnection(target,port,timeout=1);c.request('GET','/api/health');r=c.getresponse();body=r.read();c.close()
        if r.status==200 and json.loads(body).get('service')=='ThinkLab':
            c=http.client.HTTPConnection(target,port,timeout=1);c.request('GET','/api/progress');r=c.getresponse();r.read();c.close()
            if r.status==200:return 'healthy'
    except (OSError,ValueError):pass
    try:
        with socket.create_connection((target,port),timeout=.5):return 'occupied'
    except OSError:pass
    # A service bound only to another local interface must not become a second instance.
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as probe:
            if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):probe.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
            else:probe.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            probe.bind(('0.0.0.0',port))
        return 'free'
    except OSError:return 'occupied'
def main():
    p=argparse.ArgumentParser();p.add_argument('--host',default=os.environ.get('LEARNING_HOST','127.0.0.1'));p.add_argument('--port',type=int,default=int(os.environ.get('LEARNING_PORT','8791')));p.add_argument('--check',action='store_true');a=p.parse_args()
    if sys.version_info<(3,11):raise SystemExit('Python 3.11+ required; no runtime is installed automatically.')
    if not 1<=a.port<=65535:raise SystemExit('Invalid port')
    try:ipaddress.IPv4Address(a.host)
    except ValueError:raise SystemExit('Use an explicit local/private IPv4 address')
    current=state(a.host,a.port)
    if current=='healthy':print(f'ThinkLab already healthy: http://{a.host}:{a.port}/');return
    if a.check:raise SystemExit(f'Not running: {current}')
    if current=='occupied':raise SystemExit('Port occupied by another/unhealthy service. Inspect it; no process was stopped.')
    # Local-file lock prevents concurrent launch/build in this checkout; stale lock is never removed automatically.
    lock=ROOT/'local/start.lock';lock.parent.mkdir(exist_ok=True)
    try:fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    except FileExistsError:raise SystemExit('Startup lock exists: local/start.lock. Check the recorded process before removing a stale lock.')
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:
        if state(a.host,a.port)!='free':raise SystemExit('Port changed during startup; no second service started.')
        subprocess.run([PYTHON,str(ROOT/'scripts/build_content.py')],cwd=ROOT,check=True)
        env=dict(os.environ,LEARNING_HOST=a.host,LEARNING_PORT=str(a.port))
        proc=subprocess.Popen([PYTHON,str(ROOT/'server.py')],cwd=ROOT,env=env)
        try:
            for _ in range(60):
                if proc.poll() is not None:raise SystemExit(f'Service exited with code {proc.returncode}')
                if state(a.host,a.port)=='healthy':break
                time.sleep(.1)
            else:proc.terminate();raise SystemExit('Service did not become healthy; inspect the visible error.')
            print(f'ThinkLab ready: http://{a.host}:{a.port}/ PID={proc.pid} (Ctrl+C stops this instance)',flush=True)
            code=proc.wait()
            if code:raise SystemExit(code)
        except KeyboardInterrupt:
            proc.terminate();proc.wait(timeout=5)
    finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
