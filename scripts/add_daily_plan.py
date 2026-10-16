"""Use the running same-origin API; this script never starts a service."""
import argparse,http.client,json
p=argparse.ArgumentParser();p.add_argument('--host',default='192.168.0.200');p.add_argument('--port',type=int,default=8791);p.add_argument('--day',required=True);p.add_argument('problem_ids',nargs='+',type=int);a=p.parse_args()
c=http.client.HTTPConnection(a.host,a.port,timeout=6)
body=json.dumps({'day':a.day,'problemIds':a.problem_ids})
c.request('POST','/api/plan/daily',body,{'Content-Type':'application/json','X-Learning-Request':'1','Origin':f'http://{a.host}:{a.port}'})
r=c.getresponse();data=json.loads(r.read());c.close()
if r.status!=200:raise SystemExit(f'Not confirmed: HTTP {r.status}: {data.get("error")}')
print(json.dumps(data['result'],ensure_ascii=False))
