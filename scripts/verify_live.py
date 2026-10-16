import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse,http.client,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8791);a=p.parse_args();root=Path(__file__).resolve().parents[1]
def request(path,method='GET'):
    c=http.client.HTTPConnection(a.host,a.port,timeout=5);c.request(method,path);r=c.getresponse();body=r.read();headers=dict(r.getheaders());status=r.status;c.close();return status,body,headers
for file in ['index.html','style.css','bootstrap.js','content.js','algorithms.js','codes.js','sync.js','routes.js','lessons.js','algorithms-extra.js','app.js']:
    status,body,headers=request('/' if file=='index.html' else '/'+file);assert status==200,file;assert body==(root/'dist'/file).read_bytes(),file;assert headers['Cache-Control']=='no-store';assert headers['Content-Type'].startswith('text/css' if file.endswith('.css') else 'text/html' if file.endswith('.html') else 'text/javascript')
    if file=='index.html':assert b'data-thinklab-critical' in body;assert body.find(b'routes.js')<body.find(b'app.js')
assert request('/health')[0]==200
routes=json.loads(request('/api/routes')[1]);assert routes==json.loads((root/'content/routes/routes.json').read_text(encoding='utf-8'));assert len(routes)==4
snapshot=json.loads(request('/api/progress')[1]);assert isinstance(snapshot['plan'],list) and len(snapshot['plan'])==len(set(snapshot['plan']))
for path in ['/data/learning.sqlite3','/local/server.log','/.git/config','/../README.md','/%2e%2e/README.md','/routes.json']:assert request(path)[0]==404,path
assert request('/api/plan/route','POST')[0]==403
print('Live: 11 resources match local bytes/MIME/no-store and ordered required scripts; health/progress/4 routes return 200; plan shape valid; private paths 404 and unapproved route write 403. Read-only, no personal records printed.')
