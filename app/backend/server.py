"""Single-person LAN learning service; no account isolation or public exposure."""
import os,json,ipaddress,sqlite3,time,threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from storage import SQLiteProgressStore,ConflictError
from app.backend.content_import import ContentIntake
ROOT=Path(__file__).resolve().parents[2]
HOST=os.environ.get('LEARNING_HOST','127.0.0.1');PORT=int(os.environ.get('LEARNING_PORT','8791'))
PUBLIC_HOST=os.environ.get('LEARNING_PUBLIC_HOST','127.0.0.1' if HOST=='0.0.0.0' else HOST)
PUBLIC_PORT=int(os.environ.get('LEARNING_PUBLIC_PORT',str(PORT)))
STORE=SQLiteProgressStore(Path(os.environ.get('LEARNING_DB',str(ROOT/'data/learning.sqlite3'))))
ASSETS={'index.html':'text/html','style.css':'text/css','app.js':'text/javascript','content.js':'text/javascript','codes.js':'text/javascript','algorithms.js':'text/javascript','sync.js':'text/javascript','bootstrap.js':'text/javascript','routes.js':'text/javascript','lessons.js':'text/javascript','algorithms-extra.js':'text/javascript'}
COUNTERS={};COUNTER_LOCK=threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def reply(self,status,body,kind='application/json'):
        # Aggregate this service's known routes only: no IP, UA, query or request body.
        route=self.path if self.path in ['/','/health','/api/health','/api/progress','/api/import','/api/routes','/api/plan/route','/api/plan/daily','/api/v1/content/import'] or self.path[1:] in ASSETS else '(other)'
        with COUNTER_LOCK:
            count=COUNTERS.setdefault(route,{'count':0,'lastStatus':status,'lastTime':0});count.update(count=count['count']+1,lastStatus=status,lastTime=round(time.time()))
        if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'");self.end_headers()
        if self.command!='HEAD':self.wfile.write(body)
    def trusted(self):
        peer=ipaddress.ip_address(self.client_address[0]);host=self.headers.get('Host','')
        allowed_peer=peer.is_loopback or (peer.is_private if HOST=='0.0.0.0' else peer in ipaddress.ip_network(HOST+'/24',strict=False))
        allowed_hosts=[f'{HOST}:{PORT}',f'127.0.0.1:{PORT}',f'localhost:{PORT}']
        if HOST=='0.0.0.0' and ipaddress.ip_address(PUBLIC_HOST).is_private:allowed_hosts.append(f'{PUBLIC_HOST}:{PUBLIC_PORT}')
        return allowed_peer and host in allowed_hosts
    def do_GET(self):
        if not self.trusted():self.reply(403,{'error':'LAN access only'});return
        if self.path=='/api/progress':
            try:self.reply(200,STORE.snapshot())
            except sqlite3.Error:self.reply(503,{'error':'Database busy or unavailable; retry without clearing progress'})
            return
        if self.path=='/api/routes':self.reply(200,json.loads((ROOT/'content/routes/routes.json').read_text(encoding='utf-8')));return
        if self.path=='/api/health':
            with COUNTER_LOCK:counts=json.loads(json.dumps(COUNTERS))
            self.reply(200,{'service':'ThinkLab','ok':True,'routes':counts});return
        if self.path=='/health':
            try:STORE.snapshot();dbstatus='学习数据库可读取'
            except sqlite3.Error:dbstatus='学习数据库暂忙，请稍后重试；不要清空进度'
            html=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ThinkLab 连接检查</title><body style="font:18px/1.7 sans-serif;padding:20px;max-width:600px;margin:auto"><h1>ThinkLab 已连接电脑</h1><p>如果手机能看到此页，说明手机请求已到达此服务。</p><p>{dbstatus}</p><p>此检查页不需要 JavaScript。</p><p><a href="/">返回题库</a></p><p>题库仍白屏时，请尝试系统 Chrome 或 Safari，并告知是否看到了 ThinkLab 标题及错误提示。</p></body></html>'''
            self.reply(200,html.encode(),'text/html');return
        key='index.html' if self.path=='/' else self.path[1:]
        if key not in ASSETS:self.reply(404,{'error':'Not found'});return
        self.reply(200,(ROOT/'dist'/key).read_bytes(),ASSETS[key])
    do_HEAD=do_GET
    def do_POST(self):
        if not self.trusted():self.reply(403,{'error':'LAN access only'});return
        # No CORS. Cross-origin writes rejected; JSON prevents HTML form posts.
        origin=self.headers.get('Origin');expected='http://'+self.headers.get('Host','')
        if origin and origin!=expected:self.reply(403,{'error':'Origin rejected'});return
        if self.headers.get('X-Learning-Request')!='1':self.reply(403,{'error':'Learning header required'});return
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':self.reply(415,{'error':'JSON required'});return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=1024*1024:raise ValueError('Invalid size')
            def unique_pairs(pairs):
                result={}
                for key,value in pairs:
                    if key in result:raise ValueError('Duplicate JSON key')
                    result[key]=value
                return result
            body=json.loads(self.rfile.read(size),object_pairs_hook=unique_pairs)
            if not isinstance(body,dict):raise ValueError('JSON object required')
            if self.path=='/api/v1/content/import':
                peer=ipaddress.ip_address(self.client_address[0])
                if os.environ.get('LEARNING_CONTENT_IMPORT','0')!='1' or not (peer.is_loopback or self.client_address[0]==HOST):
                    self.reply(403,{'error':'Content intake disabled or not a local-machine request'});return
                if set(body)-{'batch','dryRun'}:raise ValueError('Unsupported import request fields')
                result=ContentIntake(ROOT,STORE).run(body.get('batch'),body.get('dryRun',True))
            elif self.path=='/api/import':result=STORE.import_legacy(body.get('records',{}))
            elif self.path=='/api/progress':result=STORE.apply(body.get('operations',[]))
            elif self.path=='/api/plan/daily':result=STORE.join_daily(body.get('day'),body.get('problemIds'))
            elif self.path=='/api/plan/route':result=STORE.join_route(body.get('routeId'),body.get('operationId'))
            else:self.reply(404,{'error':'Not found'});return
            self.reply(200,result)
        except ConflictError:self.reply(409,{'error':'Revision conflict','snapshot':STORE.snapshot()})
        except sqlite3.Error:self.reply(503,{'error':'Database busy or unavailable; retry without clearing progress'})
        except OSError:self.reply(503,{'error':'Storage unavailable; no publication confirmed'})
        except (ValueError,TypeError,KeyError):self.reply(400,{'error':'Invalid request'})
    def log_message(self,*args):pass # Do not collect client IP access logs.
if __name__=='__main__':
    print(f'Learning v0.2 listening on http://{HOST}:{PORT}; single-person LAN SQLite',flush=True)
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
