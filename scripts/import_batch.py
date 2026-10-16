"""Preflight locally; --apply submits to the opt-in local-machine intake API."""
import argparse,http.client,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.backend.content_import import validate
def main():
    p=argparse.ArgumentParser();p.add_argument('file',type=Path);p.add_argument('--apply',action='store_true');p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8791);a=p.parse_args()
    if a.file.stat().st_size>1024*1024:raise SystemExit('Batch exceeds 1 MiB')
    batch=json.loads(a.file.read_text(encoding='utf-8'));preview=validate(ROOT,batch)
    if not a.apply:print(json.dumps(dict(preview,dryRun=True),ensure_ascii=True));return
    c=http.client.HTTPConnection(a.host,a.port,timeout=6)
    c.request('POST','/api/v1/content/import',json.dumps({'batch':batch,'dryRun':False}),{'Content-Type':'application/json','X-Learning-Request':'1','Origin':f'http://{a.host}:{a.port}'})
    r=c.getresponse();result=json.loads(r.read());c.close()
    if r.status!=200:raise SystemExit(f'Not confirmed: HTTP {r.status}: {result.get("error")}')
    print(json.dumps(result,ensure_ascii=True))
if __name__=='__main__':main()
